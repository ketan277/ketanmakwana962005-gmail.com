"""
Steam Train Boiler Generator for Blender 3.5+
=============================================
Programmatically generates a detailed, high-poly steam train boiler section based on
hard-surface modeling techniques outlined in the tutorial.

Features:
- Main cylindrical boiler with raised metal bands
- Smokebox front plate & dish-shaped front door with brass latch details
- Flared chimney with brass trim lip and Shrinkwrap target setup
- Small dome (safety valve dome) with brass accents
- Big dome (steam dome) with smooth dome cap
- Boiler side plates, running board framing, and front buffer beam mounts
- PBR procedural materials (Dark Painted Boiler Metal, Structural Raw Steel, Brass Details)
- Studio 3-point lighting setup and camera configured for immediate preview
- Modular, clean code using pure `bpy` and `bmesh` native APIs

Author: Automated Blender MCP Pipeline
"""

import bpy
import bmesh
import math


def clean_existing_scene():
    """Removes default objects (Cube, Light, Camera) if present."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Remove orphaned data blocks to keep scene clean
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def get_or_create_collection(collection_name):
    """Retrieves an existing collection or creates a new one linked to scene root."""
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]
    collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def create_pbr_material(name, color, metallic=0.0, roughness=0.5, clearcoat=0.0):
    """Creates a native Blender Principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    if bsdf:
        # Compatibility with Blender 3.5+ and 4.0+ BSDF input socket naming
        base_color_key = "Base Color" if "Base Color" in bsdf.inputs else 0
        metallic_key = "Metallic" if "Metallic" in bsdf.inputs else "Metallic"
        roughness_key = "Roughness" if "Roughness" in bsdf.inputs else "Roughness"

        bsdf.inputs[base_color_key].default_value = color
        bsdf.inputs[metallic_key].default_value = metallic
        bsdf.inputs[roughness_key].default_value = roughness

        if "Coat Weight" in bsdf.inputs:  # Blender 4.0+
            bsdf.inputs["Coat Weight"].default_value = clearcoat
        elif "Clearcoat" in bsdf.inputs:  # Blender 3.x
            bsdf.inputs["Clearcoat"].default_value = clearcoat

    return mat


def set_auto_smooth(obj, angle_degrees=30):
    """Enables auto smooth for a mesh object across Blender 3.x and 4.x."""
    mesh = obj.data
    if hasattr(mesh, "use_auto_smooth"):
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = math.radians(angle_degrees)
    else:
        # For Blender 4.1+, shade smooth by angle modifier or smooth shading operator
        for polygon in mesh.polygons:
            polygon.use_smooth = True


def create_boiler_main(collection, mat_boiler, mat_metal):
    """
    Creates the main cylindrical boiler body with raised riveted/beveled metal bands.
    """
    mesh = bpy.data.meshes.new("Boiler_Main_Mesh")
    obj = bpy.data.objects.new("Boiler_Main", mesh)
    collection.objects.link(obj)

    bm = bmesh.new()

    # Create main boiler cylinder along X axis
    # Radius = 0.75m, Length = 4.2m (X from -2.6 to 1.6)
    radius = 0.75
    sections = 32
    length_segments = 24
    start_x = -2.6
    end_x = 1.6

    # Generate cylinder grid
    grid_verts = []
    for i in range(length_segments + 1):
        x = start_x + (end_x - start_x) * (i / length_segments)
        ring = []
        for j in range(sections):
            angle = 2 * math.pi * j / sections
            y = radius * math.sin(angle)
            z = radius * math.cos(angle) + 0.95  # Center at Z=0.95m above rail
            ring.append(bm.verts.new((x, y, z)))
        grid_verts.append(ring)

    bm.verts.ensure_lookup_table()

    # Create quad faces for cylinder body
    for i in range(length_segments):
        for j in range(sections):
            v1 = grid_verts[i][j]
            v2 = grid_verts[i][(j + 1) % sections]
            v3 = grid_verts[i + 1][(j + 1) % sections]
            v4 = grid_verts[i + 1][j]
            bm.faces.new((v1, v2, v3, v4))

    # Add raised metal bands at specific X locations along boiler
    band_indices = [3, 8, 13, 18]
    bm.faces.ensure_lookup_table()

    # Identify faces belonging to band segments and extrude outward
    band_faces = []
    for face in bm.faces:
        center_x = face.calc_center_median().x
        for b_idx in band_indices:
            target_x = start_x + (end_x - start_x) * (b_idx / length_segments)
            if abs(center_x - target_x) < 0.1:
                band_faces.append(face)
                break

    if band_faces:
        extruded = bmesh.ops.extrude_face_region(bm, geom=band_faces)
        extruded_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
        # Push extruded verts outwards radially
        for v in extruded_verts:
            dx = v.co.x
            dy = v.co.y
            dz = v.co.z - 0.95
            dist = math.sqrt(dy*dy + dz*dz)
            if dist > 0:
                scale = (dist + 0.02) / dist
                v.co.y = dy * scale
                v.co.z = 0.95 + dz * scale

    bm.to_mesh(mesh)
    bm.free()

    # Assign material
    mesh.materials.append(mat_boiler)
    mesh.materials.append(mat_metal)

    # Set smooth shading
    for poly in mesh.polygons:
        poly.use_smooth = True
    set_auto_smooth(obj, 35)

    # Add Subdivision Surface Modifier
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.render_levels = 2
    subsurf.levels = 1

    return obj


