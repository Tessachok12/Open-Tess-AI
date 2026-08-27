# plugins/example_plugin.py
# Этот плагин просто добавляет смайлик к ответу

def postprocess(response):
    return response + " 😊"

# Если раскомментировать функцию generate, она заменит ядро:
# def generate(user_message, db_manager):
#     return "Я отвечаю через плагин (замена ядра)"
