import multiprocessing
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cbook as cbook
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasAgg

import numpy as np
import imageio
from collections import defaultdict
import csv
import sqlite3
import tkinter as tk
import time

diagramID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
targetMap = { 1:1, 2:2, 3:3, 4:4, 5:7, 6:12, 7:11, 8:10, 9:9, 10:6 }

def insertToDB(_data):
    db_cursor.executemany("INSERT INTO shots (id, date, card, diagram, score, x, y) VALUES (?,?,?,?,?,?,?)", (_data,))

def getNumberOfCardsInDB():
    query = db_cursor.execute("SELECT COUNT(id) FROM shots")
    lastID = int(query.fetchone()[0])
    return int(lastID / 10)

def parseCSV(_filename):
    # diagram, score, x, y
    print("Loading data from csv")
    query = db_cursor.execute("SELECT COUNT(id) FROM shots")
    lastID = int(query.fetchone()[0])
    numCards = int(lastID / 10)
    print(str(numCards) + " already in database, starting at " + str(int(numCards) + 1))
    numCards = numCards + 1
    with open(_filename) as csvfile:
        cardsRead = 0
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            data = (lastID, "TEST_DATE", numCards, int(row[0]), int(row[1]), float(row[2]), (float(row[3]) * -1.0))
            insertToDB(data)
            cardsRead += 1
            lastID += 1
            if(int(row[0]) == 10):
                numCards = numCards + 1

    print("Added " + str(int(cardsRead / 10)) + " to database")

def plotTarget(_axis):
    fig = _axis.get_figure()
    # patches
    #outer
    _axis.add_patch(mpatches.Circle([0, 0], 23.75, linestyle = "-", fill = True, color = "black", linewidth = 0.5))
    # bull
    _axis.add_patch(mpatches.Circle([0, 0], 0.8, linestyle = "-", fill = True, color = "white", linewidth = 0.5))
    radius = 6.25
    for i in range(0, 6):
        _axis.add_patch(mpatches.Circle([0, 0], radius, linestyle = "-", fill = False, color = "white", linewidth = 0.5))
        radius = radius + 3.5

    _axis.plot([-25, 25], [0, 0], color="white", linestyle = '-', linewidth = 0.5)
    _axis.plot([0, 0], [-25, 25], color="white", linestyle = '-', linewidth = 0.5)

def summary(dict_score, dict_scatter):

    scatter_x = []
    scatter_y = []

    plot_total_perDiagram = []
    plot_avg_perDiagram = []
    # for every list of scores per diagram
    for i in range(1, 11):
        int_diagramTotal = 0
        # for every score in the list of the diagram
        int_numScores = 0
        for int_score in dict_score[i]:
            int_diagramTotal += int_score
            int_numScores = int_numScores + 1

        plot_total_perDiagram.append(int_diagramTotal)
        plot_avg_perDiagram.append(int_diagramTotal / int_numScores)

        # for every score in the list of the diagram
        int_numScores = 0
        for scatterPos in dict_scatter[i]:
            scatter_x.append(scatterPos[0])
            scatter_y.append(scatterPos[1] * -1)

    # FIGURE 1 - average per diagram
    fig, axes = plt.subplots()
    # title
    fig.canvas.set_window_title("Average per Diagram");
    axes.set_title("Average Score per Diagram")
    # labels
    axes.format_coord = lambda x, y: ""
    axes.set_xlabel("Diagram")
    axes.set_ylabel("Score")
    # plot
    plt.plot(diagramID, plot_avg_perDiagram, label = "Total Score", color = "blue")
    # save
    plt.savefig("save/summary/PD_avg_score")
    plt.close(fig)

    createHeatmap(scatter_x, scatter_y, 20, "Summary Heatmap", "save/summary/OA_heatmap")
    createSpread(scatter_x, scatter_y, "Summary Spread", "save/summary/OA_spread")

def perDiagram():
    numCards = getNumberOfCardsInDB()

    figureHeatmap = plt.figure(figsize = (16, 9), dpi = 100)
    figureSpread = plt.figure(figsize = (16, 9), dpi = 200)

    pos = [3, 4, 1]

    for i in range(1, 11):
        data_scatter_x = db_cursor.execute("SELECT x FROM shots WHERE diagram = " + str(i)).fetchall()
        data_scatter_y = db_cursor.execute("SELECT y FROM shots WHERE diagram = " + str(i)).fetchall()

        scatter_x = []
        scatter_y = []

        # reformat data to list
        for x in data_scatter_x:
            scatter_x.append(x[0])
        for y in data_scatter_y:
            scatter_y.append(y[0])

        pos[2] = targetMap[i]
        createHeatmap(figureHeatmap, pos, scatter_x, scatter_y, "Diagram " + str(i) + " Heatmap")
        createSpread(figureSpread, pos, scatter_x, scatter_y, "Diagram " + str(i) + " Spread")
    
    figureHeatmap.subplots_adjust(wspace = 0.5, hspace = 0.5)
    figureSpread.subplots_adjust(wspace = 0.5, hspace = 0.5)

    #figureHeatmap.show()
    #figureSpread.show()
    figureHeatmap.savefig("save/per_diagram/diagram_heatmap")
    figureSpread.savefig("save/per_diagram/diagram_spread")
    plt.close(figureHeatmap)
    plt.close(figureSpread)

