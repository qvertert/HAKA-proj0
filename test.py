import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()


        self.timeline = [
            {"text": "Привіт! Я щойно прокинувся.", "delay": 2, "image": "pet1.png"},
            {"text": "Час трохи попрацювати!", "delay": 4, "image": "pet2.png"},
            {"text": "Ой, я щось побачив...", "delay": 5, "image": "pet1.png"},
            {"text": "Ну все, я засинаю.", "delay": 6, "image": "pet2.png"}
        ]

        self.current_index = 0
        # -------------------------------------

        self.initUI()

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_next_step)

        # Запуск першого кроку
        if self.timeline:
            self.timer.start(self.timeline[0]["delay"] * 1000)

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