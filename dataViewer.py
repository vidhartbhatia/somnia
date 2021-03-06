import csv
import wx
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import numpy as np
import datetime
import os

import matplotlib
matplotlib.use('WXAgg')
time_fmt = mdates.DateFormatter('%H:%M')

GRAPH_WHOLE_DATA = True
VIEW_WINDOW_WIDTH = 10*60*60*3
SCROLL_WINDOW_INCR = 10*60*10

VAR_WINDOW1 = 10*60*10
SMOOTHING = 20
BINARY_TAGS = True

# csv file name 
dataFolder = "jeremy 5-11"
data_file_name = "51110"
data_dir = "Data"
labels_dir = "Tagging"
results_dir = "Test_var_agg"
ROW_LIMIT = None # set to none if want all

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
        accZ = []
        accY = []
        accX = []

        wekaPredRaw = []
        appPredRaw = []

        appPredTags = []
        wekaPredTags = []
        saaTags = []

        with open(f"{results_dir}{os.sep}{dataFolder}{os.sep}{data_file_name}_results.csv", 'r') as f:
            data = csv.DictReader(f, delimiter=',')
            for row in data:
                if ROW_LIMIT!=None:
                    if len(wekaPredTags) >=ROW_LIMIT: break
                tag = int(row['predicted'])
                if tag != -1:
                    if BINARY_TAGS: tag = 0 if tag==0 else 1
                    wekaPredRaw.append(tag)
                
                tag = int(row['tags'])
                if tag != -1:
                    if BINARY_TAGS: tag = 0 if tag==0 else 1
                    saaTags.extend([tag]*600)
        
        # filter majority over window of 7
        for i in range(len(wekaPredRaw)):
            window = sorted(wekaPredRaw[max(0,i-3):i+3])
            wekaPredTags.extend([window[len(window)//2]]*600)
        
        with open(f"{data_dir}{os.sep}{dataFolder}{os.sep}{data_file_name}.csv", 'r') as f:
            data = csv.DictReader(f, delimiter=',')
            for row in data:
                if len(dtime) < len(wekaPredTags):
                    dtime.append(datetime.datetime.fromtimestamp(int(row['time_stamp'])/1000))
                    accZ.append(float(row['accZ']))
                    accY.append(float(row['accY']))
                    accX.append(float(row['accX']))
                if len(appPredRaw) < len(wekaPredRaw):            
                    tag = int(row['phase'])
                    if tag>-1:
                        appPredRaw.append(tag)       
        
        # filter majority over window of 7
        for i in range(len(appPredRaw)):
            window = sorted(appPredRaw[max(0,i-3):i+3])
            appPredTags.extend([window[len(window)//2]]*600)

        
        print(f"read {len(dtime)} rows, {len(wekaPredTags)} wekaTags, {len(appPredTags)} appTags, {len(saaTags)} saaTags")
        assert(len(dtime) == len(wekaPredTags) == len(appPredTags))
        # print(list(map(lambda x: x.strftime('%H:%M:%S'),dtime[:100])))
        self.t = np.array(dtime)
        self.accZ = np.array(accZ)
        self.accY = np.array(accY)
        self.accX = np.array(accX)

        self.weka_tags = np.array(wekaPredTags)
        self.saa_tags = np.array(saaTags)
        self.app_tags = np.array(appPredTags)

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


        # Extents of data sequence:
        self.i_min = 0
        self.i_max = len(self.t)
        # print(self.i_max)

        # Size of plot window:
        self.i_window = len(self.t) if GRAPH_WHOLE_DATA else VIEW_WINDOW_WIDTH
        self.scrollWindow = SCROLL_WINDOW_INCR

        # Indices of data interval to be plotted:
        self.i_start = 0
        self.i_end = self.i_start + self.i_window

    def init_plot(self):
        self.fig.suptitle(f"{dataFolder}|{data_file_name}|{results_dir}|")
        self.topPlot = self.fig.add_subplot(211)
        self.bottPlot = self.fig.add_subplot(212, sharex=self.topPlot)
        self.topPlot.set_ylabel('variance (acceleration)')
        self.topPlot.xaxis.set_major_formatter(time_fmt)
        self.bottPlot.xaxis.set_major_formatter(time_fmt)
        if not BINARY_TAGS:
            self.bottPlot.set_ylabel('sleep phase tag (deep=0, light=1, rem=2, awake=3)')
        else: self.bottPlot.set_ylabel('sleep phase tag (deep=0, light=1)')
        # self.topPlot.set_xlabel('time of day')
        self.bottPlot.set_xlabel('time of day')
        # self.plot_rawAccZ = \
        #           self.topPlot.plot(self.t[self.i_start:self.i_end],
        #                          self.accZ[self.i_start:self.i_end], 'b,')[0]
        # self.plot_smooth = \
        #           self.topPlot.plot(self.t[self.i_start:self.i_end],
        #                          self.fx[self.i_start:self.i_end])[0]

        self.plot_accVar = \
            self.topPlot.plot(self.t[self.i_start:self.i_end],
                              self.varAcc[self.i_start:self.i_end], 'k', alpha=0.5, linewidth=5, label='sum')[0]
        self.plot_accVarZ = \
                  self.topPlot.plot(self.t[self.i_start:self.i_end],
                                 self.varZ[self.i_start:self.i_end], 'g', alpha=0.8, linewidth=4, label='Z')[0]

        self.plot_accVarY = \
                  self.topPlot.plot(self.t[self.i_start:self.i_end],
                                 self.varY[self.i_start:self.i_end], 'r', alpha=0.8, linewidth=4, label='Y')[0]
        self.plot_accVarX = \
                  self.topPlot.plot(self.t[self.i_start:self.i_end],
                                 self.varX[self.i_start:self.i_end], 'b', alpha=0.8, linewidth=4, label='X')[0]

        self.plot_app_tags = \
            self.bottPlot.plot(self.t[self.i_start:self.i_end],
                               self.app_tags[self.i_start:self.i_end], 'k', alpha=0.8, label='app-live-predicted', linewidth=5)[0]
        self.plot_saa_tags = \
            self.bottPlot.plot(self.t[self.i_start:self.i_end],
                               self.saa_tags[self.i_start:self.i_end], 'r', alpha=0.9, label='sleep-as-android-labeled', linewidth=2)[0]
        self.plot_weka_tags = \
            self.bottPlot.plot(self.t[self.i_start:self.i_end],
                               self.weka_tags[self.i_start:self.i_end], 'g', alpha=0.9, label='post-weka-predicted', linewidth=3)[0]
        
        self.bottPlot.legend([self.plot_app_tags, self.plot_saa_tags, self.plot_weka_tags])
        self.topPlot.legend([self.plot_accVar, self.plot_accVarZ, self.plot_accVarY, self.plot_accVarX])
        self.topPlot.fill_between(self.t, self.varAcc, color='black', alpha=0.5)
        # self.topPlot.fill_between(self.t, self.varZ, color='green')
        # self.topPlot.fill_between(self.t, self.varY, color='red')
        # self.topPlot.fill_between(self.t, self.varX, color='blue')


        self.draw_plot()

    def draw_plot(self):

        # Update data in plot:
        # self.plot_rawAccZ.set_xdata(self.t[self.i_start:self.i_end])
        # self.plot_smooth.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_accVar.set_xdata(self.t[self.i_start:self.i_end])
        # self.plot_accVar2.set_xdata(self.t[self.i_start:self.i_end])

        self.plot_accVarZ.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_accVarY.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_accVarX.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_weka_tags.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_app_tags.set_xdata(self.t[self.i_start:self.i_end])
        self.plot_saa_tags.set_xdata(self.t[self.i_start:self.i_end])

        # self.plot_rawAccZ.set_ydata(self.accZ[self.i_start:self.i_end])
        # self.plot_smooth.set_ydata(self.fx[self.i_start:self.i_end])
        self.plot_accVar.set_ydata(self.varAcc[self.i_start:self.i_end])
        self.plot_accVarZ.set_ydata(self.varZ[self.i_start:self.i_end])
        self.plot_accVarY.set_ydata(self.varY[self.i_start:self.i_end])
        self.plot_accVarX.set_ydata(self.varX[self.i_start:self.i_end])
        self.plot_weka_tags.set_ydata(self.weka_tags[self.i_start:self.i_end])
        self.plot_app_tags.set_ydata(self.app_tags[self.i_start:self.i_end])
        self.plot_saa_tags.set_ydata(self.saa_tags[self.i_start:self.i_end])

        # Adjust plot limits:
        # self.topPlot.set_xlim((min(self.t[self.i_start:self.i_end]),
        #    max(self.t[self.i_start:self.i_end])))
        self.topPlot.set_xlim((min(self.t[self.i_start:self.i_end]),
                               max(self.t[self.i_start:self.i_end])))
        # self.bottPlot.set_xlim((min(self.t[self.i_start:self.i_end]),
        #                         max(self.t[self.i_start:self.i_end])))
        # self.topPlot.set_ylim((min(self.accZ[self.i_start:self.i_end]),
        #                     max(self.accZ[self.i_start:self.i_end])))
        # self.topPlot.set_ylim(9.5,9.7 )
        # self.topPlot.set_ylim((min(self.varZ[self.i_start:self.i_end]),
        #                     max(self.varZ[self.i_start:self.i_end])))
        self.topPlot.set_ylim(0, 2)
        # self.bottPlot.set_ylim((min(self.varY[self.i_start:self.i_end]),
        #                     max(self.varY[self.i_start:self.i_end])))
        # self.bottPlot.set_ylim(0, 3.1)

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
