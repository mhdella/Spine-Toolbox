"""
Classes for handling views in PySide2's model/view framework.
Note: These are Spine Toolbox internal data models.


:author: Manuel Marin <manuelma@kth.se>
:date:   4.4.2018
"""

import logging
import inspect
from PySide2.QtCore import Qt, QObject, Signal, Slot, QModelIndex, QPoint, QRect, QPoint
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsObject
from PySide2.QtGui import QColor, QPen, QPainter, QTransform


class LinksView(QGraphicsView):
    """Pseudo-QMdiArea implemented as QGraphicsView.
    It 'views' the project_item_model as well as the connections_model.
    The project_item_model is viewed as pseudo-QMdiAreaSubwindows.
    The connections_model is viewed as object of class Link (see below)
    drawn between the pseudo-QMdiAreaSubwindows

    Attributes:
        parent(ToolboxUI): Parent of this view
    """

    subWindowActivated = Signal(name="subWindowActivated")

    def __init__(self, parent):
        """Initialize the view"""
        self._scene = QGraphicsScene()
        super().__init__(self._scene)
        self._parent = parent
        self._connection_model = None
        self._project_item_model = None
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.link_drawer = LinkDrawer(parent)
        self.scene().addItem(self.link_drawer)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.max_sw_width = 0
        self.max_sw_height = 0

    def setProjectItemModel(self, model):
        """Set project item model and connect signals"""
        self._project_item_model = model
        self._project_item_model.rowsInserted.connect(self.projectRowsInserted)
        self._project_item_model.rowsAboutToBeRemoved.connect(self.projectRowsRemoved)

    def setConnectionModel(self, model):
        """Set connection model and connect signals"""
        self._connection_model = model
        self._connection_model.dataChanged.connect(self.connectionDataChanged)
        self._connection_model.rowsAboutToBeRemoved.connect(self.connectionRowsRemoved)
        self._connection_model.columnsAboutToBeRemoved.connect(self.connectionColumnsRemoved)

    def project_item_model(self):
        """return project item model"""
        return self._project_item_model

    def connection_model(self):
        """return connection model"""
        return self._connection_model

    def subWindowList(self):
        """Return list of subwindows (replicate QMdiArea.subWindowList)"""
        return [x for x in self.scene().items() if x.type == 'subwindow']

    def setActiveSubWindow(self, item):
        """replicate QMdiArea.setActiveWindow"""
        self.scene().setActiveWindow(item)

    def activeSubWindow(self):
        """replicate QMdiArea.activeSubWindow"""
        return self.scene().activeWindow()

    def removeSubWindow(self, sw): #this method will be obsolete, since it doesn't coordinate with the model
        """remove subwindow and any attached links from the scene"""
        for item in self.scene().items():
            if item.type != "link":
                continue
            if sw.widget() == item.from_item or sw.widget() == item.to_item:
                self.scene().removeItem(item)
        self.scene().removeItem(sw)

    def find_link(self, index):
        """Find link in scene, by model index"""
        for item in self.scene().items():
            if item.type != "link":
                continue
            #logging.debug(item.model_index)
            if item.model_index == index:
                return item
        return None

    @Slot("QModelIndex", "int", "int", name='projectRowsInserted')
    def projectRowsInserted(self, item, first, last):
        """update view when model changes"""
        #logging.debug("project rows inserted")
        for ind in range(first, last+1):
            widget = item.child(ind, 0).data(role=Qt.UserRole).get_widget()
            proxy = self.scene().addWidget(widget, Qt.Window)
            proxy.type = "subwindow"
            sw_geom = proxy.windowFrameGeometry()
            self.max_sw_width = max(self.max_sw_width, sw_geom.width())
            self.max_sw_height = max(self.max_sw_height, sw_geom.height())
            position = QPoint(item.row() * self.max_sw_width, ind * self.max_sw_height)
            proxy.setPos(position)

    @Slot("QModelIndex", "int", "int", name='projectRowsRemoved')
    def projectRowsRemoved(self, item, first, last):
        """update view when model changes"""
        #logging.debug("project rows removed")
        for ind in range(first, last+1):
            sw = item.child(ind, 0).data(role=Qt.UserRole).get_widget().parent()
            self.scene().removeItem(sw)

    @Slot("QModelIndex", "QModelIndex", name='connectionDataChanged')
    def connectionDataChanged(self, top_left, bottom_right, roles=None):
        """update view when model changes"""
        #logging.debug("conn data changed")
        top = top_left.row()
        left = top_left.column()
        bottom = bottom_right.row()
        right = bottom_right.column()
        for row in range(top, bottom+1):
            for column in range(left, right+1):
                index = self.connection_model().index(row, column)
                data = self.connection_model().data(index, Qt.DisplayRole)
                if data:    #connection made, add link widget
                    input_item = self.connection_model().headerData(column, Qt.Horizontal, Qt.DisplayRole)
                    output_item = self.connection_model().headerData(row, Qt.Vertical, Qt.DisplayRole)
                    sub_windows = self.subWindowList()
                    sw_owners = list(sw.widget().owner() for sw in sub_windows)
                    o = sw_owners.index(output_item)
                    i = sw_owners.index(input_item)
                    from_slot = sub_windows[o].widget().ui.toolButton_outputslot
                    to_slot = sub_windows[i].widget().ui.toolButton_inputslot
                    link = Link(self._parent, from_slot, to_slot, index)
                    link.type = "link"
                    self.scene().addItem(link)
                else:   #connection destroyed, remove link widget
                    i = self.find_link(index)
                    if i is not None:
                        self.scene().removeItem(i)

    @Slot("QModelIndex", "int", "int", name='connectionColumnsRemoved')
    def connectionColumnsRemoved(self, index, first, last):
        """update view when model changes"""
        #logging.debug("conn columns removed")
        for row in range(self.connection_model().rowCount()):
            for column in range(first, last+1):
                index = self.connection_model().index(row, column)
                i = self.find_link(index)
                if i is not None:
                    self.scene().removeItem(i)
                    #logging.debug("remove {}".format(i))

    @Slot("QModelIndex", "int", "int", name='connectionRowsRemoved')
    def connectionRowsRemoved(self, column, first, last):
        """update view when model changes"""
        #logging.debug("conn rows removed")
        for column in range(self.connection_model().columnCount()):
            for row in range(first, last+1):
                index = self.connection_model().index(row, column)
                i = self.find_link(index)
                if i is not None:
                    self.scene().removeItem(i)
                    #logging.debug("remove {}".format(i))

    def draw_links(self, button):
        """Draw links when slot button is clicked"""
        if not self.link_drawer.drawing:
            #start drawing and remember slot
            self.link_drawer.drawing = True
            self.link_drawer.start_drawing_at(button)
            self.from_item = button.parent().owner()
            self.from_is_input = button.is_inputslot
        else:
            #stop drawing and make connection
            self.link_drawer.drawing = False
            self.to_is_input = button.is_inputslot
            if self.from_is_input == self.to_is_input:
                slot_type = 'input' if self.to_is_input else 'output'
                self._parent.msg_error.emit("Unable to make connection because the"
                                            " two slots are of the same type ('{}')."\
                                            .format(slot_type))
            else:
                self.to_item = button.parent().owner()
                # create connection
                if self.from_is_input:  #must be input to output
                    input_item = self.from_item
                    output_item = self.to_item
                else:  #must be output to input
                    output_item = self.from_item
                    input_item = self.to_item
                row = self.connection_model().header.index(output_item)
                column = self.connection_model().header.index(input_item)
                index = self.connection_model().createIndex(row, column)
                if not self.connection_model().data(index, Qt.DisplayRole):
                    self.connection_model().setData(index, "value", Qt.EditRole)  # value not used
                    self._parent.msg.emit("<b>{}</b>'s output is now connected to"\
                                  " <b>{}</b>'s input.".format(output_item, input_item))
                else:
                    self._parent.msg.emit("<b>{}</b>'s output is already connected to"\
                              " <b>{}</b>'s input.".format(output_item, input_item))

