# coding=utf-8
"""
BERT-Entity Markers models
We implement two model types:
- BertEntityStarts: Concatenate hidden states at e1 start and e2 start
- BertConcatAll: Concatenate hidden states at [CLS], e1 start and e2 start

We consider two architecture choices:
* Non-linear transformation for hidden states of e1, e2 Or
* Do not use non-linear transformation
"""
import torch
import torch.nn as nn
from torch.nn import CrossEntropyLoss, MSELoss
from transformers import BertPreTrainedModel, RobertaConfig, RobertaModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class PoolerLayer(nn.Module):
    
    def __init__(self, config):
        super(PoolerLayer, self).__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.activation = nn.Tanh()
    
    def forward(self, token_tensor):
        """

        Args:
            hidden_states (torch.FloatTensor): last hidden states of BERT for tokens
                                               size = (batch_size, hidden_size)
        Returns:
            pooled_output: Pool outputs
                           shape = (batch_size, hidden_size)
        """
        pooled_output = self.dense(token_tensor)
        pooled_output = self.activation(pooled_output)
        return pooled_output


class RobertaClassificationHead(nn.Module):
    """Head for sentence-level classification tasks."""

    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.out_proj = nn.Linear(config.hidden_size, config.num_labels)

    def forward(self, features, **kwargs):
        x = features[:, 0, :]  # take <s> token (equiv. to [CLS])
        x = self.dropout(x)
        x = self.dense(x)
        x = torch.tanh(x)
        x = self.dropout(x)
        x = self.out_proj(x)
        return x


class RobertaEntityStarts(BertPreTrainedModel):

    config_class = RobertaConfig
    base_model_prefix = "roberta"

    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels

        self.roberta = RobertaModel(config)
        self.pool_layer = PoolerLayer(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(2 * config.hidden_size, self.config.num_labels)
        self.init_weights()
    
    def forward(self,
                input_ids=None,
                attention_mask=None,
                token_type_ids=None,
                e1_ids=None,
                e2_ids=None,
                position_ids=None,
                head_mask=None,
                inputs_embeds=None,
                labels=None):
        
        outputs = self.roberta(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
        )
        sequence_output = outputs[0]
        batch_size, _, hidden_size = sequence_output.size()
        
        # Put e1_token_tensor and e2_token_tensor to cuda if available
        e1_token_tensor = torch.zeros(batch_size, hidden_size, device=device)
        e2_token_tensor = torch.zeros(batch_size, hidden_size, device=device)
        
        for i in range(e1_ids.shape[0]):
            e1_token_tensor[i] = sequence_output[i, e1_ids[i]]
            e2_token_tensor[i] = sequence_output[i, e2_ids[i]]
        
        e1_token_tensor = self.pool_layer(e1_token_tensor)
        e2_token_tensor = self.pool_layer(e2_token_tensor)
        
        # Concatenate e1_token_tensor and e2_token_tensor
        pooled_output = torch.cat((e1_token_tensor, e2_token_tensor), 1)  # (batch_size, 2*hidden_size)
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)

        outputs = (logits,) + outputs[2:]
        if labels is not None:
            if self.num_labels == 1:
                #  We are doing regression
                loss_fct = MSELoss()
                loss = loss_fct(logits.view(-1), labels.view(-1))
            else:
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            outputs = (loss,) + outputs

        return outputs  # (loss), logits, (hidden_states), (attentions)


class RobertaConcatAll(BertPreTrainedModel):

    config_class = RobertaConfig
    base_model_prefix = "roberta"
    
    def __init__(self, config):
        super(RobertaConcatAll, self).__init__(config)
        self.num_labels = config.num_labels
        
        self.roberta = RobertaModel(config)
        self.pool_layer = PoolerLayer(config)

        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(3 * config.hidden_size, self.config.num_labels)
        self.init_weights()
    
    def forward(self,
                input_ids=None,
                attention_mask=None,
                token_type_ids=None,
                e1_ids=None,
                e2_ids=None,
                position_ids=None,
                head_mask=None,
                inputs_embeds=None,
                labels=None):
        
        outputs = self.roberta(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
        )
        sequence_output = outputs[0]  # last hidden states of BERT for each token
        batch_size, _, hidden_size = sequence_output.size()
        
        # Put e1_token_tensor and e2_token_tensor to cuda if available
        e1_token_tensor = torch.zeros(batch_size, hidden_size, device=device)
        e2_token_tensor = torch.zeros(batch_size, hidden_size, device=device)
        
        for i in range(e1_ids.shape[0]):
            e1_token_tensor[i] = sequence_output[i, e1_ids[i]]
            e2_token_tensor[i] = sequence_output[i, e2_ids[i]]
        
        e1_token_tensor = self.pool_layer(e1_token_tensor)
        e2_token_tensor = self.pool_layer(e2_token_tensor)
        pooled_output = outputs[1]
        
        # Concatenate e1_token_tensor and e2_token_tensor
        pooled_output = torch.cat((pooled_output, e1_token_tensor, e2_token_tensor), 1)  # (batch_size, 3*hidden_size)
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        
        outputs = (logits,) + outputs[2:]  # add hidden states and attention if they are here
        
        if labels is not None:
            if self.num_labels == 1:
                #  We are doing regression
                loss_fct = MSELoss()
                loss = loss_fct(logits.view(-1), labels.view(-1))
            else:
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            outputs = (loss,) + outputs
        
        return outputs  # (loss), logits, (hidden_states), (attentions)
