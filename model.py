# model.py
import torch
import torch.nn as nn

class Encoder(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers=1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True)

    def forward(self, x):
        embedded = self.embedding(x)
        outputs, (hidden, cell) = self.lstm(embedded)
        return outputs, hidden, cell

class Decoder(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers=1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, encoder_outputs, hidden, cell, target_seq=None, teacher_forcing_ratio=0.5):
        batch_size = encoder_outputs.size(0)
        max_len = target_seq.size(1) if target_seq is not None else 50
        vocab_size = self.fc.out_features

        outputs = torch.zeros(batch_size, max_len, vocab_size).to(encoder_outputs.device)
        input_token = torch.full((batch_size, 1), 1, dtype=torch.long, device=encoder_outputs.device)  # <SOS>

        for t in range(max_len):
            embedded = self.embedding(input_token)
            lstm_out, (hidden, cell) = self.lstm(embedded, (hidden, cell))
            output = self.fc(lstm_out.squeeze(1))
            outputs[:, t, :] = output
            if target_seq is not None and torch.rand(1).item() < teacher_forcing_ratio:
                input_token = target_seq[:, t].unsqueeze(1)
            else:
                input_token = output.argmax(dim=1).unsqueeze(1)
        return outputs

class Seq2Seq(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers=1):
        super().__init__()
        self.encoder = Encoder(vocab_size, embed_dim, hidden_dim, num_layers)
        self.decoder = Decoder(vocab_size, embed_dim, hidden_dim, num_layers)

    def forward(self, src, trg=None, teacher_forcing_ratio=0.5):
        encoder_outputs, hidden, cell = self.encoder(src)
        return self.decoder(encoder_outputs, hidden, cell, trg, teacher_forcing_ratio)
