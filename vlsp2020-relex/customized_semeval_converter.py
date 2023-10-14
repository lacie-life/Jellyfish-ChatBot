# coding=utf-8
"""
Customized SemEval Converter for test data
"""
import numpy as np
import re
import os
import argparse

from relex.datastruct import load_data_from_file, possible_type_pairs, is_all_punct, create_sequence_with_markers


class Sample:
    
    def __init__(self, sentence, e1, e2,
                 label='OTHER', dirname=None):
        self.sentence = sentence
        self.e1 = e1
        self.e2 = e2
        self.label = label
        self.dirname = dirname
    
    def key(self):
        return self.e1.start, self.e1.end, self.e2.start, self.e2.end
    
    def __repr__(self):
        return str(self.__dict__)
    
    
def create_samples_from_one_sentence(sentence, max_distance=100,
                                     keep_same_text=False):
    """Create samples from a single sentence
    """
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
            
            sample = Sample(sentence, e1, e2, dirname=sentence.dirname)
            if abs(e1.start - e2.start) > max_distance:
                continue
            if (e1.nerType, e2.nerType) in possible_type_pairs and sample.key() not in added_dict:
                samples.append(sample)
                added_dict[sample.key()] = 1
    
    return samples


def create_samples_from_sentences(sentences, max_distance=100,
                                  keep_same_text=False):
    """Create samples from a list of sentences
    """
    samples = []
    for sen in sentences:
        tmp_samples = create_samples_from_one_sentence(sen, max_distance=max_distance,
                                                       keep_same_text=keep_same_text)
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


def create_sequence_with_markers(sample, e1_start_token='[E1]', e1_end_token='[/E1]',
                                 e2_start_token='[E2]', e2_end_token='[/E2]'):
    """Create sample with entity markers
    """
    tokens = sample.sentence.text.split(' ')
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


def write_samples_to_file(fo, f1, samples, source_file):
    for sample in samples:
        sen_with_marker = create_sequence_with_markers(sample)
        e1_start_tok_id = sample.sentence.tokens[sample.e1.start].index
        e2_start_tok_id = sample.sentence.tokens[sample.e2.start].index
        print(f"{source_file}\t{e1_start_tok_id}\t{e2_start_tok_id}\t{sample.e1.start}\t{sample.e1.end}\t{sample.e2.start}\t"
              f"{sample.e2.end}\t{sample.e1.nerType}\t{sample.e2.nerType}\t{sample.sentence.text}", file=fo)
        print(
            f"{source_file}\t{e1_start_tok_id}\t{e2_start_tok_id}\t{sample.e1.start}\t{sample.e1.end}\t{sample.e2.start}\t"
            f"{sample.e2.end}\t{sample.e1.nerType}\t{sample.e2.nerType}\t{sample.e1.text}\t{sample.e2.text}\t"
            f"{sen_with_marker}", file=f1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True, help="Path to input directory that contains JSON files")
    parser.add_argument("--output_file", type=str, required=True, help="Path to output file")
    args = parser.parse_args()
    
    basename = os.path.splitext(args.output_file)[0]
    fo = open(args.output_file, "w")
    f1 = open(basename + "-readable.txt", "w")
    files_and_dirs = os.listdir(args.input_dir)
    for file_or_dir in files_and_dirs:
        input_path = os.path.join(args.input_dir, file_or_dir)
        if os.path.isfile(input_path) and re.search(r"\.json$", input_path):
            sentences = load_data_from_file(input_path)
            samples = create_samples_from_sentences(sentences)
            m = re.search(r"^(.+)\.json$", file_or_dir)
            source_file = m.group(1)
            write_samples_to_file(fo, f1, samples, source_file)
        elif os.path.isdir(input_path):
            files = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))
                     and re.search(r"\.json$", f)]
            for file in files:
                file_path = os.path.join(input_path, file)
                sentences = load_data_from_file(file_path)
                samples = create_samples_from_sentences(sentences)
                m = re.search(r"^(.+)\.json$", file)
                source_file = "{}/{}".format(file_or_dir, m.group(1))
                write_samples_to_file(fo, f1, samples, source_file)
    fo.close()
    f1.close()

