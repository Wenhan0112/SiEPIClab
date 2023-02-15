#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 15:48:16 2023

@author: zhetao
"""

from ctypes import *
import numpy as np;
import numpy.ctypeslib as npct;
from itertools import repeat;
import math;
import string
from PyApex import AP2XXX
import time

class AP2087A(object):
    # Constants
    name = 'AP2087A'
    numPWMSlots = 2
    maxPWMPoints = 100000
    isDetect = True
    isLaser = True
    isSMU = False
    isElec = False
    hasDetector = True

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
        self.MyPowerMeter = self.MyAP2087A.Powermeter()
        self.MyTLS = self.MyAP2087A.TLS()
        
        print('Connected to the laser')
        self.connected = True


    def sweep(self):
        """ Performs a wavelength sweep """
        Trace = self.OSA.Run()
        # If the single is good (Trace > 0), we get the data in a list Data = [[Power Data], [Wavelength Data]]
        bASCII_data = True
        if Trace > 0:
        	if bASCII_data == True:
        		 Data = MyOSA.GetData("nm","log",1)
        	else:
        		Data = MyOSA.GetDataBin("nm","log",1)
        # Convert values from string representation to integers for the driver
        wavelengthArrPWM = Data[1]
        powerArrPWM = Data[0]
        return (wavelengthArrPWM, powerArrPWM)

    # def getLambdaScanResult(self, chan, useClipping, clipLimit, numPts):
    #     """ Gets the optical power results from a sweep. """
    #     wavelengthArr = np.zeros(int(numPts))
    #     powerArr = np.zeros(int(numPts))
    #     res = self.hp816x_getLambdaScanResult(self.hDriver, chan, useClipping, clipLimit, powerArr, wavelengthArr)
    #     self.checkError(res)
    #     return wavelengthArr, powerArr

    def disconnect(self):
        self.MyAP2087A.Close()
        self.connected = False
        print('Disconnected from the laser')

    # def getNumPWMChannels(self):
    #     """ Returns the number of registered PWM channels """
    #     return numPWMChan;

    def getNumSweepChannels(self):
        return len(self.pwmSlotIndex);

    # def setRangeParams(self, chan, initialRange, rangeDecrement, reset=0):
    #     return;

    def setAutorangeAll(self):
        """ Turns on autorange for all detectors and sets units to dBm """
        for slotinfo in self.pwmSlotMap:
            detslot = slotinfo[0];
            detchan = slotinfo[1]

            self.setPWMPowerUnit(detslot, detchan, 'dBm')
            self.setPWMPowerRange(detslot, detchan, rangeMode='auto')

    def readPWM(self, slot, chan):
        """ read a single wavelength """
        return float(MyPowerMeter.GetPower());

    # def setPWMAveragingTime(self, slot, chan, avgTime):
    #     res = self.hp816x_set_PWM_averagingTime(self.hDriver, slot, chan, avgTime);
    #     self.checkError(res);


    # def setPWMPowerRange(self, slot, chan, rangeMode='auto', range=0):
    #     res = self.hp816x_set_PWM_powerRange(self.hDriver, slot, chan, self.rangeModeDict[rangeMode], range);
    #     self.checkError(res);
    
    # MyTLS.SetStartWL(1545.000)
    # start_wl = MyTLS.GetStartWL()
    # print("start WL =", start_wl)
    
    # MyTLS.SetStopWL(1650.000)
    # stop_wl = MyTLS.GetStopWL()
    # print("stop WL =", stop_wl)

    def setPWMPowerUnit(self, slot, chan, unit):
        # Set Power Unit 
        MyTLS.SetPRWUnit(0)    # dBm 
        # MyTLS.SetPRWUnit(1)  # mW
        print("Power Unit =", MyTLS.GetPRWUnit())

    # def setPWMPowerRange(self, slot, chan, rangeMode='auto', range=0):
    #     res = self.hp816x_set_PWM_powerRange(self.hDriver, slot, chan, self.rangeModeDict[rangeMode], range);
    #     self.checkError(res);

    def setTLSState(self, state, slot='auto'):
        """ turn on or off"""
        if state == 'on':
            self.MyTLS.On()
        elif state == 'off':
            self.MyTLS.Off()
        else:
            print("Invalid input for laser status!")

        status = self.MyTLS.GetStatus()
        print("Laser status =", status)
        
        
    def setTLSWavelength(self, wavelength, selMode='manual', slot='auto'):
        self.MyTLS.SetWavelength(wavelength)
        time.sleep(0.150)
        dWL = self.MyTLS.GetWavelength()
        time.sleep(0.150)
        print("Get Static WL =", dWL)
        
    def setTLSPower(self, power, slot='auto', selMode='manual', unit='dBm'):
        self.MyTLS.SetPower(power)
        time.sleep(0.150)
        dPow = self.MyTLS.GetPower()
        time.sleep(0.150)
        print("Get Static Power =", dPow)
        elf.checkError(res);




    # def getSlotInstruments(self):
    #     """ Gets the name of each instrument in the slots """
    #     instStr = self.gpibQueryString('*OPT?')
    #     return list(map(string.strip, instStr[:-1].split(',')))

    # def findClosestValIdx(self, array, value):
    #     idx = (abs(array - value)).argmin()
    #     return idx

    def getName(self):
        return "AP2087A"



