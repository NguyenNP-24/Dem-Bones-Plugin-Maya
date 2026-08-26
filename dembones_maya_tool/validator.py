# -*- coding: utf-8 -*-
"""
Input validation for Dem Bones Maya Tool
"""
import maya.cmds as cmds
import dembones_maya_tool.utils as utils


class DemBonesValidator:

    @staticmethod
    def validate_mesh(mesh_path, mesh_type="mesh"):
        errors = []
        if not mesh_path:
            errors.append("{} is not set".format(mesh_type.capitalize()))
        elif not cmds.objExists(mesh_path):
            errors.append("{} does not exist".format(mesh_type.capitalize()))
        return errors

    @staticmethod
    def validate_frame_range(start_frame, end_frame):
        errors = []
        if start_frame >= end_frame:
            errors.append("Start frame ({}) must be less than end frame ({})".format(
                start_frame, end_frame))
        return errors

    @staticmethod
    def validate_parameters(global_iters, num_bones):
        errors = []
        if global_iters < 1:
            errors.append("Global iterations must be at least 1")
        if num_bones < 1:
            errors.append("Number of bones must be at least 1")
        return errors

    @staticmethod
    def validate_all(source_mesh, target_mesh, start_frame, end_frame,
                     global_iters, num_bones, check_topology=True):
        errors = []
        errors.extend(DemBonesValidator.validate_mesh(source_mesh, "Source mesh"))
        errors.extend(DemBonesValidator.validate_mesh(target_mesh, "Target mesh"))

        if source_mesh and target_mesh and source_mesh == target_mesh:
            errors.append("Source and target meshes cannot be the same")

        errors.extend(DemBonesValidator.validate_frame_range(start_frame, end_frame))
        errors.extend(DemBonesValidator.validate_parameters(global_iters, num_bones))

        if check_topology and source_mesh and target_mesh:
            if cmds.objExists(source_mesh) and cmds.objExists(target_mesh):
                is_match, _ = utils.check_topology_match(source_mesh, target_mesh)
                if not is_match:
                    errors.append("Source and target meshes do not have matching topology")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_root_parent(root_parent):
        """Return error string if root_parent is set but doesn't exist, else None."""
        if root_parent and not cmds.objExists(root_parent):
            return "Custom root parent '{}' does not exist in the scene".format(root_parent)
        return None

    @staticmethod
    def validate_sim_list(sim_entries):
        """
        Validate a list of simulation entries for Shared Skeleton mode.
        All sims must share the same vertex count (bind pose is auto-created
        from the first sim's start frame).

        Args:
            sim_entries: list of (mesh_path, src_start, src_end, clip_name)

        Returns:
            tuple: (is_valid, error_list)
        """
        errors = []

        if len(sim_entries) < 2:
            errors.append("Shared Skeleton mode requires at least 2 simulations")

        ref_vtx  = None
        ref_name = None
        for i, entry in enumerate(sim_entries):
            mesh_path, src_start, src_end, clip_name = entry
            label = "Sim {} ({})".format(i + 1, clip_name or mesh_path)

            mesh_errors = DemBonesValidator.validate_mesh(mesh_path, label)
            errors.extend(mesh_errors)

            if not mesh_errors and src_start >= src_end:
                errors.append("{}: start frame must be less than end frame".format(label))

            if not mesh_errors and cmds.objExists(mesh_path):
                vtx = cmds.polyEvaluate(mesh_path, vertex=True)
                if ref_vtx is None:
                    ref_vtx  = vtx
                    ref_name = label
                elif vtx != ref_vtx:
                    errors.append(
                        "{}: vertex count ({}) does not match {} ({})".format(
                            label, vtx, ref_name, ref_vtx))

        return (len(errors) == 0, errors)
