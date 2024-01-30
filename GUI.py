# IMPORTS
import csv
import datetime
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText

import threading
import functools
import time
import random
from PIL import Image, ImageTk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
plt.style.use('/Users/jackgardiner/Desktop/TEST STAND CONTROL/control_gui/graph_style.mplstyle')


class RootGUI():
    """
    an instance of this class is created as the main window in 'Master.py'
    """
    def __init__(self, serial, data):
        # set up main window parameters and import SerialControl() class as self.serial
        self.root = ttk.Window(themename='solar')
        self.root.title('TEST STAND CONTROL')
        self.root.geometry('1440x800+0+0')
        self.serial = serial

        ComGUI(self.root, serial, data)
        DispGUI(self.root, serial, data)
        PIDGUI(self.root, serial)
        StateGUI(self.root, serial)
        ParamsGUI(self.root, serial)
        ChannelGUI(self.root, serial)
        ParamsGUI(self.root, serial)

        [self.root.rowconfigure(i, weight=1) for i in range(5)]
        [self.root.columnconfigure(i, weight=1) for i in range(8)]

class ComGUI():
    """
    Communications Manager
    - COM port selection
    - baud rate selection
    - initial serial connection
    """
    def __init__(self, root, serial, data):

        self.root = root
        self.serial = serial
        self.data = data

        self.conn = ConnGUI(self.root, serial, data)
        self.frame = ttk.LabelFrame(root, text='Communications Manager')
        self.label_com = ttk.Label(self.frame, text='Available Port(s): ', anchor='w')
        self.label_bd = ttk.Label(self.frame, text='Baud Rate: ', anchor='w')

        # create COM Port and Baud Rate drop-downs
        self.comOptionMenu()
        self.baudOptionMenu()

        # create Refresh and Connect buttons
        self.btn_refresh = ttk.Button(self.frame, text="Refresh", width=6, command=self.com_refresh, bootstyle='secondary')
        self.btn_connect = ttk.Button(self.frame, text="Connect", width=6, command=self.serial_connect, state='disabled', bootstyle='success')

        self.padx = 5
        self.pady = 5

        # chuck it all on the grid
        self.publish()

    def publish(self):

        # labels for COM port and Baud Rate
        self.label_com.grid(column=1, row=2, sticky='e', padx=self.padx, pady=self.pady)
        self.label_bd.grid(column=1, row=3, sticky='e', padx=self.padx, pady=self.pady)

        # drop-downs for COM port and Baud rate
        self.drop_com.grid(column=2, row=2, padx=self.padx, pady=self.pady)
        self.drop_baud.grid(column=2, row=3, padx=self.padx, pady=self.pady)

        # buttons for Refresh and Connect
        self.btn_connect.grid(column=3, row=3, padx=self.padx, pady=self.pady)
        self.btn_refresh.grid(column=3, row=2, padx=self.padx, pady=self.pady) 

        self.frame.grid(row=0, column=0, rowspan=1, columnspan=2, padx=self.padx, pady=self.pady, sticky='nsew')

        [self.frame.rowconfigure(i, weight=1) for i in range(5)]
        [self.frame.columnconfigure(i, weight=1) for i in range(4)]

    def comOptionMenu(self):
        self.serial.getCOMList()

        self.selected_com = ttk.StringVar()
        self.selected_com.set(self.serial.com_list[0])

        self.drop_com = ttk.OptionMenu(self.frame,
                                       self.selected_com,
                                       *self.serial.com_list,
                                        command=self.connect_ctrl)
        self.drop_com.configure(width=6)

    def baudOptionMenu(self):
        self.selected_baud = ttk.StringVar()
        bds = ["- select -",
               "300",
               "600",
               "1200",
               "2400",
               "4800",
               "9600",
               "14400",
               "19200",
               "28800",
               "38400",
               "56000",
               "57600",
               "115200",
               "128000",
               "256000"]
        self.selected_baud.set(bds[0])

        self.drop_baud = ttk.OptionMenu(self.frame,
                                        self.selected_baud,
                                        *bds,
                                        command=self.connect_ctrl)
        self.drop_baud.configure(width=6)

    def connect_ctrl(self, value):
        '''
        method to control the activation of 'connect' button
        '''
        if '- select -' in self.selected_baud.get() or '- select -' in self.selected_com.get():
            self.btn_connect.configure(state='disabled')
        else:
            self.btn_connect.configure(state='active')

    def com_refresh(self):
        # destroy existing widget
        self.drop_com.destroy()
        # make it again (and publish)
        self.comOptionMenu()
        self.drop_com.grid(column=2, row=2, padx=self.padx, pady=self.pady)

        logic=[]
        self.connect_ctrl(logic)

    def serial_connect(self):

        if self.btn_connect["text"] in "Connect":
            self.serial.SerialOpen(self)

            # if connection established, move on
            if self.serial.ser.status:
                self.serial.t1 = threading.Thread(
                    target=self.serial.SerialSync, args=(self,), daemon=True
                )
                self.serial.t1.start()

