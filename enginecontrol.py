import dearpygui.dearpygui as dpg
import dearpygui_extend as dpge
import time
import math
import threading
import csv
import serial.tools.list_ports


nsamples = 1000

global data_y
global data_x

data_y = [0.0] * nsamples
data_x = [0.0] * nsamples

layout='''
LAYOUT two_rows center center
	ROW
		COL row_A
	ROW
		COL row_B
'''


class EngineControlGUI():
    def __init__(self, serial, data):
        self.serial = serial
        self.data = data

        self.sync_cnt = 200

    def get_com_list(self):
        ports = serial.tools.list_ports.comports()
        self.com_list = [com[0] for com in ports]

    def update_com_list(self):
        self.get_com_list()
        dpg.configure_item('Serial Port', items=self.com_list)

    def serial_open(self):
        print(f'Connecting to {dpg.get_value("Serial Port")} at {dpg.get_value("Baud Rate")}')
        try:
            self.ser.is_open
        except:
            self.ser = serial.Serial()
            self.ser.baudrate = dpg.get_value('Baud Rate')
            self.ser.port = dpg.get_value('Serial Port')
            self.ser.timeout = 0.1

        try:
            if self.ser.is_open:
                print("Already Open")
                self.ser.status = True
                dpg.configure_item('connect_button', label='Disconnect', callback=self.serial_disconnect)
                dpg.configure_item('Serial Port', enabled=False)
                dpg.configure_item('Baud Rate', enabled=False)
            else:
                self.ser = serial.Serial()
                self.ser.baudrate = dpg.get_value('Baud Rate')
                self.ser.port = dpg.get_value('Serial Port')
                self.ser.timeout = 0.1
                self.ser.open()
                self.ser.status = True
                dpg.configure_item('connect_button', label='Disconnect', callback=self.serial_disconnect)
                dpg.configure_item('Serial Port', enabled=False)
                dpg.configure_item('Baud Rate', enabled=False)
        except:
            self.ser.status = False

    def serial_loop(self):
        self.threading = True
        cnt = 0
        while self.threading:
            try:
                self.ser.write(self.data.sync.encode('utf-8'))
                #print(self.ser.readline())
                self.data.row_msg = self.ser.readline()
                self.data.decode_msg()
                print(f"got an incoming message: {self.data.msg}")
                if int(self.data.msg[2]) > 0:
                    # sync is gtg
                    self.threading = False
                    break
                if self.threading == False:
                    break
            except Exception as e:
                print(e)
            cnt += 1
            if self.threading == False:
                break
            if cnt > self.sync_cnt:
                # failed to sync
                cnt = 0
                time.sleep(0.5)
                if self.threading == False:
                    break

    def serial_start(self):
        try:
            self.ser.write(self.data.start_stream.encode('utf-8'))
        except Exception as e:
            print(e)

        self.threading = True
        while self.threading:
            try:
                self.data.row_msg = self.ser.readline()
                self.data.decode_msg()
                #print(' '.join(self.data.msg))
                self.data.data_t.append(float(self.data.msg[1])/1000)
                self.data.data_x.append(float(self.data.msg[2]))

                dpg.set_value('series_tag', [list(self.data.data_t),
                                             list(self.data.data_x)])
                dpg.set_axis_limits('x_axis', self.data.data_t[-1] - dpg.get_value('x_scale'), self.data.data_t[-1])

                dpg.fit_axis_data('x_axis')
                dpg.fit_axis_data('y_axis')

            except Exception as e:
                print(e)
                self.threading = False
                break

    def serial_connect(self):
        self.serial_open()
        time.sleep(0.5)
        self.serial_loop()
        t1 = threading.Thread(target=self.serial_start)
        t1.start()

    def save_to_csv(self):
        print('saving!')
        with open('data_1khz.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Pressure'])
            for i in range(len(self.data.data_t)):
                writer.writerow([self.data.data_t[i], self.data.data_x[i]])

    def serial_disconnect(self):
        dpg.configure_item('connect_button', label='Connect', callback=self.serial_connect)
        dpg.configure_item('Serial Port', enabled=True)
        dpg.configure_item('Baud Rate', enabled=True)

    def print_info(self):
        print(f'Connecting to {dpg.get_value("Serial Port")} at {dpg.get_value("Baud Rate")}')

        dpg.configure_item('connect_button', label='Disconnect', callback=self.serial_disconnect)

    def select_path(self):
        dpg.add_file_dialog(label='Open File', callback=lambda : print('opening'))

    def serial_gui(self):
        self.get_com_list()

        with dpg.window(label='Serial', width=280, height=390, pos=(0, 0)):
            dpg.add_combo(label='Serial Port', items=self.com_list, tag='Serial Port')
            dpg.add_combo(label='Baud Rate', items=['9600', '115200'], tag='Baud Rate')
            with dpg.group(horizontal=True):
                dpg.add_button(label='Refresh', callback=self.update_com_list, tag='refresh_button')
                dpg.add_button(label='Connect', callback=self.serial_connect, tag='connect_button')
            dpg.add_button(label='Save Data', callback=self.save_to_csv, tag='save_button')

    def graph_gui(self):
        with dpg.window(label='Live Data', width=800, height=dpg.get_viewport_height(), pos=(280, 0)):
            with dpg.plot(label='System Pressures', height=-1, width=-1):
                dpg.add_plot_legend()
                self.x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='Time [s]', tag='x_axis')
                self.y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='Pressure [Pa]', tag='y_axis')

                dpg.set_axis_limits('y_axis', 0, 4096)

                dpg.add_line_series(x=list(data_x), y=list(data_y),
                                    label='Temp', parent='y_axis',
                                    tag='series_tag')

    def settings_gui(self):
        with dpg.window(label='Settings', width=280, height=390, pos=(0, 390)):
            dpg.add_input_float(label='x-axis scale', default_value=10, tag='x_scale', step=1)
            dpg.add_button(label='Select Save Path', callback=self.select_path)
            dpg.add_button(label='Show Metrics', callback=dpg.show_metrics)
            dpg.add_button(label='Show Debug', callback=dpg.show_debug)
            dpg.add_button(label='Show Documentation', callback=dpg.show_documentation)

    def run(self):
        # Call this function at the beginning in every DearPyGui application
        dpg.create_context()
        dpg.create_viewport(title='Engine Control', resizable=True,
                            width=1440, height=780, x_pos=0, y_pos=0,
                            min_width=800, min_height=600)
        
        self.serial_gui()
        self.graph_gui()
        self.settings_gui()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

