import random
from math import pi, cos, sin

import numpy as np
from matplotlib import pyplot
from matplotlib.patches import Circle

def random_point(xy, r):
    r = float(r)
    theta = random.random() * 2 * pi
    return xy[0] + cos(theta) * r, xy[1] + sin(theta) * r

def circle(xy, radius, color, ax=None):
    e = Circle(xy=xy, radius=float(radius))
    ax.add_artist(e)
    e.set_edgecolor(color)
    e.set_facecolor('none')

def plot(vectors, radius, words, fig, ax ):
    colors = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(len(vectors))]
    for i, vector in enumerate(np.array(vectors)):
        circle(xy=vector, radius=radius[i], ax=ax, color=colors[i])

    x = [i[0] for i in vectors]
    y = [i[1] for i in vectors]
    max_radius = max(radius)
    if max_radius < 1:
        max_radius = 1
    margin = 1.2 * max_radius
    ax.set_xlim([min(x) - margin, max(x) + margin])
    ax.set_ylim([min(y) - margin, max(y) + margin])
    ax.set_aspect(1)

    for i, word in enumerate(words):
        point = random_point(vectors[i], radius[i])
        ax.text(vectors[i][0] + radius[i], vectors[i][1], '%s' % (str(word)), size=10, zorder=1, color=colors[i])
    fig.show()

def plot_dic(word2CircleDic, figure_title, filtered_words=[]):
    fig, ax = pyplot.subplots()
    fig.suptitle(figure_title, fontsize=20)
    if len(filtered_words) > 0:
        word2CircleDic = {k: word2CircleDic[k] for k in filtered_words if k in word2CircleDic}
    words = list(word2CircleDic.keys())
    radius = [values[-1] for values in word2CircleDic.values()]
    vectors = [np.multiply(np.array(values[:2]), values[-2]) for values in word2CircleDic.values()]
    plot(vectors, radius, words, fig, ax)