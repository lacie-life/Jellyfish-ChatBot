#!/bin/sh

python run_phobert_rbert.py --model_dir ./models/original_train_dev/phobert_rbert_base_maxlen_384_epochs_10 \
                            --train_data_file ./VLSP2020_RE_SemEvalFormat_3/train-phobert.txt \
                            --eval_data_file ./VLSP2020_RE_SemEvalFormat_3/dev-phobert.txt  \
                            --id2label ./VLSP2020_RE_SemEvalFormat_3/id2label.txt \
                            --train_batch_size 16 --gradient_accumulation_steps 2 \
                            --save_steps 1000 --logging_steps 1000 \
                            --do_train --do_eval