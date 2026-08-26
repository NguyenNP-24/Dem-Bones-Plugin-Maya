# -*- coding: utf-8 -*-
"""
Dem Bones Maya Tool
A tool for automatic rigging using Dem Bones algorithm

Author: Nguyen Phuc Nguyen
Version: 1.1.0
"""

from dembones_maya_tool.ui import DemBonesUI
from dembones_maya_tool.controller import DemBonesController
from dembones_maya_tool.validator import DemBonesValidator
import dembones_maya_tool.utils as utils

__version__ = "1.1.0"
__all__ = ['show_ui', 'DemBonesUI', 'DemBonesController', 'DemBonesValidator', 'utils']


def show_ui():
    ui = DemBonesUI()
    ui.create()
    return ui
