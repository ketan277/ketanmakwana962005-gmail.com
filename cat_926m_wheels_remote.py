"""
Caterpillar 926M Heavy-Duty Wheel Assembly & Interactive Remote Control
Blender 5.1.1 Compatible Python Script

Features:
- Procedural Caterpillar 926M style 4-wheel assembly with detailed rims, tread blocks, central hub, and lug bolts.
- Realistic PBR Materials: Caterpillar Yellow (Rims), Rubber Dark (Tyres), Steel Metallic (Hubs & Bolts).
- Rigged hierarchy with separate Steering Pivots (`Steer_Pivot_L`, `Steer_Pivot_R`) and rolling Wheel objects (`Front_Wheel_L`, `Front_Wheel_R`, `Rear_Wheel_L`, `Rear_Wheel_R`).
- Blender 3D Viewport N-Panel UI ("CAT 926M Remote") for speed, direction, steering, and reset controls.
- Interactive Modal Keyboard Driving Operator (WASD / Arrow Keys, Space for Stop, ESC to exit modal mode).
- Dynamic physically consistent wheel rotation linked to movement distance.

To Use:
1. Paste this script into Blender's Text Editor.
2. Click "Run Script".
3. Open 3D Viewport Sidebar (Press 'N') and find "CAT 926M Remote" tab.
4. Use UI buttons or click "Start Keyboard Control" for real-time WASD driving!
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix

# ------------------------------------------------------------------------
# Scene & Property Definitions
# ------------------------------------------------------------------------

class CAT926MProperties(bpy.types.PropertyGroup):
    target_speed: bpy.props.FloatProperty(
        name="Target Speed",
        description="Forward/Reverse Speed (m/s)",
        default=0.0,
        min=-15.0,
        max=15.0
    )
    current_speed: bpy.props.FloatProperty(
        name="Current Speed",
        description="Actual Vehicle Speed",
        default=0.0,
        min=-15.0,
        max=15.0
    )
    steering_angle: bpy.props.FloatProperty(
        name="Steering Angle",
        description="Front Wheels Steering Angle in Degrees",
        default=0.0,
        min=-40.0,
        max=40.0,
        subtype='ANGLE'
    )
    max_steering_angle: bpy.props.FloatProperty(
        name="Max Steer Angle",
        default=35.0,
        min=10.0,
        max=45.0
    )
    acceleration: bpy.props.FloatProperty(
        name="Acceleration",
        default=8.0,
        min=1.0,
        max=20.0
    )
    steering_speed: bpy.props.FloatProperty(
        name="Steer Speed",
        default=2.5,
        min=0.5,
        max=10.0
    )
    auto_center_steering: bpy.props.BoolProperty(
        name="Auto-Center Steering",
        default=True
    )

# ------------------------------------------------------------------------
# Procedural Geometry & Material Generators
# ------------------------------------------------------------------------

def get_or_create_material(name, color, metallic=0.0, roughness=0.5):
    """Creates a PBR Principled BSDF material safe across Blender 4.x and 5.x."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = metallic
            if "Roughness" in bsdf.inputs:
                bsdf.inputs["Roughness"].default_value = roughness
    return mat

