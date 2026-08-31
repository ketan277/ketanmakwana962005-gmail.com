"""
Union Pacific Big Boy 4014 Procedural 3D Generator Script for Blender
Creates a high-fidelity Hard-Surface 3D model of Union Pacific Big Boy 4014
with 4-8-8-4 wheel configuration, articulated drive chassis, boiler, cab,
tender, drive rods, PBR materials, studio lighting, and camera.
"""

import bpy
import math

def reset_scene():
    """Clear existing objects and materials."""
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_materials():
    """Create PBR materials for the Big Boy 4014 locomotive."""
    mats = {}

    # 1. Dark Engine Steel
    mat_steel = bpy.data.materials.new(name="Mat_Engine_Steel")
    mat_steel.use_nodes = True
    nodes = mat_steel.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.08, 0.09, 0.10, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.35
    mats['steel'] = mat_steel

    # 2. Boiler Jacket (Dark Metallic Paint)
    mat_boiler = bpy.data.materials.new(name="Mat_Boiler_Jacket")
    mat_boiler.use_nodes = True
    nodes = mat_boiler.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.04, 0.05, 0.06, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.85
        bsdf.inputs['Roughness'].default_value = 0.25
    mats['boiler'] = mat_boiler

    # 3. Brass / Bronze Accents
    mat_brass = bpy.data.materials.new(name="Mat_Brass_Accent")
    mat_brass.use_nodes = True
    nodes = mat_brass.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.22, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.95
        bsdf.inputs['Roughness'].default_value = 0.2
    mats['brass'] = mat_brass

    # 4. Driver Rod Steel (Brushed Metal)
    mat_rods = bpy.data.materials.new(name="Mat_Drive_Rods")
    mat_rods.use_nodes = True
    nodes = mat_rods.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.7, 0.72, 0.75, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.95
        bsdf.inputs['Roughness'].default_value = 0.2
    mats['rods'] = mat_rods

    # 5. Headlight Glass / Emission
    mat_glass = bpy.data.materials.new(name="Mat_Headlight")
    mat_glass.use_nodes = True
    nodes = mat_glass.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (1.0, 0.95, 0.8, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.1
        if 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = (1.0, 0.9, 0.7, 1.0)
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = 5.0
    mats['headlight'] = mat_glass

    # 6. Coal Material
    mat_coal = bpy.data.materials.new(name="Mat_Tender_Coal")
    mat_coal.use_nodes = True
    nodes = mat_coal.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.1
        bsdf.inputs['Roughness'].default_value = 0.85
    mats['coal'] = mat_coal

    # 7. Track Rail Steel
    mat_rail = bpy.data.materials.new(name="Mat_Track_Rail")
    mat_rail.use_nodes = True
    nodes = mat_rail.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.5, 0.52, 0.55, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.3
    mats['rail'] = mat_rail

    return mats

def assign_material(obj, mat):
    """Utility to assign material to an object."""
    if obj and mat:
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat

def create_boiler_and_cab(mats):
    """Builds boiler body, smokebox, domes, chimney, and engineer cab."""
    # Main Boiler Cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.5, depth=14.0, location=(0, 0, 3.5), rotation=(math.radians(90), 0, 0)
    )
    boiler = bpy.context.active_object
    boiler.name = "BigBoy_Boiler"
    assign_material(boiler, mats['boiler'])

    # Front Smokebox Door
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.52, depth=0.4, location=(0, -7.1, 3.5), rotation=(math.radians(90), 0, 0)
    )
    smokebox = bpy.context.active_object
    smokebox.name = "BigBoy_SmokeboxDoor"
    assign_material(smokebox, mats['steel'])

    # Chimney / Smokestack
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.4, depth=1.0, location=(0, -6.0, 5.2)
    )
    chimney = bpy.context.active_object
    chimney.name = "BigBoy_Chimney"
    assign_material(chimney, mats['steel'])

    # Steam Domes (2 Domes along top of boiler)
    for i, y_pos in enumerate([-3.5, 1.5]):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.6, depth=0.9, location=(0, y_pos, 5.2)
        )
        dome = bpy.context.active_object
        dome.name = f"BigBoy_SteamDome_{i+1}"
        assign_material(dome, mats['boiler'])

    # Engineer Cab
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 7.5, 4.0)
    )
    cab = bpy.context.active_object
    cab.name = "BigBoy_Cab"
    cab.scale = (3.4, 3.0, 2.5)
    assign_material(cab, mats['steel'])

    # Cab Roof Curve Overlay
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.75, depth=3.0, location=(0, 7.5, 5.2), rotation=(math.radians(90), 0, 0)
    )
    cab_roof = bpy.context.active_object
    cab_roof.name = "BigBoy_CabRoof"
    assign_material(cab_roof, mats['steel'])

    # Porthole Windows in Cab
    for x_side in [-1.72, 1.72]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.35, depth=0.1, location=(x_side, 7.0, 4.2), rotation=(0, math.radians(90), 0)
        )
        window = bpy.context.active_object
        window.name = f"BigBoy_CabWindow_{'L' if x_side < 0 else 'R'}"
        assign_material(window, mats['brass'])

