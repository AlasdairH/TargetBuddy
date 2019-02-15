import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import numpy as np
import imageio
from collections import defaultdict
import csv

dict_score = defaultdict(list)

diagramID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
plot_total_perDiagram = []
plot_avg_perDiagram = []

scatter_x = []
scatter_y = []

print("Loading data from file")
with open("data/scores.csv", "r") as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    line = 1
    for row in plots:
        dict_score[int(row[0])].append(int(row[1]))
        scatter_x.append(float(row[2]))
        scatter_y.append(float(row[3]))
        line = line + 1

# for every list of scores per diagram
for i in range(1, 11):
    print("Calculating data for diagram " + str(i))
    int_diagramTotal = 0
    # for every score in the list of the diagram
    int_numScores = 0
    for int_score in dict_score[i]:
        int_diagramTotal += int_score
        int_numScores = int_numScores + 1

    plot_total_perDiagram.append(int_diagramTotal)
    plot_avg_perDiagram.append(int_diagramTotal / int_numScores)

# labels
plt.xlabel("Shot Number")
plt.ylabel("Score")
plt.title("TargetBuddy")

#  FIGURE 1 - average per diagram
plt.figure(1, figsize=(2,2))
fig = plt.gcf()
fig.canvas.set_window_title("Average per Diagram")
plt.clf()
plt.plot(diagramID, plot_avg_perDiagram, label = "Total Score", color = "red")
axes = plt.gca()
axes.format_coord = lambda x, y: ""

# FIGURE 2 - scatter
plt.figure(2, figsize=(3,3))
fig = plt.gcf()
fig.canvas.set_window_title("Shot scatter")

img = imageio.imread("target.PNG")
plt.imshow(img, zorder=0, extent=[-25.0, 25.0, -25.0, 25.0])

plt.clf()
plt.scatter(scatter_x, scatter_y, label = "Scatter", color = "red")
axes = plt.gca()
axes.format_coord = lambda x, y: ""
axes.set_xlim([-10, 10])
axes.set_ylim([-10, 10])



# FIGURE 3 - heatmap
plt.figure(3, figsize=(3,3))
fig = plt.gcf()
fig.canvas.set_window_title("Shot Heatmap")

# image
heatmap, xedges, yedges = np.histogram2d(scatter_x, scatter_y, bins = 50)
extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
plt.clf()
plt.imshow(heatmap.T, extent = extent, origin = 'lower')
axes = plt.gca()
axes.set_facecolor((0.26, 0.0, 0.33))
axes.format_coord = lambda x, y: ""
axes.set_xlim([-10, 10])
axes.set_ylim([-10, 10])

# legends
#plt.legend()

plt.show()