class ConnGUI():
    def __init__(self, root, serial, data):
        self.root = root
        self.serial = serial
        self.data = data

        self.frame = ttk.LabelFrame(root, text='Connection Manager')

        self.sync_label = ttk.Label(self.frame, text='Sync Status: ', width = 15)
        self.sync_status = ttk.Label(self.frame, text='... Sync ...', width=5)

        self.ch_label = ttk.Label(self.frame, text="Active channels: ", width=15, anchor="w")
        self.ch_status = ttk.Label(self.frame, text="...", width=5)

        self.btn_start_stream = ttk.Button(self.frame, text="Start", state="disabled", width=6, bootstyle='success', command=self.start_serial)

        self.btn_stop_stream = ttk.Button(self.frame, text="Stop", state="disabled", width=6, bootstyle='warning', command=self.stop_serial)

        self.padx = 5
        self.pady = 5

        self.publish()
        self.raw = RawGUI(self.root, serial)

    def publish(self):
        
        self.sync_label.grid(column=1, row=1, padx=self.padx, pady=self.pady)
        self.sync_status.grid(column=2, row=1, padx=self.padx, pady=self.pady)

        self.ch_label.grid(column=1, row=2, padx=self.padx, pady=self.pady)
        self.ch_status.grid(column=2, row=2, padx=self.padx, pady=self.pady)

        self.btn_start_stream.grid(column=3, row=1, padx=self.padx, pady=self.pady)
        self.btn_stop_stream.grid(column=3, row=2, padx=self.padx, pady=self.pady)

        self.frame.grid(row=0, column=2, rowspan=1, columnspan=2, padx=self.padx, pady=self.pady, sticky='nsew')

        [self.frame.rowconfigure(i, weight=1) for i in range(5)]
        [self.frame.columnconfigure(i, weight=1) for i in range(4)]

    def start_serial(self):

        self.serial.t2 = threading.Thread(
            target=self.serial.SerialStart, args=(self,), daemon=True
        )
        self.serial.t2.start()
        pass

    def stop_serial(self):
        self.serial.t2 = threading.Thread(
            target=self.serial.SerialStop, args=(self,), daemon=True
        )
        self.serial.t2.start()
        pass

