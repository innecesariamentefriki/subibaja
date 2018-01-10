#!/usr/bin/python
# -*- coding: utf-8 -*-
#https://xkcd.com/327/
import sqlite3 as lite
import time
import datetime


class datos:
    def __init__(self, dbname):
        self.dbname = dbname


    def showAll(self):
        con = lite.connect(self.dbname)
        with con:
            cur = con.cursor()

            cur.execute('SELECT * FROM monedas')
            monedas = cur.fetchall()
            cur.execute('SELECT * FROM incautos')
            incautos = cur.fetchall()

            return monedas, incautos

    def firstRun(self):
        con = lite.connect(self.dbname)
        with con:
            cur = con.cursor()

            cur.execute("DROP TABLE IF EXISTS monedas")
            cur.execute("CREATE TABLE monedas(pair TEXT, action TEXT,date INT, value FLOAT)")

            cur.execute("DROP TABLE IF EXISTS incautos")
            cur.execute("CREATE TABLE incautos(first_name TEXT, id INT)")

    def addUser(self, first_name, id):
        con = lite.connect(self.dbname)
        with con:
            cur = con.cursor()
            t = (first_name, id, )
            cur.execute("INSERT INTO incautos(first_name, id) VALUES(?, ?)", t)

    def findUser(self, first_name):
        con = lite.connect(self.dbname)
        with con:
            cur = con.cursor()
            t = (first_name,)
            cur.execute("SELECT * FROM incautos WHERE first_name=?", t)
            return cur.fetchall()

    def showUsers(self):
        con = lite.connect(self.dbname)
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM incautos")
            return cur.fetchall()

    def addEvent(self, pair, action, date, value):
        con = lite.connect(self.dbname)
        with con:
            cur = con.cursor()
            timestamp = int(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple()))
            t = (pair, action, timestamp, value,)
            cur.execute("INSERT INTO monedas(pair, action, date, value) VALUES(?, ?, ?, ?)", t)

    def findEvent(self, pair, date):
        con = lite.connect(self.dbname)
        with con:
            cur = con.cursor()
            timestamp = int(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple()))
            t = (pair, timestamp,)
            cur.execute("SELECT * FROM monedas WHERE pair=? AND date=?", t)
            if cur.fetchall():
                return True
        return False
