from collections import deque
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

def addItemBy49C(sensorData:deque, newNode:sensReading):
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
    
def additemByTemp(sensorData:deque, newNode:sensReading):
    if len(sensorData) != 0:
        if sensorData[-1].temp < newNode.temp:
            sensorData.append(newNode)
        elif newNode.temp < sensorData[0].temp:
            sensorData.appendleft(newNode)
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

def sortBins(sensorData:deque, start:int, end:int):
    for i in sensorData:
        if i.temp <= end and i.temp >= start:
            i.printNode(i)
        elif i.temp>end:
            break

def scatterByTemp(sensorData:deque, start:int, end:int):
    x = 0
    while ( x+100 < len(sensorData)-1 ) and ( sensorData[x+100].temp <= start):
        x+=100
    while( x+10 < len(sensorData)-1 ) and ( sensorData[x+10].temp <= start ):
        x+=10
    while sensorData[x].temp <start:
        x += 1
    PA = list()
    t49c = list()
    PA.clear()
    t49c.clear()
    lineNum = 1
    while sensorData[x].temp <= end: # place x and y axis into seperate lists
        PA.append(sensorData[x].PAppbv)
        t49c.append(sensorData[x]._49Cppbv)
        print(lineNum, end=' ')
        sensorData[x].print()
        x+=1
        lineNum+=1
    plt.scatter(t49c, PA)
    plt.title('49C vs PA')
    plt.xlabel('49C ppbv', fontsize=14)
    plt.ylabel('PA ppbv', fontsize=14)
    plt.grid(False)
    print(len(PA))
    plt.show()
    

def scatterBy49C(sensorData:deque, start:int, end:int):
    x = 0
    while ( x+100 < len(sensorData)-1 ) and ( sensorData[x+100]._49Cppbv < start ):
        x+=100
    while( x+10 < len(sensorData)-1 ) and ( sensorData[x+10]._49Cppbv < start ):
       x+=10
    while sensorData[x]._49Cppbv < start:
       x += 1
    PA = list()
    t49c = list()
    PA.clear()
    t49c.clear()
    while sensorData[x]._49Cppbv < end: # place x and y axis into seperate lists
        PA.append(sensorData[x].PAppbv)
        t49c.append(sensorData[x]._49Cppbv)
        sensorData[x].print()
        x+=1
    plt.scatter(t49c, PA)
    plt.title('49C vs PA')
    plt.xlabel('49C ppbv', fontsize=14)
    plt.ylabel('PA ppbv', fontsize=14)
    plt.grid(False)
    plt.show()
    tkPlot = input("Do you want a TKinter Plot?(y/Y): ")
    if tkPlot == 'y' or tkPlot=='Y':
        data = {'PA':PA, '49C':t49c}
        df = DataFrame(data,columns=['PA','49C'])
        root = tk.Tk()
        figure = plt.Figure(figsize=(10,8), dpi=100)
        ax = figure.add_subplot(111)
        ax.scatter(df['PA'],df['49C'],color='g')
        scatter = FigureCanvasTkAgg(figure, root) 
        scatter.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
        ax.legend(['49C']) 
        ax.set_xlabel('PA')
        ax.set_title('PA Vs. 49C')
        root.mainloop()
    print('Done')
    

df = pd.read_csv('TempBins_01.csv')
sensorData = deque()
readData = list()
sensorData.clear()
progress = 0
numReadings = 42546
for i in range (0, numReadings):
    if i%4300 == 0:
        progress+=10
        print(progress,'%')
    readData = df.iloc[i]
    newNode = sensReading()
    newNode.FDOY = readData[0]
    newNode._49Cppbv = readData[1]
    newNode.PAppbv = readData[2]
    newNode.temp = readData[5]
    newNode.readNum = i+1
    #addItemBy49C(sensorData, newNode)
    additemByTemp(sensorData, newNode)
    newNode.print()

print("Done")
print(len(sensorData))

print('Enter the plot range')
start = int(input())
end = int(input())
scatterByTemp(sensorData, start, end)
