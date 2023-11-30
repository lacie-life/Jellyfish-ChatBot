#!/usr/bin/env bash

export PYTHONPATH=.
python main.py train --task lvtn --run_test --data_dir ./datasets/lvtn --model_name_or_path vinai/phobert-base --model_arch softmax --output_dir outputs --max_seq_length 256 --train_batch_size 8 --eval_batch_size 8 --learning_rate 3e-5 --epochs 50 --early_stop 1000 --overwrite_data