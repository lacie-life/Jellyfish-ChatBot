# coding=utf-8
# Developed by Pham Quang Nhat Minh
"""
Basic data structure
"""
import os
import re
import json
import numpy as np


def is_all_punct(text):
    """Check if a text contains only punctuations
    """
    filters = [c for c in '“!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n\'’']
    filters.append(" ")
    filters.append(" ")
    filters = frozenset(filters)
    
    b = False
    _tk = [c for c in text if c not in filters]
    if len(_tk) == 0:
        b = True
    return b


possible_type_pairs = frozenset([
    # LOCATED
    ("PERSON", "LOCATION"),
    ("ORGANIZATION", "LOCATION"),
    # PART–WHOLE
    ("LOCATION", "LOCATION"),
    ("ORGANIZATION", "ORGANIZATION"),
    ("ORGANIZATION", "LOCATION"),
    # PERSONAL-SOCIAL
    ("PERSON", "PERSON"),
    # AFFILIATION
    ("PERSON", "ORGANIZATION"),
    ("PERSON", "LOCATION"),
    ("ORGANIZATION", "ORGANIZATION"),
    ("LOCATION", "ORGANIZATION")
])


def is_begin_tag(tag):
    if re.search(r"^B-", tag):
        return True
    return False


def get_tag_name(tag):
    _tag = re.sub(r'B-', '', tag)
    _tag = re.sub(r'I-', '', _tag)
    return _tag


class Token:
    
    def __init__(self, index, form, start, end, nerLabel, nerID):
        self.index = index
        self.form = form
        self.start = start
        self.end = end
        self.nerLabel = nerLabel
        self.nerID = nerID
        self.nerType = get_tag_name(self.nerLabel)
    
    def __repr__(self):
        return str((self.index, self.form, self.start, self.end, self.nerLabel, self.nerID))


class Entity:
    
    def __init__(self, text, start, end, nerType):
        self.text = text
        self.start = start
        self.end = end
        self.nerType = nerType
    
    def __repr__(self):
        return str((self.text, self.start, self.end, self.nerType))


class Sentence:
    
    def __init__(self, index, text, tokens, relations, dirname=None):
        self.index = index
        self.text = text
        self.tokens = tokens
        self.relations = relations
        self.relation_dict = {}
        self.dirname = dirname
    
    def get_entities(self):
        """Get the list of named entities in the sentence
        """
        entities = []
        
        i = 0
        while i < len(self.tokens):
            if is_begin_tag(self.tokens[i].nerLabel):
                start = i
                j = start + 1
                while j < len(self.tokens):
                    if re.search(r"^I-", self.tokens[j].nerLabel) and self.tokens[j].nerType == self.tokens[start].nerType:
                        j += 1
                    else:
                        break
                end = j - 1
                text = " ".join([tk.form for tk in self.tokens[start:end + 1]])
                entity = Entity(text, start, end, self.tokens[start].nerType)
                entities.append(entity)
                i = end + 1
            else:
                i += 1
        return entities


class Sample:
    
    def __init__(self, tokenized_sentence, e1, e2,
                 label='OTHER', dirname=None):
        self.tokenized_sentence = tokenized_sentence
        self.e1 = e1
        self.e2 = e2
        self.label = label
        self.dirname = dirname
    
    def key(self):
        return self.e1.start, self.e1.end, self.e2.start, self.e2.end
    
    def __repr__(self):
        return str(self.__dict__)
    

def load_data_from_file(file_path):
    """Load a list of sentences from a JSON file
    """
    dirname = file_path.split("/")[-2]
    sentences = []
    with open(file_path, "r") as fi:
        json_data = json.load(fi)
        for s in json_data["sentences"]:
            idx = s["index"]
            text = s["text"]
            tokens = []
            for tk in s["tokens"]:
                token = Token(**tk)
                tokens.append(token)
            sen = Sentence(idx, text, tokens, s['relations'], dirname)
            sentences.append(sen)
    return sentences


