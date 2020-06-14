import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import tkinter as tk
from tkinter import ttk
from matplotlib import pyplot as plt

import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import urllib
import pandas as pd
import numpy as np
import time
from datetime import datetime

LARGE_FONT = ("Verdana", 12)
style.use("ggplot")

f = Figure()
a = f.add_subplot(111)

pd.options.mode.chained_assignment = None

DataPace = "1d"
resampleSize = "15Min"
DatCounter = 9000
candleWidth = 0.008

def changeTimeFrame(tf):
    global DataPace
    global DatCounter
    if tf == "7d" and resampleSize == "1Min":
        print("Too much data")
    else:
        DataPace = tf
        DatCounter = 9000

def changeSampleSize(size,width):
    global resampleSize
    global DatCounter
    global candleWidth
    if DataPace == "7d" and resampleSize == "1Min":
        print("Too much data")
    elif DataPace == "tick":
        print("You're currently viewing tick data, not OHLC.")
    else:
        resampleSize = size
        DatCounter = 9000
        candleWidth = width


def animate(i):
    url = "https://cex.io/api/trade_history/BTC/USD"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode("utf-8")
    data = json.loads(html)
    data = pd.DataFrame(data)

    buys = data[(data['type']=="buy")]
    buys["datestamp"] = (np.array(list(map(int, buys["date"]))).astype("datetime64[s]"))
    buyDates = (buys["datestamp"]).tolist()

    sells = data[(data['type']=="sell")]
    sells["datestamp"] = (np.array(list(map(int, sells["date"]))).astype("datetime64[s]"))
    sellDates = (sells["datestamp"]).tolist()

    a.clear()
    
    a.plot_date(buyDates, list(map(float,buys["price"])), "#00A3E0", label="buys")
    a.plot_date(sellDates, list(map(float,sells["price"])), "#183A54", label="sells")

    a.legend(bbox_to_anchor=(0,1.02,1, .102), loc=3, ncol=2, borderaxespad=0)

    title ="BTC/USD Prices\nLast Price: " + str(data["price"][len(data)-1])
    a.set_title(title)

class BTC(tk.Tk): #Inheritence from tk.Tk

    def __init__(self,*args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        #client icon
        #tk.Tk.iconbitmap(self, default="")
        tk.Tk.wm_title(self, "BTC Price")

        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label = "Exit", command=quit)
        menubar.add_cascade(label = "Settings", menu=filemenu)

        dataTF = tk.Menu(menubar, tearoff=1)
        dataTF.add_command(label = "Tick", command=lambda: changeTimeFrame('tick'))
        dataTF.add_command(label = "1 Day", command=lambda: changeTimeFrame('1d'))
        dataTF.add_command(label = "3 Day", command=lambda: changeTimeFrame('3d'))
        dataTF.add_command(label = "1 Week", command=lambda: changeTimeFrame('7d'))
        menubar.add_cascade(label = "Data Time Frame", menu = dataTF)

        OHLCI = tk.Menu(menubar, tearoff=1)
        OHLCI.add_command(label = "TIck", command=lambda: changeSampleSize('tick', 0.0005))
        OHLCI.add_command(label = "1  minute", command=lambda: changeSampleSize('1Min',0.002))
        OHLCI.add_command(label = "5 minute", command=lambda: changeSampleSize('5Min',0.003))
        OHLCI.add_command(label = "15 minute", command=lambda: changeSampleSize('15Min',0.008))
        OHLCI.add_command(label = "30 minute", command=lambda: changeSampleSize('30Min',0.016))
        OHLCI.add_command(label = "1 Hour", command=lambda: changeSampleSize('1H',0.032))
        OHLCI.add_command(label = "3 Hour", command=lambda: changeSampleSize('3H',0.096))

        menubar.add_cascade(label="OHLC Interval", menu=OHLCI)

        tk.Tk.config(self, menu=menubar)


        self.frames = {}

        for F in (StartPage, BTC_Page):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew") 
        
        self.show_frame(StartPage)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="ALPHA BTC TRACKER", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Agree", command=lambda: controller.show_frame(BTC_Page))
        button1.pack()

        button2 = ttk.Button(self, text="Disagree", command=quit)
        button2.pack()

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page 1", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to home", command=lambda: controller.show_frame(StartPage))
        button1.pack()

class BTC_Page(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to home", command=lambda: controller.show_frame(StartPage))
        button1.pack()

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand = True)
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)


app = BTC()
app.geometry("1280x720")
ani = animation.FuncAnimation(f, animate, interval=1000)
app.mainloop()

#https://cex.io/api/trade_history/BTC/USD, SOURCE OF DATA, ALL RIGHTS RESERVED TO CEX.IO