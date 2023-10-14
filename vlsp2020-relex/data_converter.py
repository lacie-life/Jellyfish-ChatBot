# coding=utf-8
# Developed by Pham Quang Nhat Minh
"""
Data Conversion Utility Functions
"""
import os
import sys
import re
import json
import argparse
from collections import defaultdict
from vncorenlp import VnCoreNLP
annotator = VnCoreNLP(address="http://127.0.0.1", port=9000)


def text_normalize(text):
    """
    Chuẩn hóa dấu tiếng Việt
    """

    text = re.sub(r"òa", "oà", text)
    text = re.sub(r"óa", "oá", text)
    text = re.sub(r"ỏa", "oả", text)
    text = re.sub(r"õa", "oã", text)
    text = re.sub(r"ọa", "oạ", text)
    text = re.sub(r"òe", "oè", text)
    text = re.sub(r"óe", "oé", text)
    text = re.sub(r"ỏe", "oẻ", text)
    text = re.sub(r"õe", "oẽ", text)
    text = re.sub(r"ọe", "oẹ", text)
    text = re.sub(r"ùy", "uỳ", text)
    text = re.sub(r"úy", "uý", text)
    text = re.sub(r"ủy", "uỷ", text)
    text = re.sub(r"ũy", "uỹ", text)
    text = re.sub(r"ụy", "uỵ", text)
    text = re.sub(r"Ủy", "Uỷ", text)

    return text


def get_tag_name(tag):
    _tag = re.sub(r'B-', '', tag)
    _tag = re.sub(r'I-', '', _tag)
    return _tag


class Syllable(object):

    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end
        self.nerLabel = "O"
        self.nerType = "_"
        self.nerID = -1

    def set_sentence_idx(self, idx):
        self.sentence_idx = idx

    def set_index(self, idx):
        self.idx = idx
        
    def len(self):
        return self.end - self.start
    
    def set_nerLabel(self, nerLabel):
        self.nerLabel = nerLabel
        self.nerType = get_tag_name(self.nerLabel)
    
    def set_nerID(self, nerID):
        self.nerID = nerID

    def __repr__(self):
        return str((self.text, self.idx, self.start, self.end, self.nerID, self.nerLabel))
    
    def json_data(self):
        return {"index": self.idx, "form": self.text,
                "nerLabel": self.nerLabel, "start": self.start, "end": self.end,
                "nerID": self.nerID
                }


class Token(object):

    def __init__(self, _syllables):
        self.syllables = _syllables
        self.text = "_".join([s.text for s in _syllables])
        self.text2 = " ".join([s.text for s in _syllables])
        if len(self.syllables) > 0:
            self.start = self.syllables[0].start
            self.end = self.syllables[-1].end
        else:
            self.start = None
            self.end = None

    def set_syl_indexes(self, start_syl_id, end_syl_id):
        self.start_syl_id = start_syl_id
        self.end_syl_id = end_syl_id
        
    def set_sentence_idx(self, idx):
        self.sentence_idx = idx
    
    def set_index(self, idx):
        self.idx = idx

    def __repr__(self):
        return str( (self.text, self.idx, self.start_syl_id, self.end_syl_id, self.start, self.end))


class Sentence:
    """To represent VnCoreNLP sentence object"""
    
    def __init__(self, idx, tokens, syllables, token_dicts):
        self.idx = idx
        self.tokens = tokens
        self.syllables = syllables
        self.token_dicts = token_dicts
        self.relations = []
        
        for i,tok in enumerate(self.tokens):
            tok.set_sentence_idx(self.idx)
            tok.set_index(str(self.idx) + "-" + str(i))
        for i,syl in enumerate(self.syllables):
            syl.set_sentence_idx(self.idx)
            syl.set_index(str(self.idx) + "-" + str(i))
        
        self.text = " ".join([s.text for s in self.syllables])
    
    def add_relation(self, relation):
        self.relations.append(relation)
    
    def find_end_entity_id(self, start):
        start_syl = self.syllables[start]
        i = start+1
        while i < len(self.syllables) and re.search(r"^I-", self.syllables[i].nerLabel) and self.syllables[i].nerType == start_syl.nerType:
            i += 1
        
        end = i - 1
        return end
        
    def __repr__(self):
        return str({"id": self.idx,
                    "syllables": self.syllables,
                    "relations": self.relations
                    })
    
    def json_data(self):
        data = {}
        data["index"] = self.idx
        data["text"] = self.text
        data["tokens"] = [s.json_data() for s in self.syllables]
        data["relations"] = self.relations
        return data
    

