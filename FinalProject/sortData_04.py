import pandas as pd
import xlsxwriter
from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy as np

class sensReading:
    def __init__(self):
        #-999 used a sentinel value to flag error
        self.temp = -999
        self.FDOY= -999
        self.PAppbv= -999
        self._49Cppbv = -999 #This is the more accurate sensor
        self.slope = -999
        self.readNum = -999
        self.PA_Slope = -999

    def print(self):
        print('Number:',self.readNum,'FDOY:',self.FDOY,'Temp:',self.temp,'PA (ppbv):',self.PAppbv,'49C (ppbv):',self._49Cppbv)

#defineSlopes() seperates data into 1 deg bins and calculates the slope  of regression. 
#The calculation of the slope also include readings whose temperature is at the upper and lower bounds of the bin
def defineSlopes(sensorData:list):
    startRange = -3
    endRange = startRange+1 #calculate correlation with 1deg bins
    maxTemp = 48
    startingIndex = 0
    while(endRange < maxTemp):
        i = startingIndex
        y_new = list()
        x_new = list()
        y_new.clear()
        x_new.clear()
        while sensorData[i].temp <= endRange and i < numOfValidReadings: # place x and y axis into seperate lists
            y_new.append(sensorData[i].PAppbv)
            x_new.append(sensorData[i]._49Cppbv)
            i+=1
        y_new = np.array(y_new)
        x_new = np.array(x_new)
        m,b = np.polyfit(x_new,y_new,1)
        i= startingIndex
        while sensorData[i].temp <= endRange and i < numOfValidReadings:    #Every node in the degree bin will have the same regression slope
            sensorData[i].slope = m
            i+=1
        startingIndex = i   #Move onto the next bin
        startRange = endRange
        endRange+=1
        while(sensorData[startingIndex].temp >= startRange): #Go back to begginning of the temperature range
            startingIndex-=1
        startingIndex+=1

def isNaN(num):
    return num!=num

def PA_vs_Slope(x:sensReading): #Check if values of sensorNode are changing
    currTemp = x.temp
    if currTemp >= -3.889 and currTemp<= 25.556:
        x.PA_Slope = x.PAppbv/((0.0061*x.temp) + 1.3717)
    elif currTemp > 25.556 and currTemp <= 32.778:
        x.PA_Slope = x.PAppbv/((-0.0197*currTemp) + 2.0461)
    elif currTemp > 32.778 and currTemp <= 40.556:
        x.PA_Slope = x.PAppbv/((-0.087*currTemp) + 4.2472)
    elif currTemp > 40.556 and currTemp < 44.444:
        x.PA_Slope = x.PAppbv/((0.0323*currTemp) - 0.459)
    elif currTemp >= 44.444:
        x.PA_Slope = x.PAppbv/((-0.3053*currTemp) + 14.53)

def additemByTemp(sensorData:list, newNode:sensReading):
    if len(sensorData) != 0:
        if sensorData[-1].temp < newNode.temp:
            sensorData.append(newNode)
        elif newNode.temp < sensorData[0].temp:
            sensorData.insert(0,newNode)
        else:
            x = 0
            while(x+1000 < len(sensorData)) and (sensorData[x+1000].temp <= newNode.temp):
                x+=1000
            while( x+100 < len(sensorData) ) and ( sensorData[x+100].temp <= newNode.temp ):
                x+=100
            while( x+10 < len(sensorData) ) and ( sensorData[x+10].temp <= newNode.temp ):
                x+=10
            while sensorData[x].temp < newNode.temp:
                x += 1
            sensorData.insert(x, newNode)
    elif len(sensorData) == 0:
        sensorData.append(newNode)

def scatterRegression(sensorData:list, start:float, end:float):
    i = 0
    while ( i+100 < len(sensorData)-1 ) and ( sensorData[i+100].temp <= start):
        i+=100
    while( i+10 < len(sensorData)-1 ) and ( sensorData[i+10].temp <= start ):
        i+=10
    while sensorData[i].temp <start:
        i += 1
    y = list() #THIS IS THE PA SENSOR
    x = list() #AND THIS IS THE 49C SENSOR
    y.clear()
    x.clear()
    y_new = list()
    x_new = list()
    y_new.clear()
    x_new.clear()
    while sensorData[i].temp <= end and i < numOfValidReadings: # place x and y axis into seperate lists
        y.append(sensorData[i].PAppbv)
        x.append(sensorData[i]._49Cppbv)
        y_new.append(sensorData[i].PAppbv)
        x_new.append(sensorData[i]._49Cppbv)
        i+=1
    y_new = np.array(y_new)
    x_new = np.array(x_new)
    m,b = np.polyfit(x_new, y_new, 1)
    plt.scatter(x,y, alpha=0.1)
    plt.plot(x_new, m*x_new + b, color='red')
    plt.title(f'49C vs PA.   Slope = {round(m,2)},   Temperature Range = {start}-{end}')
    plt.xlabel('49C ppbv', fontsize=14)
    plt.ylabel('PA ppbv', fontsize=14)
    plt.show()

df = pd.read_csv('TempBins_01.csv')
sensorData = list()
readData = list()
sensorData.clear()
progress = 0
numOfData = 42546
numOfValidReadings = 0
for i in range (0, numOfData):
    if i%4300 == 0:
        progress+=10
        print(progress,'%')
    readData = df.iloc[i]
    if isNaN(readData[2]) or isNaN(readData[1]):
        continue
    newNode = sensReading()
    newNode.FDOY = readData[0]
    newNode._49Cppbv = readData[1]
    newNode.PAppbv = readData[2]
    newNode.temp = readData[5]
    newNode.readNum = i+1
    PA_vs_Slope(newNode)
    additemByTemp(sensorData, newNode)
    numOfValidReadings+=1

#Start creating the excel spreadsheet with the data 
defineSlopes(sensorData)
print('Making new Spreadsheet')
outputName = 'SortedData.xlsx'
workbook = xlsxwriter.Workbook(outputName)      #Below here is formating 
worksheet = workbook.add_worksheet()
bold = workbook.add_format({'bold': 1})
worksheet.write('A1', 'Number',bold)
worksheet.write('B1', 'FDOY',bold)
worksheet.write('C1', 'Temp-C',bold)
worksheet.write('D1', 'PA ppbv',bold)
worksheet.write('E1', '49C ppbv',bold)
worksheet.write('F1', 'Slope', bold)
worksheet.write('G1', 'PA Calibrated', bold)
#Writing data into excel sheet
progress = 0
for i in range (1, numOfValidReadings):
    if i%4300 == 0:
        progress+=10
        print(progress,'%')
    worksheet.write_number(i, 0, i)
    worksheet.write_number(i, 1, sensorData[i].FDOY)
    worksheet.write_number(i, 2, sensorData[i].temp)
    worksheet.write_number(i, 3, sensorData[i].PAppbv)
    worksheet.write_number(i, 4, sensorData[i]._49Cppbv)
    worksheet.write_number(i, 5, sensorData[i].slope)
    worksheet.write_number(i, 6, sensorData[i].PA_Slope)
print('100%')
workbook.close()

#Loop to check plots
cont = 'c'
while(cont != 'q' and cont != 'Q'):
    print('Enter a temperature range from -3.8 to 47.7')
    start = float(input())
    end = float(input())
    if end <= start or start <-3.8 or end > 47.7:
        print("Bad input!")
    else:
        scatterRegression(sensorData, start, end)
    print('Quit = Q, Continue = c')
    cont = input()
print("Goodbye!")