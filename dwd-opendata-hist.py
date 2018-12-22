#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
#
# store historic weather data from opendata.dwd.de to a sqlite3 db
#
# Dirk Clemens, git@adcore.de 
#
# ['10400', 'Unit', '%', 'Grad C', 'cm', 'Grad C', 'W/m2', 'W/m2', 'W/m2', 'Grad C', 'mm', 'W/m2', 'W/m2', 'm', 'km', 'km/h', 'Grad C', 'Grad C', 'km/h', 'km/h', 'km/h', 'km/h', 'Grad', 'km/h', 'Grad C', 'Grad C', 'Grad C', 'Grad C', 'CODE_TABLE', 'CODE_TABLE', 'mm', 'mm', 'mm', 'mm', 'mm', 'CODE_TABLE', 'hPa', '%', 'Grad C', 'Grad C', 'cm', 'min', 'h']
# ['Datum', 'Uhrzeit (UTC)', 'Wolkenbedeckung', 'mittlere Temperatur (vergangener Tag, 2m)', 'Neuschneehoehe', 'Taupunkttemperatur (2m)', 'Diffuse Strahlung (letzte Stunde)', 'Direkte Strahlung (vergangene 24 Stunden)', 'Direkte Strahlung (letzte Stunde)', 'Temperatur (2m)', 'Evaporation (vergangene 24 Stunden)', 'Globalstrahlung (letzte Stunde)', 'Globalstrahlung (vergangene 24 Stunden)', 'Wolkenuntergrenze', 'Sichtweite', 'Maximalwind (vergangener Tag)', 'Maximumtemperatur (vergangener Tag, 2m)', 'Maximumtemperatur (letzte 12 Stunden, 2m)', 'Maximalwind (letzte Stunde)', 'Windboen (letzte 6 Stunden)', 'Windboen (vergangener Tag)', 'Windboen (letzte Stunde)', 'Windrichtung', 'Windgeschwindigkeit', 'Minimumtemperatur (vergangener Tag, 5cm)', 'Minimumtemperatur (vergangener Tag, 2m)', 'Minimumtemperatur (letzte 12 Stunden, 2m)', 'Minimumtemperatur (letzte 12 Stunden, 5cm)', 'vergangenes Wetter 1', 'vergangenes Wetter 2', 'Niederschlag (letzte 24 Stunden)', 'Niederschlag (letzte 3 Stunden)', 'Niederschlag (letzte 6 Stunden)', 'Niederschlag (letzte Stunde)', 'Niederschlag (letzte 12 Stunden)', 'aktuelles Wetter', 'Druck (auf Meereshoehe)', 'Relative Feuchte', 'Wassertemperatur', 'Temperatur (5cm)', 'Schneehoehe', 'Sonnenscheindauer (letzte Stunde)', 'Sonnenscheindauer (vergangener Tag)']	
#
#  CREATE TABLE "WETTER_DAILY" ('TIMESTAMP' DATETIME PRIMARY KEY,'TEMPMAX' INTEGER,'TEMPMIN' INTEGER,'TEMPAVG' INTEGER,'HUMIDITY' INTEGER,'PRESSURE' INTEGER,'WIND' INTEGER, 'RAIN' INTEGER, 'SUN' INTEGER, 'CLOUD' INTEGER)
#
# 	TIMESTAMP	TEMPMAX	TEMPMIN	TEMPAVG	HUMIDITY		PRESSURE		WIND		RAIN		SUN		CLOUD (%)
# 	1			17		26		9		37			36			23		34		42		2
#
########################################################################

import sys
import sqlite3 as sqlite3
import datetime
from time import strftime
from datetime import datetime, timedelta

####################################################################################
# The function that converts the string to float
def toInt(value):
	try:
		val = value.strip().replace(',', '.')
		return float(val)
		pass	
	except:
		return 0

####################################################################################
#
def updateDB(row):
	try:
		sdate = datetime.today().strftime('%Y-%m-%d')
		con = sqlite3.connect('/opendata.db')   
		cur = con.cursor()   
		con.execute('''REPLACE INTO WETTER_DAILY (TIMESTAMP, TEMPMAX, TEMPMIN, TEMPAVG, HUMIDITY, PRESSURE, WIND, RAIN, SUN, CLOUD)
					  VALUES(?,?,?,?,?,?,?,?,?,?)''', (sdate,toInt(row[17]), toInt(row[26]), toInt(row[9]), toInt(row[37]), toInt(row[36]), toInt(row[23]), toInt(row[34]), toInt(row[42]), toInt(row[2])))
		con.commit()
	except sqlite3.IntegrityError as e:
		print('Record already exists: %s' % (e,))
	finally:
		con.close()
				
####################################################################################
def main():
	station = 10400
	url = 'https://opendata.dwd.de/weather/weather_reports/poi/%s-BEOB.csv' % (station,)
	
	d = datetime.today() - timedelta(days=1)
	query_date = d.strftime('%d.%m.%y')
	query_hour = '18:00'
			
	from urllib.request import urlopen
	try:
		with urlopen(url) as response:
			lines = [x.decode('utf8').strip() for x in response.readlines()]
			for line in lines:
				elements = line.split(';')
				if (elements[0] == query_date) and (elements[1] == query_hour):
					updateDB(elements)
		pass
	except csv.Error as e:
		sys.exit('error reading line {}: {}'.format(reader.line_num, e))

	sys.exit(0)

if __name__ == "__main__":		
	main()
