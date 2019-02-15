import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cbook as cbook
import numpy as np
import imageio
from collections import defaultdict
import csv

diagramID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

def parseCSV(_filename):
    dict_score = defaultdict(list)
    dict_scatter = defaultdict(list)

    scatter_x = []
    scatter_y = []

    print("Loading data from file")
    with open(_filename) as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        line = 1
        for row in plots:
            dict_score[int(row[0])].append(int(row[1]))
            dict_scatter[int(row[0])].append([float(row[2]), float(row[3])])
            scatter_x.append(float(row[2]))
            scatter_y.append(float(row[3]) * -1.0)
            line = line + 1
    
    return dict_score, dict_scatter

def plotTarget(_axis):
    # patches
    _axis.add_patch(mpatches.Circle([0, 0], 0.8, linestyle = "-", fill = False, color = "black", linewidth = 0.5))
    radius = 6.25
    for i in range(0, 6):
        _axis.add_patch(mpatches.Circle([0, 0], radius, linestyle = "-", fill = False, color = "black", linewidth = 0.5))
        radius = radius + 3.5

    plt.plot([-25, 25], [0, 0], color="black", linestyle = '-', linewidth = 0.5)
    plt.plot([0, 0], [-25, 25], color="black", linestyle = '-', linewidth = 0.5)

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

def createSpread(scatter_x, scatter_y, _title, _savePath):

    xTotal = 0
    for xVal in scatter_x:
        xTotal += xVal

    yTotal = 0
    for yVal in scatter_y:
        yTotal += yVal

    xAvg = xTotal / len(scatter_x)
    yAvg = yTotal / len(scatter_y)

    # FIGURE 2 - scatter
    fig, axes = plt.subplots()
    axes.set_aspect("equal")
    # title
    fig.canvas.set_window_title("Shot Scatter");
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

    patch_avg = axes.add_patch(mpatches.Circle([xAvg, yAvg], 0.5, linestyle = "-", fill = True, color = "green", linewidth = 0.5, label = "Average"))
    plot_scatter = plt.scatter(scatter_x, scatter_y, label = "Shot", color = [1, 0, 0, 0.25], s = 450)

    # legend
    plt.legend(handles=[plot_scatter, patch_avg])

    plt.savefig(_savePath)
    plt.close(fig)

def createHeatmap(scatter_x, scatter_y, _res, _title, _savePath):
    # FIGURE 3 - heatmap
    fig, axes = plt.subplots()
    axes.set_aspect("equal")
    # title
    fig.canvas.set_window_title(_title)
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
    heatmap, xedges, yedges = np.histogram2d(scatter_x, scatter_y, bins = _res)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    plt.imshow(heatmap.T, extent = extent, origin = "lower")
    plt.savefig(_savePath)
    plt.close(fig)

def perDiagram(_diagramDict_score, _diagramDict_scatter):
    for i in range(1, 11):
        scatter_x = []
        scatter_y = []

        # for every score in the list of the diagram
        int_numScores = 0
        for scatterPos in _diagramDict_scatter[i]:
            scatter_x.append(scatterPos[0])
            scatter_y.append(scatterPos[1] * -1)
            int_numScores = int_numScores + 1

        createHeatmap(scatter_x, scatter_y, int_numScores / 2, "Diagram " + str(i) + " Heatmap", "save/per_diagram/heatmap/diagram" + str(i) + "_heatmap")
        createSpread(scatter_x, scatter_y, "Diagram " + str(i) + " Spread", "save/per_diagram/spread/diagram" + str(i) + "_spread")

def perCard(_diagramDict_score, _diagramDict_scatter):
    numCards = len(_diagramDict_scatter[1])
    print("Parsing " + str(numCards) + " cards")
    for card in range(0, numCards):
        scatter_x = []
        scatter_y = []

        # for every score in the list of the diagram
        int_numScatters = 0
        for xy in range(1, 11):
            scatter_x.append(_diagramDict_scatter[xy][card][0])
            scatter_y.append(_diagramDict_scatter[xy][card][1] * -1.0)

        createHeatmap(scatter_x, scatter_y, numCards / 2, "Card " + str(card) + " Heatmap", "save/per_card/heatmap/card" + str(card) + "_heatmap")
        createSpread(scatter_x, scatter_y, "Card " + str(card) + " Spread", "save/per_card/spread/card" + str(card) + "_spread")

# start
diagramDict_score, diagramDict_scatter = parseCSV("data/scores.csv")
print("Creating Summary")
summary(diagramDict_score, diagramDict_scatter)
print("Collating per card data")
perCard(diagramDict_score, diagramDict_scatter)
print("Collating per diagram data")
perDiagram(diagramDict_score, diagramDict_scatter)
print("Complete");