def create_smokebox_front(collection, mat_boiler, mat_brass):
    """
    Creates the front smokebox plate and dish-shaped boiler door with central latch hub.
    """
    mesh = bpy.data.meshes.new("Smokebox_Front_Door_Mesh")
    obj = bpy.data.objects.new("Smokebox_Front_Door", mesh)
    collection.objects.link(obj)

    bm = bmesh.new()

    center_x = 1.6
    center_z = 0.95
    radius = 0.76
    segments = 32

    # Ring 1: Outer flange rim
    outer_ring = []
    for j in range(segments):
        angle = 2 * math.pi * j / segments
        y = radius * math.sin(angle)
        z = radius * math.cos(angle) + center_z
        outer_ring.append(bm.verts.new((center_x, y, z)))

    # Ring 2: Stepped door boundary
    step_ring = []
    step_radius = 0.70
    door_offset_x = center_x + 0.04
    for j in range(segments):
        angle = 2 * math.pi * j / segments
        y = step_radius * math.sin(angle)
        z = step_radius * math.cos(angle) + center_z
        step_ring.append(bm.verts.new((door_offset_x, y, z)))

    # Ring 3: Convex bulge apex
    apex_ring = []
    apex_radius = 0.35
    apex_offset_x = center_x + 0.14
    for j in range(segments):
        angle = 2 * math.pi * j / segments
        y = apex_radius * math.sin(angle)
        z = apex_radius * math.cos(angle) + center_z
        apex_ring.append(bm.verts.new((apex_offset_x, y, z)))

    # Center vertex for latch hub
    center_vert = bm.verts.new((center_x + 0.18, 0, center_z))

    # Connect faces
    for j in range(segments):
        n = (j + 1) % segments
        # Flange ring face
        bm.faces.new((outer_ring[j], outer_ring[n], step_ring[n], step_ring[j]))
        # Door dish face
        bm.faces.new((step_ring[j], step_ring[n], apex_ring[n], apex_ring[j]))
        # Center cap faces
        bm.faces.new((apex_ring[j], apex_ring[n], center_vert))

    bm.to_mesh(mesh)
    bm.free()

    # Assign materials
    mesh.materials.append(mat_boiler)
    mesh.materials.append(mat_brass)

    for poly in mesh.polygons:
        poly.use_smooth = True
    set_auto_smooth(obj, 30)

    # Add Subsurf modifier
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.render_levels = 2
    subsurf.levels = 1

    # Add central latch handle wheel (brass detail)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.10,
        minor_radius=0.018,
        location=(center_x + 0.19, 0, center_z),
        rotation=(0, math.radians(90), 0)
    )
    latch_obj = bpy.context.active_object
    latch_obj.name = "Smokebox_Door_Latch"
    latch_obj.data.materials.append(mat_brass)

    # Parent latch to door
    latch_obj.parent = obj

    return obj


