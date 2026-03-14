import sys
import os
import re
import traceback
import random
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

from g4f.client import Client
from g4f.Provider import PollinationsAI
from g4f.cookies import set_cookies_dir, read_cookie_files

from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont

client = Client(provider=PollinationsAI)
ydl_opts = {'quiet': True}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        self.drag_position = None
        self.questions_list = []
        self.current_percent = 0
        self.step_increment = 5

        # Попередньо завантажуємо картинки, щоб не було блимання при читанні з диска
        self.img_talking = QPixmap(os.path.join(BASE_DIR, "pet1.png"))
        self.img_idle = QPixmap(os.path.join(BASE_DIR, "pet2.png"))

        self.initUI()

        try:
            url = input("Введіть посилання на YouTube відео: ").strip()

            print("Отримання інформації про відео...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                duration = int(info.get('duration', 0))
                if duration == 0: duration = 600
                print(f"Тривалість: {duration} секунд")

            self.step_delay_ms = int(((duration * self.step_increment) / 100) * 1000)
            print(f"Фрази з'являтимуться кожні {int(self.step_delay_ms / 1000)} сек.")

            print("Генерація фраз...")
            response = client.chat.completions.create(
                model="openai",
                messages=[{
                    "role": "user",
                    "content": "Згенеруй 50 коротких реакцій на документальне відео без номерів, кожна з нового рядка. не додавай порядкові номера кожної фрази "
                }]
            )

            content = response.choices[0].message.content.strip()
            self.questions_list = [line.strip("•- *") for line in content.split("\n") if line.strip()]

            # Таймери
            self.main_timer = QTimer(self)
            self.main_timer.timeout.connect(self.show_new_phrase)

            self.hide_timer = QTimer(self)
            self.hide_timer.setSingleShot(True)
            self.hide_timer.timeout.connect(self.hide_text)

            self.show()
            self.show_new_phrase()
            self.main_timer.start(self.step_delay_ms)

        except Exception as e:
            traceback.print_exc()
            self.text_label.setText(f"Помилка: {e}")
            self.text_label.show()
            self.show()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(650, 500)

        self.pet_label = QLabel(self)
        self.pet_label.move(30, 120)

        # Початковий стан — pet2 (мовчить)
        if not self.img_idle.isNull():
            self.pet_label.setPixmap(self.img_idle)
            self.pet_label.adjustSize()

        self.text_label = QLabel("", self)
        self.text_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("""
            color: white;
            background-color: rgba(20, 20, 20, 230);
            padding: 12px;
            border-radius: 15px;
            border: 2px solid #ffcc00;
        """)
        self.text_label.setFixedWidth(350)
        self.text_label.move(20, 20)
        self.text_label.hide()

    def show_new_phrase(self):
        if self.current_percent >= 100:
            self.main_timer.stop()
            return

        if self.questions_list:
            # Змінюємо на pet1 (говорить)
            if not self.img_talking.isNull():
                self.pet_label.setPixmap(self.img_talking)

            phrase = random.choice(self.questions_list)
            self.text_label.setText(phrase)
            self.text_label.adjustSize()
            self.text_label.show()

            # Фраза висить 6 секунд, потім ховаємо і міняємо картинку
            self.hide_timer.start(6000)

        self.current_percent += self.step_increment
        print(f"Прогрес: {self.current_percent}%")

    def hide_text(self):
        self.text_label.hide()
        # Повертаємо pet2 (мовчить)
        if not self.img_idle.isNull():
            self.pet_label.setPixmap(self.img_idle)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec())