import json 
import math
import os
import sys
from datetime import date, timedelta

import numpy as np
import yfinance as yf
from tqdm import tqdm

from stocklist import NasdaqController
from welfords import Welfords

class DataStore:
    def __init__(self, cutoff, lookbehind, window):
        self.today = date.today()
        self.f =  open('data/Variances.json', 'r+')
        self.data = json.load(self.f)
        self.cutoff = cutoff
        self.lookbehind = lookbehind
        self.window = window
        if not self.data: 
            self.StocksController = NasdaqController(True)
            self.tickers = self.StocksController.getList()
            self.populateVariances()

    def populateVariances(self):
        s = " ".join(list(self.tickers))
        print("Downloading Volumes")
        volumes = yf.download(s, period=str(self.lookbehind)+"d")['Volume']
        print("Calculating Variances") 
        for ticker in volumes:
            #print(ticker)
            calculator = Welfords(0, 0, 0)
            broken = False
            for v in volumes[ticker]:
                #not NaN
                if v != v: 
                    broken = True
                    break
                calculator.update(v)
            if not broken:
                variance = calculator.finalize()[1]
                self.data[ticker] = {"count": calculator.count, "mean" : calculator.mean, "m2" : calculator.M2, "variance" : variance, "lastupdate" : self.today.isoformat()}
        print("Writing to File")
        self.write()

    def findAnomalies(self):
        s = " ".join(list(self.data.keys())[:100])
        print("Downloading Volumes")
        volumes = yf.download(s, self.today - timedelta(days=self.window), self.today + timedelta(days=0))['Volume']
        print("Finding Anomalies: ")
        for ticker in volumes:
            window_volume = np.nanmax(volumes[ticker])
            mean, std = self.getStats(ticker)
            if  window_volume > mean + self.cutoff * std:
                print("Ticker: ", ticker, "STD: ", (window_volume-mean)/std)
        print("Writing Updates")
        self.write()

    def write(self):
        self.f.seek(0)
        self.f.write(json.dumps(self.data))
        self.f.truncate()
    
        
    def getStats(self, ticker):
        stock = self.data[ticker]
        lastupdated = date.fromisoformat(stock['lastupdate'])
        if (self.today - lastupdated).days:
            print((lastupdated - self.today).days)
            #getting missing info
            d = yf.download(ticker, lastupdated, self.today+timedelta(days=1))
            count = stock['count']
            mean = stock['mean']
            m2 = stock['m2']
            
            calculator = Welfords(count, mean, m2)

            #calculating online variance
            for v in d['Volume']:
                calculator.update(v)
            newVariance = calculator.finalize()[1]
            
            #updating stock
            stock['count'] = calculator.count
            stock['mean'] = calculator.mean
            stock['m2'] = calculator.M2      
            stock['variance'] = newVariance  
            stock['lastupdate'] = self.today.isoformat()
        
        return stock['mean'], math.sqrt(stock['variance'])

#init datastore with a (cutoff, lookbehind, window)
datastore = DataStore(7, 100, 3)
datastore.findAnomalies()



