import itertools
import math
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from visualization.ploting import plot_dic
import json

def reduce_dimensions(word2BallDic):
    vectors = []
    words = []
    word2CircleDic = {}
    for word, values in word2BallDic.items():
        words.append(word)
        vectors.append(np.multiply(values[:-2], values[-2]))
    reduced_vectors = PCA(2).fit_transform(vectors)
    for i, word in enumerate(words):
        v, l = get_vector_and_length(reduced_vectors[i])
        word2CircleDic[word] = [v[0], v[1], l, word2BallDic[word][-1]]  # TODO Fix me
    return word2CircleDic


def get_coordinates_circle(circle):
    return np.multiply(circle[:-2], circle[-2])


def get_coordinates(word, word2CircleDic):
    return np.multiply(word2CircleDic[word][:-2], word2CircleDic[word][-2])


def get_vector_and_length(coordinates):
    magnitude = np.linalg.norm(coordinates)
    return [ele / magnitude for ele in coordinates], magnitude


def magic_scaling(word, word2CircleDic, wsChildrenDic, root, scale_factor):
    children = wsChildrenDic[word]
    word2CircleDic[word][-1] = abs(word2CircleDic[word][-1] * scale_factor)
    if word != root:
        word_center = get_coordinates(word, word2CircleDic)
        root_center = get_coordinates(root, word2CircleDic)
        delta = scale_factor * (word_center[0] - root_center[0]), scale_factor * (word_center[1] - root_center[1])
        new_center = root_center[0] + delta[0], root_center[1] + delta[1]
        new_vector, new_length = get_vector_and_length(new_center)
        word2CircleDic[word][-2] = new_vector
        word2CircleDic[word][-2] = new_length
    if len(children) == 0:
        return
    for child in children:
        magic_scaling(child, word2CircleDic, wsChildrenDic, root, scale_factor)


def disjoint_circles_by_scaling_down(word1, word2, word2CircleDic, wsChildrenDic):
    old_radius1 = word2CircleDic[word1][-1]
    old_radius2 = word2CircleDic[word2][-1]
    dis = dis_between_circles_centers(word2CircleDic[word1], word2CircleDic[word2])
    dis = (dis - (dis * 0.01))
    scale_factor = dis / (old_radius1 + old_radius2)
    magic_scaling(word1, word2CircleDic, wsChildrenDic, word1, scale_factor)
    magic_scaling(word2, word2CircleDic, wsChildrenDic, word2, scale_factor)


def contain_circles(child, parent, word2CircleDic, wsChildrenDic):
    if word2CircleDic[child][-1] == 0:
        return
    dis = dis_between_circles_centers(word2CircleDic[child], word2CircleDic[parent])
    dis = (dis + (dis * 0.05))
    if is_circles_disjoint(word2CircleDic[child], word2CircleDic[parent]):
        scale_factor = (word2CircleDic[child][-1] + dis) / word2CircleDic[parent][-1]
        word2CircleDic[parent][-1] = abs(word2CircleDic[parent][-1] * scale_factor)
    else:
        scale_factor = (word2CircleDic[parent][-1] - dis) / word2CircleDic[child][-1]
        magic_scaling(child, word2CircleDic, wsChildrenDic, child, scale_factor)


def dis_between_circles_centers(circle1, circle2):
    if circle1 == circle2:
        return 0
    circle1XY = get_coordinates_circle(circle1)
    circle2XY = get_coordinates_circle(circle2)
    sum = 0
    for i in range(len(circle1XY)):
        sum = sum + pow(circle2XY[i] - circle1XY[i], 2)
    return math.sqrt(sum)


def disjoint_degree(circle1, circle2):
    dis = dis_between_circles_centers(circle1, circle2)
    return dis - circle1[-1] - circle2[-1]


def is_circles_disjoint(circle1, circle2):
    degree = disjoint_degree(circle1, circle2)
    if degree < 0:
        return False
    return True


def containment_degree(circle1, circle2):
    dis = dis_between_circles_centers(circle1, circle2)
    return circle2[-1] - dis - circle1[-1]


def is_circle2_contains_circle1(circle1, circle2):
    degree = containment_degree(circle1, circle2)
    if degree < 0:
        return False
    return True


