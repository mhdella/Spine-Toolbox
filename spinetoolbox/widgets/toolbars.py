######################################################################################################################
# Copyright (C) 2017 - 2018 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Functions to make and handle QToolBars.

:author: P. Savolainen (VTT)
:date:   19.1.2018
"""

import logging
from PySide2.QtGui import QIcon, QPixmap, QDrag
from PySide2.QtWidgets import QToolBar, QLabel, QAction, QApplication
from PySide2.QtCore import Qt, QMimeData
from config import ICON_TOOLBAR_SS
from graphics_items import ItemImage


class ItemToolBar(QToolBar):
    """A toolbar to add items using drag and drop actions.

    Attributes:
        parent (ToolboxUI): QMainWindow instance
    """
    def __init__(self, parent):
        """Init class"""
        super().__init__("Add Item Toolbar", parent=parent)  # Inherits stylesheet from ToolboxUI
        label = QLabel("Add Item")
        self.addWidget(label)
        # DS
        data_store_pixmap = QPixmap(":/icons/ds_icon.png")
        data_store_widget = DraggableWidget(self, data_store_pixmap, "Data Store")
        data_store_action = self.addWidget(data_store_widget)
        # DC
        data_connection_pixmap = QPixmap(":/icons/dc_icon.png")
        data_connection_widget = DraggableWidget(self, data_connection_pixmap, "Data Connection")
        data_connection_action = self.addWidget(data_connection_widget)
        # Tool
        tool_pixmap = QPixmap(":/icons/tool_icon.png")
        tool_widget = DraggableWidget(self, tool_pixmap, "Tool")
        tool_action = self.addWidget(tool_widget)
        # View
        view_pixmap = QPixmap(":/icons/view_icon.png")
        view_widget = DraggableWidget(self, view_pixmap, "View")
        view_action = self.addWidget(view_widget)
        # set remove all action
        remove_all_icon = QIcon()
        remove_all_icon.addPixmap(QPixmap(":/icons/remove_all.png"), QIcon.Normal, QIcon.On)
        remove_all = QAction(remove_all_icon, "Remove All", parent)
        remove_all.triggered.connect(parent.remove_all_items)
        self.addSeparator()
        self.addAction(remove_all)
        # Set stylesheet
        self.setStyleSheet(ICON_TOOLBAR_SS)
        self.setObjectName("ItemToolbar")


class DraggableWidget(QLabel):
    """A draggable QLabel.

    Attributes:
        parent (QWidget): Parent widget
        pixmap (QPixMap): Picture for the label
        text (str): Item type
    """
    def __init__(self, parent, pixmap, text):
        super().__init__(parent=parent)  # Parent passed to QFrame constructor. Inherits stylesheet from ToolboxUI.
        self.text = text
        self.setPixmap(pixmap.scaled(28, 28))
        self.drag_start_pos = None
        self.setToolTip("""
            <p>Drag-and-drop this icon into the Main View to create a new <b>{}</b> item.</p>
        """.format(self.text))
        self.setAlignment(Qt.AlignHCenter)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def mousePressEvent(self, event):
        """Register drag start position"""
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()

    def mouseMoveEvent(self, event):
        """Start dragging action if needed"""
        if not event.buttons() & Qt.LeftButton:
            return
        if not self.drag_start_pos:
            return
        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(self.text)
        drag.setMimeData(mimeData)
        drag.setPixmap(self.pixmap())
        drag.setHotSpot(self.pixmap().rect().center())
        dropAction = drag.exec_()

    def mouseReleaseEvent(self, event):
        """Forget drag start position"""
        self.drag_start_pos = None
