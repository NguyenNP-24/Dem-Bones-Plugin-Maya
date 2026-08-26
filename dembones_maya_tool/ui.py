# -*- coding: utf-8 -*-
"""
User Interface for Dem Bones Maya Tool
"""
import maya.cmds as cmds
import dembones_maya_tool.controller as controller
import dembones_maya_tool.utils as utils


class DemBonesUI:

    WINDOW_NAME  = "demBonesToolWindow"
    WINDOW_TITLE = "Dem Bones Tool - NguyenNP"

    def __init__(self):
        self.controller = controller.DemBonesController()
        self.widgets    = {}
        self._sim_rows  = []

    # ------------------------------------------------------------------
    # Window
    # ------------------------------------------------------------------

    def create(self):
        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME)

        cmds.window(
            self.WINDOW_NAME,
            title=self.WINDOW_TITLE,
            width=520,
            sizeable=True
        )

        self._create_widgets()
        cmds.showWindow(self.WINDOW_NAME)

    # ------------------------------------------------------------------
    # Build layout
    # ------------------------------------------------------------------

    def _create_widgets(self):
        cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnOffset=["both", 12])
        cmds.separator(height=8, style='none')

        # --- Mode toggle ---
        self.widgets['shared_check'] = cmds.checkBox(
            label="Shared Skeleton Mode  (multiple simulations -> one rig)",
            value=False,
            changeCommand=self._on_mode_changed,
            annotation=(
                "OFF: one simulation mesh -> one skeleton.\n"
                "ON: multiple simulation meshes (same topology) share one skeleton.\n"
                "Each sim becomes a separate animation clip on the same rig."
            )
        )

        cmds.separator(height=6, style='in')

        # --- Single mode section ---
        self.widgets['single_section'] = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=6)

        self._create_mesh_section(
            "Source Mesh (Simulation):", 'source_field',
            self._on_source_button_clicked,
            field_tip="The animated/simulated mesh DemBones will learn from.\nA static bind-pose copy will be created automatically at the start frame.",
            btn_tip="Select the simulation mesh in the viewport, then click here."
        )
        cmds.text(
            label="Bind pose will be auto-created from start frame.",
            align='left',
            font='smallObliqueLabelFont',
            annotation="The tool duplicates the sim mesh at the start frame as the bind pose target.\nThe skin cluster and bones will be applied to that duplicate."
        )

        cmds.separator(height=6, style='in')
        self._create_frame_range_section()
        cmds.setParent('..')  # end single_section

        # --- Shared mode section (hidden by default) ---
        self.widgets['shared_section'] = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=6, visible=False)

        cmds.text(
            label="Bind pose is auto-created from the first simulation at its start frame.",
            align='left',
            font='smallObliqueLabelFont'
        )

        cmds.separator(height=4, style='in')
        cmds.text(
            label="Simulations:",
            align='left',
            font='boldLabelFont',
            annotation=(
                "Add one row per simulation clip.\n"
                "All meshes must share the same vertex count as the bind-pose mesh."
            )
        )

        self.widgets['sim_scroll'] = cmds.scrollLayout(
            horizontalScrollBarThickness=0,
            verticalScrollBarThickness=8,
            height=160
        )
        self.widgets['sim_column'] = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=4)
        cmds.setParent('..')  # end sim_column
        cmds.setParent('..')  # end sim_scroll

        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=(260, 220),
            adjustableColumn=1,
            columnAttach=[(1, 'both', 0), (2, 'both', 4)]
        )
        cmds.button(
            label="+ Add Simulation",
            height=26,
            backgroundColor=[0.25, 0.45, 0.65],
            command=self._on_add_sim_clicked,
            annotation=(
                "Add a new simulation row.\n"
                "Set the mesh, clip name, and source frame range for each simulation."
            )
        )
        cmds.button(
            label="Use Timeline (all)",
            height=26,
            command=self._on_shared_timeline_clicked,
            annotation="Apply Maya's current playback range to all simulation rows at once."
        )
        cmds.setParent('..')  # end button row

        cmds.setParent('..')  # end shared_section

        cmds.separator(height=6, style='in')

        # --- Parameters ---
        self._create_parameters_section()

        cmds.separator(height=6, style='in')

        # Status bar
        self.widgets['status_text'] = cmds.text(
            label="Ready.",
            align='center',
            font='obliqueLabelFont',
            height=28,
            backgroundColor=[0.22, 0.22, 0.22],
            annotation="Status / last operation result."
        )

        cmds.separator(height=4, style='none')

        # Action buttons
        self._create_buttons()

        cmds.separator(height=8, style='none')

    def _create_mesh_section(self, label, field_key, button_command,
                              field_tip="", btn_tip=""):
        cmds.text(label=label, align='left', font='boldLabelFont',
                  annotation=field_tip)
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(390, 90), adjustableColumn=1)
        self.widgets[field_key] = cmds.textField(
            placeholderText="Select mesh, then click 'Get Selected'",
            annotation=field_tip
        )
        cmds.button(label="Get Selected", command=button_command,
                    annotation=btn_tip or "Select the mesh in viewport, then click.")
        cmds.setParent('..')

    def _create_frame_range_section(self):
        cmds.text(
            label="Frame Range:", align='left', font='boldLabelFont',
            annotation="Start and end frame of the simulation to extract bones from."
        )
        # Mirror Parameters column widths (80|80|105|80) so fields align vertically
        cmds.rowLayout(
            numberOfColumns=5,
            columnWidth5=(80, 80, 105, 80, 147),
            columnAttach=[
                (1, 'right', 6),
                (2, 'both',  2),
                (3, 'right', 6),
                (4, 'both',  2),
                (5, 'both',  2),
            ]
        )
        cmds.text(
            label="Start Frame:",
            annotation="First frame of the animation range."
        )
        self.widgets['start_frame'] = cmds.intField(
            value=1, minValue=-10000, maxValue=10000,
            annotation="First frame of the animation range."
        )
        cmds.text(
            label="End Frame:",
            annotation="Last frame of the animation range."
        )
        self.widgets['end_frame'] = cmds.intField(
            value=100, minValue=-10000, maxValue=10000,
            annotation="Last frame of the animation range."
        )
        cmds.button(
            label="Use Timeline",
            command=self._on_timeline_button_clicked,
            annotation="Auto-fill Start/End from Maya's current playback range."
        )
        cmds.setParent('..')

    def _create_parameters_section(self):
        cmds.text(
            label="Parameters:", align='left', font='boldLabelFont',
            annotation="DemBones algorithm settings."
        )

        # 4-column grid: label | field | label | field
        # columnAttach right-aligns labels so they sit flush against their fields
        cmds.rowLayout(
            numberOfColumns=4,
            columnWidth4=(80, 80, 105, 80),
            columnAttach=[
                (1, 'right', 6),
                (2, 'both',  2),
                (3, 'right', 6),
                (4, 'both',  2),
            ]
        )
        cmds.text(
            label="Quality:",
            annotation=(
                "Optimization quality (Global Iterations).\n"
                "Higher = better bone placement but slower.\n"
                "Draft: 20  |  Good: 50  |  Best: 100+"
            )
        )
        self.widgets['global_iters'] = cmds.intField(
            value=20, minValue=1, maxValue=1000,
            annotation=(
                "Optimization quality (Global Iterations).\n"
                "Higher = better bone placement but slower.\n"
                "Draft: 20  |  Good: 50  |  Best: 100+"
            )
        )
        cmds.text(
            label="Num Bones:",
            annotation=(
                "Number of bones to generate.\n"
                "More bones = finer deformation but heavier rig.\n"
                "Typical range: 8 - 64."
            )
        )
        self.widgets['num_bones'] = cmds.intField(
            value=12, minValue=1, maxValue=9999,
            annotation=(
                "Number of bones to generate.\n"
                "More bones = finer deformation but heavier rig.\n"
                "Typical range: 8 - 64."
            )
        )
        cmds.setParent('..')

        cmds.text(
            label="Tip: Quality=20 for draft (fast),  50+ for final export.",
            align='left',
            font='smallObliqueLabelFont',
            annotation="Lower iterations are fine for quick previews; raise to 50+ for final export."
        )

        cmds.separator(height=6, style='in')

        # --- Custom root parent — flat 3-column row ---
        # checkbox(155) | textField(adjustable) | button(90)
        cmds.rowLayout(
            numberOfColumns=3,
            columnWidth3=(155, 251, 90),
            adjustableColumn=2,
            columnAttach=[
                (1, 'both', 0),
                (2, 'both', 4),
                (3, 'both', 0),
            ]
        )
        self.widgets['root_parent_check'] = cmds.checkBox(
            label="Custom Root Parent:",
            value=False,
            changeCommand=self._on_root_parent_toggled,
            annotation=(
                "When enabled, the generated root joint will be parented\n"
                "under the specified object (mesh, joint, group, curve, etc.).\n"
                "When disabled, the root joint sits at world origin."
            )
        )
        self.widgets['root_parent_field'] = cmds.textField(
            placeholderText="Select object, then click 'Get Selected'",
            enable=False,
            annotation=(
                "Any scene object — mesh, joint, group, curve, locator, etc.\n"
                "The generated root joint will be parented under this object."
            )
        )
        self.widgets['root_parent_btn'] = cmds.button(
            label="Get Selected",
            enable=False,
            command=self._on_root_parent_get,
            annotation="Select any object in the viewport, then click to assign it as root parent."
        )
        cmds.setParent('..')  # end root parent row

    def _create_buttons(self):
        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=(260, 220),
            adjustableColumn=1,
            columnAttach=[(1, 'both', 4), (2, 'both', 4)]
        )
        cmds.button(
            label="GENERATE BONES",
            height=48,
            backgroundColor=[0.25, 0.62, 0.25],
            command=self._on_generate_button_clicked,
            annotation=(
                "Run DemBones and create a skeleton + skin cluster on the target mesh.\n"
                "In Single mode: uses Source + Target + Frame Range.\n"
                "In Shared Skeleton mode: concatenates all sims onto one shared rig."
            )
        )
        cmds.button(
            label="DUPLICATE MESH (static)",
            height=44,
            command=utils.duplicate_static_meshes,
            annotation=(
                "Duplicate selected mesh(es) as static snapshots at the current frame.\n"
                "Useful for creating a bind-pose target from an animated mesh."
            )
        )
        cmds.setParent('..')

    # ------------------------------------------------------------------
    # Shared skeleton sim-row management
    # ------------------------------------------------------------------

    def _make_pick_cmd(self, field):
        def cmd(*a):
            self._pick_sim_mesh(field)
        return cmd

    def _make_remove_cmd(self, layout):
        def cmd(*a):
            self._remove_sim_row(layout)
        return cmd

    def _on_add_sim_clicked(self, *args):
        selected = utils.get_selected_meshes()
        if selected:
            start, end = utils.get_timeline_range()
            for mesh_path in selected:
                self._add_sim_row(
                    mesh_name=utils.get_short_name(mesh_path),
                    start=start, end=end
                )
            self._show_success("Added {} simulation(s) from selection".format(len(selected)))
        else:
            self._add_sim_row()

    def _add_sim_row(self, mesh_name="", start=1, end=100):
        cmds.setParent(self.widgets['sim_column'])
        idx = len(self._sim_rows)
        row_layout = cmds.rowLayout(
            numberOfColumns=6,
            columnWidth6=(130, 70, 40, 70, 40, 24),
            adjustableColumn=1
        )

        mesh_field = cmds.textField(
            text=mesh_name,
            placeholderText="sim mesh {}".format(idx + 1),
            annotation="Animated simulation mesh for this clip (same topology as bind pose)."
        )
        clip_field = cmds.textField(
            text=mesh_name or "anim_{}".format(idx + 1), width=70,
            annotation="Clip name — used in the frame-range summary after generation."
        )
        start_field = cmds.intField(
            value=start, minValue=-10000, maxValue=10000,
            annotation="First frame of this simulation's source animation."
        )
        end_field = cmds.intField(
            value=end, minValue=-10000, maxValue=10000,
            annotation="Last frame of this simulation's source animation."
        )
        cmds.button(
            label="<<", width=40,
            command=self._make_pick_cmd(mesh_field),
            annotation="Select the simulation mesh in the viewport, then click to assign it."
        )
        cmds.button(
            label="X", width=24,
            backgroundColor=[0.6, 0.2, 0.2],
            command=self._make_remove_cmd(row_layout),
            annotation="Remove this simulation row."
        )

        cmds.setParent('..')

        self._sim_rows.append({
            'mesh': mesh_field,
            'clip': clip_field,
            'start': start_field,
            'end': end_field,
            'row_layout': row_layout
        })

    def _pick_sim_mesh(self, mesh_field):
        success, full_path, message = utils.get_selected_mesh()
        if success:
            cmds.textField(mesh_field, edit=True, text=utils.get_short_name(full_path))
            self._show_success("Sim mesh set: " + utils.get_short_name(full_path))
        else:
            self._show_error(message)

    def _remove_sim_row(self, row_layout):
        self._sim_rows = [r for r in self._sim_rows
                          if r['row_layout'] != row_layout]
        if cmds.rowLayout(row_layout, exists=True):
            cmds.deleteUI(row_layout)

    # ------------------------------------------------------------------
    # Mode toggle
    # ------------------------------------------------------------------

    def _on_mode_changed(self, value):
        cmds.columnLayout(self.widgets['single_section'], edit=True, visible=not value)
        cmds.columnLayout(self.widgets['shared_section'], edit=True, visible=value)

    def _on_root_parent_toggled(self, value):
        cmds.textField(self.widgets['root_parent_field'], edit=True, enable=value)
        cmds.button(self.widgets['root_parent_btn'],     edit=True, enable=value)
        if not value:
            cmds.textField(self.widgets['root_parent_field'], edit=True, text="")

    def _on_root_parent_get(self, *args):
        sel = cmds.ls(selection=True, long=True)
        if not sel:
            self._show_error("Nothing selected — select any object first.")
            return
        obj = sel[0]
        short = obj.split('|')[-1]
        cmds.textField(self.widgets['root_parent_field'], edit=True, text=short)
        self._show_success("Root parent set: " + short)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_source_button_clicked(self, *args):
        success, full_path, short_name, message = \
            self.controller.set_source_mesh_from_selection()
        if success:
            cmds.textField(self.widgets['source_field'], edit=True, text=short_name)
            self._show_success(message)
        else:
            self._show_error(message)

    def _on_timeline_button_clicked(self, *args):
        start, end = utils.get_timeline_range()
        cmds.intField(self.widgets['start_frame'], edit=True, value=start)
        cmds.intField(self.widgets['end_frame'], edit=True, value=end)
        self._show_success("Frame range set: {} - {}".format(start, end))

    def _on_shared_timeline_clicked(self, *args):
        if not self._sim_rows:
            self._show_error("No simulations added yet.")
            return
        start, end = utils.get_timeline_range()
        for row in self._sim_rows:
            cmds.intField(row['start'], edit=True, value=start)
            cmds.intField(row['end'],   edit=True, value=end)
        self._show_success("All simulations set to: {} - {}".format(start, end))

    def _get_root_parent(self):
        """Return the resolved full path of the custom root parent, or None."""
        if not cmds.checkBox(self.widgets['root_parent_check'], query=True, value=True):
            return None
        name = cmds.textField(self.widgets['root_parent_field'], query=True, text=True)
        if not name:
            return None
        matches = cmds.ls(name, long=True)
        return matches[0] if matches else name

    def _on_generate_button_clicked(self, *args):
        global_iters = cmds.intField(self.widgets['global_iters'], query=True, value=True)
        num_bones    = cmds.intField(self.widgets['num_bones'],    query=True, value=True)
        shared_mode  = cmds.checkBox(self.widgets['shared_check'], query=True, value=True)

        if shared_mode:
            self._run_shared_skeleton(global_iters, num_bones)
        else:
            self._run_single(global_iters, num_bones)

    # ------------------------------------------------------------------
    # Run helpers
    # ------------------------------------------------------------------

    def _run_single(self, global_iters, num_bones):
        start_frame = cmds.intField(self.widgets['start_frame'], query=True, value=True)
        end_frame   = cmds.intField(self.widgets['end_frame'],   query=True, value=True)

        is_valid, errors = self.controller.validate_single(
            start_frame, end_frame, global_iters, num_bones)

        if not is_valid:
            self._show_validation_error(errors)
            return

        self._show_info("Processing... Please wait")
        cmds.refresh(force=True)

        success, message = self.controller.run_dembones(
            start_frame, end_frame, global_iters, num_bones,
            root_parent=self._get_root_parent())

        self._finish(success, message)

    def _run_shared_skeleton(self, global_iters, num_bones):
        if not self._sim_rows:
            self._show_error("No simulations added. Click '+ Add Simulation' first.")
            return

        sim_entries = []
        for row in self._sim_rows:
            mesh_name = cmds.textField(row['mesh'],  query=True, text=True)
            clip_name = cmds.textField(row['clip'],  query=True, text=True)
            src_start = cmds.intField(row['start'],  query=True, value=True)
            src_end   = cmds.intField(row['end'],    query=True, value=True)

            if not mesh_name:
                self._show_error("One or more sim meshes are not set.")
                return

            matches   = cmds.ls(mesh_name, long=True)
            mesh_full = matches[0] if matches else mesh_name
            sim_entries.append((mesh_full, src_start, src_end, clip_name or mesh_name))

        self._show_info("Building shared skeleton... Please wait")
        cmds.refresh(force=True)

        success, message = self.controller.run_dembones_shared_skeleton(
            sim_entries, global_iters, num_bones,
            root_parent=self._get_root_parent())

        self._finish(success, message)

    def _finish(self, success, message):
        if success:
            self._show_success("Done!")
            cmds.confirmDialog(
                title='Success', message=message,
                button=['OK'], defaultButton='OK', icon='information')
        else:
            self._show_error(message)
            cmds.confirmDialog(
                title='Error', message=message,
                button=['OK'], defaultButton='OK', icon='critical')

    def _show_validation_error(self, errors):
        error_msg = "Validation Errors:\n\n" + "\n".join("- " + e for e in errors)
        self._show_error("Validation failed — see dialog")
        cmds.confirmDialog(
            title='Validation Error', message=error_msg,
            button=['OK'], defaultButton='OK', icon='critical')

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------

    def _show_error(self, message):
        cmds.text(self.widgets['status_text'], edit=True,
                  label="ERROR: " + message, backgroundColor=[0.75, 0.25, 0.25])
        cmds.warning(message)

    def _show_success(self, message):
        cmds.text(self.widgets['status_text'], edit=True,
                  label=message, backgroundColor=[0.22, 0.55, 0.22])

    def _show_info(self, message):
        cmds.text(self.widgets['status_text'], edit=True,
                  label=message, backgroundColor=[0.25, 0.42, 0.70])
