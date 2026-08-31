"""
===============================================================================
BAGEL CONCEPT CAR-BUS - 3D GENERATOR FOR BLENDER (bpy)
===============================================================================
Description:
    Generates a high-quality, hard-surface "Bagel" concept car-bus 3D model
    inspired by retro UAZ-452 cab-over vans with futuristic concept details.

    Features:
      - Complete scene reset (clears existing objects & orphan data)
      - Organized collections: BODY, GLASS, WHEELS, LIGHTS, DETAILS, ENVIRONMENT, RIG
      - Procedural PBR shaders (mint/teal body paint, cream roof, dark glass, rubber, chrome, lights)
      - Detailed rounded exterior shell, roof, wheel arches, bumpers, glass panels
      - 4 detailed wheels (tires + metallic multi-spoke rims)
      - Front headlights, rear taillights, turn indicators with emissive shaders
      - Exterior accessories: tubular roof rack, roof pod equipment, rear satellite dish, side mirrors, door handles, rear ladder
      - Studio floor backdrop, camera, and dynamic 3-point lighting setup
      - Auto-smooth and bevel modifiers for clean hard-surface shading

Usage:
    Open Blender (v3.5+) -> Go to Scripting tab -> New Script -> Paste & Run Script.
===============================================================================
"""

import math
import bpy
import mathutils


# =============================================================================
# 1. SCENE CLEANUP & COLLECTION SETUP
# =============================================================================

def reset_scene():
    """Clears all existing objects, meshes, materials, lights, and cameras in the scene."""
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select all objects and delete
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Purge unused mesh and material data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)


def setup_collections():
    """Creates a clean collection hierarchy for organizing the car-bus model."""
    collection_names = ["BODY", "GLASS", "WHEELS", "LIGHTS", "DETAILS", "ENVIRONMENT", "RIG"]
    collections = {}

    scene_collection = bpy.context.scene.collection

    for name in collection_names:
        if name in scene_collection.children:
            col = scene_collection.children[name]
        else:
            col = bpy.data.collections.new(name)
            scene_collection.children.link(col)
        collections[name] = col

    return collections


def link_to_collection(obj, collection):
    """Links an object to a target collection and unlinks from active scene collection if needed."""
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    for col in bpy.data.collections:
        if col != collection and obj.name in col.objects:
            col.objects.unlink(obj)


# =============================================================================
# 2. MATERIAL CREATION (PBR SHADERS)
# =============================================================================

