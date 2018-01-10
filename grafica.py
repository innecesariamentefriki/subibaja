#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import plotly.offline as py

from datetime import datetime
import time

class grafica:
    def __init__(self, par, cotizaciones):
        self.par = par
        self.cotizaciones = cotizaciones
        self.setLayout()

    def setLayout(self):
        self.INCREASING_COLOR = '#298A08'
        self.DECREASING_COLOR = '#8A0808'

        self.data = []
        self.layout = {}
        self.fig = {'data': self.data, 'layout': self.layout}


        self.fig['layout']['plot_bgcolor'] = 'rgb(250, 250, 250)'
        self.fig['layout']['xaxis'] = dict(rangeselector=dict(visible=True))
        self.fig['layout']['yaxis'] = dict(domain=[0, 0.2], showticklabels=False)
        self.fig['layout']['yaxis2'] = dict(domain=[0.2, 0.8])
        self.fig['layout']['legend'] = dict(orientation='h', y=0.9, x=0.3, yanchor='bottom')
        self.fig['layout']['margin'] = dict(t=0, b=40, r=40, l=40)

    def drawRangeSelector(self):
        # Add range buttons
        rangeselector = {'visible': True,
                         'x': 0,
                         'y': 0.9,
                         'bgcolor': 'rgba(150, 200, 250, 0.4)',
                         'font': {'size': 13},
                         'buttons': list([
                             {'count': 1, 'label': 'reset', 'step': 'all'},
                             {'count': 1, 'label': '1yr', 'step': 'year', 'stepmode': 'backward'},
                             {'count': 3, 'label': '3 mo', 'step': 'month', 'stepmode': 'backward'},
                             {'count': 1, 'label': '1 mo', 'step': 'month', 'stepmode': 'backward'},
                             {'count': 4, 'label': '4d', 'step': 'day', 'stepmode': 'backward'},
                             {'step': 'all'}
                         ])}

        self.fig['layout']['xaxis']['rangeselector'] = rangeselector

    def addDataToFig(self, data):
        self.fig['data'].append(data)

    def drawFig(self):
        py.plot(self.fig, filename='html/' + self.par + '.html')

    def drawCandleStick(self):
        dfOpen = []
        self.dfClose = []
        dfHigh = []
        dfLow =[]
        self.dfDate = []
        self.dfVolume = []
        self.dfAverage = []

        for tick in self.cotizaciones:
            dfOpen.append(tick['open'])
            self.dfClose.append(tick['close'])
            dfHigh.append(tick['high'])
            dfLow.append(tick['low'])
            self.dfVolume.append(tick['volume'])
            self.dfAverage.append(tick['weightedAverage'])
            utc_time = datetime.utcfromtimestamp(tick['date'])
            self.dfDate.append(utc_time.strftime("%Y-%m-%d %H:%M:%S"))


        data = {'type': 'candlestick',
                 'open': dfOpen[-185:],
                 'high': dfHigh[-185:],
                 'low': dfLow[-185:],
                 'close': self.dfClose[-185:],
                 'x': self.dfDate[-185:],
                 'yaxis': 'y2',
                 'name': 'GS',
                 'increasing': dict(line=dict(color=self.INCREASING_COLOR)),
                 'decreasing': dict(line=dict(color=self.DECREASING_COLOR))
                }
        return data


    # pintado de curvas
    def drawMovingAverage(self):
        mv_y = self.movingaverage(self.dfClose)
        mv_x = list(self.dfDate)

        # Clip the ends
        mv_x = mv_x[5:-5]
        mv_y = mv_y[5:-5]

        data = {
            'x': mv_x[-185:],
            'y': mv_y[-185:],
            'type': 'scatter',
            'mode': 'lines',
            'line': {'width': 1},
            'marker': {'color': '#0B615E'},
            'yaxis': 'y2',
            'name': 'Moving Average'
        }
        return data

    def drawExponentialMovingAverage(self, name, count, color):
        emv_y = self.ExpMovingAverage(self.dfClose, count)
        emv_x = list(self.dfDate)

        # Clip the ends
        emv_x = emv_x[5:-5]
        emv_y = emv_y[5:-5]

        data = {
            'x': emv_x[-185:],
            'y': emv_y[-185:],
            'type': 'scatter',
            'mode': 'lines',
            'line': {'width': 1},
            'marker': {'color': color},
            'yaxis': 'y2',
            'name': name
        }
        return data

    def drawVolumeChart(self):
        colors = []

        for i in range(len(self.dfClose)):
            if i != 0:
                if self.dfClose[i] > self.dfClose[i - 1]:
                    colors.append(self.INCREASING_COLOR)
                else:
                    colors.append(self.DECREASING_COLOR)
            else:
                colors.append(self.DECREASING_COLOR)

        # Add volume bar chart
        data = {
            'x': self.dfDate[-185:],
            'y': self.dfVolume[-185:],
            'marker': {'color': colors},
            'type': 'bar',
            'yaxis': 'y',
            'name': 'Volume'
        }
        return data

    def drawBollinger(self):
        serieBB = pd.Series(self.dfClose, index=self.dfDate)
        bbAvg, self.bbUpper, self.bbLower = self.bbands(serieBB)

        dataUpper = {
            'x': self.dfDate[-185:],
            'y': self.bbUpper[-185:],
            'type': 'scatter',
            'yaxis': 'y2',
            'line': {'width': 2},
            'marker': {'color': '#084B8A'},
            'hoverinfo': 'none',
            'legendgroup': 'Bollinger Bands',
            'name': 'Bollinger Bands'
        }

        dataLower = {
            'x': self.dfDate[-185:],
            'y': self.bbLower[-185:],
            'type': 'scatter',
            'yaxis': 'y2',
            'line': {'width': 2},
            'marker': {'color': '#084B8A'},
            'hoverinfo': 'none',
            'legendgroup': 'Bollinger Bands',
            'showlegend': False
        }

        return dataUpper, dataLower

    def drawEvents(self, anotaciones):
        self.fig['layout']['annotations'] = anotaciones

    # funciones matemáticas
    def movingaverage(self, interval, window_size=50):
        window = np.ones(int(window_size))/float(window_size)
        return np.convolve(interval, window, 'same')

    def ExpMovingAverage(self, interval, window_size=20):
        weights = np.exp(np.linspace(-1., 0., window_size))
        weights /= weights.sum()

        a = np.convolve(interval, weights)[:len(interval)]
        a[:window_size] = a[window_size]
        return a

    def bbands(self, price, window_size=20, num_of_std=2):
        rolling_mean = price.rolling(window=window_size).mean()
        rolling_std = price.rolling(window=window_size).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return rolling_mean, upper_band, lower_band

    def seriesAvgDate(self):
        return pd.Series(self.dfAverage, index=self.dfDate)

    def getLowerBollinger(self):
        return self.bbLower

    def getUpperBollinger(self):
        return self.bbUpper
