class DataMaster():
    def __init__(self):
        self.sync = "#?#\n"
        self.sync_ok = '!'
        self.StartStream = "#S#\n"
        self.StopStream = "#T#\n"
        self.SynchChannel = 0

        self.msg = []

        self.XData = []
        self.YData = []
        pass

    def DecodeMsg(self):
        temp = self.RowMsg.decode('utf-8').rstrip('\n')
        if len(temp) > 0:
            self.msg = temp.split("#")
            # print(f"Before removing index :{self.msg}")
            # del self.msg[0]
            # print(f"After removing index :{self.msg}")

    def GenChannels(self):
        self.Channels = [f"Ch{ch}" for ch in range(self.SynchChannel)]

    def buildYdata(self):
        for _ in range(self.SynchChannel):
            self.YData.append([])

    def ClearData(self):
        self.RowMsg = ""
        self.msg = []
        self.Ydata = []