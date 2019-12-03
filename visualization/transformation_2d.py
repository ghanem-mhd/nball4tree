import itertools
import math
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from ploting import plot_dic
import json
import os

ALPHA = 0.000000000001


def reduce_dimensions(balls_dic):
    vectors = []
    words = []
    circles_dic = {}
    for word, values in balls_dic.items():
        words.append(word)
        vectors.append(np.multiply(values[:-2], values[-2]))
    reduced_vectors = PCA(2).fit_transform(vectors)
    for i, word in enumerate(words):
        vector, length = get_vector_and_length(reduced_vectors[i])
        circles_dic[word] = [vector[0], vector[1], length, balls_dic[word][-1]]
    return circles_dic


def get_coordinates_circle(circle):
    return np.multiply(circle[:-2], circle[-2])


def get_coordinates(word, circles_dic):
    return np.multiply(circles_dic[word][:-2], circles_dic[word][-2])


def get_vector_and_length(coordinates):
    magnitude = np.linalg.norm(coordinates)
    return [ele / magnitude for ele in coordinates], magnitude


def magic_scaling(word, circles_dic, children_dic, root, scale_factor):
    children = children_dic[word]
    circles_dic[word][-1] = abs(circles_dic[word][-1] * scale_factor)
    if word != root:
        word_center = get_coordinates(word, circles_dic)
        root_center = get_coordinates(root, circles_dic)
        delta = scale_factor * (word_center[0] - root_center[0]), scale_factor * (word_center[1] - root_center[1])
        new_center = root_center[0] + delta[0], root_center[1] + delta[1]
        new_vector, new_length = get_vector_and_length(new_center)
        circles_dic[word][: -2] = new_vector
        circles_dic[word][-2] = new_length
    if len(children) == 0:
        return
    for child in children:
        magic_scaling(child, circles_dic, children_dic, root, scale_factor)


def check_siblings(word1, word2, circles_dic, children_dic, parent, scale_factor):
    siblings_for_word1_and_word2 = children_dic[parent]
    for sibling in siblings_for_word1_and_word2:
        if sibling != word1 and sibling != word2:
            disjoint_with_word1 = disjoint_degree(circles_dic[word1], circles_dic[sibling])
            disjoint_with_word2 = disjoint_degree(circles_dic[word2], circles_dic[sibling])
            if disjoint_with_word1 < ALPHA or disjoint_with_word2 < ALPHA:
                magic_scaling(sibling, circles_dic, children_dic, sibling, scale_factor)


def disjoint_circles_by_scaling_down(word1, word2, circles_dic, children_dic, parent):
    old_radius1 = circles_dic[word1][-1]
    old_radius2 = circles_dic[word2][-1]
    dis = dis_between_circles_centers(circles_dic[word1], circles_dic[word2])
    dis = (dis - (dis * 0.01))
    scale_factor = dis / (old_radius1 + old_radius2)
    check_siblings(word1, word2, circles_dic, children_dic, parent, scale_factor)
    magic_scaling(word1, circles_dic, children_dic, word1, scale_factor)
    magic_scaling(word2, circles_dic, children_dic, word2, scale_factor)


def contain_circles(child, parent, circles_dic, children_dic):
    if circles_dic[child][-1] == 0:
        return
    dis = dis_between_circles_centers(circles_dic[child], circles_dic[parent])
    dis = (dis + (dis * 0.05))
    if is_circles_disjoint(circles_dic[child], circles_dic[parent]):
        scale_factor = (circles_dic[child][-1] + dis) / circles_dic[parent][-1]
        circles_dic[parent][-1] = abs(circles_dic[parent][-1] * scale_factor)
    else:
        scale_factor = (circles_dic[parent][-1] - dis) / circles_dic[child][-1]
        magic_scaling(child, circles_dic, children_dic, child, scale_factor)


def dis_between_circles_centers(circle1, circle2):
    if circle1 == circle2:
        return 0
    circle1_xy = get_coordinates_circle(circle1)
    circle2_xy = get_coordinates_circle(circle2)
    dis_sum = 0
    for i in range(len(circle1_xy)):
        dis_sum = dis_sum + pow(circle2_xy[i] - circle1_xy[i], 2)
    return math.sqrt(dis_sum)


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


def save_data(file_path, circles_dic):
    with open(file_path, 'w') as file:
        for word, values in circles_dic.items():
            file.write(word + " ")
            file.write(" ".join(str(value) for value in values))
            file.write("\n")


def read_balls_file(file_path, circles_dic=None):
    if circles_dic is None:
        circles_dic = dict()
    with open(file_path, mode="r", encoding="utf-8") as balls_file:
        for line in balls_file.readlines():
            tokens = line.strip().split()
            circles_dic[tokens[0]] = [float(ele) for ele in tokens[1:]]
        return circles_dic


