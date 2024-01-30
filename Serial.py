import serial.tools.list_ports
import time
from ttkbootstrap.constants import *

class SerialControl():
    def __init__(self):
        '''
        Initializing the main varialbles for the serial data
        '''
        self.sync_cnt = 200

    def getCOMList(self):
        ports = serial.tools.list_ports.comports()
        self.com_list = [com[0] for com in ports]
        self.com_list.insert(0, '- select -')

    def SerialOpen(self, ComGUI):
        try:
            self.ser.is_open
        except:
            PORT = ComGUI.selected_com.get()
            BAUD = ComGUI.selected_baud.get()
            self.ser = serial.Serial()
            self.ser.baudrate = BAUD
            self.ser.port = PORT
            self.ser.timeout = 0.1

        try:
            if self.ser.is_open:
                print("Already Open")
                ComGUI.conn.raw.serial_text.insert(END, f"Already open!\n")
                ComGUI.conn.raw.serial_text.see(END)
                self.ser.status = True
            else:
                PORT = ComGUI.selected_com.get()
                BAUD = ComGUI.selected_baud.get()
                self.ser = serial.Serial()
                self.ser.baudrate = BAUD
                self.ser.port = PORT
                self.ser.timeout = 0.1
                self.ser.open()
                self.ser.status = True
        except:
            self.ser.status = False

    def SerialSync(self, ComGUI):
        self.threading = True
        cnt = 0
        while self.threading:
            try:
                self.ser.write(ComGUI.data.sync.encode('utf-8'))
                ComGUI.conn.sync_status["text"] = "..Sync.."
                ComGUI.conn.sync_status.configure(bootstyle='warning')
                ComGUI.data.RowMsg = self.ser.readline()
                # print(f"RowMsg: {ComGUI.data.RowMsg}")
                ComGUI.data.DecodeMsg()
                # print(f"Decoded message: {ComGUI.data.msg}")
                print(f'got an incoming message: {ComGUI.data.msg}')
                ComGUI.conn.raw.serial_text.insert(END, f"-- {ComGUI.data.msg[2]} CHANNEL(S) DETECTED -- \n")
                ComGUI.conn.raw.serial_text.see(END)
                if ComGUI.data.sync_ok in ComGUI.data.msg[1]:
                    if int(ComGUI.data.msg[2]) > 0:
                        #print(f'sync is good! got an incoming message: {ComGUI.data.msg}')
                        ComGUI.conn.btn_start_stream["state"] = "active"
                        ComGUI.conn.sync_status["text"] = "OK"
                        ComGUI.conn.sync_status.configure(bootstyle = "success")
                        ComGUI.conn.ch_status["text"] = ComGUI.data.msg[2]
                        ComGUI.conn.ch_status.configure(bootstyle = "success")
                        ComGUI.data.SynchChannel = int(ComGUI.data.msg[2])
                        ComGUI.data.GenChannels()
                        ComGUI.data.buildYdata()
                        print(ComGUI.data.Channels, ComGUI.data.YData)
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
                cnt = 0
                ComGUI.conn.sync_status["text"] = "failed"
                ComGUI.conn.sync_status.configure(bootstyle = "warning")
                time.sleep(0.5)
                if self.threading == False:
                    break

    def SerialStart(self, ConnGUI):

        try:
            self.ser.write(ConnGUI.data.StartStream.encode('utf8'))
            ConnGUI.raw.serial_text.insert(END, f"-- DATA STREAM STARTED --\n")
            ConnGUI.raw.serial_text.see(END)
        except Exception as e:
            print(e)

        self.threading = True
        while self.threading:
            try:
                ConnGUI.data.RowMsg = self.ser.readline()
                # print(f"RowMsg: {ComGUI.data.RowMsg}")
                ConnGUI.data.DecodeMsg()
                print(f"Decoded message: {ConnGUI.data.msg}")
                ConnGUI.raw.serial_text.insert(END, f"{ConnGUI.data.msg}\n")
                ConnGUI.raw.serial_text.see(END)
                # self.threading = False
            except Exception as e:
                print(e)
                self.threading = False
                break

            ConnGUI.btn_start_stream["state"] = "disabled"
            ConnGUI.btn_stop_stream["state"] = "active"

    def SerialClose(self, ComGUI):
        try:
            self.ser.is_open
            self.ser.close()
            self.ser.status = False
        except:
            self.ser.status = False

    def SerialStop(self, ConnGUI):
        self.threading = False
        print(f'-- DATA STREAM STOPPED --')
        ConnGUI.raw.serial_text.insert(END, f'-- DATA STREAM STOPPED --\n')
        ConnGUI.raw.serial_text.see(END)
        self.ser.write(ConnGUI.data.StopStream.encode('utf8'))

        ConnGUI.btn_start_stream["state"] = "active"
        ConnGUI.btn_stop_stream["state"] = "disabled"