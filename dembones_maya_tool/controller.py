# -*- coding: utf-8 -*-
"""
Controller/Business logic for Dem Bones Maya Tool
"""
import maya.cmds as cmds
import dembones_maya_tool.utils as utils
import dembones_maya_tool.validator as validator


def _apply_root_parent(joints_before, root_parent):
    """
    When root_parent is set: find the generated joint_root, move its children
    directly under root_parent, then delete joint_root.
    When root_parent is None: do nothing (joint_root stays as-is).
    Returns a short status string for the success message.
    """
    if not root_parent:
        return ""

    new_joints = set(cmds.ls(type='joint', long=True)) - joints_before
    if not new_joints:
        return ""

    # Find the top-level generated joint (joint_root) —
    # the new joint whose parent is NOT also a new joint
    joint_roots = []
    for j in new_joints:
        parents = cmds.listRelatives(j, parent=True, fullPath=True) or []
        parent_is_new_joint = parents and parents[0] in new_joints
        if not parent_is_new_joint:
            joint_roots.append(j)

    if not joint_roots:
        return ""

    try:
        for jroot in joint_roots:
            # Get direct children of joint_root
            children = cmds.listRelatives(jroot, children=True, fullPath=True) or []
            if children:
                cmds.parent(children, root_parent)
                names = [c.split('|')[-1] for c in children]
                print("  [OK] Parented {} under '{}'".format(names, root_parent))
            # Delete joint_root — it's now empty and replaced by root_parent
            cmds.delete(jroot)
            print("  [OK] Removed intermediate joint_root '{}'".format(
                jroot.split('|')[-1]))

        return " (parented under '{}')".format(root_parent)
    except Exception as e:
        print("  [WARN] Could not apply root parent: " + str(e))
        return ""


class DemBonesController:

    def __init__(self):
        self.source_mesh = ""
        self.target_mesh = ""

    def set_source_mesh_from_selection(self):
        success, full_path, message = utils.get_selected_mesh()
        if success:
            self.source_mesh = full_path
            short_name = utils.get_short_name(full_path)
            return (True, full_path, short_name, "Source mesh set: " + short_name)
        return (False, None, None, message)

    def validate_single(self, start_frame, end_frame, global_iters, num_bones):
        errors = []
        errors.extend(validator.DemBonesValidator.validate_mesh(
            self.source_mesh, "Source mesh"))
        errors.extend(validator.DemBonesValidator.validate_frame_range(
            start_frame, end_frame))
        errors.extend(validator.DemBonesValidator.validate_parameters(
            global_iters, num_bones))
        return (len(errors) == 0, errors)

    def run_dembones(self, start_frame, end_frame, global_iters, num_bones,
                     root_parent=None):
        success, message = utils.load_dembones_plugin()
        if not success:
            return (False, message)

        err = validator.DemBonesValidator.validate_root_parent(root_parent)
        if err:
            return (False, err)

        try:
            # Auto-create bind pose by duplicating sim at start_frame
            cmds.currentTime(start_frame)
            source_short = utils.get_short_name(self.source_mesh)
            bind_pose = cmds.duplicate(
                self.source_mesh,
                name=source_short + "_bindPose"
            )[0]
            cmds.delete(bind_pose, constructionHistory=True)
            print("  [OK] Bind pose created: '{}' (from frame {})".format(
                bind_pose, start_frame))

            joints_before = set(cmds.ls(type='joint', long=True))

            cmds.demBones(
                sourceMesh=self.source_mesh,
                targetMesh=bind_pose,
                startFrame=start_frame,
                endFrame=end_frame,
                globalIters=global_iters,
                numBones=num_bones
            )

            msg = _apply_root_parent(joints_before, root_parent)
            return (True, "SUCCESS! {} bones created on '{}'{}".format(
                num_bones, bind_pose, msg))
        except Exception as e:
            return (False, "Error running Dem Bones: {}".format(str(e)))

    def run_dembones_shared_skeleton(self, sim_entries,
                                     global_iters, num_bones, root_parent=None):
        """
        Generate a shared skeleton from multiple simulations.

        Concatenates all simulations onto a temporary proxy mesh, runs DemBones
        once across the full combined frame range, then removes the proxy.
        Result: one skeleton + one skinCluster, with each simulation occupying
        a distinct frame range (suitable for game-engine clip export).

        Bind pose is auto-created by duplicating the first sim mesh at its start frame.

        Args:
            sim_entries: list of (mesh_path, src_start, src_end, clip_name)
            global_iters, num_bones: DemBones parameters

        Returns:
            tuple: (success, message)
        """
        success, message = utils.load_dembones_plugin()
        if not success:
            return (False, message)

        err = validator.DemBonesValidator.validate_root_parent(root_parent)
        if err:
            return (False, err)

        is_valid, errors = validator.DemBonesValidator.validate_sim_list(sim_entries)
        if not is_valid:
            return (False, "Validation failed:\n" + "\n".join("- " + e for e in errors))

        # Auto-create bind pose from first sim at its start frame
        first_mesh, first_start, _, _ = sim_entries[0]
        cmds.currentTime(first_start)
        first_short = utils.get_short_name(first_mesh)
        target_mesh = cmds.duplicate(first_mesh, name=first_short + "_bindPose")[0]
        cmds.delete(target_mesh, constructionHistory=True)
        print("  [OK] Bind pose created: '{}' (from '{}' frame {})".format(
            target_mesh, first_short, first_start))

        # Build dst frame ranges — each sim is laid out consecutively starting at frame 1
        full_entries = []
        cursor = 1
        for mesh_path, src_start, src_end, clip_name in sim_entries:
            duration = src_end - src_start
            dst_start = cursor
            dst_end = cursor + duration
            full_entries.append((mesh_path, src_start, src_end, dst_start, dst_end, clip_name))
            cursor = dst_end + 1

        total_start = 1
        total_end = cursor - 1

        print("\nShared Skeleton — frame layout:")
        for _, _, _, dst_start, dst_end, clip_name in full_entries:
            print("  '{}': frames {} - {}".format(clip_name, dst_start, dst_end))

        proxy         = None
        cleanup_nodes = []
        abc_restore   = []
        try:
            joints_before = set(cmds.ls(type='joint', long=True))

            proxy, cleanup_nodes, abc_restore, frame_info = \
                utils.create_proxy_animated_mesh(full_entries, target_mesh)

            cmds.demBones(
                sourceMesh=proxy,
                targetMesh=target_mesh,
                startFrame=total_start,
                endFrame=total_end,
                globalIters=global_iters,
                numBones=num_bones
            )

            utils.cleanup_proxy(proxy, cleanup_nodes, abc_restore)

            parent_msg = _apply_root_parent(joints_before, root_parent)

            summary_lines = ["Shared skeleton generated ({} bones){}:".format(
                num_bones, parent_msg)]
            for clip_name, dst_start, dst_end in frame_info:
                summary_lines.append("  '{}': frames {} - {}".format(
                    clip_name, dst_start, dst_end))
            return (True, "\n".join(summary_lines))

        except Exception as e:
            utils.cleanup_proxy(proxy, cleanup_nodes, abc_restore)
            return (False, "Error in Shared Skeleton: {}".format(str(e)))
