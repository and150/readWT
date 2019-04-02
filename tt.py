import argparse
import math
import datetime as dt

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

VSTR = 2
RSTR = 5
TIME_TOL = 0.01
SEC_TOL = 5  
MIN_TOL = 5

def readRegimes(inpFile):
    arr = []
    with open(inpFile) as file:
        for line in file:
            words = str.split(line)
            if(len(words) > RSTR and  
                    words[1].count(".") == 2 and
                    words[2].count(":") == 2):
                arr.append([
                    dt.datetime.strptime(words[1]+' '+words[2],"%d.%m.%Y %H:%M:%S"),
                    words[3:]
                         ])
    return arr

def getMinMaxDate(regimes):
    minDate = regimes[0][0]
    maxDate = regimes[len(regimes)-1][0]
    return [minDate, maxDate]

def readVector(inpFile, dates_interval):
    arr = []
    with open(inpFile) as file:
        for line in file:
            words = str.split(line)
            if(len(words) > VSTR and  
                    words[0].count(".") == 2 and
                    words[1].count(":") == 2):

                currDate = dt.datetime.strptime(words[0]+' '+words[1],"%d.%m.%Y %H:%M:%S")
                if(currDate >= dates_interval[0] and currDate <= dates_interval[1] ):
                    arr.append([currDate, words[2:]])

    return arr


def extractDates(arr1):
    outArr =[]
    for i in range(0, len(arr1)):
        outArr.append(arr1[i][0])
    return outArr

def extractValues(arr1, x,y):
    outArr =[]
    for i in range(0, len(arr1)):
        try:
            outArr.append(float(arr1[i][x][y]))
        except:
            outArr.append(0.0)
    return outArr
           



def makeTimeFrame(r):
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
        currDate = r[i][0] 
        count = 0
        while(currDate < r[i+1][0]):
            currDate = currDate + tdarr[count]
            datesOutL.append(currDate)
            #print(currDate)
            count = count + 1
            if(count >= lt): break

    # insert zeros to override history
    for i in range(0, len_r - 1):
        currDate = r[i][0] 
        #print("_", end="")
        while(currDate < r[i+1][0]):
            datesOutZ.append(currDate)
            #print(currDate)
            currDate = nextDay(currDate)
    currDate = r[len_r-1][0]
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
    pOut = []

    for i in range(0, len(dates)):
        pOut = next(x for x in p if dates[i] in x)

    return pOut


def pickPress1(p, dates):
    p_filt = []
    for i in range(0, len(p)):
        ifPicked = 0
        j = 0
        for t in range(j, len(dates)):
            if(abs( (p[i][0] - dates[t]).seconds ) < 5):
                p_filt.append(p[i])
                j = j + 1
    return p_filt



def makeGraph(q, p, r, p_filt):
    # make graphs
    dates = matplotlib.dates.date2num(extractDates(q))
    dates1 = matplotlib.dates.date2num(extractDates(p))
    dates2 = matplotlib.dates.date2num(extractDates(r))
    dates3 = matplotlib.dates.date2num(extractDates(p_filt))
    
    qValues = extractValues(q,1,1)
    pValues = extractValues(p,1,0)
    rValues = extractValues(r,1,0)
    pf_Values = extractValues(p_filt,1,0)
    
    
    fig, ax1 = plt.subplots()
    ax1.plot_date(dates, qValues, 'k-', drawstyle = 'steps')
    
    ax2 = ax1.twinx()
    ax2.plot_date(dates1, pValues, 'g.', markersize = 1)
    
    for i in range(0,len(dates2)):
        plt.axvline(x = dates2[i], ymin = 0, linewidth = 0.5, color = 'red')
        
    ax2.plot_date(dates3, pf_Values, 'm.', markersize = 10)
    
    plt.show()



def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q","--RATE",  action="store", help ="read rates", default =None)
    parser.add_argument("-p","--PRESS", action="store", help ="read pessure", default =None)
    parser.add_argument("-r","--REGIMES", action="store", help ="read regimes", default =None)
    args = parser.parse_args()

    p = [] # pressure array
    q = [] # rate array

    r = [] # regimes array

    p_filt = [] # filtered pressure array
    q_filt = [] # filtered rate array

    pq_hist_out = [] # output array for WT file
    dates_filt = [] # dates framework 

    if(args.RATE!=None and args.PRESS!=None and args.REGIMES!=None):
        r = readRegimes(args.REGIMES)
        gdi_interval = getMinMaxDate(r)

        # generate time framework
        dates_filt = makeTimeFrame(r)
        #for i in range(0, len(dates_filt)):
        #    print(dates_filt[i])

        # read P and Q vectors
        q = readVector(args.RATE, gdi_interval)
        p = readVector(args.PRESS, gdi_interval)

        p_filt = pickPress(p, dates_filt)

        for i in range(0, len(p_filt)):
            print(p_filt[i][0], p_filt[i][1])
        #print(p_filt)

        ### print read data
        ###for i in range(0,len(q)):
        ###    print(q[i][0], q[i][1][1], q[i][1][2])
        ###for i in range(0,len(p)):
        ###    print(p[i][0], p[i][1][0])
        ###for i in range(1,len(r)):
        ###    print(r[i][0], r[i][1][0], r[i][0] - r[i-1][0])

        makeGraph(q, p, r, p_filt)

    else:
        print("No input files")



# start main programm
Main()
