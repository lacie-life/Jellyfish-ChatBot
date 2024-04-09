#!/usr/bin/env bash

export PYTHONPATH=.
python main.py train --task lvtn --run_test --data_dir ./datasets/lvtn2 --model_name_or_path vinai/phobert-base-v2 --model_arch softmax --output_dir outputs --max_seq_length 256 --train_batch_size 32 --eval_batch_size 32 --learning_rate 3e-5 --epochs 100 --early_stop 5 --overwrite_data