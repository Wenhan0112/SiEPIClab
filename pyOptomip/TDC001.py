"""
TDC001 in development
"""

from thorlabs_apt_device import TDC001
import re
import math
import numpy as np
import time

class TDC001Motor:
    name = 'TDC001'
    isMotor = True
    isOpt = True
    isElec = False
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
        time.sleep(2)
        self.status = [t.status if t is not None else "No Connection Directed" for t in self.tdc]
        self.connections = np.array([tdc is not None for tdc in self.tdc], dtype=bool)
        self.position =  [(t.status['position']) if t is not None else "No Connection Directed" for t in self.tdc]
        print(self.status)
        print(f'Connections: {self.visaName}')
        print(self.position)
        for t in self.tdc:
            if t is not None:
                # increase the acceleration for faster tuning.
                t.set_velocity_params(acceleration = 10000, max_velocity = 1777830, bay=0, channel=0)

    def disconnect(self):
        [t.close() for t in self.tdc if t is not None]

    def moveRelative(self, axis, x):
        # TODO: make the inputs consistent with optical stage control.
        
        # if self.minPositionSet is False and x != 0:
        #     print('Please Set Minimum Position in X Axis.')
        axis_name = int(axis+1)
        if self.tdc[axis] is None:
            print(f"No TDC001 connected in Axis {axis_name}.")
            return
        # if self.position[axis] - x < self.minPosition[axis]:
        #     print(f"Cannot Move Past Minimum Position in Axis {axis_name}.")
        #     return
        
        # Z812b motor: 29nm/step
        self.tdc[axis].move_relative(distance=int(x*1000/29), bay=0, channel=0)
        time.sleep(0.35)

        self.position[axis] = self.tdc[axis].status['position']
        # self.position[axis] -= int(x*1000/29)
        
        # print(f"TDC001 Controller Moved in Axis {axis_name} by {-x} um!")

    def moveAbsolute(self, axis, x):
        axis_name = int(axis+1)
        if self.tdc[axis] is None:
            # print(f"No TDC001 connected in Axis {axis_name}.")
            return

        self.tdc[axis].move_absolute(int(x*1000/29))
        time.sleep(0.5)

        self.position[axis] = int(x*1000/29)
        # print(f"TDC001 Controller Moved to {x} um!")
        
        
    # temp function for fineAlign, need to fix the unit
    def moveRelativeXY(self, x, y):
        # unit: um
        self.moveRelative(0, x)
        self.moveRelative(1, y)
        
    def moveRelativeXYZ(self, x, y, z):
        # unit: um
        self.moveRelative(0, x)
        self.moveRelative(1, y)
        # self.moveRelative(2, z)
        
    def moveAbsoluteXYZ(self, x, y, z):
        # unit: um
        self.moveAbsolute(0, x)
        self.moveAbsolute(1, y)
        time.sleep(10)
        # self.moveRelative(2, z)
        
    def getPosition(self): # in um
        positions_um = [pos*29/1000 for pos in self.position]
        return positions_um

    def setMinPosition(self, axis, minPosition):
        self.minPosition[axis] = minPosition
        self.minPositionSet[axis] = True