def load_data_from_dir(data_dir):
    """Loading data from a directory and return a list of sentences
    """
    print(f"Loading data from {data_dir}")
    sentences = []
    subdirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))
            and re.search(r"\.conll", d)]
    print(f"# Number of sub directories: {len(subdirs)}")
    for subdir in subdirs:
        subdir_ = os.path.join(data_dir, subdir)
        files = [f for f in os.listdir(subdir_) if re.search(r"\.json", f)]
        for file in files:
            file_path = os.path.join(subdir_, file)
            tmp_sentences = load_data_from_file(file_path)
            sentences.extend(tmp_sentences)
    return sentences


def create_samples_from_one_sentence(sentence, max_distance=100,
                                     use_posi_sen_only=False,
                                     is_train=False, keep_same_text=False):
    """Create samples from a single sentence
    """
    if use_posi_sen_only and len(sentence.relations) == 0:
        return []
    
    if is_train and len(sentence.relations) > 50:
        return []
    
    relation_dict = {}
    for rel in sentence.relations:
        if rel['type'] == 'PERSONAL - SOCIAL' and rel['e2_start'] < rel['e1_start']:
            relation_dict[(rel["e2_start"], rel["e2_end"], rel["e1_start"], rel["e1_end"])] = rel["type"]
        else:
            relation_dict[(rel["e1_start"], rel["e1_end"], rel["e2_start"], rel["e2_end"])] = rel["type"]
    
    samples = []
    entities = sentence.get_entities()
    added_dict = {}
    for i in range(len(entities)):
        e1 = entities[i]
        for j in range(len(entities)):
            e2 = entities[j]
            if j == i:
                continue
            if e1.text == e2.text and not keep_same_text:
                continue
            if e1.nerType == 'PERSON' and e2.nerType == 'PERSON' and e2.start < e1.start:
                continue
            if is_all_punct(e1.text) or is_all_punct(e2.text):
                continue

            sample = Sample(sentence.text, e1, e2, dirname=sentence.dirname)
            if sample.key() in relation_dict:
                label = relation_dict[sample.key()]
                sample.label = label
            
            if is_train:
                if (e1.nerType, e2.nerType) in possible_type_pairs and (sample.label != 'OTHER' or abs(e1.start - e2.start) <= max_distance) \
                        and sample.key() not in added_dict:
                    samples.append(sample)
                    added_dict[sample.key()] = 1
            else:
                if abs(e1.start - e2.start) > max_distance:
                    continue
                if (e1.nerType, e2.nerType) in possible_type_pairs and sample.key() not in added_dict:
                    samples.append(sample)
                    added_dict[sample.key()] = 1
                
    return samples


def create_samples_from_sentences(sentences, max_distance=100,
                                  use_posi_sen_only=False, has_label=True,
                                  is_train=False, keep_same_text=False):
    """Create samples from a list of sentences
    """
    samples = []
    for sen in sentences:
        tmp_samples = create_samples_from_one_sentence(sen, max_distance=max_distance,
                                                       use_posi_sen_only=use_posi_sen_only,
                                                       is_train=is_train, keep_same_text=keep_same_text)
        samples.extend(tmp_samples)
    return samples


def create_sequence_with_markers(sample, e1_start_token='[E1]', e1_end_token='[/E1]',
                                 e2_start_token='[E2]', e2_end_token='[/E2]'):
    """Create sample with entity markers
    """
    tokens = sample.tokenized_sentence.split(' ')
    e1_start, e1_end = sample.e1.start, sample.e1.end
    e2_start, e2_end = sample.e2.start, sample.e2.end

    res = []
    positions = [e1_start, e1_end + 1, e2_start, e2_end + 1]
    symbols = [e1_start_token, e1_end_token, e2_start_token, e2_end_token]

    if e2_start == e1_end + 1:
        indexes = [0, 1, 2, 3]
    elif e1_start == e2_end + 1:
        indexes = [2, 3, 0, 1]
    else:
        indexes = np.argsort(positions)

    for i in range(len(tokens)):
        for j in range(len(indexes)):
            if i == positions[indexes[j]]:
                res.append(symbols[indexes[j]])
        res.append(tokens[i])

    if e1_end + 1 == len(tokens):
        res.append(e1_end_token)
    if e2_end + 1 == len(tokens):
        res.append(e2_end_token)

    return ' '.join(res)
