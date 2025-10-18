"""
DemBones Maya Tool Installer
-----------------------------
Drag this file into Maya viewport to install.
Installs for ALL Maya versions (2018-2025)
"""

import os
import shutil
import sys
import maya.cmds as cmds
import maya.mel as mel


class DemBonesInstaller:
    
    TOOL_NAME = "dembones_maya_tool"
    PLUGIN_NAME = "DemBones.mll"
    ICON_NAME = "icon.png"
    SHELF_NAME = "CustomTools"
    PLUGINS_DIR = "outputMll"
    
    def __init__(self):
        self.installer_dir = os.path.dirname(__file__)
        self.plugins_dir = os.path.join(self.installer_dir, self.PLUGINS_DIR)
        self.tool_source = os.path.join(self.installer_dir, self.TOOL_NAME)
        self.icon_source = os.path.join(self.installer_dir, self.ICON_NAME)
        self.maya_docs = os.path.expanduser("~/Documents/maya")
    
    def install(self):
        print("\n" + "=" * 70)
        print("  DEM BONES MAYA TOOL - INSTALLER")
        print("=" * 70)
        
        if not self._validate_sources():
            return False
        
        versions = self._find_maya_versions()
        if not versions:
            print("\n[ERROR] No Maya versions found in: " + self.maya_docs)
            return False
        
        print("\nFound Maya versions: " + ", ".join(versions))
        
        for version in versions:
            self._install_for_version(version)
        
        self._create_shelf_button()
        self._load_plugin_in_current_session()
        
        print("\n" + "=" * 70)
        print("  ✅ INSTALLATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nTo use the tool:")
        print("  • Click the 'DemBones' shelf button")
        print("  • Or run in Script Editor: import dembones_maya_tool; dembones_maya_tool.show_ui()")
        print("\n" + "=" * 70 + "\n")
        
        return True
    
    def _validate_sources(self):
        errors = []
        
        if not os.path.exists(self.plugins_dir):
            errors.append("Missing plugins folder: " + self.PLUGINS_DIR)
        else:
            mll_files = [f for f in os.listdir(self.plugins_dir) if f.endswith('.mll')]
            if not mll_files:
                errors.append("No .mll files found in: " + self.PLUGINS_DIR)
            else:
                print("\nFound plugin files:")
                for mll in sorted(mll_files):
                    print("  • " + mll)
        
        if not os.path.exists(self.tool_source):
            errors.append("Missing folder: " + self.TOOL_NAME)
        
        if not os.path.exists(self.icon_source):
            print("\n[WARNING] Icon file not found: " + self.ICON_NAME)
            print("  Button will use default icon")
        
        if errors:
            print("\n[ERROR] Installation failed!")
            for error in errors:
                print("  • " + error)
            return False
        
        return True
    
    def _find_maya_versions(self):
        if not os.path.exists(self.maya_docs):
            return []
        
        versions = []
        for name in os.listdir(self.maya_docs):
            if name.isdigit() and 2018 <= int(name) <= 2025:
                maya_dir = os.path.join(self.maya_docs, name)
                if os.path.isdir(maya_dir):
                    versions.append(name)
        
        return sorted(versions)
    
    def _find_plugin_for_version(self, version):
        if not os.path.exists(self.plugins_dir):
            return None
        
        exact_match = "DemBones_maya" + version + ".mll"
        exact_path = os.path.join(self.plugins_dir, exact_match)
        
        if os.path.exists(exact_path):
            return exact_path
        
        alt_match = "DemBones_" + version + ".mll"
        alt_path = os.path.join(self.plugins_dir, alt_match)
        
        if os.path.exists(alt_path):
            return alt_path
        
        generic_path = os.path.join(self.plugins_dir, "DemBones.mll")
        if os.path.exists(generic_path):
            print("  ℹ Using generic DemBones.mll")
            return generic_path
        
        return None
    
    def _install_for_version(self, version):
        print("\n--- Installing for Maya " + version + " ---")
        
        version_dir = os.path.join(self.maya_docs, version)
        plug_dir = os.path.join(version_dir, "plug-ins")
        scripts_dir = os.path.join(version_dir, "scripts")
        icons_dir = os.path.join(version_dir, "prefs", "icons")
        
        os.makedirs(plug_dir, exist_ok=True)
        os.makedirs(scripts_dir, exist_ok=True)
        os.makedirs(icons_dir, exist_ok=True)
        
        plugin_source = self._find_plugin_for_version(version)
        
        if plugin_source:
            plugin_dest = os.path.join(plug_dir, self.PLUGIN_NAME)
            try:
                shutil.copy2(plugin_source, plugin_dest)
                print("  ✓ Plugin copied: " + os.path.basename(plugin_source))
                print("    → " + plugin_dest)
            except Exception as e:
                print("  ✗ Failed to copy plugin: " + str(e))
        else:
            print("  ⚠ No plugin found for Maya " + version)
        
        tool_dest = os.path.join(scripts_dir, self.TOOL_NAME)
        try:
            if os.path.exists(tool_dest):
                shutil.rmtree(tool_dest)
            
            shutil.copytree(self.tool_source, tool_dest)
            print("  ✓ Tool copied to: " + scripts_dir)
        except Exception as e:
            print("  ✗ Failed to copy tool: " + str(e))
        
        if os.path.exists(self.icon_source):
            icon_dest = os.path.join(icons_dir, self.ICON_NAME)
            try:
                shutil.copy2(self.icon_source, icon_dest)
                print("  ✓ Icon copied to: " + icons_dir)
            except Exception as e:
                print("  ✗ Failed to copy icon: " + str(e))
    
    def _create_shelf_button(self):
        print("\n--- Creating Shelf Button ---")
        
        try:
            top_level_shelf = mel.eval('$tempVar = $gShelfTopLevel')
            
            if cmds.shelfLayout(self.SHELF_NAME, exists=True, query=True):
                cmds.deleteUI(self.SHELF_NAME, layout=True)
            
            shelf = cmds.shelfLayout(self.SHELF_NAME, parent=top_level_shelf)
            
            command = '''import sys
import importlib

scripts_dir = cmds.internalVar(userScriptDir=True)
tool_path = os.path.join(scripts_dir, 'dembones_maya_tool')
if tool_path not in sys.path:
    sys.path.insert(0, scripts_dir)

import dembones_maya_tool
importlib.reload(dembones_maya_tool)
dembones_maya_tool.show_ui()
'''
            
            icon_path = "commandButton.png"
            prefs_icons = os.path.join(cmds.internalVar(userPrefDir=True), "icons", self.ICON_NAME)
            if os.path.exists(prefs_icons):
                icon_path = prefs_icons
                print("  ✓ Using custom icon: " + self.ICON_NAME)
            else:
                print("  ℹ Using default icon")
            
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
            
            try:
                mel.eval('saveAllShelves $gShelfTopLevel')
                print("  ✓ Shelf saved")
            except:
                pass
            
        except Exception as e:
            print("  ✗ Failed to create shelf button: " + str(e))
    
    def _load_plugin_in_current_session(self):
        print("\n--- Loading Plugin in Current Session ---")
        
        try:
            maya_version = cmds.about(version=True)
            current_plug_dir = os.path.join(self.maya_docs, maya_version, "plug-ins")
            current_plugin = os.path.join(current_plug_dir, self.PLUGIN_NAME)
            
            if not os.path.exists(current_plugin):
                print("  ⚠ Plugin not installed for Maya " + maya_version)
                return
            
            try:
                if cmds.pluginInfo(self.PLUGIN_NAME, query=True, loaded=True):
                    print("  ℹ Plugin already loaded, reloading...")
                    cmds.unloadPlugin(self.PLUGIN_NAME)
                
                cmds.loadPlugin(current_plugin)
                print("  ✓ Plugin loaded: " + self.PLUGIN_NAME)
                
                cmds.pluginInfo(self.PLUGIN_NAME, edit=True, autoload=True)
                print("  ✓ Auto-load enabled")
                
                commands = cmds.pluginInfo(self.PLUGIN_NAME, query=True, command=True)
                if commands:
                    print("  ✓ Available commands: " + str(commands))
                else:
                    print("  ⚠ No commands found in plugin")
                    
            except Exception as e:
                print("  ✗ Failed to load plugin: " + str(e))
                
        except Exception as e:
            print("  ✗ Error: " + str(e))


def install():
    installer = DemBonesInstaller()
    installer.install()


def onMayaDroppedPythonFile(*args):
    install()


if __name__ == "__main__":
    install()