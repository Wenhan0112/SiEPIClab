# The MIT License (MIT)

# Copyright (c) 2015 Michael Caverley

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# Version 1.1

import math
import numpy as np
import collections
import hp816x_instr
from time import sleep

class fineAlign(object):
    wavelength = 1550e-9  # Fine align wavelength
    laserPower = 0  # Laser power for fine align
    laserOutput = 'highpower'  # Which laser output to use
    laserSlot = 'auto'  # Which laser slot to use. Default to first found laser

    # A list containing the detectors which will be used for fine align. It will use the detector in
    # the first index, then the second etc...
    detectorPriority = [0]

    roughStepSize = 9
    fineStepSize = 3  # Stage step size in microns

    scanWindowSize = 50#50  # Size of square window which will be searched by fine align

    threshold = -59#-56  # Spiral search will stop once power is greater than the threshold

    numGradientIter = 25#50

    useCrosshair = 0  # Set to 1 to use crosshair search after gradient. Doesn't work very well.

    abort = False  # Can set to true to self.abort a fine align
    
    use_cache = True

    NO_ERROR = 0
    DEVICE_NOT_FOUND = 1
    FINE_ALIGN_ABORTED = 2
    def __init__(self, laser, stage):
        self.laser = laser
        self.stage = stage
        self.cache = collections.defaultdict(list)
        self.idx = (None, None)


    def doFineAlign(self):
        xStartPos = self.stage.getPosition()[0]
        yStartPos = self.stage.getPosition()[1]
        print('Performing fine alignment...')
        
        for det in [0]:#self.detectorPriority:
            self.cache = collections.defaultdict(list)
            self.idx = (0, 0)
            

            maxSteps = math.ceil(self.scanWindowSize / float(self.roughStepSize))
            # Get the detector slot number and channel for the chosen detector index
            detSlot = self.laser.pwmSlotMap[det][0]
            detChan = self.laser.pwmSlotMap[det][1]

            self.laser.setPWMPowerUnit(detSlot, detChan, 'dBm')
            
            # Try to set laser output. If the laser only has one output, an error is thrown
            # which will be ignored here
            # try:
            #     self.laser.setTLSOutput(self.laserOutput, slot=self.laserSlot)
            # except hp816x_instr.InstrumentError:
            #     pass
        
            self.laser.setTLSWavelength(self.wavelength, slot=self.laserSlot)
            # self.laser.setTLSPower(self.laserPower, slot=self.laserSlot)
            self.laser.setTLSState('on', slot=self.laserSlot)

            # Spiral search method
            res = self.spiralSearch(maxSteps, detSlot, detChan)
            if res == self.DEVICE_NOT_FOUND:
                xStopPos = self.stage.getPosition()[0]
                yStopPos = self.stage.getPosition()[1]
                self.stage.moveRelativeXY(xStartPos - xStopPos, yStartPos - yStopPos)
                print('Could not find a device using this detector.')
                continue
            elif res == self.FINE_ALIGN_ABORTED:
                print('Fine align self.aborted.')
                break
            print('Found a device. Optimizing power...')

            # Gradient search stage      
            res = self.gradientSearch(detSlot, detChan)

            # Crosshair method
            if self.useCrosshair:
                res = self.crosshairSearch(maxSteps, detSlot, detChan)
            self.laser.setAutorangeAll()
            print('\nFine align completed.')
            print('Final power is: 2.2f', self.laser.readPWM(detSlot, detChan))
            return res, True

        # Fine align failed  
        print('Fine align failed.')
        xStopPos = self.stage.getPosition()[0]
        yStopPos = self.stage.getPosition()[1]
        self.stage.moveRelativeXY(xStartPos - xStopPos, yStartPos - yStopPos)
        self.laser.setAutorangeAll()
        return res, False

    def read_power(self, det_slot, det_chan, force_sample=False, is_spiral = False):
        if not self.use_cache:
            return self.laser.readPWM(det_slot, det_chan)
        if self.cache[self.idx] and not force_sample:
            print(self.cache[self.idx][-1], end = '')
            return self.cache[self.idx][-1]
        power = self.laser.readPWM(det_slot, det_chan)
        if not is_spiral:
            self.cache[self.idx].append(power)
        return power

    def spiralSearch(self, maxSteps, detSlot, detChan):
        numSteps = 1
        print('spiral search started')
        # power = self.laser.readPWM(detSlot, detChan)
        power = self.read_power(detSlot, detChan, is_spiral = True)

        direction = 1

        # If threshold already met return right away
        if power > self.threshold:
            return self.NO_ERROR

        # Spiral search stage
        while power <= self.threshold and numSteps < maxSteps:
            # print('sprial step')
            
            # X movement
            for ii in range(1, numSteps + 1):
                # print('stage move x')
                # print(self.stepSize * direction)

                self.stage.moveRelativeXY(self.roughStepSize * direction, 0) # double the stepsize in sprial sweep
                self.idx = (self.idx[0]+direction, self.idx[1])
                # power = self.laser.readPWM(detSlot, detChan)
                power = self.read_power(detSlot, detChan, is_spiral = True)
                # print(power, end = '')
                
                if self.abort:
                    return self.FINE_ALIGN_ABORTED
                elif power > self.threshold:
                    return self.NO_ERROR

            # Y movement
            for ii in range(1, numSteps + 1):
                self.stage.moveRelativeXY(0, self.roughStepSize * direction)
                self.idx = (self.idx[0], self.idx[1]+direction)
                # power = self.laser.readPWM(detSlot, detChan)
                power = self.read_power(detSlot, detChan, is_spiral = True)
                if self.abort:
                    return self.FINE_ALIGN_ABORTED
                elif power > self.threshold:
                    return self.NO_ERROR
                    
            numSteps += 1

            # Swap sweep direction
            if direction == 1:
                direction = -1
            else:
                direction = 1

        return self.DEVICE_NOT_FOUND  # Return error

    def gradientSearch(self, detSlot, detChan):
        peakFoundCount = 0;  # Count how many consective peaks are found
        numConsecutivePeaks = 1;  # Need this many consecutive peaks to conclude the peak was found
        found_peak = False
        for ii in range(self.numGradientIter):
            if self.abort:
                return self.FINE_ALIGN_ABORTED
            # Always move in the direction of increasing power
            base_idx = self.idx
            # power = self.laser.readPWM(detSlot, detChan)
            sleep_time = 0.5
            
            print('\n(it = %d)' %ii, end='')
            power = self.read_power(detSlot, detChan, force_sample=found_peak)
            
            print('xpos ', end = '')
            self.stage.moveRelativeXY(self.fineStepSize, 0)
            sleep(sleep_time)
            self.idx = (base_idx[0]+1, base_idx[1])
            # power_posx = self.laser.readPWM(detSlot, detChan)
            power_posx = self.read_power(detSlot, detChan, force_sample=found_peak)
            if power_posx > power:
                peakFoundCount = 0
                continue

            print('xneg ', end = '')
            self.stage.moveRelativeXY(-2 * self.fineStepSize, 0)
            sleep(sleep_time)
            self.idx = (base_idx[0]-1, base_idx[1])
            # power_negx = self.laser.readPWM(detSlot, detChan)
            power_negx = self.read_power(detSlot, detChan, force_sample=found_peak)
            if power_negx > power:
                peakFoundCount = 0
                continue

            print('ypos ', end = '')
            self.stage.moveRelativeXY(self.fineStepSize, self.fineStepSize)
            sleep(sleep_time)
            self.idx = (base_idx[0], base_idx[1]+1)
            # power_posy = self.laser.readPWM(detSlot, detChan)
            power_posy = self.read_power(detSlot, detChan, force_sample=found_peak)
            if power_posy > power:
                peakFoundCount = 0
                continue

            print('yneg ', end = '')
            self.stage.moveRelativeXY(0, -2 * self.fineStepSize)
            sleep(sleep_time)
            self.idx = (base_idx[0], base_idx[1]-1)
            # power_negy = self.laser.readPWM(detSlot, detChan)
            power_negy = self.read_power(detSlot, detChan, force_sample=found_peak)
            if power_negy > power:
                peakFoundCount = 0
                continue

            self.stage.moveRelativeXY(0, self.fineStepSize)
            self.idx = base_idx
            if peakFoundCount == numConsecutivePeaks:
                return self.NO_ERROR

            peakFoundCount += 1
            found_peak = True

        return self.NO_ERROR

    def crosshairSearch(self, maxSteps, detSlot, detChan):
        # Search X direction
        self.stage.moveRelativeXY(-self.scanWindowSize / 2.0, 0)
        xStartPos = self.stage.getPosition()[0];
        yStartPos = self.stage.getPosition()[1];
        numSteps = int(self.scanWindowSize / float(self.fineStepSize))
        powerXVals = np.zeros(numSteps)
        sweepXCoords = np.zeros(numSteps)

        for ii in range(numSteps):
            if self.abort:
                return self.FINE_ALIGN_ABORTED
            powerXVals[ii] = self.laser.readPWM(detSlot, detChan)
            sweepXCoords[ii] = self.stage.getPosition()[0]
            self.stage.moveRelativeXY(self.fineStepSize, 0)

        maxPowerXIdx = np.argmax(powerXVals)
        maxPowerXPos = sweepXCoords[maxPowerXIdx]

        xStopPos = self.stage.getPosition()[0];
        yStopPos = self.stage.getPosition()[1];
        self.stage.moveRelativeXY(maxPowerXPos - xStopPos, yStartPos - yStopPos)

        # Search Y direction
        self.stage.moveRelativeXY(0, -self.scanWindowSize / 2.0)
        xStartPos = self.stage.getPosition()[0];
        yStartPos = self.stage.getPosition()[1];
        powerYVals = np.zeros(numSteps)
        sweepYCoords = np.zeros(numSteps)

        for ii in range(numSteps):
            if self.abort:
                return self.FINE_ALIGN_ABORTED
            powerYVals[ii] = self.laser.readPWM(detSlot, detChan)
            sweepYCoords[ii] = self.stage.getPosition()[1]
            self.stage.moveRelativeXY(0, self.fineStepSize)

        maxPowerYIdx = np.argmax(powerYVals)
        maxPowerYPos = sweepYCoords[maxPowerYIdx]

        xStopPos = self.stage.getPosition()[0];
        yStopPos = self.stage.getPosition()[1];
        self.stage.moveRelativeXY(maxPowerXPos - xStopPos, maxPowerYPos - yStopPos)

        return self.NO_ERROR
