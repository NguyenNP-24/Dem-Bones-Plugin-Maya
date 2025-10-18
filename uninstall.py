"""
DemBones Maya Tool Uninstaller
-------------------------------
Drag this file into Maya viewport to uninstall.
Removes tool from ALL Maya versions (2018–2025)
"""

import os
import shutil
import maya.cmds as cmds # type: ignore
import maya.mel as mel # type: ignore


class DemBonesUninstaller:
    
    TOOL_NAME = "dembones_maya_tool"
    PLUGIN_NAME = "DemBones.mll"
    SHELF_NAME = "DemBones"
    
    def __init__(self):
        self.maya_docs = os.path.expanduser("~/Documents/maya")
    
    def uninstall(self):
        """Run complete uninstallation"""
        print("\n" + "=" * 70)
        print("  DEM BONES MAYA TOOL - UNINSTALLER")
        print("=" * 70)
        
        versions = self._find_maya_versions()
        if not versions:
            print("\n[WARNING] No Maya versions found in: " + self.maya_docs)
        else:
            print("\nFound Maya versions: " + ", ".join(versions))
            for version in versions:
                self._uninstall_for_version(version)
        
        self._remove_shelf()
        self._unload_plugin()
        self._refresh_ui()

        print("\n" + "=" * 70)
        print("  ✅ UNINSTALLATION COMPLETED SUCCESSFULLY!")
        print("=" * 70 + "\n")
        
        return True
    
    # ---------------------------------------------------------
    def _find_maya_versions(self):
        if not os.path.exists(self.maya_docs):
            return []
        
        versions = []
        for name in os.listdir(self.maya_docs):
            if name.isdigit() and 2018 <= int(name) <= 2025:
                path = os.path.join(self.maya_docs, name)
                if os.path.isdir(path):
                    versions.append(name)
        return sorted(versions)
    
    # ---------------------------------------------------------
    def _uninstall_for_version(self, version):
        print("\n--- Uninstalling from Maya " + version + " ---")
        
        version_dir = os.path.join(self.maya_docs, version)
        plug_dir = os.path.join(version_dir, "plug-ins")
        scripts_dir = os.path.join(version_dir, "scripts")
        shelf_dir = os.path.join(version_dir, "prefs", "shelves")
        icons_dir = os.path.join(version_dir, "prefs", "icons")
        
        removed_items = []
        
        # Remove plugin
        plugin_path = os.path.join(plug_dir, self.PLUGIN_NAME)
        if os.path.exists(plugin_path):
            try:
                os.remove(plugin_path)
                removed_items.append("Plugin")
            except PermissionError:
                print("  ✗ Permission denied removing plugin. Try running Maya as Administrator.")
            except Exception as e:
                print("  ✗ Failed to remove plugin: " + str(e))
        
        # Remove tool folder
        tool_path = os.path.join(scripts_dir, self.TOOL_NAME)
        if os.path.exists(tool_path):
            try:
                shutil.rmtree(tool_path)
                removed_items.append("Tool folder")
            except PermissionError:
                print("  ✗ Permission denied removing tool folder. Try running Maya as Administrator.")
            except Exception as e:
                print("  ✗ Failed to remove tool folder: " + str(e))
        
        # Remove shelf file
        shelf_file = os.path.join(shelf_dir, "shelf_" + self.SHELF_NAME + ".mel")
        if os.path.exists(shelf_file):
            try:
                os.remove(shelf_file)
                removed_items.append("Shelf file")
            except PermissionError:
                print("  ✗ Permission denied removing shelf file. Try running Maya as Administrator.")
            except Exception as e:
                print("  ✗ Failed to remove shelf file: " + str(e))
        
        # Remove custom icons
        if os.path.exists(icons_dir):
            for file in os.listdir(icons_dir):
                if "dembones" in file.lower():
                    try:
                        os.remove(os.path.join(icons_dir, file))
                        removed_items.append("Icon (" + file + ")")
                    except Exception:
                        pass
        
        if removed_items:
            print("  ✓ Removed: " + ", ".join(removed_items))
        else:
            print("  ℹ Nothing to remove (already clean)")
    
    # ---------------------------------------------------------
    def _remove_shelf(self):
        print("\n--- Removing Shelf from Current Session ---")
        
        try:
            if cmds.shelfLayout(self.SHELF_NAME, exists=True):
                # remove buttons first
                children = cmds.shelfLayout(self.SHELF_NAME, q=True, ca=True) or []
                for c in children:
                    try:
                        cmds.deleteUI(c)
                    except:
                        pass
                cmds.deleteUI(self.SHELF_NAME, layout=True)
                print(f"  ✓ Shelf '{self.SHELF_NAME}' removed")
                
                try:
                    mel.eval('saveAllShelves $gShelfTopLevel')
                except:
                    pass
            else:
                print("  ℹ Shelf not found in current session")
        except Exception as e:
            print("  ✗ Failed to remove shelf: " + str(e))
    
    # ---------------------------------------------------------
    def _unload_plugin(self):
        print("\n--- Unloading Plugin from Current Session ---")
        try:
            plugin_short = self.PLUGIN_NAME.replace(".mll", "")
            if cmds.pluginInfo(plugin_short, q=True, loaded=True):
                cmds.unloadPlugin(plugin_short)
                print(f"  ✓ Plugin '{plugin_short}' unloaded")
            else:
                print("  ℹ Plugin not loaded in current session")
        except Exception:
            print("  ℹ Plugin not found or already unloaded")
    
    # ---------------------------------------------------------
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


# =============================================================
def uninstall():
    DemBonesUninstaller().uninstall()


def onMayaDroppedPythonFile(*args):
    uninstall()


if __name__ == "__main__":
    uninstall()