def read_children_file(ws_children_file, children_dic=None):
    if children_dic is None:
        children_dic = dict()
    with open(ws_children_file, 'r') as children_file:
        for ln in children_file:
            tokens = ln[:-1].split()
            children_dic[tokens[0]] = tokens[1:]
        return children_dic


def fix(word, circles_dic, children_dic, balls_dic):
    children = children_dic[word]
    if len(children) == 0:
        return
    for child in children:
        fix(child, circles_dic, children_dic, balls_dic)
    if len(children) > 1:
        for child1, child2 in itertools.combinations(children, 2):
            if not is_circles_disjoint(circles_dic[child1], circles_dic[child2]) and \
                    is_circles_disjoint(balls_dic[child1], balls_dic[child2]):
                disjoint_circles_by_scaling_down(child1, child2, circles_dic, children_dic, word)
    if word == "*root*":
        return
    for child in children:
        if not is_circle2_contains_circle1(circles_dic[child], circles_dic[word]) and \
                is_circle2_contains_circle1(balls_dic[child1], balls_dic[word]):
            contain_circles(child, word, circles_dic, children_dic)


def check_one_level(word, circles_dic, children_dic, disjoint_failed=None, contained_failed=None):
    if contained_failed is None:
        contained_failed = {}
    if disjoint_failed is None:
        disjoint_failed = {}
    children = children_dic[word]
    disjoint_failed[word] = []
    contained_failed[word] = []
    if len(children) == 0:
        return
    for child in children:
        check_one_level(child, circles_dic, children_dic, disjoint_failed, contained_failed)
    if len(children) > 1:
        for child1, child2 in itertools.combinations(children, 2):
            is_disjoint = is_circles_disjoint(circles_dic[child1], circles_dic[child2])
            if not is_disjoint:
                disjoint_failed[word].append('{} {}'.format(child1, child2, word))
    if word != "*root*":
        for child in children:
            contained = is_circle2_contains_circle1(circles_dic[child], circles_dic[word])
            if not contained:
                contained_failed[word].append("{} {}".format(child, word))


def check_all_tree(circles_dic, children_dic, name="Tree"):
    disjoint_failed = {}
    contained_failed = {}
    check_one_level("*root*", circles_dic, children_dic, disjoint_failed, contained_failed)
    disjoint_failed = {k: v for k, v in disjoint_failed.items() if len(v) > 0}
    contained_failed = {k: v for k, v in contained_failed.items() if len(v) > 0}
    print("Checking {}".format(name))
    print("Disjoint Condition Failed Cases", json.dumps(disjoint_failed, indent=4, sort_keys=True))
    print("Contained Condition Failed Cases", json.dumps(contained_failed, indent=4, sort_keys=True))
    print("")


def reduce_and_fix(balls_file_path, children_file_path, output):
    output_file_path, output_file_ext = os.path.splitext(output)
    output_file_before = output_file_path + "_before" + output_file_ext
    output_file_after = output_file_path + "_after" + output_file_ext
    children_dic = {}
    balls_dic = {}
    read_balls_file(balls_file_path, balls_dic)
    read_children_file(children_file_path, children_dic)
    circles_dic = reduce_dimensions(balls_dic)
    print("\nBalls reduced to circles successfully\n")
    check_all_tree(balls_dic, children_dic, "N-Balls")
    check_all_tree(circles_dic, children_dic, "2D circles before fixing")
    save_data(output_file_before, circles_dic)
    fix("*root*", circles_dic, children_dic, balls_dic)
    check_all_tree(circles_dic, children_dic, "2D circles after fixing")
    save_data(output_file_after, circles_dic)

def read_words_to_show_file(file_path):
    words_to_show = []
    if file_path is None or file_path == "":
        return words_to_show
    with open(file_path, mode="r", encoding="utf-8") as filw:
        for line in filw.readlines():
            words_to_show.extend(line.strip().split(" "))
    return words_to_show


def visualize(circles_file_path, words_to_show_file_path):
    output_file_path, output_file_ext = os.path.splitext(circles_file_path)
    output_file_before = output_file_path + "_before" + output_file_ext
    output_file_after = output_file_path + "_after" + output_file_ext
    circles_dic_before = {}
    words_to_show = read_words_to_show_file(words_to_show_file_path)
    read_balls_file(output_file_before, circles_dic_before)
    plot_dic(circles_dic_before, 'Circles before fixing', words_to_show)
    circles_dic_after = {}
    read_balls_file(output_file_after, circles_dic_after)
    plot_dic(circles_dic_after, 'Circles after fixing', words_to_show)
    plt.show()


def check_embeddings(balls_file_path, children_file_path):
    balls_dic = {}
    children_dic = {}
    read_balls_file(balls_file_path, balls_dic)
    read_children_file(children_file_path, children_dic)
    check_all_tree(balls_dic, children_dic, "")