class Link(QGraphicsLineItem):
    """An item that represents a connection in mdiArea"""

    def __init__(self, parent, from_widget, to_widget, index):
        """Initializes item.

        Args:
            parent (ToolboxUI): QMainWindow instance
            from_slot (QToolButton): the button where this link origins from
            to_slot (QToolButton): the destination button
            index (QModelIndex): the corresponding index in the model
        """
        super().__init__()
        self._parent = parent
        self._from_slot = from_widget
        self._to_slot = to_widget
        self.setZValue(1)   #TODO: is this better than stackBefore?
        self.model_index = index
        self.pen_color = QColor(0,255,0,176)
        self.pen_width = 10
        self.from_item = self._from_slot.parent()
        self.to_item = self._to_slot.parent()
        self.setToolTip("<html><p>Connection from <b>{}</b>'s ouput to <b>{}</b>'s input<\html>"\
            .format(self.from_item.owner(), self.to_item.owner()))
        self.setPen(QPen(self.pen_color, self.pen_width))
        self.update_line()

    def compute_offsets(self):
        self.from_offset = self.from_item.frameGeometry().topLeft()
        self.to_offset = self.to_item.frameGeometry().topLeft()

    def update_extreme_points(self):    #TODO: look for a better way
        """update from and to slot current positions"""
        self.compute_offsets()
        self.from_rect = self._from_slot.geometry()
        self.to_rect = self._to_slot.geometry()
        self.from_center = self.from_rect.center() + self.from_offset
        self.to_center = self.to_rect.center() + self.to_offset
        self.from_topleft = self.from_rect.topLeft() + self.from_offset
        self.to_topleft = self.to_rect.topLeft() + self.to_offset
        self.from_bottomright = self.from_rect.bottomRight() + self.from_offset
        self.to_bottomright = self.to_rect.bottomRight() + self.to_offset

    def update_line(self):
        #logging.debug("update_line")
        self.update_extreme_points()
        self.setLine(self.from_center.x(), self.from_center.y(), self.to_center.x(), self.to_center.y())

    def mousePressEvent(self, e):
        """Trigger slot button if it is underneath"""
        if e.button() != Qt.LeftButton:
            e.ignore()
        else:
            if self._from_slot.underMouse():
                self._from_slot.animateClick()
            elif self._to_slot.underMouse():
                self._to_slot.animateClick()

    def contextMenuEvent(self, e):
        """show contex menu unless mouse is over one of slot button"""
        if self._from_slot.underMouse() or self._to_slot.underMouse():
            e.ignore()
        else:
            self._parent.show_link_context_menu(e.screenPos(), self.model_index)

    def paint(self, painter, option, widget):

        #only paint if two items are visible
        if self.from_item.isVisible() and self.to_item.isVisible():
            self.update_line()
            from_geom = QRect(self.from_topleft, self.from_bottomright)
            to_geom = QRect(self.to_topleft, self.to_bottomright)
            #check whether the active sw overlaps rects and update color accordingly
            from_covered = False
            to_covered = False
            sw = self._parent.ui.mdiArea.activeSubWindow()
            if sw:
                active_item = sw.widget()
                sw_geom = sw.windowFrameGeometry()
                from_covered = active_item != self.from_item and sw_geom.intersects(from_geom)
                to_covered = active_item != self.to_item and sw_geom.intersects(to_geom)
            if from_covered:
                from_rect_color = QColor(128,128,128,128)
            else:
                from_rect_color = self.pen_color
            if to_covered:
                to_rect_color = QColor(128,128,128,64)
            else:
                to_rect_color = self.pen_color
            painter.fillRect(from_geom, from_rect_color)
            painter.fillRect(to_geom, to_rect_color)
            super().paint(painter, option, widget)