def find_syl_index(text, start, end, syllables):
    """Find start and end indexes of syllables
    """
    start_syl_id = None
    end_syl_id = None
    for i, syl in enumerate(syllables):
        if syl.start == start:
            start_syl_id = i
        if syl.end == end:
            end_syl_id = i+1

        if i > 0 and syl.start >= start >= syllables[i - 1].end:
            start_syl_id = i
        if i == 0 and syl.start > start:
            start_syl_id = i

        if i < len(syllables)-1 and syl.end < end < syllables[i + 1].start:
            end_syl_id = i+1

        if syl.end >= end > syl.start:
            end_syl_id = i+1
        if i == len(syllables)-1 and syl.end <= end:
            end_syl_id = i+1

        if i > 0 and syl.start < start and syllables[i-1].end < start:
            start_syl_id = i

        if syl.start < start and syl.end >= end:
            start_syl_id = i
            end_syl_id = i + 1

        if i == 0 and len(syllables) > 0 and syl.start < start and syl.end < end:
            start_syl_id = i

    if start_syl_id is None:
        print(f"Cannot find start_syl_id: '{start}' (end={end}) '{text[start:end]}' in '{syllables}'", file=sys.stderr)
    if end_syl_id is None:
        print("Cannot find end_syl_id: '{}' (start={}) '{}' in '{}'".format(end, start, text[start:end], syllables), file=sys.stderr)

    return start_syl_id, end_syl_id


def find_tok_index(start_syl_id, end_syl_id, tokens):
    start_tok_id = None
    end_tok_id = None

    for i,tk in enumerate(tokens):
        if tk.start_syl_id == start_syl_id:
            start_tok_id = i
        if tk.end_syl_id == end_syl_id:
            end_tok_id = i+1
    return start_tok_id, end_tok_id


def create_syl_index(tokens):
    i = 0
    for tk in tokens:
        start_syl_id = i
        end_syl_id = i + len(tk.syllables)
        tk.set_syl_indexes(start_syl_id, end_syl_id)
        i = end_syl_id


def word_tokenize(words, raw_text, start_pos=0):
    tokens = []
    syllables = []
    
    _pos = start_pos
    for w in words:
        syls = []
        _syls = w.split("_")
        _syls = [s for s in _syls if s != ""]
        for s in _syls:
            start = raw_text.find(s, _pos)
            end = start + len(s)
            
            assert start != -1, f"'{w}' '{s}' pos={_pos} start={start}\t'{raw_text[_pos:]}'\t{raw_text}"
            # assert start - _pos < 3, f"'{w}' '{s}' pos={_pos} start={start}\t'{raw_text[_pos:]}'\t{raw_text}"
            _pos = end
        
            syl = Syllable(s, start, end)
            syls.append(syl)
            syllables.append(syl)
        token = Token(syls)
        tokens.append(token)
    create_syl_index(tokens)
    return tokens, syllables, _pos
    

def read_annotated_result(annotated_data, text):
    sentences = []
    # print(annotated_data["sentences"][-2])
    global_pos = 0
    for i,sen in enumerate(annotated_data["sentences"]):
        forms = [tok['form'] for tok in sen]
        tokens, syllables, global_pos = word_tokenize(forms, text, start_pos=global_pos)
        senobj = Sentence(i, tokens, syllables, sen)
        sentences.append(senobj)
    return sentences


def is_begin_of_chunk(i, tokens):
    """Check if the token in position i is the begin of an entity
    """
    assert i >= 0
    if tokens[i]['nerType'] == "O":
        return False
    if i == 0:
        return True
    if tokens[i]["nerID"] == 0:
        return True
    if tokens[i]["nerID"] != tokens[i-1]["nerID"]:
        return True
    return False


