# coding=utf-8
"""
Generate submission files
"""
import logging
import re
import os
import argparse
from collections import defaultdict
from rbert.utils import init_logger


logger = logging.getLogger(__name__)


def load_map_files(json_dir):
    path2token_map = {}
    subdirs = [d for d in os.listdir(json_dir) if os.path.isdir(os.path.join(json_dir, d))
               and re.search(r"\.(conll|txt)", d)]
    for subdir in subdirs:
        subdir_path = os.path.join(json_dir, subdir)
        files = [f for f in os.listdir(subdir_path) if re.search(r"\.tsv\.map\.txt", f)]
        assert len(files) == 1
        input_file = os.path.join(subdir_path, files[0])
        token_map = {}
        with open(input_file, "r") as map_file:
            for line in map_file:
                line = line.strip()
                if line == "":
                    continue
                id1, id2 = line.split("\t")
                token_map[id1] = id2
        path2token_map[subdir] = token_map
    return path2token_map


def load_predictions(file_path):
    path2tuples = defaultdict(list)
    with open(file_path, "r") as fi:
        for line in fi:
            line = line.strip()
            if line == "":
                continue
            fields = line.split("\t")
            lb, _path, e1_id, e2_id = fields[:4]
            if lb == "OTHER":
                continue
            dirname = _path.split("/")[0]
            path2tuples[dirname].append((e1_id, e2_id, lb))
    return path2tuples


def get_NerId(file_path):
    tokenId2NerId = {}
    with open(file_path, 'r') as fi:
        for line in fi:
            line = line.rstrip()
            if not re.search(r"^1-\d+", line):
                continue
            fields = line.split("\t")
            tokID = fields[0]
            nerID = -1
            if len(fields) >= 4 and fields[4] not in ["*", "_"]:
                m = re.search(r"^(LOCATION|ORGANIZATION|PERSON|MISCELLANEOUS)\[(\d+)\]", fields[4])
                if m:
                    nerID = int(m.group(2))
                elif re.search(r"^(LOCATION|ORGANIZATION|PERSON|MISCELLANEOUS)$", fields[4]):
                    nerID = 0
            tokenId2NerId[tokID] = nerID
    return tokenId2NerId


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction_file", type=str, required=True, help="Path to prediction file.")
    parser.add_argument("--json_dir", type=str, required=True, help="Path to directory that contain JSON files.")
    parser.add_argument("--input_dir", type=str, required=True, help="Path to test input dir.")
    parser.add_argument("--output_dir", type=str, required=True, help="Path to output dir.")
    args = parser.parse_args()
    init_logger()
    
    logger.info(args)
    
    path2token_map = load_map_files(args.json_dir)
    
    path2tuples = load_predictions(args.prediction_file)
    # path2relex_res store the map between dirname/filename => relex_rs
    # relex_rs is the map from token_index a list of tuples
    # [(type, e1_index),...]
    path2relex_rs = {}
    for _path, tuples in path2tuples.items():
        assert _path in path2token_map, "{}".format(_path)
        token_map = path2token_map[_path]
        relex_rs = defaultdict(list)
        for e1, e2, label in tuples:
            assert e1 in token_map, "{}\t{}".format(e1, _path)
            assert e2 in token_map, "{}\t{}".format(e2, _path)
            e11_p = token_map[e1]
            e21_p = token_map[e2]
            relex_rs[e21_p].append((label, e11_p))
        path2relex_rs[_path] = relex_rs
    
    os.makedirs(args.output_dir, exist_ok=True)
    subdirs = [d for d in os.listdir(args.input_dir) if os.path.isdir(os.path.join(args.input_dir, d))
               and re.search(r"\.(conll|txt)", d)]
    logger.info("Number of sub-directories: {}".format(len(subdirs)))
    
    for subdir in subdirs:
        subdir_path = os.path.join(args.input_dir, subdir)
        output_subdir = os.path.join(args.output_dir, subdir)
        os.makedirs(output_subdir, exist_ok=True)
        
        files = [f for f in os.listdir(subdir_path) if re.search(r"\.tsv", f)]
        assert len(files) == 1
        filename = files[0]
        input_file = os.path.join(subdir_path, filename)
        output_file = os.path.join(output_subdir, filename)
        
        if subdir in path2relex_rs:
            relex_rs = path2relex_rs[subdir]
        else:
            relex_rs = {}
        
        # Get entity ids for each token index
        tokenId2NerId = get_NerId(input_file)
        
        # Write output
        fo = open(output_file, 'w')
        with open(input_file, 'r') as fi:
            for line in fi:
                line = line.rstrip()
                if not re.search(r"^1-\d+", line):
                    print(line, file=fo)
                    continue
                fields = line.split("\t")
                if len(fields) == 3:
                    # Process data unlabeled data file
                    fields.append("_")
                    fields.append("_")
                assert len(fields) >= 5, "{}\t{}".format(input_file, line)
                fields = fields[:5]
                token_index = fields[0]
                if token_index in relex_rs:
                    tuples = relex_rs[token_index]
                    types, e1_ids = zip(*tuples)
                    fields.append("|".join(types))
                    assert token_index in tokenId2NerId, "{}\t{}\t{}".format(input_file, token_index, line)
                    e2_nerID = tokenId2NerId[token_index]
                    assert e2_nerID != -1, "{}\t{}\t{}".format(input_file, token_index, line)
                    new_e1_ids = []
                    for e1_id in e1_ids:
                        assert e1_id in tokenId2NerId, "{}\t{}\t{}".format(input_file, e1_id, line)
                        e1_nerID = tokenId2NerId[e1_id]
                        assert e1_nerID != -1, "{}\t{}\t{}".format(input_file, e1_id, line)
                        if e1_nerID == 0 and e2_nerID == 0:
                            new_e1_ids.append(e1_id)
                        else:
                            new_e1_id = "{}[{}_{}]".format(e1_id, e1_nerID, e2_nerID)
                            new_e1_ids.append(new_e1_id)
                    fields.append("|".join(new_e1_ids))
                else:
                    fields.append("_")
                    fields.append("_")
                print("\t".join(fields), file=fo)
        fo.close()

