from youtube_transcript_api import YouTubeTranscriptApi
import re
import os
from g4f.client import Client
from g4f.Provider import PollinationsAI
from g4f.cookies import set_cookies_dir, read_cookie_files
import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont
import yt_dlp




client = Client(provider=PollinationsAI)
ydl_opts = {'quiet': True}
cookies_dir = os.path.join(os.getcwd(), "har_and_cookies")
os.makedirs(cookies_dir, exist_ok=True)

set_cookies_dir(cookies_dir)
read_cookie_files()

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        with open("note.txt", "w", encoding="utf-8") as file:
            pass

        def get_video_id(url):
            match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
            if match:
                return match.group(1)
            raise ValueError("id isnt identyfied")

        url = input("Введіть посилання на YouTube відео: ")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                print(f"Тривалість: {info.get('duration')} секунд")
                durtattion = info.get('duration')
            except Exception as e:
                print(f"Помилка: {e}")
        try:
            video_id = get_video_id(url)

            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, languages=["uk", "en"])

            for line in transcript:
                #print(line.text)
                with open("note.txt", "a", encoding="utf-8") as file:
                    file.write(line.text + "\n")

            with open("note.txt", "r", encoding="utf-8") as file:
                content = file.read()

            response = client.chat.completions.create(
                model="openai",
                messages=[
                    {"role": "user",
                     "content": "Скажи якусь коротку фразу до 20 слів, спираючись на субтитри, витягнуті з відео: " + content + ". фраза має містити звернення до користувача, як ніби ти - друг користувача, який із ним дивиться це відео"}
                ]
            )
            ans = response.choices[0].message.content
            print(response.choices[0].message.content)

            self.timeline = [
                {"text": ans, "delay": 2, "image": "pet1.png"},
                #{"text": "Час трохи попрацювати!", "delay": 4, "image": "pet2.png"},
                #{"text": "Ой, я щось побачив...", "delay": 5, "image": "pet1.png"},
                #{"text": "Ну все, я засинаю.", "delay": 6, "image": "pet2.png"}
            ]

            self.current_index = 0

            self.initUI()

            self.timer = QTimer(self)
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.show_next_step)

            # Запуск першого кроку
            if self.timeline:
                self.timer.start(self.timeline[0]["delay"] * 1000)
        except Exception as e:
            print("Помилка:", e)

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Контейнер для спрайту
        self.pet_label = QLabel(self)

        # Контейнер для тексту
        self.text_label = QLabel("", self)
        self.text_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.text_label.setStyleSheet("""
            color: white; 
            background-color: rgba(20, 20, 20, 220); 
            padding: 10px; 
            border-radius: 12px;
            border: 2px solid #ffcc00;
        """)
        self.text_label.hide()

        # Початкові позиції
        self.text_label.move(0, 0)
        self.pet_label.move(30, 50)

        self.resize(600, 600)
        self.show()

    def show_next_step(self):
        if self.current_index < len(self.timeline):
            data = self.timeline[self.current_index]

            # 1. Оновлюємо спрайт
            pixmap = QPixmap(data["image"])
            if not pixmap.isNull():
                self.pet_label.setPixmap(pixmap)
                self.pet_label.adjustSize()
            else:
                print(f"Помилка: Не вдалося знайти файл {data['image']}")

            # 2. Оновлюємо текст
            self.text_label.setText(data["text"])
            self.text_label.show()
            self.text_label.adjustSize()

            # 3. Плануємо наступний крок
            self.current_index += 1
            if self.current_index < len(self.timeline):
                next_delay = self.timeline[self.current_index]["delay"] * 1000
                self.timer.start(next_delay)
        else:
            print("Всі дії виконано.")

    # Логіка перетягування мишкою
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec())