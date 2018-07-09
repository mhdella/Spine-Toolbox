#############################################################################
# Copyright (C) 2017 - 2018 VTT Technical Research Centre of Finland
#
# This file is part of Spine Toolbox.
#
# Spine Toolbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../spinetoolbox/ui/spine_datapackage_form.ui',
# licensing of '../spinetoolbox/ui/spine_datapackage_form.ui' applies.
#
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(921, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_descriptor = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_descriptor.sizePolicy().hasHeightForWidth())
        self.label_descriptor.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_descriptor.setFont(font)
        self.label_descriptor.setObjectName("label_descriptor")
        self.verticalLayout.addWidget(self.label_descriptor)
        self.treeView_descriptor = QtWidgets.QTreeView(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView_descriptor.sizePolicy().hasHeightForWidth())
        self.treeView_descriptor.setSizePolicy(sizePolicy)
        self.treeView_descriptor.setMinimumSize(QtCore.QSize(0, 0))
        self.treeView_descriptor.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView_descriptor.setObjectName("treeView_descriptor")
        self.verticalLayout.addWidget(self.treeView_descriptor)
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_resource_data = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_resource_data.sizePolicy().hasHeightForWidth())
        self.label_resource_data.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_resource_data.setFont(font)
        self.label_resource_data.setObjectName("label_resource_data")
        self.horizontalLayout.addWidget(self.label_resource_data)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label_resource_name = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setWeight(50)
        font.setBold(False)
        self.label_resource_name.setFont(font)
        self.label_resource_name.setObjectName("label_resource_name")
        self.horizontalLayout.addWidget(self.label_resource_name)
        self.comboBox_resource_name = QtWidgets.QComboBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_resource_name.sizePolicy().hasHeightForWidth())
        self.comboBox_resource_name.setSizePolicy(sizePolicy)
        self.comboBox_resource_name.setObjectName("comboBox_resource_name")
        self.horizontalLayout.addWidget(self.comboBox_resource_name)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.tableView_resource_data = QtWidgets.QTableView(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_resource_data.sizePolicy().hasHeightForWidth())
        self.tableView_resource_data.setSizePolicy(sizePolicy)
        self.tableView_resource_data.setObjectName("tableView_resource_data")
        self.tableView_resource_data.horizontalHeader().setVisible(False)
        self.tableView_resource_data.horizontalHeader().setHighlightSections(False)
        self.tableView_resource_data.verticalHeader().setVisible(False)
        self.tableView_resource_data.verticalHeader().setHighlightSections(False)
        self.verticalLayout_2.addWidget(self.tableView_resource_data)
        self.verticalLayout_3.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 921, 27))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave_datapackage = QtWidgets.QAction(MainWindow)
        self.actionSave_datapackage.setObjectName("actionSave_datapackage")
        self.actionConvert = QtWidgets.QAction(MainWindow)
        self.actionConvert.setObjectName("actionConvert")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionResource_Spine_names = QtWidgets.QAction(MainWindow)
        self.actionResource_Spine_names.setObjectName("actionResource_Spine_names")
        self.actionField_Spine_names = QtWidgets.QAction(MainWindow)
        self.actionField_Spine_names.setObjectName("actionField_Spine_names")
        self.actionInfer_datapackage = QtWidgets.QAction(MainWindow)
        self.actionInfer_datapackage.setObjectName("actionInfer_datapackage")
        self.actionNew_datapackage = QtWidgets.QAction(MainWindow)
        self.actionNew_datapackage.setObjectName("actionNew_datapackage")
        self.actionLoad_datapackage = QtWidgets.QAction(MainWindow)
        self.actionLoad_datapackage.setObjectName("actionLoad_datapackage")
        self.menuFile.addAction(self.actionInfer_datapackage)
        self.menuFile.addAction(self.actionLoad_datapackage)
        self.menuFile.addAction(self.actionSave_datapackage)
        self.menuFile.addAction(self.actionConvert)
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Spine datapackage form", None, -1))
        self.label_descriptor.setText(QtWidgets.QApplication.translate("MainWindow", "Descriptor", None, -1))
        self.label_resource_data.setText(QtWidgets.QApplication.translate("MainWindow", "Resource data", None, -1))
        self.label_resource_name.setText(QtWidgets.QApplication.translate("MainWindow", "name:", None, -1))
        self.menuFile.setTitle(QtWidgets.QApplication.translate("MainWindow", "Datapackage", None, -1))
        self.actionSave_datapackage.setText(QtWidgets.QApplication.translate("MainWindow", "Save datapackage.json", None, -1))
        self.actionSave_datapackage.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+S", None, -1))
        self.actionConvert.setText(QtWidgets.QApplication.translate("MainWindow", "Convert to Spine.sqlite", None, -1))
        self.actionConvert.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+F5", None, -1))
        self.actionQuit.setText(QtWidgets.QApplication.translate("MainWindow", "Quit", None, -1))
        self.actionQuit.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Q", None, -1))
        self.actionResource_Spine_names.setText(QtWidgets.QApplication.translate("MainWindow", "Resource Spine-names", None, -1))
        self.actionField_Spine_names.setText(QtWidgets.QApplication.translate("MainWindow", "Field Spine-names", None, -1))
        self.actionInfer_datapackage.setText(QtWidgets.QApplication.translate("MainWindow", "Infer from csv", None, -1))
        self.actionInfer_datapackage.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+I", None, -1))
        self.actionNew_datapackage.setText(QtWidgets.QApplication.translate("MainWindow", "New", None, -1))
        self.actionLoad_datapackage.setText(QtWidgets.QApplication.translate("MainWindow", "Load datapackage.json", None, -1))
        self.actionLoad_datapackage.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+L", None, -1))

