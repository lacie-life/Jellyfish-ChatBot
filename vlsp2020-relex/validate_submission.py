# coding=utf-8
"""
Validate submission results of VLSP2020-Relex
"""
import re
import os
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_dir", type=str, default="./data/VLSP2020_RE_test",
                        help="Path to test data directory.")
    parser.add_argument("submission_dir", type=str, help="Path to submission directory.")
    args = parser.parse_args()
    
    input_subdirs = [d for d in os.listdir(args.test_dir) if os.path.isdir(os.path.join(args.test_dir, d))
                     and not re.search(r"^\.+$", d)]
    output_subdirs = [d for d in os.listdir(args.submission_dir) if os.path.isdir(os.path.join(args.submission_dir, d))
                     and not re.search(r"^\.+$", d)]
    
    assert len(input_subdirs) == len(output_subdirs), "Number of sub-dirs: {}\t{}".format(len(input_subdirs), len(output_subdirs))
    assert set(input_subdirs) == set(output_subdirs)
    
    for subdir in input_subdirs:
        inp_subdir = os.path.join(args.submission_dir, subdir)
        out_subdir = os.path.join(args.submission_dir, subdir)
        
        inp_files = [f for f in os.listdir(inp_subdir) if os.path.isfile(os.path.join(inp_subdir, f))]
        out_files = [f for f in os.listdir(out_subdir) if os.path.isfile(os.path.join(out_subdir, f))]
        
        assert len(inp_files) == len(out_files)
        assert len(inp_files) == 1
        assert inp_files[0] == out_files[0]
        
        inp_file = os.path.join(inp_subdir, inp_files[0])
        out_file = os.path.join(out_subdir, out_files[0])
        
        with open(inp_file, "r") as fi:
            inp_lines = fi.readlines()
        with open(out_file, "r") as fi:
            out_lines = fi.readlines()
        
        assert len(inp_lines) == len(out_lines)
        
        for inp_line, out_line in zip(inp_lines, out_lines):
            inp_line = inp_line.strip()
            out_line = out_line.strip()
        
            if not re.search(r"^1-\d+", inp_line):
                assert inp_line == out_line, "{}\t{}\t{}".format(inp_file, inp_line, out_line)
                continue
            
            inp_fields = inp_line.split("\t")
            out_fields = out_line.split("\t")
            assert len(out_fields) == 7
            assert inp_fields[0] == out_fields[0]
            assert inp_fields[1] == out_fields[1]
            assert inp_fields[2] == out_fields[2]