def create_chimney(boiler_obj, collection, mat_boiler, mat_brass):
    """
    Creates the chimney/smokestack with flared top rim and Shrinkwrap target setup.
    """
    mesh = bpy.data.meshes.new("Chimney_Mesh")
    obj = bpy.data.objects.new("Chimney", mesh)
    collection.objects.link(obj)

    bm = bmesh.new()

    segments = 32
    base_x = 1.10
    base_z_center = 0.95

    # Height profile of chimney along Z
    profile = [
        # (height_above_center, radius, material_index)
        (0.70, 0.25, 0),  # Base flange (conforming to boiler surface)
        (0.75, 0.22, 0),  # Neck start
        (1.10, 0.20, 0),  # Tapered column shaft
        (1.35, 0.26, 0),  # Flared top expander
        (1.42, 0.28, 1),  # Decorative brass top rim lip
        (1.42, 0.22, 1),  # Inward lip step
        (1.15, 0.21, 0),  # Inner smoke funnel wall
    ]

    rings = []
    for height, radius, mat_idx in profile:
        ring = []
        for j in range(segments):
            angle = 2 * math.pi * j / segments
            y = radius * math.sin(angle)
            z = height + base_z_center
            ring.append(bm.verts.new((base_x, y, z)))
        rings.append(ring)

    for r in range(len(profile) - 1):
        mat_idx = profile[r][2]
        for j in range(segments):
            n = (j + 1) % segments
            face = bm.faces.new((rings[r][j], rings[r][n], rings[r+1][n], rings[r+1][j]))
            face.material_index = mat_idx

    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_boiler)
    mesh.materials.append(mat_brass)

    for poly in mesh.polygons:
        poly.use_smooth = True
    set_auto_smooth(obj, 30)

    # Add Shrinkwrap modifier targeting boiler_obj to fit curved base seamlessly
    shrinkwrap = obj.modifiers.new(name="Shrinkwrap_Base", type='SHRINKWRAP')
    shrinkwrap.target = boiler_obj
    shrinkwrap.wrap_method = 'NEAREST_SURFACEPOINT'
    shrinkwrap.show_in_editmode = False

    # Add Subdivision surface modifier
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.render_levels = 2
    subsurf.levels = 1

    return obj


def create_small_dome(boiler_obj, collection, mat_boiler, mat_brass):
    """
    Creates the safety valve / small dome section on top of the boiler.
    """
    mesh = bpy.data.meshes.new("Small_Dome_Mesh")
    obj = bpy.data.objects.new("Small_Dome", mesh)
    collection.objects.link(obj)

    bm = bmesh.new()
    segments = 32
    base_x = -0.20
    base_z_center = 0.95

    profile = [
        (0.70, 0.26, 0),  # Base flange onto boiler
        (0.76, 0.23, 0),  # Lower neck step
        (0.95, 0.22, 0),  # Dome body
        (1.10, 0.20, 1),  # Brass top collar
        (1.15, 0.16, 1),  # Brass dome cap
        (1.18, 0.05, 1),  # Brass top valve tip
    ]

    rings = []
    for height, radius, mat_idx in profile:
        ring = []
        for j in range(segments):
            angle = 2 * math.pi * j / segments
            y = radius * math.sin(angle)
            z = height + base_z_center
            ring.append(bm.verts.new((base_x, y, z)))
        rings.append(ring)

    for r in range(len(profile) - 1):
        mat_idx = profile[r][2]
        for j in range(segments):
            n = (j + 1) % segments
            face = bm.faces.new((rings[r][j], rings[r][n], rings[r+1][n], rings[r+1][j]))
            face.material_index = mat_idx

    # Cap top vertex
    top_vert = bm.verts.new((base_x, 0, 1.20 + base_z_center))
    last_ring = rings[-1]
    for j in range(segments):
        n = (j + 1) % segments
        face = bm.faces.new((last_ring[j], last_ring[n], top_vert))
        face.material_index = 1

    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_boiler)
    mesh.materials.append(mat_brass)

    for poly in mesh.polygons:
        poly.use_smooth = True
    set_auto_smooth(obj, 30)

    # Shrinkwrap base modifier
    shrinkwrap = obj.modifiers.new(name="Shrinkwrap_Base", type='SHRINKWRAP')
    shrinkwrap.target = boiler_obj
    shrinkwrap.wrap_method = 'NEAREST_SURFACEPOINT'

    # Subsurf modifier
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.render_levels = 2
    subsurf.levels = 1

    return obj