class DispGUI():
    def __init__(self, root, serial, data):
        self.root = root
        self.serial = serial
        self.data = data
        self.frame = ttk.LabelFrame(root, text='Live Data')

        self.padx = 5
        self.pady = 5
        self.time_span = 5      # seconds
        self.sample_freq = 20   # hz

        self.create_graph()
        self.publish()

        # Schedule the update_graph method to be called every 1000 milliseconds (1 second)
        self.t1 = threading.Thread(target=self.update_graph, daemon=True)

        # self.t1.start()

        #self.update_graph()
        
    def create_graph(self):
        height_px = 400
        width_px = 600
        res = 80
        self.x_start = 0
        self.x_vals = []
        self.y_vals = []
        self.myfig = plt.Figure(figsize=(width_px/res, height_px/res), dpi=res)
        self.customize_figure(self.myfig)
        self.canvas = FigureCanvasTkAgg(self.myfig, master=self.frame)
        self.canvas.draw()     

    def customize_figure(self, fig):
        ax = fig.add_subplot(111)
        ax.plot(self.x_vals, self.y_vals)
        ax.spines[['right', 'top']].set_visible(False)
        ax.set_xlabel('Time')
        ax.set_ylabel('Pressure')
        ax.set_ylim(0,100)
        ax.set_xlim(0,5)

    def publish(self):
        self.frame.grid(row=0, column=5, rowspan=2, columnspan=3, padx=self.padx, pady=self.pady, sticky='nsew')
        self.canvas.get_tk_widget().pack()

    def update_graph(self):

        while True:

            self.x_start += 1.0/self.sample_freq
            self.x_vals.append(self.x_start)
            self.x_vals = self.x_vals[-(self.time_span*self.sample_freq):]

            self.y_vals.append(random.randint(1, 100))
            self.y_vals = self.y_vals[-(self.time_span*self.sample_freq):]

            #print(self.x_vals)

            ax = self.myfig.gca()
            ax.lines[0].set_ydata(self.y_vals)
            ax.lines[0].set_xdata(self.x_vals)

            
            if len(self.x_vals) >= (self.time_span*self.sample_freq):
                x_min = self.x_vals[-(self.time_span*self.sample_freq)]
                x_max = self.x_vals[-1]
            else:
                x_min = self.x_vals[0]
                x_max = self.time_span

            ax.set_xlim(x_min, x_max)

            #ax.fill_between(self.x_vals[-2:], self.y_vals[-2:], color='#BC951A', alpha=0.2, label='Shaded Area')

            self.canvas.draw()

            time.sleep(int(1.0/self.sample_freq))

class ChannelGUI():
    def __init__(self, root, serial):
        self.root = root
        self.serial = serial
        self.padx = 5
        self.pady = 5

        self.frame = ttk.LabelFrame(self.root, text='Channels')

        ch_list = ['Press. 1', 'Press. 2', 'Temp. 1', 'Force. 1', ]
        for i in range(len(ch_list)):
            ttk.Label(self.frame, text=f'{ch_list[i]}').grid(column=0, row=i+1, padx=10, pady=self.pady)
            ttk.Checkbutton(self.frame, bootstyle='square-toggle').grid(column=1, row=i+1, padx=self.padx, pady=self.pady)

        self.publish()

    def publish(self):
        self.frame.grid(column=4, row=0, columnspan=1, rowspan=2, sticky='nsew', padx=self.padx, pady=self.pady)

class PIDGUI():
    def __init__(self, root, serial):
        self.root = root
        self.serial = serial
        self.padx = 5
        self.pady = 5

        self.frame = ttk.LabelFrame(self.root, text='P&ID Diagram')

        image_path = '/Users/jackgardiner/Desktop/TEST STAND CONTROL/control_gui/Liquid test stand.png'
        image1 = Image.open(image_path)
        image1.thumbnail((500,500))
        test = ImageTk.PhotoImage(image1)
        self.label1 = tk.Label(self.frame, image=test)
        self.label1.image = test

        self.as_timer()

        self.sol_n2 = ValveControlFrame(self.frame, 'N2', 'OPEN', 'MANUAL', 'N2 Control')
        self.sol_fu = ValveControlFrame(self.frame, 'FU', 'OPEN', 'MANUAL', 'Fuel Control')
        self.sol_ox = ValveControlFrame(self.frame, 'OX', 'OPEN', 'MANUAL', 'Oxidiser Control')

        self.publish()

    def publish(self):
        self.sol_n2.place(x=40, y=15)
        self.sol_fu.place(x=500, y=200)
        self.sol_ox.place(x=40, y=285)
        self.label1.pack()
        self.frame.grid(column=0, row=1, columnspan=4, rowspan=2, sticky='nsew', padx=self.padx, pady=self.pady)

    def as_timer(self):
        self.timer_frame = ttk.Frame(self.frame, padding=(3,3,3,3), bootstyle='danger')
        
        lbl_title = ttk.Label(self.timer_frame, text='Auto-Sequence Timer', font=('Helvetica', 14, 'bold'), anchor='center', bootstyle='danger')
        self.lbl_clock = ttk.Label(self.timer_frame, text='00:00:00', font=('Helvetica', 16, 'bold'), anchor='center')

        lbl_title.pack(fill='both', expand=True, ipadx=5)
        self.lbl_clock.pack(fill='both', expand=True, ipadx=5, ipady=5)

        self.timer_frame.place(x=482, y=15)
   
