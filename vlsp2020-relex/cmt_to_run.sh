#!/bin/sh

python run_phobert_em.py --model_dir ./models/original_train_dev/phobert_em_es_base_maxlen_384_epochs_10_6 \
                         --train_data_file ./VLSP2020_RE_SemEvalFormat_6/train-phobert.txt \
                         --eval_data_file ./VLSP2020_RE_SemEvalFormat_6/dev-phobert.txt \
                         --id2label ./VLSP2020_RE_SemEvalFormat_6/id2label.txt \
                         --train_batch_size 4 --gradient_accumulation_steps 2 \
                         --save_steps 1000 --logging_steps 1000 \
                         --model_type es --do_train --do_eval