def save_data(file_path, word2CircleDic):
    with open(file_path, 'w') as file:
        for word, values in word2CircleDic.items():
            file.write(word + " ")
            file.write(" ".join(str(value) for value in values))
            file.write("\n")


def read_balls_file(file_path, word2CircleDic=dict()):
    with open(file_path, mode="r", encoding="utf-8") as w2ball:
        for line in w2ball.readlines():
            wlst = line.strip().split()
            word2CircleDic[wlst[0]] = [float(ele) for ele in wlst[1:]]
        return word2CircleDic


def read_chilren_file(wsChildrenFile, wsChildrenDic=dict()):
    with open(wsChildrenFile, 'r') as chfh:
        for ln in chfh:
            wlst = ln[:-1].split()
            wsChildrenDic[wlst[0]] = wlst[1:]
        return wsChildrenDic


def fix(word, word2CircleDic, wsChildrenDic, word2BallDic):
    children = wsChildrenDic[word]
    if len(children) == 0:
        return
    for child in children:
        fix(child, word2CircleDic, wsChildrenDic, word2BallDic)
    if len(children) > 1:
        for child1, child2 in itertools.combinations(children, 2):
            if not is_circles_disjoint(word2CircleDic[child1], word2CircleDic[child2]) and \
                    is_circles_disjoint(word2BallDic[child1], word2BallDic[child2]):
                disjoint_circles_by_scaling_down(child1, child2, word2CircleDic, wsChildrenDic)
    if word == "*root*":
        return
    for child in children:
        contained = is_circle2_contains_circle1(word2CircleDic[child], word2CircleDic[word])
        if not contained:
            contain_circles(child, word, word2CircleDic, wsChildrenDic)


def check_one_level(word, word2CircleDic, wsChildrenDic, disjoint_failed={}, contained_failed={}):
    children = wsChildrenDic[word]
    disjoint_failed[word] = []
    contained_failed[word] = []
    if len(children) == 0:
        return
    for child in children:
        check_one_level(child, word2CircleDic, wsChildrenDic, disjoint_failed, contained_failed)
    if len(children) > 1:
        for child1, child2 in itertools.combinations(children, 2):
            is_disjoint = is_circles_disjoint(word2CircleDic[child1], word2CircleDic[child2])
            if not is_disjoint:
                disjoint_failed[word].append('{} {}'.format(child1, child2, word))
    if word != "*root*":
        for child in children:
            contained = is_circle2_contains_circle1(word2CircleDic[child], word2CircleDic[word])
            if not contained:
                contained_failed[word].append("{} {}".format(child, word))


def check_all_tree(word2CircleDic, wsChildrenDic, name="Tree"):
    disjoint_failed = {}
    contained_failed = {}
    check_one_level("*root*", word2CircleDic, wsChildrenDic, disjoint_failed, contained_failed)
    disjoint_failed = {k: v for k, v in disjoint_failed.items() if len(v) > 0}
    contained_failed = {k: v for k, v in contained_failed.items() if len(v) > 0}
    print("Checking {}".format(name))
    print("Disjoint Condition Failed",json.dumps(disjoint_failed, indent=4, sort_keys=True))
    print("Contained Condition Failed",json.dumps(contained_failed, indent=4, sort_keys=True))
    print("------------------------------------------------------------")


def do_all(balls_file_path, children_file_path):

    wsChildrenDic = {}
    word2BallDic = {}

    read_balls_file(balls_file_path, word2BallDic)
    read_chilren_file(children_file_path, wsChildrenDic)
    word2CircleDic = reduce_dimensions(word2BallDic)

    check_all_tree(word2BallDic, wsChildrenDic, "Balls")

    check_all_tree(word2CircleDic, wsChildrenDic, "2D circles before fixing")

    plot_dic(word2CircleDic, 'Before', word2CircleDic)

    fix("*root*", word2CircleDic, wsChildrenDic, word2BallDic)

    check_all_tree(word2CircleDic, wsChildrenDic, "2D circles after fixing")

    plot_dic(word2CircleDic, 'After', word2CircleDic)

    plt.show()
