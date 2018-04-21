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

# Form implementation generated from reading ui file '../spinetoolbox/ui/tool_template_form.ui'
#
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.ApplicationModal)
        Form.resize(495, 548)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit_name = QtWidgets.QLineEdit(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_name.sizePolicy().hasHeightForWidth())
        self.lineEdit_name.setSizePolicy(sizePolicy)
        self.lineEdit_name.setMinimumSize(QtCore.QSize(220, 24))
        self.lineEdit_name.setMaximumSize(QtCore.QSize(5000, 24))
        self.lineEdit_name.setClearButtonEnabled(True)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.horizontalLayout.addWidget(self.lineEdit_name)
        self.comboBox_tooltype = QtWidgets.QComboBox(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_tooltype.sizePolicy().hasHeightForWidth())
        self.comboBox_tooltype.setSizePolicy(sizePolicy)
        self.comboBox_tooltype.setMinimumSize(QtCore.QSize(180, 24))
        self.comboBox_tooltype.setMaximumSize(QtCore.QSize(16777215, 24))
        self.comboBox_tooltype.setCurrentText("")
        self.comboBox_tooltype.setObjectName("comboBox_tooltype")
        self.horizontalLayout.addWidget(self.comboBox_tooltype)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.textEdit_description = QtWidgets.QTextEdit(self.tab)
        self.textEdit_description.setMaximumSize(QtCore.QSize(16777215, 120))
        self.textEdit_description.setObjectName("textEdit_description")
        self.verticalLayout_2.addWidget(self.textEdit_description)
        self.treeView_includes = QtWidgets.QTreeView(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView_includes.sizePolicy().hasHeightForWidth())
        self.treeView_includes.setSizePolicy(sizePolicy)
        self.treeView_includes.setMaximumSize(QtCore.QSize(16777215, 160))
        self.treeView_includes.setObjectName("treeView_includes")
        self.verticalLayout_2.addWidget(self.treeView_includes)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setMaximumSize(QtCore.QSize(60, 16777215))
        self.label.setObjectName("label")
        self.horizontalLayout_7.addWidget(self.label)
        self.label_mainpath = QtWidgets.QLabel(self.tab)
        self.label_mainpath.setText("")
        self.label_mainpath.setObjectName("label_mainpath")
        self.horizontalLayout_7.addWidget(self.label_mainpath)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.toolButton_plus_includes = QtWidgets.QToolButton(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_plus_includes.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_includes.setSizePolicy(sizePolicy)
        self.toolButton_plus_includes.setMinimumSize(QtCore.QSize(20, 20))
        self.toolButton_plus_includes.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.toolButton_plus_includes.setFont(font)
        self.toolButton_plus_includes.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_plus_includes.setIcon(icon)
        self.toolButton_plus_includes.setObjectName("toolButton_plus_includes")
        self.horizontalLayout_3.addWidget(self.toolButton_plus_includes)
        self.toolButton_minus_includes = QtWidgets.QToolButton(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_minus_includes.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_includes.setSizePolicy(sizePolicy)
        self.toolButton_minus_includes.setMinimumSize(QtCore.QSize(20, 20))
        self.toolButton_minus_includes.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.toolButton_minus_includes.setFont(font)
        self.toolButton_minus_includes.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_minus_includes.setIcon(icon1)
        self.toolButton_minus_includes.setObjectName("toolButton_minus_includes")
        self.horizontalLayout_3.addWidget(self.toolButton_minus_includes)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.lineEdit_args = QtWidgets.QLineEdit(self.tab)
        self.lineEdit_args.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_args.sizePolicy().hasHeightForWidth())
        self.lineEdit_args.setSizePolicy(sizePolicy)
        self.lineEdit_args.setMinimumSize(QtCore.QSize(220, 24))
        self.lineEdit_args.setMaximumSize(QtCore.QSize(5000, 24))
        self.lineEdit_args.setClearButtonEnabled(True)
        self.lineEdit_args.setObjectName("lineEdit_args")
        self.verticalLayout_2.addWidget(self.lineEdit_args)
        spacerItem1 = QtWidgets.QSpacerItem(20, 26, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.treeView_inputfiles = QtWidgets.QTreeView(self.tab_2)
        self.treeView_inputfiles.setObjectName("treeView_inputfiles")
        self.verticalLayout_3.addWidget(self.treeView_inputfiles)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.toolButton_plus_inputfiles = QtWidgets.QToolButton(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_plus_inputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_inputfiles.setSizePolicy(sizePolicy)
        self.toolButton_plus_inputfiles.setMinimumSize(QtCore.QSize(20, 20))
        self.toolButton_plus_inputfiles.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.toolButton_plus_inputfiles.setFont(font)
        self.toolButton_plus_inputfiles.setText("")
        self.toolButton_plus_inputfiles.setIcon(icon)
        self.toolButton_plus_inputfiles.setObjectName("toolButton_plus_inputfiles")
        self.horizontalLayout_6.addWidget(self.toolButton_plus_inputfiles)
        self.toolButton_minus_inputfiles = QtWidgets.QToolButton(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_minus_inputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_inputfiles.setSizePolicy(sizePolicy)
        self.toolButton_minus_inputfiles.setMinimumSize(QtCore.QSize(20, 20))
        self.toolButton_minus_inputfiles.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.toolButton_minus_inputfiles.setFont(font)
        self.toolButton_minus_inputfiles.setText("")
        self.toolButton_minus_inputfiles.setIcon(icon1)
        self.toolButton_minus_inputfiles.setObjectName("toolButton_minus_inputfiles")
        self.horizontalLayout_6.addWidget(self.toolButton_minus_inputfiles)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.treeView_inputfiles_opt = QtWidgets.QTreeView(self.tab_2)
        self.treeView_inputfiles_opt.setObjectName("treeView_inputfiles_opt")
        self.verticalLayout_3.addWidget(self.treeView_inputfiles_opt)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.toolButton_plus_outputfiles = QtWidgets.QToolButton(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_plus_outputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_outputfiles.setSizePolicy(sizePolicy)
        self.toolButton_plus_outputfiles.setMinimumSize(QtCore.QSize(20, 20))
        self.toolButton_plus_outputfiles.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.toolButton_plus_outputfiles.setFont(font)
        self.toolButton_plus_outputfiles.setText("")
        self.toolButton_plus_outputfiles.setIcon(icon)
        self.toolButton_plus_outputfiles.setObjectName("toolButton_plus_outputfiles")
        self.horizontalLayout_5.addWidget(self.toolButton_plus_outputfiles)
        self.toolButton_minus_outputfiles = QtWidgets.QToolButton(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_minus_outputfiles.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_outputfiles.setSizePolicy(sizePolicy)
        self.toolButton_minus_outputfiles.setMinimumSize(QtCore.QSize(20, 20))
        self.toolButton_minus_outputfiles.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.toolButton_minus_outputfiles.setFont(font)
        self.toolButton_minus_outputfiles.setText("")
        self.toolButton_minus_outputfiles.setIcon(icon1)
        self.toolButton_minus_outputfiles.setObjectName("toolButton_minus_outputfiles")
        self.horizontalLayout_5.addWidget(self.toolButton_minus_outputfiles)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.treeView_outputfiles = QtWidgets.QTreeView(self.tab_2)
        self.treeView_outputfiles.setObjectName("treeView_outputfiles")
        self.verticalLayout_3.addWidget(self.treeView_outputfiles)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.toolButton_plus_inputfiles_opt = QtWidgets.QToolButton(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_plus_inputfiles_opt.sizePolicy().hasHeightForWidth())
        self.toolButton_plus_inputfiles_opt.setSizePolicy(sizePolicy)
        self.toolButton_plus_inputfiles_opt.setMinimumSize(QtCore.QSize(20, 20))
        self.toolButton_plus_inputfiles_opt.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.toolButton_plus_inputfiles_opt.setFont(font)
        self.toolButton_plus_inputfiles_opt.setText("")
        self.toolButton_plus_inputfiles_opt.setIcon(icon)
        self.toolButton_plus_inputfiles_opt.setObjectName("toolButton_plus_inputfiles_opt")
        self.horizontalLayout_4.addWidget(self.toolButton_plus_inputfiles_opt)
        self.toolButton_minus_inputfiles_opt = QtWidgets.QToolButton(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton_minus_inputfiles_opt.sizePolicy().hasHeightForWidth())
        self.toolButton_minus_inputfiles_opt.setSizePolicy(sizePolicy)
        self.toolButton_minus_inputfiles_opt.setMinimumSize(QtCore.QSize(20, 20))
        self.toolButton_minus_inputfiles_opt.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.toolButton_minus_inputfiles_opt.setFont(font)
        self.toolButton_minus_inputfiles_opt.setText("")
        self.toolButton_minus_inputfiles_opt.setIcon(icon1)
        self.toolButton_minus_inputfiles_opt.setObjectName("toolButton_minus_inputfiles_opt")
        self.horizontalLayout_4.addWidget(self.toolButton_minus_inputfiles_opt)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem4)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, 6, 0, 6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.pushButton_ok = QtWidgets.QPushButton(Form)
        self.pushButton_ok.setDefault(True)
        self.pushButton_ok.setObjectName("pushButton_ok")
        self.horizontalLayout_2.addWidget(self.pushButton_ok)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem6)
        self.pushButton_cancel = QtWidgets.QPushButton(Form)
        self.pushButton_cancel.setDefault(True)
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.horizontalLayout_2.addWidget(self.pushButton_cancel)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem7)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_statusbar_placeholder = QtWidgets.QHBoxLayout()
        self.horizontalLayout_statusbar_placeholder.setSpacing(0)
        self.horizontalLayout_statusbar_placeholder.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_statusbar_placeholder.setObjectName("horizontalLayout_statusbar_placeholder")
        self.widget_invisible_dummy = QtWidgets.QWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_invisible_dummy.sizePolicy().hasHeightForWidth())
        self.widget_invisible_dummy.setSizePolicy(sizePolicy)
        self.widget_invisible_dummy.setMinimumSize(QtCore.QSize(0, 20))
        self.widget_invisible_dummy.setMaximumSize(QtCore.QSize(0, 20))
        self.widget_invisible_dummy.setObjectName("widget_invisible_dummy")
        self.horizontalLayout_statusbar_placeholder.addWidget(self.widget_invisible_dummy)
        self.verticalLayout.addLayout(self.horizontalLayout_statusbar_placeholder)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.lineEdit_name, self.pushButton_ok)
        Form.setTabOrder(self.pushButton_ok, self.pushButton_cancel)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Tool Template", None, -1))
        self.lineEdit_name.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Item name (required)</p></body></html>", None, -1))
        self.lineEdit_name.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Type tool name here...", None, -1))
        self.textEdit_description.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Type description here...", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Form", "Main dir:", None, -1))
        self.toolButton_plus_includes.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Add source files and folders that your tool requires in order to run, <b>starting by the main program</b>.</p></body></html>", None, -1))
        self.toolButton_minus_includes.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Remove selected or all if nothing is selected</p></body></html>", None, -1))
        self.lineEdit_args.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Item description (optional)</p></body></html>", None, -1))
        self.lineEdit_args.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Type command line arguments here...", None, -1))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtWidgets.QApplication.translate("Form", "General", None, -1))
        self.toolButton_plus_inputfiles.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Add input filenames as they appear in your program code</p></body></html>", None, -1))
        self.toolButton_minus_inputfiles.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Remove selected names or all if nothing is selected</p></body></html>", None, -1))
        self.toolButton_plus_outputfiles.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Add optional input filenames as they appear in your program code</p></body></html>", None, -1))
        self.toolButton_minus_outputfiles.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Remove selected names or all if nothing is selected</p></body></html>", None, -1))
        self.toolButton_plus_inputfiles_opt.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Add output filenames as they appear in your program code</p></body></html>", None, -1))
        self.toolButton_minus_inputfiles_opt.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Remove selected names or all if nothing is selected</p></body></html>", None, -1))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtWidgets.QApplication.translate("Form", "Input/Output", None, -1))
        self.pushButton_ok.setText(QtWidgets.QApplication.translate("Form", "Ok", None, -1))
        self.pushButton_cancel.setText(QtWidgets.QApplication.translate("Form", "Cancel", None, -1))

import resources_icons_rc