def create_material(name, base_color, metallic=0.0, roughness=0.5, transmission=0.0, emission_color=(0, 0, 0, 1), emission_strength=0.0):
    """Utility function to build Principled BSDF materials."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial')

    # Principled BSDF node
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')

    # Configure BSDF inputs
    if 'Base Color' in node_bsdf.inputs:
        node_bsdf.inputs['Base Color'].default_value = base_color
    if 'Metallic' in node_bsdf.inputs:
        node_bsdf.inputs['Metallic'].default_value = metallic
    if 'Roughness' in node_bsdf.inputs:
        node_bsdf.inputs['Roughness'].default_value = roughness
    if 'Transmission' in node_bsdf.inputs:
        node_bsdf.inputs['Transmission'].default_value = transmission
    elif 'Transmission Weight' in node_bsdf.inputs: # Compatibility with Blender 4.0+
        node_bsdf.inputs['Transmission Weight'].default_value = transmission

    # Emission handling
    if emission_strength > 0:
        if 'Emission Color' in node_bsdf.inputs:
            node_bsdf.inputs['Emission Color'].default_value = emission_color
            node_bsdf.inputs['Emission Strength'].default_value = emission_strength
        elif 'Emission' in node_bsdf.inputs:
            node_bsdf.inputs['Emission'].default_value = emission_color

    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])

    # Glass material transparency settings
    if transmission > 0:
        if hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
        if hasattr(mat, "shadow_method"):
            mat.shadow_method = 'NONE'

    return mat


def build_materials_library():
    """Generates all PBR materials required for the Bagel vehicle."""
    mats = {}

    # 1. Main Body: Glossy Retro Mint / Teal Green Metallic Paint
    mats['Body_MintTeal'] = create_material(
        name="Mat_Body_MintTeal",
        base_color=(0.18, 0.52, 0.45, 1.0),
        metallic=0.2,
        roughness=0.18
    )

    # 2. Roof & Trim: Off-White / Cream Paint
    mats['Body_CreamWhite'] = create_material(
        name="Mat_Body_CreamWhite",
        base_color=(0.92, 0.90, 0.84, 1.0),
        metallic=0.05,
        roughness=0.25
    )

    # 3. Tinted Glass Windows
    mats['Glass_Tinted'] = create_material(
        name="Mat_Glass_Tinted",
        base_color=(0.05, 0.08, 0.1, 1.0),
        metallic=0.1,
        roughness=0.05,
        transmission=0.85
    )

    # 4. Rubber Tires
    mats['Tire_Rubber'] = create_material(
        name="Mat_Tire_Rubber",
        base_color=(0.08, 0.08, 0.08, 1.0),
        metallic=0.0,
        roughness=0.65
    )

    # 5. Metallic Rims
    mats['Rim_Metal'] = create_material(
        name="Mat_Rim_Metal",
        base_color=(0.8, 0.82, 0.85, 1.0),
        metallic=0.9,
        roughness=0.2
    )

    # 6. Chrome / Polished Metal Accessories
    mats['Chrome_Metal'] = create_material(
        name="Mat_Chrome_Metal",
        base_color=(0.9, 0.9, 0.92, 1.0),
        metallic=0.95,
        roughness=0.12
    )

    # 7. Dark Plastic Bumpers & Trim
    mats['Dark_Plastic'] = create_material(
        name="Mat_Dark_Plastic",
        base_color=(0.04, 0.04, 0.05, 1.0),
        metallic=0.1,
        roughness=0.45
    )

    # 8. Headlights (Emissive Warm White)
    mats['Light_Headlight'] = create_material(
        name="Mat_Light_Headlight",
        base_color=(1.0, 0.95, 0.8, 1.0),
        metallic=0.1,
        roughness=0.1,
        emission_color=(1.0, 0.95, 0.8, 1.0),
        emission_strength=4.0
    )

    # 9. Taillights (Emissive Red)
    mats['Light_Taillight'] = create_material(
        name="Mat_Light_Taillight",
        base_color=(0.9, 0.05, 0.05, 1.0),
        metallic=0.1,
        roughness=0.15,
        emission_color=(1.0, 0.05, 0.05, 1.0),
        emission_strength=3.5
    )

    # 10. Turn Indicators (Emissive Amber)
    mats['Light_Indicator'] = create_material(
        name="Mat_Light_Indicator",
        base_color=(1.0, 0.45, 0.0, 1.0),
        metallic=0.1,
        roughness=0.15,
        emission_color=(1.0, 0.5, 0.0, 1.0),
        emission_strength=3.0
    )

    # 11. Tech Equipment / Dish Body
    mats['Equipment_Metal'] = create_material(
        name="Mat_Equipment_Metal",
        base_color=(0.7, 0.72, 0.75, 1.0),
        metallic=0.8,
        roughness=0.3
    )

    # 12. Studio Backdrop Floor
    mats['Studio_Floor'] = create_material(
        name="Mat_Studio_Floor",
        base_color=(0.12, 0.13, 0.15, 1.0),
        metallic=0.0,
        roughness=0.5
    )

    return mats


# =============================================================================
# 3. HELPER GEOMETRY FUNCTIONS
# =============================================================================

def set_smooth_shading(obj):
    """Sets object shade smooth and enables auto smooth for hard-surface edges."""
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True
        # Enable auto smooth if available on mesh data
        if hasattr(obj.data, "use_auto_smooth"):
            obj.data.use_auto_smooth = True
            if hasattr(obj.data, "auto_smooth_angle"):
                obj.data.auto_smooth_angle = math.radians(35)


def add_bevel_modifier(obj, width=0.02, segments=2):
    """Applies a Bevel modifier to round off sharp hard-surface mesh edges."""
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(30)


def apply_material(obj, mat):
    """Assigns a material to a mesh object."""
    if obj and mat:
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat


# =============================================================================
# 4. VEHICLE BODY & CABIN GENERATION
# =============================================================================

def create_bagel_body(collections, mats):
    """Creates the rounded UAZ-452 cab-over inspired main body shell and roof."""

    # --- Main Lower Body Shell ---
    # Create cube base scaled to dimensions (~4.4m L x 2.0m W x 1.6m H for lower shell)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.1))
    body_obj = bpy.context.active_object
    body_obj.name = "Body_Main"
    body_obj.scale = (2.0, 4.4, 1.5)
    bpy.ops.object.transform_apply(scale=True)

    link_to_collection(body_obj, collections['BODY'])
    apply_material(body_obj, mats['Body_MintTeal'])

    # Add Subdivision & Bevel for retro smooth cab-over curve silhouette
    sub_mod = body_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    sub_mod.levels = 2
    sub_mod.render_levels = 3

    add_bevel_modifier(body_obj, width=0.04, segments=3)
    set_smooth_shading(body_obj)

    # --- Cream/Off-White Roof Cap ---
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.95))
    roof_obj = bpy.context.active_object
    roof_obj.name = "Body_Roof"
    roof_obj.scale = (1.92, 4.25, 0.45)
    bpy.ops.object.transform_apply(scale=True)

    link_to_collection(roof_obj, collections['BODY'])
    apply_material(roof_obj, mats['Body_CreamWhite'])

    roof_sub = roof_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    roof_sub.levels = 2
    roof_sub.render_levels = 3

    add_bevel_modifier(roof_obj, width=0.03, segments=3)
    set_smooth_shading(roof_obj)

    # --- Front Nose & Grille Panel ---
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.18, 1.05))
    grille_obj = bpy.context.active_object
    grille_obj.name = "Body_FrontGrille"
    grille_obj.scale = (1.4, 0.08, 0.4)
    bpy.ops.object.transform_apply(scale=True)

    link_to_collection(grille_obj, collections['BODY'])
    apply_material(grille_obj, mats['Dark_Plastic'])
    add_bevel_modifier(grille_obj, width=0.015, segments=2)
    set_smooth_shading(grille_obj)

    # Horizontal grille vent lines
    for i in range(3):
        z_pos = 0.93 + i * 0.08
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.21, z_pos))
        slat = bpy.context.active_object
        slat.name = f"Grille_Slat_{i+1}"
        slat.scale = (1.3, 0.04, 0.02)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(slat, collections['BODY'])
        apply_material(slat, mats['Chrome_Metal'])

    # --- Wheel Arch / Fender Flares ---
    fender_coords = [
        ("Fender_FL", 1.02, 1.25, 0.72),
        ("Fender_FR", -1.02, 1.25, 0.72),
        ("Fender_RL", 1.02, -1.25, 0.72),
        ("Fender_RR", -1.02, -1.25, 0.72),
    ]

    for name, x, y, z in fender_coords:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.55, depth=0.22, location=(x, y, z), rotation=(0, math.radians(90), 0)
        )
        fender = bpy.context.active_object
        fender.name = name
        fender.scale = (1.0, 1.15, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(fender, collections['BODY'])
        apply_material(fender, mats['Dark_Plastic'])
        add_bevel_modifier(fender, width=0.02, segments=2)
        set_smooth_shading(fender)

    # --- Front & Rear Bumpers ---
    # Front Heavy Bumper
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.25, 0.52))
    f_bumper = bpy.context.active_object
    f_bumper.name = "Bumper_Front"
    f_bumper.scale = (2.08, 0.22, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    link_to_collection(f_bumper, collections['BODY'])
    apply_material(f_bumper, mats['Dark_Plastic'])
    add_bevel_modifier(f_bumper, width=0.03, segments=2)
    set_smooth_shading(f_bumper)

    # Front Tow Shackles
    for side, x in [("L", 0.5), ("R", -0.5)]:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.06, minor_radius=0.02, location=(x, 2.37, 0.52), rotation=(math.radians(90), 0, 0)
        )
        shackle = bpy.context.active_object
        shackle.name = f"TowHook_Front_{side}"
        link_to_collection(shackle, collections['BODY'])
        apply_material(shackle, mats['Chrome_Metal'])

    # Rear Bumper
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -2.25, 0.55))
    r_bumper = bpy.context.active_object
    r_bumper.name = "Bumper_Rear"
    r_bumper.scale = (2.08, 0.22, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    link_to_collection(r_bumper, collections['BODY'])
    apply_material(r_bumper, mats['Dark_Plastic'])
    add_bevel_modifier(r_bumper, width=0.03, segments=2)
    set_smooth_shading(r_bumper)


# =============================================================================
# 5. WINDOWS & GLASS PANELS
# =============================================================================

def create_bagel_windows(collections, mats):
    """Creates front curved windshield, panoramic side windows, and rear glass elements."""

    # --- Panoramic Front Windshield ---
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.05, 1.55))
    windshield = bpy.context.active_object
    windshield.name = "Windshield_Front"
    windshield.rotation_euler = (math.radians(-14), 0, 0)
    windshield.scale = (1.65, 0.06, 0.62)
    bpy.ops.object.transform_apply(scale=True)

    link_to_collection(windshield, collections['GLASS'])
    apply_material(windshield, mats['Glass_Tinted'])
    add_bevel_modifier(windshield, width=0.01, segments=2)
    set_smooth_shading(windshield)

    # --- Side Windows (Left & Right Rows) ---
    window_positions = [
        ("Window_Front_L", 0.98, 1.25, 1.55, (1.1, 0.05, 0.52)),
        ("Window_Front_R", -0.98, 1.25, 1.55, (1.1, 0.05, 0.52)),
        ("Window_Mid_L", 0.98, 0.1, 1.55, (1.0, 0.05, 0.52)),
        ("Window_Mid_R", -0.98, 0.1, 1.55, (1.0, 0.05, 0.52)),
        ("Window_Rear_L", 0.98, -1.05, 1.55, (1.1, 0.05, 0.52)),
        ("Window_Rear_R", -0.98, -1.05, 1.55, (1.1, 0.05, 0.52)),
    ]

    for name, x, y, z, scale in window_positions:
        # Swap scale X/Y for side placement orientation
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z))
        win = bpy.context.active_object
        win.name = name
        win.scale = (scale[1], scale[0], scale[2])
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(win, collections['GLASS'])
        apply_material(win, mats['Glass_Tinted'])
        add_bevel_modifier(win, width=0.01, segments=2)
        set_smooth_shading(win)

    # --- Rear Door Window Glass ---
    for side, x in [("L", 0.42), ("R", -0.42)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -2.18, 1.55))
        r_win = bpy.context.active_object
        r_win.name = f"Window_Back_{side}"
        r_win.scale = (0.6, 0.05, 0.5)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(r_win, collections['GLASS'])
        apply_material(r_win, mats['Glass_Tinted'])
        add_bevel_modifier(r_win, width=0.01, segments=2)
        set_smooth_shading(r_win)


# =============================================================================
# 6. WHEELS & SUSPENSION ASSEMBLY
# =============================================================================

def create_wheel(name, location, collections, mats, mirror_x=False):
    """Generates a complete wheel assembly with treaded tire, rim, and hub cap."""
    wheel_group = []

    # 1. Outer Tire
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.42, minor_radius=0.16,
        major_segments=32, minor_segments=16,
        location=location,
        rotation=(0, math.radians(90), 0)
    )
    tire = bpy.context.active_object
    tire.name = f"{name}_Tire"
    link_to_collection(tire, collections['WHEELS'])
    apply_material(tire, mats['Tire_Rubber'])
    set_smooth_shading(tire)
    wheel_group.append(tire)

    # 2. Metallic Multi-Spoke Rim
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.32, depth=0.22, vertices=24,
        location=location,
        rotation=(0, math.radians(90), 0)
    )
    rim = bpy.context.active_object
    rim.name = f"{name}_Rim"
    link_to_collection(rim, collections['WHEELS'])
    apply_material(rim, mats['Rim_Metal'])
    add_bevel_modifier(rim, width=0.01, segments=2)
    set_smooth_shading(rim)
    wheel_group.append(rim)

    # 3. Center Metallic Hub Cap
    x_offset = -0.12 if mirror_x else 0.12
    hub_loc = (location[0] + x_offset, location[1], location[2])

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.12, depth=0.08, vertices=16,
        location=hub_loc,
        rotation=(0, math.radians(90), 0)
    )
    hub = bpy.context.active_object
    hub.name = f"{name}_HubCap"
    link_to_collection(hub, collections['WHEELS'])
    apply_material(hub, mats['Chrome_Metal'])
    set_smooth_shading(hub)
    wheel_group.append(hub)

    # 4. Concept Rim Spokes
    num_spokes = 5
    for i in range(num_spokes):
        angle = (2 * math.pi / num_spokes) * i
        spoke_y = location[1] + math.sin(angle) * 0.2
        spoke_z = location[2] + math.cos(angle) * 0.2

        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(hub_loc[0], spoke_y, spoke_z),
            rotation=(angle, 0, 0)
        )
        spoke = bpy.context.active_object
        spoke.name = f"{name}_Spoke_{i+1}"
        spoke.scale = (0.04, 0.05, 0.18)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(spoke, collections['WHEELS'])
        apply_material(spoke, mats['Rim_Metal'])
        set_smooth_shading(spoke)
        wheel_group.append(spoke)


def create_all_wheels(collections, mats):
    """Instantiates 4 wheels at the vehicle wheel arch positions."""
    wheel_coords = [
        ("Wheel_FL", (1.02, 1.25, 0.5), False),
        ("Wheel_FR", (-1.02, 1.25, 0.5), True),
        ("Wheel_RL", (1.02, -1.25, 0.5), False),
        ("Wheel_RR", (-1.02, -1.25, 0.5), True),
    ]

    for name, loc, mirror in wheel_coords:
        create_wheel(name, loc, collections, mats, mirror_x=mirror)


# =============================================================================
# 7. HEADLIGHTS & LIGHTING FIXTURES
# =============================================================================

def create_bagel_lights(collections, mats):
    """Creates front round headlights, turn signals, and rear taillights."""

    # --- Dual Round Front Headlights ---
    headlight_coords = [
        ("Headlight_Outer_L", 0.72, 2.21, 1.05),
        ("Headlight_Outer_R", -0.72, 2.21, 1.05),
        ("Headlight_Inner_L", 0.52, 2.22, 1.05),
        ("Headlight_Inner_R", -0.52, 2.22, 1.05),
    ]

    for name, x, y, z in headlight_coords:
        # Chrome Housing Ring
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.12, depth=0.06, location=(x, y, z), rotation=(math.radians(90), 0, 0)
        )
        housing = bpy.context.active_object
        housing.name = f"{name}_Housing"
        link_to_collection(housing, collections['LIGHTS'])
        apply_material(housing, mats['Chrome_Metal'])
        set_smooth_shading(housing)

        # Emissive Lens
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.10, location=(x, y + 0.02, z)
        )
        lens = bpy.context.active_object
        lens.name = f"{name}_Lens"
        lens.scale = (1.0, 0.3, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(lens, collections['LIGHTS'])
        apply_material(lens, mats['Light_Headlight'])
        set_smooth_shading(lens)

    # --- Amber Turn Signal Indicators ---
    for side, x in [("L", 0.92), ("R", -0.92)]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(x, 2.18, 0.82)
        )
        ind = bpy.context.active_object
        ind.name = f"Indicator_Front_{side}"
        ind.scale = (0.12, 0.04, 0.08)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(ind, collections['LIGHTS'])
        apply_material(ind, mats['Light_Indicator'])
        set_smooth_shading(ind)

    # --- Rear Taillight Assemblies ---
    taillight_coords = [
        ("Taillight_L", 0.82, -2.21, 1.1),
        ("Taillight_R", -0.82, -2.21, 1.1),
    ]

    for name, x, y, z in taillight_coords:
        # Dark Housing Box
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(x, y, z)
        )
        box = bpy.context.active_object
        box.name = f"{name}_Housing"
        box.scale = (0.16, 0.05, 0.42)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(box, collections['LIGHTS'])
        apply_material(box, mats['Dark_Plastic'])

        # Red Emissive Light Bar
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(x, y - 0.02, z + 0.08)
        )
        red_bar = bpy.context.active_object
        red_bar.name = f"{name}_RedBar"
        red_bar.scale = (0.12, 0.03, 0.18)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(red_bar, collections['LIGHTS'])
        apply_material(red_bar, mats['Light_Taillight'])

        # Amber Rear Indicator Bar
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(x, y - 0.02, z - 0.10)
        )
        amb_bar = bpy.context.active_object
        amb_bar.name = f"{name}_AmbBar"
        amb_bar.scale = (0.12, 0.03, 0.10)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(amb_bar, collections['LIGHTS'])
        apply_material(amb_bar, mats['Light_Indicator'])


# =============================================================================
# 8. EXTERIOR CONCEPT ACCESSORIES & HARD-SURFACE DETAILS
# =============================================================================

def create_bagel_details(collections, mats):
    """Creates roof rack, roof pod, signature rear satellite dish, mirrors, and handles."""

    # --- Tubular Roof Rack Frame ---
    # Main Outer Frame Tubes
    rack_bars = [
        ("Roof_Rack_Side_L", (0.85, 0.2, 2.22), (0.03, 3.2, 0.03)),
        ("Roof_Rack_Side_R", (-0.85, 0.2, 2.22), (0.03, 3.2, 0.03)),
        ("Roof_Rack_Front", (0.0, 1.75, 2.22), (1.7, 0.03, 0.03)),
        ("Roof_Rack_Rear", (0.0, -1.35, 2.22), (1.7, 0.03, 0.03)),
    ]

    for name, loc, scale in rack_bars:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        bar = bpy.context.active_object
        bar.name = name
        bar.scale = scale
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(bar, collections['DETAILS'])
        apply_material(bar, mats['Dark_Plastic'])
        set_smooth_shading(bar)

    # Roof Rack Crossbars
    for i in range(4):
        y_pos = 1.2 - i * 0.8
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y_pos, 2.22))
        cross = bpy.context.active_object
        cross.name = f"Roof_Rack_Crossbar_{i+1}"
        cross.scale = (1.68, 0.025, 0.025)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(cross, collections['DETAILS'])
        apply_material(cross, mats['Dark_Plastic'])

    # Roof Rack Supports / Mounts
    for x in [0.85, -0.85]:
        for y in [1.5, 0.3, -0.9]:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.025, depth=0.1, location=(x, y, 2.16)
            )
            supp = bpy.context.active_object
            supp.name = f"Roof_Rack_Mount_{x}_{y}"
            link_to_collection(supp, collections['DETAILS'])
            apply_material(supp, mats['Chrome_Metal'])

    # --- Roof Tech Equipment Pod / HVAC Unit ---
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.8, 2.32))
    pod = bpy.context.active_object
    pod.name = "Roof_Equipment_Pod"
    pod.scale = (0.9, 0.8, 0.16)
    bpy.ops.object.transform_apply(scale=True)
    link_to_collection(pod, collections['DETAILS'])
    apply_material(pod, mats['Equipment_Metal'])
    add_bevel_modifier(pod, width=0.015, segments=2)
    set_smooth_shading(pod)

    # Pod Air Vents
    for i in range(4):
        x_pos = -0.3 + i * 0.2
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_pos, 0.8, 2.41))
        vent = bpy.context.active_object
        vent.name = f"Roof_Pod_Vent_{i+1}"
        vent.scale = (0.08, 0.6, 0.02)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(vent, collections['DETAILS'])
        apply_material(vent, mats['Dark_Plastic'])

    # --- Signature Concept Rear Satellite Dish Assembly ---
    # Dish Mount Base
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.15, depth=0.15, location=(0, -1.85, 2.15)
    )
    dish_base = bpy.context.active_object
    dish_base.name = "Satellite_Dish_Base"
    link_to_collection(dish_base, collections['DETAILS'])
    apply_material(dish_base, mats['Dark_Plastic'])

    # Dish Arm Bracket
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.03, depth=0.35, location=(0, -1.85, 2.32), rotation=(0, math.radians(25), 0)
    )
    dish_arm = bpy.context.active_object
    dish_arm.name = "Satellite_Dish_Arm"
    link_to_collection(dish_arm, collections['DETAILS'])
    apply_material(dish_arm, mats['Chrome_Metal'])

    # Parabolic Dish Reflector
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.35, location=(0.08, -1.85, 2.48), rotation=(0, math.radians(40), 0)
    )
    dish = bpy.context.active_object
    dish.name = "Satellite_Dish_Reflector"
    dish.scale = (0.25, 1.0, 1.0) # Flatten sphere to form parabolic dish
    bpy.ops.object.transform_apply(scale=True)
    link_to_collection(dish, collections['DETAILS'])
    apply_material(dish, mats['Equipment_Metal'])
    set_smooth_shading(dish)

    # Dish Feed Horn / Transceiver
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.04, radius2=0.01, depth=0.15,
        location=(0.22, -1.85, 2.56), rotation=(0, math.radians(-50), 0)
    )
    horn = bpy.context.active_object
    horn.name = "Satellite_Dish_FeedHorn"
    link_to_collection(horn, collections['DETAILS'])
    apply_material(horn, mats['Chrome_Metal'])

    # --- Side Mirrors ---
    mirror_coords = [
        ("Mirror_L", 1.08, 1.82, 1.42, 15),
        ("Mirror_R", -1.08, 1.82, 1.42, -15),
    ]

    for name, x, y, z, angle in mirror_coords:
        # Arm
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.02, depth=0.22, location=(x, y, z), rotation=(0, math.radians(90), 0)
        )
        arm = bpy.context.active_object
        arm.name = f"{name}_Arm"
        link_to_collection(arm, collections['DETAILS'])
        apply_material(arm, mats['Dark_Plastic'])

        # Casing
        offset_x = 0.12 if x > 0 else -0.12
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(x + offset_x, y + 0.05, z)
        )
        casing = bpy.context.active_object
        casing.name = f"{name}_Casing"
        casing.rotation_euler = (0, 0, math.radians(angle))
        casing.scale = (0.08, 0.18, 0.28)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(casing, collections['DETAILS'])
        apply_material(casing, mats['Body_CreamWhite'])
        add_bevel_modifier(casing, width=0.01, segments=2)
        set_smooth_shading(casing)

        # Mirror Glass Face
        glass_x = (x + offset_x) - (0.04 if x > 0 else -0.04)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(glass_x, y + 0.05, z)
        )
        m_glass = bpy.context.active_object
        m_glass.name = f"{name}_Glass"
        m_glass.scale = (0.01, 0.16, 0.26)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(m_glass, collections['DETAILS'])
        apply_material(m_glass, mats['Chrome_Metal'])

    # --- Flush Hard-Surface Door Handles ---
    handle_coords = [
        ("Handle_Door_FL", 1.01, 1.1, 1.15),
        ("Handle_Door_FR", -1.01, 1.1, 1.15),
        ("Handle_Door_RL", 1.01, -0.4, 1.15),
        ("Handle_Door_RR", -1.01, -0.4, 1.15),
        ("Handle_Door_Back", 0.0, -2.21, 1.15),
    ]

    for name, x, y, z in handle_coords:
        rot_z = 90 if x == 0 else 0
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(x, y, z), rotation=(0, 0, math.radians(rot_z))
        )
        hnd = bpy.context.active_object
        hnd.name = name
        hnd.scale = (0.04, 0.18, 0.04)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(hnd, collections['DETAILS'])
        apply_material(hnd, mats['Chrome_Metal'])
        add_bevel_modifier(hnd, width=0.005, segments=2)

    # --- Rear Roof Access Ladder ---
    ladder_x = -0.65
    for i in range(5):
        z_pos = 0.8 + i * 0.28
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(ladder_x, -2.24, z_pos)
        )
        rung = bpy.context.active_object
        rung.name = f"Rear_Ladder_Rung_{i+1}"
        rung.scale = (0.32, 0.025, 0.025)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(rung, collections['DETAILS'])
        apply_material(rung, mats['Dark_Plastic'])

    # Ladder Vertical Side Rails
    for side_x in [ladder_x - 0.16, ladder_x + 0.16]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(side_x, -2.24, 1.36)
        )
        rail = bpy.context.active_object
        rail.name = f"Rear_Ladder_Rail_{side_x}"
        rail.scale = (0.025, 0.025, 1.25)
        bpy.ops.object.transform_apply(scale=True)
        link_to_collection(rail, collections['DETAILS'])
        apply_material(rail, mats['Dark_Plastic'])


# =============================================================================
# 9. ENVIRONMENT, CAMERA & THREE-POINT LIGHTING
# =============================================================================

def create_environment_and_camera(collections, mats):
    """Sets up studio backdrop, 3/4 perspective main camera, and studio lighting."""

    # --- Studio Ground Floor Plane with Curved Backdrop ---
    bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    link_to_collection(floor, collections['ENVIRONMENT'])
    apply_material(floor, mats['Studio_Floor'])

    # --- Main Studio Camera ---
    cam_data = bpy.data.cameras.new(name="Camera_Main")
    cam_data.lens = 50 # 50mm focal length for clean, distortion-free perspective
    cam_obj = bpy.data.objects.new("Camera_Main", cam_data)

    # Position camera for cinematic 3/4 front view
    cam_obj.location = (6.2, 7.5, 3.2)
    cam_obj.rotation_euler = (math.radians(72), 0, math.radians(132))

    link_to_collection(cam_obj, collections['ENVIRONMENT'])
    bpy.context.scene.camera = cam_obj

    # --- Three-Point Studio Lighting Setup ---
    # 1. Key Light (Main Soft Sun/Area)
    key_light_data = bpy.data.lights.new(name="Light_Key", type='AREA')
    key_light_data.energy = 800
    key_light_data.size = 5.0
    key_light_obj = bpy.data.objects.new("Light_Key", key_light_data)
    key_light_obj.location = (5.0, 6.0, 6.0)
    key_light_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))
    link_to_collection(key_light_obj, collections['ENVIRONMENT'])

    # 2. Fill Light (Softer shadow filler)
    fill_light_data = bpy.data.lights.new(name="Light_Fill", type='AREA')
    fill_light_data.energy = 350
    fill_light_data.size = 6.0
    fill_light_obj = bpy.data.objects.new("Light_Fill", fill_light_data)
    fill_light_obj.location = (-6.0, 4.0, 4.5)
    fill_light_obj.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-45))
    link_to_collection(fill_light_obj, collections['ENVIRONMENT'])

    # 3. Rim / Edge Light (Highlights car contours from behind)
    rim_light_data = bpy.data.lights.new(name="Light_Rim", type='SPOT')
    rim_light_data.energy = 1200
    rim_light_data.spot_size = math.radians(60)
    rim_light_obj = bpy.data.objects.new("Light_Rim", rim_light_data)
    rim_light_obj.location = (-4.0, -6.0, 5.0)
    rim_light_obj.rotation_euler = (math.radians(-45), math.radians(-30), math.radians(-140))
    link_to_collection(rim_light_obj, collections['ENVIRONMENT'])


# =============================================================================
# 10. RIG CONTAINER / ROOT EMPTY SETUP
# =============================================================================

def create_rig_container(collections):
    """Creates a root empty object in RIG collection to anchor vehicle parts for editing & animation."""
    root_empty = bpy.data.objects.new("Bagel_Vehicle_Root", None)
    root_empty.empty_display_type = 'CUBE'
    root_empty.empty_display_size = 2.5
    root_empty.location = (0, 0, 0)
    link_to_collection(root_empty, collections['RIG'])
    return root_empty


# =============================================================================
# MAIN EXECUTION ENTRY POINT
# =============================================================================

def build_bagel_concept_vehicle():
    """Main function executing scene reset, material creation, geometry building, and setup."""
    print("=====================================================")
    print("Generating Bagel Concept Car-Bus 3D Model...")
    print("=====================================================")

    # 1. Clear existing scene
    reset_scene()

    # 2. Build collection hierarchy
    collections = setup_collections()

    # 3. Generate PBR materials library
    mats = build_materials_library()

    # 4. Create root rig empty
    create_rig_container(collections)

    # 5. Build vehicle components
    create_bagel_body(collections, mats)
    create_bagel_windows(collections, mats)
    create_all_wheels(collections, mats)
    create_bagel_lights(collections, mats)
    create_bagel_details(collections, mats)

    # 6. Create studio environment, camera, and lighting
    create_environment_and_camera(collections, mats)

    print("=====================================================")
    print("Successfully generated Bagel Concept Car-Bus model!")
    print("Collections created: BODY, GLASS, WHEELS, LIGHTS, DETAILS, ENVIRONMENT, RIG")
    print("=====================================================")


if __name__ == "__main__":
    build_bagel_concept_vehicle()
