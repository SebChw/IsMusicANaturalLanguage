import torch
from torch.utils.data import Dataset

#! Probably this representation sucks!!!!! and it just can't do anything good.
#! Since our vectors


class midiTextGeneratorDataset(Dataset):
    """I've decided not to use start and END tokens since, they are not necessary. Start token only confuses the network.
        Since after start network has to return completely different results not having any context.

        However this approach of multilabel classification seems not to be working

    Args:
        Dataset ([type]): [description]
    """

    def __init__(self, path: str):
        with open(path, 'r') as f:
            corpus = f.read().strip()

        # In that case we must filter everything at first and divide tokens and counts
        self.data = corpus.split("\n")
        self.tokens = []
        self.counts = []

        for i, song in enumerate(self.data):
            self.tokens.append([])
            self.counts.append([])

            tokenized = song.split(" ")

            for j in range(0, len(tokenized)):
                if j % 2 == 0:
                    self.tokens[i].append(tokenized[j])
                else:
                    self.counts[i].append(int(tokenized[j]))

        self.unique_letters = set(
            "".join(["".join(song) for song in self.tokens]))

        self.num2word = self.get_num2word_mapping(self.unique_letters)
        self.word2num = {v: k for k, v in self.num2word.items()}

        self.tensor_size = len(self.word2num)

    def get_num2word_mapping(self, letters: set) -> dict:
        mapping = {}
        for index, l in enumerate(letters):
            mapping[index] = l

        return mapping

    def token_to_tensor(self, token: str) -> torch.tensor:
        tensor = torch.zeros((self.tensor_size, 1))

        if token != "":
            for letter in token:
                tensor[self.word2num[letter]] = 1

        # we want [1, 1, num_of_characters]
        return torch.unsqueeze(tensor.view(1, -1), 0)

    def tensor_to_token(self, tensor: torch.tensor) -> str:
        notes = tensor.nonzero()
        token = ""
        for _, note in notes:
            token += self.num2word[note.item()]
            if len(token) > 10:
                break

        return token

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx):
        song = self.tokens[idx]

        inp = self.token_to_tensor(song[0])
        for token in song[1:]:
            t = self.token_to_tensor(token)
            inp = torch.cat((inp, t), dim=0)

        # self.print_given_song(idx)
        return inp, torch.tensor(self.counts[idx])

    def print_given_song(self, idx):
        print(len(self.data[idx].split(" ")))
        print(self.data[idx])


if __name__ == "__main__":
    path = "lstm_dataset_compressed_very_small.txt"
    dataset = midiTextGeneratorDataset(path)