def create_big_dome(boiler_obj, collection, mat_boiler, mat_brass):
    """
    Creates the main steam dome on top of the boiler with smooth hemispherical cap.
    """
    mesh = bpy.data.meshes.new("Big_Dome_Mesh")
    obj = bpy.data.objects.new("Big_Dome", mesh)
    collection.objects.link(obj)

    bm = bmesh.new()
    segments = 32
    base_x = -1.60
    base_z_center = 0.95

    profile = [
        (0.68, 0.38, 0),  # Base flange onto boiler cylinder
        (0.76, 0.34, 0),  # Stepped base ring
        (1.05, 0.34, 0),  # Cylindrical dome body
        (1.22, 0.30, 0),  # Dome shoulder curve start
        (1.32, 0.20, 0),  # Dome hemispherical curve
        (1.37, 0.08, 0),  # Near top cap
    ]

    rings = []
    for height, radius, mat_idx in profile:
        ring = []
        for j in range(segments):
            angle = 2 * math.pi * j / segments
            y = radius * math.sin(angle)
            z = height + base_z_center
            ring.append(bm.verts.new((base_x, y, z)))
        rings.append(ring)

    for r in range(len(profile) - 1):
        mat_idx = profile[r][2]
        for j in range(segments):
            n = (j + 1) % segments
            face = bm.faces.new((rings[r][j], rings[r][n], rings[r+1][n], rings[r+1][j]))
            face.material_index = mat_idx

    # Center apex vertex for dome top
    apex_vert = bm.verts.new((base_x, 0, 1.39 + base_z_center))
    last_ring = rings[-1]
    for j in range(segments):
        n = (j + 1) % segments
        face = bm.faces.new((last_ring[j], last_ring[n], apex_vert))
        face.material_index = 0

    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_boiler)
    mesh.materials.append(mat_brass)

    for poly in mesh.polygons:
        poly.use_smooth = True
    set_auto_smooth(obj, 30)

    # Shrinkwrap base modifier
    shrinkwrap = obj.modifiers.new(name="Shrinkwrap_Base", type='SHRINKWRAP')
    shrinkwrap.target = boiler_obj
    shrinkwrap.wrap_method = 'NEAREST_SURFACEPOINT'

    # Subsurf modifier
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.render_levels = 2
    subsurf.levels = 1

    return obj


def create_chassis_frame(collection, mat_steel):
    """
    Creates the main chassis frame running beneath the boiler along X.
    Uses Mirror modifier along Y and Bevel modifier for hard-surface detailing.
    """
    mesh = bpy.data.meshes.new("Chassis_Frame_Mesh")
    obj = bpy.data.objects.new("Chassis_Frame", mesh)
    collection.objects.link(obj)

    bm = bmesh.new()

    # Half-chassis beam on +Y side (X from -4.2 to 1.9, Y from 0.65 to 0.78, Z from -0.15 to 0.15)
    x1, x2 = -4.2, 1.9
    y1, y2 = 0.65, 0.78
    z1, z2 = -0.15, 0.15

    verts = [
        bm.verts.new((x1, y1, z1)), bm.verts.new((x2, y1, z1)),
        bm.verts.new((x2, y2, z1)), bm.verts.new((x1, y2, z1)),
        bm.verts.new((x1, y1, z2)), bm.verts.new((x2, y1, z2)),
        bm.verts.new((x2, y2, z2)), bm.verts.new((x1, y2, z2)),
    ]

    bm.faces.new((verts[0], verts[1], verts[2], verts[3]))
    bm.faces.new((verts[7], verts[6], verts[5], verts[4]))
    bm.faces.new((verts[1], verts[5], verts[6], verts[2]))
    bm.faces.new((verts[4], verts[0], verts[3], verts[7]))
    bm.faces.new((verts[0], verts[4], verts[5], verts[1]))
    f_outer = bm.faces.new((verts[3], verts[2], verts[6], verts[7]))

    # Inset the outer face to create recessed channel
    bmesh.ops.inset_individual(bm, faces=[f_outer], thickness=0.03, depth=-0.015)

    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_steel)
    set_auto_smooth(obj, 35)

    mirror = obj.modifiers.new(name="Mirror_Y", type='MIRROR')
    mirror.use_axis[0] = False
    mirror.use_axis[1] = True
    mirror.use_axis[2] = False

    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.012
    bevel.segments = 3
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(30)

    return obj


