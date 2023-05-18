#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 15:48:16 2023

@author: zhetao
"""

from ctypes import *
import numpy as np
import numpy.ctypeslib as npct
from itertools import repeat
import math;
import string
from PyApex import AP2XXX
import time
import matplotlib.pyplot as plt

class AP2087A(object):
    # Constants
    name = 'AP2087A'
    numPWMSlots = 2
    maxPWMPoints = 100000
    isDetect = True
    isLaser = True
    isMotor = False
    isSMU = False
    isElec = False
    hasDetector = True

    sweepStartWvl = 1520e-9;
    sweepStopWvl = 1600e-9;
    sweepStepWvl = 0.04e-9;
    
    # dummy parameters
    sweepSpeed = '10nm';
    sweepUnit = 'dBm'
    sweepPower = 0;
    sweepLaserOutput = 'lowsse';
    sweepNumScans = 1;
    sweepPWMChannel = 3; # 0:1+2, 1: 1&2, 2:1,3:2
    sweepInitialRange = -20;
    sweepRangeDecrement = 20;
    sweepUseClipping = 1;
    sweepClipLimit = -100;
    
    def __init__(self):
        self.connected = False

    def __del__(self):
        if self.connected:
            self.disconnect()

    def connect(self, IPAddr = "160.254.88.3", reset=0, forceTrans=1, autoErrorCheck=1):
        """ Connects to the instrument.
        IPAddr -- instrument IP address
        reset -- Reset instrument after connecting
        """
        if self.connected:
            print('Already connected to the laser. Aborting connection.')
            return
        self.MyAP2087A = AP2XXX(IPAddr) #169.254.226.27
        self.OSA = self.MyAP2087A.OSA()
        self.PowerMeter = self.MyAP2087A.Powermeter()
        self.TLS = self.MyAP2087A.TLS()
        
        # dummy index and map
        self.pwmSlotIndex = [1, 2]
        self.pwmSlotMap = [(1,1), (1,2)]
        
        self.OSA.SetPolarizationMode('1&2') # use both detectors
        print('Connected to the laser')
        self.connected = True
        
        
    def sweep(self):
        """ Performs a wavelength sweep """
        
        self.OSA.SetPolarizationMode(self.sweepPWMChannel)
        self.OSA.SetStartWavelength(self.sweepStartWvl*1e9)
        self.OSA.SetStopWavelength(self.sweepStopWvl*1e9)
        self.OSA.DeactivateAutoNPoints()
        self.OSA.SetNPoints(int((self.sweepStopWvl-self.sweepStartWvl)/self.sweepStepWvl))
        print('start wlen = %2.2f, stop wlen = %2.2f, points = %d.' 
              %(self.OSA.GetStartWavelength(), self.OSA.GetStopWavelength(), self.OSA.GetNPoints()))
        Trace = self.OSA.Run()
        time.sleep(1)
        # If the single measurement is good (Trace > 0), we get the data in a list Data = [[Power Data], [Wavelength Data]]
        bASCII_data = True #TODO: [ZJ] not sure what it means
        if Trace > 0:
        	if bASCII_data == True:
        		Data = self.OSA.GetData(ScaleX = "nm", ScaleY = "log", TraceNumber = 1)
        	else:
        		Data = self.OSA.GetDataBin(ScaleX = "nm", ScaleY = "log", TraceNumber = 1)
                
        # Convert values from string representation to integers for the driver
        wavelengthArrPWM = np.asarray(Data[1])
        powerArrPWM = np.asarray(Data[0])
        # self.OSA.SetPolarizationMode('1&2')

        return (wavelengthArrPWM, powerArrPWM)

    def disconnect(self):
        self.MyAP2087A.Close()
        self.connected = False
        print('Disconnected from the laser')

    def readPWM(self, slot, chan):
        power = float(self.PowerMeter.GetPower(Polar=chan))
        print('%2.2f' %power, end = '')
        """ read a single wavelength """
        return power
    
    def setTLSState(self, state, slot='auto'):
        """ turn on or off"""
        if state == 'on':
            self.TLS.On()
        elif state == 'off':
            self.TLS.Off()
        else:
            print("Invalid input for laser status!")

        status = self.TLS.GetStatus()
        print("Laser status =", status)
        
    def setTLSWavelength(self, wavelength, selMode='manual', slot='auto'):
        # wavelength input unit: um
        self.TLS.SetWavelength(int(wavelength*1e9))
        time.sleep(0.150)
        dWL = self.TLS.GetWavelength()
        time.sleep(0.150)
        print("Set TLS wavelength = ", dWL)
        
    def setPWMPowerUnit(self, slot, chan, unit):
        # Set Power Unit 
        self.TLS.SetUnit(unit)    # dBm / mW
        print("Power Unit =", self.TLS.GetUnit())
        
    def setTLSPower(self, power, slot='auto', selMode='manual', unit='dBm'):
        self.TLS.SetPower(power)
        time.sleep(0.150)
        dPow = self.TLS.GetPower()
        time.sleep(0.150)
        # print("Get Static Power =", dPow)
        elf.checkError(res);
        
    # dummy function
    def getNumSweepChannels(self):
        return len(self.pwmSlotIndex);

    def setRangeParams(self, chan, initialRange, rangeDecrement, reset=0):
        print(initialRange)
        print(rangeDecrement)
        return;

    def setAutorangeAll(self): #TODO
        """ Turns on autorange for all detectors and sets units to dBm """
        # for slotinfo in self.pwmSlotMap:
        #     detslot = slotinfo[0];
        #     detchan = slotinfo[1]

        #     self.setPWMPowerUnit(detslot, detchan, 'dBm')
            # self.setPWMPowerRange(detslot, detchan, rangeMode='auto')
        return
    def findTLSSlots(self):
        """ Returns a list of all tunable lasers in the mainframe """
        return [0]
    

    def getNumPWMChannels(self):
        """ Returns the number of registered PWM channels """
        return 2;
    
    # def setPWMAveragingTime(self, slot, chan, avgTime):
    #     res = self.hp816x_set_PWM_averagingTime(self.hDriver, slot, chan, avgTime);
    #     self.checkError(res);


    # def setPWMPowerRange(self, slot, chan, rangeMode='auto', range=0):
    #     res = self.hp816x_set_PWM_powerRange(self.hDriver, slot, chan, self.rangeModeDict[rangeMode], range);
    #     self.checkError(res);
    
    # TLS.SetStartWL(1545.000)
    # start_wl = TLS.GetStartWL()
    # print("start WL =", start_wl)
    
    # TLS.SetStopWL(1650.000)
    # stop_wl = TLS.GetStopWL()
    # print("stop WL =", stop_wl)

    # def setPWMPowerRange(self, slot, chan, rangeMode='auto', range=0):
    #     res = self.hp816x_set_PWM_powerRange(self.hDriver, slot, chan, self.rangeModeDict[rangeMode], range);
    #     self.checkError(res);

    # def getSlotInstruments(self):
    #     """ Gets the name of each instrument in the slots """
    #     instStr = self.gpibQueryString('*OPT?')
    #     return list(map(string.strip, instStr[:-1].split(',')))

    def getName(self):
        return "AP2087A"

    def getDetector(self):
        return "AP2087A"

