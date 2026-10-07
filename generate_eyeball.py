import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Clear unused materials and meshes
for m in bpy.data.materials:
    bpy.data.materials.remove(m)
for m in bpy.data.meshes:
    bpy.data.meshes.remove(m)

# Set Render Engine to EEVEE
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(scene.eevee, "use_raytracing") else 'BLENDER_EEVEE'

# EEVEE properties for Blender 4.0 / 4.2 compatibility
if hasattr(scene.eevee, "use_gtao"):
    scene.eevee.use_gtao = True
if hasattr(scene.eevee, "use_bloom"):
    scene.eevee.use_bloom = True
if hasattr(scene.eevee, "use_ssr"):
    scene.eevee.use_ssr = True
    scene.eevee.use_ssr_refraction = True

# 1. CREATE INNER SPHERE (Eyeball & Lens/Pupil)
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1.0, location=(0, 0, 0))
inner_sphere = bpy.context.active_object
inner_sphere.name = "Inner_Eyeball"

# Rotate 90 degrees on Y axis so pole faces +X direction
inner_sphere.rotation_euler[1] = math.radians(90)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Edit mode: Push front faces back to create lens/pupil concavity & bevel edge
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(inner_sphere.data)
bm.verts.ensure_lookup_table()

# Identify front pole vertices (X > 0.85)
front_verts = [v for v in bm.verts if v.co.x > 0.85]
for v in front_verts:
    # Push back along X axis
    v.co.x -= 0.18

bmesh.update_edit_mesh(inner_sphere.data)

# Bevel the rim edges around the lens
bm.edges.ensure_lookup_table()
rim_edges = [e for e in bm.edges if any(v.co.x > 0.65 and v.co.x < 0.82 for v in e.verts)]
if rim_edges:
    bmesh.ops.bevel(bm, geom=rim_edges, offset=0.04, segments=4, profile=0.5)

bmesh.update_edit_mesh(inner_sphere.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Shade Auto Smooth
bpy.ops.object.shade_smooth()

# 2. CREATE OUTER SPHERE (Cornea)
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1.02, location=(0, 0, 0))
outer_sphere = bpy.context.active_object
outer_sphere.name = "Outer_Cornea"

outer_sphere.rotation_euler[1] = math.radians(90)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Edit mode: Bulge front cornea faces outward
bpy.ops.object.mode_set(mode='EDIT')
bm_out = bmesh.from_edit_mesh(outer_sphere.data)
bm_out.verts.ensure_lookup_table()

for v in bm_out.verts:
    if v.co.x > 0.7:
        # Smooth outward bulge along X
        factor = (v.co.x - 0.7) / 0.32
        v.co.x += factor * 0.15

bmesh.update_edit_mesh(outer_sphere.data)
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.shade_smooth()

# 3. OUTER MATERIAL (Cornea Glass)
mat_cornea = bpy.data.materials.new(name="Cornea_Glass")
mat_cornea.use_nodes = True
nodes_c = mat_cornea.node_tree.nodes
links_c = mat_cornea.node_tree.links

bsdf_c = nodes_c.get("Principled BSDF")
if bsdf_c:
    # Glass settings
    if "Transmission Weight" in bsdf_c.inputs:
        bsdf_c.inputs["Transmission Weight"].default_value = 1.0
    elif "Transmission" in bsdf_c.inputs:
        bsdf_c.inputs["Transmission"].default_value = 1.0
    bsdf_c.inputs["Roughness"].default_value = 0.0
    bsdf_c.inputs["IOR"].default_value = 1.376

if hasattr(mat_cornea, "use_screen_refraction"):
    mat_cornea.use_screen_refraction = True
if hasattr(mat_cornea, "blend_method"):
    mat_cornea.blend_method = 'BLEND'

outer_sphere.data.materials.append(mat_cornea)

# 4. INNER MATERIAL (Procedural Iris & Sclera)
mat_iris = bpy.data.materials.new(name="Procedural_Iris")
mat_iris.use_nodes = True
nodes_i = mat_iris.node_tree.nodes
links_i = mat_iris.node_tree.links
nodes_i.clear()

# Create Shader Nodes according to Video Tutorial
# Group 1: Base Radial Color (Sclera, Iris, Pupil)
node_tex_coord1 = nodes_i.new('ShaderNodeTexCoord')
node_mapping1 = nodes_i.new('ShaderNodeMapping')
node_gradient = nodes_i.new('ShaderNodeTexGradient')
node_color_ramp1 = nodes_i.new('ShaderNodeValToRGB')

node_gradient.gradient_type = 'SPHERICAL'

# Shift Z location to 0.6 so spherical gradient centers on front pupil region
node_mapping1.inputs['Location'].default_value[0] = -0.6

# Connect Group 1
links_i.new(node_tex_coord1.outputs['Object'], node_mapping1.inputs['Vector'])
links_i.new(node_mapping1.outputs['Vector'], node_gradient.inputs['Vector'])
links_i.new(node_gradient.outputs['Color'], node_color_ramp1.inputs['Fac'])

# Color Ramp 1 configuration (Sclera -> Limbal Ring -> Iris -> Pupil)
cr1 = node_color_ramp1.color_ramp
cr1.interpolation = 'B_SPLINE'

# Position 0: Sclera (White)
cr1.elements[0].position = 0.0
cr1.elements[0].color = (0.92, 0.92, 0.94, 1.0)

# Position 1: Limbal Ring (Dark Outer Border)
cr1.elements[1].position = 0.35
cr1.elements[1].color = (0.01, 0.03, 0.08, 1.0)

