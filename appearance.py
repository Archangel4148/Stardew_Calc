from PyQt5.QtCore import QRect, Qt, pyqtSignal, QCoreApplication
from PyQt5.QtGui import QFontDatabase, QFont, QPainter, QColor
from PyQt5.QtWidgets import QApplication, QWidget


def set_app_font(app: QApplication):
    # Set up fonts
    font_path = "./ui/fonts/Stardew_Valley.otf"
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        stardew_font = QFont(font_family, 15)
        app.setFont(stardew_font)
    else:
        print("Failed to load font:", font_path)

def toggle_day_night(app: QApplication, state:bool):
    if state:
        apply_day_theme(app)
    else:
        apply_cool_night_theme(app)
    set_app_font(app)

def apply_day_theme(app: QApplication):
    stardew_stylesheet = """
    QWidget {
        background-color: #F5E0C3; /* Light cream/brown background */
        color: #6A4E35;           /* Soft brown text */
        font-size: 21px;
    }

    QHeaderView::section {
        background-color: #A67C52; /* Wood-like header color */
        color: #F5E0C3;           /* Cream-colored text */
        padding: 8px;
        border: none;
        font-size: 25px;
    }

    QTableView {
        background-color: #FFE5B4; /* Soft peach for table background */
        gridline-color: #C4A484;   /* Light brown gridlines */
        alternate-background-color: #FFDBAC; /* Alternate row background */
        color: #6A4E35;           /* Text in the table */
        font-size: 20px;
    }

    QTableView QTableCornerButton::section {
        background-color: #A67C52; /* Match table headers */
    }

    QComboBox, QSpinBox {
        background-color: #FFD29E; /* Warm light orange */
        border: 2px solid #A67C52; /* Wood-like border */
        color: #6A4E35;           /* Soft brown text */
        padding: 5px;
        font-size: 20px;
    }

    QPushButton {
        background-color: #FFD29E; /* Soft orange buttons */
        border: 2px solid #A67C52; /* Wood-like border */
        color: #6A4E35;           /* Brown text */
        padding: 10px;
        border-radius: 5px;        /* Rounded corners */
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #FFB76B; /* Darker orange when hovered */
    }

    QPushButton:pressed {
        background-color: #FFA54B; /* Even darker orange when pressed */
    }

    QScrollBar {
        background-color: #FFE5B4; /* Match table background */
    }

    QScrollBar::handle {
        background-color: #A67C52; /* Scrollbar handle with a wood-like color */
    }

    QScrollBar::add-line, QScrollBar::sub-line {
        background-color: #FFD29E; /* Scrollbar arrows */
    }

    QScrollBar::up-arrow, QScrollBar::down-arrow {
        background-color: #A67C52; /* Arrow color */
    }

    """
    app.setStyleSheet(stardew_stylesheet)

def apply_cool_night_theme(app: QApplication):
    cool_night_stylesheet = """
    QWidget {
        background-color: #1C1C2D; /* Dark navy blue background */
        color: #E8E8E8;            /* Light gray text for readability */
        font-size: 21px;
    }

    QHeaderView::section {
        background-color: #292B3A; /* Dark purple-gray for headers */
        color: #D1C6E7;            /* Light lavender text */
        padding: 8px;
        border: none;
        font-size: 25px;
    }

    QTableView {
        background-color: #2A2D38; /* Dark slate gray for table background */
        gridline-color: #5A5A7E;   /* Light purple-gray gridlines */
        alternate-background-color: #3A3D48; /* Slightly lighter alternate row */
        color: #E8E8E8;            /* Light text for the table */
        font-size: 20px;
    }

    QTableView QTableCornerButton::section {
        background-color: #292B3A; /* Match header color */
    }

    QComboBox, QSpinBox {
        background-color: #3E3F5D; /* Dark purple for controls */
        border: 2px solid #5A5A7E; /* Light purple-gray border */
        color: #E8E8E8;            /* Light text */
        padding: 5px;
        font-size: 20px;
    }

    QPushButton {
        background-color: #4B4D69; /* Darker button background */
        border: 2px solid #5A5A7E; /* Light border */
        color: #E8E8E8;            /* Light text */
        padding: 10px;
        border-radius: 5px;       /* Rounded corners */
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #656A8A; /* Lighter purple-gray on hover */
    }

    QPushButton:pressed {
        background-color: #4A4E68; /* Darker when pressed */
    }

    QScrollBar {
        background-color: #2A2D38; /* Match table background */
    }

    QScrollBar::handle {
        background-color: #4B4D69; /* Scrollbar handle color */
    }

    QScrollBar::add-line, QScrollBar::sub-line {
        background-color: #3E3F5D; /* Scrollbar arrows */
    }

    QScrollBar::up-arrow, QScrollBar::down-arrow {
        background-color: #5A5A7E; /* Arrow color */
    }
    """
    app.setStyleSheet(cool_night_stylesheet)


class ToggleSwitch(QWidget):
    clicked = pyqtSignal()  # Declare the clicked signal

    def __init__(self, parent=None):
        super(ToggleSwitch, self).__init__(parent)
        self.is_checked = False
        self.setMinimumSize(60, 40)  # Increased the size to accommodate larger handle

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = QRect(0, 0, self.width(), self.height())
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the track (background) - Make it narrower
        track_height = self.height() // 3  # Track is 1/3 of the widget height
        track_rect = QRect(0, (self.height() - track_height) // 2, self.width(), track_height)

        if self.is_checked:
            painter.setBrush(QColor(76, 175, 80))  # Green when checked
        else:
            painter.setBrush(QColor(200, 200, 200))  # Grey when unchecked
        painter.drawRoundedRect(track_rect, track_height // 2, track_height // 2)

        # Draw the handle (slider) - Larger than the track
        handle_diameter = self.height() - 10  # Make the handle almost the full height
        handle_rect = QRect(5, (self.height() - handle_diameter) // 2, handle_diameter, handle_diameter)

        if self.is_checked:
            handle_rect.moveRight(self.width() - 5)
        else:
            handle_rect.moveLeft(5)

        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(handle_rect)  # Using ellipse for a circular handle

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # Check if left button is clicked
            self.is_checked = not self.is_checked
            self.update()  # Trigger repaint
            self.clicked.emit()
