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
        self.position = 0
        self.minPositionSet = False
        self.minPosition = 0

    def connect(self, SerialPortName):
        self.visaName = SerialPortName
        numbers = re.findall('[0-9]+', SerialPortName)
        COM = "COM" + numbers[0]
        self.tdc = TDC001(serial_port=COM, home=False) 
            # Potentially try home=True? Homing is probably needed after initialisation. Or set the initial point as 0?
        self.tdc.identify()
        self.status = self.tdc.status
        print('Connected\n')

    def disconnect(self):
        self.tdc.close()

    def moveRelative(self, x):
        if self.minPositionSet is False and x != 0:
            print('Please Set Minimum Position in X Axis.')
        else:
            if self.position - x < self.minPosition:
                print("Cannot Move Past Minimum X Position.")
            else:
                self.tdc.move_relative(distance=int(1000 * x), bay=0, channel=0)
                self.position -= x


    def getPosition(self):
        return self.position

    def setMinXPosition(self, minPosition):
        self.minXPosition = minPosition
        self.minPositionSet = True

    def setMaxZPosition(self, maxPosition):
        self.maxZPosition = maxPosition
        self.maxZPositionSet = True
