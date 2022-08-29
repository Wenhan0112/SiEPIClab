class ElectroOpticDevice:

    def __init__(self, device_id, wavelength, polarization, x, y, type_):
        """Object used to store all information associated with an electro-optic device"""
        self.device_id = device_id
        self.wavelength = wavelength
        self.polarization = polarization
        self.type = type_

        self.opticalCoordinates = [x, y]
        self.electricalCoordinates = []

    def addElectricalCoordinates(self, padName, x, y):
        """Associates a bondpad with the device"""
        self.electricalCoordinates.append([padName, x, y])

    def getOpticalCoordinates(self):
        """Returns the coordinates of the optical input for the device as [x coordinate, y coordinate]"""
        return self.opticalCoordinates

    def getElectricalCoordinates(self):
        """Return a list of electrical bondpads. Bondpads are stored as lists in the form [pad name,
        x coordinate, y coordinate]"""
        return self.electricalCoordinates

    def getDeviceID(self):
        """Returns the device id of the device. IDs should be unique for each device within a chip"""
        return self.device_id

    def getDeviceType(self):
        """Returns the type of the device"""
        x = self.type.split(',')
        return x[0]

    def getReferenceBondPad(self):
        """Returns the name and coordinates of the left-most bond pad within
        an electro-optic device in the form of a list [bond pad name, x coordinates, y coordinates]"""
        reference = self.electricalCoordinates[0]
        for bondPad in self.electricalCoordinates:
            if bondPad[1] < reference[1]:
                reference = bondPad
        return reference

