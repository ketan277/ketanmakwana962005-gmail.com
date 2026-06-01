import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_island():
    # Ocean plane
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
    ocean = bpy.context.object
    ocean.name = "Ocean"

    # Island (Subdivided plane)
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0.1))
    island = bpy.context.object
    island.name = "Forgotten_Island"

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=20)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Blue/Dark Green Sand Material
    mat = bpy.data.materials.new(name="Blue_Sand")
    mat.use_nodes = True
    # "Exactly the color of the ocean" - Deep blue-green
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.01, 0.1, 0.15, 1)
    island.data.materials.append(mat)

def create_hut():
    # Simple hut with thatched roof
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1.5))
    hut = bpy.context.object
    hut.scale = (2, 2, 1.5)

    # Roof (Cone)
    bpy.ops.mesh.primitive_cone_add(radius=2.5, depth=2, location=(0, 0, 4))
    roof = bpy.context.object

    # Materials
    wood_mat = bpy.data.materials.new(name="Hut_Wood")
    wood_mat.use_nodes = True
    wood_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.05, 0.02, 1)
    hut.data.materials.append(wood_mat)

    thatch_mat = bpy.data.materials.new(name="Thatch")
    thatch_mat.use_nodes = True
    thatch_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.15, 0.05, 1)
    roof.data.materials.append(thatch_mat)

def create_cave_entrance():
    # Dark brown stones forming an entrance
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(6, 0, 0.5), rotation=(0, math.radians(90), 0), major_radius=2, minor_radius=0.5)
    cave = bpy.context.object
    cave.name = "Cave_Entrance"
    cave.scale[0] = 0.5

    stone_mat = bpy.data.materials.new(name="Cave_Stone")
    stone_mat.use_nodes = True
    stone_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.03, 0.02, 1)
    cave.data.materials.append(stone_mat)

def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 20))
    sun = bpy.context.object
    sun.data.energy = 8.0

    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    nodes["Background"].inputs[0].default_value = (0.3, 0.6, 1.0, 1) # Bright Sky

def setup_camera():
    bpy.ops.object.camera_add(location=(15, -15, 10), rotation=(math.radians(65), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_island()
    create_hut()
    create_cave_entrance()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