class StateGUI():
    def __init__(self, root, serial):
        self.root = root
        self.serial = serial
        self.padx = 5
        self.pady = 5
        self.btn_w = 12

        self.frame = ttk.LabelFrame(self.root, text='System State')

        self.btn_safe = ttk.Button(self.frame, text='SAFE', width=self.btn_w, bootstyle='success')
        self.btn_armed = ttk.Button(self.frame, text='ARMED', width=self.btn_w, bootstyle='warning', state='disabled')

        self.btn_manop = ttk.Button(self.frame, text='Manual Op.', width=self.btn_w)
        self.btn_stby = ttk.Button(self.frame, text='Standby', width=self.btn_w, bootstyle='outline')
        self.btn_tdepress = ttk.Button(self.frame, text='Tank De-Press.', width=self.btn_w, bootstyle='outline')

        self.btn_tpress = ttk.Button(self.frame, text='Tank Press.', width=self.btn_w, bootstyle='outline-danger')
        self.btn_fire = ttk.Button(self.frame, text='FIRE', width=self.btn_w, bootstyle='danger')

        self.btn_asrun = ttk.Button(self.frame, text="A/S Running", width=self.btn_w, bootstyle='success', state='disabled')
        self.btn_edpress = ttk.Button(self.frame, text="Emerg. De-Press.", width=self.btn_w, bootstyle='outline-danger')

        self.publish()

    def publish(self):
        self.btn_safe.grid(column=0, row=1, padx=self.padx, pady=self.pady)
        self.btn_armed.grid(column=0, row=2, padx=self.padx, pady=self.pady)

        ttk.Separator(self.frame, orient='vertical').place(relx=0.25, relheight=0.94)

        self.btn_manop.grid(column=2, row=0, padx=self.padx, pady=self.pady)
        self.btn_stby.grid(column=2, row=1, padx=self.padx, pady=self.pady)
        self.btn_tdepress.grid(column=2, row=2, padx=self.padx, pady=self.pady)

        self.btn_tpress.grid(column=3, row=0, padx=self.padx, pady=self.pady)
        self.btn_fire.grid(column=3, row=1, padx=self.padx, pady=self.pady)

        ttk.Separator(self.frame, orient='vertical').place(relx=0.75, relheight=0.94)

        self.btn_asrun.grid(column=5, row=0, padx=self.padx, pady=self.pady)
        self.btn_edpress.grid(column=5, row=1, padx=self.padx, pady=self.pady)

        self.frame.grid(column=0, row=3, columnspan=4, rowspan=1, sticky='nsew', padx=self.padx, pady=self.pady)

        [self.frame.rowconfigure(i, weight=1) for i in range(3)]
        [self.frame.columnconfigure(i, weight=1) for i in range(6)]

