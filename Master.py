from GUI import RootGUI
from Serial import SerialControl
from Data import DataMaster

mySerial = SerialControl()
myData = DataMaster()

RootMaster = RootGUI(mySerial, myData)

# run
RootMaster.root.mainloop()