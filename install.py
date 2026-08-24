# -*- coding: utf-8 -*-
"""
DemBones Maya Tool Installer
-----------------------------
Drag this file into Maya viewport to install.
"""

import os
import shutil
import sys
import maya.cmds as cmds
import maya.mel as mel


def _makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


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

        # Use Maya's own API to get correct user directories for THIS running session
        self.scripts_dir = cmds.internalVar(userScriptDir=True)
        self.prefs_dir = cmds.internalVar(userPrefDir=True)
        self.icons_dir = os.path.join(self.prefs_dir, "icons")

        # Derive plug-ins dir: scripts_dir is .../maya/2020/scripts/
        # plug-ins is .../maya/2020/plug-ins/
        version_dir = os.path.dirname(self.scripts_dir.rstrip("/\\"))
        self.plug_dir = os.path.join(version_dir, "plug-ins")

    def install(self):
        print("\n" + "=" * 70)
        print("  DEM BONES MAYA TOOL - INSTALLER")
        print("=" * 70)

        maya_version = cmds.about(version=True)
        print("\nInstalling for Maya " + maya_version)
        print("  Scripts dir : " + self.scripts_dir)
        print("  Plug-ins dir: " + self.plug_dir)
        print("  Icons dir   : " + self.icons_dir)

        if not self._validate_sources():
            return False

        self._install_plugin(maya_version)
        self._install_tool()
        self._install_icon()
        self._create_shelf_button()
        self._load_plugin_in_current_session()

        print("\n" + "=" * 70)
        print("  [DONE] INSTALLATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nTo use the tool:")
        print("  * Click the 'DemBones' shelf button")
        print("  * Or run: import dembones_maya_tool; dembones_maya_tool.show_ui()")
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
                    print("  * " + mll)

        if not os.path.exists(self.tool_source):
            errors.append("Missing folder: " + self.TOOL_NAME)

        if not os.path.exists(self.icon_source):
            print("\n[WARNING] Icon not found: " + self.ICON_NAME + " (will use default)")

        if errors:
            print("\n[ERROR] Installation failed!")
            for error in errors:
                print("  * " + error)
            return False

        return True

    def _find_plugin_for_version(self, version):
        for name in ["DemBones_maya" + version + ".mll",
                     "DemBones_" + version + ".mll",
                     "DemBones.mll"]:
            path = os.path.join(self.plugins_dir, name)
            if os.path.exists(path):
                return path
        return None

    def _install_plugin(self, version):
        print("\n--- Installing Plugin ---")
        _makedirs(self.plug_dir)
        plugin_source = self._find_plugin_for_version(version)
        if not plugin_source:
            print("  [WARN] No .mll found for Maya " + version)
            return
        dest = os.path.join(self.plug_dir, self.PLUGIN_NAME)
        try:
            shutil.copy2(plugin_source, dest)
            print("  [OK] " + os.path.basename(plugin_source) + " -> " + dest)
        except Exception as e:
            print("  [FAIL] " + str(e))

    def _install_tool(self):
        print("\n--- Installing Tool Scripts ---")
        _makedirs(self.scripts_dir)
        dest = os.path.join(self.scripts_dir, self.TOOL_NAME)
        try:
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(self.tool_source, dest)
            print("  [OK] Tool copied -> " + dest)
        except Exception as e:
            print("  [FAIL] " + str(e))

    def _install_icon(self):
        if not os.path.exists(self.icon_source):
            return
        print("\n--- Installing Icon ---")
        _makedirs(self.icons_dir)
        dest = os.path.join(self.icons_dir, self.ICON_NAME)
        try:
            shutil.copy2(self.icon_source, dest)
            print("  [OK] Icon -> " + dest)
        except Exception as e:
            print("  [FAIL] " + str(e))

    def _create_shelf_button(self):
        print("\n--- Creating Shelf Button ---")
        try:
            top_level_shelf = mel.eval('$tempVar = $gShelfTopLevel')

            if cmds.shelfLayout(self.SHELF_NAME, exists=True, query=True):
                cmds.deleteUI(self.SHELF_NAME, layout=True)

            shelf = cmds.shelfLayout(self.SHELF_NAME, parent=top_level_shelf)

            command = (
                'import sys, os\n'
                'import maya.cmds as cmds\n'
                'scripts_dir = cmds.internalVar(userScriptDir=True)\n'
                'if scripts_dir not in sys.path:\n'
                '    sys.path.insert(0, scripts_dir)\n'
                'import dembones_maya_tool\n'
                'try:\n'
                '    import importlib; importlib.reload(dembones_maya_tool)\n'
                'except Exception:\n'
                '    reload(dembones_maya_tool)\n'
                'dembones_maya_tool.show_ui()\n'
            )

            icon_path = "commandButton.png"
            custom_icon = os.path.join(self.icons_dir, self.ICON_NAME)
            if os.path.exists(custom_icon):
                icon_path = custom_icon
                print("  [OK] Using custom icon")
            else:
                print("  [INFO] Using default icon")

            cmds.shelfButton(
                parent=shelf,
                label="DemBones",
                annotation="Open Dem Bones Tool - Auto Rigging",
                image=icon_path,
                imageOverlayLabel="",
                command=command,
                sourceType="python"
            )
            print("  [OK] Shelf '" + self.SHELF_NAME + "' created")

            try:
                mel.eval('saveAllShelves $gShelfTopLevel')
                print("  [OK] Shelf saved")
            except Exception:
                pass

        except Exception as e:
            print("  [FAIL] " + str(e))

    def _load_plugin_in_current_session(self):
        print("\n--- Loading Plugin ---")
        plugin_path = os.path.join(self.plug_dir, self.PLUGIN_NAME)
        if not os.path.exists(plugin_path):
            print("  [WARN] Plugin file not found: " + plugin_path)
            return
        try:
            if cmds.pluginInfo(self.PLUGIN_NAME, query=True, loaded=True):
                print("  [INFO] Already loaded, reloading...")
                cmds.unloadPlugin(self.PLUGIN_NAME)
            cmds.loadPlugin(plugin_path)
            print("  [OK] Plugin loaded")
            cmds.pluginInfo(self.PLUGIN_NAME, edit=True, autoload=True)
            print("  [OK] Auto-load enabled")
            commands = cmds.pluginInfo(self.PLUGIN_NAME, query=True, command=True)
            if commands:
                print("  [OK] Commands: " + str(commands))
            else:
                print("  [WARN] No commands registered by plugin")
        except Exception as e:
            print("  [FAIL] " + str(e))


def install():
    installer = DemBonesInstaller()
    installer.install()


def onMayaDroppedPythonFile(*args):
    install()


if __name__ == "__main__":
    install()
