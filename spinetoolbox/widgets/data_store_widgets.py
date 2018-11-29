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
Classes for data store widgets.

:author: M. Marin (KTH)
:date:   26.11.2018
"""

import os
import time  # just to measure loading time and sqlalchemy ORM performance
import logging
import json
import numpy as np
from numpy import atleast_1d as arr
from scipy.sparse.csgraph import dijkstra
from PySide2.QtWidgets import QMainWindow, QHeaderView, QDialog, QInputDialog, QToolButton, \
    QMessageBox, QCheckBox, QFileDialog, QApplication, QErrorMessage, QPushButton, QLabel, \
    QGraphicsScene, QGraphicsRectItem, QAction
from PySide2.QtCore import Qt, Signal, Slot, QSettings, QPointF, QRectF, QItemSelection, QItemSelectionModel, QSize
from PySide2.QtGui import QFont, QFontMetrics, QGuiApplication, QIcon, QPixmap, QPalette
from ui.tree_view_form import Ui_MainWindow as tree_view_form_ui
from ui.graph_view_form import Ui_MainWindow as graph_view_form_ui
from config import STATUSBAR_SS
from spinedatabase_api import SpineDBAPIError, SpineIntegrityError
from widgets.custom_menus import ObjectTreeContextMenu, ParameterContextMenu, \
    ObjectItemContextMenu, GraphViewContextMenu
from widgets.custom_delegates import ObjectParameterValueDelegate, ObjectParameterDefinitionDelegate, \
    RelationshipParameterValueDelegate, RelationshipParameterDefinitionDelegate
from widgets.custom_qdialog import AddObjectClassesDialog, AddObjectsDialog, \
    AddRelationshipClassesDialog, AddRelationshipsDialog, \
    EditObjectClassesDialog, EditObjectsDialog, \
    EditRelationshipClassesDialog, EditRelationshipsDialog, \
    CommitDialog
from models import ObjectTreeModel, ObjectClassListModel, RelationshipClassListModel, \
    ObjectParameterValueModel, ObjectParameterDefinitionModel, \
    RelationshipParameterDefinitionModel, RelationshipParameterValueModel, \
    ObjectParameterDefinitionProxy, ObjectParameterValueProxy, \
    RelationshipParameterDefinitionProxy, RelationshipParameterValueProxy, JSONModel
from graphics_items import ObjectItem, ArcItem, CustomTextItem
from excel_import_export import import_xlsx_to_db, export_spine_database_to_xlsx
from spinedatabase_api import copy_database
from datapackage_import_export import import_datapackage
from helpers import busy_effect, relationship_pixmap, object_pixmap, fix_name_ambiguity


class DataStoreForm(QMainWindow):
    """A widget to show and edit Spine objects in a data store.

    Attributes:
        data_store (DataStore): The DataStore instance that owns this form
        db_map (DiffDatabaseMapping): The object relational database mapping
        database (str): The database name
    """
    msg = Signal(str, name="msg")
    msg_error = Signal(str, name="msg_error")

    def __init__(self, data_store, db_map, database, ui):
        """Initialize class."""
        super().__init__(flags=Qt.Window)
        # TODO: Maybe set the parent as ToolboxUI so that its stylesheet is inherited. This may need
        # reimplementing the window minimizing and maximizing actions as well as setting the window modality
        self._data_store = data_store
        # Setup UI from Qt Designer file
        self.ui = ui
        self.ui.setupUi(self)
        self.qsettings = QSettings("SpineProject", "Spine Toolbox")
        # Set up status bar
        self.ui.statusbar.setFixedHeight(20)
        self.ui.statusbar.setSizeGripEnabled(False)
        self.ui.statusbar.setStyleSheet(STATUSBAR_SS)
        # Set up corner widgets
        icon = QIcon(":/icons/relationship_parameter_icon.png")
        button = QPushButton(icon, "Relationship parameter")
        button.setFlat(True)
        button.setLayoutDirection(Qt.LeftToRight)
        button.mousePressEvent = lambda e: e.ignore()
        self.ui.tabWidget_relationship_parameter.setCornerWidget(button, Qt.TopRightCorner)
        icon = QIcon(":/icons/object_parameter_icon.png")
        button = QPushButton(icon, "Object parameter")
        button.setLayoutDirection(Qt.LeftToRight)
        button.setFlat(True)
        button.mousePressEvent = lambda e: e.ignore()
        self.ui.tabWidget_object_parameter.setCornerWidget(button, Qt.TopRightCorner)
        # Class attributes
        self.err_msg = QErrorMessage(self)
        # DB db_map
        self.db_map = db_map
        self.database = database
        self.object_icon_dict = {}
        self.relationship_icon_dict = {}
        # Object tree model
        self.object_tree_model = ObjectTreeModel(self)
        # Parameter value models
        self.object_parameter_value_model = ObjectParameterValueModel(self)
        self.object_parameter_value_proxy = ObjectParameterValueProxy(self)
        self.relationship_parameter_value_model = RelationshipParameterValueModel(self)
        self.relationship_parameter_value_proxy = RelationshipParameterValueProxy(self)
        # Parameter definition models
        self.object_parameter_definition_model = ObjectParameterDefinitionModel(self)
        self.object_parameter_definition_proxy = ObjectParameterDefinitionProxy(self)
        self.relationship_parameter_definition_model = RelationshipParameterDefinitionModel(self)
        self.relationship_parameter_definition_proxy = RelationshipParameterDefinitionProxy(self)
        # Other
        self.default_row_height = QFontMetrics(QFont("", 0)).lineSpacing()
        max_screen_height = max([s.availableSize().height() for s in QGuiApplication.screens()])
        self.visible_rows = int(max_screen_height / self.default_row_height)
        # Ensure this window gets garbage-collected when closed
        self.setAttribute(Qt.WA_DeleteOnClose)

    def connect_signals(self):
        """Connect signals to slots."""
        # Message signals
        self.msg.connect(self.add_message)
        self.msg_error.connect(self.add_error_message)
        # Menu actions
        self.ui.actionCommit.triggered.connect(self.show_commit_session_dialog)
        self.ui.actionRollback.triggered.connect(self.rollback_session)
        self.ui.actionRefresh.triggered.connect(self.refresh_session)
        self.ui.actionClose.triggered.connect(self.close)
        # Object tree
        self.ui.treeView_object.selectionModel().selectionChanged.connect(self.handle_object_tree_selection_changed)
        # Parameter tables delegate commit data
        self.ui.tableView_object_parameter_definition.itemDelegate().commit_model_data.\
            connect(self.set_parameter_definition_data)
        self.ui.tableView_object_parameter_value.itemDelegate().commit_model_data.\
            connect(self.set_parameter_value_data)
        self.ui.tableView_relationship_parameter_definition.itemDelegate().commit_model_data.\
            connect(self.set_parameter_definition_data)
        self.ui.tableView_relationship_parameter_value.itemDelegate().commit_model_data.\
            connect(self.set_parameter_value_data)
        # DS destroyed
        self._data_store.destroyed.connect(self.close)

    @Slot(str, name="add_message")
    def add_message(self, msg):
        """Append regular message to status bar.

        Args:
            msg (str): String to show in QStatusBar
        """
        current_msg = self.ui.statusbar.currentMessage()
        self.ui.statusbar.showMessage("\t".join([msg, current_msg]), 5000)

    @Slot(str, name="add_error_message")
    def add_error_message(self, msg):
        """Show error message.

        Args:
            msg (str): String to show in QErrorMessage
        """
        self.err_msg.showMessage(msg)

    def set_commit_rollback_actions_enabled(self, on):
        self.ui.actionCommit.setEnabled(on)
        self.ui.actionRollback.setEnabled(on)

    @Slot("bool", name="show_commit_session_dialog")
    def show_commit_session_dialog(self, checked=False):
        """Query user for a commit message and commit changes to source database."""
        if not self.db_map.has_pending_changes():
            self.msg.emit("Nothing to commit yet.")
            return
        dialog = CommitDialog(self, self.database)
        answer = dialog.exec_()
        if answer != QDialog.Accepted:
            return
        self.commit_session(dialog.commit_msg)

    @busy_effect
    def commit_session(self, commit_msg):
        try:
            self.db_map.commit_session(commit_msg)
            self.set_commit_rollback_actions_enabled(False)
        except SpineDBAPIError as e:
            self.msg_error.emit(e.msg)
            return
        msg = "All changes committed successfully."
        self.msg.emit(msg)

    @Slot("bool", name="rollback_session")
    def rollback_session(self, checked=False):
        try:
            self.db_map.rollback_session()
            self.set_commit_rollback_actions_enabled(False)
        except SpineDBAPIError as e:
            self.msg_error.emit(e.msg)
            return
        msg = "All changes since last commit rolled back successfully."
        self.msg.emit(msg)
        self.init_models()

    @Slot("bool", name="refresh_session")
    def refresh_session(self, checked=False):
        msg = "Session refreshed."
        self.msg.emit(msg)
        self.init_models()

    def object_icon(self, object_class_name):
        """An appropriate object icon for object_class_name."""
        try:
            icon = self.object_icon_dict[object_class_name]
        except KeyError:
            icon = QIcon(object_pixmap(object_class_name))
            self.object_icon_dict[object_class_name] = icon
        return icon

    def relationship_icon(self, object_class_name_list):
        """An appropriate relationship icon for object_class_name_list."""
        try:
            icon = self.relationship_icon_dict[object_class_name_list]
        except KeyError:
            icon = QIcon(relationship_pixmap(object_class_name_list.split(",")))
            self.relationship_icon_dict[object_class_name_list] = icon
        return icon

    def init_models(self):
        """Initialize models."""
        self.init_object_tree_model()
        self.init_parameter_value_models()
        self.init_parameter_definition_models()

    def init_parameter_value_models(self):
        """Initialize parameter value models from source database."""
        self.object_parameter_value_model.init_model()
        self.relationship_parameter_value_model.init_model()
        self.object_parameter_value_proxy.setSourceModel(self.object_parameter_value_model)
        self.relationship_parameter_value_proxy.setSourceModel(self.relationship_parameter_value_model)

    def init_parameter_definition_models(self):
        """Initialize parameter (definition) models from source database."""
        self.object_parameter_definition_model.init_model()
        self.relationship_parameter_definition_model.init_model()
        self.object_parameter_definition_proxy.setSourceModel(self.object_parameter_definition_model)
        self.relationship_parameter_definition_proxy.setSourceModel(self.relationship_parameter_definition_model)

    def init_views(self):
        """Initialize model views."""
        self.init_object_tree_view()
        self.init_object_parameter_value_view()
        self.init_relationship_parameter_value_view()
        self.init_object_parameter_definition_view()
        self.init_relationship_parameter_definition_view()

    def init_object_tree_view(self):
        """Init object tree view."""
        self.ui.treeView_object.setModel(self.object_tree_model)
        self.ui.treeView_object.header().hide()
        self.ui.treeView_object.expand(self.object_tree_model.root_item.index())
        self.ui.treeView_object.resizeColumnToContents(0)

    def init_object_parameter_value_view(self):
        """Init object parameter value view."""
        self.ui.tableView_object_parameter_value.setModel(self.object_parameter_value_proxy)
        h = self.object_parameter_value_model.horizontal_header_labels().index
        self.ui.tableView_object_parameter_value.horizontalHeader().hideSection(h('id'))
        self.ui.tableView_object_parameter_value.horizontalHeader().hideSection(h('object_class_id'))
        self.ui.tableView_object_parameter_value.horizontalHeader().hideSection(h('object_id'))
        self.ui.tableView_object_parameter_value.horizontalHeader().hideSection(h('parameter_id'))
        self.ui.tableView_object_parameter_value.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.ui.tableView_object_parameter_value.verticalHeader().setDefaultSectionSize(self.default_row_height)
        self.ui.tableView_object_parameter_value.horizontalHeader().setResizeContentsPrecision(self.visible_rows)
        self.ui.tableView_object_parameter_value.resizeColumnsToContents()

    def init_relationship_parameter_value_view(self):
        """Init relationship parameter value view."""
        self.ui.tableView_relationship_parameter_value.setModel(self.relationship_parameter_value_proxy)
        h = self.relationship_parameter_value_model.horizontal_header_labels().index
        self.ui.tableView_relationship_parameter_value.horizontalHeader().hideSection(h('id'))
        self.ui.tableView_relationship_parameter_value.horizontalHeader().hideSection(h('relationship_class_id'))
        self.ui.tableView_relationship_parameter_value.horizontalHeader().hideSection(h('object_class_id_list'))
        self.ui.tableView_relationship_parameter_value.horizontalHeader().hideSection(h('object_class_name_list'))
        self.ui.tableView_relationship_parameter_value.horizontalHeader().hideSection(h('relationship_id'))
        self.ui.tableView_relationship_parameter_value.horizontalHeader().hideSection(h('object_id_list'))
        self.ui.tableView_relationship_parameter_value.horizontalHeader().hideSection(h('parameter_id'))
        self.ui.tableView_relationship_parameter_value.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.ui.tableView_relationship_parameter_value.verticalHeader().setDefaultSectionSize(self.default_row_height)
        self.ui.tableView_relationship_parameter_value.horizontalHeader().\
            setResizeContentsPrecision(self.visible_rows)
        self.ui.tableView_relationship_parameter_value.resizeColumnsToContents()

    def init_object_parameter_definition_view(self):
        """Init object parameter definition view."""
        self.ui.tableView_object_parameter_definition.setModel(self.object_parameter_definition_proxy)
        h = self.object_parameter_definition_model.horizontal_header_labels().index
        self.ui.tableView_object_parameter_definition.horizontalHeader().hideSection(h('id'))
        self.ui.tableView_object_parameter_definition.horizontalHeader().hideSection(h('object_class_id'))
        self.ui.tableView_object_parameter_definition.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.ui.tableView_object_parameter_definition.verticalHeader().setDefaultSectionSize(self.default_row_height)
        self.ui.tableView_object_parameter_definition.horizontalHeader().setResizeContentsPrecision(self.visible_rows)
        self.ui.tableView_object_parameter_definition.resizeColumnsToContents()

    def init_relationship_parameter_definition_view(self):
        """Init relationship parameter definition view."""
        self.ui.tableView_relationship_parameter_definition.setModel(self.relationship_parameter_definition_proxy)
        h = self.relationship_parameter_definition_model.horizontal_header_labels().index
        self.ui.tableView_relationship_parameter_definition.horizontalHeader().hideSection(h('id'))
        self.ui.tableView_relationship_parameter_definition.horizontalHeader().hideSection(h('relationship_class_id'))
        self.ui.tableView_relationship_parameter_definition.horizontalHeader().hideSection(h('object_class_id_list'))
        self.ui.tableView_relationship_parameter_definition.horizontalHeader().\
            setSectionResizeMode(QHeaderView.Interactive)
        self.ui.tableView_relationship_parameter_definition.verticalHeader().\
            setDefaultSectionSize(self.default_row_height)
        self.ui.tableView_relationship_parameter_definition.horizontalHeader().\
            setResizeContentsPrecision(self.visible_rows)
        self.ui.tableView_relationship_parameter_definition.resizeColumnsToContents()

    def setup_delegates(self):
        """Set delegates for tables."""
        # Object parameter
        table_view = self.ui.tableView_object_parameter_definition
        delegate = ObjectParameterDefinitionDelegate(self)
        table_view.setItemDelegate(delegate)
        # Object parameter value
        table_view = self.ui.tableView_object_parameter_value
        delegate = ObjectParameterValueDelegate(self)
        table_view.setItemDelegate(delegate)
        # Relationship parameter
        table_view = self.ui.tableView_relationship_parameter_definition
        delegate = RelationshipParameterDefinitionDelegate(self)
        table_view.setItemDelegate(delegate)
        # Relationship parameter value
        table_view = self.ui.tableView_relationship_parameter_value
        delegate = RelationshipParameterValueDelegate(self)
        table_view.setItemDelegate(delegate)

    @Slot("bool", name="show_add_object_classes_form")
    def show_add_object_classes_form(self, checked=False):
        """Show dialog to let user select preferences for new object classes."""
        dialog = AddObjectClassesDialog(self)
        dialog.show()

    @Slot("bool", name="show_add_objects_form")
    def show_add_objects_form(self, checked=False, class_id=None):
        """Show dialog to let user select preferences for new objects."""
        dialog = AddObjectsDialog(self, class_id=class_id)
        dialog.show()

    @Slot("bool", name="show_add_relationship_classes_form")
    def show_add_relationship_classes_form(self, checked=False, object_class_id=None):
        """Show dialog to let user select preferences for new relationship class."""
        dialog = AddRelationshipClassesDialog(self, object_class_one_id=object_class_id)
        dialog.show()

    @Slot("bool", name="show_add_relationships_form")
    def show_add_relationships_form(
            self, checked=False, relationship_class_id=None, object_id=None, object_class_id=None):
        """Show dialog to let user select preferences for new relationships."""
        dialog = AddRelationshipsDialog(
            self,
            relationship_class_id=relationship_class_id,
            object_id=object_id,
            object_class_id=object_class_id
        )
        dialog.show()

    def add_object_classes(self, object_classes):
        """Insert new object classes."""
        for object_class in object_classes:
            self.object_tree_model.add_object_class(object_class)
        self.set_commit_rollback_actions_enabled(True)
        msg = "Successfully added new object class(es) '{}'.".format("', '".join([x.name for x in object_classes]))
        self.msg.emit(msg)

    @busy_effect
    def add_objects(self, objects):
        """Insert new objects."""
        for object_ in objects:
            self.object_tree_model.add_object(object_)
        self.set_commit_rollback_actions_enabled(True)
        msg = "Successfully added new object(s) '{}'.".format("', '".join([x.name for x in objects]))
        self.msg.emit(msg)

    def add_relationship_classes(self, wide_relationship_classes):
        """Insert new relationship classes."""
        object_name_list_lengths = list()
        for wide_relationship_class in wide_relationship_classes:
            self.object_tree_model.add_relationship_class(wide_relationship_class)
            object_name_list_lengths.append(len(wide_relationship_class.object_class_id_list.split(',')))
        object_name_list_length = max(object_name_list_lengths)
        self.set_commit_rollback_actions_enabled(True)
        relationship_class_name_list = "', '".join([x.name for x in wide_relationship_classes])
        msg = "Successfully added new relationship class(es) '{}'.".format(relationship_class_name_list)
        self.msg.emit(msg)

    def add_relationships(self, wide_relationships):
        """Insert new relationships."""
        for wide_relationship in wide_relationships:
            self.object_tree_model.add_relationship(wide_relationship)
        self.set_commit_rollback_actions_enabled(True)
        relationship_name_list = "', '".join([x.name for x in wide_relationships])
        msg = "Successfully added new relationship(s) '{}'.".format(relationship_name_list)
        self.msg.emit(msg)

    @Slot("bool", name="show_edit_object_classes_form")
    def show_edit_object_classes_form(self, checked=False):
        indexes = self.ui.treeView_object.selectionModel().selectedIndexes()
        if not indexes:
            return
        kwargs_list = list()
        for index in indexes:
            if index.data(Qt.UserRole) != "object_class":
                continue
            kwargs_list.append(index.data(Qt.UserRole + 1))
        dialog = EditObjectClassesDialog(self, kwargs_list)
        dialog.show()

    @Slot("bool", name="show_edit_objects_form")
    def show_edit_objects_form(self, checked=False):
        indexes = self.ui.treeView_object.selectionModel().selectedIndexes()
        if not indexes:
            return
        kwargs_list = list()
        for index in indexes:
            if index.data(Qt.UserRole) != "object":
                continue
            kwargs_list.append(index.data(Qt.UserRole + 1))
        dialog = EditObjectsDialog(self, kwargs_list)
        dialog.show()

    @Slot("bool", name="show_edit_relationship_classes_form")
    def show_edit_relationship_classes_form(self, checked=False):
        indexes = self.ui.treeView_object.selectionModel().selectedIndexes()
        if not indexes:
            return
        kwargs_list = list()
        for index in indexes:
            if index.data(Qt.UserRole) != "relationship_class":
                continue
            kwargs_list.append(index.data(Qt.UserRole + 1))
        dialog = EditRelationshipClassesDialog(self, kwargs_list)
        dialog.show()

    @Slot("bool", name="show_edit_relationships_form")
    def show_edit_relationships_form(self, checked=False):
        current = self.ui.treeView_object.currentIndex()
        if current.data(Qt.UserRole) != "relationship":
            return
        class_id = current.data(Qt.UserRole + 1)['class_id']
        wide_relationship_class = self.db_map.single_wide_relationship_class(id=class_id).one_or_none()
        if not wide_relationship_class:
            return
        indexes = self.ui.treeView_object.selectionModel().selectedIndexes()
        if not indexes:
            return
        kwargs_list = list()
        for index in indexes:
            if index.data(Qt.UserRole) != "relationship":
                continue
            # Only edit relationships of the same class as the one in current index, for now...
            if index.data(Qt.UserRole + 1)['class_id'] != class_id:
                continue
            kwargs_list.append(index.data(Qt.UserRole + 1))
        dialog = EditRelationshipsDialog(self, kwargs_list, wide_relationship_class)
        dialog.show()

    @busy_effect
    def update_object_classes(self, object_classes):
        """Update object classes."""
        self.object_tree_model.update_object_classes(object_classes)
        ids = [x.id for x in object_classes]
        new_names = [x.name for x in object_classes]
        self.rename_items_in_parameter_models('object_class', ids, new_names)
        self.set_commit_rollback_actions_enabled(True)
        msg = "Successfully updated object classes '{}'.".format("', '".join([x.name for x in object_classes]))
        self.msg.emit(msg)

    @busy_effect
    def update_objects(self, objects):
        """Update objects."""
        self.object_tree_model.update_objects(objects)
        ids = [x.id for x in objects]
        new_names = [x.name for x in objects]
        self.rename_items_in_parameter_models('object', ids, new_names)
        self.set_commit_rollback_actions_enabled(True)
        msg = "Successfully updated objects '{}'.".format("', '".join([x.name for x in objects]))
        self.msg.emit(msg)

    @busy_effect
    def update_relationships(self, wide_relationships):
        """Update relationships."""
        self.object_tree_model.update_relationships(wide_relationships)
        # NOTE: we don't need to call rename_items_in_parameter_models here, for now
        self.set_commit_rollback_actions_enabled(True)
        relationship_name_list = "', '".join([x.name for x in wide_relationships])
        msg = "Successfully updated relationships '{}'.".format(relationship_name_list)
        self.msg.emit(msg)

    @busy_effect
    def update_relationship_classes(self, wide_relationship_classes):
        """Update relationship classes."""
        self.object_tree_model.update_relationship_classes(wide_relationship_classes)
        ids = [x.id for x in wide_relationship_classes]
        new_names = [x.name for x in wide_relationship_classes]
        self.rename_items_in_parameter_models('relationship_class', ids, new_names)
        self.set_commit_rollback_actions_enabled(True)
        relationship_class_name_list = "', '".join([x.name for x in wide_relationship_classes])
        msg = "Successfully updated relationship classes '{}'.".format(relationship_class_name_list)
        self.msg.emit(msg)

    def rename_items_in_parameter_models(self, renamed_type, ids, new_names):
        """Rename items in parameter definition and value models."""
        self.object_parameter_definition_model.rename_items(renamed_type, ids, new_names)
        self.object_parameter_value_model.rename_items(renamed_type, ids, new_names)
        self.relationship_parameter_definition_model.rename_items(renamed_type, ids, new_names)
        self.relationship_parameter_value_model.rename_items(renamed_type, ids, new_names)

    @Slot("QModelIndex", "QVariant", name="set_parameter_value_data")
    def set_parameter_value_data(self, index, new_value):
        """Update (object or relationship) parameter value with newly edited data."""
        if new_value is None:
            return
        proxy_model = index.model()
        source_model = proxy_model.sourceModel()
        source_index = proxy_model.mapToSource(index)
        source_model.setData(source_index, new_value)

    @Slot("QModelIndex", "QVariant", name="set_parameter_definition_data")
    def set_parameter_definition_data(self, index, new_value):
        """Update (object or relationship) parameter definition with newly edited data."""
        if new_value is None:
            return
        proxy_model = index.model()
        source_model = proxy_model.sourceModel()
        source_index = proxy_model.mapToSource(index)
        parameter_name_column = source_model.horizontal_header_labels().index('parameter_name')
        if source_model.setData(source_index, new_value) and source_index.column() == parameter_name_column:
            parameter_id_column = source_model.horizontal_header_labels().index('id')
            id = source_index.sibling(source_index.row(), parameter_id_column).data(Qt.DisplayRole)
            new_name = new_value
            self.object_parameter_value_model.rename_items("parameter", [id], [new_name])
            self.relationship_parameter_value_model.rename_items("parameter", [id], [new_name])

    def show_commit_session_prompt(self):
        """Shows the commit session message box."""
        config = self._data_store._toolbox._config
        commit_at_exit = config.get("settings", "commit_at_exit")
        if commit_at_exit == "0":
            # Don't commit session and don't show message box
            return
        elif commit_at_exit == "1":  # Default
            # Show message box
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Commit pending changes")
            msg.setText("The current session has uncommitted changes. Do you want to commit them now?")
            msg.setInformativeText("WARNING: If you choose not to commit, all changes will be lost.")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            chkbox = QCheckBox()
            chkbox.setText("Do not ask me again")
            msg.setCheckBox(chkbox)
            answer = msg.exec_()
            chk = chkbox.checkState()
            if answer == QMessageBox.Yes:
                self.show_commit_session_dialog()
                if chk == 2:
                    # Save preference into config file
                    config.set("settings", "commit_at_exit", "2")
            else:
                if chk == 2:
                    # Save preference into config file
                    config.set("settings", "commit_at_exit", "0")
        elif commit_at_exit == "2":
            # Commit session and don't show message box
            self.show_commit_session_dialog()
        else:
            config.set("settings", "commit_at_exit", "1")
        return

    def restore_ui(self):
        """Restore UI state from previous session."""
        window_size = self.qsettings.value("{0}/windowSize".format(self.settings_key))
        window_pos = self.qsettings.value("{0}/windowPosition".format(self.settings_key))
        window_maximized = self.qsettings.value("{0}/windowMaximized".format(self.settings_key), defaultValue='false')
        n_screens = self.qsettings.value("{0}/n_screens".format(self.settings_key), defaultValue=1)
        if window_size:
            self.resize(window_size)
        if window_pos:
            self.move(window_pos)
        if window_maximized == 'true':
            self.setWindowState(Qt.WindowMaximized)
        # noinspection PyArgumentList
        if len(QGuiApplication.screens()) < int(n_screens):
            # There are less screens available now than on previous application startup
            self.move(0, 0)  # Move this widget to primary screen position (0,0)

    def closeEvent(self, event=None):
        """Handle close window.

        Args:
            event (QEvent): Closing event if 'X' is clicked.
        """
        # save qsettings
        self.qsettings.setValue("{}/windowSize".format(self.settings_key), self.size())
        self.qsettings.setValue("{}/windowPosition".format(self.settings_key), self.pos())
        if self.windowState() == Qt.WindowMaximized:
            self.qsettings.setValue("{}/windowMaximized".format(self.settings_key), True)
        else:
            self.qsettings.setValue("{}/windowMaximized".format(self.settings_key), False)
        if self.db_map.has_pending_changes():
            self.show_commit_session_prompt()
        self.db_map.close()
        if event:
            event.accept()


class TreeViewForm(DataStoreForm):
    """A widget to show and edit Spine objects in a data store.

    Attributes:
        data_store (DataStore): The DataStore instance that owns this form
        db_map (DiffDatabaseMapping): The object relational database mapping
        database (str): The database name
    """
    def __init__(self, data_store, db_map, database):
        """Initialize class."""
        tic = time.clock()
        super().__init__(data_store, db_map, database, tree_view_form_ui())
        # JSON models
        self.object_parameter_json_model = JSONModel(self)
        self.relationship_parameter_json_model = JSONModel(self)
        self.object_parameter_json_splitter_sizes = None
        self.relationship_parameter_json_splitter_sizes = None
        # Context menus
        self.object_tree_context_menu = None
        self.object_parameter_value_context_menu = None
        self.relationship_parameter_value_context_menu = None
        self.object_parameter_context_menu = None
        self.relationship_parameter_context_menu = None
        # Others
        self.clipboard = QApplication.clipboard()
        self.clipboard_text = self.clipboard.text()
        self.focus_widget = None  # Last widget which had focus before showing a menu from the menubar
        self.fully_expand_icon = QIcon(QPixmap(":/icons/fully_expand.png"))
        self.fully_collapse_icon = QIcon(QPixmap(":/icons/fully_collapse.png"))
        self.find_next_icon = QIcon(QPixmap(":/icons/find_next.png"))
        # init models and views
        self.init_models()
        self.init_views()
        self.setup_delegates()
        self.setup_buttons()
        self.connect_signals()
        self.settings_key = 'treeViewWidget'
        self.restore_ui()
        self.setWindowTitle("Data store tree view    -- {} --".format(self.database))
        # Ensure this window gets garbage-collected when closed
        toc = time.clock()
        self.msg.emit("Tree view form created in {} seconds".format(toc - tic))

    def setup_buttons(self):
        """Specify actions and menus for add/remove parameter buttons."""
        # Setup button actions
        self.ui.toolButton_add_object_parameter_values.\
            setDefaultAction(self.ui.actionAdd_object_parameter_values)
        self.ui.toolButton_remove_object_parameter_values.\
            setDefaultAction(self.ui.actionRemove_object_parameter_values)
        self.ui.toolButton_add_relationship_parameter_values.\
            setDefaultAction(self.ui.actionAdd_relationship_parameter_values)
        self.ui.toolButton_remove_relationship_parameter_values.\
            setDefaultAction(self.ui.actionRemove_relationship_parameter_values)
        self.ui.toolButton_add_object_parameter_definitions.\
            setDefaultAction(self.ui.actionAdd_object_parameter_definitions)
        self.ui.toolButton_remove_object_parameter_definitions.\
            setDefaultAction(self.ui.actionRemove_object_parameter_definitions)
        self.ui.toolButton_add_relationship_parameter_definitions.\
            setDefaultAction(self.ui.actionAdd_relationship_parameter_definitions)
        self.ui.toolButton_remove_relationship_parameter_definitions.\
            setDefaultAction(self.ui.actionRemove_relationship_parameter_definitions)

    def connect_signals(self):
        """Connect signals to slots."""
        # Menu actions
        super().connect_signals()
        self.ui.actionImport.triggered.connect(self.show_import_file_dialog)
        self.ui.actionExport.triggered.connect(self.show_export_file_dialog)
        self.ui.actionAdd_object_classes.triggered.connect(self.show_add_object_classes_form)
        self.ui.actionAdd_objects.triggered.connect(self.show_add_objects_form)
        self.ui.actionAdd_relationship_classes.triggered.connect(self.show_add_relationship_classes_form)
        self.ui.actionAdd_relationships.triggered.connect(self.show_add_relationships_form)
        self.ui.actionAdd_object_parameter_values.triggered.connect(self.add_object_parameter_values)
        self.ui.actionAdd_relationship_parameter_values.triggered.connect(self.add_relationship_parameter_values)
        self.ui.actionAdd_object_parameter_definitions.triggered.connect(self.add_object_parameter_definitions)
        self.ui.actionAdd_relationship_parameter_definitions.triggered.\
            connect(self.add_relationship_parameter_definitions)
        self.ui.actionEdit_object_classes.triggered.connect(self.show_edit_object_classes_form)
        self.ui.actionEdit_objects.triggered.connect(self.show_edit_objects_form)
        self.ui.actionEdit_relationship_classes.triggered.connect(self.show_edit_relationship_classes_form)
        self.ui.actionEdit_relationships.triggered.connect(self.show_edit_relationships_form)
        self.ui.actionRemove_object_tree_items.triggered.connect(self.remove_object_tree_items)
        self.ui.actionRemove_object_parameter_definitions.triggered.connect(self.remove_object_parameter_definitions)
        self.ui.actionRemove_object_parameter_values.triggered.connect(self.remove_object_parameter_values)
        self.ui.actionRemove_relationship_parameter_definitions.triggered.\
            connect(self.remove_relationship_parameter_definitions)
        self.ui.actionRemove_relationship_parameter_values.triggered.\
            connect(self.remove_relationship_parameter_values)
        # Copy and paste
        self.ui.actionCopy.triggered.connect(self.copy)
        self.ui.actionPaste.triggered.connect(self.paste)
        # Object tree
        self.ui.treeView_object.edit_key_pressed.connect(self.edit_object_tree_items)
        self.ui.treeView_object.customContextMenuRequested.connect(self.show_object_tree_context_menu)
        self.ui.treeView_object.doubleClicked.connect(self.find_next_leaf)
        # Autofilter parameter tables
        self.ui.tableView_object_parameter_definition.filter_changed.connect(self.apply_autofilter)
        self.ui.tableView_object_parameter_value.filter_changed.connect(self.apply_autofilter)
        self.ui.tableView_relationship_parameter_definition.filter_changed.connect(self.apply_autofilter)
        self.ui.tableView_relationship_parameter_value.filter_changed.connect(self.apply_autofilter)
        # Parameter value tables delegate json editor requested
        self.ui.tableView_object_parameter_value.itemDelegate().json_editor_requested.\
            connect(self.edit_object_parameter_json)
        self.ui.tableView_relationship_parameter_value.itemDelegate().json_editor_requested.\
            connect(self.edit_relationship_parameter_json)
        # Parameter tables selection changes
        self.ui.tableView_object_parameter_definition.selectionModel().selectionChanged.\
            connect(self.handle_object_parameter_definition_selection_changed)
        self.ui.tableView_object_parameter_value.selectionModel().selectionChanged.\
            connect(self.handle_object_parameter_value_selection_changed)
        self.ui.tableView_relationship_parameter_definition.selectionModel().selectionChanged.\
            connect(self.handle_relationship_parameter_definition_selection_changed)
        self.ui.tableView_relationship_parameter_value.selectionModel().selectionChanged.\
            connect(self.handle_relationship_parameter_value_selection_changed)
        # Parameter value tables current changed
        self.ui.tableView_object_parameter_value.selectionModel().currentChanged.\
            connect(self.handle_object_parameter_value_current_changed)
        self.ui.tableView_relationship_parameter_value.selectionModel().currentChanged.\
            connect(self.handle_relationship_parameter_value_current_changed)
        # Parameter json models data changed
        self.object_parameter_json_model.dataChanged.connect(self.handle_object_parameter_json_data_changed)
        self.relationship_parameter_json_model.dataChanged.\
            connect(self.handle_relationship_parameter_json_data_changed)
        # Parameter tabwidgets current changed
        self.ui.tabWidget_object_parameter.currentChanged.connect(self.handle_object_parameter_tab_changed)
        self.ui.tabWidget_relationship_parameter.currentChanged.connect(self.handle_relationship_parameter_tab_changed)
        # Parameter tables context menu requested
        self.ui.tableView_object_parameter_definition.customContextMenuRequested.\
            connect(self.show_object_parameter_context_menu)
        self.ui.tableView_object_parameter_value.customContextMenuRequested.\
            connect(self.show_object_parameter_value_context_menu)
        self.ui.tableView_relationship_parameter_definition.customContextMenuRequested.\
            connect(self.show_relationship_parameter_context_menu)
        self.ui.tableView_relationship_parameter_value.customContextMenuRequested.\
            connect(self.show_relationship_parameter_value_context_menu)
        # Clipboard data changed
        self.clipboard.dataChanged.connect(self.clipboard_data_changed)
        # Menu about to show
        self.ui.menuFile.aboutToShow.connect(self.handle_menu_about_to_show)
        self.ui.menuEdit.aboutToShow.connect(self.handle_menu_about_to_show)
        self.ui.menuSession.aboutToShow.connect(self.handle_menu_about_to_show)

    @Slot(name="clipboard_data_changed")
    def clipboard_data_changed(self):
        """Store data from clipboard."""
        self.clipboard_text = self.clipboard.text()

    @Slot("bool", name="copy")
    def copy(self, checked=False):
        """Copy data to clipboard."""
        focus_widget = self.focusWidget()
        try:
            focus_widget.copy()
        except AttributeError:
            pass

    @Slot("bool", name="paste")
    def paste(self, checked=False):
        """Paste data from clipboard."""
        focus_widget = self.focusWidget()
        try:
            focus_widget.paste(self.clipboard_text)
        except AttributeError:
            pass

    @Slot("QModelIndex","QModelIndex", name="handle_object_parameter_value_current_changed")
    def handle_object_parameter_value_current_changed(self, current, previous):
        """Show/hide json table."""
        header = self.object_parameter_value_model.horizontal_header_labels()
        data = current.data(Qt.EditRole)
        splitter = self.ui.tableView_object_parameter_json.parent()
        if header[current.column()] == "json":
            # Reset json model
            self.object_parameter_json_model.reset_model(data)
            self.ui.tableView_object_parameter_json.resizeColumnsToContents()
            if self.ui.tableView_object_parameter_json.isVisible():
                return
            if not self.object_parameter_json_splitter_sizes:
                # Apply decent sizes
                sizes = splitter.sizes()
                width = self.ui.tableView_object_parameter_json.columnWidth(0)
                if sizes[1] < width:
                    sizes[0] = sum(sizes) - width
                    sizes[1] = width
                splitter.setSizes(sizes)
            else:
                # Apply stored sizes
                splitter.setSizes(self.object_parameter_json_splitter_sizes)
            self.ui.tableView_object_parameter_json.show()
        elif self.ui.tableView_object_parameter_json.isVisible():
            # Save sizes and hide
            self.object_parameter_json_splitter_sizes = splitter.sizes()
            self.ui.tableView_object_parameter_json.hide()

    @Slot("QModelIndex","QModelIndex", name="handle_relationship_parameter_value_current_changed")
    def handle_relationship_parameter_value_current_changed(self, current, previous):
        """Show/hide json table."""
        header = self.relationship_parameter_value_model.horizontal_header_labels()
        data = current.data(Qt.EditRole)
        splitter = self.ui.tableView_relationship_parameter_json.parent()
        if header[current.column()] == "json":
            # Reset json model
            self.relationship_parameter_json_model.reset_model(data)
            self.ui.tableView_relationship_parameter_json.resizeColumnsToContents()
            if self.ui.tableView_relationship_parameter_json.isVisible():
                return
            if not self.relationship_parameter_json_splitter_sizes:
                # Apply decent sizes
                sizes = splitter.sizes()
                width = self.ui.tableView_relationship_parameter_json.columnWidth(0)
                if sizes[1] < width:
                    sizes[0] = sum(sizes) - width
                    sizes[1] = width
                splitter.setSizes(sizes)
            else:
                # Apply stored sizes
                splitter.setSizes(self.relationship_parameter_json_splitter_sizes)
            self.ui.tableView_relationship_parameter_json.show()
        elif self.ui.tableView_relationship_parameter_json.isVisible():
            # Save sizes and hide
            self.relationship_parameter_json_splitter_sizes = splitter.sizes()
            self.ui.tableView_relationship_parameter_json.hide()

    @Slot(name="edit_object_parameter_json")
    def edit_object_parameter_json(self):
        """Start editing object parameter json."""
        index = self.object_parameter_json_model.index(0, 0)
        self.ui.tableView_object_parameter_json.scrollTo(index)
        self.ui.tableView_object_parameter_json.edit(index)

    @Slot(name="edit_relationship_parameter_json")
    def edit_relationship_parameter_json(self):
        """Start editing relationship parameter json."""
        index = self.relationship_parameter_json_model.index(0, 0)
        self.ui.tableView_relationship_parameter_json.scrollTo(index)
        self.ui.tableView_relationship_parameter_json.edit(index)

    @Slot("QItemSelection", "QItemSelection", name="handle_object_parameter_definition_selection_changed")
    def handle_object_parameter_definition_selection_changed(self, selected, deselected):
        """Enable/disable the option to remove rows."""
        selection = self.ui.tableView_object_parameter_definition.selectionModel().selection()
        tab_index = self.ui.tabWidget_object_parameter.currentIndex()
        self.ui.actionRemove_object_parameter_definitions.setEnabled(tab_index == 1 and not selection.isEmpty())

    @Slot("QItemSelection", "QItemSelection", name="handle_object_parameter_value_selection_changed")
    def handle_object_parameter_value_selection_changed(self, selected, deselected):
        """Enable/disable the option to remove rows."""
        selection = self.ui.tableView_object_parameter_value.selectionModel().selection()
        tab_index = self.ui.tabWidget_object_parameter.currentIndex()
        self.ui.actionRemove_object_parameter_values.setEnabled(tab_index == 0 and not selection.isEmpty())

    @Slot("QItemSelection", "QItemSelection", name="handle_relationship_parameter_definition_selection_changed")
    def handle_relationship_parameter_definition_selection_changed(self, selected, deselected):
        """Enable/disable the option to remove rows."""
        selection = self.ui.tableView_relationship_parameter_definition.selectionModel().selection()
        tab_index = self.ui.tabWidget_relationship_parameter.currentIndex()
        self.ui.actionRemove_relationship_parameter_definitions.setEnabled(tab_index == 1 and not selection.isEmpty())

    @Slot("QItemSelection", "QItemSelection", name="handle_relationship_parameter_value_selection_changed")
    def handle_relationship_parameter_value_selection_changed(self, selected, deselected):
        """Enable/disable the option to remove rows."""
        selection = self.ui.tableView_relationship_parameter_value.selectionModel().selection()
        tab_index = self.ui.tabWidget_relationship_parameter.currentIndex()
        self.ui.actionRemove_relationship_parameter_values.setEnabled(tab_index == 0 and not selection.isEmpty())

    @Slot("int", name="handle_object_parameter_tab_changed")
    def handle_object_parameter_tab_changed(self, index):
        """Apply filter. Enable/disable the option to remove rows."""
        if index == 0:
            self.object_parameter_value_proxy.apply_filter()
        else:
            self.object_parameter_definition_proxy.apply_filter()
        selected = self.ui.tableView_object_parameter_definition.selectionModel().selection()
        self.ui.actionRemove_object_parameter_definitions.setEnabled(index == 1 and not selected.isEmpty())
        selected = self.ui.tableView_object_parameter_value.selectionModel().selection()
        self.ui.actionRemove_object_parameter_values.setEnabled(index == 0 and not selected.isEmpty())

    @Slot("int", name="handle_relationship_parameter_tab_changed")
    def handle_relationship_parameter_tab_changed(self, index):
        """Apply filter. Enable/disable the option to remove rows."""
        if index == 0:
            self.relationship_parameter_value_proxy.apply_filter()
        else:
            self.relationship_parameter_definition_proxy.apply_filter()
        selected = self.ui.tableView_relationship_parameter_definition.selectionModel().selection()
        self.ui.actionRemove_relationship_parameter_definitions.setEnabled(index == 1 and not selected.isEmpty())
        selected = self.ui.tableView_relationship_parameter_value.selectionModel().selection()
        self.ui.actionRemove_relationship_parameter_values.setEnabled(index == 0 and not selected.isEmpty())

    @Slot(name="handle_menu_about_to_show")
    def handle_menu_about_to_show(self):
        """Called when a menu from the menubar is about to show.
        Adjust copy paste actions depending on which widget has the focus.
        Enable/disable actions to edit object tree items depending on selection.
        Enable/disable actions to remove object tree items depending on selection.
        """
        # Edit object tree item actions
        indexes = self.ui.treeView_object.selectionModel().selectedIndexes()
        item_types = {x.data(Qt.UserRole) for x in indexes}
        self.ui.actionEdit_object_classes.setEnabled('object_class' in item_types)
        self.ui.actionEdit_objects.setEnabled('object' in item_types)
        self.ui.actionEdit_relationship_classes.setEnabled('relationship_class' in item_types)
        self.ui.actionEdit_relationships.setEnabled('relationship' in item_types)
        # Remove object tree items action
        self.ui.actionRemove_object_tree_items.setEnabled(len(indexes) > 0)
        # Copy/paste actions
        if self.focusWidget() != self.ui.menubar:
            self.focus_widget = self.focusWidget()
        self.ui.actionCopy.setText("Copy")
        self.ui.actionPaste.setText("Paste")
        self.ui.actionCopy.setEnabled(False)
        self.ui.actionPaste.setEnabled(False)
        if self.focus_widget == self.ui.treeView_object:
            focus_widget_name = "object tree"
        elif self.focus_widget == self.ui.tableView_object_parameter_definition:
            focus_widget_name = "object parameter definition"
        elif self.focus_widget == self.ui.tableView_object_parameter_value:
            focus_widget_name = "object parameter value"
        elif self.focus_widget == self.ui.tableView_object_parameter_json:
            focus_widget_name = "object parameter json"
        elif self.focus_widget == self.ui.tableView_relationship_parameter_definition:
            focus_widget_name = "relationship parameter definition"
        elif self.focus_widget == self.ui.tableView_relationship_parameter_value:
            focus_widget_name = "relationship parameter value"
        elif self.focus_widget == self.ui.tableView_relationship_parameter_json:
            focus_widget_name = "relationship parameter json"
        else:
            return
        if not self.focus_widget.selectionModel().selection().isEmpty():
            self.ui.actionCopy.setText("Copy from {}".format(focus_widget_name))
            self.ui.actionCopy.setEnabled(True)
        if focus_widget_name != "object tree" and self.clipboard_text:
            self.ui.actionPaste.setText("Paste to {}".format(focus_widget_name))
            self.ui.actionPaste.setEnabled(True)

    @Slot("bool", name="show_import_file_dialog")
    def show_import_file_dialog(self, checked=False):
        """Show dialog to allow user to select a file to import."""
        answer = QFileDialog.getOpenFileName(
            self, "Select file to import", self._data_store.project().project_dir, "*.*")
        file_path = answer[0]
        if not file_path:  # Cancel button clicked
            return
        self.import_file(file_path)

    @busy_effect
    def import_file(self, file_path, checked=False):
        """Import data from file into current database."""
        if file_path.lower().endswith('datapackage.json'):
            try:
                import_datapackage(self, file_path)
                self.init_parameter_value_models()
                self.init_parameter_definition_models()
                self.msg.emit("Datapackage successfully imported.")
            except SpineDBAPIError as e:
                self.msg_error.emit("Unable to import datapackage: {}.".format(e.msg))
        elif file_path.lower().endswith('xlsx'):
            error_log = []
            try:
                insert_log, error_log = import_xlsx_to_db(self.db_map, file_path)
                self.msg.emit("Excel file successfully imported.")
                self.set_commit_rollback_actions_enabled(True)
                # logging.debug(insert_log)
                self.init_models()
            except SpineIntegrityError as e:
                self.msg_error.emit(e.msg)
            except SpineDBAPIError as e:
                self.msg_error.emit("Unable to import Excel file: {}".format(e.msg))
            finally:
                if not len(error_log) == 0:
                    msg = "Something went wrong in importing an Excel file " \
                          "into the current session. Here is the error log:\n\n{0}".format(error_log)
                    # noinspection PyTypeChecker, PyArgumentList, PyCallByClass
                    QMessageBox.information(self, "Excel import may have failed", msg)
                    # logging.debug(error_log)

    @Slot("bool", name="show_export_file_dialog")
    def show_export_file_dialog(self, checked=False):
        """Show dialog to allow user to select a file to export."""
        answer = QFileDialog.getSaveFileName(self,
                                             "Export to file",
                                             self._data_store.project().project_dir,
                                             "Excel file (*.xlsx);;SQlite database (*.sqlite *.db)")
        file_path = answer[0]
        if not file_path:  # Cancel button clicked
            return
        if answer[1].startswith("SQlite"):
            self.export_to_sqlite(file_path)
        elif answer[1].startswith("Excel"):
            self.export_to_excel(file_path)

    @busy_effect
    def export_to_excel(self, file_path):
        """Export data from database into Excel file."""
        filename = os.path.split(file_path)[1]
        try:
            export_spine_database_to_xlsx(self.db_map, file_path)
            self.msg.emit("Excel file successfully exported.")
        except PermissionError:
            self.msg_error.emit("Unable to export to file <b>{0}</b>.<br/>"
                                "Close the file in Excel and try again.".format(filename))
        except OSError:
            self.msg_error.emit("[OSError] Unable to export to file <b>{0}</b>".format(filename))

    @busy_effect
    def export_to_sqlite(self, file_path):
        """Export data from database into SQlite file."""
        # Remove file if exists (at this point, the user has confirmed that overwritting is ok)
        try:
            os.remove(file_path)
        except OSError:
            pass
        dst_url = 'sqlite:///{0}'.format(file_path)
        copy_database(dst_url, self.db_map.db_url)
        self.msg.emit("SQlite file successfully exported.")

    def init_object_tree_model(self):
        """Initialize object tree model."""
        self.object_tree_model.build_tree(self.database)
        self.ui.actionExport.setEnabled(self.object_tree_model.root_item.hasChildren())

    def init_views(self):
        """Initialize model views."""
        super().init_views()
        self.init_parameter_json_views()

    def init_parameter_json_views(self):
        """Init object and relationship parameter json views."""
        self.ui.tableView_object_parameter_json.setModel(self.object_parameter_json_model)
        self.ui.tableView_object_parameter_json.hide()
        self.ui.tableView_object_parameter_json.verticalHeader().setDefaultSectionSize(self.default_row_height)
        self.ui.tableView_object_parameter_json.horizontalHeader().setResizeContentsPrecision(self.visible_rows)
        self.ui.tableView_relationship_parameter_json.setModel(self.relationship_parameter_json_model)
        self.ui.tableView_relationship_parameter_json.hide()
        self.ui.tableView_relationship_parameter_json.verticalHeader().setDefaultSectionSize(self.default_row_height)
        self.ui.tableView_relationship_parameter_json.horizontalHeader().setResizeContentsPrecision(self.visible_rows)

    @Slot("QModelIndex", "QModelIndex", "QVector", name="handle_object_parameter_json_data_changed")
    def handle_object_parameter_json_data_changed(self, top_left, bottom_right, roles=[]):
        """Called when the user edits the object parameter json table.
        Set json field in object parameter value table."""
        if Qt.EditRole not in roles:
            return
        json = self.object_parameter_json_model.json()
        index = self.ui.tableView_object_parameter_value.currentIndex()
        self.set_parameter_value_data(index, json)

    @Slot("QModelIndex", "QModelIndex", "QVector", name="handle_relationship_parameter_json_data_changed")
    def handle_relationship_parameter_json_data_changed(self, top_left, bottom_right, roles=[]):
        """Called when the user edits the relationship parameter json table.
        Set json field in relationship parameter value table."""
        if Qt.EditRole not in roles:
            return
        json = self.relationship_parameter_json_model.json()
        index = self.ui.tableView_relationship_parameter_value.currentIndex()
        self.set_parameter_value_data(index, json)

    @Slot("QModelIndex", name="find_next_leaf")
    def find_next_leaf(self, index):
        """If index corresponds to a relationship, then expand the next ocurrence of it."""
        if not index.isValid():
            return # just to be safe
        clicked_type = index.data(Qt.UserRole)
        if not clicked_type:  # root item
            return
        if not clicked_type == 'relationship':
            return
        clicked_item = index.model().itemFromIndex(index)
        if clicked_item.hasChildren():
            return
        self.find_next(index)

    def find_next(self, index):
        """Expand next occurrence of a relationship."""
        next_index = self.object_tree_model.next_relationship_index(index)
        if not next_index:
            return
        self.ui.treeView_object.setCurrentIndex(next_index)
        self.ui.treeView_object.scrollTo(next_index)
        self.ui.treeView_object.expand(next_index)

    @Slot("QItemSelection", "QItemSelection", name="handle_object_tree_selection_changed")
    def handle_object_tree_selection_changed(self, selected, deselected):
        """Called when the object tree selection changes.
        Set default rows and apply filters on parameter models."""
        self.set_default_parameter_rows()
        self.update_and_apply_filter(selected, deselected)

    def set_default_parameter_rows(self):
        """Set default rows for parameter models according to selection in object tree."""
        selection = tree_selection = self.ui.treeView_object.selectionModel().selection()
        if selection.count() != 1:
            return
        index = selection.indexes()[0]
        item_type = index.data(Qt.UserRole)
        if item_type == 'object_class':
            default_row = dict(
                object_class_id=index.data(Qt.UserRole + 1)['id'],
                object_class_name=index.data(Qt.UserRole + 1)['name'])
            for model in (self.object_parameter_definition_model, self.object_parameter_value_model):
                model.set_default_row(**default_row)
                model.set_rows_to_default(model.rowCount() - 1, model.rowCount() - 1)
        elif item_type == 'object':
            default_row = dict(
                object_class_id=index.parent().data(Qt.UserRole + 1)['id'],
                object_class_name=index.parent().data(Qt.UserRole + 1)['name'])
            self.object_parameter_definition_model.set_default_row(**default_row)
            last_row = self.object_parameter_definition_model.rowCount() - 1
            self.object_parameter_definition_model.set_rows_to_default(last_row, last_row)
            default_row.update(dict(
                object_id=index.data(Qt.UserRole + 1)['id'],
                object_name=index.data(Qt.UserRole + 1)['name']))
            self.object_parameter_value_model.set_default_row(**default_row)
            last_row = self.object_parameter_value_model.rowCount() - 1
            self.object_parameter_value_model.set_rows_to_default(last_row, last_row)
        elif item_type == 'relationship_class':
            default_row = dict(
                relationship_class_id=index.data(Qt.UserRole + 1)['id'],
                relationship_class_name=index.data(Qt.UserRole + 1)['name'],
                object_class_id_list=index.data(Qt.UserRole + 1)['object_class_id_list'],
                object_class_name_list=index.data(Qt.UserRole + 1)['object_class_name_list'])
            for model in (self.relationship_parameter_definition_model, self.relationship_parameter_value_model):
                model.set_default_row(**default_row)
                model.set_rows_to_default(model.rowCount() - 1, model.rowCount() - 1)
        elif item_type == 'relationship':
            default_row = dict(
                relationship_class_id=index.parent().data(Qt.UserRole + 1)['id'],
                relationship_class_name=index.parent().data(Qt.UserRole + 1)['name'],
                object_class_id_list=index.parent().data(Qt.UserRole + 1)['object_class_id_list'],
                object_class_name_list=index.parent().data(Qt.UserRole + 1)['object_class_name_list'])
            self.relationship_parameter_definition_model.set_default_row(**default_row)
            last_row = self.relationship_parameter_definition_model.rowCount() - 1
            self.relationship_parameter_definition_model.set_rows_to_default(last_row, last_row)
            default_row.update(dict(
                relationship_id=index.data(Qt.UserRole + 1)['id'],
                object_id_list=index.data(Qt.UserRole + 1)['object_id_list'],
                object_name_list=index.data(Qt.UserRole + 1)['object_name_list']))
            self.relationship_parameter_value_model.set_default_row(**default_row)
            last_row = self.relationship_parameter_value_model.rowCount() - 1
            self.relationship_parameter_value_model.set_rows_to_default(last_row, last_row)
        elif item_type == 'root':
            default_row = dict()
            for model in (self.object_parameter_definition_model, self.object_parameter_value_model,
                          self.relationship_parameter_definition_model, self.relationship_parameter_value_model):
                model.set_default_row(**default_row)
                model.set_rows_to_default(model.rowCount() - 1, model.rowCount() - 1)

    def update_and_apply_filter(self, selected, deselected):
        """Apply filters on parameter models according to selected and deselected object tree indexes."""
        selected_object_class_ids = set()
        selected_object_ids = set()
        selected_relationship_class_ids = set()
        selected_object_id_lists = set()
        deselected_object_class_ids = set()
        deselected_object_ids = set()
        deselected_relationship_class_ids = set()
        deselected_object_id_lists = set()
        for index in deselected.indexes():
            item_type = index.data(Qt.UserRole)
            item = index.data(Qt.UserRole + 1)
            if item_type == 'object_class':
                deselected_object_class_ids.add(item['id'])
            elif item_type == 'object':
                deselected_object_ids.add(item['id'])
            elif item_type == 'relationship_class':
                deselected_relationship_class_ids.add(item['id'])
            elif item_type == 'relationship':
                deselected_object_id_lists.add(item['object_id_list'])
        self.object_parameter_definition_proxy.diff_update_object_class_id_set(deselected_object_class_ids)
        self.object_parameter_value_proxy.diff_update_object_class_id_set(deselected_object_class_ids)
        self.object_parameter_value_proxy.diff_update_object_id_set(deselected_object_ids)
        self.relationship_parameter_definition_proxy.\
            diff_update_relationship_class_id_set(deselected_relationship_class_ids)
        self.relationship_parameter_definition_proxy.diff_update_object_class_id_set(deselected_object_class_ids)
        self.relationship_parameter_value_proxy.diff_update_relationship_class_id_set(
            deselected_relationship_class_ids)
        self.relationship_parameter_value_proxy.diff_update_object_class_id_set(deselected_object_class_ids)
        self.relationship_parameter_value_proxy.diff_update_object_id_set(deselected_object_ids)
        self.relationship_parameter_value_proxy.diff_update_object_id_list_set(deselected_object_id_lists)
        for index in selected.indexes():
            item_type = index.data(Qt.UserRole)
            item = index.data(Qt.UserRole + 1)
            if item_type == 'object_class':
                selected_object_class_ids.add(item['id'])
            elif item_type == 'object':
                selected_object_ids.add(item['id'])
            elif item_type == 'relationship_class':
                selected_relationship_class_ids.add(item['id'])
            elif item_type == 'relationship':
                selected_object_id_lists.add(item['object_id_list'])
        self.object_parameter_definition_proxy.update_object_class_id_set(selected_object_class_ids)
        self.object_parameter_value_proxy.update_object_class_id_set(selected_object_class_ids)
        self.object_parameter_value_proxy.update_object_id_set(selected_object_ids)
        self.relationship_parameter_definition_proxy.update_relationship_class_id_set(selected_relationship_class_ids)
        self.relationship_parameter_definition_proxy.update_object_class_id_set(selected_object_class_ids)
        self.relationship_parameter_value_proxy.update_relationship_class_id_set(selected_relationship_class_ids)
        self.relationship_parameter_value_proxy.update_object_class_id_set(selected_object_class_ids)
        self.relationship_parameter_value_proxy.update_object_id_set(selected_object_ids)
        self.relationship_parameter_value_proxy.update_object_id_list_set(selected_object_id_lists)
        if self.ui.tabWidget_object_parameter.currentIndex() == 0:
            self.object_parameter_value_proxy.apply_filter()
        else:
            self.object_parameter_definition_proxy.apply_filter()
        if self.ui.tabWidget_relationship_parameter.currentIndex() == 0:
            self.relationship_parameter_value_proxy.apply_filter()
        else:
            self.relationship_parameter_definition_proxy.apply_filter()

    @Slot("QObject", "int", "QStringList", name="apply_autofilter")
    def apply_autofilter(self, proxy_model, column, text_list):
        """Called when the tableview wants to trigger the autofilter."""
        header = proxy_model.sourceModel().horizontal_header_labels()
        kwargs = {header[column]: text_list}
        proxy_model.add_rule(**kwargs)
        proxy_model.apply_filter()

    @Slot("QPoint", name="show_object_tree_context_menu")
    def show_object_tree_context_menu(self, pos):
        """Context menu for object tree.

        Args:
            pos (QPoint): Mouse position
        """
        index = self.ui.treeView_object.indexAt(pos)
        global_pos = self.ui.treeView_object.viewport().mapToGlobal(pos)
        self.object_tree_context_menu = ObjectTreeContextMenu(self, global_pos, index)
        option = self.object_tree_context_menu.get_action()
        if option == "Copy":
            self.ui.treeView_object.copy()
        elif option == "Add object classes":
            self.show_add_object_classes_form()
        elif option == "Add objects":
            self.call_show_add_objects_form(index)
        elif option == "Add relationship classes":
            self.call_show_add_relationship_classes_form(index)
        elif option == "Add relationships":
            self.call_show_add_relationships_form(index)
        elif option == "Edit object classes":
            self.show_edit_object_classes_form()
        elif option == "Edit objects":
            self.show_edit_objects_form()
        elif option == "Edit relationship classes":
            self.show_edit_relationship_classes_form()
        elif option == "Edit relationships":
            self.show_edit_relationships_form()
        elif option == "Find next":
            self.find_next(index)
        elif option.startswith("Remove selected"):
            self.remove_object_tree_items()
        elif option == "Add parameter definitions":
            self.call_add_parameters(index)
        elif option == "Add parameter values":
            self.call_add_parameter_values(index)
        elif option == "Fully expand":
            self.fully_expand_selection()
        elif option == "Fully collapse":
            self.fully_collapse_selection()
        else:  # No option selected
            pass
        self.object_tree_context_menu.deleteLater()
        self.object_tree_context_menu = None

    def fully_expand_selection(self):
        for index in self.ui.treeView_object.selectionModel().selectedIndexes():
            self.object_tree_model.forward_sweep(index, call=self.ui.treeView_object.expand)

    def fully_collapse_selection(self):
        for index in self.ui.treeView_object.selectionModel().selectedIndexes():
            self.object_tree_model.forward_sweep(index, call=self.ui.treeView_object.collapse)

    def call_show_add_objects_form(self, index):
        class_id = index.data(Qt.UserRole + 1)['id']
        self.show_add_objects_form(class_id=class_id)

    def call_show_add_relationship_classes_form(self, index):
        object_class_id = index.data(Qt.UserRole + 1)['id']
        self.show_add_relationship_classes_form(object_class_id=object_class_id)

    def call_show_add_relationships_form(self, index):
        relationship_class = index.data(Qt.UserRole + 1)
        object_ = index.parent().data(Qt.UserRole + 1)
        object_class = index.parent().parent().data(Qt.UserRole + 1)
        self.show_add_relationships_form(
            relationship_class_id=relationship_class['id'],
            object_id=object_['id'],
            object_class_id=object_class['id'])

    def call_add_parameters(self, tree_index):
        class_type = tree_index.data(Qt.UserRole)
        if class_type == 'object_class':
            self.add_object_parameter_definitions()
        elif class_type == 'relationship_class':
            self.add_relationship_parameter_definitions()

    def call_add_parameter_values(self, tree_index):
        entity_type = tree_index.data(Qt.UserRole)
        if entity_type == 'object':
            self.add_object_parameter_values()
        elif entity_type == 'relationship':
            self.add_relationship_parameter_values()

    def add_object_classes(self, object_classes):
        """Insert new object classes."""
        super().add_object_classes(object_classes)
        self.ui.actionExport.setEnabled(True)

    def edit_object_tree_items(self):
        """Called when F2 is pressed while the object tree has focus.
        Call the appropriate method to show the edit form,
        depending on the current index."""
        current = self.ui.treeView_object.currentIndex()
        current_type = current.data(Qt.UserRole)
        if current_type == 'object_class':
            self.show_edit_object_classes_form()
        elif current_type == 'object':
            self.show_edit_objects_form()
        elif current_type == 'relationship_class':
            self.show_edit_relationship_classes_form()
        elif current_type == 'relationship':
            self.show_edit_relationships_form()

    @busy_effect
    @Slot("bool", name="remove_object_tree_items")
    def remove_object_tree_items(self, checked=False):
        """Remove all selected items from the object treeview."""
        indexes = self.ui.treeView_object.selectionModel().selectedIndexes()
        if not indexes:
            return
        removed_id_dict = {}
        for index in indexes:
            removed_type = index.data(Qt.UserRole)
            removed_id = index.data(Qt.UserRole + 1)['id']
            removed_id_dict.setdefault(removed_type, set()).add(removed_id)
        try:
            self.db_map.remove_items(**{k + "_ids": v for k, v in removed_id_dict.items()})  # FIXME: this is ugly
            for key, value in removed_id_dict.items():
                self.object_tree_model.remove_items(key, *value)
            for key, value in removed_id_dict.items():
                self.object_parameter_definition_model.remove_items(key, *value)
                self.object_parameter_value_model.remove_items(key, *value)
                self.relationship_parameter_definition_model.remove_items(key, *value)
                self.relationship_parameter_value_model.remove_items(key, *value)
            self.set_commit_rollback_actions_enabled(True)
            self.ui.actionExport.setEnabled(self.object_tree_model.root_item.hasChildren())
            self.msg.emit("Successfully removed items.")
        except SpineDBAPIError as e:
            self.msg_error.emit(e.msg)

    @Slot("QPoint", name="show_object_parameter_value_context_menu")
    def show_object_parameter_value_context_menu(self, pos):
        """Context menu for object parameter value table view.

        Args:
            pos (QPoint): Mouse position
        """
        index = self.ui.tableView_object_parameter_value.indexAt(pos)
        global_pos = self.ui.tableView_object_parameter_value.viewport().mapToGlobal(pos)
        remove_icon = self.ui.actionRemove_object_parameter_values.icon()
        self.object_parameter_value_context_menu = ParameterContextMenu(self, global_pos, index, remove_icon)
        option = self.object_parameter_value_context_menu.get_action()
        if option == "Remove selected":
            self.remove_object_parameter_values()
        elif option == "Copy":
            self.ui.tableView_object_parameter_value.copy()
        elif option == "Paste":
            self.ui.tableView_object_parameter_value.paste(self.clipboard_text)
        self.object_parameter_value_context_menu.deleteLater()
        self.object_parameter_value_context_menu = None

    @Slot("QPoint", name="show_relationship_parameter_value_context_menu")
    def show_relationship_parameter_value_context_menu(self, pos):
        """Context menu for relationship parameter value table view.

        Args:
            pos (QPoint): Mouse position
        """
        index = self.ui.tableView_relationship_parameter_value.indexAt(pos)
        global_pos = self.ui.tableView_relationship_parameter_value.viewport().mapToGlobal(pos)
        remove_icon = self.ui.actionRemove_relationship_parameter_values.icon()
        self.relationship_parameter_value_context_menu = ParameterContextMenu(self, global_pos, index, remove_icon)
        option = self.relationship_parameter_value_context_menu.get_action()
        if option == "Remove selected":
            self.remove_relationship_parameter_values()
        elif option == "Copy":
            self.ui.tableView_relationship_parameter_value.copy()
        elif option == "Paste":
            self.ui.tableView_relationship_parameter_value.paste(self.clipboard_text)
        self.relationship_parameter_value_context_menu.deleteLater()
        self.relationship_parameter_value_context_menu = None

    @Slot("QPoint", name="show_object_parameter_context_menu")
    def show_object_parameter_context_menu(self, pos):
        """Context menu for object parameter table view.

        Args:
            pos (QPoint): Mouse position
        """
        index = self.ui.tableView_object_parameter_definition.indexAt(pos)
        global_pos = self.ui.tableView_object_parameter_definition.viewport().mapToGlobal(pos)
        remove_icon = self.ui.actionRemove_object_parameter_definitions.icon()
        self.object_parameter_context_menu = ParameterContextMenu(self, global_pos, index, remove_icon)
        option = self.object_parameter_context_menu.get_action()
        if option == "Remove selected":
            self.remove_object_parameter_definitions()
        elif option == "Copy":
            self.ui.tableView_object_parameter_definition.copy()
        elif option == "Paste":
            self.ui.tableView_object_parameter_definition.paste(self.clipboard_text)
        self.object_parameter_context_menu.deleteLater()
        self.object_parameter_context_menu = None

    @Slot("QPoint", name="show_relationship_parameter_context_menu")
    def show_relationship_parameter_context_menu(self, pos):
        """Context menu for relationship parameter table view.

        Args:
            pos (QPoint): Mouse position
        """
        index = self.ui.tableView_relationship_parameter_definition.indexAt(pos)
        global_pos = self.ui.tableView_relationship_parameter_definition.viewport().mapToGlobal(pos)
        remove_icon = self.ui.actionRemove_relationship_parameter_definitions.icon()
        self.relationship_parameter_context_menu = ParameterContextMenu(self, global_pos, index, remove_icon)
        option = self.relationship_parameter_context_menu.get_action()
        if option == "Remove selected":
            self.remove_relationship_parameter_definitions()
        elif option == "Copy":
            self.ui.tableView_relationship_parameter_definition.copy()
        elif option == "Paste":
            self.ui.tableView_relationship_parameter_definition.paste(self.clipboard_text)
        self.relationship_parameter_context_menu.deleteLater()
        self.relationship_parameter_context_menu = None

    @Slot(name="add_object_parameter_values")
    def add_object_parameter_values(self):
        """Sweep object treeview selection.
        For each item in the selection, add a parameter value row if needed.
        """
        model = self.object_parameter_value_model
        proxy_index = self.ui.tableView_object_parameter_value.currentIndex()
        index = self.object_parameter_value_proxy.mapToSource(proxy_index)
        row = model.rowCount() - 1
        tree_selection = self.ui.treeView_object.selectionModel().selection()
        if not tree_selection.isEmpty():
            object_class_name_column = model.horizontal_header_labels().index('object_class_name')
            object_name_column = model.horizontal_header_labels().index('object_name')
            row_column_tuples = list()
            data = list()
            i = 0
            for tree_index in tree_selection.indexes():
                if tree_index.data(Qt.UserRole) == 'object_class':
                    object_class_name = tree_index.data(Qt.DisplayRole)
                    object_name = None
                elif tree_index.data(Qt.UserRole) == 'object':
                    object_class_name = tree_index.parent().data(Qt.DisplayRole)
                    object_name = tree_index.data(Qt.DisplayRole)
                else:
                    continue
                row_column_tuples.append((row + i, object_class_name_column))
                row_column_tuples.append((row + i, object_name_column))
                data.extend([object_class_name, object_name])
                i += 1
            if i > 0:
                model.insertRows(row, i)
                indexes = [model.index(row, column) for row, column in row_column_tuples]
                model.batch_set_data(indexes, data)
        self.ui.tabWidget_object_parameter.setCurrentIndex(0)
        self.object_parameter_value_proxy.apply_filter()

    @Slot(name="add_relationship_parameter_values")
    def add_relationship_parameter_values(self):
        """Sweep object treeview selection.
        For each item in the selection, add a parameter value row if needed.
        """
        model = self.relationship_parameter_value_model
        proxy_index = self.ui.tableView_relationship_parameter_value.currentIndex()
        index = self.relationship_parameter_value_proxy.mapToSource(proxy_index)
        row = model.rowCount() - 1
        tree_selection = self.ui.treeView_object.selectionModel().selection()
        if not tree_selection.isEmpty():
            relationship_class_name_column = model.horizontal_header_labels().index('relationship_class_name')
            object_name_list_column = model.horizontal_header_labels().index('object_name_list')
            row_column_tuples = list()
            data = list()
            i = 0
            for tree_index in tree_selection.indexes():
                if tree_index.data(Qt.UserRole) == 'relationship_class':
                    selected_object_class_name = tree_index.parent().parent().data(Qt.DisplayRole)
                    object_name = tree_index.parent().data(Qt.DisplayRole)
                    relationship_class_name = tree_index.data(Qt.DisplayRole)
                    object_class_name_list = tree_index.data(Qt.UserRole + 1)["object_class_name_list"].split(",")
                    object_name_list = list()
                    for object_class_name in object_class_name_list:
                        if object_class_name == selected_object_class_name:
                            object_name_list.append(object_name)
                        else:
                            object_name_list.append('')
                elif tree_index.data(Qt.UserRole) == 'relationship':
                    relationship_class_name = tree_index.parent().data(Qt.DisplayRole)
                    object_name_list = tree_index.data(Qt.UserRole + 1)["object_name_list"].split(",")
                else:
                    continue
                row_column_tuples.append((row + i, relationship_class_name_column))
                data.append(relationship_class_name)
                row_column_tuples.append((row + i, object_name_list_column))
                data.append(",".join(object_name_list))
                i += 1
            if i > 0:
                model.insertRows(row, i)
                indexes = [model.index(row, column) for row, column in row_column_tuples]
                model.batch_set_data(indexes, data)
        self.ui.tabWidget_relationship_parameter.setCurrentIndex(0)
        self.relationship_parameter_value_proxy.apply_filter()

    @Slot(name="add_object_parameter_definitions")
    def add_object_parameter_definitions(self):
        """Sweep object treeview selection.
        For each item in the selection, add a parameter value row if needed.
        """
        model = self.object_parameter_definition_model
        proxy_index = self.ui.tableView_object_parameter_definition.currentIndex()
        index = self.object_parameter_definition_proxy.mapToSource(proxy_index)
        row = model.rowCount() - 1
        tree_selection = self.ui.treeView_object.selectionModel().selection()
        if not tree_selection.isEmpty():
            object_class_name_column = model.horizontal_header_labels().index('object_class_name')
            row_column_tuples = list()
            data = list()
            i = 0
            for tree_index in tree_selection.indexes():
                if tree_index.data(Qt.UserRole) == 'object_class':
                    object_class_name = tree_index.data(Qt.DisplayRole)
                elif tree_index.data(Qt.UserRole) == 'object':
                    object_class_name = tree_index.parent().data(Qt.DisplayRole)
                else:
                    continue
                row_column_tuples.append((row + i, object_class_name_column))
                data.append(object_class_name)
                i += 1
            if i > 0:
                model.insertRows(row, i)
                indexes = [model.index(row, column) for row, column in row_column_tuples]
                model.batch_set_data(indexes, data)
        self.ui.tabWidget_object_parameter.setCurrentIndex(1)
        self.object_parameter_definition_proxy.apply_filter()

    @Slot(name="add_relationship_parameter_definitions")
    def add_relationship_parameter_definitions(self):
        """Sweep object treeview selection.
        For each item in the selection, add a parameter row if needed.
        """
        model = self.relationship_parameter_definition_model
        proxy_index = self.ui.tableView_relationship_parameter_definition.currentIndex()
        index = self.relationship_parameter_definition_proxy.mapToSource(proxy_index)
        row = model.rowCount() - 1
        tree_selection = self.ui.treeView_object.selectionModel().selection()
        if not tree_selection.isEmpty():
            relationship_class_name_column = model.horizontal_header_labels().index('relationship_class_name')
            row_column_tuples = list()
            data = list()
            i = 0
            for tree_index in tree_selection.indexes():
                if tree_index.data(Qt.UserRole) == 'relationship_class':
                    relationship_class_name = tree_index.data(Qt.DisplayRole)
                elif tree_index.data(Qt.UserRole) == 'relationship':
                    relationship_class_name = tree_index.parent().data(Qt.DisplayRole)
                else:
                    continue
                row_column_tuples.append((row + i, relationship_class_name_column))
                data.append(relationship_class_name)
                i += 1
            if i > 0:
                model.insertRows(row, i)
                indexes = [model.index(row, column) for row, column in row_column_tuples]
                model.batch_set_data(indexes, data)
        self.ui.tabWidget_relationship_parameter.setCurrentIndex(1)
        self.relationship_parameter_definition_proxy.apply_filter()

    @busy_effect
    @Slot(name="remove_object_parameter_values")
    def remove_object_parameter_values(self):
        selection = self.ui.tableView_object_parameter_value.selectionModel().selection()
        source_row_set = self.source_row_set(selection, self.object_parameter_value_proxy)
        parameter_value_ids = set()
        id_column = self.object_parameter_value_model.horizontal_header_labels().index("id")
        for source_row in source_row_set:
            if self.object_parameter_value_model.is_work_in_progress(source_row):
                continue
            source_index = self.object_parameter_value_model.index(source_row, id_column)
            parameter_value_ids.add(source_index.data(Qt.EditRole))
        try:
            self.db_map.remove_items(parameter_value_ids=parameter_value_ids)
            self.object_parameter_value_model.remove_row_set(source_row_set)
            self.set_commit_rollback_actions_enabled(True)
            self.msg.emit("Successfully removed parameter vales.")
        except SpineDBAPIError as e:
            self.msg_error.emit(e.msg)

    @busy_effect
    @Slot(name="remove_relationship_parameter_values")
    def remove_relationship_parameter_values(self):
        selection = self.ui.tableView_relationship_parameter_value.selectionModel().selection()
        source_row_set = self.source_row_set(selection, self.relationship_parameter_value_proxy)
        parameter_value_ids = set()
        id_column = self.relationship_parameter_value_model.horizontal_header_labels().index("id")
        for source_row in source_row_set:
            if self.relationship_parameter_value_model.is_work_in_progress(source_row):
                continue
            source_index = self.relationship_parameter_value_model.index(source_row, id_column)
            parameter_value_ids.add(source_index.data(Qt.EditRole))
        try:
            self.db_map.remove_items(parameter_value_ids=parameter_value_ids)
            self.relationship_parameter_value_model.remove_row_set(source_row_set)
            self.set_commit_rollback_actions_enabled(True)
            self.msg.emit("Successfully removed parameter vales.")
        except SpineDBAPIError as e:
            self.msg_error.emit(e.msg)

    @busy_effect
    @Slot("bool", name="remove_object_parameter_definitions")
    def remove_object_parameter_definitions(self, checked=False):
        selection = self.ui.tableView_object_parameter_definition.selectionModel().selection()
        source_row_set = self.source_row_set(selection, self.object_parameter_definition_proxy)
        parameter_ids = set()
        id_column = self.object_parameter_definition_model.horizontal_header_labels().index("id")
        for source_row in source_row_set:
            if self.object_parameter_definition_model.is_work_in_progress(source_row):
                continue
            source_index = self.object_parameter_definition_model.index(source_row, id_column)
            parameter_ids.add(source_index.data(Qt.EditRole))
        try:
            self.db_map.remove_items(parameter_ids=parameter_ids)
            self.object_parameter_definition_model.remove_row_set(source_row_set)
            self.object_parameter_value_model.remove_items("parameter", *parameter_ids)
            self.set_commit_rollback_actions_enabled(True)
            self.msg.emit("Successfully removed parameters.")
        except SpineDBAPIError as e:
            self.msg_error.emit(e.msg)

    @busy_effect
    @Slot("bool", name="remove_relationship_parameter_definitions")
    def remove_relationship_parameter_definitions(self, checked=False):
        selection = self.ui.tableView_relationship_parameter_definition.selectionModel().selection()
        source_row_set = self.source_row_set(selection, self.relationship_parameter_definition_proxy)
        parameter_ids = set()
        id_column = self.relationship_parameter_definition_model.horizontal_header_labels().index("id")
        for source_row in source_row_set:
            if self.relationship_parameter_definition_model.is_work_in_progress(source_row):
                continue
            source_index = self.relationship_parameter_definition_model.index(source_row, id_column)
            parameter_ids.add(source_index.data(Qt.EditRole))
        try:
            self.db_map.remove_items(parameter_ids=parameter_ids)
            self.relationship_parameter_definition_model.remove_row_set(source_row_set)
            self.relationship_parameter_value_model.remove_items("parameter", *parameter_ids)
            self.set_commit_rollback_actions_enabled(True)
            self.msg.emit("Successfully removed parameters.")
        except SpineDBAPIError as e:
            self.msg_error.emit(e.msg)

    def source_row_set(self, selection, proxy_model):
        """A set of source rows corresponding to a selection of proxy indexes
        from any of the following models:
        object_parameter_definition_model, relationship_parameter_definition_model,
        object_parameter_value_model, relationship_parameter_value_model
        """
        if selection.isEmpty():
            return {}
        proxy_row_set = set()
        while not selection.isEmpty():
            current = selection.takeFirst()
            top = current.top()
            bottom = current.bottom()
            proxy_row_set.update(range(top, bottom + 1))
        return {proxy_model.map_row_to_source(r) for r in proxy_row_set}

    def restore_ui(self):
        """Restore UI state from previous session."""
        super().restore_ui()
        splitter_tree_parameter_state = self.qsettings.value("treeViewWidget/splitterTreeParameterState")
        if splitter_tree_parameter_state:
            self.ui.splitter_tree_parameter.restoreState(splitter_tree_parameter_state)

    def close_editors(self):
        """Close any open editor in the parameter table views.
        Call this before closing the database mapping."""
        current = self.ui.tableView_object_parameter_definition.currentIndex()
        if self.ui.tableView_object_parameter_definition.isPersistentEditorOpen(current):
            self.ui.tableView_object_parameter_definition.closePersistentEditor(current)
        current = self.ui.tableView_object_parameter_value.currentIndex()
        if self.ui.tableView_object_parameter_value.isPersistentEditorOpen(current):
            self.ui.tableView_object_parameter_value.closePersistentEditor(current)
        current = self.ui.tableView_relationship_parameter_definition.currentIndex()
        if self.ui.tableView_relationship_parameter_definition.isPersistentEditorOpen(current):
            self.ui.tableView_relationship_parameter_definition.closePersistentEditor(current)
        current = self.ui.tableView_relationship_parameter_value.currentIndex()
        if self.ui.tableView_relationship_parameter_value.isPersistentEditorOpen(current):
            self.ui.tableView_relationship_parameter_value.closePersistentEditor(current)

    def closeEvent(self, event=None):
        """Handle close window.

        Args:
            event (QEvent): Closing event if 'X' is clicked.
        """
        super().closeEvent(event)
        self.qsettings.setValue(
            "{}/splitterTreeParameterState".format(self.settings_key),
            self.ui.splitter_tree_parameter.saveState())
        self.close_editors()


class GraphViewForm(DataStoreForm):
    """A widget to show the graph view.

    Attributes:
        owner (View or Data Store): View or DataStore instance
        db_map (DiffDatabaseMapping): The object relational database mapping
        database (str): The database name
        read_only (bool): Whether or not the form should be editable
    """
    def __init__(self, owner, db_map, database, read_only=False):
        """Initialize class."""
        tic = time.clock()
        super().__init__(owner, db_map, database, graph_view_form_ui())
        self.ui.graphicsView._graph_view_form = self
        self.read_only = read_only
        self._has_graph = False
        self._scene_bg = None
        self.font = QApplication.font()
        self.font.setPointSize(72)
        self.font_metric = QFontMetrics(self.font)
        self.extent = 6 * self.font.pointSize()
        self._spread = 3 * self.extent
        self.object_label_color = self.palette().color(QPalette.Normal, QPalette.Window)
        self.object_label_color.setAlphaF(.5)
        self.arc_label_color = self.palette().color(QPalette.Normal, QPalette.Window)
        self.arc_label_color.setAlphaF(.8)
        self.arc_color = self.palette().color(QPalette.Normal, QPalette.WindowText)
        self.arc_color.setAlphaF(.75)
        # Set flat object tree
        self.object_tree_model.is_flat = True
        # Data for ObjectItems
        self.object_ids = list()
        self.object_names = list()
        self.object_class_ids = list()
        self.object_class_names = list()
        # Data for ArcItems
        self.arc_object_id_lists = list()
        self.arc_relationship_class_ids = list()
        self.arc_object_class_name_lists = list()
        self.arc_label_object_name_lists = list()
        self.arc_label_object_class_name_lists = list()
        self.src_ind_list = list()
        self.dst_ind_list = list()
        # Data for template ObjectItems and ArcItems (these are persisted across graph builds)
        self.heavy_positions = {}
        self.is_template = {}
        self.template_id_dims = {}
        self.arc_template_ids = {}
        # Data of relationship templates
        self.template_id = 1
        self.relationship_class_dict = {}  # template_id => relationship_class_name, relationship_class_id
        # Icon dicts
        self.object_class_list_model = ObjectClassListModel(self)
        self.relationship_class_list_model = RelationshipClassListModel(self)
        # Contex menus
        self.object_item_context_menu = None
        self.graph_view_context_menu = None
        # Hidden and rejected items
        self.hidden_items = list()
        self.rejected_items = list()
        # Current item selection
        self.object_item_selection = list()
        self.arc_item_selection = list()
        # Set up splitters
        area = self.dockWidgetArea(self.ui.dockWidget_parameter)
        self.handle_parameter_dock_location_changed(area)
        area = self.dockWidgetArea(self.ui.dockWidget_item_palette)
        self.handle_item_palette_dock_location_changed(area)
        # Initialize stuff
        self.init_models()
        self.init_views()
        self.setup_delegates()
        self.create_add_more_actions()
        self.connect_signals()
        self.settings_key = "graphViewWidget" if not self.read_only else "graphViewWidgetReadOnly"
        self.restore_ui()
        self.add_toggle_view_actions()
        self.init_commit_rollback_actions()
        self.build_graph()
        title = database + " (read only) " if read_only else database
        self.setWindowTitle("Data store graph view    -- {} --".format(title))
        toc = time.clock()
        self.msg.emit("Graph view form created in {} seconds\t".format(toc - tic))

    def init_models(self):
        """Initialize models."""
        super().init_models()
        self.object_class_list_model.populate_list()
        self.relationship_class_list_model.populate_list()

    def init_object_tree_model(self):
        """Initialize object tree model."""
        self.object_tree_model.build_tree(self.database)

    def init_parameter_value_models(self):
        """Initialize parameter value models from source database."""
        self.object_parameter_value_model.has_empty_row = not self.read_only
        self.relationship_parameter_value_model.has_empty_row = not self.read_only
        super().init_parameter_value_models()
        # self.object_parameter_value_proxy.default = False
        # self.relationship_parameter_value_proxy.default = False

    def init_parameter_definition_models(self):
        """Initialize parameter (definition) models from source database."""
        self.object_parameter_definition_model.has_empty_row = not self.read_only
        self.relationship_parameter_definition_model.has_empty_row = not self.read_only
        super().init_parameter_definition_models()
        # self.object_parameter_definition_proxy.default = False
        # self.relationship_parameter_definition_proxy.default = False

    def init_views(self):
        super().init_views()
        self.ui.listView_object_class.setModel(self.object_class_list_model)
        self.ui.listView_relationship_class.setModel(self.relationship_class_list_model)

    def create_add_more_actions(self):
        """Setup 'Add more' action and button."""
        # object class
        index = self.object_class_list_model.add_more_index
        action = QAction()
        icon = QIcon(":/icons/plus_object_icon.png")
        action.setIcon(icon)
        action.setText(index.data(Qt.DisplayRole))
        button = QToolButton()
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button.setDefaultAction(action)
        button.setIconSize(QSize(32, 32))
        button.setFixedSize(64, 56)
        self.ui.listView_object_class.setIndexWidget(index, button)
        action.triggered.connect(self.show_add_object_classes_form)
        # relationship class
        index = self.relationship_class_list_model.add_more_index
        action = QAction()
        icon = QIcon(":/icons/plus_relationship_icon.png")
        action.setIcon(icon)
        action.setText(index.data(Qt.DisplayRole))
        button = QToolButton()
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button.setDefaultAction(action)
        button.setIconSize(QSize(32, 32))
        button.setFixedSize(64, 56)
        self.ui.listView_relationship_class.setIndexWidget(index, button)
        action.triggered.connect(self.show_add_relationship_classes_form)

    def connect_signals(self):
        """Connect signals."""
        super().connect_signals()
        self.ui.graphicsView.item_dropped.connect(self.handle_item_dropped)
        self.ui.dockWidget_parameter.dockLocationChanged.connect(self.handle_parameter_dock_location_changed)
        self.ui.dockWidget_item_palette.dockLocationChanged.connect(self.handle_item_palette_dock_location_changed)
        self.ui.actionGraph_hide_selected.triggered.connect(self.hide_selected_items)
        self.ui.actionGraph_show_hidden.triggered.connect(self.show_hidden_items)
        self.ui.actionGraph_prune_selected.triggered.connect(self.prune_selected_items)
        self.ui.actionGraph_reinstate_pruned.triggered.connect(self.reinstate_pruned_items)
        self.ui.menuGraph.aboutToShow.connect(self.handle_menu_about_to_show)

    @Slot(name="handle_menu_about_to_show")
    def handle_menu_about_to_show(self):
        """Called when a menu from the menubar is about to show."""
        self.ui.actionGraph_hide_selected.setEnabled(len(self.object_item_selection) > 0)
        self.ui.actionGraph_show_hidden.setEnabled(len(self.hidden_items) > 0)
        self.ui.actionGraph_prune_selected.setEnabled(len(self.object_item_selection) > 0)
        self.ui.actionGraph_reinstate_pruned.setEnabled(len(self.rejected_items) > 0)

    @Slot("Qt.DockWidgetArea", name="handle_parameter_dock_location_changed")
    def handle_parameter_dock_location_changed(self, area):
        """Called when the parameter dock widget location changes.
        Adjust splitter orientation accordingly."""
        if area & (Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea):
            self.ui.splitter_object_relationship_parameter.setOrientation(Qt.Vertical)
        else:
            self.ui.splitter_object_relationship_parameter.setOrientation(Qt.Horizontal)

    @Slot("Qt.DockWidgetArea", name="handle_item_palette_dock_location_changed")
    def handle_item_palette_dock_location_changed(self, area):
        """Called when the item palette dock widget location changes.
        Adjust splitter orientation accordingly."""
        if area & (Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea):
            self.ui.splitter_object_relationship_class.setOrientation(Qt.Vertical)
        else:
            self.ui.splitter_object_relationship_class.setOrientation(Qt.Horizontal)

    def add_toggle_view_actions(self):
        """Add toggle view actions to View menu."""
        self.ui.menuDock_Widgets.addAction(self.ui.dockWidget_object_tree.toggleViewAction())
        self.ui.menuDock_Widgets.addAction(self.ui.dockWidget_parameter.toggleViewAction())
        if not self.read_only:
            self.ui.menuDock_Widgets.addAction(self.ui.dockWidget_item_palette.toggleViewAction())
        else:
            self.ui.dockWidget_item_palette.hide()

    def init_commit_rollback_actions(self):
        if not self.read_only:
            self.set_commit_rollback_actions_enabled(False)
        else:
            self.ui.menuSession.removeAction(self.ui.actionCommit)
            self.ui.menuSession.removeAction(self.ui.actionRollback)

    @busy_effect
    @Slot("bool", name="build_graph")
    def build_graph(self, checked=True):
        """Initialize graph data and build graph."""
        tic = time.clock()
        self.init_graph_data()
        self._has_graph = self.make_graph()
        if self._has_graph:
            self.ui.graphicsView.scale_to_fit_scene()
            toc = time.clock()
            self.msg.emit("Graph built in {} seconds\t".format(toc - tic))
        self.hidden_items = list()

    @Slot("QItemSelection", "QItemSelection", name="handle_object_tree_selection_changed")
    def handle_object_tree_selection_changed(self, selected, deselected):
        """Select or deselect all children when selecting or deselecting the parent."""
        self.build_graph()

    def init_graph_data(self):
        """Initialize graph data by querying db_map."""
        rejected_object_names = [x.object_name for x in self.rejected_items]
        self.object_ids = list()
        self.object_names = list()
        self.object_class_ids = list()
        self.object_class_names = list()
        root_item = self.object_tree_model.root_item
        index = self.object_tree_model.indexFromItem(root_item)
        is_root_selected = self.ui.treeView_object.selectionModel().isSelected(index)
        for i in range(root_item.rowCount()):
            object_class_item = root_item.child(i, 0)
            object_class_id = object_class_item.data(Qt.UserRole + 1)['id']
            object_class_name = object_class_item.data(Qt.UserRole + 1)['name']
            index = self.object_tree_model.indexFromItem(object_class_item)
            is_object_class_selected = self.ui.treeView_object.selectionModel().isSelected(index)
            for j in range(object_class_item.rowCount()):
                object_item = object_class_item.child(j, 0)
                object_id = object_item.data(Qt.UserRole + 1)["id"]
                object_name = object_item.data(Qt.UserRole + 1)["name"]
                if object_name in rejected_object_names:
                    continue
                index = self.object_tree_model.indexFromItem(object_item)
                is_object_selected = self.ui.treeView_object.selectionModel().isSelected(index)
                if is_root_selected or is_object_class_selected or is_object_selected:
                    self.object_ids.append(object_id)
                    self.object_names.append(object_name)
                    self.object_class_ids.append(object_class_id)
                    self.object_class_names.append(object_class_name)
        self.arc_object_id_lists = list()
        self.arc_relationship_class_ids = list()
        self.arc_object_class_name_lists = list()
        self.arc_label_object_name_lists = list()
        self.arc_label_object_class_name_lists = list()
        self.src_ind_list = list()
        self.dst_ind_list = list()
        relationship_class_dict = {
            x.id: {
                "name": x.name,
                "object_class_name_list": x.object_class_name_list
            } for x in self.db_map.wide_relationship_class_list()
        }
        for relationship in self.db_map.wide_relationship_list():
            object_class_name_list = relationship_class_dict[relationship.class_id]["object_class_name_list"]
            split_object_class_name_list = object_class_name_list.split(",")
            object_id_list = relationship.object_id_list
            split_object_id_list = [int(x) for x in object_id_list.split(",")]
            split_object_name_list = relationship.object_name_list.split(",")
            for i in range(len(split_object_id_list)):
                src_object_id = split_object_id_list[i]
                try:
                    dst_object_id = split_object_id_list[i + 1]
                except IndexError:
                    dst_object_id = split_object_id_list[0]
                try:
                    src_ind = self.object_ids.index(src_object_id)
                    dst_ind = self.object_ids.index(dst_object_id)
                except ValueError:
                    continue
                self.src_ind_list.append(src_ind)
                self.dst_ind_list.append(dst_ind)
                src_object_name = self.object_names[src_ind]
                dst_object_name = self.object_names[dst_ind]
                self.arc_object_id_lists.append(object_id_list)
                self.arc_relationship_class_ids.append(relationship.class_id)
                self.arc_object_class_name_lists.append(object_class_name_list)
                # Find out label items
                arc_label_object_name_list = list()
                arc_label_object_class_name_list = list()
                for object_name, object_class_name in zip(split_object_name_list, split_object_class_name_list):
                    if object_name in (src_object_name, dst_object_name):
                        continue
                    arc_label_object_name_list.append(object_name)
                    arc_label_object_class_name_list.append(object_class_name)
                self.arc_label_object_name_lists.append(arc_label_object_name_list)
                self.arc_label_object_class_name_lists.append(arc_label_object_class_name_list)
        # Add template items hanging around
        scene = self.ui.graphicsView.scene()
        if scene:
            self.heavy_positions = {}
            object_items = [x for x in scene.items() if isinstance(x, ObjectItem) and x.template_id_dim]
            object_ind = len(self.object_ids)
            self.template_id_dims = {}
            self.is_template = {}
            object_ind_dict = {}
            for item in object_items:
                object_id = item.object_id
                object_name = item.object_name
                try:
                    found_ind = self.object_ids.index(object_id)
                    is_template = self.is_template.get(found_ind)
                    if not is_template:
                        self.template_id_dims[found_ind] = item.template_id_dim
                        self.is_template[found_ind] = False
                        self.heavy_positions[found_ind] = item.pos()
                        continue
                except ValueError:
                    pass
                object_class_id = item.object_class_id
                object_class_name = item.object_class_name
                self.object_ids.append(object_id)
                self.object_names.append(object_name)
                self.object_class_ids.append(object_class_id)
                self.object_class_names.append(object_class_name)
                self.template_id_dims[object_ind] = item.template_id_dim
                self.is_template[object_ind] = item.is_template
                self.heavy_positions[object_ind] = item.pos()
                object_ind_dict[item] = object_ind
                object_ind += 1
            arc_items = [x for x in scene.items() if isinstance(x, ArcItem) and x.is_template]
            arc_ind = len(self.arc_label_object_name_lists)
            self.arc_template_ids = {}
            for item in arc_items:
                src_item = item.src_item
                dst_item = item.dst_item
                try:
                    src_ind = object_ind_dict[src_item]
                except KeyError:
                    src_object_id = src_item.object_id
                    src_ind = self.object_ids.index(src_object_id)
                try:
                    dst_ind = object_ind_dict[dst_item]
                except KeyError:
                    dst_object_id = dst_item.object_id
                    dst_ind = self.object_ids.index(dst_object_id)
                self.src_ind_list.append(src_ind)
                self.dst_ind_list.append(dst_ind)
                # NOTE: These arcs correspond to template arcs.
                relationship_class_id = item.relationship_class_id
                object_class_name_list = item.object_class_name_list
                self.arc_object_id_lists.append("")  # TODO: is this one filled when creating the relationship?
                self.arc_relationship_class_ids.append(relationship_class_id)
                self.arc_object_class_name_lists.append(object_class_name_list)
                # Label don't matter
                self.arc_label_object_name_lists.append("")
                self.arc_label_object_class_name_lists.append("")
                self.arc_template_ids[arc_ind] = item.template_id
                arc_ind += 1

    def shortest_path_matrix(self, object_name_list, src_ind_list, dst_ind_list, spread):
        """Return the shortest-path matrix."""
        N = len(object_name_list)
        if not N:
            return None
        dist = np.zeros((N, N))
        src_ind = arr(src_ind_list)
        dst_ind = arr(dst_ind_list)
        try:
            dist[src_ind, dst_ind] = dist[dst_ind, src_ind] = spread
        except IndexError:
            pass
        d = dijkstra(dist, directed=False)
        # Remove infinites and zeros
        d[d == np.inf] = spread * 3
        d[d == 0] = spread * 1e-6
        return d

    def sets(self, N):
        """Return sets of vertex pairs indices."""
        sets = []
        for n in range(1, N):
            pairs = np.zeros((N - n, 2), int)  # pairs on diagonal n
            pairs[:, 0] = np.arange(N - n)
            pairs[:, 1] = pairs[:, 0] + n
            mask = np.mod(range(N - n), 2 * n) < n
            s1 = pairs[mask]
            s2 = pairs[~mask]
            if len(s1) > 0:
                sets.append(s1)
            if len(s2) > 0:
                sets.append(s2)
        return sets

    def vertex_coordinates(self, matrix, heavy_positions={}, iterations=10, weight_exp=-2, initial_diameter=1000):
        """Return x and y coordinates for each vertex in the graph, computed using VSGD-MS."""
        N = len(matrix)
        if N == 1:
            return [0], [0]
        mask = np.ones((N, N)) == 1 - np.tril(np.ones((N, N)))  # Upper triangular except diagonal
        np.random.seed(0)
        layout = np.random.rand(N, 2) * initial_diameter - initial_diameter / 2  # Random layout with initial diameter
        heavy_ind_list = list()
        heavy_pos_list = list()
        for ind, pos in heavy_positions.items():
            heavy_ind_list.append(ind)
            heavy_pos_list.append([pos.x(), pos.y()])
        heavy_ind = arr(heavy_ind_list)
        heavy_pos = arr(heavy_pos_list)
        if heavy_ind.any():
            # Shift random layout to the center of heavy position
            shift = np.mean(matrix[heavy_ind, :][:, heavy_ind], axis=0)
            layout[:, 0] += shift[0]
            layout[:, 1] += shift[1]
            # Apply heavy positions
            layout[heavy_ind, :] = heavy_pos
        weights = matrix ** weight_exp  # bus-pair weights (lower for distant buses)
        maxstep = 1 / np.min(weights[mask])
        minstep = 1 / np.max(weights[mask])
        lambda_ = np.log(minstep / maxstep) / (iterations - 1)  # exponential decay of allowed adjustment
        sets = self.sets(N)  # construct sets of bus pairs
        for iteration in range(iterations):
            step = maxstep * np.exp(lambda_ * iteration)  # how big adjustments are allowed?
            rand_order = np.random.permutation(N)  # we don't want to use the same pair order each iteration
            for p in sets:
                v1, v2 = rand_order[p[:, 0]], rand_order[p[:, 1]]  # arrays of vertex1 and vertex2
                # current distance (possibly accounting for system rescaling)
                dist = ((layout[v1, 0] - layout[v2, 0]) ** 2 + (layout[v1, 1] - layout[v2, 1]) ** 2) ** 0.5
                r = (matrix[v1, v2] - dist)[:, None] / 2 * (layout[v1] - layout[v2]) / dist[:, None]  # desired change
                dx1 = r * np.minimum(1, weights[v1, v2] * step)[:, None]
                dx2 = -dx1
                layout[v1, :] += dx1  # update position
                layout[v2, :] += dx2
                if heavy_ind.any():
                    # Apply heavy positions
                    layout[heavy_ind, :] = heavy_pos
        return layout[:, 0], layout[:, 1]

    def make_graph(self):
        """Make graph."""
        scene = self.new_scene()
        d = self.shortest_path_matrix(self.object_names, self.src_ind_list, self.dst_ind_list, self._spread)
        if d is None:
            return False
        x, y = self.vertex_coordinates(d, self.heavy_positions)
        object_items = list()
        for i in range(len(self.object_names)):
            object_id = self.object_ids[i]
            object_name = self.object_names[i]
            object_class_id = self.object_class_ids[i]
            object_class_name = self.object_class_names[i]
            object_item = ObjectItem(
                self, object_id, object_name, object_class_id, object_class_name,
                x[i], y[i], self.extent, label_font=self.font, label_color=self.object_label_color)
            try:
                template_id_dim = self.template_id_dims[i]
                object_item.template_id_dim = template_id_dim
                if self.is_template[i]:
                    object_item.make_template()
            except KeyError:
                pass
            scene.addItem(object_item)
            object_items.append(object_item)
        for k in range(len(self.src_ind_list)):
            i = self.src_ind_list[k]
            j = self.dst_ind_list[k]
            object_id_list = self.arc_object_id_lists[k]
            relationship_class_id = self.arc_relationship_class_ids[k]
            object_class_names = self.arc_object_class_name_lists[k]
            label_object_names = self.arc_label_object_name_lists[k]
            label_object_class_names = self.arc_label_object_class_name_lists[k]
            label_parts = self.relationship_graph(
                label_object_names, label_object_class_names, self.extent, self._spread / 2,
                label_font=self.font, label_color=Qt.transparent,
                relationship_class_id=relationship_class_id)
            arc_item = ArcItem(
                self, object_id_list, relationship_class_id, label_object_class_names, # object_class_names,
                object_items[i], object_items[j], .25 * self.extent,
                self.arc_color, label_color=self.arc_label_color, label_parts=label_parts)
            try:
                template_id = self.arc_template_ids[k]
                arc_item.template_id = template_id
                arc_item.make_template()
            except KeyError:
                pass
            scene.addItem(arc_item)
        return True

    def new_scene(self):
        """A new scene with a background."""
        old_scene = self.ui.graphicsView.scene()
        if old_scene:
            old_scene.deleteLater()
        self._scene_bg = QGraphicsRectItem()
        self._scene_bg.setPen(Qt.NoPen)
        self._scene_bg.setZValue(-100)
        scene = QGraphicsScene()
        self.ui.graphicsView.setScene(scene)
        scene.addItem(self._scene_bg)
        scene.changed.connect(self.handle_scene_changed)
        scene.selectionChanged.connect(self.handle_scene_selection_changed)
        return scene

    @Slot(name="handle_scene_selection_changed")
    def handle_scene_selection_changed(self):
        """Show parameters for selected items."""
        scene = self.ui.graphicsView.scene()  # TODO: should we use sender() here?
        current_items = scene.selectedItems()
        previous_items = self.object_item_selection + self.arc_item_selection
        selected = [x for x in current_items if x not in previous_items]
        deselected = [x for x in previous_items if x not in current_items]
        self.object_item_selection = [x for x in current_items if isinstance(x, ObjectItem)]
        self.arc_item_selection = [x for x in current_items if isinstance(x, ArcItem)]
        selected_object_ids = set()
        selected_object_id_lists = set()
        deselected_object_ids = set()
        deselected_object_id_lists = set()
        object_class_ids = set()
        relationship_class_ids = set()
        for item in selected:
            if isinstance(item, ObjectItem):
                selected_object_ids.add(item.object_id)
            elif isinstance(item, ArcItem):
                selected_object_id_lists.add(item.object_id_list)
        for item in deselected:
            if isinstance(item, ObjectItem):
                deselected_object_ids.add(item.object_id)
            elif isinstance(item, ArcItem):
                deselected_object_id_lists.add(item.object_id_list)
        for item in current_items:
            if isinstance(item, ObjectItem):
                object_class_ids.add(item.object_class_id)
            elif isinstance(item, ArcItem):
                relationship_class_ids.add(item.relationship_class_id)
        self.object_parameter_value_proxy.diff_update_object_id_set(deselected_object_ids)
        self.object_parameter_value_proxy.update_object_id_set(selected_object_ids)
        self.object_parameter_value_proxy.apply_filter()
        self.object_parameter_definition_proxy.clear_object_class_id_set()
        self.object_parameter_definition_proxy.update_object_class_id_set(object_class_ids)
        self.object_parameter_definition_proxy.apply_filter()
        self.relationship_parameter_value_proxy.diff_update_object_id_list_set(deselected_object_id_lists)
        self.relationship_parameter_value_proxy.update_object_id_list_set(selected_object_id_lists)
        self.relationship_parameter_value_proxy.apply_filter()
        self.relationship_parameter_definition_proxy.clear_relationship_class_id_set()
        self.relationship_parameter_definition_proxy.update_relationship_class_id_set(relationship_class_ids)
        self.relationship_parameter_definition_proxy.apply_filter()

    @Slot("QList<QRectF>", name="handle_scene_changed")
    def handle_scene_changed(self, region):
        """Make a new scene with usage instructions if previous is empty,
        where empty means the only item is the bg.
        """
        if len(self.ui.graphicsView.scene().items()) > 1:  # TODO: should we use sender() here?
            return
        scene = self.new_scene()
        usage = """
            <html>
            <head>
            <style type="text/css">
            ol {
                margin-left: 80px;
                padding-left: 0px;
            }
            ul {
                margin-left: 40px;
                padding-left: 0px;
            }
            </style>
            </head>
            <h3>Usage:</h3>
            <ol>
            <li>Select items in <a href="Object tree">Object tree</a> to show objects here.
                <ul>
                <li>Hold down the 'Ctrl' key or just drag your mouse to add multiple items to the selection.</li>
                <li>Selected objects are vertices in the graph,
                while relationships between those objects are edges.
                </ul>
            </li>
            <li>Select items here to show their parameters in <a href="Parameter dock">Parameter dock</a>.
                <ul>
                <li>Hold down 'Ctrl' to add multiple items to the selection.</li>
                <li> Hold down 'Ctrl' and drag your mouse to perform a rubber band selection.</li>
                </ul>
            </li>
        """
        if not self.read_only:
            usage += """
                <li>Drag icons from <a href="Item palette">Item palette</a>
                and drop them here to create new items.</li>
            """
        usage += """
            </ol>
            </html>
        """
        usage_item = CustomTextItem(usage, self.font)
        usage_item.linkActivated.connect(self.handle_usage_link_activated)
        scene.addItem(usage_item)
        self._has_graph = False
        self.ui.graphicsView.scale_to_fit_scene()

    @Slot("QString", name="handle_usage_link_activated")
    def handle_usage_link_activated(self, link):
        if link == "Object tree":
            self.ui.dockWidget_object_tree.show()
        elif link == "Parameter dock":
            self.ui.dockWidget_parameter.show()
        elif link == "Item palette":
            self.ui.dockWidget_item_palette.show()

    @Slot("QPoint", "QString", name="handle_item_dropped")
    def handle_item_dropped(self, pos, text):
        if self._has_graph:
            scene = self.ui.graphicsView.scene()
        else:
            scene = self.new_scene()
        # Make scene background the size of the scene
        view_rect = self.ui.graphicsView.viewport().rect()
        top_left = self.ui.graphicsView.mapToScene(view_rect.topLeft())
        bottom_right = self.ui.graphicsView.mapToScene(view_rect.bottomRight())
        rectf = QRectF(top_left, bottom_right)
        self._scene_bg.setRect(rectf)
        scene_pos = self.ui.graphicsView.mapToScene(pos)
        data = eval(text)
        if data["type"] == "object_class":
            class_id = data["id"]
            class_name = data["name"]
            name = class_name
            object_item = ObjectItem(
                self, 0, name, class_id, class_name, scene_pos.x(), scene_pos.y(), self.extent,
                label_font=self.font, label_color=self.object_label_color)
            scene.addItem(object_item)
            object_item.make_template()
        elif data["type"] == "relationship_class":
            relationship_class_id = data["id"]
            object_class_id_list = [int(x) for x in data["object_class_id_list"].split(',')]
            object_class_name_list = data["object_class_name_list"].split(',')
            object_name_list = object_class_name_list.copy()
            fix_name_ambiguity(object_name_list)
            relationship_graph = self.relationship_graph(
                object_name_list, object_class_name_list, self.extent, self._spread,
                label_font=self.font, label_color=self.object_label_color,
                object_class_id_list=object_class_id_list, relationship_class_id=relationship_class_id)
            self.add_relationship_template(scene, scene_pos.x(), scene_pos.y(), *relationship_graph)
            self.relationship_class_dict[self.template_id] = {"id": data["id"], "name": data["name"]}
            self.template_id += 1
        self._has_graph = True

    def add_relationship_template(self, scene, x, y, object_items, arc_items, dimension_at_origin=None):
        """Add relationship parts into the scene to form a 'relationship template'."""
        for item in object_items + arc_items:
            scene.addItem(item)
        # Make template
        for dimension, object_item in enumerate(object_items):
            object_item.template_id_dim[self.template_id] = dimension
            object_item.make_template()
        for arc_item in arc_items:
            arc_item.template_id = self.template_id
            arc_item.make_template()
        # Move
        try:
            rectf = object_items[dimension_at_origin].sceneBoundingRect()
        except (IndexError, TypeError):
            rectf = QRectF()
            for object_item in object_items:
                rectf |= object_item.sceneBoundingRect()
        center = rectf.center()
        for object_item in object_items:
            object_item.moveBy(x - center.x(), y - center.y())
            object_item.move_related_items_by(QPointF(x, y) - center)

    @busy_effect
    def add_relationship(self, template_id, object_items):
        """Try and add relationship given a template id and a list of object items."""
        object_id_list = list()
        object_name_list = list()
        object_dimensions = [x.template_id_dim[template_id] for x in object_items]
        for dimension in sorted(object_dimensions):
            ind = object_dimensions.index(dimension)
            item = object_items[ind]
            object_name = item.object_name
            if not object_name:
                logging.debug("can't find name {}".format(object_name))
                return False
            object_ = self.db_map.single_object(name=object_name).one_or_none()
            if not object_:
                logging.debug("can't find object {}".format(object_name))
                return False
            object_id_list.append(object_.id)
            object_name_list.append(object_name)
        if len(object_id_list) < 2:
            logging.debug("too short {}".format(len(object_id_list)))
            return False
        name = self.relationship_class_dict[template_id]["name"] + "_" + "__".join(object_name_list)
        class_id = self.relationship_class_dict[template_id]["id"]
        wide_kwargs = {
            'name': name,
            'object_id_list': object_id_list,
            'class_id': class_id
        }
        try:
            wide_relationship = self.db_map.add_wide_relationships(wide_kwargs)[0]
            for item in object_items:
                del item.template_id_dim[template_id]
            items = self.ui.graphicsView.scene().items()
            arc_items = [x for x in items if isinstance(x, ArcItem) and x.template_id == template_id]
            for item in arc_items:
                item.remove_template()
                item.template_id = None
                item.object_id_list = ",".join([str(x) for x in object_id_list])
            self.set_commit_rollback_actions_enabled(True)
            msg = "Successfully added new relationship '{}'.".format(wide_relationship.name)
            self.msg.emit(msg)
            return True
        except SpineIntegrityError as e:
            self.msg_error.emit(e.msg)
            return False
        except SpineDBAPIError as e:
            self.msg_error.emit(e.msg)
            return False

    def relationship_graph(
            self, object_name_list, object_class_name_list,
            extent, spread, label_font, label_color,
            object_class_id_list=[], relationship_class_id=None):
        """Lists of object and arc items that form a relationship."""
        object_items = list()
        arc_items = list()
        src_ind_list = list(range(len(object_name_list)))
        dst_ind_list = src_ind_list[1:] + src_ind_list[:1]
        d = self.shortest_path_matrix(object_name_list, src_ind_list, dst_ind_list, spread)
        if d is None:
            return [], []
        x, y = self.vertex_coordinates(d)
        for i in range(len(object_name_list)):
            x_ = x[i]
            y_ = y[i]
            object_name = object_name_list[i]
            object_class_name = object_class_name_list[i]
            try:
                object_class_id = object_class_id_list[i]
            except IndexError:
                object_class_id = None
            object_item = ObjectItem(
                self, None, object_name, object_class_id, object_class_name, x_, y_, extent,
                label_font=label_font, label_color=label_color)
            object_items.append(object_item)
        for i in range(len(object_items)):
            src_item = object_items[i]
            try:
                dst_item = object_items[i + 1]
            except IndexError:
                dst_item = object_items[0]
            arc_item = ArcItem(
                self, None, relationship_class_id, None,
                src_item, dst_item, extent / 4, self.arc_color)
            arc_items.append(arc_item)
        return object_items, arc_items

    def add_object_classes(self, object_classes):
        """Insert new object classes."""
        super().add_object_classes(object_classes)
        for object_class in object_classes:
            self.object_class_list_model.add_object_class(object_class)

    def show_add_relationship_classes_form(self):
        """Show dialog to let user select preferences for new relationship class."""
        dialog = AddRelationshipClassesDialog(self)
        dialog.show()

    def add_relationship_classes(self, wide_relationship_classes):
        """Insert new relationship classes."""
        dim_count_list = list()
        for wide_relationship_class in wide_relationship_classes:
            self.relationship_class_list_model.add_relationship_class(wide_relationship_class)
        self.set_commit_rollback_actions_enabled(True)
        relationship_class_name_list = "', '".join([x.name for x in wide_relationship_classes])
        msg = "Successfully added new relationship class(es) '{}'.".format(relationship_class_name_list)
        self.msg.emit(msg)

    def show_graph_view_context_menu(self, global_pos):
        """Show context menu for graphics view."""
        self.graph_view_context_menu = GraphViewContextMenu(self, global_pos)
        option = self.graph_view_context_menu.get_action()
        if option == "Hide selected items":
            self.hide_selected_items()
        elif option == "Show hidden items":
            self.show_hidden_items()
        elif option == "Prune selected items":
            self.prune_selected_items()
        elif option == "Reinstate pruned items":
            self.reinstate_pruned_items()
        else:
            pass
        self.graph_view_context_menu.deleteLater()
        self.graph_view_context_menu = None

    @Slot("bool", name="reinstate_pruned_items")
    def hide_selected_items(self, checked=False):
        """Hide selected items."""
        self.hidden_items.extend(self.object_item_selection)
        for item in self.object_item_selection:
            item.set_all_visible(False)

    @Slot("bool", name="reinstate_pruned_items")
    def show_hidden_items(self, checked=False):
        """Show hidden items."""
        scene = self.ui.graphicsView.scene()
        if not scene:
            return
        for item in self.hidden_items:
            item.set_all_visible(True)
            self.hidden_items = list()

    @Slot("bool", name="reinstate_pruned_items")
    def prune_selected_items(self, checked=False):
        """Prune selected items."""
        self.rejected_items.extend(self.object_item_selection)
        self.build_graph()

    @Slot("bool", name="reinstate_pruned_items")
    def reinstate_pruned_items(self, checked=False):
        """Reinstate pruned items."""
        self.rejected_items = list()
        self.build_graph()

    def show_object_item_context_menu(self, e, main_item):
        """Show context menu for object_item."""
        global_pos = e.screenPos()
        self.object_item_context_menu = ObjectItemContextMenu(self, global_pos, main_item)
        option = self.object_item_context_menu.get_action()
        if option == 'Hide':
            self.hide_selected_items()
        elif option == 'Prune':
            self.prune_selected_items()
        elif option in ('Set name', 'Rename'):
            main_item.edit_name()
        elif option == 'Remove':
            self.remove_graph_items()
        try:
            relationship_class = self.object_item_context_menu.relationship_class_dict[option]
            relationship_class_id = relationship_class["id"]
            relationship_class_name = relationship_class["name"]
            object_class_id_list = relationship_class["object_class_id_list"]
            object_class_name_list = relationship_class['object_class_name_list']
            object_name_list = relationship_class['object_name_list']
            dimension = relationship_class['dimension']
            object_items, arc_items = self.relationship_graph(
                object_name_list, object_class_name_list, self.extent, self._spread,
                label_font=self.font, label_color=self.object_label_color,
                object_class_id_list=object_class_id_list, relationship_class_id=relationship_class_id)
            scene = self.ui.graphicsView.scene()
            scene_pos = e.scenePos()
            self.add_relationship_template(
                scene, scene_pos.x(), scene_pos.y(), object_items, arc_items, dimension_at_origin=dimension)
            object_items[dimension].merge_item(main_item)
            self._has_graph = True
            self.relationship_class_dict[self.template_id] = {
                "id": relationship_class_id,
                "name": relationship_class_name
            }
            self.template_id += 1
        except KeyError:
            pass
        self.object_item_context_menu.deleteLater()
        self.object_item_context_menu = None

    @busy_effect
    @Slot("bool", name="remove_graph_items")
    def remove_graph_items(self, checked=False):
        """Remove all selected items in the graph."""
        if not self.object_item_selection + self.arc_item_selection:
            return
        removed_id_dict = {
            "object": set(x.object_id for x in self.object_item_selection if x.object_id)
        }
        try:
            self.db_map.remove_items(**{k + "_ids": v for k, v in removed_id_dict.items()})  # FIXME: this is ugly
            for key, value in removed_id_dict.items():
                self.object_tree_model.remove_items(key, *value)
            for key, value in removed_id_dict.items():
                self.object_parameter_definition_model.remove_items(key, *value)
                self.object_parameter_value_model.remove_items(key, *value)
                self.relationship_parameter_definition_model.remove_items(key, *value)
                self.relationship_parameter_value_model.remove_items(key, *value)
            for item in self.object_item_selection:
                item.wipe_out()
            #for item in self.arc_item_selection:
            #    item.scene().removeItem(item)
            self.set_commit_rollback_actions_enabled(True)
            self.msg.emit("Successfully removed items.")
        except SpineDBAPIError as e:
            self.msg_error.emit(e.msg)

    def restore_ui(self):
        """Restore UI state from previous session."""
        super().restore_ui()
        window_state = self.qsettings.value("{0}/windowState".format(self.settings_key))
        if window_state:
            self.restoreState(window_state, version=1)  # Toolbar and dockWidget positions

    def closeEvent(self, event=None):
        """Handle close window.

        Args:
            event (QEvent): Closing event if 'X' is clicked.
        """
        super().closeEvent(event)
        self.qsettings.setValue("{0}/windowState".format(self.settings_key), self.saveState(version=1))
        scene = self.ui.graphicsView.scene()
        if scene:
            scene.deleteLater()