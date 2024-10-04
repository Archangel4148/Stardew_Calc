from PyQt5.QtWidgets import QApplication


def apply_dark_theme(app: QApplication):
    dark_stylesheet = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-size: 14px;
    }

    QHeaderView::section {
        background-color: #3c3f41;
        color: #ffffff;
        padding: 5px;
        border: none;
    }

    QTableView {
        background-color: #353535;
        gridline-color: #4d4d4d;
        alternate-background-color: #454545;
        color: #ffffff;
    }

    QTableView QTableCornerButton::section {
        background-color: #3c3f41;
    }

    QComboBox, QSpinBox {
        background-color: #454545;
        border: 1px solid #5a5a5a;
        color: #ffffff;
    }

    QPushButton {
        background-color: #3c3f41;
        border: 1px solid #5a5a5a;
        color: #ffffff;
    }

    QPushButton:hover {
        background-color: #5a5a5a;
    }

    """
    app.setStyleSheet(dark_stylesheet)