"""
TDC001 in development
"""

from thorlabs_apt_device import TDC001
import re
import math
import numpy as np

class TDC001Motor:
    name = 'TDC001'
    isMotor = True
    isOpt = False
    isElec = True
    isLaser = False
    isDetect = False
    isSMU = False

    def __init__(self, num_axis):
        self.tdc = None
        self.num_axis = num_axis
        self.position = np.zeros(num_axis)
        self.minPositionSet = np.zeros(num_axis, dtype=bool)
        self.minPosition = np.zeros(num_axis)
        self.connections = np.zeros(num_axis, dtype=bool)

    def connect(self, visa_names):
        self.visaName = visa_names
        self.tdc = []
        for visa_name in visa_names:
            if visa_name == "None":
                self.tdc.append(None)
            else:
                serial_port = "COM" + re.findall('[0-9]+', visa_name)[0]
                self.tdc.append(TDC001(serial_port=serial_port, home=False))
                # Potentially try home=True? Homing is probably needed after initialisation. Or just set the initial point as 0?
        [t.identify() for t in self.tdc if t is not None]
        self.status = [t.status if t is not None else None for t in self.tdc]
        self.connections = np.array([tdc is not None for tdc in self.tdc], dtype=bool)
        print(f'Connections: {self.visaName}')

    def disconnect(self):
        [t.close() for t in self.tdc if t is not None]

    def moveRelative(self, axis, x):
        # if self.minPositionSet is False and x != 0:
        #     print('Please Set Minimum Position in X Axis.')
        axis_name = int(axis+1)
        if self.tdc[axis] is None:
            print(f"No TDC001 connected in Axis {axis_name}.")
            return
        if self.position[axis] - x < self.minPosition[axis]:
            print(f"Cannot Move Past Minimum Position in Axis {axis_name}.")
            return
        self.tdc[axis].move_relative(distance=int(1000 * x), bay=0, channel=0)
        self.position[axis] -= x
        print(f"TDC001 Controller Moved in Axis {axis_name} by {-x} um!")
    
    
    def getPosition(self):
        return self.position

    def setMinPosition(self, axis, minPosition):
        self.minPosition[axis] = minPosition
        self.minPositionSet[axis] = True
