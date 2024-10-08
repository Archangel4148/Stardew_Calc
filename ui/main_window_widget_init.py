# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\main_window_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_main_window_widget(object):
    def setupUi(self, main_window_widget):
        main_window_widget.setObjectName("main_window_widget")
        main_window_widget.resize(663, 477)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(main_window_widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.big_layout = QtWidgets.QHBoxLayout()
        self.big_layout.setObjectName("big_layout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.toggle_layout = QtWidgets.QFormLayout()
        self.toggle_layout.setObjectName("toggle_layout")
        self.verticalLayout.addLayout(self.toggle_layout)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.season_label = QtWidgets.QLabel(main_window_widget)
        self.season_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.season_label.setObjectName("season_label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.season_label)
        self.season_combo_box = QtWidgets.QComboBox(main_window_widget)
        self.season_combo_box.setObjectName("season_combo_box")
        self.season_combo_box.addItem("")
        self.season_combo_box.addItem("")
        self.season_combo_box.addItem("")
        self.season_combo_box.addItem("")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.season_combo_box)
        self.day_label = QtWidgets.QLabel(main_window_widget)
        self.day_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.day_label.setObjectName("day_label")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.day_label)
        self.day_spin_box = QtWidgets.QSpinBox(main_window_widget)
        self.day_spin_box.setMinimum(1)
        self.day_spin_box.setMaximum(28)
        self.day_spin_box.setObjectName("day_spin_box")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.day_spin_box)
        self.fertilizer_label = QtWidgets.QLabel(main_window_widget)
        self.fertilizer_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fertilizer_label.setObjectName("fertilizer_label")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.fertilizer_label)
        self.fertilizer_combo_box = QtWidgets.QComboBox(main_window_widget)
        self.fertilizer_combo_box.setObjectName("fertilizer_combo_box")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.fertilizer_combo_box)
        self.verticalLayout.addLayout(self.formLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.verticalLayout.setStretch(3, 1)
        self.big_layout.addLayout(self.verticalLayout)
        self.crop_table_view = QtWidgets.QTableView(main_window_widget)
        self.crop_table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.crop_table_view.setObjectName("crop_table_view")
        self.crop_table_view.verticalHeader().setVisible(False)
        self.big_layout.addWidget(self.crop_table_view)
        self.big_layout.setStretch(1, 1)
        self.verticalLayout_2.addLayout(self.big_layout)

        self.retranslateUi(main_window_widget)
        QtCore.QMetaObject.connectSlotsByName(main_window_widget)

    def retranslateUi(self, main_window_widget):
        _translate = QtCore.QCoreApplication.translate
        main_window_widget.setWindowTitle(_translate("main_window_widget", "Form"))
        self.season_label.setText(_translate("main_window_widget", "Season:"))
        self.season_combo_box.setItemText(0, _translate("main_window_widget", "Winter"))
        self.season_combo_box.setItemText(1, _translate("main_window_widget", "Spring"))
        self.season_combo_box.setItemText(2, _translate("main_window_widget", "Summer"))
        self.season_combo_box.setItemText(3, _translate("main_window_widget", "Fall"))
        self.day_label.setText(_translate("main_window_widget", "Day:"))
        self.fertilizer_label.setText(_translate("main_window_widget", "Fertilizer:"))
