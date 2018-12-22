# -*- coding: utf-8 -*-
#
# parse dwd opendata weather forecast
#
# Dirk Clemens, git@adcore.de 
#
# https://opendata.dwd.de/weather/local_forecasts/mos/MOSMIX_L/single_stations/10400/kml/MOSMIX_L_LATEST_10400.kmz
#
############################################################
# DWD Wetter
# DD      Windrichtung            146
# FF      Windgeschwindigkeit     26
# FX1     Maximale Windböe innerhalb der letzten Stunde      44
# Neff    Effektive Wolkendecke   66
# PPPP    Luftdruck               1014.2
# RR6c    Gesamtniederschlag während der letzten 6 Stunden, konsitent mit dem signifikanten Wetter       0.00
# TTT     Temperatur 2m über der Oberfläche     -0.30
# time    01:00
# ww      Signifikantes Wetter    2
# wwd     Wahrscheinlichkeit: Auftreten von Schichtniederschlägen innerhalb der letzten Stunden      Bewölkung unverändert
# SunD	  Sonnenscheindauer Vortag insgesamt	(s)
# RSunD	  Relative Sonnenscheindauer innerhalb der letzten 24 Stunden (%)
# Tx	  Maximale Temperatur - innerhalb der letzten 12 Stunden
# Tn 	  Mindesttemperatur - innerhalb der letzten 12 Stunden
############################################################
#

import zipfile
from lxml import etree
import re
import dateutil.parser
from io import BytesIO
from urllib.request import urlopen

def numeric(s):
    try:
        if '-' in s:
            return 0
        else:
            return int(s)
        pass
    except ValueError:
        return round(float(s)*1.0, 1)

def getElementValueAsList(tree, element):
    for df in tree.xpath('////*[name()="dwd:Forecast" and @*[name()="dwd:elementName" and .="%s"]]' % element):
        # strip unnecessary whitespaces
        elements = re.sub(r'\s+', r';', str(df.getchildren()[0].text).lstrip(' '))
        # print (elements)
        lst = elements.split(";")
        # print (len(lst))
        for index, item in enumerate(lst):  # convert from string
            lst[index] = numeric(lst[index])
        return lst

def analyse(tree):
    # That first part in "double" tag name stands for namespace.
    # You can ignore namespace while selecting element in lxml
    # as //*[name()="Placemark"]/*[name()="ExtendedData"]...
    # The same for attributes: //*[name()="Forecast" and @*[name()="elementName"]]


    #<kml:description>DUESSELDORF</kml:description>
    for df in tree.xpath('////*[name()="kml:description"]'):
        print (df.text)

    #<dwd:IssueTime>2018-12-18T15:00:00.000Z</dwd:IssueTime>
    for df in tree.xpath('////*[name()="dwd:IssueTime"]'):
        print (dateutil.parser.parse(df.text).__format__("%d.%m.%Y %H:%M"))

    print ('\n')

    ele_TimeStamp = []
    for df in tree.xpath('//*[name()="dwd:ForecastTimeSteps"]'):
        timeslots = df.getchildren()
        for timeslot in timeslots:
            # print ('timeslot=' + timeslot.text)
            tm = dateutil.parser.parse(timeslot.text).__format__("%d.%m.%Y %H:%M")
            #tm = timeslot.text
            ele_TimeStamp.append(tm)
    print("Time", ele_TimeStamp)

    ele_PPPP = getElementValueAsList(tree, 'PPPP')  # =x/100
    for index, item in enumerate(ele_PPPP):
        ele_PPPP[index] = float(ele_PPPP[index]) / 100.0
    print("PPPP", ele_PPPP)

    ele_FX1 = getElementValueAsList(tree, 'FX1')
    print("FX1 ", ele_FX1)

    ele_ww = getElementValueAsList(tree, 'ww')
    print("ww  ", ele_ww)

    ele_SunD = getElementValueAsList(tree, 'SunD')  # =round(x)
    for index, item in enumerate(ele_SunD):
        ele_SunD[index] = round(float(ele_SunD[index]), 2)
    print("SunD", ele_SunD)

    ele_TX = getElementValueAsList(tree, 'TX')  # =x-273.15
    for index, item in enumerate(ele_TX):
        if (int(ele_TX[index]) > 99):
            ele_TX[index] = round(float(ele_TX[index]) - 273.15, 2)
    print("TX  ", ele_TX)

    ele_Tn = getElementValueAsList(tree, 'TN')  # =x-273.15
    for index, item in enumerate(ele_Tn):
        if (int(ele_Tn[index]) > 99):
            ele_Tn[index] = round(float(ele_Tn[index]) - 273.15, 2)
    print("Tn  ", ele_Tn)

    ele_Neff = getElementValueAsList(tree, 'Neff')  # =x*8/100
    for index, item in enumerate(ele_Neff):
        ele_Neff[index] = float(ele_Neff[index]) * 8 / 100
    print("Neff", ele_Neff)

    print("R101", getElementValueAsList(tree, 'R101'))


def go():
    url = 'https://opendata.dwd.de/weather/local_forecasts/mos/MOSMIX_L/single_stations/10400/kml/MOSMIX_L_LATEST_10400.kmz'

    kmz = zipfile.ZipFile(BytesIO(urlopen(url).read()), 'r')
    #kmz = zipfile.ZipFile('MOSMIX_L_LATEST_10400.kmz', 'r')

    kml_filename = kmz.namelist()[0]
    #print (kml_filename)

    tree = etree.parse(kmz.open(kml_filename, "r"))
    #print (tree)

    analyse(tree)

    kmz.close()


if __name__ == '__main__':
    print ('\n')
    go()
