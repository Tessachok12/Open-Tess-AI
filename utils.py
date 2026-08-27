# utils.py
import torch

class Vocabulary:
    def __init__(self):
        self.word2idx = {'<PAD>': 0, '<SOS>': 1, '<EOS>': 2, '<UNK>': 3}
        self.idx2word = {0: '<PAD>', 1: '<SOS>', 2: '<EOS>', 3: '<UNK>'}
        self.counter = 4

    def add_word(self, word):
        if word not in self.word2idx:
            self.word2idx[word] = self.counter
            self.idx2word[self.counter] = word
            self.counter += 1

    def add_sentence(self, sentence):
        for word in sentence.split():
            self.add_word(word)

    def encode(self, sentence, max_len):
        tokens = [self.word2idx.get(w, self.word2idx['<UNK>']) for w in sentence.split()]
        tokens = [self.word2idx['<SOS>']] + tokens + [self.word2idx['<EOS>']]
        if len(tokens) > max_len:
            tokens = tokens[:max_len]
        else:
            tokens += [self.word2idx['<PAD>']] * (max_len - len(tokens))
        return torch.tensor(tokens, dtype=torch.long)

    def decode(self, indices):
        words = []
        for idx in indices:
            if idx == self.word2idx['<EOS>']:
                break
            if idx not in (self.word2idx['<PAD>'], self.word2idx['<SOS>']):
                words.append(self.idx2word.get(idx, '<UNK>'))
        return ' '.join(words)

    def __len__(self):
        return self.counter