def create_wheel(name, radius, width, position, mats, is_driver=False):
    """Creates a wheel assembly with axle and optional spokes for drivers."""
    # Wheel Rim
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=width, location=position, rotation=(0, math.radians(90), 0)
    )
    wheel = bpy.context.active_object
    wheel.name = name
    assign_material(wheel, mats['steel'])

    if is_driver:
        # Hub Accent
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius * 0.3, depth=width * 1.1, location=position, rotation=(0, math.radians(90), 0)
        )
        hub = bpy.context.active_object
        hub.name = f"{name}_Hub"
        assign_material(hub, mats['brass'])

        # Pin for Drive Rods
        pin_pos = (position[0] + (0.15 if position[0] > 0 else -0.15), position[1], position[2] + radius * 0.5)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.1, depth=width * 1.3, location=pin_pos, rotation=(0, math.radians(90), 0)
        )
        pin = bpy.context.active_object
        pin.name = f"{name}_Pin"
        assign_material(pin, mats['rods'])

    return wheel

def create_4884_running_gear(mats):
    """Builds the 4-8-8-4 articulated engine chassis, wheels, cylinders, and drive rods."""
    driver_radius = 0.86  # Scale 68 inch driver
    pilot_radius = 0.45
    trailing_radius = 0.5
    wheel_w = 0.25

    # --- 1. Leading Pilot Truck (4 Wheels / 2 Axles) ---
    pilot_y_positions = [-8.5, -7.3]
    for i, y_pos in enumerate(pilot_y_positions):
        for x_side in [-1.4, 1.4]:
            create_wheel(f"BigBoy_PilotWheel_{i+1}_{'L' if x_side < 0 else 'R'}",
                         pilot_radius, wheel_w, (x_side, y_pos, 0.45), mats)
        # Axle
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.1, depth=2.8, location=(0, y_pos, 0.45), rotation=(0, math.radians(90), 0)
        )
        assign_material(bpy.context.active_object, mats['steel'])

    # --- 2. Front Driver Set (8 Wheels / 4 Axles) ---
    front_driver_y = [-5.8, -4.4, -3.0, -1.6]
    for i, y_pos in enumerate(front_driver_y):
        for x_side in [-1.45, 1.45]:
            create_wheel(f"BigBoy_FrontDriver_{i+1}_{'L' if x_side < 0 else 'R'}",
                         driver_radius, wheel_w, (x_side, y_pos, 0.86), mats, is_driver=True)
        # Axle
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.18, depth=2.9, location=(0, y_pos, 0.86), rotation=(0, math.radians(90), 0)
        )
        assign_material(bpy.context.active_object, mats['steel'])

    # Front Side Rods (Left & Right)
    for x_side in [-1.6, 1.6]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(x_side, -3.7, 1.29)
        )
        rod = bpy.context.active_object
        rod.name = f"BigBoy_FrontSideRod_{'L' if x_side < 0 else 'R'}"
        rod.scale = (0.08, 4.4, 0.12)
        assign_material(rod, mats['rods'])

    # --- 3. Rear Driver Set (8 Wheels / 4 Axles) ---
    rear_driver_y = [0.2, 1.6, 3.0, 4.4]
    for i, y_pos in enumerate(rear_driver_y):
        for x_side in [-1.45, 1.45]:
            create_wheel(f"BigBoy_RearDriver_{i+1}_{'L' if x_side < 0 else 'R'}",
                         driver_radius, wheel_w, (x_side, y_pos, 0.86), mats, is_driver=True)
        # Axle
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.18, depth=2.9, location=(0, y_pos, 0.86), rotation=(0, math.radians(90), 0)
        )
        assign_material(bpy.context.active_object, mats['steel'])

    # Rear Side Rods (Left & Right)
    for x_side in [-1.6, 1.6]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(x_side, 2.3, 1.29)
        )
        rod = bpy.context.active_object
        rod.name = f"BigBoy_RearSideRod_{'L' if x_side < 0 else 'R'}"
        rod.scale = (0.08, 4.4, 0.12)
        assign_material(rod, mats['rods'])

    # --- 4. Trailing Truck (4 Wheels / 2 Axles) ---
    trailing_y = [5.8, 7.2]
    for i, y_pos in enumerate(trailing_y):
        for x_side in [-1.4, 1.4]:
            create_wheel(f"BigBoy_TrailingWheel_{i+1}_{'L' if x_side < 0 else 'R'}",
                         trailing_radius, wheel_w, (x_side, y_pos, 0.5), mats)
        # Axle
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.12, depth=2.8, location=(0, y_pos, 0.5), rotation=(0, math.radians(90), 0)
        )
        assign_material(bpy.context.active_object, mats['steel'])

    # --- 5. Cylinders (4 Steam Cylinders: 2 Front, 2 Rear) ---
    cylinder_locs = [
        (-1.7, -6.8, 1.1), (1.7, -6.8, 1.1),   # Front Cylinders
        (-1.7, -0.8, 1.1), (1.7, -0.8, 1.1)    # Rear Cylinders
    ]
    for i, loc in enumerate(cylinder_locs):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.55, depth=2.2, location=loc, rotation=(math.radians(90), 0, 0)
        )
        cyl = bpy.context.active_object
        cyl.name = f"BigBoy_Cylinder_{i+1}"
        assign_material(cyl, mats['steel'])

    # --- 6. Main Connecting Drive Rods ---
    main_rod_pairs = [
        ((-1.6, -5.3, 1.2), (-1.6, 0.7, 1.2)), # Left Front & Rear Main Rods
        ((1.6, -5.3, 1.2), (1.6, 0.7, 1.2))    # Right Front & Rear Main Rods
    ]
    for pair in main_rod_pairs:
        for pos in pair:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
            m_rod = bpy.context.active_object
            m_rod.name = "BigBoy_MainDriveRod"
            m_rod.scale = (0.1, 2.8, 0.15)
            assign_material(m_rod, mats['rods'])

