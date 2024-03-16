from enginecontrol import EngineControlGUI
from serial_com import SerialManager
from data import DataManager

data = DataManager()
serial = SerialManager()

app = EngineControlGUI(serial, data)
app.run()