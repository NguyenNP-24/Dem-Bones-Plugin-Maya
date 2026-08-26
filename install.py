# -*- coding: utf-8 -*-
"""
DemBones Maya Tool Installer
Drag this file into Maya viewport to install.
"""
import os
import sys
import shutil
import maya.cmds as cmds
import maya.mel as mel


TOOL_NAME    = "dembones_maya_tool"
PLUGIN_NAME  = "DemBones.mll"
PLUGIN_SHORT = "DemBones"
SHELF_NAME   = "CustomTools"
ICON_NAME    = "icon.png"
PLUGINS_DIR  = "outputMll"


def _get_paths():
    scripts_dir = cmds.internalVar(userScriptDir=True)
    prefs_dir   = cmds.internalVar(userPrefDir=True)
    version_dir = os.path.dirname(scripts_dir.rstrip("/\\"))
    return {
        'scripts' : scripts_dir,
        'plug_ins': os.path.join(version_dir, "plug-ins"),
        'shelves' : os.path.join(prefs_dir, "shelves"),
        'icons'   : os.path.join(prefs_dir, "icons"),
    }


def _makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def _remove_file(path):
    if os.path.isfile(path):
        try:
            os.remove(path)
        except Exception:
            pass


def _remove_dir(path):
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except Exception:
            pass


def _find_plugin(plugins_dir, version):
    for name in [
        "DemBones_maya" + version + ".mll",
        "DemBones_" + version + ".mll",
        "DemBones.mll",
    ]:
        path = os.path.join(plugins_dir, name)
        if os.path.exists(path):
            return path
    return None


