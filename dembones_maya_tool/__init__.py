"""
Dem Bones Maya Tool
A tool for automatic rigging using Dem Bones algorithm

Author: Nguyen Phuc Nguyen
Version: 1.0.0
"""

from .ui import DemBonesUI
from .controller import DemBonesController
from .validator import DemBonesValidator
from . import utils

__version__ = "1.0.0"
__all__ = ['show_ui', 'DemBonesUI', 'DemBonesController', 'DemBonesValidator', 'utils']


def show_ui():
    """
    Show the Dem Bones tool UI
    
    Returns:
        DemBonesUI: The UI instance
    """
    ui = DemBonesUI()
    ui.create()
    return ui