def is_begin_tag(tag):
    if re.search(r"^B-", tag):
        return True
    return False


def load_WebAnno_data(file_path):
    text = None
    tokens = []
    id2token = {}
    relations = []
    with open(file_path, 'r') as fi:
        for line in fi:
            line = line.rstrip()
            if line == "":
                continue
            text_match = re.search(r"#Text=(.+)$", line)
            if text_match:
                text = text_match.group(1)
            elif re.search(r"^1-\d+", line):
                fields = line.split("\t")
                start, end = fields[1].split("-")
                token = {"id": fields[0], "start": int(start), "end": int(end),
                         "form": fields[2], "nerType": "O", "nerID": -1}
                if len(fields) >= 4 and fields[4] not in ["*", "_"]:
                    m = re.search(r"^(LOCATION|ORGANIZATION|PERSON|MISCELLANEOUS)\[(\d+)\]", fields[4])
                    if m:
                        token["nerType"] = m.group(1)
                        token["nerID"] = int(m.group(2))
                    elif re.search(r"^(LOCATION|ORGANIZATION|PERSON|MISCELLANEOUS)$", fields[4]):
                        token["nerType"] = fields[4]
                        token["nerID"] = 0
                if len(fields) >= 6 and not re.search(r"^_$", fields[5]) and not re.search(r"^_$", fields[6]):
                    relation_types = fields[5].split("|")
                    e1_start_ids = fields[6].split("|")
                    
                    if len(relation_types) != len(e1_start_ids):
                        print("Length missmatched in %s" % file_path, file=sys.stderr)
                        
                    e2_start_id = fields[0]
                    e1_start_id = None
                    for rel_type, e1_start_str in zip(relation_types, e1_start_ids):
                        match_nerid = re.search(r"^(\d+-\d+(\.\d)*)\[(\d+)_(\d+)]$", e1_start_str)
                        if match_nerid:
                            e1_ner_id = match_nerid.group(2)
                            e2_ner_id = match_nerid.group(3)
                            e1_start_id = match_nerid.group(1)
                        elif re.search(r"^\d+-\d+(\.\d)*$", e1_start_str):
                            e1_ner_id = 0
                            e2_ner_id = token['nerID']
                            e1_start_id = e1_start_str
                        else:
                            print("Invalid e1_start_id: %s in %s" % (e1_start_str, file_path), file=sys.stderr)
                        
                        if e1_start_id is not None:
                            relations.append({"type": rel_type, "e1_start": e1_start_id, "e2_start": e2_start_id,
                                              "e1_ner_id": e1_ner_id, "e2_ner_id": e2_ner_id})
                tokens.append(token)
                id2token[fields[0]] = token
    if text is None:
        raise ValueError(
            "File {} does not have Text field".format(file_path)
        )
    text2 = " ".join([tk["form"] for tk in tokens])
    if text2 != text:
        print(f"{len(text.split(' '))} {len(text2.split(' '))} {file_path}\n'{text}'\n'{text2}'", file=sys.stderr)
    
    for i in range(len(tokens)):
        if tokens[i]['nerType'] != 'O':
            if is_begin_of_chunk(i, tokens):
                tokens[i]['nerLabel'] = "B-" + tokens[i]['nerType']
            else:
                tokens[i]['nerLabel'] = "I-" + tokens[i]['nerType']
        else:
            tokens[i]['nerLabel'] = "O"
    
    return text, tokens, id2token, relations


def is_all_punct(text):
    """Check if a text contains only punctuations
    """
    filters = frozenset([c for c in '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'])
    b = False
    _tk = [c for c in text if c not in filters]
    if len(_tk) == 0:
        b = True
    return b


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K


def comp_key(x, y):
    x_s_id, x_tok_id = x.split("-")
    y_s_id, y_tok_id = y.split("-")
    
    x_s_id = int(x_s_id)
    y_s_id = int(y_s_id)
    x_tok_id = int(x_tok_id)
    y_tok_id = int(y_tok_id)
    
    if x_s_id < y_s_id:
        return -1
    elif x_s_id > y_s_id:
        return 1
    else:
        return x_tok_id - y_tok_id
    

