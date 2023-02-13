import wx

import TDC001
import TDC001MotorPanel

# Panel in the Connect Instruments window which contains the connection settings for the Qontrol motors.
class TDC001MotorParameters(wx.Panel):
    name = 'Thorlabs TDC001 Controllers'

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
        self.instList = ("None",) + kwargs['visaAddrLst']
        self.num_axis = 4
        self.InitUI()

    def InitUI(self):
        """
        Initializes the user interface for connecting to the thorlabs actuators.
        """
        sb = wx.StaticBox(self, label='Thorlabs Connection Parameters')
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.paras = []
        self.para_tcs = []
        for i in range(self.num_axis):
            para = wx.BoxSizer(wx.HORIZONTAL)
            para_name = wx.StaticText(self, label=f'Serial Port {int(i+1)}')
            para_tc = wx.ComboBox(self, choices=self.instList)
            para_tc.SetValue("None")
            para.AddMany([(para_name, 1, wx.EXPAND), (para_tc, 1, wx.EXPAND)])
            self.paras.append((para, para_tc))

        self.disconnectBtn = wx.Button(self, label='Disconnect')
        self.disconnectBtn.Bind(wx.EVT_BUTTON, self.disconnect)
        self.disconnectBtn.Disable()

        self.connectBtn = wx.Button(self, label='Connect')
        self.connectBtn.Bind(wx.EVT_BUTTON, self.connect)

        hbox.AddMany([(self.disconnectBtn, 0), (self.connectBtn, 0)])
        vbox.AddMany([(para, 0, wx.EXPAND) for para, _ in self.paras] + [(hbox, 0)])

        self.SetSizer(vbox)

    def connect(self, event):
        self.stage = TDC001.TDC001Motor(self.num_axis)
        self.stage.connect([str(para_tc.GetValue()) for _, para_tc in self.paras])
        self.stage.panelClass = TDC001MotorPanel.topTDC001MotorPanel
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
