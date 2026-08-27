# core.py
import torch
import os
from model import Seq2Seq
from utils import Vocabulary
from db_manager import DatabaseManager
from plugin_loader import PluginLoader
from trainer import train_model
import config

class OpenTessAI:
    def __init__(self, bot_name=config.BOT_NAME, lang=config.LANG):
        self.bot_name = bot_name
        self.lang = lang
        self.db = DatabaseManager(bot_name, lang)
        self.plugins = PluginLoader()
        self.plugins.load_plugins()

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.vocab = Vocabulary()
        self.model = None

        os.makedirs('models', exist_ok=True)

        if os.path.exists(config.MODEL_SAVE_PATH):
            try:
                # Исправление: разрешаем загрузку пользовательских объектов
                checkpoint = torch.load(config.MODEL_SAVE_PATH, map_location=self.device, weights_only=False)
                self.vocab = checkpoint['vocab']
                self.model = Seq2Seq(len(self.vocab), config.EMBED_DIM, config.HIDDEN_DIM, config.NUM_LAYERS)
                self.model.load_state_dict(checkpoint['model_state'])
                self.model.to(self.device)
                self.model.eval()
                print("Модель загружена из файла.")
            except Exception as e:
                print(f"Ошибка при загрузке модели: {e}")
                print("Создаём новую модель (старый файл будет перезаписан при обучении).")
                self.model = Seq2Seq(len(self.vocab), config.EMBED_DIM, config.HIDDEN_DIM, config.NUM_LAYERS)
                self.model.to(self.device)
        else:
            self.model = Seq2Seq(len(self.vocab), config.EMBED_DIM, config.HIDDEN_DIM, config.NUM_LAYERS)
            self.model.to(self.device)
            print("Создана новая модель. Для обучения наберите 'train'.")

    def train(self):
        print("Начинаем обучение на всех диалогах из БД...")
        train_model(self.model, self.vocab, self.db)
        self.model.eval()
        print("Обучение завершено.")

    def generate_response(self, user_message):
        user_message = self.plugins.apply_preprocess(user_message)

        plugin_response = self.plugins.apply_generate(user_message, self.model, self.vocab, self.db)
        if plugin_response is not None:
            bot_response = plugin_response
        else:
            self.model.eval()
            with torch.no_grad():
                src_tensor = self.vocab.encode(user_message, config.MAX_SEQ_LEN).unsqueeze(0).to(self.device)
                output = self.model(src_tensor, None, teacher_forcing_ratio=0)
                pred_indices = output.argmax(dim=-1).squeeze(0).cpu().tolist()
                bot_response = self.vocab.decode(pred_indices)
                if not bot_response:
                    bot_response = "Извините, я не понял."

        bot_response = self.plugins.apply_postprocess(bot_response)

        self.db.save_dialog(user_message, bot_response)
        return bot_response

    def run_console(self):
        print(f"=== Open Tess AI ({self.bot_name}, {self.lang}) ===")
        print("Введите 'exit' для выхода, 'train' для дообучения.")
        while True:
            try:
                inp = input("Вы: ").strip()
                if inp.lower() == 'exit':
                    break
                if inp.lower() == 'train':
                    self.train()
                    continue
                if not inp:
                    continue
                resp = self.generate_response(inp)
                print(f"Бот: {resp}")
            except KeyboardInterrupt:
                print("\nДо свидания!")
                break
        self.db.close()

if __name__ == "__main__":
    bot = OpenTessAI()
    bot.run_console()