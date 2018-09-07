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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

"""
Module for view class.

:author: Jon Olauson <jolauson@kth.se>
:date:   14.07.2018

"""

import os
import copy
import getpass
import logging
from PySide2.QtGui import QDesktopServices
from PySide2.QtCore import Slot, QUrl, QFileSystemWatcher, Qt
from PySide2.QtWidgets import QInputDialog
from metaobject import MetaObject
from widgets.view_subwindow_widget import ViewWidget
from widgets.add_db_reference_widget import AddDbReferenceWidget
from spinedatabase_api import DatabaseMapping, SpineDBAPIError, copy_database
from widgets.network_map_widget import NetworkMapForm
from network_map import NetworkMap
from graphics_items import ViewImage
from helpers import create_dir, busy_effect
import numpy as np
from numpy import atleast_1d as arr


class View(MetaObject):
    """View class.

    Attributes:
        toolbox (ToolboxUI): QMainWindow instance
        name (str): Object name
        description (str): Object description
        references (list): List of references (for now it's only database references)
        x (int): Initial X coordinate of item icon
        y (int): Initial Y coordinate of item icon
    """
    def __init__(self, toolbox, name, description, references, x, y):
        """Class constructor."""
        super().__init__(name, description)
        self._toolbox = toolbox
        self._project = self._toolbox.project()
        self.item_type = "View"
        self.item_category = "Views"
        self._widget = ViewWidget(self.item_type)
        self._widget.set_name_label(name)
        self.data_dir_watcher = QFileSystemWatcher(self)
        # Make directory for View
        self.data_dir = os.path.join(self._project.project_dir, self.short_name)
        self.references = references
        try:
            create_dir(self.data_dir)
            self.data_dir_watcher.addPath(self.data_dir)
        except OSError:
            self._toolbox.msg_error.emit("[OSError] Creating directory {0} failed."
                                        " Check permissions.".format(self.data_dir))
        self.databases = list()  # name of imported databases NOTE: Not in use at the moment
        # Populate references model
        self._widget.populate_reference_list(self.references)
        # Populate data (files) model
        data_files = self.data_files()
        self._widget.populate_data_list(data_files)
        self.add_db_reference_form = None
        self._graphics_item = ViewImage(self._toolbox, x - 35, y - 35, 70, 70, self.name)
        self.connect_signals()

    def connect_signals(self):
        """Connect this data store's signals to slots."""
        self._widget.ui.pushButton_open.clicked.connect(self.open_directory)
        self._widget.ui.toolButton_plus.clicked.connect(self.show_add_db_reference_form)
        self._widget.ui.toolButton_minus.clicked.connect(self.remove_references)
        self._widget.ui.listView_data.doubleClicked.connect(self.open_data_file)
        self._widget.ui.listView_references.doubleClicked.connect(self.open_reference)
        self._widget.ui.toolButton_add.clicked.connect(self.import_references)
        self.data_dir_watcher.directoryChanged.connect(self.refresh)

    def project(self):
        """Returns current project or None if no project open."""
        return self._project

    def set_icon(self, icon):
        self._graphics_item = icon

    def get_icon(self):
        """Returns the item representing this Data Store on the scene."""
        return self._graphics_item

    def get_widget(self):
        """Returns the graphical representation (QWidget) of this object."""
        return self._widget

    @Slot(name="open_directory")
    def open_directory(self):
        """Open file explorer in this Data Store's data directory."""
        url = "file:///" + self.data_dir
        # noinspection PyTypeChecker, PyCallByClass, PyArgumentList
        res = QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))
        if not res:
            self._toolbox.msg_error.emit("Failed to open directory: {0}".format(self.data_dir))

    @Slot(name="show_add_db_reference_form")
    def show_add_db_reference_form(self):
        """Show the form for querying database connection options."""
        self.add_db_reference_form = AddDbReferenceWidget(self._toolbox, self)
        self.add_db_reference_form.show()

    def add_reference(self, reference):
        """Add reference to reference list and populate widget's reference list."""
        self.references.append(reference)
        self._widget.populate_reference_list(self.references)

    @Slot(name="remove_references")
    def remove_references(self):
        """Remove selected references from reference list.
        Removes all references if nothing is selected.
        """
        indexes = self._widget.ui.listView_references.selectedIndexes()
        if not indexes:  # Nothing selected
            self.references.clear()
            self._toolbox.msg.emit("All references removed")
        else:
            rows = [ind.row() for ind in indexes]
            rows.sort(reverse=True)
            for row in rows:
                self.references.pop(row)
            self._toolbox.msg.emit("Selected references removed")
        self._widget.populate_reference_list(self.references)

    @Slot(name="import_references")
    def import_references(self):
        """Import data from selected items in reference list into local SQLite file.
        If no item is selected then import all of them.
        """
        if not self.references:
            self._toolbox.msg_warning.emit("No data to import")
            return
        indexes = self._widget.ui.listView_references.selectedIndexes()
        if not indexes:  # Nothing selected, import all
            references_to_import = self.references
        else:
            references_to_import = [self.references[ind.row()] for ind in indexes]
        for reference in references_to_import:
            try:
                self.import_reference(reference)
            except Exception as e:
                self._toolbox.msg_error.emit("Import failed: {}".format(e))
                continue
        data_files = self.data_files()
        self._widget.populate_data_list(data_files)

    @busy_effect
    def import_reference(self, reference):
        """Import reference database into local SQLite file"""
        database = reference['database']
        self._toolbox.msg.emit("Importing database <b>{0}</b>".format(database))
        # Source
        source_url = reference['url']
        # Destination
        if source_url.startswith('sqlite'):
            dest_filename = os.path.join(self.data_dir, database)
        else:
            dest_filename = os.path.join(self.data_dir, database + ".sqlite")
        try:
            os.remove(dest_filename)
        except OSError:
            pass
        dest_url = "sqlite:///" + dest_filename
        copy_database(dest_url, source_url)
        self.databases.append(database)

    @busy_effect
    @Slot("QModelIndex", name="open_data_file")
    def open_data_file(self, index):
        """Open file in Data Store form."""
        if not index:
            return
        if not index.isValid():
            logging.error("Index not valid")
            return
        data_file = self.data_files()[index.row()]
        data_file_path = os.path.join(self.data_dir, data_file)
        db_url = "sqlite:///" + data_file_path
        username = getpass.getuser()
        try:
            mapping = DatabaseMapping(db_url, username)
        except SpineDBAPIError as e:
            self._toolbox.msg_error.emit(e.msg)
            return
        # network_map = NetworkMap(self, mapping)
        network_map_form = NetworkMapForm(self._toolbox, self, mapping)
        network_map_form.show()

    @busy_effect
    @Slot("QModelIndex", name="open_reference")
    def open_reference(self, index):
        """Open reference in spine data explorer."""
        if not index:
            return
        if not index.isValid():
            logging.error("Index not valid")
            return
        reference = self.references[index.row()]
        db_url = reference['url']
        database = reference['database']
        username = reference['username']
        try:
            mapping = DatabaseMapping(db_url, username)
        except SpineDBAPIError as e:
            self._toolbox.msg_error.emit(e.msg)
            return
        network_map_form = NetworkMapForm(self._toolbox, self, mapping)
        network_map_form.show()

    def data_references(self):
        """Returns a list of connection strings that are in this item as references (self.references)."""
        return self.references

    def data_files(self):
        """Return a list of files in the data directory."""
        if not os.path.isdir(self.data_dir):
            return None
        return os.listdir(self.data_dir)

    @Slot(name="refresh")
    def refresh(self):
        """Refresh data files QTreeView.
        NOTE: Might lead to performance issues."""
        d = self.data_files()
        self._widget.populate_data_list(d)