def create_tender(mats):
    """Builds the large fuel and water tender wagon attached behind the cab."""
    # Tender Body Tank
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 14.5, 3.2))
    tender = bpy.context.active_object
    tender.name = "BigBoy_TenderBody"
    tender.scale = (3.3, 9.5, 2.6)
    assign_material(tender, mats['steel'])

    # Coal Mound on top of Tender
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 12.0, 4.8))
    coal = bpy.context.active_object
    coal.name = "BigBoy_TenderCoal"
    coal.scale = (3.1, 5.0, 0.8)
    assign_material(coal, mats['coal'])

    # Tender Wheels (14 Wheels total: 7 Axles)
    tender_axle_y = [10.5, 11.8, 13.1, 14.4, 15.7, 17.5, 18.8]
    for i, y_pos in enumerate(tender_axle_y):
        for x_side in [-1.35, 1.35]:
            create_wheel(f"BigBoy_TenderWheel_{i+1}_{'L' if x_side < 0 else 'R'}",
                         0.45, 0.22, (x_side, y_pos, 0.45), mats)
        # Axle
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.1, depth=2.7, location=(0, y_pos, 0.45), rotation=(0, math.radians(90), 0)
        )
        assign_material(bpy.context.active_object, mats['steel'])

def create_details_and_headlight(mats):
    """Builds cowcatcher (pilot grate), front headlight, whistle, and handrails."""
    # Front Cowcatcher / Pilot Grate
    bpy.ops.mesh.primitive_cone_add(
        radius1=1.8, radius2=0.5, depth=1.2, location=(0, -8.8, 0.8), rotation=(math.radians(-90), 0, 0)
    )
    cowcatcher = bpy.context.active_object
    cowcatcher.name = "BigBoy_Cowcatcher"
    assign_material(cowcatcher, mats['steel'])

    # Center Front Headlight
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.35, depth=0.6, location=(0, -7.2, 3.7), rotation=(math.radians(90), 0, 0)
    )
    headlight_body = bpy.context.active_object
    headlight_body.name = "BigBoy_HeadlightHousing"
    assign_material(headlight_body, mats['brass'])

    # Headlight Lens / Glass
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.32, depth=0.08, location=(0, -7.51, 3.7), rotation=(math.radians(90), 0, 0)
    )
    lens = bpy.context.active_object
    lens.name = "BigBoy_HeadlightLens"
    assign_material(lens, mats['headlight'])

    # Steam Whistle Accent
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.08, depth=0.5, location=(-0.5, 6.2, 5.4)
    )
    whistle = bpy.context.active_object
    whistle.name = "BigBoy_Whistle"
    assign_material(whistle, mats['brass'])

    # Piping along Boiler
    for x_side in [-1.55, 1.55]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.04, depth=13.0, location=(x_side, 0.0, 3.6), rotation=(math.radians(90), 0, 0)
        )
        pipe = bpy.context.active_object
        pipe.name = f"BigBoy_BoilerPipe_{'L' if x_side < 0 else 'R'}"
        assign_material(pipe, mats['brass'])

