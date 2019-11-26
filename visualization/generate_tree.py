from collections import defaultdict
from nltk.corpus import wordnet as wn

input_examples_words_mapping = {
    'Cities': ['City', 'Berlin', 'London', 'Tokyo', 'Paris', 'Singapore', 'Amsterdam', 'Seoul'],
    'Fruits': ['Fruit', 'Orange', 'Banana'],
    'Small': ['church', 'kirk', 'cathedral'],
    'Medium': ['car', 'house', 'toy', 'fruit', 'banana'],
    'Large': ['Akee', 'Apple', 'Apricot', 'Kiwifruit', 'Kumquat', 'Lime', 'Loquat', 'Pineapple', 'Tayberry', 'Plumcot',
              'Lychee', 'Damson', 'Cucumber', 'Cloudberry', 'Banana', 'Fig', 'Jambul', 'Mango', 'Orange', 'Clementine',
              'Papaya', 'Peach', 'Salal', 'Satsuma'],
    'Large2': ['City', 'Berlin', 'London', 'Tokyo', 'Paris', 'Singapore', 'Amsterdam', 'Seoul', 'Baku', 'Damascus',
               'Djibouti', 'Gustavia', 'Havana', 'Helsinki', 'Nassau'],
    'Custom': []
}


def print_words_paths_summery(words_paths):
    print('%s words paths found' % (len(words_paths)))


def print_children_summery(children):
    sub_tree_count = 0
    leaves_count = 0
    for line in children:
        tokens = line.split(" ")
        if len(tokens) > 1:
            sub_tree_count = sub_tree_count + 1
        else:
            leaves_count = leaves_count + 1
    print('%s Leaves found' % leaves_count)
    print('%s Subtree found' % (sub_tree_count - 1))


def generate_words_paths(words, glove_words_set):
    all_words_paths = ["*root* *root*\n"]
    word_paths = {}
    for word in words:
        if word.lower() not in glove_words_set:
            continue
        synsets = wn.synsets(word)
        for synset in synsets:
            generare_hypernym_path(synset, word_paths, glove_words_set)
    for value in word_paths.values():
        all_words_paths.append(value + "\n")
    return all_words_paths


def generate_path(synset, glove_words_set):
    word_path = synset.name() + " *root* "
    hypernym_path_synsets = synset.hypernym_paths()[0]
    for hypernym_path_synset in hypernym_path_synsets:
        word = hypernym_path_synset.name()
        if "_" not in word and "-" not in word and word.split('.')[0] in glove_words_set:
            word_path += hypernym_path_synset.name() + " "
    return word_path


def generare_hypernym_path(synset, words_paths, glove_words_set):
    if synset is None:
        return
    if "_" in synset.name() and "-" in synset.name():
        return
    if synset.name() in words_paths:
        return
    synset_path = generate_path(synset, glove_words_set)
    words_paths[synset.name()] = synset_path
    hypernym_path_synsets = synset.hypernym_paths()[0]
    for hypernym_path_synset in hypernym_path_synsets:
        word = hypernym_path_synset.name()
        if "_" not in word and "-" not in word and word.split('.')[0] in glove_words_set:
            generare_hypernym_path(hypernym_path_synset, words_paths, glove_words_set)


def generate_child(words_paths):
    child_dic = {}
    for word_path_line in words_paths:
        word = word_path_line.strip().split()[0]
        child_dic[word] = set()
    for word_path_line in words_paths:
        path_tokens = word_path_line.strip().split()[1:]
        for i, token in enumerate(path_tokens):
            if i < len(path_tokens) - 1:
                child_dic[path_tokens[i]].add(path_tokens[i + 1])
    output = []
    for key, child_item in child_dic.items():
        output_line = key + " "
        for value in list(child_item):
            output_line += value + " "
        output.append(output_line[:-1] + "\n")
    return output


def generate_ws_cat_codes(words_paths_file="", children_file="", outFile="", depth=0):
    words_paths_dic, children_dic = defaultdict(), defaultdict()
    with open(words_paths_file, 'r') as cfh:
        for ln in cfh.readlines():
            lst = ln[:-1].split()
            words_paths_dic[lst[0]] = lst[1:]
    with open(children_file, 'r') as chfh:
        for ln in chfh.readlines():
            lst = ln.strip().split()
            if len(lst) == 0:
                continue
            if len(lst) == 1:
                children_dic[lst[0]] = []
            else:
                children_dic[lst[0]] = lst[1:]
    ofh = open(outFile, 'w')
    ml, nm = 0, ''
    for node, parent_list in words_paths_dic.items():
        parent_list = parent_list[:-1]
        child_list = ["1"]
        if ml < len(parent_list):
            ml = len(parent_list)
            nm = node
        for (parent, child) in zip(parent_list[:-1], parent_list[1:]):
            if parent in children_dic:
                children = children_dic[parent]
            if child in children:
                child_list.append(str(children.index(child) + 1))
        child_list += ['0'] * (depth - len(child_list))
        line = " ".join([node] + child_list) + "\n"
        ofh.write(line)
    ofh.close()
    return nm, ml


def write_data_to_file(file_path, lines):
    with open(file_path, 'w') as file:
        for line in lines:
            file.write(line)
            if not '\n' in line:
                file.write("\n")


def read_word2vec_file(glove_file_path):
    glove_words_set = set()
    with open(glove_file_path, mode="r", encoding="utf-8") as file:
        for line in file:
            glove_words_set.add(line[:-1].split()[0])
    return glove_words_set


def read_input_words(input_file_path):
    words = []
    with open(input_file_path, mode="r", encoding="utf-8") as file:
        for line in file:
            words.extend([x.strip() for x in str(line).split(',')])
    return words


def generate_files(word2vec_file_path=None, input_file_path=None, sample=None, output_path=None):
    glove_words = read_word2vec_file(word2vec_file_path)
    if sample is None or sample == 'None':
        words = read_input_words(input_file_path)
    else:
        words = input_examples_words_mapping[sample]

    words_paths_file = output_path + '/small.wordSensePath.txt'
    generated_child_file = output_path + '/small.children.txt'
    cat_code = output_path + '/small.catcode.txt'

    words_paths = generate_words_paths(words, glove_words)
    if len(words_paths) <= 0:
        print('No words paths found! Try Again!')
    else:
        print_words_paths_summery(words_paths)
        children = generate_child(words_paths)
        print_children_summery(children)
        write_data_to_file(generated_child_file, children)
        write_data_to_file(words_paths_file, words_paths)
        generate_ws_cat_codes(words_paths_file, generated_child_file, cat_code, depth=15)
