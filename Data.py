class DataManager():
    def __init__(self) -> None:
        self.sync = "#?#\n"
        self.sync_ok = '!'
        self.start_stream = "#S#\n"
        self.stop_stream = "#T#\n"
        self.sync_channel = 0

        self.msg = []

        self.data_t = []
        self.data_x = []

    def decode_msg(self):
        temp = self.row_msg.decode('utf-8').rstrip('\n')
        if len(temp) > 0:
            self.msg = temp.split("#")