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
    """Creates a 3-point studio lighting setup and positions camera for preview."""
    # Key Light (Top-Front-Right)
    key_data = bpy.data.lights.new(name="Key_Light_Data", type='AREA')
    key_data.energy = 800
    key_data.size = 2.5
    key_data.color = (1.0, 0.95, 0.9)  # Soft warm key
    key_obj = bpy.data.objects.new("Key_Light", key_data)
    key_obj.location = (4.0, -3.5, 4.0)
    key_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))
    collection.objects.link(key_obj)

    # Fill Light (Front-Left)
    fill_data = bpy.data.lights.new(name="Fill_Light_Data", type='AREA')
    fill_data.energy = 350
    fill_data.size = 3.5
    fill_data.color = (0.85, 0.9, 1.0)  # Soft cool fill
    fill_obj = bpy.data.objects.new("Fill_Light", fill_data)
    fill_obj.location = (3.5, 4.0, 2.5)
    fill_obj.rotation_euler = (math.radians(60), math.radians(-15), math.radians(135))
    collection.objects.link(fill_obj)

    # Rim / Back Light (Top-Back)
    rim_data = bpy.data.lights.new(name="Rim_Light_Data", type='AREA')
    rim_data.energy = 600
    rim_data.size = 2.0
    rim_data.color = (1.0, 1.0, 1.0)  # Crisp white rim edge light
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = (-4.0, 2.5, 3.5)
    rim_obj.rotation_euler = (math.radians(120), math.radians(10), math.radians(-45))
    collection.objects.link(rim_obj)

    # Camera setup (3/4 perspective angle view)
    cam_data = bpy.data.cameras.new(name="Boiler_Camera_Data")
    cam_data.lens = 50
    cam_obj = bpy.data.objects.new("Boiler_Camera", cam_data)
    cam_obj.location = (4.8, -4.2, 2.4)
    cam_obj.rotation_euler = (math.radians(68), 0, math.radians(48))
    collection.objects.link(cam_obj)

    bpy.context.scene.camera = cam_obj


def generate_steam_train_boiler():
    """Main execution function to construct the full train boiler scene."""
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
    boiler_main = create_boiler_main(boiler_collection, mat_boiler, mat_metal)
    smokebox_door = create_smokebox_front(boiler_collection, mat_boiler, mat_brass)
    chimney = create_chimney(boiler_main, boiler_collection, mat_boiler, mat_brass)
    small_dome = create_small_dome(boiler_main, boiler_collection, mat_boiler, mat_brass)
    big_dome = create_big_dome(boiler_main, boiler_collection, mat_boiler, mat_brass)
    side_plates = create_side_plates(boiler_collection, mat_metal)

    # Build Lighting & Camera
    create_lighting_and_camera(boiler_collection)

    print("Successfully generated Steam Train Boiler model in collection 'SteamTrain_Boiler'.")


if __name__ == "__main__":
    generate_steam_train_boiler()