class LinkDrawer(QGraphicsLineItem):
    """An item that allows one to draw links between slot buttons in mdiArea
    Attributes:
        parent (ToolboxUI): QMainWindow instance
    """

    def __init__(self, parent):
        """Initializes item.

        Params:
            parent (ToolboxUI): QMainWindow instance
        """
        super().__init__()
        self._parent = parent
        self.fr = None
        self.drawing = False
        # set pen
        self.pen_color = QColor(255,0,255)
        self.pen_width = 6
        self.setPen(QPen(self.pen_color, self.pen_width))
        self.setZValue(2)   #TODO: is this better than stackBefore?
        self.hide()
        self.type = "link-drawer"

    def start_drawing_at(self, button):
        """start drawing"""
        button_pos = button.geometry().center()
        sw_offset = button.parent().frameGeometry().topLeft()
        self.fr = button_pos + sw_offset
        self.to = self.fr
        self.setLine(self.fr.x(), self.fr.y(), self.fr.x(), self.fr.y())
        self.show()
        self.grabMouse()

    def mouseMoveEvent(self, e):
        """Update line end position.

        Args:
            e (QMouseEvent): Mouse event
        """
        if self.fr is not None:
            self.to = e.pos().toPoint()
            moved = self.fr - self.to
            if moved.manhattanLength() > 3:
                self.setLine(self.fr.x(), self.fr.y(), self.to.x(), self.to.y())

    def mousePressEvent(self, e):
        """If link lands on slot button, trigger click

        Args:
            e (QMouseEvent): Mouse event
        """
        self.ungrabMouse()
        self.hide()
        if e.button() != Qt.LeftButton:
            self.drawing = False
        else:
            pos = e.pos().toPoint()
            view_pos = self._parent.ui.mdiArea.mapFromScene(pos)
            for item in self._parent.ui.mdiArea.items(view_pos):
                if item.isWindow():
                    break
            if item:
                sw = item.widget()
                sw_offset = sw.frameGeometry().topLeft()
                pos -= sw_offset
                candidate_button = sw.childAt(pos)
                if hasattr(candidate_button, 'is_inputslot'):
                    candidate_button.animateClick()
                else:
                    self.drawing = False
                    self._parent.msg_error.emit("Unable to make connection."
                                                " Try landing the connection onto a slot button.")


    def paint(self, painter, option, widget):
        """Draw small squares on slot positions.

        Args:
            e (QPaintEvent): Paint event
        """
        p = QPoint(self.pen_width, self.pen_width)
        painter.fillRect(QRect(self.fr-p, self.fr+p), self.pen_color)
        painter.fillRect(QRect(self.to-p, self.to+p), self.pen_color)
        super().paint(painter, option, widget)