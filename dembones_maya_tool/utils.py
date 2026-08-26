# -*- coding: utf-8 -*-
"""
Utility functions for Dem Bones Maya Tool
"""
import maya.cmds as cmds


def get_short_name(full_path):
    if not full_path:
        return ""
    return full_path.split('|')[-1]


def get_selected_mesh():
    selection = cmds.ls(selection=True, type='transform', long=True)
    if not selection:
        return (False, None, "Please select a mesh")
    shapes = cmds.listRelatives(selection[0], shapes=True, type='mesh')
    if not shapes:
        return (False, None, "Selected object is not a mesh")
    return (True, selection[0], "Mesh selected successfully")


def get_selected_meshes():
    """Return list of full paths for all selected mesh transforms (skips non-meshes)."""
    selection = cmds.ls(selection=True, type='transform', long=True)
    meshes = []
    for obj in selection:
        shapes = cmds.listRelatives(obj, shapes=True, type='mesh')
        if shapes:
            meshes.append(obj)
    return meshes


def check_topology_match(mesh1, mesh2):
    try:
        vtx1  = cmds.polyEvaluate(mesh1, vertex=True)
        face1 = cmds.polyEvaluate(mesh1, face=True)
        edge1 = cmds.polyEvaluate(mesh1, edge=True)
        vtx2  = cmds.polyEvaluate(mesh2, vertex=True)
        face2 = cmds.polyEvaluate(mesh2, face=True)
        edge2 = cmds.polyEvaluate(mesh2, edge=True)
        details = {
            'mesh1': {'name': get_short_name(mesh1), 'vertices': vtx1, 'faces': face1, 'edges': edge1},
            'mesh2': {'name': get_short_name(mesh2), 'vertices': vtx2, 'faces': face2, 'edges': edge2},
            'match': vtx1 == vtx2 and face1 == face2 and edge1 == edge2
        }
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
    start = int(cmds.playbackOptions(query=True, minTime=True))
    end   = int(cmds.playbackOptions(query=True, maxTime=True))
    return (start, end)


def load_dembones_plugin():
    try:
        if not cmds.pluginInfo('DemBones', query=True, loaded=True):
            cmds.loadPlugin('DemBones')
            return (True, "DemBones plugin loaded successfully")
        return (True, "DemBones plugin already loaded")
    except Exception as e:
        return (False, "Failed to load DemBones plugin: {}".format(str(e)))


def duplicate_static_meshes(*args):
    sel = cmds.ls(sl=True, long=True)
    if not sel:
        cmds.warning("No objects selected.")
        return []
    current_frame = cmds.currentTime(q=True)
    static_meshes = []
    for obj in sel:
        dup = cmds.duplicate(obj, name="{}_static".format(obj.split('|')[-1]))[0]
        # Unlock transform attrs before freeze (skinned meshes have locked transforms)
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            try:
                cmds.setAttr(dup + '.' + attr, lock=False)
            except Exception:
                pass
        try:
            cmds.makeIdentity(dup, apply=True, t=1, r=1, s=1, n=0)
        except Exception:
            pass
        cmds.delete(dup, ch=True)
        static_meshes.append(dup)
    cmds.select(static_meshes, r=True)
    print("[OK] Created {} static meshes at frame {}.".format(
        len(static_meshes), int(current_frame)))
    return static_meshes


# ------------------------------------------------------------------
# Shared Skeleton helpers
# ------------------------------------------------------------------

def _find_alembic_node(mesh_transform):
    """Return the AlembicNode driving this mesh, or None."""
    shapes = cmds.listRelatives(mesh_transform, shapes=True, fullPath=True) or []
    for shape in shapes:
        history = cmds.listHistory(shape, pruneDagObjects=True) or []
        for node in history:
            if cmds.nodeType(node) == 'AlembicNode':
                return node
    return None