def convert_conll_to_json(input_file_path, output_file_path, cached_file, mapping_file,
                          wseg=False, overwrite_cache=False):
    text, anno_tokens, id2token, relations = load_WebAnno_data(input_file_path)
    text = text_normalize(text)
    if os.path.exists(cached_file) and not overwrite_cache:
        print("Loading parsing result from file %s" % cached_file)
        with open(cached_file, "r") as fi:
            annotated_data = json.load(fi)
    else:
        print("Parse text using VnCoreNLP from file %s" % input_file_path)
        
        annotated_data = annotator.annotate(text)
        with open(cached_file, "w") as fo:
            json.dump(annotated_data, fo, ensure_ascii=False, indent=2)

    sentences = read_annotated_result(annotated_data, text)
    # Get mapping from web_anno token id to syllable id in the sentence
    sylid2annoid = {}
    annoid2syl_indexes = defaultdict(list)
    
    print("# Number of sentences: ", len(sentences))

    for sen in sentences:
        # print(f"{sen.idx} - {len(sen.syllables)} syllables")
        for syl in sen.syllables:
            # if is_all_punct(syl.text):
            #     continue
            # print("Search syllable for: %s" % syl)
            found_tok = None
            for anno_tok in anno_tokens:
                if is_all_punct(syl.text) and anno_tok["start"] == syl.start:
                    continue
                if anno_tok["start"] == syl.start and anno_tok["end"] == syl.end:
                    found_tok = anno_tok
                    break
                if syl.start == anno_tok['start'] and syl.end < anno_tok["end"] and is_all_punct(anno_tok["form"][syl.end:]):
                    found_tok = anno_tok
                    break
                if syl.end == anno_tok['end'] and syl.start > anno_tok['start'] and is_all_punct(anno_tok['form'][0:syl.start]):
                    found_tok = anno_tok
                    break
                if is_all_punct(syl.text) and anno_tok['start'] < syl.start < syl.end < anno_tok['end']:
                    found_tok = anno_tok
                    break
                if not is_all_punct(syl.text) and anno_tok['start'] <= syl.start < syl.end <= anno_tok['end']:
                    found_tok = anno_tok
                    break
                    
            if found_tok is not None:
                sylid2annoid[syl.idx] = found_tok['id']
                annoid2syl_indexes[found_tok['id']].append(syl.idx)
            else:
                print("Could not find the mapping for %s in %s" % (syl, input_file_path), file=sys.stderr)
    
    for sen in sentences:
        for syl in sen.syllables:
            syl.set_nerLabel("O")
            if syl.idx in sylid2annoid:
                anno_id = sylid2annoid[syl.idx]
                tok = id2token[anno_id]
                syl.set_nerLabel(tok["nerLabel"])
                syl.set_nerID(tok['nerID'])
       
    s_rel_count = 0
    
    for r in relations:
        r_e1_start = r['e1_start']
        r_e2_start = r['e2_start']
        rel_type = r['type']
        if r_e1_start not in annoid2syl_indexes or r_e2_start not in annoid2syl_indexes:
            continue
            
        e1_candidates = annoid2syl_indexes[r_e1_start]
        e2_candidates = annoid2syl_indexes[r_e2_start]
        e1_candidates = sorted(e1_candidates)
        e2_candidates = sorted(e2_candidates)
        
        e1_start_id = e1_candidates[0]
        e2_start_id = e2_candidates[0]
        
        e1_s_id, e1_start_tok_id = e1_start_id.split("-")
        e2_s_id, e2_start_tok_id = e2_start_id.split("-")
        
        e1_s_id = int(e1_s_id)
        e2_s_id = int(e2_s_id)
        
        if e1_s_id != e2_s_id:
            print("%d # %d: %s in file: %s" % (e1_s_id, e2_s_id, r, input_file_path), file=sys.stderr)
            continue
        # assert e1_s_id == e2_s_id, "%s in file: %s" % (r, input_file_path)
        
        e1_start_tok_id = int(e1_start_tok_id)
        e2_start_tok_id = int(e2_start_tok_id)
        
        sen = sentences[e1_s_id]
        assert is_begin_tag(sen.syllables[e1_start_tok_id].nerLabel), f"{e1_start_tok_id}\t{sen.syllables[e1_start_tok_id].nerLabel},{sen.syllables[e1_start_tok_id]}\t{input_file_path}"
        assert is_begin_tag(sen.syllables[e2_start_tok_id].nerLabel), f"{e2_start_tok_id}\t{sen.syllables[e2_start_tok_id].nerLabel},{sen.syllables[e2_start_tok_id]}\t{input_file_path}"
        
        # Look for the last indexes of entities e1, e2
        e1_end_tok_id = sen.find_end_entity_id(e1_start_tok_id)
        e2_end_tok_id = sen.find_end_entity_id(e2_start_tok_id)
        
        text1 = " ".join([s.text for s in sen.syllables[e1_start_tok_id:e1_end_tok_id+1]])
        text2 = " ".join([s.text for s in sen.syllables[e2_start_tok_id:e2_end_tok_id + 1]])
        
        rel = {
            "type": rel_type,
            "e1_start": e1_start_tok_id,
            "e2_start": e2_start_tok_id,
            "e1_end": e1_end_tok_id,
            "e2_end": e2_end_tok_id,
            "e1_text": text1,
            "e2_text": text2,
        }
        
        sen.add_relation(rel)
        s_rel_count += 1
    
    # assert s_rel_count == len(relations), f"{s_rel_count} # {len(relations)}"
    
    # Write to output file
    data = []
    for sen in sentences:
        data.append(sen.json_data())
    with open(output_file_path, "w") as fo:
        json.dump({"sentences": data}, fo, ensure_ascii=False, indent=2)
    
    # Write mapping file
    with open(mapping_file, "w") as fo:
        for sylid in sorted(sylid2annoid.keys(), key=cmp_to_key(comp_key)):
            print(f"{sylid}\t{sylid2annoid[sylid]}", file=fo)
    return sentences
    