def create_buffer_beams(collection, mat_steel):
    """
    Creates front and rear structural buffer beam plates with matching beveling.
    """
    mesh = bpy.data.meshes.new("Buffer_Beams_Mesh")
    obj = bpy.data.objects.new("Buffer_Beams", mesh)
    collection.objects.link(obj)

    bm = bmesh.new()

    def add_beam_box(bm, x_min, x_max, y_min, y_max, z_min, z_max):
        v0 = bm.verts.new((x_min, y_min, z_min))
        v1 = bm.verts.new((x_max, y_min, z_min))
        v2 = bm.verts.new((x_max, y_max, z_min))
        v3 = bm.verts.new((x_min, y_max, z_min))
        v4 = bm.verts.new((x_min, y_min, z_max))
        v5 = bm.verts.new((x_max, y_min, z_max))
        v6 = bm.verts.new((x_max, y_max, z_max))
        v7 = bm.verts.new((x_min, y_max, z_max))

        bm.faces.new((v0, v1, v2, v3))
        bm.faces.new((v7, v6, v5, v4))
        bm.faces.new((v1, v5, v6, v2))
        bm.faces.new((v4, v0, v3, v7))
        bm.faces.new((v0, v4, v5, v1))
        bm.faces.new((v3, v2, v6, v7))

    # Front Buffer Beam
    add_beam_box(bm, 1.90, 1.98, -0.85, 0.85, -0.15, 0.40)
    # Rear Buffer Beam
    add_beam_box(bm, -4.28, -4.20, -0.85, 0.85, -0.15, 0.40)

    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_steel)
    set_auto_smooth(obj, 35)

    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.012
    bevel.segments = 3
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(30)

    return obj


