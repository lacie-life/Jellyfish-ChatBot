# coding=utf-8
"""
Data Loading function for Roberta-EM
"""
import copy
import json
import logging
import os

import torch
from rbert.data_loader import create_examples_from_relex_samples
from relex.datautils import load_relex_samples, load_relex_samples_for_test
from torch.utils.data import TensorDataset

logger = logging.getLogger(__name__)


class InputFeatures(object):
    """
    A single set of features of data.

    Args:
        input_ids: Indices of input sequence tokens in the vocabulary.
        attention_mask: Mask to avoid performing attention on padding token indices.
            Mask values selected in ``[0, 1]``:
            Usually  ``1`` for tokens that are NOT MASKED, ``0`` for MASKED (padded) tokens.
        token_type_ids: Segment token indices to indicate first and second portions of the inputs.
    """
    
    def __init__(self, input_ids, attention_mask, token_type_ids, label_id,
                 e1_start_id, e2_start_id):
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        self.token_type_ids = token_type_ids
        self.label_id = label_id
        self.e1_start_id = e1_start_id
        self.e2_start_id = e2_start_id
    
    def __repr__(self):
        return str(self.to_json_string())
    
    def to_dict(self):
        """Serializes this instance to a Python dictionary."""
        output = copy.deepcopy(self.__dict__)
        return output
    
    def to_json_string(self):
        """Serializes this instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def convert_examples_to_features(
        examples,
        max_seq_len,
        tokenizer,
        cls_token="<s>",
        cls_token_segment_id=0,
        sep_token="</s>",
        pad_token=1,
        pad_token_segment_id=0,
        sequence_a_segment_id=0,
        add_sep_token=False,
        mask_padding_with_zero=True,
):
    features = []
    for (ex_index, example) in enumerate(examples):
        if ex_index % 5000 == 0:
            logger.info("Writing example %d of %d" % (ex_index, len(examples)))

        # Account for <s> and </s> with "- 2" and with "- 3" for RoBERTa.
        if add_sep_token:
            special_tokens_count = 2
        else:
            special_tokens_count = 1
            
        tokens_a = tokenizer.tokenize(example.text_a)
        
        e11_p = tokens_a.index("[E1]")  # the start position of entity1
        e12_p = tokens_a.index("[/E1]")  # the end position of entity1
        e21_p = tokens_a.index("[E2]")  # the start position of entity2
        e22_p = tokens_a.index("[/E2]")  # the end position of entity2
        
        if e12_p + 1 > max_seq_len or e22_p + 1 > max_seq_len:
            min_p = min(e11_p, e12_p, e21_p, e22_p)
            max_p = max(e11_p, e12_p, e21_p, e22_p)
            dist = max_p - min_p + 1
            window_size = int((max_seq_len - special_tokens_count - dist)/2)
            tokens_a = tokens_a[min_p-window_size+1:max_p+window_size]
            print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(e11_p,e12_p,e21_p,e22_p,min_p,max_p, window_size, example.text_a))
            print("{}\t{}".format(len(tokens_a)," ".join(tokens_a)))
            print()

            e11_p = tokens_a.index("[E1]")
            e12_p = tokens_a.index("[/E1]")
            e21_p = tokens_a.index("[E2]")
            e22_p = tokens_a.index("[/E2]")
            
        # Replace the token
        tokens_a[e11_p] = "$"
        tokens_a[e12_p] = "$"
        tokens_a[e21_p] = "#"
        tokens_a[e22_p] = "#"
        
        # Add 1 because of the <s> token
        e11_p += 1
        e12_p += 1
        e21_p += 1
        e22_p += 1

        if len(tokens_a) > max_seq_len - special_tokens_count:
            tokens_a = tokens_a[: (max_seq_len - special_tokens_count)]
        
        tokens = tokens_a
        if add_sep_token:
            tokens += [sep_token]
        
        token_type_ids = [sequence_a_segment_id] * len(tokens)
        
        tokens = [cls_token] + tokens
        token_type_ids = [cls_token_segment_id] + token_type_ids
        
        input_ids = tokenizer.convert_tokens_to_ids(tokens)
        
        # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
        attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)
        
        # Zero-pad up to the sequence length.
        padding_length = max_seq_len - len(input_ids)
        input_ids = input_ids + ([pad_token] * padding_length)
        attention_mask = attention_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
        token_type_ids = token_type_ids + ([pad_token_segment_id] * padding_length)
        
        assert len(input_ids) == max_seq_len, "Error with input length {} vs {}".format(len(input_ids), max_seq_len)
        assert len(attention_mask) == max_seq_len, "Error with attention mask length {} vs {}".format(
            len(attention_mask), max_seq_len
        )
        assert len(token_type_ids) == max_seq_len, "Error with token type length {} vs {}".format(
            len(token_type_ids), max_seq_len
        )
        
        label_id = int(example.label)
        
        if ex_index < 5:
            logger.info("*** Example ***")
            logger.info("tokens: %s" % " ".join([str(x) for x in tokens]))
            logger.info("input_ids: %s" % " ".join([str(x) for x in input_ids]))
            logger.info("attention_mask: %s" % " ".join([str(x) for x in attention_mask]))
            logger.info("token_type_ids: %s" % " ".join([str(x) for x in token_type_ids]))
            logger.info("label: %s (id = %d)" % (example.label, label_id))
            logger.info("e1_start_id: %s" % e11_p)
            logger.info("e2_start_id: %s" % e21_p)
        
        features.append(
            InputFeatures(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids,
                label_id=label_id,
                e1_start_id=e11_p,
                e2_start_id=e21_p,
            )
        )
    return features


def load_and_cache_examples(args, input_file, tokenizer, for_test=False):
    # Load data features from cache or dataset file
    if args.add_sep_token:
        cached_features_file = input_file + "-bert_em-add_sep_token-cached_{}_{}".format(
            list(filter(None, args.model_name_or_path.split("/"))).pop(),
            args.max_seq_len,
        )
    else:
        cached_features_file = input_file + "-bert_em-cached_{}_{}".format(
            list(filter(None, args.model_name_or_path.split("/"))).pop(),
            args.max_seq_len,
        )
    if os.path.exists(cached_features_file) and not args.overwrite_cache:
        logger.info("Loading features from cached file %s", cached_features_file)
        features = torch.load(cached_features_file)
    else:
        logger.info("Creating features from dataset file at %s", input_file)
        if for_test:
            samples, labels = load_relex_samples_for_test(input_file)
        else:
            samples, labels = load_relex_samples(input_file)
        examples = create_examples_from_relex_samples(samples, labels)
        
        features = convert_examples_to_features(
            examples, args.max_seq_len, tokenizer, add_sep_token=args.add_sep_token
        )
        logger.info("Saving features into cached file %s", cached_features_file)
        torch.save(features, cached_features_file)
    
    # Convert to Tensors and build dataset
    all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
    all_attention_mask = torch.tensor([f.attention_mask for f in features], dtype=torch.long)
    all_token_type_ids = torch.tensor([f.token_type_ids for f in features], dtype=torch.long)
    all_e1_ids = torch.tensor([f.e1_start_id for f in features], dtype=torch.long)  # add e1 start id
    all_e2_ids = torch.tensor([f.e2_start_id for f in features], dtype=torch.long)  # add e2 start id
    
    all_label_ids = torch.tensor([f.label_id for f in features], dtype=torch.long)
    
    dataset = TensorDataset(
        all_input_ids,
        all_attention_mask,
        all_token_type_ids,
        all_label_ids,
        all_e1_ids,
        all_e2_ids,
    )
    return dataset
