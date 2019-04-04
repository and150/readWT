import argparse
import math
import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
#from collections import OrderedDict

VSTR = 2
RSTR = 5


def readRegimes(inpFile):
    arr = {}
    curr = {}
    with open(inpFile) as file:
        for line in file:
            words = str.split(line)
            if(len(words) > RSTR and  
                    words[1].count(".") == 2 and
                    words[2].count(":") == 2):
                currDate = dt.datetime.strptime(words[1]+' '+words[2],"%d.%m.%Y %H:%M:%S")
                curr = {currDate : words[3:]}
                arr.update(curr)
    return arr

def readVector(inpFile, dates_interval):
    arr = {}
    curr ={}
    with open(inpFile) as file:
        for line in file:
            words = str.split(line)
            if(len(words) > VSTR and  
                    words[0].count(".") == 2 and
                    words[1].count(":") == 2):

                currDate = dt.datetime.strptime(words[0]+' '+words[1],"%d.%m.%Y %H:%M:%S")
                if(currDate >= dates_interval[0] and currDate <= dates_interval[1] ):
                    curr = {currDate : words[2:]}
                    arr.update(curr)
    return arr


def extractValues(dict1, x,y):
    outArr =[]
    for z in dict1:
        try:
            outArr.append(float(dict1[z][x][y]))
        except:
            outArr.append(0.0)
    return outArr
           

def makeTimeFrame(regimeDict):
    r = list(regimeDict.keys())
    tdarr = [
             dt.timedelta(hours = 0.01),
             dt.timedelta(hours = 0.02),
             dt.timedelta(hours = 0.04),
             dt.timedelta(hours = 0.07),
             dt.timedelta(hours = 0.15),
             dt.timedelta(hours = 0.30),
             dt.timedelta(hours = 0.70),
             dt.timedelta(hours = 1.50),
             dt.timedelta(hours = 3.00),
             dt.timedelta(hours = 6.00),
             dt.timedelta(hours = 12.0),
             dt.timedelta(hours = 24.0)
            ]

    lt = len(tdarr)
    len_r = len(r)
    datesOutZ = []
    datesOutL = []
    datesOut = []
    daysDelta = 0

    # insert additional dates (~log)
    for i in range(0, len_r - 1):
        currDate = r[i] 
        count = 0
        while(currDate < r[i+1]):
            currDate = currDate + tdarr[count]
            datesOutL.append(currDate)
            #print(currDate)
            count = count + 1
            if(count >= lt): break

    # insert zeros to override history
    for i in range(0, len_r - 1):
        currDate = r[i] 
        #print("_", end="")
        while(currDate < r[i+1]):
            datesOutZ.append(currDate)
            #print(currDate)
            currDate = nextDay(currDate)
    currDate = r[len_r-1]
    datesOutZ.append(currDate)
    #print("_", end="")
    #print(currDate)


    # combine two lists of dates
    in_Z = set(datesOutZ)
    in_L = set(datesOutL)
    in_L_but_not_in_Z = in_L - in_Z
    datesOut = datesOutZ + list(in_L_but_not_in_Z)
    datesOut.sort()
    #for i in range(0, len(datesOut)):
    #    print(datesOut[i])

    return datesOut


def nextDay(date1):
    nextDay = date1  + dt.timedelta(days = 1)
    nextDay = nextDay.replace(hour = 0, minute = 0, second = 0)
    #print(date1, nextDay, "aaa")
    return nextDay

def isDiffDay(date1, date2):
    if(date1.year == date2.year and date1.month == date2.month and date1.day == date2.day):
        return False
    else:
        return True


def pickPress(p, dates):
    dStack = dates[:]
    pOut = {}

    while dStack:
        find = dStack.pop(0)
        if find in p:
            pOut.update({find : p[find]})
        else:
            ff = min(p.keys(), key = lambda k: abs(k - find)) 
            pOut.update({ff : p[ff]})
    return pOut



def setup(ax):
    ax.xaxis.set_major_formatter(md.DateFormatter('%d.%m.%Y'))
    ax.xaxis.set_major_locator(md.DayLocator())
    ax.xaxis.set_minor_locator(md.HourLocator())
    #ax.tick_params(axis='x', which='major', length = 10, width = 5.0)
    #ax.tick_params(axis='x', which='minor', length = 1, width = 0.5)
 

def makeGraph(q, p, r, pf):
    # make graphs
    qDates  = md.date2num(list(q.keys()))
    pDates  = md.date2num(list(p.keys()))
    rDates  = md.date2num(list(r.keys()))
    pfDates = md.date2num(list(pf.keys()))

    qValues  = list(float(item[0]) for item in list(q.values()))
    pValues  = list(float(item[0]) for item in list(p.values()))
    rValues  = list(float(item[0]) for item in list(r.values()))
    pfValues = list(float(item[0]) for item in list(pf.values()))

    
    fig, ax1 = plt.subplots()
    ax1.plot_date(qDates, qValues, 'k-', drawstyle = 'steps')
    ax2 = ax1.twinx()
    ax2.plot_date(pDates, pValues, 'g.', markersize = 1)
    setup(ax2)

    for i in range(0,len(rDates)):
        plt.axvline(x = rDates[i], ymin = 0, linewidth = 0.5, color = 'red')
       
    ax2.plot_date(pfDates, pfValues, 'k.', markersize = 10)
    plt.show()

def makeEtab(pressFiltered, regimes):
    commonTimeFrame = list(set([*regimes, *pressFiltered]))
    commonTimeFrame.sort()

    eventTable = []
    prevrr = [None]

    for time in commonTimeFrame:

        if time in pressFiltered:
            pp = float(*pressFiltered[time])
        else:
            pp = 0.01

        if time in regimes:
            rr = regimes[time] 
            prevrr = regimes[time]
        else:
            rr = prevrr + ['add'] 


        eventTable.append([time, pp, *rr])

    for xx in eventTable:
        print(*xx)


def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q","--RATE",  action="store", help ="read rates", default =None)
    parser.add_argument("-p","--PRESS", action="store", help ="read pessure", default =None)
    parser.add_argument("-r","--REGIMES", action="store", help ="read regimes", default =None)
    args = parser.parse_args()

    p = {} # pressure dictionary
    q = {} # rate dictionary
    r = {} # regimes dictionary

    pFilt = {} # filtered pressure dictionary
    qFilt = {} # filtered rate dictionary

    pqHistOut = [] # output array for WT file
    tfw = [] # dates framework 

    if(args.RATE!=None and args.PRESS!=None and args.REGIMES!=None):
        r = readRegimes(args.REGIMES)
        gdiInterval = [min(r), max(r)]

        # generate time framework
        tfw = makeTimeFrame(r)

        # read P and Q vectors
        q = readVector(args.RATE,  gdiInterval)
        p = readVector(args.PRESS, gdiInterval)
        pFilt = pickPress(p, tfw)

        makeEtab(pFilt, r)

        makeGraph(q, p, r, pFilt)
    else:
        print("No input files")

# start main programm
Main()
