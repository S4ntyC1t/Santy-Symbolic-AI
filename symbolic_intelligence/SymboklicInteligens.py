# Project: Symbolic AI | Team: Swagaphonchin Team | Lead: S4ntyC1t
import json
import os
import time
import random
import re
import requests
from difflib import get_close_matches
import pymorphy3
import PyPDF2  # Не забудь: pip install PyPDF2 --break-system-packages

class SymbolicAI:
    def __init__(self, memory_file="brain.json", web_memory="brain_web.json", logic_file="logic_rules.json"):
        # Файлы данных
        self.memory_file = memory_file
        self.web_memory = web_memory
        self.logic_file = logic_file
        
        # Данные пользователя
        self.user_name = "Максим"
        self.os_info = "CachyOS (Arch Linux)"
        
        # Внутренние базы
        self.brain, self.responses, self.web_brain, self.logic_rules = {}, {}, {}, {}
        self.morph = pymorphy3.MorphAnalyzer()
        
        # Черный список (не используем)
        self.blacklist = ["cursor ai", "bazzite", "nobara"]
        
        # Лингвистические настройки
        self.synonyms = {
            "ии": "искусственный интеллект", 
            "нейросеть": "нейронная сеть",
            "ит": "информационные технологии",
            "пайтон": "python",
            "раст": "rust"
        }
        self.stop_words = ["да", "это", "как", "ну", "бы", "просто", "ли", "же", "вот"]
        
        # Диалоговые триггеры
        self.dialogue_triggers = {
            "понял": "Рад, что мы на одной волне. Записал в нейронные связи.",
            "привет": f"Привет, {self.user_name}! Система {self.os_info} готова. Что сегодня в приоритете?",
            "продолжим": "Слушаю внимательно. Каков наш следующий шаг?",
            "хорошо": "Отлично. Двигаемся дальше по плану.",
            "круто": "Технологии — это мощь, особенно в твоих руках!",
            "кто ты": "Я твой Symbolic AI, экспертная система без тяжелых нейросетей.",
            "время": f"Сейчас {time.strftime('%H:%M:%S')}. Самое время для кодинга!"
        }

        self.init_system()

    def init_system(self):
        """Загрузка всех баз знаний без потерь данных"""
        files_map = [(self.memory_file, "main"), (self.web_memory, "web"), (self.logic_file, "logic")]
        for file, attr in files_map:
            if os.path.exists(file):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if attr == "main":
                            self.brain, self.responses = data.get("brain", {}), data.get("responses", {})
                        elif attr == "web": self.web_brain = data
                        elif attr == "logic": self.logic_rules = data
                except Exception as e:
                    print(f"[!] Ошибка загрузки {file}: {e}")

    def normalize(self, word):
        """Приведение слова к нормальной форме"""
        word = word.lower().strip()
        if word in self.synonyms: return self.synonyms[word]
        return self.morph.parse(word)[0].normal_form

    def humanize(self, text):
        """Добавление вежливости и контекста к ответам"""
        intros = ["Смотри, ", "По моим данным, ", "Слушай, ", "О, это интересно: "]
        return f"{random.choice(intros)}{self.user_name}, {text}"

    def compare_logic(self, text):
        """Анализ сравнения технологий"""
        text = text.lower()
        if any(x in text for x in ["лучше", " vs ", " или ", "разница"]):
            if "python" in text and ("lua" in text or "rust" in text):
                return "Python идеален для ИИ и веба, но Rust в Zavodio даст тебе полный контроль над памятью."
            if "linux" in text or "windows" in text:
                return f"На твоем {self.os_info} производительность выше за счет планировщика ядер, чем в Windows."
        return None

    def ingest_book(self, file_name):
        """Глубокий анализ PDF и TXT учебников"""
        if not os.path.exists(file_name):
            return f"Файл '{file_name}' не найден."

        print(f"(...) {self.user_name}, провожу деконструкцию документа: {file_name}...")
        content = ""
        try:
            if file_name.lower().endswith('.pdf'):
                with open(file_name, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text: content += page_text + "\n"
            else:
                with open(file_name, "r", encoding="utf-8") as f:
                    content = f.read()

            if not content.strip(): return "Файл пуст."

            funcs = re.findall(r'def\s+(\w+)\s*\(', content)
            classes = re.findall(r'class\s+(\w+)', content)
            libs = re.findall(r'import\s+(\w+)', content)
            
            topic = file_name.replace(".pdf", "").replace(".txt", "").lower()
            self.logic_rules[topic] = {
                "summary": content[:800].replace('\n', ' ') + "...",
                "functions": list(set(funcs)),
                "classes": list(set(classes)),
                "libraries": list(set(libs)),
                "timestamp": time.ctime(),
                "type": "Expert PDF" if file_name.lower().endswith('.pdf') else "Manual Book"
            }

            with open(self.logic_file, "w", encoding="utf-8") as f:
                json.dump(self.logic_rules, f, ensure_ascii=False, indent=4)

            return f"Учебник '{topic}' изучен! Найдено {len(funcs)} функций и {len(classes)} классов."
        except Exception as e:
            return f"Ошибка при анализе: {e}"

    def learn_wiki(self, topic):
        """Обучение через веб-энциклопедию"""
        print(f"(...) {self.user_name}, подключаюсь к Wiki для изучения '{topic}'...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{topic.capitalize()}"
        try:
            res = requests.get(url, headers=headers, timeout=5).json()
            extract = res.get('extract', "")
            if extract:
                self.logic_rules[topic.lower()] = {
                    "summary": extract, 
                    "type": "Wiki Knowledge", 
                    "timestamp": time.ctime()
                }
                with open(self.logic_file, "w", encoding="utf-8") as f:
                    json.dump(self.logic_rules, f, ensure_ascii=False, indent=4)
                return f"Тема '{topic}' успешно добавлена в базу."
            return "Информация не найдена."
        except: return "Ошибка сети."

    def build_code(self, task):
        """Синтез кода на основе изученного в PDF"""
        task = task.lower()
        if "калькулятор" in task or "калькутор" in task:
            return "a = float(input('A: '))\nb = float(input('B: '))\nprint(f'Сумма: {a+b}')"
        
        if "робот" in task or "robot" in task:
            return "class Robot:\n    def __init__(self, name):\n        self.name = name\n        print(f'Робот {self.name} активирован')"
        
        if "палиндром" in task:
            return "def is_palindrome(s):\n    return s == s[::-1]\n\nprint(is_palindrome(input('Введи слово: ')))"
            
        return None

    def process(self, u_input):
        start_t = time.perf_counter()
        clean_text = re.sub(r'[^\w\s\.]', '', u_input.lower()).strip()
        if not clean_text: return
        
        # 1. ЧЕРНЫЙ СПИСОК
        if any(item in clean_text for item in self.blacklist):
            print(f"\nИИ: {self.user_name}, я не работаю с {clean_text}. Это запрещено.")
            return

        words = clean_text.split()

        # 2. КОМАНДЫ ОБУЧЕНИЯ
        if "загрузи учебник" in clean_text:
            print(f"\nИИ: {self.ingest_book(words[-1])}")
            return
        if "выучи" in clean_text:
            print(f"\nИИ: {self.learn_wiki(words[-1])}")
            return

        # 3. ПРИОРИТЕТ: СИНТЕЗ КОДА
        # Если есть "напиши" или "код", сначала пробуем составить программу
        if any(x in clean_text for x in ["код", "напиши", "напишы"]):
            code = self.build_code(clean_text)
            if code:
                print(f"\nИИ: {self.user_name}, вот заготовка кода:\n\n{code}")
                return

        # 4. ТРИГГЕРЫ ДИАЛОГА
        for word in words:
            if word in self.dialogue_triggers:
                print(f"\nИИ: {self.dialogue_triggers[word]}")
                return

        # 5. СРАВНЕНИЕ ТЕХНОЛОГИЙ
        comp = self.compare_logic(clean_text)
        if comp:
            print(f"\nИИ: {self.humanize(comp)}")
            return

        # 6. ПОИСК В ПАМЯТИ (ИЗ УЧЕБНИКОВ) ИЛИ WIKI
        important = [w for w in words if w not in self.stop_words]
        if not important: return
        target = self.normalize(important[-1])

        if target in self.logic_rules:
            data = self.logic_rules[target]
            print(f"\nИИ (Память): {data['summary']}")
            if data.get('functions'): print(f"Методы: {', '.join(data['functions'][:5])}")
            print(f"[Источник: {data.get('type')} | {(time.perf_counter()-start_t)*1000000:.1f} мкс]")
        else:
            print(f"(...) Ищу '{target}' в сети...")
            try:
                url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{target.capitalize()}"
                res = requests.get(url, timeout=3).json()
                print(f"\nИИ: {self.humanize(res.get('extract', 'Информации пока нет.'))}")
            except: print("\nИИ: Сеть недоступна.")

if __name__ == "__main__":
    ai = SymbolicAI()
    print("--- SYMBOLIC AI v17.2: THE SOLID CORE ---")
    try:
        while True:
            cmd = input("\nВы: ")
            if cmd.lower() in ["exit", "выход"]: break
            ai.process(cmd)
    except KeyboardInterrupt: pass