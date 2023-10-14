# coding=utf-8
"""
Conduct experiments with R-BERT model with VinAI PhoBERT
We use the code base from: https://github.com/monologg/R-BERT
"""
import argparse

from phobert_rbert.data_loader import load_and_cache_examples
from phobert_rbert.trainer import Trainer
from phobert_rbert.utils import init_logger, load_tokenizer, set_seed


def main(args):
    init_logger()
    set_seed(args)
    tokenizer = load_tokenizer(args)

    train_dataset = load_and_cache_examples(args, args.train_data_file, tokenizer)
    test_dataset = load_and_cache_examples(args, args.eval_data_file, tokenizer)

    trainer = Trainer(args, tokenizer, train_dataset=train_dataset, test_dataset=test_dataset)

    if args.do_train:
        trainer.train()

    if args.do_eval:
        trainer.load_model()
        trainer.evaluate()
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--train_data_file", type=str, required=True,
                        help="The input training data file (a text file).")
    # Other parameters
    parser.add_argument(
        "--eval_data_file", required=True,
        type=str,
        help="Path to validation data (a text file).",
    )
    parser.add_argument(
        "--id2label", type=str, required=True,
        help="Path to id2label file"
    )
    
    parser.add_argument("--model_dir", type=str, default="./models", help="Path to save model checkpoints")
    parser.add_argument(
        "--model_name_or_path",
        type=str,
        default="vinai/phobert-base",
        help="Model name or path to BERT model",
    )
    parser.add_argument(
        "--overwrite_cache", action="store_true", help="Overwrite the cached training and evaluation sets"
    )
    parser.add_argument("--do_lower_case", action="store_true", help="Whether to lower case texts")
    parser.add_argument("--seed", type=int, default=77, help="random seed for initialization")
    parser.add_argument("--train_batch_size", default=16, type=int, help="Batch size for training.")
    parser.add_argument("--eval_batch_size", default=32, type=int, help="Batch size for evaluation.")
    parser.add_argument(
        "--max_seq_len",
        default=384,
        type=int,
        help="The maximum total input sequence length after tokenization.",
    )
    parser.add_argument(
        "--learning_rate",
        default=2e-5,
        type=float,
        help="The initial learning rate for Adam.",
    )
    parser.add_argument(
        "--num_train_epochs",
        default=10.0,
        type=float,
        help="Total number of training epochs to perform.",
    )
    parser.add_argument("--weight_decay", default=0.0, type=float, help="Weight decay if we apply some.")
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=1,
        help="Number of updates steps to accumulate before performing a backward/update pass.",
    )
    parser.add_argument("--adam_epsilon", default=1e-8, type=float, help="Epsilon for Adam optimizer.")
    parser.add_argument("--max_grad_norm", default=1.0, type=float, help="Max gradient norm.")
    parser.add_argument(
        "--max_steps",
        default=-1,
        type=int,
        help="If > 0: set total number of training steps to perform. Override num_train_epochs.",
    )
    parser.add_argument("--warmup_steps", default=0, type=int, help="Linear warmup over warmup_steps.")
    parser.add_argument(
        "--dropout_rate",
        default=0.1,
        type=float,
        help="Dropout for fully-connected layers",
    )
    
    parser.add_argument("--logging_steps", type=int, default=250, help="Log every X updates steps.")
    parser.add_argument(
        "--save_steps",
        type=int,
        default=250,
        help="Save checkpoint every X updates steps.",
    )
    
    parser.add_argument("--do_train", action="store_true", help="Whether to run training.")
    parser.add_argument("--do_eval", action="store_true", help="Whether to run eval on the test set.")
    parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")
    parser.add_argument(
        "--add_sep_token",
        action="store_true",
        help="Add [SEP] token at the end of the sentence",
    )
    
    args = parser.parse_args()
    
    main(args)
