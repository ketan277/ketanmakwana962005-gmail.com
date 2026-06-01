import bpy
import math
import random

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_valley():
    # Green rolling hills
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
    ground = bpy.context.object

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=40)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Displacement for hills
    tex = bpy.data.textures.new("HillTex", type='CLOUDS')
    tex.noise_scale = 10.0
    mod = ground.modifiers.new(name="Hills", type='DISPLACE')
    mod.texture = tex
    mod.strength = 10.0

    grass_mat = bpy.data.materials.new(name="Lush_Grass")
    grass_mat.use_nodes = True
    grass_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.4, 0.05, 1)
    ground.data.materials.append(grass_mat)

def create_streams():
    # Mossy rocks and streams
    for i in range(5):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(random_coord(), random_coord(), 0.5))
        rock = bpy.context.object
        rock.scale[2] = 0.5

        moss_mat = bpy.data.materials.new(name="Mossy_Rock")
        moss_mat.use_nodes = True
        moss_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.1, 0.02, 1)
        rock.data.materials.append(moss_mat)

def random_coord():
    return random.uniform(-20, 20)

def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
    sun = bpy.context.object
    sun.data.energy = 10.0

    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    nodes["Background"].inputs[0].default_value = (0.5, 0.8, 1.0, 1) # Bright Sky

def setup_camera():
    bpy.ops.object.camera_add(location=(50, -50, 30), rotation=(math.radians(60), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_valley()
    create_streams()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
