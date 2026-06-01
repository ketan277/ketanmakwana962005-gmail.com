import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_dome():
    # Silver dome
    bpy.ops.mesh.primitive_uv_sphere_add(radius=10, location=(0, 0, 0))
    dome = bpy.context.object
    dome.name = "Observatory_Dome"
    dome.scale[2] = 0.8

    # Silver Mat
    mat = bpy.data.materials.new(name="Silver_Metal")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0.8, 0.8, 0.8, 1)
    bsdf.inputs[4].default_value = 1.0 # Metallic
    bsdf.inputs[7].default_value = 0.2
    dome.data.materials.append(mat)

    # Hole at the top
    # (Visualized as an empty space or a black circle)
    bpy.ops.mesh.primitive_circle_add(radius=2, location=(0, 0, 8), fill_type='NGON')
    hole = bpy.context.object
    hole_mat = bpy.data.materials.new(name="Hole")
    hole_mat.use_nodes = True
    hole_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0, 0, 0, 1)
    hole.data.materials.append(hole_mat)

def create_telescope():
    # Large wooden tube
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=15, location=(0, 0, 4))
    tube = bpy.context.object
    tube.rotation_euler[0] = math.radians(-45)

    wood_mat = bpy.data.materials.new(name="Telescope_Wood")
    wood_mat.use_nodes = True
    wood_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.05, 0.02, 1)
    tube.data.materials.append(wood_mat)

    # Eyepiece
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1, location=(0, -5, 0.5))
    eye = bpy.context.object
    eye.rotation_euler[0] = math.radians(-45)
    eye.data.materials.append(wood_mat)

def create_lake_and_wall():
    # Stone wall circle
    bpy.ops.mesh.primitive_torus_add(major_radius=15, minor_radius=1, location=(0, 0, 0))
    wall = bpy.context.object

    # Water surrounding
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0.5))
    water = bpy.context.object
    water.name = "Lake_Water"

    water_mat = bpy.data.materials.new(name="Lake_Material")
    water_mat.use_nodes = True
    bsdf = water_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0.05, 0.1, 0.2, 1)
    bsdf.inputs[17].default_value = 1.0
    water.data.materials.append(water_mat)

def setup_lighting():
    # Starry night light
    bpy.ops.object.light_add(type='POINT', location=(20, 20, 20))
    light = bpy.context.object
    light.data.energy = 2000.0
    light.data.color = (0.8, 0.9, 1.0)

    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    nodes["Background"].inputs[0].default_value = (0.005, 0.005, 0.01, 1)

def setup_camera():
    bpy.ops.object.camera_add(location=(35, -35, 20), rotation=(math.radians(60), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_dome()
    create_telescope()
    create_lake_and_wall()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
