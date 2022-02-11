import torch.nn as nn
import torch


class DecoderRNN(nn.Module):
    def __init__(self, hidden_size, output_size, device):
        super(DecoderRNN, self).__init__()
        self.hidden_size = hidden_size
        self.device = device

        # since we have notes played + number of times it happened
        self.gru = nn.GRU(output_size + 1, hidden_size)
        self.out_classification = nn.Linear(hidden_size, output_size)
        # What this would yield is logarithm of expected value of poisson distribution
        self.out_counts = nn.Linear(hidden_size, 1)

    def forward(self, input, hidden):
        input = input.view(1, 1, -1)
        output, hidden = self.gru(input, hidden)
        # print(output.shape)
        output_classification = self.out_classification(output[0])
        output_counts = self.out_counts(output[0])

        return output_classification, output_counts, hidden

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size, device=self.device)
