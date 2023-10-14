# coding=utf-8
"""
Convert from JSON data into SemEval2020-Task 8 Format
"""
import os
import re
import argparse
import numpy as np
from collections import Counter

from relex.datastruct import load_data_from_dir, create_samples_from_sentences, create_sequence_with_markers

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True, type=str,
                        help="Path to input data directory (JSON files)")
    parser.add_argument("--output_dir", required=True, type=str)
    parser.add_argument("--max_distance", type=int, default=100,
                        help="Only consider entities whose distance is less than max_distance")
    parser.add_argument("--use_posi_sen_only", action="store_true",
                        help="Whether to use sentences with at least one relation")
    parser.add_argument("--keep_same_text", action="store_true",
                        help="Whether to keep entities with same texts")
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    print(args)
    
    filename = None
    match = re.search(r"VLSP2020_RE_(.+)/?$", args.input_dir.split("/").pop())
    if match:
        filename = match.group(1)
        if re.search(r"train", filename):
            filename = "train"
    else:
        raise ValueError("Invalid input directory name: %s" % args.input_dir)
    
    sentences = load_data_from_dir(args.input_dir)
    
    if filename == "train":
        is_train = True
    else:
        is_train = False
    
    if filename in ["train", "dev"]:
        has_label = True
    else:
        has_label = False
    
    samples = create_samples_from_sentences(sentences,
                                            max_distance=args.max_distance,
                                            use_posi_sen_only=args.use_posi_sen_only,
                                            is_train=is_train, has_label=has_label,
                                            keep_same_text=args.keep_same_text)
    labels = [s.label for s in samples]
    
    print(f"Number of samples: {len(samples)}")
    print("Label distribution:")
    print(Counter(labels))
    print()
    target_names = np.unique(labels).tolist()
    target_names = sorted(target_names)
    id2label = {}
    label2id = {}
    for i, lb in enumerate(target_names):
        id2label[i] = lb
        label2id[lb] = i
    
    # Write id2label
    if filename == "train":
        with open(os.path.join(args.output_dir, "id2label.txt"), "w") as fo:
            for i in sorted(id2label.keys()):
                print(f"{i}\t{id2label[i]}", file=fo)
    
    f1 = open(os.path.join(args.output_dir, filename + ".txt"), "w")
    f2 = open(os.path.join(args.output_dir, filename + "-readble.txt"), "w")
    for sample in samples:
        lb = sample.label
        print(f"{label2id[lb]}\t{sample.e1.start}\t{sample.e1.end}\t{sample.e2.start}\t"
              f"{sample.e2.end}\t{sample.e1.nerType}\t{sample.e2.nerType}\t{sample.tokenized_sentence}", file=f1)
        sen_with_marker = create_sequence_with_markers(sample)
        dirname = ""
        if sample.dirname is not None:
            dirname = sample.dirname
        print(f"{lb}\t{sample.e1.start}\t{sample.e1.end}\t{sample.e2.start}\t"
              f"{sample.e2.end}\t{sample.e1.nerType}\t{sample.e2.nerType}\t{sample.e1.text}\t{sample.e2.text}\t{dirname}\t{sen_with_marker}", file=f2)
    f1.close()