def create_drivers_cab(collection, mat_boiler, mat_brass, mat_metal):
    """
    Creates the detailed driver's cab shell with front/rear end walls, circular porthole
    windows with brass bezel trim, curved roof profile with overhang, and boiler cutout alignment.
    Uses Mirror modifier along Y for symmetric topology.
    """
    mesh = bpy.data.meshes.new("Drivers_Cab_Mesh")
    obj = bpy.data.objects.new("Drivers_Cab", mesh)
    collection.objects.link(obj)

    bm = bmesh.new()

    # Coordinates for half-cab shell (+Y side)
    x_front = -2.30
    x_back = -4.10
    y_outer = 0.95
    y_overhang = 1.02
    z_bottom = 0.20
    z_eaves = 2.00
    z_apex = 2.25

    # 1. Outer Side Wall Panel (Y = y_outer, X from x_back to x_front, Z from z_bottom to z_eaves)
    v_s1 = bm.verts.new((x_back, y_outer, z_bottom))
    v_s2 = bm.verts.new((x_front, y_outer, z_bottom))
    v_s3 = bm.verts.new((x_front, y_outer, z_eaves))
    v_s4 = bm.verts.new((x_back, y_outer, z_eaves))
    bm.faces.new((v_s1, v_s2, v_s3, v_s4))

    # 2. Curved Roof Shell (+Y side, extending from center line Y=0 to y_overhang)
    r_front_center = bm.verts.new((x_front - 0.05, 0.0, z_apex))
    r_front_sh     = bm.verts.new((x_front - 0.05, 0.68, z_apex - 0.07))
    r_front_eaves  = bm.verts.new((x_front - 0.05, y_overhang, z_eaves))

    r_back_center  = bm.verts.new((x_back + 0.05, 0.0, z_apex))
    r_back_sh      = bm.verts.new((x_back + 0.05, 0.68, z_apex - 0.07))
    r_back_eaves   = bm.verts.new((x_back + 0.05, y_overhang, z_eaves))

    bm.faces.new((r_front_center, r_front_sh, r_back_sh, r_back_center))
    bm.faces.new((r_front_sh, r_front_eaves, r_back_eaves, r_back_sh))

    # Helper to build wall end panel with circular window cutout and clean quad topology around all 12 vertices
    def add_wall_with_circular_window(bm, x_pos, is_front=True):
        win_center_y = 0.48
        win_center_z = 1.55
        win_rad = 0.18
        outer_rad = 0.35
        win_segs = 12

        # Inner window circle verts
        win_verts = []
        for j in range(win_segs):
            angle = 2 * math.pi * j / win_segs
            wy = win_center_y + win_rad * math.sin(angle)
            wz = win_center_z + win_rad * math.cos(angle)
            win_verts.append(bm.verts.new((x_pos, wy, wz)))

        # Outer concentric circle ring verts
        outer_ring_verts = []
        for j in range(win_segs):
            angle = 2 * math.pi * j / win_segs
            oy = win_center_y + outer_rad * math.sin(angle)
            oz = win_center_z + outer_rad * math.cos(angle)
            outer_ring_verts.append(bm.verts.new((x_pos, oy, oz)))

        # Quad ring between inner window circle and outer ring (all 12 segments quad-connected)
        for j in range(win_segs):
            n = (j + 1) % win_segs
            if is_front:
                bm.faces.new((win_verts[j], win_verts[n], outer_ring_verts[n], outer_ring_verts[j]))
            else:
                bm.faces.new((win_verts[n], win_verts[j], outer_ring_verts[j], outer_ring_verts[n]))

        # Outer wall boundary verts
        v_bot_in  = bm.verts.new((x_pos, 0.0, z_bottom))
        v_bot_out = bm.verts.new((x_pos, y_outer, z_bottom))
        v_top_out = bm.verts.new((x_pos, y_outer, z_eaves))
        v_top_in  = bm.verts.new((x_pos, 0.0, z_apex))
        v_sh_in   = bm.verts.new((x_pos, 0.68, z_apex - 0.07))

        # Connect outer ring vertices to outer wall boundary corners
        # outer_ring_verts[0] = Top, [3] = Right (+Y), [6] = Bottom, [9] = Left (0)
        if is_front:
            bm.faces.new((v_bot_in, v_bot_out, outer_ring_verts[6], outer_ring_verts[9]))
            bm.faces.new((v_bot_out, v_top_out, outer_ring_verts[3], outer_ring_verts[6]))
            bm.faces.new((v_top_out, v_sh_in, outer_ring_verts[0], outer_ring_verts[3]))
            bm.faces.new((v_sh_in, v_top_in, outer_ring_verts[9], outer_ring_verts[0]))
        else:
            bm.faces.new((v_bot_in, outer_ring_verts[9], outer_ring_verts[6], v_bot_out))
            bm.faces.new((v_bot_out, outer_ring_verts[6], outer_ring_verts[3], v_top_out))
            bm.faces.new((v_top_out, outer_ring_verts[3], outer_ring_verts[0], v_sh_in))
            bm.faces.new((v_sh_in, outer_ring_verts[0], outer_ring_verts[9], v_top_in))

    # 3. Front Wall Panel with Circular Porthole Cutout
    add_wall_with_circular_window(bm, x_front, is_front=True)

    # 4. Rear Wall Panel with Circular Porthole Cutout
    add_wall_with_circular_window(bm, x_back, is_front=False)

    bm.to_mesh(mesh)
    bm.free()

    # Assign materials
    mesh.materials.append(mat_boiler)
    mesh.materials.append(mat_metal)
    mesh.materials.append(mat_brass)

    for poly in mesh.polygons:
        poly.use_smooth = True
    set_auto_smooth(obj, 35)

    # Add Mirror modifier along Y axis with clipping enabled
    mirror = obj.modifiers.new(name="Mirror_Y", type='MIRROR')
    mirror.use_axis[0] = False
    mirror.use_axis[1] = True
    mirror.use_axis[2] = False
    mirror.use_clip = True

    # Add Solidify modifier to give realistic sheet metal thickness
    solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = 0.025
    solidify.offset = -1.0

    # Add Subdivision Surface modifier
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.render_levels = 2
    subsurf.levels = 1

    # Add Brass Porthole Window Bezels (Front & Rear) directly via native BMesh geometry
    win_center_y = 0.48
    win_center_z = 1.55
    win_rad = 0.18
    bezel_r = 0.018
    major_segs = 16
    minor_segs = 8

    for win_x in [x_front + 0.01, x_back - 0.01]:
        for side_sign in [1, -1]:
            bezel_mesh = bpy.data.meshes.new("Window_Bezel_Mesh")
            bezel_obj = bpy.data.objects.new(
                f"Window_Bezel_{'Front' if win_x > -3.0 else 'Rear'}_{'R' if side_sign > 0 else 'L'}",
                bezel_mesh
            )
            collection.objects.link(bezel_obj)

            bm_b = bmesh.new()
            center_y = side_sign * win_center_y

            torus_rings = []
            for i in range(major_segs):
                major_angle = 2 * math.pi * i / major_segs
                ring_y = center_y + win_rad * math.sin(major_angle)
                ring_z = win_center_z + win_rad * math.cos(major_angle)

                ring_verts = []
                for j in range(minor_segs):
                    minor_angle = 2 * math.pi * j / minor_segs
                    dx = bezel_r * math.cos(minor_angle)
                    r_off = bezel_r * math.sin(minor_angle)

                    vx = win_x + dx
                    vy = ring_y + r_off * math.sin(major_angle)
                    vz = ring_z + r_off * math.cos(major_angle)
                    ring_verts.append(bm_b.verts.new((vx, vy, vz)))
                torus_rings.append(ring_verts)

            for i in range(major_segs):
                n_i = (i + 1) % major_segs
                for j in range(minor_segs):
                    n_j = (j + 1) % minor_segs
                    v1 = torus_rings[i][j]
                    v2 = torus_rings[n_i][j]
                    v3 = torus_rings[n_i][n_j]
                    v4 = torus_rings[i][n_j]
                    bm_b.faces.new((v1, v2, v3, v4))

            bm_b.to_mesh(bezel_mesh)
            bm_b.free()

            bezel_mesh.materials.append(mat_brass)
            for poly in bezel_mesh.polygons:
                poly.use_smooth = True
            set_auto_smooth(bezel_obj, 30)
            bezel_obj.parent = obj

    return obj


