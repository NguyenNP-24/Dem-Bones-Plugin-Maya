"""
Controller/Business logic for  Dem Bones Maya Tool
"""
import maya.cmds as cmds
from . import utils
from . import validator


class DemBonesController:
    """Controller for Dem Bones operations"""
    
    def __init__(self):
        self.source_mesh = ""
        self.target_mesh = ""
    
    def set_source_mesh_from_selection(self):
        """
        Set source mesh from current selection
        
        Returns:
            tuple: (success, full_path, short_name, message)
        """
        success, full_path, message = utils.get_selected_mesh()
        
        if success:
            self.source_mesh = full_path
            short_name = utils.get_short_name(full_path)
            return (True, full_path, short_name, "Source mesh set: " + short_name)
        else:
            return (False, None, None, message)
    
    def set_target_mesh_from_selection(self):
        """
        Set target mesh from current selection
        
        Returns:
            tuple: (success, full_path, short_name, message)
        """
        success, full_path, message = utils.get_selected_mesh()
        
        if success:
            self.target_mesh = full_path
            short_name = utils.get_short_name(full_path)
            return (True, full_path, short_name, "Target mesh set: " + short_name)
        else:
            return (False, None, None, message)
    
    def validate_inputs(self, start_frame, end_frame, global_iters, num_bones):
        """
        Validate all inputs before running
        
        Args:
            start_frame (int): Start frame
            end_frame (int): End frame
            global_iters (int): Global iterations
            num_bones (int): Number of bones
            
        Returns:
            tuple: (is_valid, error_list)
        """
        return validator.DemBonesValidator.validate_all(
            self.source_mesh,
            self.target_mesh,
            start_frame,
            end_frame,
            global_iters,
            num_bones,
            check_topology=True
        )
    
    def run_dembones(self, start_frame, end_frame, global_iters, num_bones):
        """
        Execute Dem Bones algorithm
        
        Args:
            start_frame (int): Start frame
            end_frame (int): End frame
            global_iters (int): Global iterations
            num_bones (int): Number of bones to generate
            
        Returns:
            tuple: (success, message)
        """
        # Load plugin
        success, message = utils.load_dembones_plugin()
        if not success:
            return (False, message)
        
        # Run Dem Bones
        try:
            cmds.demBones(
                sourceMesh=self.source_mesh,
                targetMesh=self.target_mesh,
                startFrame=start_frame,
                endFrame=end_frame,
                globalIters=global_iters,
                numBones=num_bones
            )
            
            target_name = utils.get_short_name(self.target_mesh)
            success_msg = "SUCCESS! {} bones created on '{}'".format(
                num_bones, target_name)
            
            return (True, success_msg)
            
        except Exception as e:
            error_msg = "Error running Dem Bones: {}".format(str(e))
            return (False, error_msg)
