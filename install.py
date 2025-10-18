"""
DemBones Maya Tool Installer
-----------------------------
Drag this file into Maya viewport to install.
Installs for ALL Maya versions (2018-2025)
"""

import os
import shutil
import sys
import maya.cmds as cmds # type: ignore
import maya.mel as mel # type: ignore


class DemBonesInstaller:
    
    TOOL_NAME = "dembones_maya_tool"
    PLUGIN_NAME = "DemBones.mll"
    ICON_NAME = "icon.png"
    SHELF_NAME = "CustomTools"
    
    def __init__(self):
        # Get installer directory
        self.installer_dir = os.path.dirname(__file__)
        self.plugin_source = os.path.join(self.installer_dir, self.PLUGIN_NAME)
        self.tool_source = os.path.join(self.installer_dir, self.TOOL_NAME)
        self.icon_source = os.path.join(self.installer_dir, self.ICON_NAME)
        
        # Get Maya documents directory
        self.maya_docs = os.path.expanduser("~/Documents/maya")
    
    def install(self):
        """Run complete installation"""
        print("\n" + "=" * 70)
        print("  DEM BONES MAYA TOOL - INSTALLER")
        print("=" * 70)
        
        # Validate source files
        if not self._validate_sources():
            return False
        
        # Install for all Maya versions
        versions = self._find_maya_versions()
        if not versions:
            print("\n[ERROR] No Maya versions found in: " + self.maya_docs)
            return False
        
        print("\nFound Maya versions: " + ", ".join(versions))
        
        for version in versions:
            self._install_for_version(version)
        
        # Create shelf button in current Maya session
        self._create_shelf_button()
        self._refresh_ui()
        

        
        print("\n" + "=" * 70)
        print("  ✅ INSTALLATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nTo use the tool:")
        print("  • Click the 'DemBones' shelf button")
        print("  • Or run in Script Editor: import dembones_maya_tool; dembones_maya_tool.show_ui()")
        print("\n" + "=" * 70 + "\n")
        
        return True
    
    def _validate_sources(self):
        """Validate source files exist"""
        errors = []
        
        if not os.path.exists(self.plugin_source):
            errors.append("Missing: " + self.PLUGIN_NAME)
        
        if not os.path.exists(self.tool_source):
            errors.append("Missing folder: " + self.TOOL_NAME)
        
        # Icon is optional - just warn if missing
        if not os.path.exists(self.icon_source):
            print("\n[WARNING] Icon file not found: " + self.ICON_NAME)
            print("  Button will use default icon")
        
        if errors:
            print("\n[ERROR] Installation failed!")
            for error in errors:
                print("  • " + error)
            print("\nMake sure these files are in the same directory as install.py:")
            print("  • " + self.PLUGIN_NAME)
            print("  • " + self.TOOL_NAME + "/ (folder)")
            print("  • " + self.ICON_NAME + " (optional)")
            return False
        
        return True
    
    def _find_maya_versions(self):
        """Find all installed Maya versions"""
        if not os.path.exists(self.maya_docs):
            return []
        
        versions = []
        for name in os.listdir(self.maya_docs):
            # Check if it's a year (2018-2025)
            if name.isdigit() and 2018 <= int(name) <= 2025:
                maya_dir = os.path.join(self.maya_docs, name)
                if os.path.isdir(maya_dir):
                    versions.append(name)
        
        return sorted(versions)
    
    def _install_for_version(self, version):
        """Install for specific Maya version"""
        print("\n--- Installing for Maya " + version + " ---")
        
        version_dir = os.path.join(self.maya_docs, version)
        plug_dir = os.path.join(version_dir, "plug-ins")
        scripts_dir = os.path.join(version_dir, "scripts")
        icons_dir = os.path.join(version_dir, "prefs", "icons")
        
        # Create directories if they don't exist
        os.makedirs(plug_dir, exist_ok=True)
        os.makedirs(scripts_dir, exist_ok=True)
        os.makedirs(icons_dir, exist_ok=True)
        
        # Copy plugin
        plugin_dest = os.path.join(plug_dir, self.PLUGIN_NAME)
        try:
            shutil.copy2(self.plugin_source, plugin_dest)
            print("  ✓ Plugin copied to: " + plug_dir)
            cmds.loadPlugin("DemBones.mll", quiet=True)
            cmds.pluginInfo("DemBones.mll", edit=True, autoload=True)
            
        except Exception as e:
            print("  ✗ Failed to copy plugin: " + str(e))

        plugin_dir = os.path.dirname(plugin_dest)
        if os.path.exists(plugin_dest):
            try:
                cmds.pluginInfo(addPluginPath=plugin_dir)
                cmds.loadPlugin(plugin_dest, quiet=False)
                cmds.pluginInfo(plugin_dest, edit=True, autoload=True)
                print("  ✓ Plugin loaded and set to auto-load")
            except Exception as e:
                print("  ✗ Failed to load or set autoload: " + str(e))

        
        # Copy tool folder
        tool_dest = os.path.join(scripts_dir, self.TOOL_NAME)
        try:
            # Remove existing installation
            if os.path.exists(tool_dest):
                shutil.rmtree(tool_dest)
            
            shutil.copytree(self.tool_source, tool_dest)
            print("  ✓ Tool copied to: " + scripts_dir)
        except Exception as e:
            print("  ✗ Failed to copy tool: " + str(e))
        
        # Copy icon
        if os.path.exists(self.icon_source):
            icon_dest = os.path.join(icons_dir, self.ICON_NAME)
            try:
                shutil.copy2(self.icon_source, icon_dest)
                print("  ✓ Icon copied to: " + icons_dir)
            except Exception as e:
                print("  ✗ Failed to copy icon: " + str(e))
    
    def _create_shelf_button(self):
        """Create shelf button in current Maya session"""
        print("\n--- Creating Shelf Button ---")
        
        try:
            # Get or create shelf
            top_level_shelf = mel.eval('$tempVar = $gShelfTopLevel')
            
            # Delete shelf if exists
            if cmds.shelfLayout(self.SHELF_NAME, exists=True, query=True):
                cmds.deleteUI(self.SHELF_NAME, layout=True)
            
            # Create new shelf
            shelf = cmds.shelfLayout(
                self.SHELF_NAME,
                parent=top_level_shelf
            )
            
            # Command to run
            command = '''import sys
import importlib

# Add to path if needed
scripts_dir = cmds.internalVar(userScriptDir=True)
tool_path = os.path.join(scripts_dir, 'dembones_maya_tool')
if tool_path not in sys.path:
    sys.path.insert(0, scripts_dir)

# Import and run
import dembones_maya_tool
importlib.reload(dembones_maya_tool)
dembones_maya_tool.show_ui()
'''
            
            # Determine icon path
            icon_path = "commandButton.png"  # Default
            prefs_icons = os.path.join(cmds.internalVar(userPrefDir=True), "icons", self.ICON_NAME)
            if os.path.exists(prefs_icons):
                icon_path = prefs_icons
                print("  ✓ Using custom icon: " + self.ICON_NAME)
            else:
                print("  ℹ Using default icon (custom icon not found)")
            
            # Create shelf button
            cmds.shelfButton(
                parent=shelf,
                label="DemBones",
                annotation="Open Dem Bones Tool - Auto Rigging",
                image=icon_path,
                imageOverlayLabel="",
                command=command,
                sourceType="python"
            )
            
            print("  ✓ Shelf '" + self.SHELF_NAME + "' created with button")
            
            # Save shelf
            try:
                mel.eval('saveAllShelves $gShelfTopLevel')
                print("  ✓ Shelf saved")
            except:
                pass
            
        except Exception as e:
            print("  ✗ Failed to create shelf button: " + str(e))

        
    def _refresh_ui(self):
        """Force Maya UI refresh"""
        print("\n--- Refreshing Maya UI ---")
        try:
            cmds.refresh(force=True)
            mel.eval("buildNewShelfTab $gShelfTopLevel;")  # rebuild shelf area
            mel.eval("restorePanelState all;")
            print("  ✓ UI refreshed successfully")
        except Exception as e:
            print("  ℹ UI refresh skipped: " + str(e))
            
def install():
    """Run installation"""
    installer = DemBonesInstaller()
    installer.install()


def onMayaDroppedPythonFile(*args):
    """Called when file is dragged into Maya viewport"""
    install()
    cmds.pluginInfo("DemBones.mll", edit=True, autoload=True)
    cmds.loadPlugin("DemBones.mll", quiet=True)
            


if __name__ == "__main__":
    install()