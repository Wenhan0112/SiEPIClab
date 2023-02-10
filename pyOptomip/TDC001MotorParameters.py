import wx

import TDC001
import TDC001MotorPanel

# Panel in the Connect Instruments window which contains the connection settings for the Qontrol motors.
class TDC001MotorParameters(wx.Panel):
    name = 'Thorlabs Stage: Electrical Probing'

    def __init__(self, parent, connectPanel, **kwargs):
        """
        Initializes the connection panel for the qontrol actuators within the instrument connection panel.
        Args:
            parent:
            connectPanel:
            **kwargs:
        """
        super(TDC001MotorParameters, self).__init__(parent)
        self.connectPanel = connectPanel
        self.instList = kwargs['visaAddrLst']
        self.InitUI()

    def InitUI(self):
        """
        Initializes the user interface for connecting to the thorlabs actuators.
        """
        sb = wx.StaticBox(self, label='Thorlabs Connection Parameters')
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # First Parameter: Serial Port
        self.para1 = wx.BoxSizer(wx.HORIZONTAL)
        self.para1name = wx.StaticText(self, label='Serial Port')
        self.para1tc = wx.ComboBox(self, choices=self.instList)
        for x in self.instList:
            if x == 'ASRL10::INSTR':
                self.para1tc.SetValue('ASRL10::INSTR')
        # self.para1tc = wx.TextCtrl(self,value='ASRL5::INSTR')
        self.para1.AddMany([(self.para1name, 1, wx.EXPAND), (self.para1tc, 1, wx.EXPAND)])

        self.disconnectBtn = wx.Button(self, label='Disconnect')
        self.disconnectBtn.Bind(wx.EVT_BUTTON, self.disconnect)
        self.disconnectBtn.Disable()

        self.connectBtn = wx.Button(self, label='Connect')
        self.connectBtn.Bind(wx.EVT_BUTTON, self.connect)

        hbox.AddMany([(self.disconnectBtn, 0), (self.connectBtn, 0)])
        vbox.AddMany([(self.para1, 0, wx.EXPAND), (self.para2, 0, wx.EXPAND), (hbox, 0)])

        self.SetSizer(vbox)

    def connect(self, event):
        self.stage = TDC001.TDC001Motor()
        self.stage.connect(str(self.para1tc.GetValue()))
        self.stage.panelClass = TDC001MotorPanel.topBSC203MotorPanel
        self.connectPanel.instList.append(self.stage)
        print("Connected to Thorlabs Stage.")
        self.disconnectBtn.Enable()
        self.connectBtn.Disable()

    def disconnect(self, event):
        self.stage.disconnect()
        if self.stage in self.connectPanel.instList:
            self.connectPanel.instList.remove(self.stage)
        self.disconnectBtn.Disable()
        self.connectBtn.Enable()