class RawGUI():
    def __init__(self, root, serial):
        self.root = root
        self.serial = serial
        self.padx = 5
        self.pady = 5

        self.frame = ttk.LabelFrame(self.root, text='Raw Serial Data')
        
        self.serial_text = ScrolledText(self.frame, width=40, height=16, padding=5, autohide=True)
        #self.serial_text.insert(END, 'hkskgdbfkhgb')

        self.input_box()
        self.publish()

        self.t2 = threading.Thread(target=self.print_serial, daemon=True)
        # self.t2.start()

    def input_box(self):
        self.input_frame = ttk.Frame(self.frame)
        
        self.serial_input = ttk.Entry(self.input_frame, width=29)
        self.serial_send = ttk.Button(self.input_frame, text='SEND', width=8, bootstyle='outline-warning')
    
        self.serial_input.pack(side='left')
        self.serial_send.pack(side='left')

    def publish(self):
        #self.button.pack()
        self.serial_text.pack()
        self.input_frame.pack()
        self.frame.grid(column=4, row=2, columnspan=2, rowspan=2, sticky='nsew', padx=self.padx, pady=self.pady)

    
    def print_serial(self):
        while True:
            rand_msg = str(random.randint(1,100))+'\n'
            self.serial_text.insert(END, rand_msg)
            self.serial_text.see(END)
            time.sleep(0.05)

class ParamsGUI():
    def __init__(self, root, serial):
        self.root = root
        self.serial = serial
        self.padx = 5
        self.pady = 5

        self.frame = ttk.LabelFrame(self.root, text='Parameters')

        self.notebook = ttk.Notebook(self.frame)

        self.serial_settings()
        self.as_settings()
        self.data_settings()

        self.publish()

    def serial_settings(self):
        self.params_serial = ttk.Frame(self.notebook)
        self.notebook.add(self.params_serial, text='Serial Com')

        ttk.Button(self.params_serial, text='serial button').pack()

    def as_settings(self):

        self.params_as = ttk.Frame(self.notebook)
        self.notebook.add(self.params_as, text='Auto-sequence')

        ttk.Button(self.params_as, text='a/s button').pack()

    def data_settings(self):

        self.params_data = ttk.Frame(self.notebook)

        self.save_folder = '/Users/jackgardiner/Desktop'

        params_label = ttk.Label(self.params_data, text='Save Path')
        #self.path_label = ttk.Label(self.params_data, text='/Users/jackgardiner/Desktop', bootstyle='inverse')
        self.btn_browse = ttk.Button(self.params_data, width=24, text=self.save_folder, bootstyle='light', command=self.update_save_dir)

        params_label.grid(column=0, row=0, padx=self.padx, pady=self.pady)
        #self.path_label.grid(column=1, row=0, padx=self.padx, pady=self.pady)
        self.btn_browse.grid(column=1, row=0, padx=self.padx, pady=self.pady)

        self.notebook.add(self.params_data, text='Data Logging')


    def publish(self):
        #self.button.pack()
        self.notebook.pack(expand=True, fill='both')

        self.frame.grid(column=6, row=2, columnspan=2, rowspan=2, sticky='nsew', padx=self.padx, pady=self.pady)

    def update_save_dir(self):
        self.save_path = filedialog.askdirectory()
        self.btn_browse.configure(text=self.save_path)

class ValveControlFrame(ttk.Frame):
    def __init__(self, parent, valve_ID, valve_state, valve_status, valve_name):
        super().__init__(parent)


        header_font = ('Helvetica', 12, 'bold')
        
        outline_frame = ttk.Frame(self, bootstyle='secondary', padding=(5, 5, 5, 5))

        lbl_name = ttk.Label(outline_frame, text=f'{valve_name}', font=header_font, anchor='center', bootstyle='inverse-secondary')
        lbl_status = ttk.Label(outline_frame, text=f'{valve_status}', anchor='center', bootstyle='inverse-success')
        btn_open = ttk.Button(outline_frame, text='OPEN', width=5, bootstyle='danger')
        btn_close = ttk.Button(outline_frame, text='CLOSE', width=5, bootstyle='danger', state='disabled')
        
        lbl_name.grid(row=0, column=0, columnspan=2, sticky='nsew')
        lbl_status.grid(row=1, column=0, columnspan=2, sticky='nsew')
        btn_open.grid(row=2, column=0, sticky='nsew')
        btn_close.grid(row=2, column=1, sticky='nsew')

        outline_frame.pack(expand=True, fill='both')

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=2)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        #self.place(x=x, y=y)