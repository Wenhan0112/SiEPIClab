"""
TDC001 in development
"""

from thorlabs_apt_device import TDC001
import re
import math


class TDC001Motor:
    name = 'TDC001'
    isMotor = True
    isOpt = False
    isElec = True
    isLaser = False
    isDetect = False
    isSMU = False

    def __init__(self):
        self.tdc = None
        self.position = [0, 0]
        self.minPositionSet = [False, False]
        self.minPosition = [0, 0]

    def connect(self, SerialPortName1, SerialPortName2):
        self.visaName = [SerialPortName1, SerialPortName2]
        numbers = [re.findall('[0-9]+', spn) for spn in self.visaName]
        COM = ["COM" + n[0] for n in numbers]
        self.tdc = [TDC001(serial_port=c, home=False) for c in COM]
            # Potentially try home=True? Homing is probably needed after initialisation. Or just set the initial point as 0?
        [t.identify() for t in self.tdc]
        self.status = [t.status for t in self.tdc]
        print('Connected\n')

    def disconnect(self):
        [t.close for t in self.tdc]

    def moveRelativeX(self, x):
        # if self.minPositionSet is False and x != 0:
        #     print('Please Set Minimum Position in X Axis.')
        if self.position[0] - x < self.minPosition[0]:
            print("Cannot Move Past Minimum X Position.")
        else:
            self.tdc[0].move_relative(distance=int(1000 * x), bay=0, channel=0)
            self.position[0] -= x
            print("TDC Controlled Moved in X Axis!")
    
    def moveRelativeX(self, y):
        # if self.minPositionSet is False and x != 0:
        #     print('Please Set Minimum Position in X Axis.')
        if self.position[1] - y < self.minPosition[1]:
            print("Cannot Move Past Minimum XYPosition.")
        else:
            self.tdc[1].move_relative(distance=int(1000 * y), bay=0, channel=0)
            self.position[1] -= y
            print("TDC Controlled Moved in Y Axis!")
    def getPosition(self):
        return self.position

    def setMinXPosition(self, minPosition):
        self.minPosition[0] = minPosition
        self.minPositionSet[0] = True

    def setMinYPosition(self, minPosition):
        self.minPosition[1] = minPosition
        self.minPositionSet[1] = True
