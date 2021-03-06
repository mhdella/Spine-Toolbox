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
Spine Toolbox default configurations.

:author: P. Savolainen (VTT)
:date:   2.1.2018
"""

import sys
import os
from PySide2.QtGui import QColor

SPINE_TOOLBOX_VERSION = "0.1.75"
REQUIRED_SPINE_DBAPI_VERSION = "0.0.10"
ERROR_COLOR = QColor('red')
SUCCESS_COLOR = QColor('green')
NEUTRAL_COLOR = QColor('blue')
BLACK_COLOR = QColor('black')
# SPINE GREEN HTML: #99cc33 RGBa: 153, 204, 51, 255
# SPINE BLUE HTML: #004ac2 RGBa: 0, 74, 194, 255
# Selected characters that are not allowed in folder names
INVALID_CHARS = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", "."]
# "." is actually valid in a folder name but this is
# to prevent the user from creating folders like /..../

# Paths to application, configuration file, default project and work dirs, and documentation index page
if getattr(sys, "frozen", False):
    APPLICATION_PATH = os.path.realpath(os.path.dirname(sys.executable))
    CONFIGURATION_FILE = os.path.abspath(os.path.join(APPLICATION_PATH, "conf", "settings.conf"))
    DEFAULT_PROJECT_DIR = os.path.abspath(os.path.join(APPLICATION_PATH, "projects"))
    DEFAULT_WORK_DIR = os.path.abspath(os.path.join(APPLICATION_PATH, "work"))
    DOC_INDEX_PATH = os.path.abspath(os.path.join(APPLICATION_PATH, "docs", "html", "index.html"))
else:
    APPLICATION_PATH = os.path.realpath(os.path.dirname(__file__))
    CONFIGURATION_FILE = os.path.abspath(os.path.join(APPLICATION_PATH, os.path.pardir, "conf", "settings.conf"))
    DEFAULT_PROJECT_DIR = os.path.abspath(os.path.join(APPLICATION_PATH, os.path.pardir, "projects"))
    DEFAULT_WORK_DIR = os.path.abspath(os.path.join(APPLICATION_PATH, os.path.pardir, "work"))
    DOC_INDEX_PATH = os.path.abspath(os.path.join(
            APPLICATION_PATH, os.path.pardir, "docs", "build", "html", "index.html"))

# Tool output directory name
TOOL_OUTPUT_DIR = "output"

# GAMS
if not sys.platform == "win32":
    GAMS_EXECUTABLE = "gams"
    GAMSIDE_EXECUTABLE = "gamside"
else:
    GAMS_EXECUTABLE = "gams.exe"
    GAMSIDE_EXECUTABLE = "gamside.exe"

# Julia
if not sys.platform == "win32":
    JULIA_EXECUTABLE = "julia"
else:
    JULIA_EXECUTABLE = "julia.exe"

# Tool types
TOOL_TYPES = ["GAMS", "Julia", "Executable"]

# Required and optional keywords for Tool template definition files
REQUIRED_KEYS = ['name', 'tooltype', 'includes']
OPTIONAL_KEYS = ['description', 'short_name', 'inputfiles', 'inputfiles_opt', 'outputfiles', 'cmdline_args']
LIST_REQUIRED_KEYS = ['includes', 'inputfiles', 'inputfiles_opt', 'outputfiles']  # These should be lists

SQL_DIALECT_API = {
    'mysql': 'pymysql',
    'sqlite': 'sqlite3',
    'mssql': 'pyodbc',
    'postgresql': 'psycopg2',
    'oracle': 'cx_oracle'
}

# Default settings
SETTINGS = {"project_directory": "",
            "open_previous_project": "true",
            "previous_project": "",
            "show_exit_prompt": "true",
            "logging_level": "2",
            "datetime": "true",
            "gams_path": "",
            "use_repl": "true",
            "julia_path": "",
            "save_at_exit": "1",
            "commit_at_exit": "1",
            "delete_data": "false"}

# Stylesheets
STATUSBAR_SS = "QStatusBar{" \
                    "background-color: #EBEBE0;" \
                    "border-width: 1px;" \
                    "border-color: gray;" \
                    "border-style: groove;}"

SETTINGS_SS = "#SettingsForm{background-color: ghostwhite;}" \
                "QLabel{color: white;}" \
                "QCheckBox{color: white;}" \
                "QGroupBox{border: 2px solid gray; " \
                    "background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #004AC2, stop: 1 #80B0FF);" \
                    "border-radius: 5px;" \
                    "margin-top: 0.5em;}" \
                "QGroupBox:title{border-radius: 2px; " \
                    "background-color: ghostwhite;" \
                    "subcontrol-origin: margin;" \
                    "subcontrol-position: top center;" \
                    "padding-top: 0px;" \
                    "padding-bottom: 0px;" \
                    "padding-right: 3px;" \
                    "padding-left: 3px;}"

# NOTE: border-style property needs to be set for QToolBar so the lineargradient works on GNOME desktop environment
# (known Qt issue)
ICON_TOOLBAR_SS = "QToolBar{spacing: 6px; " \
                    "background: qlineargradient(x1: 1, y1: 1, x2: 0, y2: 0, stop: 0 #cce0ff, stop: 1 #66a1ff);" \
                    "padding: 3px;" \
                    "border-style: solid;}" \
                  "QToolButton{background-color: white;" \
                    "border-width: 1px;" \
                    "border-style: inset;" \
                    "border-color: darkslategray;" \
                    "border-radius: 2px;}" \
                  "QLabel{color:black;" \
                    "padding: 3px;}"

TEXTBROWSER_SS = "QTextBrowser{background-color: black;}"
# ToolboxUI stylesheet. A lot of widgets inherit this sheet.
MAINWINDOW_SS = "QMainWindow:separator{width: 3px; background-color: lightgray; border: 1px solid white;}" \
                "QPushButton{border: 1px outset brown; border-radius: 2px; min-width: 70px; min-height: 20px;" \
                    "background-color: qlineargradient(x1: 1, y1: 1, x2: 0, y2: 0, stop: 0 #d9d9d9, stop: 1 #f2f2f2);}" \
                "QPushButton:focus{background-color: #f2f2f0; border: 1px outset brown; outline: 1px dotted brown}" \
                "QPushButton:hover{background-color: qlineargradient(x1: 1, y1: 1, x2: 0, y2: 0, stop: 0 #f2f2f2, stop: 1 #d9d9d9);}" \
                "QPushButton:pressed{background-color: #f2f2f2;}" \
                "QToolButton:focus{border: 1px ridge black;}" \
                "QToolButton::pressed{background-color: #f2f2f2;}" \
                "QToolButton::menu-indicator{width: 0px;}" \
                "QCheckBox:focus{border-color: black; border-width: 1px; border-style: ridge;}" \
                "QComboBox:focus{border-color: black; border-width: 1px; border-style: ridge;}" \
                "QLineEdit:focus{border-color: black; border-width: 1px; border-style: ridge;}" \
                "QTextEdit:focus{border-color: black; border-width: 2px; border-style: ridge;}" \
                "QTreeView:focus{border-color: darkslategray; border-width: 2px; border-style: ridge;}"
TOOL_TREEVIEW_HEADER_SS = "QHeaderView::section{background-color: #ffe6cc;}"
DC_TREEVIEW_HEADER_SS = "QHeaderView::section{background-color: #ffe6cc;}"
TT_TREEVIEW_HEADER_SS = "QHeaderView::section{background-color: #ffe6cc;}"
HEADER_POINTSIZE = 8
# Draw border on all QWidgets when in focus
# TT_FOCUS_SS = ":focus {border: 1px groove;}"

JL_REPL_TIME_TO_DEAD = 5.0
JL_REPL_RESTART_LIMIT = 3
