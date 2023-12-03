# coding=utf-8
"""
Utility functions for data loading
"""
import numpy as np


class RelexSample:
    
    def __init__(self, sentence, e1_start, e1_end, e2_start, e2_end, e1_type, e2_type):
        self.sentence = sentence
        self.e1_start = e1_start
        self.e1_end = e1_end
        self.e2_start = e2_start
        self.e2_end = e2_end
        self.e1_type = e1_type
        self.e2_type = e2_type


def create_sequence_with_markers(sample, e1_start_token='[E1]', e1_end_token='[/E1]',
                                 e2_start_token='[E2]', e2_end_token='[/E2]'):
    """Create sample with entity markers
    """
    tokens = sample.sentence.split(' ')
    e1_start, e1_end = sample.e1_start, sample.e1_end
    e2_start, e2_end = sample.e2_start, sample.e2_end
    
    res = []
    positions = [e1_start, e1_end+1, e2_start, e2_end+1]
    symbols = [e1_start_token, e1_end_token, e2_start_token, e2_end_token]
    
    if e2_start == e1_end+1:
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
    
    if e1_end+1 == len(tokens):
        res.append(e1_end_token)
    if e2_end+1 == len(tokens):
        res.append(e2_end_token)
        
    return ' '.join(res)


def load_relex_samples(file_path, do_lower_case=False):
    """Loading list of RelexSample from data in SemEval 2010 format
    """
    samples = []
    labels = []
    with open(file_path, "r", encoding="utf-8") as fi:
        for line in fi:
            line = line.strip()
            if line == "":
                continue
            fields = line.split("\t")
            lb = int(fields[0])
            sentence = fields[7]
            if do_lower_case:
                sentence = sentence.lower()
            sample = RelexSample(sentence, int(fields[1]), int(fields[2]),
                                 int(fields[3]), int(fields[4]), fields[6], fields[6])
            samples.append(sample)
            labels.append(lb)
    return samples, labels


def load_relex_samples_for_test(file_path, do_lower_case=False):
    """Loading list of RelexSample from a datafile of SemEval 2010 format (test data)
    """
    samples = []
    labels = []
    default_label = 2
    with open(file_path, "r") as fi:
        for line in fi:
            line = line.strip()
            if line == "":
                continue
            fields = line.split("\t")
            e1_start = int(fields[3])
            e1_end = int(fields[4])
            e2_start = int(fields[5])
            e2_end = int(fields[6])
            e1_type = fields[7]
            e2_type = fields[8]
            sentence = fields[9]
            if do_lower_case:
                sentence = sentence.lower()
            sample = RelexSample(sentence, e1_start, e1_end, e2_start, e2_end, e1_type, e2_type)
            samples.append(sample)
            labels.append(default_label)
    return samples, labels
    

def load_id2label(file_path):
    """Load id2label from file id2label.txt
    """
    id2label = {}
    with open(file_path, 'r') as fi:
        for line in fi:
            line = line.strip()
            if line == "":
                continue
            i, lb = line.split("\t")
            id2label[int(i)] = lb
    return id2label
        