def main(args):
    """Convert data in conll format into json format
    
       We perform sentence, word segmentation, dependency parsed relations
       (with VnCoreNLP toolkit)
       
       The output is saved into JSON format
    """
    if (
            os.path.exists(args.output_dir)
            and os.listdir(args.output_dir)
            and not args.overwrite_output_dir
    ):
        raise ValueError(
            "Output directory ({}) already exists and is not empty. Use --overwrite_output_dir to overcome.".format(
                args.output_dir
            )
        )
    os.makedirs(args.output_dir, exist_ok=True)
    args.cache_dir = args.output_dir + "-cached"
    os.makedirs(args.cache_dir, exist_ok=True)
    
    subdirs = [d for d in os.listdir(args.input_dir) if os.path.isdir(os.path.join(args.input_dir, d))
               and re.search(r"\.(conll|txt)", d)]
    print("Number of sub-directories: {}".format(len(subdirs)))
    
    for subdir in subdirs:
        subdir_ = os.path.join(args.input_dir, subdir)
        output_subdir = os.path.join(args.output_dir, subdir)
        cached_subdir = os.path.join(args.cache_dir, subdir)
        os.makedirs(cached_subdir, exist_ok=True)
        
        os.makedirs(output_subdir, exist_ok=True)
        files = [f for f in os.listdir(subdir_) if re.search(r"\.tsv", f)]
        for file in files:
            file_path = os.path.join(subdir_, file)
            output_file_path = os.path.join(output_subdir, file + ".json")
            mapping_file = os.path.join(output_subdir, file + ".map.txt")
            cached_file = os.path.join(cached_subdir, file + ".json")
            convert_conll_to_json(file_path, output_file_path, cached_file, mapping_file,
                                  wseg=args.wseg,
                                  overwrite_cache=args.overwrite_cache)
                    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True,
                        help="Path to input directory")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Path to output directory"
                        )
    parser.add_argument("--overwrite_cache", action="store_true", help="Whether to overwrite the cached directory")
    parser.add_argument("--overwrite_output_dir", action="store_true", help="Whether to overwrite the output directory")
    parser.add_argument("--wseg", action="store_true", help="Whether to do sentence & word segmentation with VnCoreNLP")
    args = parser.parse_args()
    main(args)