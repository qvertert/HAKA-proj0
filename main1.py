from youtube_transcript_api import YouTubeTranscriptApi
import re
import os
from g4f.client import Client
from g4f.Provider import PollinationsAI
from g4f.cookies import set_cookies_dir, read_cookie_files
import sys
import traceback
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont
import yt_dlp

client = Client(provider=PollinationsAI)
ydl_opts = {'quiet': True}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cookies_dir = os.path.join(BASE_DIR, "har_and_cookies")
os.makedirs(cookies_dir, exist_ok=True)

set_cookies_dir(cookies_dir)
read_cookie_files()


def get_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    raise ValueError("ID відео не знайдено")


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        self.drag_position = None
        self.timeline = []
        self.current_index = 0

        self.initUI()

        note_path = os.path.join(BASE_DIR, "note.txt")
        with open(note_path, "w", encoding="utf-8") as file:
            pass

        try:
            url = input("Введіть посилання на YouTube відео: ").strip()
            phrase_interval = float(input("Введіть інтервал зміни фраз у секундах: ").strip())

            if phrase_interval <= 0:
                raise ValueError("Інтервал має бути більшим за 0")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                duration = int(info.get('duration', 0))
                print(f"Тривалість: {duration} секунд")

            video_id = get_video_id(url)

            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, languages=["uk", "en"])

            for line in transcript:
                with open(note_path, "a", encoding="utf-8") as file:
                    file.write(line.text + "\n")

            with open(note_path, "r", encoding="utf-8") as file:
                content = file.read()

            response = client.chat.completions.create(
                model="openai",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "згенеруй 10 коротких фраз, спираючись на субтитри відео з таймкодами. "
                            "фрази мають стосуватись кожних 10%-ти відсотків пройденого відео. "
                            "ти маєш писати фрази, як ніби ти дивишся це відео разом із користувачем, "
                            "та звертаєшся із цими фразами до нього. "
                            "не включай таймкоди до вихідного тексту!! "
                            "надаю субтитри: " + content
                        )
                    }
                ]
            )

            questions_text = response.choices[0].message.content.strip()
            print("Згенеровані фрази:\n")
            print(questions_text)

            questions_list = [q.strip("•- \t") for q in questions_text.split("\n") if q.strip()]

            if not questions_list:
                questions_list = [questions_text]

            image_path = os.path.join(BASE_DIR, "pet1.png")

            self.timeline.append({
                "text": "Привіт, я твій десктоп пет.",
                "delay": 1,
                "image": image_path
            })

            for question in questions_list:
                self.timeline.append({
                    "text": question,
                    "delay": phrase_interval,
                    "image": image_path
                })

            self.timer = QTimer(self)
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.show_next_step)

            self.show()
            self.raise_()
            self.activateWindow()

            if self.timeline:
                self.show_next_step()

        except Exception as e:
            print("Помилка:", e)
            traceback.print_exc()

            self.text_label.setText(f"Помилка:\n{e}")
            self.text_label.adjustSize()
            self.text_label.show()
            self.show()
            self.raise_()
            self.activateWindow()

    def initUI(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.pet_label = QLabel(self)

        self.text_label = QLabel("", self)
        self.text_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("""
            color: white;
            background-color: rgba(20, 20, 20, 220);
            padding: 10px;
            border-radius: 12px;
            border: 2px solid #ffcc00;
        """)
        self.text_label.hide()

        self.text_label.move(0, 0)
        self.pet_label.move(30, 80)

        self.resize(650, 500)
        self.move(100, 100)
        self.show()

    def show_next_step(self):
        if self.current_index < len(self.timeline):
            data = self.timeline[self.current_index]

            pixmap = QPixmap(data["image"])
            if not pixmap.isNull():
                self.pet_label.setPixmap(pixmap)
                self.pet_label.adjustSize()
                self.pet_label.show()
            else:
                print(f"Помилка: Не вдалося знайти файл {data['image']}")

            self.text_label.setText(data["text"])
            self.text_label.resize(500, 150)
            self.text_label.adjustSize()
            self.text_label.show()

            self.show()
            self.raise_()
            self.activateWindow()

            self.current_index += 1
            if self.current_index < len(self.timeline):
                next_delay = int(self.timeline[self.current_index]["delay"] * 1000)
                self.timer.start(next_delay)
        else:
            print("Всі дії виконано.")

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