from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QTextEdit, QFrame, QColorDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QColor, QIcon, QPainter, QPixmap, QCursor
import sys, os

# Отключить автоматическое масштабирование DPI в Qt (если нужно)
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

app = QApplication(sys.argv)
# Или вручную установить атрибут:
app.setAttribute(Qt.AA_EnableHighDpiScaling, False)


class ColorIndicator(QFrame):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(20, 20)
        self.setStyleSheet(f"background-color: {self.color.name()}; border-radius: 10px; border: 1px solid #888;")

    def setColor(self, color):
        self.color = color
        self.setStyleSheet(f"background-color: {self.color.name()}; border-radius: 10px; border: 1px solid #888;")


class CardWidget(QFrame):
    def __init__(self, text, color=QColor("#fff8b0"), parent=None):
        super().__init__(parent)
        self.color = color
        self.setStyleSheet(f"""
            background-color: {self.color.name()};
            border-radius: 12px;
            border: 1px solid #d9d9d9;
        """)
        self.setFixedSize(200, 140)
        self._drag_active = False
        self._resize_active = False
        self._resize_area = 15
        self._mouse_pos = None
        self.init_ui(text)

    def init_ui(self, text):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(5)

        # Текст редактируемый
        self.text_edit = QTextEdit(text, self)
        self.text_edit.setStyleSheet("""
            font-family: Arial; 
            font-size: 14px;
            background: transparent;
            border: none;
        """)
        self.text_edit.setAcceptRichText(False)
        self.layout.addWidget(self.text_edit)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(8)

        self.color_indicator = ColorIndicator(self.color, self)

        # Кнопка смены цвета с PNG иконкой
        self.color_btn = QPushButton("", self)
        self.color_btn.setFixedSize(24, 24)
        self.color_btn.setToolTip("Сменить цвет")
        self.color_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.color_btn.setIcon(QIcon("img/palette.png"))  # путь к PNG иконке
        self.color_btn.setIconSize(QSize(18, 18))
        self.color_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                color: #3A8DFF;
            }
        """)
        self.color_btn.clicked.connect(self.change_color)

        # Кнопка дублирования (через символьную иконку)
        self.dup_btn = QPushButton("", self)
        self.dup_btn.setFixedSize(24, 24)
        self.dup_btn.setToolTip("Дублировать карточку")
        self.dup_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.dup_btn.setIcon(self._create_icon('⎘'))
        self.dup_btn.setIconSize(QSize(18, 18))
        self.dup_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 16px;
            }
            QPushButton:hover {
                color: green;
            }
        """)
        self.dup_btn.clicked.connect(self.duplicate_card)

        # Кнопка удаления (через символьную иконку)
        self.delete_btn = QPushButton("", self)
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setToolTip("Удалить карточку")
        self.delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.delete_btn.setIcon(self._create_icon('✕'))
        self.delete_btn.setIconSize(QSize(18, 18))
        self.delete_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 16px;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_card)

        self.buttons_layout.addWidget(self.color_indicator)
        self.buttons_layout.addWidget(self.color_btn)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.dup_btn)
        self.buttons_layout.addWidget(self.delete_btn)

        self.layout.addLayout(self.buttons_layout)

    def _create_icon(self, char):
        pix = QPixmap(24, 24)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        painter.setPen(Qt.black)
        font = painter.font()
        font.setPointSize(18)
        painter.setFont(font)
        painter.drawText(pix.rect(), Qt.AlignCenter, char)
        painter.end()
        return QIcon(pix)

    def change_color(self):
        color = QColorDialog.getColor(initial=self.color, parent=self)
        if color.isValid():
            self.color = color
            self.color_indicator.setColor(color)
            self.setStyleSheet(f"""
                background-color: {self.color.name()};
                border-radius: 12px;
                border: 1px solid #d9d9d9;
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_in_resize_zone(event.pos()):
                self._resize_active = True
                self._mouse_pos = event.globalPos()
                self._orig_rect = self.geometry()
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self._drag_active = True
                self._drag_start = event.pos()
                self.raise_()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self._drag_active:
            delta = pos - self._drag_start
            new_pos = self.pos() + delta
            parent_rect = self.parent().rect()
            new_x = max(0, min(new_pos.x(), parent_rect.width() - self.width()))
            new_y = max(0, min(new_pos.y(), parent_rect.height() - self.height()))
            self.move(new_x, new_y)
            self.setCursor(Qt.SizeAllCursor)
        elif self._resize_active:
            diff = event.globalPos() - self._mouse_pos
            new_width = max(120, self._orig_rect.width() + diff.x())
            new_height = max(100, self._orig_rect.height() + diff.y())
            self.setFixedSize(new_width, new_height)
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            if self.is_in_resize_zone(pos):
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        self._resize_active = False
        self.setCursor(Qt.ArrowCursor)

    def is_in_resize_zone(self, pos):
        rect = self.rect()
        return pos.x() >= rect.width() - self._resize_area and pos.y() >= rect.height() - self._resize_area

    def delete_card(self):
        self.setParent(None)
        self.deleteLater()

    def duplicate_card(self):
        parent = self.parent()
        if parent:
            new_card = CardWidget(self.text_edit.toPlainText(), self.color, parent)
            new_pos = self.pos() + QPoint(30, 30)
            board_rect = parent.rect()
            x = min(new_pos.x(), board_rect.width() - new_card.width())
            y = min(new_pos.y(), board_rect.height() - new_card.height())
            new_card.move(x, y)
            new_card.show()
            parent.cards.append(new_card)


class BoardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #f7f7f7; border: 1px solid #ccc; border-radius: 8px;")
        self.setMinimumSize(720, 480)
        self.cards = []

    def add_card(self, text="Новая карточка", color=None):
        if color is None:
            color = self.random_pastel_color()
        card = CardWidget(text, color, self)
        offset = len(self.cards) * 30
        card.move(20 + offset, 20 + offset)
        card.show()
        self.cards.append(card)

    def random_pastel_color(self):
        import random
        base = 180
        r = random.randint(base, 255)
        g = random.randint(base, 255)
        b = random.randint(base, 255)
        return QColor(r, g, b)


class BottomBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setStyleSheet("background: #ffffff; border-top: 1px solid #ccc;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(20)

        self.add_card_btn = QPushButton("", self)
        self.add_card_btn.setToolTip("Добавить новую карточку")
        self.add_card_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_card_btn.setIcon(self.create_icon('+'))
        self.add_card_btn.setIconSize(QSize(23, 23))
        self.add_card_btn.setFixedSize(37, 37)
        self.add_card_btn.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                background-color: #2979FF;  /* хороший современный синий */
                border: none;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)

        layout.addWidget(self.add_card_btn)
        layout.addStretch()
    
    def create_icon(self, char):
        pix = QPixmap(40,40)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPointSize(28)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pix.rect(), Qt.AlignCenter, char)
        painter.end()
        return QIcon(pix)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тудушник-доска")
        self.setGeometry(100, 100, 900, 650)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 0)
        main_layout.setSpacing(0)

        self.board = BoardWidget(self)
        main_layout.addWidget(self.board)

        self.bottom_bar = BottomBar(self)
        main_layout.addWidget(self.bottom_bar)

        self.bottom_bar.add_card_btn.clicked.connect(self.on_add_card)

    def on_add_card(self):
        self.board.add_card()


if __name__ == "__main__":
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
