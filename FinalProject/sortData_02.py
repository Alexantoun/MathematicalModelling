import pandas as pd
import xlsxwriter
from pandas import DataFrame
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#In range 20-30 degrees, we have 1565

class sensReading:
    def __init__(self):
        #-999 used a sentinel value to flag error
        self.temp = -999
        self.FDOY= -999
        self.PAppbv= -999
        self._49Cppbv = -999 #This is the more accurate sensor
        self.readNum = -999

    def print(self):
        print('Number:',self.readNum,'FDOY:',self.FDOY,'Temp:',self.temp,'PA (ppbv):',self.PAppbv,'49C (ppbv):',self._49Cppbv)
def isNaN(num):
    return num!=num
def addItemBy49C(sensorData:list, newNode:sensReading):
    if len(sensorData) != 0:
        if sensorData[-1]._49Cppbv < newNode._49Cppbv:
            sensorData.append(newNode)
        elif newNode._49C < sensorData[0]._49Cppbv:
            sensorData.appendleft(newNode)
        else:
            x = 0
            while( x+100 < len(sensorData)-1 ) and ( sensorData[x+100]._49Cppbv < newNode._49Cppbv ):
                x+=100
            while( x+10 < len(sensorData)-1 ) and ( sensorData[x+10]._49Cppbv < newNode._49Cppbv ):
                x+=10
            while sensorData[x]._49Cppbv < newNode._49Cppbv:
                x += 1
            sensorData.insert(x, newNode)
    elif len(sensorData) == 0:
        sensorData.append(newNode)
    
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

def sortBins(sensorData:list, start:int, end:int):
    for i in sensorData:
        if i.temp <= end and i.temp >= start:
            i.printNode(i)
        elif i.temp>end:
            break

def scatterNoRegression(sensorData:list, start:int, end:int):
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
    #lineNum = 1
    while sensorData[i].temp <= end: # place x and y axis into seperate lists
        y.append(sensorData[i].PAppbv)
        x.append(sensorData[i]._49Cppbv)
        #print(lineNum, end=' ')
        sensorData[i].print()
        i+=1
        #lineNum+=1
    plt.plot(x, y, 'o', alpha=0.2)
    plt.title('49C vs PA')
    plt.xlabel('49C ppbv', fontsize=14)
    plt.ylabel('PA ppbv', fontsize=14)
    plt.grid(False)
    print(len(y))
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
    additemByTemp(sensorData, newNode)
    numOfValidReadings+=1


print('Making new Spreadsheet')
outputName = 'SortedData.xlsx'
workbook = xlsxwriter.Workbook(outputName)
worksheet = workbook.add_worksheet()
bold = workbook.add_format({'bold': 1})

row = 1
col = 0
worksheet.write('A1', 'Number',bold)
worksheet.write('B1', 'FDOY',bold)
worksheet.write('C1', 'Temp-C',bold)
worksheet.write('D1', 'PA ppbv',bold)
worksheet.write('E1', '49C ppbv',bold)
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
workbook.close()

cont = 'c'
while(cont != 'q' and cont != 'Q'):
    print('Enter a temperature range')
    start = int(input())
    end = int(input())
    scatterNoRegression(sensorData, start, end)
    print('Quit = Q, Continue = c')
    cont = input()
print("Goodbye!")