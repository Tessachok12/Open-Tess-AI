import json
import random
from pathlib import Path
import importlib.util


#  ЗАГРУЗКА СЛОВАРЯ

def load_dictionary():
    """Загружает словарь из dictionary.json в папке плагина"""
    dict_path = Path(__file__).parent / "dictionary.json"
    if not dict_path.exists():
        return None
    with open(dict_path, "r", encoding="utf-8") as f:
        return json.load(f)


#  ЗАГРУЗКА ШАБЛОНОВ

def load_templates(filter_group=None, filter_level=None):
    """
    Загружает шаблоны из templates.json с фильтрацией по группе и уровню
    filter_group: base, time, question, negative, conditional, comparison, imperative, abstract
    filter_level: A1, A2, B1, B2
    """
    templates_path = Path(__file__).parent / "templates.json"
    if not templates_path.exists():
        # Фоллбэк: базовые шаблоны
        return [
            {"id": 1, "group": "base", "level": "A1", "template": "Я {verb} {noun}."},
            {"id": 2, "group": "base", "level": "A1", "template": "Мне нравится {adj} {noun}."},
            {"id": 3, "group": "base", "level": "A1", "template": "Сегодня {noun} {verb}."},
            {"id": 4, "group": "base", "level": "A1", "template": "Это очень {adj} {noun}."},
        ]
    
    with open(templates_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        templates = data.get("templates", [])
    
    if filter_group:
        templates = [t for t in templates if t.get("group") == filter_group]
    if filter_level:
        templates = [t for t in templates if t.get("level") == filter_level]
    
    return templates


#  ЗАГРУЗКА RESPONSE_BANK

def load_response_bank():
    """
    Загружает response_bank_korotki.py:
    - сначала ищет в папке плагина (response_bank.py)
    - потом в корне проекта (response_bank_korotki.py)
    """
    # Ищем в папке плагина
    local_bank = Path(__file__).parent / "response_bank.py"
    if local_bank.exists():
        spec = importlib.util.spec_from_file_location("response_bank_local", local_bank)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.ResponseBank()
    
    # Ищем в корне проекта
    root_bank = Path(__file__).parent.parent.parent / "response_bank_korotki.py"
    if root_bank.exists():
        spec = importlib.util.spec_from_file_location("response_bank_root", root_bank)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.ResponseBank()
    
    return None


#  ИНИЦИАЛИЗАЦИЯ

_dictionary = None
_templates = None
_response_bank = None

def _init():
    global _dictionary, _templates, _response_bank
    if _dictionary is None:
        _dictionary = load_dictionary()
    if _templates is None:
        _templates = load_templates()
    if _response_bank is None:
        _response_bank = load_response_bank()


#  ОБРАБОТКА СПЕЦИАЛЬНЫХ ВОПРОСОВ

def handle_special_questions(user_message):
    """Обрабатывает конкретные вопросы пользователя"""
    user_lower = user_message.lower().strip()
    
    # Вопросы "Кто ты?"
    who_patterns = [
        "кто ты", "ты кто", "кто такой", "расскажи о себе", 
        "представься", "что ты за бот", "твоё имя", "как тебя зовут",
        "кто вы", "вы кто", "что ты такое", "ты человек", "ты бот",
        "ты робот", "ии", "искусственный интеллект", "кто ты такой"
    ]
    if any(pattern in user_lower for pattern in who_patterns):
        responses = [
            "Я OTAI — более улучшенная версия старого ИИ-бота TAIB! 😊",
            "Привет! Я OTAI, улучшенная версия TAIB. Рад познакомиться!",
            "OTAI — это я! Эволюционировавший TAIB с новыми возможностями.",
            "Я OTAI, преемник TAIB. Теперь я умнее и быстрее!",
            "Меня зовут OTAI. Я — новая версия бота TAIB, но с расширенным функционалом."
        ]
        return random.choice(responses)
    
    # Приветствия
    hello_patterns = ["привет", "здравствуй", "здравствуйте", "салют", "хай", "hi", "hello", "ку", "прив"]
    if any(pattern in user_lower for pattern in hello_patterns):
        responses = [
            "Привет! Рад тебя видеть! Я OTAI.",
            "Здравствуй! Как у тебя дела?",
            "Привет-привет! Я OTAI, чем могу помочь?",
            "Салют! Давно не виделись!",
            "Здравствуйте! Рад познакомиться!"
        ]
        return random.choice(responses)
    
    # Как дела?
    how_patterns = ["как дела", "как ты", "как жизнь", "как настроение", "как у тебя"]
    if any(pattern in user_lower for pattern in how_patterns):
        responses = [
            "У меня всё отлично! А у тебя?",
            "Прекрасно! Спасибо, что спросили!",
            "Всё супер! Я полон энергии!",
            "Отлично! А как твои дела?",
            "Замечательно! Чем могу быть полезен?"
        ]
        return random.choice(responses)
    
    # Что ты умеешь?
    ability_patterns = ["что умеешь", "что ты можешь", "твои возможности", "что ты делаешь"]
    if any(pattern in user_lower for pattern in ability_patterns):
        responses = [
            "Я умею отвечать на вопросы, вести диалог и генерировать случайные фразы!",
            "Я могу общаться, отвечать на твои вопросы и даже шутить!",
            "Мои возможности: диалог, генерация ответов, обработка запросов.",
            "Я умею поддерживать беседу и помогать с разными вопросами."
        ]
        return random.choice(responses)
    
    # Прощание
    goodbye_patterns = ["пока", "до свидания", "увидимся", "прощай", "bye", "goodbye", "до встречи"]
    if any(pattern in user_lower for pattern in goodbye_patterns):
        responses = [
            "Пока! Рад был пообщаться!",
            "До свидания! Возвращайся ещё!",
            "Увидимся! Буду ждать тебя снова!",
            "Пока-пока! Не пропадай!"
        ]
        return random.choice(responses)
    
    return None  # Если не обработали — возвращаем None


#  ОПРЕДЕЛЕНИЕ ГРУППЫ ШАБЛОНОВ

def detect_group(user_message):
    """Определяет группу шаблонов по ключевым словам"""
    user_lower = user_message.lower()
    
    if any(word in user_lower for word in ["почему", "как", "что", "зачем", "неужели", "чей", "чьё"]):
        return "question"
    elif any(word in user_lower for word in ["вчера", "завтра", "скоро", "уже", "только что", "недавно", "позже"]):
        return "time"
    elif any(word in user_lower for word in ["не", "никогда", "без", "невозможно", "нельзя"]):
        return "negative"
    elif any(word in user_lower for word in ["если", "чтобы", "из-за", "несмотря", "когда"]):
        return "conditional"
    elif any(word in user_lower for word in ["лучше", "чем", "предпочитаю", "самое", "самый"]):
        return "comparison"
    elif any(word in user_lower for word in ["попробуй", "рекомендую", "стоит", "не забудь", "давай"]):
        return "imperative"
    elif any(word in user_lower for word in ["говорят", "часто", "многие", "каждый", "иногда", "обычно"]):
        return "abstract"
    else:
        return "base"


#  ГЛАВНАЯ ФУНКЦИЯ ГЕНЕРАЦИИ

def generate(user_message, db_manager):
    """Основная функция, вызываемая ботом для генерации ответа"""
    _init()
    
    # 1. Проверяем специальные вопросы (кто ты, привет, как дела и т.д.)
    special_response = handle_special_questions(user_message)
    if special_response:
        return special_response
    
    # 2. Пробуем response_bank (готовые ответы по шаблонам)
    if _response_bank:
        resp = _response_bank.get_response(user_message)
        if resp:
            return resp
    
    # 3. Определяем группу шаблонов и генерируем ответ
    group = detect_group(user_message)
    templates = load_templates(filter_group=group)
    
    # Если в группе нет шаблонов — берём все
    if not templates:
        templates = load_templates()
    
    # 4. Если есть словарь и шаблоны — генерируем
    if _dictionary and templates:
        nouns = _dictionary.get("nouns", [])
        verbs = _dictionary.get("verbs", [])
        adjectives = _dictionary.get("adjectives", [])
        adverbs = _dictionary.get("adverbs", [])
        
        if nouns and verbs and adjectives:
            template_obj = random.choice(templates)
            template = template_obj["template"]
            
            # Подставляем слова с проверкой наличия
            result = template
            if "{noun}" in result and nouns:
                result = result.replace("{noun}", random.choice(nouns))
            if "{verb}" in result and verbs:
                result = result.replace("{verb}", random.choice(verbs))
            if "{adj}" in result and adjectives:
                result = result.replace("{adj}", random.choice(adjectives))
            if "{adv}" in result and adverbs:
                result = result.replace("{adv}", random.choice(adverbs))
            
            return result
    
    # Фоллбэк
    return "Извините, я не понял, но вот вам случайный ответ."

#  ДОПОЛНИТЕЛЬНЫЕ ХУКИ (для plugin_loader)

def preprocess(user_message):
    """Предобработка сообщения пользователя"""
    return user_message

def postprocess(response):
    """Постобработка ответа бота"""
    return response