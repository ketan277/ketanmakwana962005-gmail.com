import bpy
import math
import random

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_sky():
    # Use a Sun light for cinematic jungle rays
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
    sun = bpy.context.object
    sun.data.energy = 5.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(135))

    # World background for a slightly "sinister red" mood
    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    nodes["Background"].inputs[0].default_value = (0.02, 0.005, 0.005, 1) # Deep dark red-black

def create_jungle_ground():
    # Ground plane
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = "Jungle_Ground"

    # Material
    mat = bpy.data.materials.new(name="Mud_Ground")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.02, 0.01, 1) # Dark brown mud
    ground.data.materials.append(mat)

def create_trees(num_trees=15):
    for i in range(num_trees):
        x = random.uniform(-8, 8)
        y = random.uniform(-8, 8)
        height = random.uniform(5, 10)

        # Trunk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=height, location=(x, y, height/2))
        trunk = bpy.context.object

        # Leaves (using metaballs or simple spheres for "thick" look)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=2, location=(x, y, height))
        leaves = bpy.context.object
        leaves.scale[2] = 0.5 # Flattened canopy

        # Material - Sinister Red for leaves
        leaf_mat = bpy.data.materials.new(name="Sinister_Red_Leaves")
        leaf_mat.use_nodes = True
        # Ti plants shaded the forest red
        leaf_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.01, 0.01, 1)
        leaves.data.materials.append(leaf_mat)

def create_rock_pond():
    # Simple pond representation
    bpy.ops.mesh.primitive_circle_add(radius=3, fill_type='NGON', location=(0, 0, 0.01))
    pond = bpy.context.object
    pond.name = "Rock_Pond"

    water_mat = bpy.data.materials.new(name="Pond_Water")
    water_mat.use_nodes = True
    bsdf = water_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0.01, 0.05, 0.05, 1) # Dark water
    bsdf.inputs[7].default_value = 0.0 # Roughness
    bsdf.inputs[15].default_value = 1.33 # IOR
    bsdf.inputs[17].default_value = 1.0 # Transmission
    pond.data.materials.append(water_mat)

def setup_camera():
    bpy.ops.object.camera_add(location=(12, -12, 5), rotation=(math.radians(75), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_sky()
    create_jungle_ground()
    create_trees()
    create_rock_pond()
    setup_camera()

    # Set to Cycles for cinematic look
    bpy.context.scene.render.engine = 'CYCLES'
    if bpy.context.preferences.addons.get('cycles'):
        bpy.context.scene.cycles.device = 'GPU' # Attempt GPU

if __name__ == "__main__":
    main()