def create_wheel_mesh(name="CAT926M_Wheel_Mesh"):
    """Generates detailed 3D geometry for a Caterpillar 926M heavy loader tyre & rim."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    # Materials
    mat_rubber = get_or_create_material("CAT_TyreRubber", (0.05, 0.05, 0.05, 1.0), metallic=0.0, roughness=0.85)
    mat_yellow = get_or_create_material("CAT_YellowRim", (0.95, 0.62, 0.03, 1.0), metallic=0.2, roughness=0.3)
    mat_steel = get_or_create_material("CAT_SteelHub", (0.2, 0.2, 0.22, 1.0), metallic=0.85, roughness=0.35)

    # Dimensions (Caterpillar 926M Tyre size: ~1.6m outer diameter, ~0.65m width, rim diameter ~0.85m)
    outer_radius = 0.8
    rim_radius = 0.42
    hub_radius = 0.22
    width = 0.65
    half_w = width / 2.0
    segments = 36

    # 1. Main Outer Tyre Cylinder Base
    # Generate profile concentric rings
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        diameter1=outer_radius * 2,
        diameter2=outer_radius * 2,
        depth=width,
        matrix=Matrix.Rotation(math.radians(90), 4, 'Y')
    )

    # Assign tyre rubber material to base faces
    for face in bm.faces:
        face.material_index = 0

    # 2. Add Chunky Off-Road V-Pattern Tread Lug Blocks
    tread_count = 18
    lug_width = 0.12
    lug_depth = 0.045
    for i in range(tread_count):
        angle = (2 * math.pi / tread_count) * i
        # Chevron pattern left and right halves
        for side in [-1, 1]:
            center_y = side * (width * 0.22)
            rot_z = Matrix.Rotation(angle, 4, 'X')
            trans = Matrix.Translation((0, math.sin(angle) * outer_radius, math.cos(angle) * outer_radius))
            skew = Matrix.Rotation(math.radians(side * 25), 4, 'X')

            # Create tread block box
            res = bmesh.ops.create_cube(bm, size=1.0)
            verts = res['verts']
            bmesh.ops.scale(bm, vec=(lug_width, 0.14, lug_depth), verts=verts)
            bmesh.ops.transform(bm, matrix=skew, verts=verts)
            bmesh.ops.transform(bm, matrix=Matrix.Translation((0, center_y, 0)), verts=verts)
            bmesh.ops.transform(bm, matrix=rot_z, verts=verts)
            bmesh.ops.transform(bm, matrix=Matrix.Translation((0, math.sin(angle)*(outer_radius + lug_depth*0.4), math.cos(angle)*(outer_radius + lug_depth*0.4))), verts=verts)

    # 3. Create Rim Bevel & Inner Rim (CAT Yellow)
    rim_bmesh = bmesh.new()
    bmesh.ops.create_cone(
        rim_bmesh,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        diameter1=rim_radius * 2,
        diameter2=rim_radius * 2,
        depth=width * 0.92,
        matrix=Matrix.Rotation(math.radians(90), 4, 'Y')
    )
    for f in rim_bmesh.faces:
        f.material_index = 1

    # Rim Flange / Lip
    bmesh.ops.create_cone(
        rim_bmesh,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        diameter1=rim_radius * 2 * 1.08,
        diameter2=rim_radius * 2 * 1.08,
        depth=width * 0.95,
        matrix=Matrix.Rotation(math.radians(90), 4, 'Y')
    )
    for f in rim_bmesh.faces:
        f.material_index = 1

    # Merge Rim into main BM
    bm.from_mesh(rim_bmesh.to_mesh(bpy.data.meshes.new("temp")))
    rim_bmesh.free()

    # 4. Central Heavy Hub & Lug Bolts (Steel / Metallic)
    hub_bmesh = bmesh.new()
    # Central axle hub box protrusion
    for side in [-1, 1]:
        bmesh.ops.create_cone(
            hub_bmesh,
            cap_ends=True,
            cap_tris=False,
            segments=24,
            diameter1=hub_radius * 2,
            diameter2=hub_radius * 2 * 0.9,
            depth=0.15,
            matrix=Matrix.Translation((side * (half_w * 0.85), 0, 0)) @ Matrix.Rotation(math.radians(90), 4, 'Y')
        )
        # 10 Wheel Lug Bolts per side
        num_bolts = 10
        bolt_circle_r = hub_radius * 0.72
        for b in range(num_bolts):
            ba = (2 * math.pi / num_bolts) * b
            by = math.sin(ba) * bolt_circle_r
            bz = math.cos(ba) * bolt_circle_r
            bmesh.ops.create_cone(
                hub_bmesh,
                cap_ends=True,
                segments=8,
                diameter1=0.05,
                diameter2=0.05,
                depth=0.08,
                matrix=Matrix.Translation((side * (half_w * 0.92), by, bz)) @ Matrix.Rotation(math.radians(90), 4, 'Y')
            )

    for f in hub_bmesh.faces:
        f.material_index = 2

    bm.from_mesh(hub_bmesh.to_mesh(bpy.data.meshes.new("temp2")))
    hub_bmesh.free()

    # Finalize Mesh
    bm.to_mesh(mesh)
    bm.free()

    # Attach Materials to Mesh
    mesh.materials.append(mat_rubber)
    mesh.materials.append(mat_yellow)
    mesh.materials.append(mat_steel)

    return mesh

# ------------------------------------------------------------------------
# Rig Assembly Builder
# ------------------------------------------------------------------------

def build_cat926m_wheels_rig():
    """Builds full CAT 926M 4-Wheel Assembly with Steering Pivots & Controllers."""
    # Clear existing CAT 926M objects if re-running script
    existing_objs = [obj for obj in bpy.data.objects if "CAT926M" in obj.name or "Wheel_" in obj.name or "Steer_" in obj.name]
    for obj in existing_objs:
        bpy.data.objects.remove(obj, do_unlink=True)

    # Base Collection setup
    collection_name = "CAT_926M_Vehicle"
    coll = bpy.data.collections.get(collection_name)
    if not coll:
        coll = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(coll)

    # 1. Main Root Controller
    root_obj = bpy.data.objects.new("CAT926M_Root", None)
    root_obj.empty_display_type = 'CUBE'
    root_obj.empty_display_size = 1.5
    coll.objects.link(root_obj)

    # Shared Wheel Mesh
    shared_wheel_mesh = create_wheel_mesh("CAT926M_HeavyWheel_Mesh")

    # Dimensions & Positions (Caterpillar 926M Specs)
    wheel_track = 2.2    # Distance between Left & Right wheels (X axis)
    wheel_base = 3.0     # Distance between Front & Rear axles (Y axis)
    half_track = wheel_track / 2.0
    half_base = wheel_base / 2.0
    wheel_z = 0.8        # Hub height off ground

    root_obj.location = (0, 0, 0)

    # 2. Front Axle Setup (With Steering Pivots)
    front_steer_pivots = {}
    wheels = {}

    wheel_configs = [
        ("Front_Wheel_L",  half_track,  half_base, wheel_z, True),
        ("Front_Wheel_R", -half_track,  half_base, wheel_z, True),
        ("Rear_Wheel_L",   half_track, -half_base, wheel_z, False),
        ("Rear_Wheel_R",  -half_track, -half_base, wheel_z, False),
    ]

    for name, x, y, z, is_front in wheel_configs:
        if is_front:
            # Create Steering Pivot Empty
            pivot_name = f"Steer_Pivot_{'L' if x > 0 else 'R'}"
            pivot = bpy.data.objects.new(pivot_name, None)
            pivot.empty_display_type = 'SINGLE_ARROW'
            pivot.empty_display_size = 0.8
            pivot.location = (x, y, z)
            pivot.parent = root_obj
            coll.objects.link(pivot)
            front_steer_pivots[name] = pivot

            # Create Front Wheel attached to Steering Pivot
            w_obj = bpy.data.objects.new(name, shared_wheel_mesh)
            w_obj.location = (0, 0, 0)
            w_obj.parent = pivot
            coll.objects.link(w_obj)
            wheels[name] = w_obj
        else:
            # Rear Wheel direct parent to Root
            w_obj = bpy.data.objects.new(name, shared_wheel_mesh)
            w_obj.location = (x, y, z)
            w_obj.parent = root_obj
            coll.objects.link(w_obj)
            wheels[name] = w_obj

    # 3. Add Simple Chassis Visual Indicator Frame
    chassis_mesh = bpy.data.meshes.new("CAT926M_SubFrame")
    bm_c = bmesh.new()
    bmesh.ops.create_cube(bm_c, size=1.0)
    bmesh.ops.scale(bm_c, vec=(wheel_track - 0.4, wheel_base + 0.6, 0.2), verts=bm_c.verts)
    bm_c.to_mesh(chassis_mesh)
    bm_c.free()

    chassis_obj = bpy.data.objects.new("CAT926M_Frame", chassis_mesh)
    chassis_obj.location = (0, 0, wheel_z)
    chassis_obj.parent = root_obj
    mat_frame = get_or_create_material("CAT_DarkChassis", (0.1, 0.1, 0.1, 1.0), metallic=0.7, roughness=0.4)
    chassis_mesh.materials.append(mat_frame)
    coll.objects.link(chassis_obj)

    # Select Root object
    bpy.context.view_layer.objects.active = root_obj
    root_obj.select_set(True)

    return root_obj

# ------------------------------------------------------------------------
# Core Drive & Update Logic
# ------------------------------------------------------------------------

def update_vehicle_transform(scene, delta_time):
    """Updates vehicle position, front wheel steering angle, and wheel rolling rotations."""
    cat_props = scene.cat926m_props
    root = bpy.data.objects.get("CAT926M_Root")
    if not root:
        return

    # 1. Smoothly interpolate current speed towards target speed
    target_spd = cat_props.target_speed
    accel = cat_props.acceleration
    if cat_props.current_speed < target_spd:
        cat_props.current_speed = min(cat_props.target_speed, cat_props.current_speed + accel * delta_time)
    elif cat_props.current_speed > target_spd:
        cat_props.current_speed = max(cat_props.target_speed, cat_props.current_speed - accel * delta_time)

    spd = cat_props.current_speed
    steer_deg = cat_props.steering_angle
    steer_rad = math.radians(steer_deg)

    # 2. Update Front Steering Pivots
    pivot_l = bpy.data.objects.get("Steer_Pivot_L")
    pivot_r = bpy.data.objects.get("Steer_Pivot_R")
    if pivot_l:
        pivot_l.rotation_euler.z = steer_rad
    if pivot_r:
        pivot_r.rotation_euler.z = steer_rad

    # 3. Advance Vehicle Position based on speed & steering angle (Ackermann-like kinematics)
    if abs(spd) > 0.001:
        distance = spd * delta_time
        wheel_base = 3.0

        # If steering, rotate vehicle root around turn center
        if abs(steer_rad) > 0.001:
            turn_radius = wheel_base / math.tan(steer_rad)
            angular_velocity = spd / turn_radius
            heading_change = angular_velocity * delta_time

            root.rotation_euler.z += heading_change

            # Forward motion vector in local space
            heading = root.rotation_euler.z
            dx = -math.sin(heading) * distance
            dy = math.cos(heading) * distance
            root.location.x += dx
            root.location.y += dy
        else:
            # Straight forward/reverse
            heading = root.rotation_euler.z
            dx = -math.sin(heading) * distance
            dy = math.cos(heading) * distance
            root.location.x += dx
            root.location.y += dy

        # 4. Physically consistent wheel rolling rotation (Angle = Distance / Radius)
        tyre_radius = 0.8
        roll_angle_delta = distance / tyre_radius

        wheel_names = ["Front_Wheel_L", "Front_Wheel_R", "Rear_Wheel_L", "Rear_Wheel_R"]
        for w_name in wheel_names:
            w_obj = bpy.data.objects.get(w_name)
            if w_obj:
                # Rotate around local X axis
                w_obj.rotation_euler.x += roll_angle_delta

# ------------------------------------------------------------------------
# UI Operators
# ------------------------------------------------------------------------

class CAT926M_OT_DriveControl(bpy.types.Operator):
    """Execute Quick UI Command (Forward, Reverse, Stop, Steer Left, Steer Right, Center)"""
    bl_idname = "cat926m.drive_control"
    bl_label = "Drive Control"
    bl_options = {'REGISTER', 'UNDO'}

    action: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.cat926m_props
        if self.action == "FORWARD":
            props.target_speed = 6.0
        elif self.action == "REVERSE":
            props.target_speed = -4.0
        elif self.action == "STOP":
            props.target_speed = 0.0
            props.current_speed = 0.0
        elif self.action == "STEER_LEFT":
            props.steering_angle = min(props.max_steering_angle, props.steering_angle + 10.0)
        elif self.action == "STEER_RIGHT":
            props.steering_angle = max(-props.max_steering_angle, props.steering_angle - 10.0)
        elif self.action == "STEER_CENTER":
            props.steering_angle = 0.0
        elif self.action == "RESET":
            props.target_speed = 0.0
            props.current_speed = 0.0
            props.steering_angle = 0.0
            root = bpy.data.objects.get("CAT926M_Root")
            if root:
                root.location = (0, 0, 0)
                root.rotation_euler = (0, 0, 0)

            # Reset Wheel Rotations
            for w_name in ["Front_Wheel_L", "Front_Wheel_R", "Rear_Wheel_L", "Rear_Wheel_R"]:
                w_obj = bpy.data.objects.get(w_name)
                if w_obj:
                    w_obj.rotation_euler.x = 0

        # Run one frame step update for instant visual feedback
        update_vehicle_transform(context.scene, 0.05)
        return {'FINISHED'}

class CAT926M_OT_BuildRig(bpy.types.Operator):
    """Rebuild CAT 926M 4-Wheel Assembly Rig"""
    bl_idname = "cat926m.build_rig"
    bl_label = "Rebuild 4-Wheel Assembly"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        build_cat926m_wheels_rig()
        self.report({'INFO'}, "Caterpillar 926M Wheel Rig Created Successfully!")
        return {'FINISHED'}

# ------------------------------------------------------------------------
# Interactive Modal Keyboard Driving Operator (WASD / Arrows)
# ------------------------------------------------------------------------

class CAT926M_OT_ModalDrive(bpy.types.Operator):
    """Real-time Keyboard Remote Control (WASD / Arrow Keys, Space=Stop, ESC=Exit)"""
    bl_idname = "wm.cat926m_modal_drive"
    bl_label = "Start Real-Time Keyboard Remote Control"

    _timer = None
    _keys_pressed = set()

    def modal(self, context, event):
        props = context.scene.cat926m_props

        # Catch Key Press / Release events
        if event.type in {'W', 'UP_ARROW', 'S', 'DOWN_ARROW', 'A', 'LEFT_ARROW', 'D', 'RIGHT_ARROW', 'SPACE'}:
            if event.value == 'PRESS':
                self._keys_pressed.add(event.type)
            elif event.value == 'RELEASE':
                self._keys_pressed.discard(event.type)

        if event.type == 'ESC':
            context.window_manager.event_timer_remove(self._timer)
            context.workspace.status_text_set(None)
            self.report({'INFO'}, "Keyboard Remote Control Stopped.")
            return {'CANCELLED'}

        if event.type == 'TIMER':
            dt = 0.03  # approx 30 FPS update loop

            # Handle Accelerate / Reverse / Stop
            if 'SPACE' in self._keys_pressed:
                props.target_speed = 0.0
                props.current_speed = 0.0
            elif 'W' in self._keys_pressed or 'UP_ARROW' in self._keys_pressed:
                props.target_speed = 8.0
            elif 'S' in self._keys_pressed or 'DOWN_ARROW' in self._keys_pressed:
                props.target_speed = -5.0
            else:
                # Coasting friction
                props.target_speed = 0.0

            # Handle Steering
            steer_rate = props.steering_speed * 15.0 * dt
            if 'A' in self._keys_pressed or 'LEFT_ARROW' in self._keys_pressed:
                props.steering_angle = min(props.max_steering_angle, props.steering_angle + steer_rate)
            elif 'D' in self._keys_pressed or 'RIGHT_ARROW' in self._keys_pressed:
                props.steering_angle = max(-props.max_steering_angle, props.steering_angle - steer_rate)
            else:
                if props.auto_center_steering and abs(props.steering_angle) > 0.1:
                    sign = 1.0 if props.steering_angle > 0 else -1.0
                    props.steering_angle -= sign * steer_rate * 0.8
                    if abs(props.steering_angle) < 0.5:
                        props.steering_angle = 0.0

            # Execute Physics & Wheel Rotation Update
            update_vehicle_transform(context.scene, dt)

            # Redraw Viewport
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.03, window=context.window)
        wm.modal_handler_add(self)
        context.workspace.status_text_set("CAT 926M Remote Drive: [W/Up]=Forward | [S/Down]=Reverse | [A/Left, D/Right]=Steer | [SPACE]=Stop | [ESC]=Exit")
        self.report({'INFO'}, "Keyboard Remote Control Active! Use WASD or Arrow Keys. Press ESC to stop.")
        return {'RUNNING_MODAL'}

# ------------------------------------------------------------------------
# Custom N-Panel Remote Control UI Panel
# ------------------------------------------------------------------------

class CAT926M_PT_RemotePanel(bpy.types.Panel):
    """Creates a custom Caterpillar Remote Control Panel in the 3D Viewport N-Panel"""
    bl_label = "Caterpillar 926M Remote"
    bl_idname = "CAT926M_PT_remote_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAT 926M Remote'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.cat926m_props

        # Header / Rebuild Rig Button
        box_main = layout.box()
        box_main.label(text="Vehicle Setup", icon='TRUCK')
        box_main.operator("cat926m.build_rig", text="Rebuild Wheel Rig", icon='FILE_REFRESH')

        # Interactive Modal Drive Switch
        box_drive = layout.box()
        box_drive.label(text="Real-Time Keyboard Remote", icon='GAMEPAD')
        box_drive.operator("wm.cat926m_modal_drive", text="Start Keyboard Control (WASD)", icon='PLAY')

        # Live Status Telemetry
        box_status = layout.box()
        box_status.label(text="Telemetry Status", icon='VIEW_CAMERA')
        col = box_status.column(align=True)
        col.label(text=f"Current Speed: {props.current_speed:.2f} m/s")
        col.label(text=f"Steering Angle: {props.steering_angle:.1f}°")

        # Speed Controls & Sliders
        box_speed = layout.box()
        box_speed.label(text="Speed Controls", icon='SPEED')
        box_speed.prop(props, "target_speed", slider=True)

        row_s = box_speed.row(align=True)
        op_fwd = row_s.operator("cat926m.drive_control", text="Forward", icon='TRIPPLE_BAR')
        op_fwd.action = "FORWARD"
        op_rev = row_s.operator("cat926m.drive_control", text="Reverse", icon='FRAME_PREV')
        op_rev.action = "REVERSE"
        op_stp = row_s.operator("cat926m.drive_control", text="STOP", icon='CANCEL')
        op_stp.action = "STOP"

        # Steering Controls
        box_steer = layout.box()
        box_steer.label(text="Steering Controls", icon='DRIVER')
        box_steer.prop(props, "steering_angle", slider=True)
        box_steer.prop(props, "auto_center_steering")

        row_st = box_steer.row(align=True)
        op_l = row_st.operator("cat926m.drive_control", text="◄ Left", icon='BACK')
        op_l.action = "STEER_LEFT"
        op_c = row_st.operator("cat926m.drive_control", text="Center", icon='OUTLINER_OB_EMPTY')
        op_c.action = "STEER_CENTER"
        op_r = row_st.operator("cat926m.drive_control", text="Right ►", icon='FORWARD')
        op_r.action = "STEER_RIGHT"

        # Reset & Calibration
        layout.separator()
        op_rst = layout.operator("cat926m.drive_control", text="Reset Position & Rotation", icon='REFRESH')
        op_rst.action = "RESET"

# ------------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------------

classes = (
    CAT926MProperties,
    CAT926M_OT_DriveControl,
    CAT926M_OT_BuildRig,
    CAT926M_OT_ModalDrive,
    CAT926M_PT_RemotePanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cat926m_props = bpy.props.PointerProperty(type=CAT926MProperties)

    # Auto build assembly on script execution
    build_cat926m_wheels_rig()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cat926m_props

if __name__ == "__main__":
    register()
