# -*- coding: utf-8 -*-

import wx
import pandas as pd
from datetime import datetime
import wx.adv
import wx.grid as grid
import regex as re
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from dateutil.parser import parse
import os


class DAV(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(600,380))
        self.initialize()
            
    def initialize(self):
        pannel = wx.Panel(self)
        
        rows = wx.BoxSizer(wx.VERTICAL)
        butSize = wx.BoxSizer(wx.HORIZONTAL)
        
        numSize = wx.BoxSizer(wx.HORIZONTAL)
        self.text_1 = wx.StaticText(pannel, label = "From :")
        self.text_2 = wx.StaticText(pannel, label = "To :")
       
        self.start_date = wx.adv.GenericDatePickerCtrl(pannel, size=(120,-1),
                                       style = wx.TAB_TRAVERSAL
                                       | wx.adv.DP_DROPDOWN
                                       | wx.adv.DP_SHOWCENTURY
                                       | wx.adv.DP_ALLOWNONE )
        self.Bind(wx.adv.EVT_DATE_CHANGED, self.OnFromDateChanged, self.start_date)
        
        self.end_date= wx.adv.GenericDatePickerCtrl(pannel, size=(120,-1),
                                        style = wx.TAB_TRAVERSAL
                                        | wx.adv.DP_DROPDOWN
                                        | wx.adv.DP_SHOWCENTURY
                                        | wx.adv.DP_ALLOWNONE )
        self.Bind(wx.adv.EVT_DATE_CHANGED, self.OnToDateChanged, self.end_date)
        
        
        numSize.Add(self.text_1 , 1, wx.ALIGN_CENTER | wx.LEFT, border=10)
        numSize.Add(self.start_date, 1, wx.CENTER , border=10)
        numSize.Add(self.text_2 , 1, wx.CENTER | wx.RIGHT, border=10)
        numSize.Add(self.end_date, 1, wx.ALIGN_CENTER | wx.RIGHT , 10)
        
        rows.Add(numSize, 2, wx.ALIGN_CENTER)
        
        self.text_3 = wx.StaticText(pannel, label = "Features")
        feature_set = ["Information of all penalty cases",
                       "Distribution of cases by offence code",
                       "Cases captures by radar or camera",
                       "Display cases casued by mobile phone usage"]
        self.features = wx.Choice( pannel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, feature_set , 0 )
        rows.Add(self.text_3 , 1, wx.CENTER | wx.RIGHT, border=10)
        rows.Add(self.features, 1, wx.ALIGN_CENTER | wx.BOTTOM, border=10)
        
        self.backButton = wx.Button(pannel, label='Back')
        butSize.Add(self.backButton , 1, wx.ALIGN_CENTER | wx.RIGHT, border=10)
        rows.Add(butSize, 1, wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.onBack, self.backButton)
        self.backButton.Hide()

        self.processButton = wx.Button(pannel, label='Process')
        butSize.Add(self.processButton, 1, wx.ALIGN_CENTER | wx.RIGHT, border=10)
        rows.Add(butSize, 1, wx.ALIGN_CENTER)
        
        self.Bind(wx.EVT_BUTTON, self.process, self.processButton)
        
        pannel.SetSizerAndFit(rows)
        self.Show(True)
        self.from_date = datetime.now().strftime('%d/%m/%Y')
        self.to_date = datetime.now().strftime('%d/%m/%Y')
        
    def OnFromDateChanged(self, evt):                   #method to convert from date time to dd/mm/yyyy format
        self.from_date = evt.GetDate().Format("%d/%m/%Y")
        return self.from_date

    def OnToDateChanged(self, evt):                     #method to convert to date time to dd/mm/yyyy format
        self.to_date = evt.GetDate().Format("%d/%m/%Y")
        if self.from_date > self.to_date:
            print("Start date must be before End date.")    
        return self.to_date

    def csv_to_dataframe(self, filename):
        if os.path.isfile('data_set.csv'):
            self.data = pd.read_csv(filename , low_memory=False) 
            self.data.head()
            return pd.DataFrame(self.data)
        else:
            print("Incorrect file type")
            
    
    def process(self, event):
        self.text_1.Hide()
        self.text_2.Hide()
        self.start_date.Hide()
        self.end_date.Hide()
        self.text_3.Hide()
        self.features.Hide()
        self.features.Hide()
        self.processButton.Hide()
        
        df = self.csv_to_dataframe("data_set.csv")
        self.filtered_data = []
        self.camera_Radar_offence = []
        self.key_list= [dat for dat in self.data.keys()]
        
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.canvas, proportion=1, flag=wx.LEFT | wx.TOP | wx.GROW)
       
        #code for the 2nd feature
        if self.features.GetCurrentSelection() == 1:
            date_range = (df["OFFENCE_MONTH"] >= self.from_date ) & (df["OFFENCE_MONTH"] <= self.to_date)
            print(df.loc[date_range])
            data_frame = df.groupby("OFFENCE_CODE").agg({"OFFENCE_MONTH": "count"})\
                  .sort_values(by="OFFENCE_MONTH", ascending=False).reset_index()[:10]
            
            l1 = [val['OFFENCE_CODE'] for val in data_frame.iloc(0)]
            l2 = [val['OFFENCE_MONTH'] for val in data_frame.iloc(0)]

            self.axes.plot(l2, l1)
            self.axes.set_xlabel("Offence Count")
            self.axes.set_ylabel("Offence Code")
            self.axes.set_title("Distribution of Cases by Top 10 Offence Codes")
            self.canvas.draw()
            
            
        #code for the 4th feature
        if self.features.GetCurrentSelection() == 3:                   
            mobile_cases = df[df["MOBILE_PHONE_IND"] == "Y"]
            mobile_related_cases_by_month = mobile_cases.groupby("OFFENCE_MONTH")\
                .agg({"OFFENCE_MONTH": "count"})
            total_cases = df.groupby("OFFENCE_MONTH").agg({"OFFENCE_MONTH": "count"})
            mobile_related_cases_by_month["%"] = mobile_related_cases_by_month["OFFENCE_MONTH"]/total_cases["OFFENCE_MONTH"]*100     
            self.axes.plot(mobile_related_cases_by_month["%"], color='r')
            self.axes.set_xticklabels([])
            self.axes.set_xlabel("Time ->")
            self.axes.set_ylabel("Percentage of mobile related cases")
            self.axes.set_title("Trend of Mobile Phone Related Cases Over Time")
        
        if self.features.GetCurrentSelection() == 0 or self.features.GetCurrentSelection() == 2:
            for i in df.itertuples(index=False):
                if parse(self.from_date) <= parse(i[1]) <= parse(self.to_date):
                    
                    #condition of th 1st feature
                    if self.features.GetCurrentSelection() == 0:
                        data_list = []
                        for j in range(len(i)):
                            data_list.append(i[j])
                        dictionary = dict(zip(self.key_list, data_list))
                        self.filtered_data.append(dictionary)
                        self.result = 1
                    
                    #condition of th 3rd feature
                    if self.features.GetCurrentSelection() == 2:
                        if  re.findall('camera', i[3].lower()) or  re.findall('radar', i[3].lower()):
                            data_list = []
                            for j in range(len(i)):
                                data_list.append(i[j])
                            dictionary = dict(zip(self.key_list, data_list))
                            self.camera_Radar_offence.append(dictionary)
                            self.result = 3
                        
        #create table for feature 1
        if self.features.GetCurrentSelection() == 0:
            self.feature_1_table = grid.Grid(self)
            self.feature_1_table.CreateGrid(len(self.filtered_data), 25)
            for index, val in enumerate(self.key_list):
                self.feature_1_table.SetColLabelValue(index, str(val))
            for index,data in enumerate(self.filtered_data):
                for col,val in enumerate(data):
                    self.feature_1_table.SetCellValue(index, col, str(data[val]))
            sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
            sizer_1.Add(self.feature_1_table, 1,  wx.CENTER ,border=10)
            self.SetSizer(sizer_1)
        
        #create table for feature 2
        if self.features.GetCurrentSelection() == 2:
            self.feature_2_table = grid.Grid(self)
            self.feature_2_table.CreateGrid(len(self.camera_Radar_offence), 25)
            for index, val in enumerate(self.key_list):
                self.feature_2_table.SetColLabelValue(index, str(val))
            for index,data in enumerate(self.camera_Radar_offence):
                for col,val in enumerate(data):
                    self.feature_2_table.SetCellValue(index, col, str(data[val]))
            sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
            sizer_2.Add(self.feature_2_table, 1, wx.EXPAND)
            self.SetSizer(sizer_2)
        
        self.backButton.Show()
        

    def onBack(self, event):    #show hide button 
        self.text_1.Show()
        self.text_2.Show()
        self.start_date.Show()
        self.end_date.Show()
        self.text_3.Show()
        self.features.Show()
        self.processButton.Show()
        self.backButton.Hide()
        if self.features.GetCurrentSelection() == 0:
            self.feature_1_table.Hide()
        if self.features.GetCurrentSelection() == 1:
            self.figure.Hide()
            self.canvas.Hide()
        if self.features.GetCurrentSelection() == 2:
            self.feature_2_table.Hide()
        if self.features.GetCurrentSelection() == 3:
            self.figure.Hide()
            self.canvas.Hide()
        

app = wx.App()
frame = DAV(None, 'Data Analysis & Visualization tool')
app.MainLoop()