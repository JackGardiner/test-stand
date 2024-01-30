class AutoSequencer():
    def __init__(self):
        pass

    def start_stream(self, ConnGUI):
        print('start stream')
        ConnGUI.ch_status.configure(text='WOOHOO')
        ConnGUI.btn_start_stream.configure(state='disabled')

    def stop_stream(self, ConnGUI):
        print('stop stream')