def create_proxy_animated_mesh(sim_entries, target_mesh):
    """
    Build a proxy mesh that plays each sim's animation in successive frame ranges.

    Root cause of the "frozen" bug: blendShapes are live — at scene frame 1201,
    the Flag_fall Alembic cache is still sampled at scene time 1201, which is past
    its 1-1200 range and gets clamped. Fix: retime each AlembicNode so it plays at
    (scene_time - dst_offset) instead of scene_time.

    Args:
        sim_entries: list of (mesh, src_start, src_end, dst_start, dst_end, clip_name)
        target_mesh: bind-pose mesh used as base shape

    Returns:
        (proxy, cleanup_nodes, alembic_restore_data, frame_range_info)
        alembic_restore_data: list of (time_attr, [original_plugs]) for cleanup
    """
    proxy = cmds.duplicate(target_mesh, name="demBones_proxy")[0]
    cmds.setAttr(proxy + ".visibility", 0)

    blendshape_nodes = []
    retime_nodes     = []
    alembic_restore  = []   # [(time_attr, [orig_plug, ...]), ...]
    frame_range_info = []

    for idx, entry in enumerate(sim_entries):
        sim_mesh, src_start, src_end, dst_start, dst_end, clip_name = entry

        # offset: when scene is at dst_start, Alembic should see src_start
        # => alembic_time = scene_time - (dst_start - src_start)
        offset = dst_start - src_start

        # --- Retime AlembicNode if found ---
        abc_node = _find_alembic_node(sim_mesh)
        if abc_node:
            time_attr = abc_node + '.time'
            orig_plugs = cmds.listConnections(
                time_attr, plugs=True, source=True, destination=False) or []

            if offset != 0:
                pma = cmds.createNode(
                    'plusMinusAverage', name='demBones_retime_{}'.format(idx))
                cmds.setAttr(pma + '.operation', 2)          # subtract
                cmds.connectAttr('time1.outTime', pma + '.input1D[0]')
                cmds.setAttr(pma + '.input1D[1]', float(offset))

                for plug in orig_plugs:
                    cmds.disconnectAttr(plug, time_attr)
                cmds.connectAttr(pma + '.output1D', time_attr)
                retime_nodes.append(pma)
                print("  [INFO] '{}' Alembic retimed by -{} frames".format(
                    clip_name, offset))
            else:
                print("  [INFO] '{}' Alembic no offset needed".format(clip_name))

            alembic_restore.append((time_attr, orig_plugs))
        else:
            print("  [WARN] '{}' has no AlembicNode — blendshape only "
                  "(animation may not remap correctly)".format(clip_name))

        # --- Blendshape: proxy tracks sim_mesh ---
        bs = cmds.blendShape(sim_mesh, proxy,
                              name="demBones_bs_{}".format(idx),
                              weight=(0, 0.0))[0]
        blendshape_nodes.append(bs)

        # Step-function keys: weight=1 inside dst range, 0 outside
        # Use 'step' tangents to avoid interpolation bleeding between sims
        if dst_start > 1:
            cmds.setKeyframe(bs, attribute="w[0]", value=0.0, time=dst_start - 1)
            cmds.keyTangent(bs, attribute="w[0]",
                            time=(dst_start - 1, dst_start - 1),
                            outTangentType='step')

        cmds.setKeyframe(bs, attribute="w[0]", value=1.0, time=dst_start)
        cmds.setKeyframe(bs, attribute="w[0]", value=1.0, time=dst_end)
        cmds.keyTangent(bs, attribute="w[0]",
                        time=(dst_end, dst_end),
                        outTangentType='step')
        cmds.setKeyframe(bs, attribute="w[0]", value=0.0, time=dst_end + 1)

        # Make sure all earlier blendshapes are 0 in this range
        for earlier_bs in blendshape_nodes[:-1]:
            cmds.setKeyframe(earlier_bs, attribute="w[0]", value=0.0, time=dst_start)
            cmds.setKeyframe(earlier_bs, attribute="w[0]", value=0.0, time=dst_end)
            cmds.keyTangent(earlier_bs, attribute="w[0]",
                            time=(dst_start, dst_start),
                            inTangentType='step', outTangentType='step')

        frame_range_info.append((clip_name, dst_start, dst_end))
        print("  Mapped '{}': src {}-{} -> proxy {}-{}".format(
            clip_name, src_start, src_end, dst_start, dst_end))

    cleanup_nodes = blendshape_nodes + retime_nodes
    return (proxy, cleanup_nodes, alembic_restore, frame_range_info)


def cleanup_proxy(proxy, cleanup_nodes, alembic_restore):
    """
    Remove proxy mesh and retime nodes, restore original Alembic time connections.
    """
    # Restore Alembic time connections BEFORE deleting retime nodes
    for time_attr, orig_plugs in alembic_restore:
        current = cmds.listConnections(
            time_attr, plugs=True, source=True, destination=False) or []
        for plug in current:
            try:
                cmds.disconnectAttr(plug, time_attr)
            except Exception:
                pass
        for plug in orig_plugs:
            try:
                node = plug.split('.')[0]
                if cmds.objExists(node):
                    cmds.connectAttr(plug, time_attr, force=True)
            except Exception:
                pass

    try:
        existing = [n for n in cleanup_nodes if cmds.objExists(n)]
        if existing:
            cmds.delete(existing)
    except Exception as e:
        print("[WARN] Cleanup error: " + str(e))

    try:
        if proxy and cmds.objExists(proxy):
            cmds.delete(proxy)
    except Exception as e:
        print("[WARN] Proxy delete error: " + str(e))
