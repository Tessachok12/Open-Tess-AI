# plugin_loader.py
import importlib.util
import os
import sys

class PluginLoader:
    def __init__(self, plugin_dir='plugins'):
        self.plugin_dir = plugin_dir
        self.hooks = []

    def load_plugins(self):
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)

        for item in os.listdir(self.plugin_dir):
            item_path = os.path.join(self.plugin_dir, item)

            # Если папка — загружаем plugin.py внутри неё
            if os.path.isdir(item_path):
                plugin_file = os.path.join(item_path, 'plugin.py')
                if os.path.exists(plugin_file):
                    self._load_module(plugin_file, item)

            # Если .py файл — загружаем как раньше (для обратной совместимости)
            elif item.endswith('.py') and not item.startswith('__'):
                self._load_module(item_path, item[:-3])

    def _load_module(self, filepath, module_name):
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)

        hook = {
            'preprocess': getattr(mod, 'preprocess', None),
            'postprocess': getattr(mod, 'postprocess', None),
            'generate': getattr(mod, 'generate', None)
        }
        self.hooks.append(hook)
        print(f"Загружен плагин: {module_name}")

    def apply_preprocess(self, user_message):
        for hook in self.hooks:
            if hook['preprocess']:
                user_message = hook['preprocess'](user_message)
        return user_message

    def apply_generate(self, user_message, model, vocab, db_manager):
        for hook in self.hooks:
            if hook['generate']:
                return hook['generate'](user_message, db_manager)
        return None

    def apply_postprocess(self, bot_response):
        for hook in self.hooks:
            if hook['postprocess']:
                bot_response = hook['postprocess'](bot_response)
        return bot_response