def create_side_plates(collection, mat_metal):
    """
    Creates the boiler lower side plates, running boards, and front buffer beam mounts.
    Uses Mirror modifier along Y axis for symmetric modeling.
    """
    mesh = bpy.data.meshes.new("Boiler_Side_Plates_Mesh")
    obj = bpy.data.objects.new("Boiler_Side_Plates", mesh)
    collection.objects.link(obj)

    bm = bmesh.new()

    # Right side plate panel geometry (Y > 0)
    # Extends from X = -2.7 to 1.85, Y around 0.78 to 0.85, Z around 0.1 to 0.75
    y_pos = 0.80
    thick = 0.03

    # Front buffer extension apron (X=1.85, Y from 0 to 0.82, Z=0.15)
    # Side apron plate verts
    v1 = bm.verts.new((-2.70, y_pos, 0.20))
    v2 = bm.verts.new((1.85, y_pos, 0.20))
    v3 = bm.verts.new((1.85, y_pos, 0.75))
    v4 = bm.verts.new((-2.70, y_pos, 0.75))

    # Extrude thickness (outward in Y)
    v1_out = bm.verts.new((-2.70, y_pos + thick, 0.20))
    v2_out = bm.verts.new((1.85, y_pos + thick, 0.20))
    v3_out = bm.verts.new((1.85, y_pos + thick, 0.75))
    v4_out = bm.verts.new((-2.70, y_pos + thick, 0.75))

    # Outer side face
    bm.faces.new((v1_out, v2_out, v3_out, v4_out))
    # Inner side face
    bm.faces.new((v4, v3, v2, v1))
    # Top face
    bm.faces.new((v4_out, v3_out, v3, v4))
    # Bottom face
    bm.faces.new((v1, v2, v2_out, v1_out))
    # Front face
    bm.faces.new((v2, v3, v3_out, v2_out))
    # Back face
    bm.faces.new((v1_out, v4_out, v4, v1))

    # Front Buffer Beam cross plate (connects to center line)
    v_buf1 = bm.verts.new((1.85, 0.0, -0.05))
    v_buf2 = bm.verts.new((1.85, y_pos + thick, -0.05))
    v_buf3 = bm.verts.new((1.85, y_pos + thick, 0.35))
    v_buf4 = bm.verts.new((1.85, 0.0, 0.35))

    v_buf1_b = bm.verts.new((1.81, 0.0, -0.05))
    v_buf2_b = bm.verts.new((1.81, y_pos + thick, -0.05))
    v_buf3_b = bm.verts.new((1.81, y_pos + thick, 0.35))
    v_buf4_b = bm.verts.new((1.81, 0.0, 0.35))

    bm.faces.new((v_buf1, v_buf2, v_buf3, v_buf4))
    bm.faces.new((v_buf4_b, v_buf3_b, v_buf2_b, v_buf1_b))
    bm.faces.new((v_buf1_b, v_buf2_b, v_buf2, v_buf1))
    bm.faces.new((v_buf4, v_buf3, v_buf3_b, v_buf4_b))
    bm.faces.new((v_buf2_b, v_buf3_b, v_buf3, v_buf2))
    bm.faces.new((v_buf4_b, v_buf1_b, v_buf1, v_buf4))

    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_metal)

    for poly in mesh.polygons:
        poly.use_smooth = False
    set_auto_smooth(obj, 35)

    # Add Mirror modifier along Y axis
    mirror = obj.modifiers.new(name="Mirror_Y", type='MIRROR')
    mirror.use_axis[0] = False
    mirror.use_axis[1] = True
    mirror.use_axis[2] = False
    mirror.use_bisect_axis[1] = False
    mirror.use_clip = True

    return obj


