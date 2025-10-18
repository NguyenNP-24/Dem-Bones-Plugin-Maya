"""
User Interface for Dem Bones Maya Tool
"""
import maya.cmds as cmds
from . import controller
from . import utils


class DemBonesUI:
    """UI for Dem Bones Tool"""
    
    WINDOW_NAME = "demBonesToolWindow"
    WINDOW_TITLE = "Dem Bones Tool - NguyenNP"
    
    def __init__(self):
        self.controller = controller.DemBonesController()
        self.widgets = {}
    
    def create(self):
        """Create and show the UI window"""
        # Delete existing window
        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME)
        
        # Create window
        window = cmds.window(
            self.WINDOW_NAME,
            title=self.WINDOW_TITLE,
            widthHeight=(500, 450),
            sizeable=True
        )
        
        # Build UI
        self._create_widgets()
        
        # Show window
        cmds.showWindow(window)
    
    def _create_widgets(self):
        """Create all UI widgets"""
        main_layout = cmds.columnLayout(
            adjustableColumn=True, 
            rowSpacing=10, 
            columnOffset=["both", 15]
        )
        
        cmds.separator(height=10, style='none')
        
        # Source Mesh Section
        self._create_mesh_section(
            "Source Mesh (Simulation):",
            'source_field',
            self._on_source_button_clicked
        )
        
        cmds.separator(height=5, style='none')
        
        # Target Mesh Section
        self._create_mesh_section(
            "Target Mesh (Output):",
            'target_field',
            self._on_target_button_clicked
        )
        
        cmds.separator(height=10, style='in')
        
        # Frame Range Section
        self._create_frame_range_section()
        
        cmds.separator(height=10, style='in')
        
        # Parameters Section
        self._create_parameters_section()
        
        cmds.separator(height=10, style='in')
        
        # Status Text
        self.widgets['status_text'] = cmds.text(
            label="", 
            align='center', 
            font='obliqueLabelFont', 
            height=30
        )
        
        cmds.separator(height=5, style='none')
        
        # Buttons
        self._create_buttons()
        
        cmds.separator(height=10, style='none')
    
    def _create_mesh_section(self, label, field_key, button_command):
        """Create a mesh selection section"""
        cmds.text(label=label, align='left', font='boldLabelFont')
        
        cmds.rowLayout(
            numberOfColumns=2, 
            columnWidth2=(400, 80), 
            adjustableColumn=1
        )
        
        self.widgets[field_key] = cmds.textField(
            placeholderText="Select mesh and click 'Get Selected'"
        )
        
        cmds.button(label="Get Selected", command=button_command)
        cmds.setParent('..')
    
    def _create_frame_range_section(self):
        """Create frame range section"""
        cmds.text(label="Frame Range:", align='left', font='boldLabelFont')
        
        cmds.rowLayout(
            numberOfColumns=5, 
            columnWidth5=(80, 80, 80, 80, 140)
        )
        
        cmds.text(label="Start Frame:")
        self.widgets['start_frame'] = cmds.intField(
            value=1, 
            minValue=-10000, 
            maxValue=10000
        )
        
        cmds.text(label="End Frame:")
        self.widgets['end_frame'] = cmds.intField(
            value=100, 
            minValue=-10000, 
            maxValue=10000
        )
        
        cmds.button(label="Use Timeline", command=self._on_timeline_button_clicked)
        cmds.setParent('..')
    
    def _create_parameters_section(self):
        """Create parameters section"""
        cmds.text(label="Parameters:", align='left', font='boldLabelFont')
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(200, 100))
        cmds.text(label="Global Iterations:", align='left')
        self.widgets['global_iters'] = cmds.intField(
            value=50, 
            minValue=1, 
            maxValue=1000
        )
        cmds.setParent('..')
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(200, 100))
        cmds.text(label="Number of Bones:", align='left')
        self.widgets['num_bones'] = cmds.intField(
            value=12, 
            minValue=1, 
            maxValue=100
        )
        cmds.setParent('..')
    
    def _create_buttons(self):
        """Create action buttons"""
        cmds.rowLayout(
            numberOfColumns=2, 
            columnWidth2=(240, 240), 
            adjustableColumn=1, 
            columnAttach=[(1, 'both', 5), (2, 'both', 5)]
        )
        
        cmds.button(
            label="GENERATE BONES",
            height=50,
            backgroundColor=[0.3, 0.7, 0.3],
            command=self._on_generate_button_clicked
        )
        
        cmds.button(
            label="Close",
            height=50,
            command=self._on_close_button_clicked
        )
        
        cmds.setParent('..')
    
    # Event Handlers
    
    def _on_source_button_clicked(self, *args):
        """Handle source mesh button click"""
        success, full_path, short_name, message = \
            self.controller.set_source_mesh_from_selection()
        
        if success:
            cmds.textField(self.widgets['source_field'], edit=True, text=short_name)
            self._show_success(message)
        else:
            self._show_error(message)
    
    def _on_target_button_clicked(self, *args):
        """Handle target mesh button click"""
        success, full_path, short_name, message = \
            self.controller.set_target_mesh_from_selection()
        
        if success:
            cmds.textField(self.widgets['target_field'], edit=True, text=short_name)
            self._show_success(message)
        else:
            self._show_error(message)
    
    def _on_timeline_button_clicked(self, *args):
        """Handle timeline button click"""
        start, end = utils.get_timeline_range()
        
        cmds.intField(self.widgets['start_frame'], edit=True, value=start)
        cmds.intField(self.widgets['end_frame'], edit=True, value=end)
        
        self._show_success("Frame range set: {} - {}".format(start, end))
    
    def _on_generate_button_clicked(self, *args):
        """Handle generate button click"""
        # Get parameters from UI
        start_frame = cmds.intField(self.widgets['start_frame'], query=True, value=True)
        end_frame = cmds.intField(self.widgets['end_frame'], query=True, value=True)
        global_iters = cmds.intField(self.widgets['global_iters'], query=True, value=True)
        num_bones = cmds.intField(self.widgets['num_bones'], query=True, value=True)
        
        # Validate inputs
        is_valid, errors = self.controller.validate_inputs(
            start_frame, end_frame, global_iters, num_bones
        )
        
        if not is_valid:
            error_msg = "Validation Errors:\n\n" + "\n".join("- " + e for e in errors)
            self._show_error(error_msg)
            cmds.confirmDialog(
                title='Validation Error',
                message=error_msg,
                button=['OK'],
                defaultButton='OK',
                icon='critical'
            )
            return
        
        # Show processing status
        self._show_info("Processing... Please wait")
        cmds.refresh()
        
        # Run Dem Bones
        success, message = self.controller.run_dembones(
            start_frame, end_frame, global_iters, num_bones
        )
        
        if success:
            self._show_success(message)
            cmds.confirmDialog(
                title='Success',
                message=message,
                button=['OK'],
                defaultButton='OK',
                icon='information'
            )
        else:
            self._show_error(message)
            cmds.confirmDialog(
                title='Error',
                message=message,
                button=['OK'],
                defaultButton='OK',
                icon='critical'
            )
    
    def _on_close_button_clicked(self, *args):
        """Handle close button click"""
        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME)
    
    # Status Display Methods
    
    def _show_error(self, message):
        """Show error message in status bar"""
        cmds.text(
            self.widgets['status_text'], 
            edit=True, 
            label="ERROR: " + message, 
            backgroundColor=[0.8, 0.3, 0.3]
        )
        cmds.warning(message)
    
    def _show_success(self, message):
        """Show success message in status bar"""
        cmds.text(
            self.widgets['status_text'], 
            edit=True, 
            label=message, 
            backgroundColor=[0.3, 0.7, 0.3]
        )
    
    def _show_info(self, message):
        """Show info message in status bar"""
        cmds.text(
            self.widgets['status_text'], 
            edit=True, 
            label=message, 
            backgroundColor=[0.3, 0.5, 0.8]
        )