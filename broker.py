#!/usr/bin/python
# -*- coding: utf-8 -*-
import poloniex as plx

import datetime as datetime


class broker:
    def __init__(self, key, token, pair):
        self.api = plx.poloniex(key, token)
        self.pair = pair
        self.baseCoin = pair.split('_')[0]
        self.minimaInversion = {
            'USDT': 50,
            'BTC': 0.01
        }

    def activeBalances(self):
        todos = self.api.returnBalances()
        balances = {}
        for coin in todos:
            if float(todos[coin]) > 0:
                balances[coin] = float(todos[coin])
        return balances

    def openOrders(self):
        return self.api.returnOpenOrders(self.pair)

    def closedOrders(self):
        origen = datetime.datetime(2018, 01, 01, 0, 0).strftime('%s')
        cerradas = self.api.returnTradeHistory(self.pair, origen)
        return cerradas

    def tradeHistory(self):
        return self.api.returnMarketTradeHistory(self.pair)

    def candlesticks(self, start, end, period):
        return self.api.returnChartData(self.pair, start, end, period)

    def returnOrderBook(self):
        return self.api.returnOrderBook(self.pair)

    # True si hay el mínimo de dinero necesario para comprar
    # según lo que se haya configurado para la moneda base
    def hayDinero(self):
        base = self.pair.split('_')[0]
        balances = self.activeBalances()
        for coin in balances:
            if coin == base:
                if balances[coin] > self.minimaInversion[base]:
                    #logging.info(" %.4f %s disponibles" % (balances[coin], coin))
                    return True
        return False

