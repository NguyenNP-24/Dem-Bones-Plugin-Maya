"""
Reload Dem Bones Tool in Maya
Copy and paste this code into Maya Script Editor
"""

import sys
import importlib

# Add tool path if not already in sys.path
tool_path = "D:/"
if tool_path not in sys.path:
    sys.path.insert(0, tool_path)

# Import main module
import dembones_maya_tool

# Reload all submodules
importlib.reload(dembones_maya_tool.utils)
importlib.reload(dembones_maya_tool.validator)
importlib.reload(dembones_maya_tool.controller)
importlib.reload(dembones_maya_tool.ui)
importlib.reload(dembones_maya_tool)

# Show UI
dembones_maya_tool.show_ui()

print("Dem Bones Tool reloaded successfully!")
