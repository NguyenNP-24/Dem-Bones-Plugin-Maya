"""
Utility functions for Dem Bones Maya Tool
"""
import maya.cmds as cmds # type: ignore


def get_short_name(full_path):
    """
    Get short name from full Maya path
    
    Args:
        full_path (str): Full path like |group|mesh
        
    Returns:
        str: Short name like 'mesh'
    """
    if not full_path:
        return ""
    return full_path.split('|')[-1]


def get_selected_mesh():
    """
    Get currently selected mesh with validation
    
    Returns:
        tuple: (success, full_path, message)
    """
    selection = cmds.ls(selection=True, type='transform', long=True)
    
    if not selection:
        return (False, None, "Please select a mesh")
    
    # Check if it has a mesh shape
    shapes = cmds.listRelatives(selection[0], shapes=True, type='mesh')
    if not shapes:
        return (False, None, "Selected object is not a mesh")
    
    return (True, selection[0], "Mesh selected successfully")


def check_topology_match(mesh1, mesh2):
    """
    Check if two meshes have matching topology
    
    Args:
        mesh1 (str): First mesh name
        mesh2 (str): Second mesh name
        
    Returns:
        tuple: (is_match, details_dict)
    """
    try:
        # Get topology info for mesh1
        vtx1 = cmds.polyEvaluate(mesh1, vertex=True)
        face1 = cmds.polyEvaluate(mesh1, face=True)
        edge1 = cmds.polyEvaluate(mesh1, edge=True)
        
        # Get topology info for mesh2
        vtx2 = cmds.polyEvaluate(mesh2, vertex=True)
        face2 = cmds.polyEvaluate(mesh2, face=True)
        edge2 = cmds.polyEvaluate(mesh2, edge=True)
        
        details = {
            'mesh1': {
                'name': get_short_name(mesh1),
                'vertices': vtx1,
                'faces': face1,
                'edges': edge1
            },
            'mesh2': {
                'name': get_short_name(mesh2),
                'vertices': vtx2,
                'faces': face2,
                'edges': edge2
            },
            'match': vtx1 == vtx2 and face1 == face2 and edge1 == edge2
        }
        
        # Print info
        print("=" * 50)
        print("Topology Check:")
        print("  {}: {} verts, {} faces, {} edges".format(
            details['mesh1']['name'], vtx1, face1, edge1))
        print("  {}: {} verts, {} faces, {} edges".format(
            details['mesh2']['name'], vtx2, face2, edge2))
        print("  Result: {}".format("MATCHED" if details['match'] else "NOT MATCHED"))
        print("=" * 50)
        
        return (details['match'], details)
        
    except Exception as e:
        print("Error checking topology: " + str(e))
        return (False, {'error': str(e)})


def get_timeline_range():
    """
    Get timeline start and end frame
    
    Returns:
        tuple: (start_frame, end_frame)
    """
    start = int(cmds.playbackOptions(query=True, minTime=True))
    end = int(cmds.playbackOptions(query=True, maxTime=True))
    return (start, end)


def load_dembones_plugin():
    """
    Load DemBones plugin if not loaded
    
    Returns:
        tuple: (success, message)
    """
    try:
        if not cmds.pluginInfo('DemBones', query=True, loaded=True):
            cmds.loadPlugin('DemBones')
            return (True, "DemBones plugin loaded successfully")
        return (True, "DemBones plugin already loaded")
    except Exception as e:
        error_msg = "Failed to load DemBones plugin: {}".format(str(e))
        return (False, error_msg)

def duplicate_static_meshes(*args):
    """
    Duplicate selected meshes as static copies at current frame.
    """
    sel = cmds.ls(sl=True, long=True)
    if not sel:
        cmds.warning("⚠️ No objects selected.")
        return []

    current_frame = cmds.currentTime(q=True)
    static_meshes = []

    for obj in sel:
        dup = cmds.duplicate(obj, name=f"{obj.split('|')[-1]}_static")[0]
        cmds.currentTime(current_frame)
        cmds.makeIdentity(dup, apply=True, t=1, r=1, s=1, n=0)
        cmds.delete(dup, ch=True)
        static_meshes.append(dup)

    cmds.select(static_meshes, r=True)
    print(f"✅ Created {len(static_meshes)} static meshes at frame {int(current_frame)}.")
    return static_meshes
