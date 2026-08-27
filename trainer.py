# trainer.py
import torch
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from model import Seq2Seq
from utils import Vocabulary
import config

class DialogDataset(Dataset):
    def __init__(self, dialogs, vocab, max_len=config.MAX_SEQ_LEN):
        self.data = []
        for user, bot in dialogs:
            src = vocab.encode(user, max_len)
            trg = vocab.encode(bot, max_len)
            self.data.append((src, trg))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

def train_model(model, vocab, db_manager, epochs=config.EPOCHS, batch_size=config.BATCH_SIZE, lr=config.LEARNING_RATE):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    dialogs = db_manager.get_all_dialogs()
    if len(dialogs) < 2:
        print("Недостаточно данных для обучения (нужно хотя бы 2 диалога).")
        return

    
    for user, bot in dialogs:
        vocab.add_sentence(user)
        vocab.add_sentence(bot)

    
    model.encoder.embedding = torch.nn.Embedding(len(vocab), config.EMBED_DIM, padding_idx=0)
    model.decoder.embedding = torch.nn.Embedding(len(vocab), config.EMBED_DIM, padding_idx=0)
    model.decoder.fc = torch.nn.Linear(config.HIDDEN_DIM, len(vocab))
    model.to(device)

    dataset = DialogDataset(dialogs, vocab)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = torch.nn.CrossEntropyLoss(ignore_index=0)

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for src_batch, trg_batch in dataloader:
            src_batch = src_batch.to(device)
            trg_batch = trg_batch.to(device)

            optimizer.zero_grad()
            output = model(src_batch, trg_batch, teacher_forcing_ratio=0.5)
            loss = criterion(output.reshape(-1, output.size(-1)), trg_batch.reshape(-1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Эпоха {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.4f}")

    
    torch.save({
        'model_state': model.state_dict(),
        'vocab': vocab
    }, config.MODEL_SAVE_PATH)
    print(f"Модель сохранена в {config.MODEL_SAVE_PATH}")