def install():
    installer_dir = os.path.dirname(__file__)
    plugins_dir   = os.path.join(installer_dir, PLUGINS_DIR)
    tool_source   = os.path.join(installer_dir, TOOL_NAME)
    icon_source   = os.path.join(installer_dir, ICON_NAME)

    print("\n" + "=" * 70)
    print("  DEM BONES MAYA TOOL - INSTALLER")
    print("=" * 70)

    maya_version = cmds.about(version=True)
    paths = _get_paths()

    print("\nInstalling for Maya " + maya_version)
    print("  Scripts : " + paths['scripts'])
    print("  Plug-ins: " + paths['plug_ins'])
    print("  Icons   : " + paths['icons'])

    # --- Validate source files ---
    errors = []
    if not os.path.isdir(plugins_dir):
        errors.append("Missing folder: " + PLUGINS_DIR)
    if not os.path.isdir(tool_source):
        errors.append("Missing folder: " + TOOL_NAME)
    if errors:
        msg = "Installation failed:\n\n" + "\n".join("- " + e for e in errors)
        print("\n[ERROR] " + " | ".join(errors))
        cmds.confirmDialog(
            title="DemBones Install Failed",
            message=msg,
            button=["OK"],
            defaultButton="OK",
            icon="critical"
        )
        return False

    mll_files = [f for f in os.listdir(plugins_dir) if f.endswith('.mll')]
    print("\nFound plugin files:")
    for f in sorted(mll_files):
        print("  * " + f)

    # =========================================================
    # STEP 1: Unload old plugin and clear module cache
    # =========================================================
    print("\n--- Cleaning Up Old Install ---")

    try:
        if cmds.pluginInfo(PLUGIN_SHORT, query=True, loaded=True):
            cmds.pluginInfo(PLUGIN_SHORT, edit=True, autoload=False)
            cmds.unloadPlugin(PLUGIN_SHORT, force=True)
            print("  [OK] Old plugin unloaded")
    except Exception:
        pass

    removed_modules = []
    for key in list(sys.modules.keys()):
        if key == TOOL_NAME or key.startswith(TOOL_NAME + "."):
            del sys.modules[key]
            removed_modules.append(key)
    if removed_modules:
        print("  [OK] Module cache cleared: " + ", ".join(removed_modules))

    # Remove old files on disk
    _remove_file(os.path.join(paths['plug_ins'], PLUGIN_NAME))
    _remove_dir(os.path.join(paths['scripts'], TOOL_NAME))

    # Remove old shelf from UI
    try:
        if cmds.shelfLayout(SHELF_NAME, exists=True, query=True):
            cmds.deleteUI(SHELF_NAME, layout=True)
            print("  [OK] Old shelf removed")
    except Exception:
        pass

    # =========================================================
    # STEP 2: Copy new files
    # =========================================================
    print("\n--- Installing Plugin ---")
    _makedirs(paths['plug_ins'])
    plugin_src = _find_plugin(plugins_dir, maya_version)
    if plugin_src:
        dest = os.path.join(paths['plug_ins'], PLUGIN_NAME)
        try:
            shutil.copy2(plugin_src, dest)
            print("  [OK] " + os.path.basename(plugin_src) + " -> " + dest)
        except Exception as e:
            print("  [FAIL] " + str(e))
    else:
        print("  [WARN] No .mll found for Maya " + maya_version)

    print("\n--- Installing Tool Scripts ---")
    _makedirs(paths['scripts'])
    dest = os.path.join(paths['scripts'], TOOL_NAME)
    # Safety: if old dir still exists after cleanup, force remove
    if os.path.isdir(dest):
        try:
            shutil.rmtree(dest)
        except Exception as e:
            print("  [FAIL] Cannot remove old tool folder: " + str(e))
            print("         Close any editors that have these files open and try again.")
            return False
    try:
        shutil.copytree(tool_source, dest)
        print("  [OK] -> " + dest)
    except Exception as e:
        print("  [FAIL] " + str(e))
        return False

    print("\n--- Installing Icon ---")
    if os.path.isfile(icon_source):
        _makedirs(paths['icons'])
        dest = os.path.join(paths['icons'], ICON_NAME)
        try:
            shutil.copy2(icon_source, dest)
            print("  [OK] -> " + dest)
        except Exception as e:
            print("  [FAIL] " + str(e))
    else:
        print("  [INFO] No icon file found (using default)")

    # =========================================================
    # STEP 3: Load plugin
    # =========================================================
    print("\n--- Loading Plugin ---")
    plugin_path = os.path.join(paths['plug_ins'], PLUGIN_NAME)
    try:
        cmds.loadPlugin(plugin_path)
        cmds.pluginInfo(PLUGIN_SHORT, edit=True, autoload=True)
        commands = cmds.pluginInfo(PLUGIN_SHORT, query=True, command=True)
        print("  [OK] Plugin loaded, autoload enabled")
        if commands:
            print("  [OK] Commands: " + str(commands))
    except Exception as e:
        print("  [FAIL] " + str(e))

    # =========================================================
    # STEP 4: Create shelf button
    # =========================================================
    print("\n--- Creating Shelf Button ---")
    try:
        top_level_shelf = mel.eval('$tempVar = $gShelfTopLevel')
        shelf = cmds.shelfLayout(SHELF_NAME, parent=top_level_shelf)

        icon_path = "commandButton.png"
        custom_icon = os.path.join(paths['icons'], ICON_NAME)
        if os.path.isfile(custom_icon):
            icon_path = custom_icon

        shelf_command = (
            'import sys\n'
            'import maya.cmds as cmds\n'
            'scripts_dir = cmds.internalVar(userScriptDir=True)\n'
            'if scripts_dir not in sys.path:\n'
            '    sys.path.insert(0, scripts_dir)\n'
            'import dembones_maya_tool\n'
            'import dembones_maya_tool.utils\n'
            'import dembones_maya_tool.validator\n'
            'import dembones_maya_tool.controller\n'
            'import dembones_maya_tool.ui\n'
            'try:\n'
            '    import importlib\n'
            '    importlib.reload(dembones_maya_tool.utils)\n'
            '    importlib.reload(dembones_maya_tool.validator)\n'
            '    importlib.reload(dembones_maya_tool.controller)\n'
            '    importlib.reload(dembones_maya_tool.ui)\n'
            '    importlib.reload(dembones_maya_tool)\n'
            'except AttributeError:\n'
            '    reload(dembones_maya_tool.utils)\n'
            '    reload(dembones_maya_tool.validator)\n'
            '    reload(dembones_maya_tool.controller)\n'
            '    reload(dembones_maya_tool.ui)\n'
            '    reload(dembones_maya_tool)\n'
            'dembones_maya_tool.show_ui()\n'
        )

        cmds.shelfButton(
            parent=shelf,
            label="DemBones",
            annotation="Open Dem Bones Tool",
            image=icon_path,
            imageOverlayLabel="",
            command=shelf_command,
            sourceType="python"
        )
        try:
            mel.eval('saveAllShelves $gShelfTopLevel')
            print("  [OK] Shelf created and saved")
        except Exception:
            print("  [OK] Shelf created")
    except Exception as e:
        print("  [FAIL] " + str(e))

    # =========================================================
    # STEP 5: Import fresh modules into current session
    # =========================================================
    print("\n--- Loading Tool into Session ---")
    try:
        if paths['scripts'] not in sys.path:
            sys.path.insert(0, paths['scripts'])
        import dembones_maya_tool
        import dembones_maya_tool.utils
        import dembones_maya_tool.validator
        import dembones_maya_tool.controller
        import dembones_maya_tool.ui
        try:
            import importlib
            importlib.reload(dembones_maya_tool.utils)
            importlib.reload(dembones_maya_tool.validator)
            importlib.reload(dembones_maya_tool.controller)
            importlib.reload(dembones_maya_tool.ui)
            importlib.reload(dembones_maya_tool)
        except AttributeError:
            reload(dembones_maya_tool.utils)
            reload(dembones_maya_tool.validator)
            reload(dembones_maya_tool.controller)
            reload(dembones_maya_tool.ui)
            reload(dembones_maya_tool)
        print("  [OK] All modules loaded")
    except Exception as e:
        print("  [FAIL] " + str(e))

    print("\n" + "=" * 70)
    print("  [DONE] INSTALLATION COMPLETE")
    print("=" * 70)
    print("\n  Click the 'DemBones' button in the '" + SHELF_NAME + "' shelf to open the tool.")
    print("\n" + "=" * 70 + "\n")

    cmds.confirmDialog(
        title="DemBones Installed",
        message=(
            "Installation complete!\n\n"
            "Click the 'DemBones' button in the\n"
            "'" + SHELF_NAME + "' shelf to open the tool."
        ),
        button=["OK"],
        defaultButton="OK",
        icon="information"
    )
    return True


def onMayaDroppedPythonFile(*args):
    install()


if __name__ == "__main__":
    install()
