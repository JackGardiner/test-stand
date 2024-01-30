from GUI import RootGUI
from Serial import SerialControl
from Data import DataMaster

mySerial = SerialControl()
myData = DataMaster()

RootMaster = RootGUI(mySerial, myData)
#RootMaster.root.focus_force()

# run
RootMaster.root.mainloop()