def create_lighting_and_camera(collection):
    """Creates a 3-point studio lighting setup and positions 50mm camera to frame full locomotive."""
    # Key Light (Top-Front-Right)
    key_data = bpy.data.lights.new(name="Key_Light_Data", type='AREA')
    key_data.energy = 1200
    key_data.size = 4.0
    key_data.color = (1.0, 0.95, 0.9)  # Soft warm key
    key_obj = bpy.data.objects.new("Key_Light", key_data)
    key_obj.location = (5.5, -5.5, 5.0)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(-40))
    collection.objects.link(key_obj)

    # Fill Light (Front-Left)
    fill_data = bpy.data.lights.new(name="Fill_Light_Data", type='AREA')
    fill_data.energy = 550
    fill_data.size = 5.0
    fill_data.color = (0.85, 0.9, 1.0)  # Soft cool fill
    fill_obj = bpy.data.objects.new("Fill_Light", fill_data)
    fill_obj.location = (4.5, 5.5, 3.5)
    fill_obj.rotation_euler = (math.radians(55), math.radians(-15), math.radians(130))
    collection.objects.link(fill_obj)

    # Rim / Back Light (Top-Back)
    rim_data = bpy.data.lights.new(name="Rim_Light_Data", type='AREA')
    rim_data.energy = 900
    rim_data.size = 3.0
    rim_data.color = (1.0, 1.0, 1.0)  # Crisp white rim edge light
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = (-6.5, 4.0, 4.5)
    rim_obj.rotation_euler = (math.radians(115), math.radians(10), math.radians(-50))
    collection.objects.link(rim_obj)

    # Camera setup (3/4 perspective angle view framing full ~6m length locomotive)
    cam_data = bpy.data.cameras.new(name="Locomotive_Camera_Data")
    cam_data.lens = 50
    cam_obj = bpy.data.objects.new("Locomotive_Camera", cam_data)
    cam_obj.location = (6.8, -6.5, 3.2)
    cam_obj.rotation_euler = (math.radians(72), 0, math.radians(44))
    collection.objects.link(cam_obj)

    bpy.context.scene.camera = cam_obj


def generate_steam_train_boiler():
    """Main execution function to construct the full train boiler & cab scene."""
    clean_existing_scene()

    # Collection Setup
    boiler_collection = get_or_create_collection("SteamTrain_Boiler")

    # PBR Materials Setup
    mat_boiler = create_pbr_material(
        name="PBR_Boiler_DarkPaintedMetal",
        color=(0.04, 0.05, 0.07, 1.0),
        metallic=0.85,
        roughness=0.32,
        clearcoat=0.2
    )

    mat_metal = create_pbr_material(
        name="PBR_Structural_RawSteel",
        color=(0.025, 0.025, 0.03, 1.0),
        metallic=0.92,
        roughness=0.55
    )

    mat_brass = create_pbr_material(
        name="PBR_Brass_Details",
        color=(0.85, 0.62, 0.22, 1.0),
        metallic=1.0,
        roughness=0.22
    )

    # Build Geometry
    chassis = create_chassis_frame(boiler_collection, mat_metal)
    buffer_beams = create_buffer_beams(boiler_collection, mat_metal)
    boiler_main = create_boiler_main(boiler_collection, mat_boiler, mat_metal)
    smokebox_door = create_smokebox_front(boiler_collection, mat_boiler, mat_brass)
    chimney = create_chimney(boiler_main, boiler_collection, mat_boiler, mat_brass)
    small_dome = create_small_dome(boiler_main, boiler_collection, mat_boiler, mat_brass)
    big_dome = create_big_dome(boiler_main, boiler_collection, mat_boiler, mat_brass)
    side_plates = create_side_plates(boiler_collection, mat_metal)
    drivers_cab = create_drivers_cab(boiler_collection, mat_boiler, mat_brass, mat_metal)

    # Build Lighting & Camera
    create_lighting_and_camera(boiler_collection)

    print("Successfully generated Steam Train Boiler model in collection 'SteamTrain_Boiler'.")


if __name__ == "__main__":
    generate_steam_train_boiler()
