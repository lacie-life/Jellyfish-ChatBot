# coding=utf-8
"""
Classify samples into test data
Keep the order of samples
"""
import os
import argparse
import logging
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, SequentialSampler
from tqdm.auto import tqdm
from transformers import BertForSequenceClassification, BertConfig
import rbert
import bert_em
from rbert.model import RBERT
from rbert.utils import init_logger, load_tokenizer
from bert_em.model import BertEntityStarts, BertConcatAll

logger = logging.getLogger(__name__)


def predict(train_args, args, model, test_dataset, id2label, return_proba=False):
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
        batch = tuple(t.to(args.device) for t in batch)
        with torch.no_grad():
            if args.model_type == "rbert":
                inputs = {
                    "input_ids": batch[0],
                    "attention_mask": batch[1],
                    "token_type_ids": batch[2],
                    "labels": None,
                    "e1_mask": batch[4],
                    "e2_mask": batch[5],
                }
            elif args.model_type == "bert_em_cls":
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
    
    if return_proba:
        return preds, probas
    else:
        return preds
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_type", type=str, required=True,
                        choices=["rbert", "bert_em_cls", "bert_em_es", "bert_em_all"],
                        help="Model type")
    parser.add_argument("--model_dir", type=str, required=True, help="Path to model directory")
    parser.add_argument("--input_file", type=str, required=True, help="Path to input file")
    parser.add_argument("--output_file", type=str, required=True, help="Path to output file (to store predicted labels)")
    parser.add_argument("--eval_batch_size", type=int, default=32, help="Batch size for evaluation.")
    parser.add_argument("--no_cuda", action="store_true", help="Whether to use GPU for evaluation.")
    parser.add_argument("--overwrite_cache", action="store_true", help="Whether to overwrite cached feature file.")
    args = parser.parse_args()
    
    init_logger()
    logger.info("%s" % args)
    config = BertConfig.from_pretrained(args.model_dir)
    
    train_args = torch.load(os.path.join(args.model_dir, "training_args.bin"))
    logger.info("Training args: {}".format(train_args))
    train_args.eval_batch_size = args.eval_batch_size
    train_args.overwrite_cache = args.overwrite_cache
    
    # For BERT-EM, we have to use GPU because we fix device="cuda" in the code
    args.device = "cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu"

    # Check whether model exists
    if not os.path.exists(args.model_dir):
        raise Exception("Model doesn't exists! Train first!")

    # Load tokenizer
    tokenizer = load_tokenizer(train_args)
    
    if args.model_type == "rbert":
        model = RBERT.from_pretrained(args.model_dir, args=train_args)
    elif args.model_type == "bert_em_cls":
        model = BertForSequenceClassification.from_pretrained(args.model_dir, config=config)
    elif args.model_type == "bert_em_es":
        model = BertEntityStarts.from_pretrained(args.model_dir, config=config)
    else:
        model = BertConcatAll.from_pretrained(args.model_dir, config=config)
    
    model.to(args.device)
    logger.info("***** Model Loaded *****")
    
    if args.model_type == "rbert":
        test_dataset = rbert.data_loader.load_and_cache_examples(train_args, args.input_file, tokenizer, for_test=True)
    else:
        test_dataset = bert_em.data_loader.load_and_cache_examples(train_args, args.input_file, tokenizer, for_test=True)
    
    predictions = predict(train_args, args, model, test_dataset, config.id2label)
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

