# (C) Developed by Pham Quang Nhat Minh
"""
Ensemble two models to make predictions
"""
import argparse
import logging
import os

import numpy as np
import torch
import torch.nn.functional as F
from sklearn import metrics
from torch.utils.data import DataLoader, SequentialSampler
from tqdm.auto import tqdm
from transformers import RobertaConfig, RobertaForSequenceClassification

import phobert_em.data_loader as emloader
import phobert_rbert.data_loader as rloader
from phobert_em.model import RobertaConcatAll, RobertaEntityStarts
from phobert_rbert.model import RBERT
from phobert_rbert.utils import init_logger, load_tokenizer

logger = logging.getLogger(__name__)

device = "cuda" if torch.cuda.is_available()  else "cpu"


def load_model(model_type, model_dir, train_args):
    config = RobertaConfig.from_pretrained(model_dir)
    if model_type == "rbert":
        model = RBERT.from_pretrained(model_dir, args=train_args)
    elif model_type == "bert_em_cls":
        model = RobertaForSequenceClassification.from_pretrained(model_dir, config=config)
    elif model_type == "bert_em_es":
        model = RobertaEntityStarts.from_pretrained(model_dir, config=config)
    else:
        model = RobertaConcatAll.from_pretrained(model_dir, config=config)
    return model


def predict(train_args, model_type, model, test_dataset, id2label):
    """Return the list of predicted labels by RBERT for test_dataset
    """
    eval_sampler = SequentialSampler(test_dataset)
    eval_dataloader = DataLoader(test_dataset, sampler=eval_sampler, batch_size=train_args.eval_batch_size)
    
    preds = None
    probas = None

    # for batch in tqdm(eval_dataloader, desc="Evaluating"):
    for batch in eval_dataloader:
        batch = tuple(t.to(device) for t in batch)
        with torch.no_grad():
            if model_type == "rbert":
                inputs = {
                    "input_ids": batch[0],
                    "attention_mask": batch[1],
                    "token_type_ids": batch[2],
                    "labels": None,
                    "e1_mask": batch[4],
                    "e2_mask": batch[5],
                }
            elif model_type == "bert_em_cls":
                inputs = {
                    "input_ids": batch[0],
                    "attention_mask": batch[1],
                    "token_type_ids": batch[2],
                    "labels": None,
                }
            else:
                inputs = {
                    "input_ids": batch[0],
                    "attention_mask": batch[1],
                    "token_type_ids": batch[2],
                    "labels": None,
                    "e1_ids": batch[4],
                    "e2_ids": batch[5],
                }
            outputs = model(**inputs)
            logits = outputs[0]
        
        proba = F.softmax(logits, dim=1)
        if preds is None:
            preds = logits.detach().cpu().numpy()
            probas = proba.detach().cpu().numpy()
        else:
            preds = np.append(preds, logits.detach().cpu().numpy(), axis=0)
            probas = np.append(probas, proba.detach().cpu().numpy(), axis=0)
    
    preds = np.argmax(preds, axis=1)
    preds = [id2label[i] for i in preds]

    return preds, probas

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, help="Path to input file")
    parser.add_argument("--eval_batch_size", type=int, default=32, help="Batch size for evaluation.")
    parser.add_argument("--overwrite_cache", action="store_true", help="Whether to overwrite cached feature file.")
    args = parser.parse_args()

    print("Running RE Process...")

    models = [
        {
            "model_type": "rbert",
            "model_dir": "./original_train_dev/phobert_rbert_base_maxlen_384_epochs_1000"
        },
        {
            "model_type": "bert_em_es",
            "model_dir": "./original_train_dev/phobert_em_es_base_maxlen_384_epochs_10"
        },
    ]
    weights = [0.5, 0.5]

    config = RobertaConfig.from_pretrained(models[0]["model_dir"])
    id2label = config.id2label
    
    list_probas = []
    for md in models:
        model_type = md["model_type"]
        model_dir = md["model_dir"]
        train_args = torch.load(os.path.join(model_dir, "training_args.bin"))
        train_args.eval_batch_size = args.eval_batch_size
        train_args.overwrite_cache = True
        
        tokenizer = load_tokenizer(train_args)
        model = load_model(model_type, model_dir, train_args)
        model.to(device)

        if model_type == "rbert":
            test_dataset = rloader.load_and_cache_examples(train_args, args.input_file, tokenizer,
                                                                             for_test=False)
        else:
            test_dataset = emloader.load_and_cache_examples(train_args, args.input_file, tokenizer,
                                                                          for_test=False)
        _, probas = predict(train_args, model_type, model, test_dataset, id2label)
        
        list_probas.append(probas)
    
    weighted_probas = []
    for w, probas in zip(weights, list_probas):
        weighted_probas.append(probas * w)
    
    weighted_probas = np.asarray(weighted_probas)
    
    ensemble_probas = weighted_probas.sum(axis=0)
    predictions = np.argmax(ensemble_probas, axis=1)
    predictions = [id2label[i] for i in predictions]

    f1 = open("./output.txt", "w", encoding="utf-8")
    with open(args.input_file, "r", encoding="utf-8") as fi:
        for i, line in enumerate(fi):
            line = line.strip()
            if line == "":
                continue
            fields = line.split("\t")

            print(f"{predictions[i]}\t{int(fields[1])}\t{int(fields[2])}\t{int(fields[3])}\t{int(fields[4])}\t{fields[5]}\t{fields[6]}\t{fields[7]}", file=f1)

    print(predictions)

