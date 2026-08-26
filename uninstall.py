# -*- coding: utf-8 -*-
"""
DemBones Maya Tool Uninstaller
Drag this file into Maya viewport to uninstall.
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


def _remove_file(path):
    if os.path.isfile(path):
        try:
            os.remove(path)
            print("  [OK] Removed file: " + path)
            return True
        except Exception as e:
            print("  [FAIL] " + path + " -> " + str(e))
    return False


def _remove_dir(path):
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
            print("  [OK] Removed folder: " + path)
            return True
        except Exception as e:
            print("  [FAIL] " + path + " -> " + str(e))
    return False


def uninstall():
    print("\n" + "=" * 70)
    print("  DEM BONES MAYA TOOL - UNINSTALLER")
    print("=" * 70)

    paths = _get_paths()

    # 1. Disable autoload and unload plugin from session
    print("\n--- Unloading Plugin ---")
    try:
        if cmds.pluginInfo(PLUGIN_SHORT, query=True, loaded=True):
            cmds.pluginInfo(PLUGIN_SHORT, edit=True, autoload=False)
            cmds.unloadPlugin(PLUGIN_SHORT, force=True)
            print("  [OK] Plugin unloaded and autoload disabled")
        else:
            # Still disable autoload even if not loaded
            try:
                cmds.pluginInfo(PLUGIN_SHORT, edit=True, autoload=False)
            except Exception:
                pass
            print("  [INFO] Plugin was not loaded")
    except Exception as e:
        print("  [INFO] " + str(e))

    # 2. Clear Python module cache so stale imports can't persist
    print("\n--- Clearing Module Cache ---")
    removed_modules = []
    for key in list(sys.modules.keys()):
        if key == TOOL_NAME or key.startswith(TOOL_NAME + "."):
            del sys.modules[key]
            removed_modules.append(key)
    if removed_modules:
        print("  [OK] Cleared: " + ", ".join(removed_modules))
    else:
        print("  [INFO] No cached modules found")

    # 3. Remove files from disk
    print("\n--- Removing Files ---")
    _remove_file(os.path.join(paths['plug_ins'], PLUGIN_NAME))
    _remove_dir(os.path.join(paths['scripts'], TOOL_NAME))
    _remove_file(os.path.join(paths['icons'], ICON_NAME))
    _remove_file(os.path.join(paths['shelves'], "shelf_" + SHELF_NAME + ".mel"))

    # 4. Remove shelf from live UI
    print("\n--- Removing Shelf ---")
    try:
        if cmds.shelfLayout(SHELF_NAME, exists=True, query=True):
            cmds.deleteUI(SHELF_NAME, layout=True)
            print("  [OK] Shelf '" + SHELF_NAME + "' removed from UI")
            try:
                mel.eval('saveAllShelves $gShelfTopLevel')
            except Exception:
                pass
        else:
            print("  [INFO] Shelf not present in current session")
    except Exception as e:
        print("  [FAIL] " + str(e))

    # 5. Refresh UI
    try:
        cmds.refresh(force=True)
    except Exception:
        pass

    print("\n" + "=" * 70)
    print("  [DONE] UNINSTALLATION COMPLETE")
    print("=" * 70 + "\n")

    cmds.confirmDialog(
        title="DemBones Uninstalled",
        message="DemBones Tool has been removed successfully.",
        button=["OK"],
        defaultButton="OK",
        icon="information"
    )


def onMayaDroppedPythonFile(*args):
    uninstall()


if __name__ == "__main__":
    uninstall()
