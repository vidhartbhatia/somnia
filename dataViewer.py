import csv
import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import numpy as np
import datetime
import os

import matplotlib
matplotlib.use('WXAgg')


VAR_WINDOW1 = 60*10
VAR_WINDOW2 = 10*60*10
SMOOTHING = 20


class MyFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'scrollable plot',
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
        accY = []
        accX = []
        tags = []
        tags2 = []

        # with open(f"50615.csv", 'r') as f:
        #     data = csv.DictReader(f, delimiter=',')
        #     for row in data:
        #         # if len(tags) >=10000: break
        #         phase = int(row['phase'])
        #         if (phase != -1):
        #             tags.extend([phase]*600)
        # with open(f"Tagging{os.sep}vis_tagging_506_final.csv", 'r') as f:
        with open(f"Data{os.sep}vids 5-8{os.sep}50824.csv", 'r') as f:
            data = csv.DictReader(f, delimiter=',')
            for row in data:
                # if len(tags) >=10000: break
                phase = int(row['phase'])
                if phase != -1:
                    tags.extend([phase]*600)
                # tags2.extend([int(row['tags'])]*600)

        tags2 = tags
        # for 4-26 1587887526800
        # 4-17 1587115911544
        # 420 - 1587368475096
        # vids 5-6

        with open(f"Data{os.sep}vids 5-8{os.sep}50824.csv", 'r') as f:
            data = csv.DictReader(f, delimiter=',')
            index = 0
            for row in data:
                if len(dtime) >= len(tags):
                    break
                time.append(int(row['time']))
                if index == 0:
                    dtime.append(
                        datetime.datetime.fromtimestamp(int(1588929844328)/1000))
                else:
                    dtime.append(dtime[index-1] +
                                 datetime.timedelta(milliseconds=100))
                # dtime.append(datetime.datetime.fromtimestamp(int(row['time_stamp'])/1000))
                accZ.append(float(row['accZ']))
                accY.append(float(row['accY']))
                accX.append(float(row['accX']))
                index += 1
        # time = list(map(lambda x: x, map(lambda t: t-time[0], time)))

        # tags.extend([5] * (len(time) - len(tags)))
        print(len(dtime), len(tags))
        # time = time[:len(tags)]
        assert(len(dtime) == len(tags))
        # print(list(map(lambda x: x.strftime('%H:%M:%S'),dtime[:100])))
        self.t = np.array(dtime)
        self.accZ = np.array(accZ)
        self.accY = np.array(accY)
        self.accX = np.array(accX)
        self.tags = np.array(tags)
        self.tags2 = np.array(tags2)

        # self.fx = np.zeros(len(accZ))
        # self.fx[0] = self.accZ[0]
        # val = self.accZ[0]
        # for i in range(1, len(self.accZ)):
        #     val += (self.accZ[i]-val) / SMOOTHING
        #     self.fx[i] = val

        self.varZ = np.zeros(len(accZ))
        self.varY = np.zeros(len(accY))
        self.varX = np.zeros(len(accX))
        self.varAcc = np.zeros(len(accZ))

        for i in range(len(accZ)):
            self.varZ[i] = np.var(
                self.accZ[max(0, i-VAR_WINDOW1):i])
            self.varY[i] = np.var(
                self.accY[max(0, i-VAR_WINDOW1):i])
            self.varX[i] = np.var(
                self.accX[max(0, i-VAR_WINDOW1):i])
            self.varAcc[i] = self.varZ[i]+self.varX[i]+self.varY[i]

        self.varZ2 = np.zeros(len(accZ))
        self.varY2 = np.zeros(len(accY))
        self.varX2 = np.zeros(len(accX))
        self.varAcc2 = np.zeros(len(accZ))
        for i in range(len(accZ)):
            self.varZ2[i] = np.var(
                self.accZ[max(0, i-VAR_WINDOW2):i])
            self.varY2[i] = np.var(
                self.accY[max(0, i-VAR_WINDOW2):i])
            self.varX2[i] = np.var(
                self.accX[max(0, i-VAR_WINDOW2):i])
            self.varAcc2[i] = self.varZ2[i]+self.varX2[i]+self.varY2[i]
        # print(self.varZ[:100])


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
        # self.topPlot = self.fig.add_subplot(211)
        self.midPlot = self.fig.add_subplot(211)
        self.bottPlot = self.fig.add_subplot(212, sharex=self.midPlot)

        # self.topPlot.set_ylim(8,10)
        # self.plot_rawAccZ = \
        #           self.topPlot.plot(self.t[self.i_start:self.i_end],
        #                          self.accZ[self.i_start:self.i_end], 'b,')[0]
        # self.plot_smooth = \
        #           self.topPlot.plot(self.t[self.i_start:self.i_end],
        #                          self.fx[self.i_start:self.i_end])[0]

        # self.plot_accVarZ = \
        #           self.midPlot.plot(self.t[self.i_start:self.i_end],
        #                          self.varZ[self.i_start:self.i_end], 'g', linewidth=0.5)[0]

        # self.plot_accVarY = \
        #           self.midPlot.plot(self.t[self.i_start:self.i_end],
        #                          self.varY[self.i_start:self.i_end], 'r', linewidth=0.5)[0]
        # self.plot_accVarX = \
        #           self.midPlot.plot(self.t[self.i_start:self.i_end],
        #                          self.varX[self.i_start:self.i_end], 'b', linewidth=0.5)[0]
        self.plot_accVar = \
            self.midPlot.plot(self.t[self.i_start:self.i_end],
                              self.varAcc[self.i_start:self.i_end], 'b',)[0]

        self.plot_accVar2 = \
            self.midPlot.plot(self.t[self.i_start:self.i_end],
                              self.varAcc2[self.i_start:self.i_end], 'g')[0]
        self.plot_tags = \
            self.bottPlot.plot(self.t[self.i_start:self.i_end],
                               self.tags[self.i_start:self.i_end], 'b', label='predicted')[0]
        self.plot_tags2 = \
            self.bottPlot.plot(self.t[self.i_start:self.i_end],
                               self.tags2[self.i_start:self.i_end], 'r', label='labeled')[0]
        self.bottPlot.legend([self.plot_tags, self.plot_tags2])

        self.midPlot.set_ylim(0, 0.01)
        self.bottPlot.set_ylim(0, 3.1)

    def draw_plot(self):

        # Update data in plot:
        # self.plot_rawAccZ.set_xdata(self.t[self.i_start:self.i_end])
        # self.plot_smooth.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_accVar.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_accVar2.set_xdata(self.t[self.i_start:self.i_end])

        # self.plot_accVarZ.set_xdata(self.t[self.i_start:self.i_end])
        # self.plot_accVarY.set_xdata(self.t[self.i_start:self.i_end])
        # self.plot_accVarX.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_tags.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_tags2.set_xdata(self.t[self.i_start:self.i_end])

        # self.plot_rawAccZ.set_ydata(self.accZ[self.i_start:self.i_end])
        # self.plot_smooth.set_ydata(self.fx[self.i_start:self.i_end])
        self.plot_accVar.set_ydata(self.varAcc[self.i_start:self.i_end])
        self.plot_accVar2.set_ydata(self.varAcc2[self.i_start:self.i_end])
        # self.plot_accVarZ.set_ydata(self.varZ[self.i_start:self.i_end])
        # self.plot_accVarY.set_ydata(self.varY[self.i_start:self.i_end])
        # self.plot_accVarX.set_ydata(self.varX[self.i_start:self.i_end])
        self.plot_tags.set_ydata(self.tags[self.i_start:self.i_end])
        self.plot_tags2.set_ydata(self.tags2[self.i_start:self.i_end])

        # Adjust plot limits:
        # self.topPlot.set_xlim((min(self.t[self.i_start:self.i_end]),
        #    max(self.t[self.i_start:self.i_end])))
        self.midPlot.set_xlim((min(self.t[self.i_start:self.i_end]),
                               max(self.t[self.i_start:self.i_end])))
        self.bottPlot.set_xlim((min(self.t[self.i_start:self.i_end]),
                                max(self.t[self.i_start:self.i_end])))
        # self.topPlot.set_ylim((min(self.accZ[self.i_start:self.i_end]),
        #                     max(self.accZ[self.i_start:self.i_end])))
        # self.topPlot.set_ylim(9.5,9.7 )
        # self.midPlot.set_ylim((min(self.varZ[self.i_start:self.i_end]),
        #                     max(self.varZ[self.i_start:self.i_end])))
        self.midPlot.set_ylim(0, 0.01)
        # self.bottPlot.set_ylim((min(self.varY[self.i_start:self.i_end]),
        #                     max(self.varY[self.i_start:self.i_end])))
        self.bottPlot.set_ylim(0, 3.1)

        # self.midPlot.legend()
        # self.bottPlot.legend()
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
        if keycode == wx.WXK_LEFT:
            self.updateGraph(-self.scrollWindow)
        elif keycode == wx.WXK_RIGHT:
            self.updateGraph(self.scrollWindow)
        else:
            event.Skip()

    def updateGraph(self, shift):
        self.i_start += shift
        self.i_end += shift
        # self.canvas.SetScrollPos(wx.HORIZONTAL, new_pos)
        self.draw_plot()


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None, id=-1)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
