from collections import defaultdict
from nltk.corpus import wordnet as wn

input_examples_words_mapping = {
    'Cities': ['City','Berlin','London','Tokyo','Paris','Singapore','Amsterdam','Seoul'],
    'Fruits': ['Fruit','Orange','Banana'],
    'Small': ['church', 'kirk', 'cathedral'],
    'Medium': ['car','house','toy','fruit','banana'],
    'Large': ['Akee','Apple','Apricot','Kiwifruit','Kumquat','Lime','Loquat','Pineapple','Tayberry','Plumcot','Lychee','Damson','Cucumber','Cloudberry','Banana','Fig','Jambul','Mango','Orange','Clementine','Papaya','Peach','Salal','Satsuma'],
    'Large2' : ['City', 'Berlin', 'London', 'Tokyo', 'Paris', 'Singapore', 'Amsterdam', 'Seoul', 'Baku', 'Damascus', 'Djibouti', 'Gustavia', 'Havana', 'Helsinki', 'Nassau'],
    'Custom' : []
}


def generate_words_paths_file(words, file, glove_words_set=set()):
    output = ["*root* *root* "]
    words_paths = {}
    for word in words:
        if word.lower() not in glove_words_set:
            continue
        synsets = wn.synsets(word)
        for synset in synsets:
            generare_hypernym_path(synset, words_paths, glove_words_set)
    for value in words_paths.values():
        output.append(value + "\n")
    write_data_to_file(file, output)

def generate_child_file(paths_file, file):
    child_dic = {}
    with open(paths_file, 'r') as ifh:
        has_child = set()
        all_words = set()
        input_lines = ifh.readlines()
        for ln in input_lines:
            word = ln.strip().split()[0]
            child_dic[word] = set()
        for ln in input_lines:
            path_tokens = ln.strip().split()[1:]
            for i, token in enumerate(path_tokens):
                if i < len(path_tokens) - 1:
                    child_dic[path_tokens[i]].add(path_tokens[i + 1])
        output = []
        for key, value in child_dic.items():
            output_line = key + " "
            for value in list(value):
                output_line += value + " "
            output.append(output_line[:-1])
        write_data_to_file(file, output)

def write_data_to_file(file_path, lines):
    with open(file_path, 'w') as file:
        for line in lines:
            file.write(line)
            if not '\n' in line:
                file.write("\n")

def generate_path(synset, glove_words_set=set()):
    word_path = synset.name() + " *root* "
    hypernym_path_synsets = synset.hypernym_paths()[0]
    for hypernym_path_synset in hypernym_path_synsets:
        word = hypernym_path_synset.name()
        if "_" not in word and "-" not in word and word.split('.')[0] in glove_words_set:
            word_path += hypernym_path_synset.name() + " "
    return word_path

def generare_hypernym_path(synset, words_paths, glove_words_set=set()):
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

def generate_ws_cat_codes(cpathFile="", childrenFile="", outFile="", depth=0):
    wsPathDic, wsChildrenDic = defaultdict(), defaultdict()
    with open(cpathFile, 'r') as cfh:
        for ln in cfh.readlines():
            lst = ln[:-1].split()
            wsPathDic[lst[0]] = lst[1:]
    with open(childrenFile, 'r') as chfh:
        for ln in chfh.readlines():
            lst = ln.strip().split()
            if len(lst) == 0:
                continue
            if len(lst) == 1:
                wsChildrenDic[lst[0]] = []
            else:
                wsChildrenDic[lst[0]] = lst[1:]
    ofh = open(outFile, 'w')
    ml, nm = 0, ''
    for node, plst in wsPathDic.items():
        plst = plst[:-1]
        clst = ["1"]
        if ml < len(plst):
            ml = len(plst)
            nm = node
        for (parent, child) in zip(plst[:-1], plst[1:]):
            if parent in wsChildrenDic:
                children = wsChildrenDic[parent]
            if child in children:
                clst.append(str(children.index(child) + 1))
        clst += ['0'] * (depth - len(clst))
        line = " ".join([node] + clst) + "\n"
        ofh.write(line)
    ofh.close()
    return nm, ml

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

def generate_files(word2vec_file_path=None, input_file_path=None , sample=None, output_path=None):
    glove_words = read_word2vec_file(word2vec_file_path)
    words = None
    if sample is None:
        words = read_input_words(input_file_path)
    else:
        words = input_examples_words_mapping[sample]

    words_paths = output_path + '/small.wordSensePath.txt'
    generated_child_file = output_path + '/small.children.txt'
    cat_code = output_path + '/small.catcode.txt'

    generate_words_paths_file(words, words_paths, glove_words)
    generate_child_file(words_paths, generated_child_file)
    generate_ws_cat_codes(words_paths, generated_child_file, cat_code, depth=15)








