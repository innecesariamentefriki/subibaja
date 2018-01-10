#!/usr/bin/python
# -*- coding: utf-8 -*-

# capa de abstracción para interactuar con diversas casas de cambio
import broker as brk

# almacenamiento con shelve
import datos as dts

# gráficas con plotly
import grafica as gfx

# toma de decisiones
import aljoritmoh as wtf

import logging
import sys, getopt
import time
import requests

# para enviar mensajes con telegram
TOKEN = ''

def main(argv):
    coin = ''
    exchange = ''
    try:
        opts, args = getopt.getopt(argv, "hp:")
    except getopt.GetoptError:
        print 'monimonimoni.py -p <pair>'
        print 'Example: monimonimoni.py -p USDT_DASH'

        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'monimonimoni.py -p <pair>'
            sys.exit()
        elif opt in ("-p"):
            pair = arg

    logging.basicConfig(filename='monimonimoni.log', level=logging.INFO)

    # crea el broker que va a operar con el exchange
    currito = brk.broker('', '', pair)

    # Carga el almacenamiento offline de avisos y usuarios de la app
    ddbb = dts.datos('monimonimoni.db')
    #ddbb.firstRun()
    #exit()

    # coge las cotizaciones del exchange
    ahora = int(time.time())
    cotizaciones = currito.candlesticks(ahora - 3500000, ahora, 1800)

    # pinta candlesticks
    grafica = gfx.grafica(pair, cotizaciones)
    grafica.addDataToFig(grafica.drawCandleStick())

    # pinta selector de rango y volumen
    #grafica.drawRangeSelector()
    grafica.addDataToFig(grafica.drawVolumeChart())

    # pinta media móvil y exponenciales
    grafica.addDataToFig(grafica.drawMovingAverage())
    grafica.addDataToFig(grafica.drawExponentialMovingAverage('EMA 1: 30', 30, '#DBA901'))
    grafica.addDataToFig(grafica.drawExponentialMovingAverage('EMA 2: 20', 20, '#A901DB'))

    # pinta bolllinger
    dataUpper, dataLower = grafica.drawBollinger()
    grafica.addDataToFig(dataUpper)
    grafica.addDataToFig(dataLower)

    # toma de decisiones
    oraculo = wtf.aljoritmoh()
    compras = oraculo.aboveBollinger(grafica.seriesAvgDate(), grafica.getLowerBollinger())
    ventas = oraculo.underBollinger(grafica.seriesAvgDate(), grafica.getUpperBollinger())

    # pinta los eventos
    anotaciones = []
    for event in compras:
        anotaciones.append(event)
    for event in ventas:
        anotaciones.append(event)
    grafica.drawEvents(anotaciones)

    # genera la gráfica
    grafica.drawFig()

    # comprobando si los últimos avisos son recientes
    if not checkEvent(pair, 'buy', compras[-1]):
        logging.info("no existe")
        date = compras[-1]['x']
        value = compras[-1]['y']
        ddbb.addEvent(pair, 'buy', date, value)
        smsAviso(pair, 'buy', date, value)

    if not checkEvent(pair, 'sell', ventas[-1]):
        logging.info("no existe")
        date = ventas[-1]['x']
        value = ventas[-1]['y']
        ddbb.addEvent(pair, 'sell', date, value)
        smsAviso(pair, 'sell', date, value)


def checkEvent(pair, action, ultima):
    ddbb = dts.datos('monimonimoni.db')
    date = ultima['x']
    value = ultima['y']
    logging.info(("valorando %s %s %s %.16f") % (pair, action, date, value))
    if ddbb.findEvent(pair, date):
        return True
    else:
        return False

def smsAviso(pair, action, date, value):
    ddbb = dts.datos('monimonimoni.db')
    for incauto in ddbb.showUsers():
        payload = {
            'chat_id': incauto[1],
            'text': "%s %s a las %s a %s. Compruébalo en https://www.example.org/html/%s.html" %
                           (action, pair, date, value, pair)
        }
        r = requests.get('https://api.telegram.org/bot' + TOKEN + '/sendMessage', params=payload)
        logging.info("bot %s" % incauto[0])
        logging.info("bot url %s" % str(r.url))
        logging.info("bot json %s" % str(r.json))


if __name__ == "__main__":
    main(sys.argv[1:])
