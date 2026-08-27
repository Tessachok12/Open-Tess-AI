# config.py
BOT_NAME = "open_tess_ai"   # Имя бота – используется в имени БД и модели
LANG = "ru"                 # Язык (влияет на имя БД)
EMBED_DIM = 128
HIDDEN_DIM = 256
NUM_LAYERS = 1
MAX_SEQ_LEN = 50
EPOCHS = 10
BATCH_SIZE = 16
LEARNING_RATE = 0.001
MODEL_SAVE_PATH = "models/open_tess_ai.pt"
