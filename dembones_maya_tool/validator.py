"""
Input validation for Dem Bones Maya Tool
"""
import maya.cmds as cmds
from . import utils


class DemBonesValidator:
    """Validator for Dem Bones inputs"""
    
    @staticmethod
    def validate_mesh(mesh_path, mesh_type="mesh"):
        """
        Validate a single mesh
        
        Args:
            mesh_path (str): Full path to mesh
            mesh_type (str): Type description for error message
            
        Returns:
            list: List of error messages (empty if valid)
        """
        errors = []
        
        if not mesh_path:
            errors.append("{} is not set".format(mesh_type.capitalize()))
        elif not cmds.objExists(mesh_path):
            errors.append("{} does not exist".format(mesh_type.capitalize()))
        
        return errors
    
    @staticmethod
    def validate_frame_range(start_frame, end_frame):
        """
        Validate frame range
        
        Args:
            start_frame (int): Start frame
            end_frame (int): End frame
            
        Returns:
            list: List of error messages (empty if valid)
        """
        errors = []
        
        if start_frame >= end_frame:
            errors.append("Start frame ({}) must be less than end frame ({})".format(
                start_frame, end_frame))
        
        return errors
    
    @staticmethod
    def validate_parameters(global_iters, num_bones):
        """
        Validate algorithm parameters
        
        Args:
            global_iters (int): Number of global iterations
            num_bones (int): Number of bones to generate
            
        Returns:
            list: List of error messages (empty if valid)
        """
        errors = []
        
        if global_iters < 1:
            errors.append("Global iterations must be at least 1")
        
        if num_bones < 1:
            errors.append("Number of bones must be at least 1")
        
        return errors
    
    @staticmethod
    def validate_all(source_mesh, target_mesh, start_frame, end_frame, 
                     global_iters, num_bones, check_topology=True):
        """
        Validate all inputs
        
        Args:
            source_mesh (str): Source mesh path
            target_mesh (str): Target mesh path
            start_frame (int): Start frame
            end_frame (int): End frame
            global_iters (int): Global iterations
            num_bones (int): Number of bones
            check_topology (bool): Whether to check topology match
            
        Returns:
            tuple: (is_valid, error_list)
        """
        errors = []
        
        # Validate source mesh
        errors.extend(DemBonesValidator.validate_mesh(source_mesh, "Source mesh"))
        
        # Validate target mesh
        errors.extend(DemBonesValidator.validate_mesh(target_mesh, "Target mesh"))
        
        # Check if source and target are the same
        if source_mesh and target_mesh and source_mesh == target_mesh:
            errors.append("Source and target meshes cannot be the same")
        
        # Validate frame range
        errors.extend(DemBonesValidator.validate_frame_range(start_frame, end_frame))
        
        # Validate parameters
        errors.extend(DemBonesValidator.validate_parameters(global_iters, num_bones))
        
        # Check topology match
        if check_topology and source_mesh and target_mesh:
            if cmds.objExists(source_mesh) and cmds.objExists(target_mesh):
                is_match, details = utils.check_topology_match(source_mesh, target_mesh)
                if not is_match:
                    errors.append("Source and target meshes do not have matching topology")
        
        return (len(errors) == 0, errors)