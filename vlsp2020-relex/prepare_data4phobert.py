"""Prepare data for PhoBERT
"""
import argparse
import os

import numpy as np
from pyvi import ViTokenizer

from relex.datautils import load_id2label


class Syllable(object):

    def __init__(self, text):
        self.text = text
        self.token_index = None

    def set_token_index(self, token_index):
        self.token_index = token_index


class Token(object):

    def __init__(self, form, _syllables):
        self.form = form
        self.syllables = _syllables

    def set_syl_indexes(self, start_syl_id, end_syl_id):
        # end syllable index is exclusive
        self.start_syl_id = start_syl_id
        self.end_syl_id = end_syl_id


def create_syl_index(tokens):
    i = 0
    for tk in tokens:
        start_syl_id = i
        end_syl_id = i + len(tk.syllables)
        tk.set_syl_indexes(start_syl_id, end_syl_id)
        i = end_syl_id


def word_tokenize(words):
    tokens = []
    syllables = []
    
    for i,w in enumerate(words):
        syls = []
        _syls = w.split("_")
        _syls = [s for s in _syls if s != ""]
        for s in _syls:
            syl = Syllable(s)
            syl.set_token_index(i)
            syls.append(syl)
            syllables.append(syl)
        token = Token(w, syls)
        tokens.append(token)
    create_syl_index(tokens)
    return tokens, syllables


class Sentence:
    
    def __init__(self, tokens, syllables):
        self.tokens = tokens
        self.syllables = syllables

    def word_segmented_text(self):
        return " ".join([w.form for w in self.tokens])
    
    def get_fixed_tokenized_text(self, e1_start, e1_end, e2_start, e2_end):
        """Split a token into smaller tokens if the there is overlapping
           between two entities or an entity is inside a token
        """
        return ""        


    @staticmethod
    def from_vncorenlp_sentence(json_data):
        forms = [tok['form'] for tok in json_data]
        tokens, syllables = word_tokenize(forms)
        senobj = Sentence(tokens, syllables)
        return senobj
    
    @staticmethod
    def from_pyvi_sentence(tokenized_text):
        forms = tokenized_text.split(" ")
        tokens, syllables = word_tokenize(forms)
        senobj = Sentence(tokens, syllables)
        return senobj


def create_sequence_with_markers(tokens, e1_start, e1_end, e2_start, e2_end,
                                 e1_start_token='[E1]', e1_end_token='[/E1]',
                                 e2_start_token='[E2]', e2_end_token='[/E2]'):
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

def merge_entities(e1_tok_start, e1_tok_end, e2_tok_start, e2_tok_end):
    if e1_tok_end == e2_tok_start:
        e1_tok_end += 1
    else:
        e1_tok_end += (e2_tok_start - e1_tok_end)
      

def convert_to_phobert(line, id2label):
    lb, e1_start, e1_end, e2_start, e2_end, e1_type, e2_type, text = line.split("\t")
    e1_start = int(e1_start)
    e1_end = int(e1_end)
    e2_start = int(e2_start)
    e2_end = int(e2_end)
    
    # Remove comments to debug
    # print("Input:", e1_start, e1_end, e2_start, e2_end, text)

    tokenized_text = ViTokenizer.tokenize(text, sylabelize=False)
    tokenized_text = ViTokenizer.tokenize(text, sylabelize=False)
    sen = Sentence.from_pyvi_sentence(tokenized_text)

    e1_tok_start = sen.syllables[e1_start].token_index
    e1_tok_end = sen.syllables[e1_end].token_index
    e2_tok_start = sen.syllables[e2_start].token_index
    e2_tok_end = sen.syllables[e2_end].token_index

    # Check if two entity is overlapping
    new_text = sen.word_segmented_text()

    # Fix word segmentation errors for two entities

    words = new_text.split(" ")
    text_with_markers = create_sequence_with_markers(words, e1_tok_start, e1_tok_end, e2_tok_start, e2_tok_end)
    new_line = "\t".join([lb, str(e1_tok_start), str(e1_tok_end), 
                          str(e2_tok_start), str(e2_tok_end), e1_type, e2_type, new_text])
    
    # print(e1_tok_start, e1_tok_end, e2_tok_start, e2_tok_end)
    
    if(e1_tok_start == e2_tok_start and e1_tok_end == e2_tok_end):
        pass

    if(e1_tok_start == e2_tok_start and e1_tok_end < e2_tok_end):
        pass

    if(e1_tok_end == e2_tok_start and e1_tok_start < e2_tok_start):
        e1_tok_end = e1_tok_end - 1

    if (e1_tok_end == e2_tok_end):
        if(e1_start < e2_start):
            e1_tok_end = e1_tok_end - 1
        else:
            e2_tok_end = e2_tok_end - 1

    # print(e1_tok_start, e1_tok_end, e2_tok_start, e2_tok_end) 

    e1_text = " ".join(words[e1_tok_start:e1_tok_end+1])
    e2_text = " ".join(words[e2_tok_start:e2_tok_end+1])

    line_with_markers = "\t".join([id2label[int(lb)], str(e1_tok_start), str(e1_tok_end), str(e2_tok_start), str(e2_tok_end), e1_type, e2_type, e1_text, e2_text, text_with_markers])
    new_line = "\t".join([lb, str(e1_tok_start), str(e1_tok_end), 
                          str(e2_tok_start), str(e2_tok_end), e1_type, e2_type, new_text])
    return new_line, line_with_markers


def main(args):
    id2label = load_id2label(args.id2label)
    basename = os.path.splitext(args.input_file)[0]
    output_file = os.path.join(basename + "-phobert.txt")
    output_file_readble = os.path.join(basename + "-phobert-readable.txt")
    fo = open(output_file, "w", encoding="utf-8")
    fo_readble = open(output_file_readble, "w", encoding="utf-8")
    with open(args.input_file, "r") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            phobert_line, line_with_markers = convert_to_phobert(line, id2label)
            print(phobert_line, file=fo)
            print(line_with_markers, file=fo_readble)
    fo.close()
    fo_readble.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True,
                        help="Path to input data file (txt)")
    parser.add_argument("--id2label", type=str, required=True, help="Path to id2label file")
    args = parser.parse_args()
    main(args)