# Element 2: Iris Primary Color (Vibrant Blue/Cyan)
e2 = cr1.elements.new(0.42)
e2.color = (0.05, 0.40, 0.85, 1.0)

# Element 3: Inner Iris Detail (Gold / Hazel accent)
e3 = cr1.elements.new(0.52)
e3.color = (0.75, 0.50, 0.10, 1.0)

# Element 4: Pupil (Black)
e4 = cr1.elements.new(0.58)
e4.color = (0.0, 0.0, 0.0, 1.0)


# Group 2: Voronoi Radial Striations
node_tex_coord2 = nodes_i.new('ShaderNodeTexCoord')
node_mapping2 = nodes_i.new('ShaderNodeMapping')
node_voronoi = nodes_i.new('ShaderNodeTexVoronoi')
node_color_ramp2 = nodes_i.new('ShaderNodeValToRGB')

node_mapping2.vector_type = 'NORMAL'
node_mapping2.inputs['Scale'].default_value[1] = 0.0 # Y scale = 0 for radial striations
node_voronoi.inputs['Scale'].default_value = 35.0

links_i.new(node_tex_coord2.outputs['Object'], node_mapping2.inputs['Vector'])
links_i.new(node_mapping2.outputs['Vector'], node_voronoi.inputs['Vector'])
links_i.new(node_voronoi.outputs['Color'], node_color_ramp2.inputs['Fac'])

cr2 = node_color_ramp2.color_ramp
cr2.elements[0].position = 0.2
cr2.elements[0].color = (0.1, 0.1, 0.1, 1.0)
cr2.elements[1].position = 0.8
cr2.elements[1].color = (0.9, 0.9, 0.9, 1.0)


# Mix Node 1 (Overlay Group 1 & Group 2)
mix1 = nodes_i.new('ShaderNodeMix')
mix1.data_type = 'RGBA'
mix1.blend_type = 'OVERLAY'
mix1.inputs['Factor'].default_value = 0.65

links_i.new(node_color_ramp1.outputs['Color'], mix1.inputs[6]) # A
links_i.new(node_color_ramp2.outputs['Color'], mix1.inputs[7]) # B


# Group 3: Noise Texture for organic depth
node_noise = nodes_i.new('ShaderNodeTexNoise')
node_noise.inputs['Scale'].default_value = 45.0
node_noise.inputs['Detail'].default_value = 5.0

node_color_ramp3 = nodes_i.new('ShaderNodeValToRGB')
links_i.new(node_noise.outputs['Color'], node_color_ramp3.inputs['Fac'])

# Mix Node 2
mix2 = nodes_i.new('ShaderNodeMix')
mix2.data_type = 'RGBA'
mix2.blend_type = 'OVERLAY'
mix2.inputs['Factor'].default_value = 0.35

links_i.new(mix1.outputs[2], mix2.inputs[6]) # A from Mix1
links_i.new(node_color_ramp3.outputs['Color'], mix2.inputs[7]) # B from Noise Ramp


# Principled BSDF & Output
bsdf_i = nodes_i.new('ShaderNodeBsdfPrincipled')
bsdf_i.inputs['Roughness'].default_value = 0.05 # Slimy wet surface

node_bump = nodes_i.new('ShaderNodeBump')
node_bump.inputs['Strength'].default_value = 0.08
node_bump.inputs['Distance'].default_value = 0.03

links_i.new(mix2.outputs[2], bsdf_i.inputs['Base Color'])
links_i.new(mix2.outputs[2], node_bump.inputs['Height'])
links_i.new(node_bump.outputs['Normal'], bsdf_i.inputs['Normal'])

node_output = nodes_i.new('ShaderNodeOutputMaterial')
links_i.new(bsdf_i.outputs['BSDF'], node_output.inputs['Surface'])

inner_sphere.data.materials.append(mat_iris)


# 5. CAMERA & LIGHTING SETUP
cam_data = bpy.data.cameras.new(name="Camera")
cam_data.lens = 85 # Portrait lens for nice perspective
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Position camera in front of the eyeball facing the iris (+X side)
cam_obj.location = (2.6, -1.2, 0.7)

# Constraint camera to look at center of front pupil (0.8, 0, 0)
track = cam_obj.constraints.new(type='TRACK_TO')
track.target = inner_sphere
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# Studio Lights
# Key Light
key_light_data = bpy.data.lights.new(name="KeyLight", type='AREA')
key_light_data.energy = 250
key_light_data.size = 2.0
key_light_obj = bpy.data.objects.new("KeyLight", key_light_data)
key_light_obj.location = (3.0, -2.5, 2.5)
key_light_obj.rotation_euler = (math.radians(45), math.radians(30), math.radians(-30))
bpy.context.collection.objects.link(key_light_obj)

# Fill Light
fill_light_data = bpy.data.lights.new(name="FillLight", type='AREA')
fill_light_data.energy = 80
fill_light_data.size = 3.0
fill_light_obj = bpy.data.objects.new("FillLight", fill_light_data)
fill_light_obj.location = (2.0, 3.0, -1.0)
bpy.context.collection.objects.link(fill_light_obj)

# World Background Setup
world = bpy.data.worlds.new(name="StudioWorld")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.04, 0.05, 0.07, 1.0)
    bg_node.inputs['Strength'].default_value = 0.8

# Render Settings
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.filepath = "/app/eyeball_render.png"

# Save Blend File
bpy.ops.wm.save_as_mainfile(filepath="/app/eyeball.blend")

# Render Frame
bpy.ops.render.render(write_still=True)
print("SUCCESS: Eyeball generated and rendered.")
