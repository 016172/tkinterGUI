import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import tkinter as tk
from tkinter import ttk

import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import urllib
import pandas as pd
import numpy as np

TICKER_API_URL = "'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest/"
LARGE_FONT = ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

dataPointsY = []
dataPointsX = []

def animate(i):
    url = "https://cex.io/api/trade_history/BTC/USD"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    data = json.loads(html)
    data = pd.DataFrame(data)
    #print(min(data["date"]))
    print(data)
   
   
    buys = data[(data['type']=="buy")]
    buys["datestamp"] = np.array(buys["date"]).astype("datetime64[s]")
    buyDates = (buys["datestamp"]).tolist()
    

    sells = data[(data['type']=="sell")]
    sells["datestamp"] = np.array(sells["date"]).astype("datetime64[s]")
    sellDates = (sells["datestamp"]).tolist()

    a.clear()

    a.plot_date(buyDates, buys["price"])
    a.plot_date(sellDates, sells["price"])

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
ani = animation.FuncAnimation(f, animate, interval=5000)
app.mainloop()



#https://cex.io/api/trade_history/BTC/USD, perfect to use!!