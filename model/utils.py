from model import rnn
import torch


def load_model(path: str, dataset, device):
    model = rnn.DecoderRNN(256, dataset.tensor_size)
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    return model.to(device)