def create_railroad_track(mats):
    """Builds steel rails and wooden ties beneath the Big Boy locomotive."""
    track_length = 32.0
    # Steel Rails (Left & Right)
    for x_side in [-1.45, 1.45]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(x_side, 4.0, 0.0)
        )
        rail = bpy.context.active_object
        rail.name = f"Track_Rail_{'L' if x_side < 0 else 'R'}"
        rail.scale = (0.12, track_length, 0.18)
        assign_material(rail, mats['rail'])

    # Wooden Ties (Sleepers along length)
    for y_pos in [y * 0.8 for y in range(-12, 26)]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(0, y_pos, -0.15)
        )
        tie = bpy.context.active_object
        tie.name = f"Track_Tie_{y_pos}"
        tie.scale = (3.6, 0.4, 0.15)
        assign_material(tie, mats['coal'])

def setup_studio_lighting_and_camera():
    """Sets up camera and cinematic 3-point lighting environment."""
    # Camera
    bpy.ops.object.camera_add(
        location=(-14.0, -16.0, 6.5), rotation=(math.radians(72), 0, math.radians(-42))
    )
    cam = bpy.context.active_object
    cam.name = "BigBoy_StudioCamera"
    bpy.context.scene.camera = cam

    # Sun / Key Light
    bpy.ops.object.light_add(
        type='SUN', location=(-10, -10, 15)
    )
    key_light = bpy.context.active_object
    key_light.name = "Key_Light"
    key_light.data.energy = 4.5

    # Fill Light
    bpy.ops.object.light_add(
        type='AREA', location=(10, -5, 8)
    )
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 300.0

    # Rim Light
    bpy.ops.object.light_add(
        type='SPOT', location=(0, 22, 12)
    )
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Light"
    rim_light.data.energy = 800.0

def build_union_pacific_big_boy():
    """Master build function."""
    print("Initializing Union Pacific Big Boy 4014 procedural generation...")
    reset_scene()
    mats = create_materials()

    create_boiler_and_cab(mats)
    create_4884_running_gear(mats)
    create_tender(mats)
    create_details_and_headlight(mats)
    create_railroad_track(mats)
    setup_studio_lighting_and_camera()

    print("Successfully generated Union Pacific Big Boy 4014 3D Hard-Surface Model!")

if __name__ == "__main__":
    build_union_pacific_big_boy()
