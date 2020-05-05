import numpy as np
import datetime
import os

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure

import wx, csv

VAR_WINDOW1 = 60*10 
VAR_WINDOW2 = 20*10 
SMOOTHING = 20

class MyFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self,parent, id, 'scrollable plot',
                style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER,
                size=(800, 400))
        self.panel = wx.Panel(self, -1)

        self.fig = Figure((5, 4), 75)
        self.canvas = FigureCanvasWxAgg(self.panel, -1, self.fig)
        self.scroll_range = 400
        self.canvas.SetScrollbar(wx.HORIZONTAL, 0, 5,
                                 self.scroll_range)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, -1, wx.EXPAND)

        self.panel.SetSizer(sizer)
        self.panel.Fit()

        self.init_data()
        self.init_plot()

        self.canvas.Bind(wx.EVT_SCROLLWIN, self.OnScrollEvt)
        self.canvas.Bind(wx.EVT_CHAR_HOOK, self.onKeyPress)

    def init_data(self):
        dtime = []
        time = []
        accZ = []
        with open(f"Data{os.sep}vids 5-3{os.sep}50357.csv", 'r') as f:
            data = csv.DictReader(f, delimiter=',')
            for row in data:
                time.append(int(row['time']))
                dtime.append(datetime.datetime.fromtimestamp(int(row['time_stamp'])/1000))
                accZ.append(float(row['accZ']))
        time = list(map(lambda x: x/10, map(lambda t: t-time[0], time)))

        # print(list(map(lambda x: x.strftime('%H:%M:%S'),dtime[:100])))
        self.t = np.array(dtime)
        self.x = np.array(accZ)
        self.fx = np.zeros(len(accZ))
        self.fx[0] = self.x[0]
        val = self.x[0]
        for i in range(1, len(self.x)):
            val += (self.x[i]-val) / SMOOTHING
            self.fx[i] = val

        self.var1 = np.zeros(len(accZ))
        self.var2 = np.zeros(len(accZ))
        for i in range(len(accZ)):
            self.var1[i] = np.var(accZ[max(0, i-VAR_WINDOW1//2):i+VAR_WINDOW1//2]) 
            self.var2[i] = np.var(accZ[max(0, i-VAR_WINDOW2//2):i+VAR_WINDOW2//2])
        # print(self.var1[:100])

        # Extents of data sequence:
        self.i_min = 0
        self.i_max = len(self.t)
        # print(self.i_max)

        # Size of plot window:
        self.i_window = 10*60*60
        self.scrollWindow = 10*60*10

        # Indices of data interval to be plotted:
        self.i_start = 0
        self.i_end = self.i_start + self.i_window

    def init_plot(self):
        self.topPlot = self.fig.add_subplot(311)
        self.midPlot = self.fig.add_subplot(312, sharex=self.topPlot)
        self.bottPlot = self.fig.add_subplot(313, sharex=self.topPlot)
        # self.topPlot.set_ylim(8,10)
        self.plot_rawAccZ = \
                  self.topPlot.plot(self.t[self.i_start:self.i_end],
                                 self.x[self.i_start:self.i_end], 'b,')[0]
        self.plot_smooth = \
                  self.topPlot.plot(self.t[self.i_start:self.i_end],
                                 self.fx[self.i_start:self.i_end])[0]

        self.plot_accZVar1 = \
                  self.midPlot.plot(self.t[self.i_start:self.i_end],
                                 self.var1[self.i_start:self.i_end])[0]
        
        self.plot_accZVar2 = \
                  self.bottPlot.plot(self.t[self.i_start:self.i_end],
                                 self.var2[self.i_start:self.i_end])[0]

    def draw_plot(self):

        # Update data in plot:
        self.plot_rawAccZ.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_smooth.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_accZVar1.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_accZVar2.set_xdata(self.t[self.i_start:self.i_end])

        self.plot_rawAccZ.set_ydata(self.x[self.i_start:self.i_end])
        self.plot_smooth.set_ydata(self.fx[self.i_start:self.i_end])
        self.plot_accZVar1.set_ydata(self.var1[self.i_start:self.i_end])
        self.plot_accZVar2.set_ydata(self.var2[self.i_start:self.i_end])

        # Adjust plot limits:
        self.topPlot.set_xlim((min(self.t[self.i_start:self.i_end]),
                           max(self.t[self.i_start:self.i_end])))
        self.midPlot.set_xlim((min(self.t[self.i_start:self.i_end]),
                           max(self.t[self.i_start:self.i_end])))
        self.bottPlot.set_xlim((min(self.t[self.i_start:self.i_end]),
                           max(self.t[self.i_start:self.i_end])))                           
        # self.topPlot.set_ylim((min(self.x[self.i_start:self.i_end]),
        #                     max(self.x[self.i_start:self.i_end])))
        self.topPlot.set_ylim(9.5,9.7 )
        # self.midPlot.set_ylim((min(self.var1[self.i_start:self.i_end]),
        #                     max(self.var1[self.i_start:self.i_end])))
        self.midPlot.set_ylim(0, 0.001)           
        self.bottPlot.set_ylim((min(self.var2[self.i_start:self.i_end]),
                            max(self.var2[self.i_start:self.i_end])))                 
        self.bottPlot.set_ylim(0, 0.001)           
        
        # Redraw:
        self.canvas.draw()

    def update_scrollpos(self, new_pos):
        self.i_start = self.i_min + new_pos
        self.i_end = self.i_min + self.i_window + new_pos
        self.canvas.SetScrollPos(wx.HORIZONTAL, new_pos)
        self.draw_plot()

    def OnScrollEvt(self, event):
        evtype = event.GetEventType()

        if evtype == wx.EVT_SCROLLWIN_THUMBTRACK.typeId:
            pos = event.GetPosition()
            self.update_scrollpos(pos)
        elif evtype == wx.EVT_SCROLLWIN_LINEDOWN.typeId:
            pos = self.canvas.GetScrollPos(wx.HORIZONTAL)
            self.update_scrollpos(pos + 6000)
        elif evtype == wx.EVT_SCROLLWIN_LINEUP.typeId:
            pos = self.canvas.GetScrollPos(wx.HORIZONTAL)
            self.update_scrollpos(pos - 6000)
        elif evtype == wx.EVT_SCROLLWIN_PAGEUP.typeId:
            pos = self.canvas.GetScrollPos(wx.HORIZONTAL)
            self.update_scrollpos(pos - 6000*5)
        elif evtype == wx.EVT_SCROLLWIN_PAGEDOWN.typeId:
            pos = self.canvas.GetScrollPos(wx.HORIZONTAL)
            self.update_scrollpos(pos + 6000*5)
        else:
            print("unhandled scroll event, type id:", evtype)

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode==wx.WXK_LEFT:
            self.updateGraph(-self.scrollWindow)
        elif keycode==wx.WXK_RIGHT:
            self.updateGraph(self.scrollWindow)
        else: event.Skip()

    def updateGraph(self, shift):
        self.i_start += shift
        self.i_end += shift
        # self.canvas.SetScrollPos(wx.HORIZONTAL, new_pos)
        self.draw_plot()

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None,id=-1)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()