import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_cave_interior():
    # Large sphere with inverted normals to act as cave walls
    bpy.ops.mesh.primitive_uv_sphere_add(radius=15, location=(0, 0, 0))
    cave = bpy.context.object
    cave.name = "Cave_Interior"

    # Flip normals (approximate with scale)
    cave.scale = (-1, -1, -1)

    # Red Stone Material
    mat = bpy.data.materials.new(name="Red_Cave_Stone")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.02, 0.02, 1)
    cave.data.materials.append(mat)

def create_chest():
    # Wooden chest in the center
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
    chest = bpy.context.object
    chest.scale = (1.2, 0.8, 0.7)

    # Wood Mat
    wood_mat = bpy.data.materials.new(name="Chest_Wood")
    wood_mat.use_nodes = True
    wood_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.02, 0.01, 1)
    chest.data.materials.append(wood_mat)

    # Gold Trim (Secondary object)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
    trim = bpy.context.object
    trim.scale = (1.22, 0.82, 0.1) # Lid trim
    trim.location[2] = 1.7

    gold_mat = bpy.data.materials.new(name="Gold_Trim")
    gold_mat.use_nodes = True
    bsdf = gold_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (1.0, 0.8, 0.1, 1)
    bsdf.inputs[4].default_value = 1.0 # Metallic
    bsdf.inputs[7].default_value = 0.1 # Shiny
    trim.data.materials.append(gold_mat)

def create_torch_light():
    # Sconce / Torch representation
    bpy.ops.object.light_add(type='POINT', location=(5, 5, 5))
    torch = bpy.context.object
    torch.data.energy = 500.0
    torch.data.color = (1.0, 0.5, 0.1) # Fire orange

    # Shadows dancing
    torch.data.shadow_soft_size = 0.5

def setup_camera():
    bpy.ops.object.camera_add(location=(6, -6, 4), rotation=(math.radians(60), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_cave_interior()
    create_chest()
    create_torch_light()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
