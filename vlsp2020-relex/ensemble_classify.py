# (C) Developed by Pham Quang Nhat Minh
"""
Ensemble two models to make predictions
"""
import os
import argparse
import logging
from tqdm.auto import tqdm
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, SequentialSampler
from transformers import BertForSequenceClassification, BertConfig
import rbert
import bert_em
from rbert.model import RBERT
from rbert.utils import init_logger, load_tokenizer
from bert_em.model import BertEntityStarts, BertConcatAll

logger = logging.getLogger(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"


def load_model(model_type, model_dir, train_args):
    config = BertConfig.from_pretrained(model_dir)
    if model_type == "rbert":
        model = RBERT.from_pretrained(model_dir, args=train_args)
    elif model_type == "bert_em_cls":
        model = BertForSequenceClassification.from_pretrained(model_dir, config=config)
    elif model_type == "bert_em_es":
        model = BertEntityStarts.from_pretrained(model_dir, config=config)
    else:
        model = BertConcatAll.from_pretrained(model_dir, config=config)
    return model


def predict(train_args, model_type, model, test_dataset, id2label):
    """Return the list of predicted labels by RBERT for test_dataset
    """
    eval_sampler = SequentialSampler(test_dataset)
    eval_dataloader = DataLoader(test_dataset, sampler=eval_sampler, batch_size=train_args.eval_batch_size)
    
    logger.info("***** Running prediction on test dataset *****")
    logger.info("  Num examples = %d", len(test_dataset))
    logger.info("  Batch size = %d", train_args.eval_batch_size)
    
    preds = None
    probas = None
    for batch in tqdm(eval_dataloader, desc="Evaluating"):
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
    parser.add_argument("--input_file", type=str, required=True, help="Path to input file")
    parser.add_argument("--output_file", type=str, required=True,
                        help="Path to output file (to store predicted labels)")
    parser.add_argument("--eval_batch_size", type=int, default=32, help="Batch size for evaluation.")
    parser.add_argument("--overwrite_cache", action="store_true", help="Whether to overwrite cached feature file.")
    args = parser.parse_args()

    init_logger()
    logger.info("%s" % args)

    models = [
        {
            "model_type": "rbert",
            "model_dir": "./models/all_data/rbert_bert4news_maxlen_384_epochs_10"
        },
        {
            "model_type": "bert_em_es",
            "model_dir": "./models/all_data/bert_em_es_bert4news_maxlen_384_epochs_10"
        },
    ]
    weights = [0.4, 0.6]

    config = BertConfig.from_pretrained(models[0]["model_dir"])
    id2label = config.id2label

    list_probas = []
    for md in models:
        model_type = md["model_type"]
        model_dir = md["model_dir"]
        train_args = torch.load(os.path.join(model_dir, "training_args.bin"))
        train_args.eval_batch_size = args.eval_batch_size
        train_args.overwrite_cache = args.overwrite_cache
    
        tokenizer = load_tokenizer(train_args)
        logger.info("Get predictions of {} from {}".format(model_type, model_dir))
        logger.info("Training args: {}".format(train_args))
        model = load_model(model_type, model_dir, train_args)
        model.to(device)
        logger.info("***** Model Loaded *****")
    
        if model_type == "rbert":
            test_dataset = rbert.data_loader.load_and_cache_examples(train_args, args.input_file, tokenizer,
                                                                     for_test=True)
        else:
            test_dataset = bert_em.data_loader.load_and_cache_examples(train_args, args.input_file, tokenizer,
                                                                       for_test=True)
        _, probas = predict(train_args, model_type, model, test_dataset, id2label)
    
        list_probas.append(probas)

    weighted_probas = []
    for w, probas in zip(weights, list_probas):
        weighted_probas.append(probas * w)

    weighted_probas = np.asarray(weighted_probas)
    logger.info("Weighted Probas: {}".format(weighted_probas.shape))

    ensemble_probas = weighted_probas.sum(axis=0)
    logger.info("Ensemble Probas: {}".format(ensemble_probas.shape))
    predictions = np.argmax(ensemble_probas, axis=1)
    predictions = [id2label[i] for i in predictions]

    # Write predictions to a file
    # Sanity check
    original_lines = []
    with open(args.input_file, 'r') as fi:
        for line in fi:
            line = line.strip()
            if line == "":
                continue
            original_lines.append(line)
    assert len(predictions) == len(original_lines), "Number of lines and predictions mismatched"

    with open(args.output_file, "w") as fo:
        for pred, line in zip(predictions, original_lines):
            print("{}\t{}".format(pred, line), file=fo)