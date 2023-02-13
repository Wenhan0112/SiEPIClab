import wx


# Panel that appears in the main window which contains the controls for the Thorlabs motors.
class topTDC001MotorPanel(wx.Panel):
    def __init__(self, parent, motor):
        super(topTDC001MotorPanel, self).__init__(parent)
        self.tdc = motor
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='Wedge Probe Stage')
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        for axis in range(0, self.tdc.num_axis):
            if self.tdc.connections[axis]:
                motorPanel = TDC001Panel(self, axis)
                vbox.Add(motorPanel, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)
                vbox.Add((-1, 2))
                vbox.Add(wx.StaticLine(self), flag=wx.EXPAND, border=0, proportion=0)
                vbox.Add((-1, 2))

        self.SetSizer(vbox)


class TDC001Panel(wx.Panel):

    def __init__(self, parent, axis):
        super(TDC001Panel, self).__init__(parent)
        self.parent = parent
        self.axis = axis
        self.InitUI()

    def InitUI(self):

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label=str(int(self.axis+1)))
        hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)
        st1 = wx.StaticText(self, label='')
        hbox.Add(st1, flag=wx.EXPAND, border=8, proportion=1)
        btn1 = wx.Button(self, label='-', size=(50, 20))
        btn2 = wx.Button(self, label='+', size=(50, 20))

        self.initialvalue = 100

        hbox.Add(btn1, flag=wx.EXPAND | wx.RIGHT, proportion=0, border=8)
        btn1.Bind(wx.EVT_BUTTON, self.OnButton_MinusButtonHandler)
        self.tc = wx.TextCtrl(self, value=str(self.initialvalue))  # change str(self.axis) to '0'
        self.tc.Bind(wx.EVT_TEXT, self.movementcheck)

        hbox.Add(self.tc, proportion=2, flag=wx.EXPAND)
        st1 = wx.StaticText(self, label='um')
        hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)
        hbox.Add(btn2, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=8)
        btn2.Bind(wx.EVT_BUTTON, self.OnButton_PlusButtonHandler)
        self.SetSizer(hbox)

    def getMoveValue(self):
        try:
            val = float(self.tc.GetValue())
        except ValueError:
            self.tc.SetValue('0')
            print("Value Error")
            return 0.0
        return val

    def OnButton_MinusButtonHandler(self, event):

        self.parent.tdc.moveRelative(self.axis, int(self.getMoveValue()))
        print(f"Axis {self.axis+1} Moved Negative")


    def OnButton_PlusButtonHandler(self, event):
        self.parent.tdc.moveRelative(self.axis, int((-1)*self.getMoveValue()))
        print(f"Axis {self.axis+1} Moved Positive")

    def movementcheck(self, event):

        self.inputcheck('thorlabs')
        if self.inputcheckflag == False:
            print("***********************************************")
            self.tc.SetValue('')
            return

    def inputcheck(self, setting):

        self.inputcheckflag = True

        if setting == 'thorlabs':

            if self.tc.GetValue() == '':
                return True

            if self.tc.GetValue().isnumeric() == False:
                self.inputcheckflag = False
                print('Please check move value')
            else:
                if float(self.tc.GetValue()) >= 10000:
                    self.inputcheckflag = False
                    print('Movement value cannot be larger than 10000')