def perCard():
    numCards = getNumberOfCardsInDB()
    for i in range(1, numCards + 1):
        data_scatter_x = db_cursor.execute("SELECT x FROM shots WHERE card = " + str(i)).fetchall()
        data_scatter_y = db_cursor.execute("SELECT y FROM shots WHERE card = " + str(i)).fetchall()

        scatter_x = []
        scatter_y = []

        # reformat data to list
        for x in data_scatter_x:
            scatter_x.append(x[0])
        for y in data_scatter_y:
            scatter_y.append(y[0])



def createSpread(_figure, _pos, scatter_x, scatter_y, _title):

    xTotal = 0
    for xVal in scatter_x:
        xTotal += xVal

    yTotal = 0
    for yVal in scatter_y:
        yTotal += yVal

    xAvg = xTotal / len(scatter_x)
    yAvg = yTotal / len(scatter_y)

    # FIGURE 2 - scatter
    axes = _figure.add_subplot(_pos[0], _pos[1], _pos[2])
    axes.set_aspect("equal")
    # title
    #fig.canvas.set_window_title("Shot Scatter");
    axes.set_title(_title)
    # labels
    axes.format_coord = lambda x, y: ""
    axes.set_xlabel("mm")
    axes.set_ylabel("mm")
    # axes
    axes.format_coord = lambda x, y: ""
    axes.set_xlim([-25, 25])
    axes.set_ylim([-25, 25])

    plotTarget(axes)

    patch_avg = axes.add_patch(mpatches.Circle([xAvg, yAvg], 0.5, linestyle = "-", fill = True, color = "green", linewidth = 0.5, label = "Average", zorder = 20))
    plot_scatter = plt.scatter(scatter_x, scatter_y, label = "Shot", color = [1, 0, 0, 0.25], s = 200, edgecolors = "none", zorder = 10)

    # legend
    plt.legend(handles=[plot_scatter, patch_avg])

def createHeatmap(_figure, _pos, scatter_x, scatter_y, _title):
    # FIGURE 3 - heatmap
    axes = _figure.add_subplot(_pos[0], _pos[1], _pos[2])
    axes.set_aspect("equal")
    # title
    axes.set_title(_title)
    # labels
    axes.format_coord = lambda x, y: ""
    axes.set_xlabel("mm")
    axes.set_ylabel("mm")
    # axes edit
    axes.set_facecolor((0.26, 0.0, 0.33))
    axes.format_coord = lambda x, y: ""
    axes.set_xlim([-25.2, 25])
    axes.set_ylim([-25, 25])
    #axes.grid(linestyle = ":")

    plotTarget(axes)

    # image
    heatmap, xedges, yedges = np.histogram2d(scatter_x, scatter_y, bins = 20)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    axes.imshow(heatmap.T, extent = extent, origin = "lower")

def cmdImport(_filepath):
    print("Starting import")
    parseCSV(_filepath)
    db.commit()
    print("Import complete")

def cmdGenerateAll():
    query = db_cursor.execute("SELECT COUNT(id) FROM shots")
    lastID = int(query.fetchone()[0])
    if(lastID == 0):
        print("No data to generate from")
        return

    start = time.time()
    #print("Creating Summary")
    #summary()
    print("Collating per diagram data")
    perDiagram()
    #print("Collating per card data")
    #perCard()
    end = time.time()
    print("Generation took " + str(end - start) + " seconds")

def cmdClearDB():
    print("Clearing database")
    db_cursor.execute("DROP TABLE IF EXISTS shots")
    db_cursor.execute("CREATE TABLE IF NOT EXISTS shots (id INTEGAR PRIMARY KEY, date TEXT, card INTEGAR, diagram INTEGAR, score INTEGAR, x REAL, y REAL)")
    db.commit()

def createUI():
    root = tk.Tk()
    root.title("TargetBuddy")
    w1 = tk.Label(root, text = "File: ")
    w2 = tk.Entry(root)
    w3 = tk.Button(root, text = "Import", command = lambda: cmdImport(w2.get()))
    w4 = tk.Button(root, text = "Clear Database", command = cmdClearDB)
    w5 = tk.Button(root, text = "Generate All", command = cmdGenerateAll)
    
    w1.grid(row = 0, column = 0)
    w2.grid(row = 0, column = 1)
    w3.grid(row = 1, column = 0)
    w4.grid(row = 1, column = 1)
    w5.grid(row = 2, column = 0)
    
    w2.insert(10, "data/scores.csv")

# start
db = sqlite3.connect("TargetBuddy.db", check_same_thread = False)
db_cursor = db.cursor()

db_cursor.execute("CREATE TABLE IF NOT EXISTS shots (id INTEGAR PRIMARY KEY, date TEXT, card INTEGAR, diagram INTEGAR, score INTEGAR, x REAL, y REAL)")
db.commit()

print("Getting number of cards in DB")
query = db_cursor.execute("SELECT COUNT(id) FROM shots")
numCards = query.fetchone()
print("Found " + str(int(int(numCards[0]) / 10)) + " cards in databse")

createUI()
tk.mainloop()

db.close()
print("Complete");

