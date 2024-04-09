from vphoberttagger.arguments import get_predict_argument
from vphoberttagger.constant import LABEL_MAPPING, MODEL_MAPPING
from vphoberttagger.helper import normalize_text, _get_tags
from vncorenlp import VnCoreNLP

from typing import Union
from transformers import AutoConfig, AutoTokenizer

import os
import torch
import itertools
import numpy as np

import argparse
import logging

import torch.nn.functional as F
from sklearn import metrics
from torch.utils.data import DataLoader, SequentialSampler
from tqdm.auto import tqdm
from transformers import RobertaConfig, RobertaForSequenceClassification

# import run_ensemble_phobert
import subprocess


class ViTagger(object):
    def __init__(self, model_path: Union[str or os.PathLike],  no_cuda=False):
        self.device = 'cuda' if not no_cuda and torch.cuda.is_available() else 'cpu'
        print("[ViTagger] VnCoreNLP loading ...")
        self.rdrsegmenter = VnCoreNLP("./vphoberttagger/vncorenlp/VnCoreNLP-1.2.jar", annotators="wseg", max_heap_size='-Xmx2g')
        print("[ViTagger] Model loading ...")
        self.model, self.tokenizer,  self.max_seq_len, self.label2id, self.use_crf = self.load_model(model_path, device=self.device)
        self.id2label = {idx: label for idx, label in enumerate(self.label2id)}
        print("[ViTagger] All ready!")

    @staticmethod
    def load_model(model_path: Union[str or os.PathLike],  device='cpu'):
        if device == 'cpu':
            checkpoint_data = torch.load(model_path, map_location='cpu')
        else:
            checkpoint_data = torch.load(model_path)
        args = checkpoint_data["args"]
        max_seq_len = args.max_seq_length
        use_crf = True if 'crf' in args.model_arch else False
        tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=False)
        config = AutoConfig.from_pretrained(args.model_name_or_path, num_labels=len(args.label2id))
        model_clss = MODEL_MAPPING[args.model_name_or_path][args.model_arch]
        model = model_clss(config=config)
        model.load_state_dict(checkpoint_data['model'])
        model.to(device)
        model.eval()

        return model, tokenizer, max_seq_len, args.label2id, use_crf

    def preprocess(self, in_raw: str):
        # print("1")
        norm_text = normalize_text(in_raw)
        sents = []
        sentences = self.rdrsegmenter.tokenize(norm_text)
        for sentence in sentences:
            sents.append(sentence)
        return sents

    def convert_tensor(self, tokens):
        seq_len = len(tokens)
        encoding = self.tokenizer(tokens,
                                  padding='max_length',
                                  truncation=True,
                                  is_split_into_words=True,
                                  max_length=self.max_seq_len)
        if 'vinai/phobert' in self.tokenizer.name_or_path:
            subwords = self.tokenizer.tokenize(' '.join(tokens))
            valid_ids = np.zeros(len(encoding.input_ids), dtype=int)
            label_marks = np.zeros(len(encoding.input_ids), dtype=int)
            i = 1
            for idx, subword in enumerate(subwords[:self.max_seq_len - 2]):
                if idx != 0 and subwords[idx - 1].endswith("@@"):
                    continue
                if self.use_crf:
                    valid_ids[i - 1] = idx + 1
                else:
                    valid_ids[idx + 1] = 1
                i += 1
        else:
            valid_ids = np.zeros(len(encoding.input_ids), dtype=int)
            label_marks = np.zeros(len(encoding.input_ids), dtype=int)
            i = 1
            word_ids = encoding.word_ids()
            for idx in range(1, len(word_ids)):
                if word_ids[idx] is not None and word_ids[idx] != word_ids[idx - 1]:
                    if self.use_crf:
                        valid_ids[i - 1] = idx
                    else:
                        valid_ids[idx] = 1
                    i += 1
        if self.max_seq_len >= seq_len + 2:
            label_marks[:seq_len] = [1] * seq_len
        else:
            label_marks[:-2] = [1] * (self.max_seq_len - 2)
        if self.use_crf and label_marks[0] == 0:
            raise f"{tokens} have mark == 0 at index 0!"
        item = {key: torch.as_tensor([val]).to(self.device, dtype=torch.long) for key, val in encoding.items()}
        item['valid_ids'] = torch.as_tensor([valid_ids]).to(self.device, dtype=torch.long)
        item['label_masks'] = torch.as_tensor([valid_ids]).to(self.device, dtype=torch.long)
        return item

    def extract_entity_doc(self, in_raw: str):
        # print("1")
        sents = self.preprocess(in_raw)
        entities_doc = []
        for sent in sents:
            item = self.convert_tensor(sent)
            with torch.no_grad():
                outputs = self.model(**item)
            entity = None
            if isinstance(outputs.tags[0], list):
                tags = list(itertools.chain(*outputs.tags))
            else:
                tags = outputs.tags
            for w, l in list(zip(sent, tags)):
                w = w.replace("_", " ")
                tag = self.id2label[l]
                if not tag == 'O':
                    prefix, tag = tag.split('-')
                    if entity is None:
                        entity = (w, tag)
                    else:
                        if entity[-1] == tag:
                            if prefix == 'I':
                                entity = (entity[0] + f' {w}', tag)
                            else:
                                entities_doc.append(entity)
                                entity = (w, tag)
                        else:
                            entities_doc.append(entity)
                            entity = (w, tag)
                elif entity is not None:
                    entities_doc.append(entity)
                    entities_doc.append((w, 'O'))
                    entity = None
                else:
                    entities_doc.append((w, 'O'))
                    entity = None
        return entities_doc

    def __call__(self, in_raw: str, path: str):
        f1 = open(path, "w", encoding="utf-8")
        # print("1")
        sents = self.preprocess(in_raw)
        entites = []
        isRunRE = False
        for sent in sents:
            e_tag=[]
            item = self.convert_tensor(sent)
            with torch.no_grad():
                outputs = self.model(**item)
            entity = None
            if isinstance(outputs.tags[0], list):
                tags = list(itertools.chain(*outputs.tags))
            else:
                tags = outputs.tags
            for l in tags:
                e_tag.append(self.id2label[l])

            # print(e_tag)

            e_tags = []
            curr_tag = {'type': None, 'start_idx': None,
                        'end_idx': None, 'entity': None}
            i=0
            for w, l in list(zip(sent, tags)):
                w = w.replace("_", " ")
                tag = self.id2label[l]
                
                if not tag == 'O':
                    prefix, tag = tag.split('-')
                    # print("1",entity)
                    if entity is None:
                        entity = (w, tag)
                        curr_tag['start_idx'] = i
                        # print("2",entity,i)
                    else:
                        # print("3",entity)
                        if entity[-1] == tag:
                            if prefix == 'I':
                                entity = (entity[0] + f' {w}', tag)
                            else:
                                entites.append(entity)
                                entity = (w, tag)
                        else:
                            entites.append(entity)
                            entity = (w, tag)
                elif entity is not None:
                    # print("4",entity,i)
                    entites.append(entity)
                    curr_tag['end_idx'] = i-1
                    curr_tag['type'] = entity[1]
                    curr_tag['entity'] = entity[0]
                    e_tags.append(tuple(curr_tag.values()))
                    entity = None
                else:
                    # print("5",entity)
                    entity = None
                i=i+1
            # print(e_tags)
            e_sent=' '.join(sent)
            # print(e_sent)
            RE_input = {'label': None, 'e1_start_idx': None, 'e1_end_idx': None,
                        'e2_start_idx': None, 'e2_end_idx': None,
                        'e1_type': None, 'e2_type': None, 'sent': None}
            NER_output = []
            for i in range(len(e_tags)):
                for j in range(len(e_tags)):
                    if j!=i:
                        RE_input['label'] = '0'
                        RE_input['e1_start_idx'] = e_tags[i][1]
                        RE_input['e1_end_idx'] = e_tags[i][2]
                        RE_input['e2_start_idx'] = e_tags[j][1]
                        RE_input['e2_end_idx'] = e_tags[j][2]
                        RE_input['e1_type'] = e_tags[i][0]
                        RE_input['e2_type'] = e_tags[j][0]
                        RE_input['sent'] = e_sent
                        NER_output.append(tuple(RE_input.values()))
                        print(f"{0}\t{e_tags[i][1]}\t{e_tags[i][2]}\t{e_tags[j][1]}\t{e_tags[j][2]}\t{e_tags[i][0]}\t{e_tags[j][0]}\t{e_sent}", file=f1)
            if len(entites) > 1:
                isRunRE = True
        return NER_output, isRunRE

def tagging():
    args = get_predict_argument()
    predictor = ViTagger(args.model_path, no_cuda=args.no_cuda)
    path_file = "RE_input.txt"
    # f1 = open(path_file, "w", encoding="utf-8")
    while True:
        in_raw = input('Enter text:')
        # input_RE = predictor(in_raw, f1)
        # print(predictor(in_raw, path_file))
        Ner_output, isRunRE = predictor(in_raw, path_file)
        print(Ner_output)
        if isRunRE:
            subprocess.run(["python", "run_ensemble_phobert.py", "--input_file", path_file])


if __name__ == "__main__":
    tagging()

