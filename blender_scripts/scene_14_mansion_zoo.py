import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_mansion_hall():
    # Large hallway
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 10))
    hall = bpy.context.object
    hall.scale = (5, 20, 10)
    hall.scale = (-1, -1, -1) # Invert

    wall_mat = bpy.data.materials.new(name="Mahogany")
    wall_mat.use_nodes = True
    wall_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.01, 0.005, 1)
    hall.data.materials.append(wall_mat)

def create_pens():
    # Habitat cages/pens along the hall
    for i in range(4):
        y = i * 8 - 12
        bpy.ops.mesh.primitive_cube_add(location=(3, y, 2.5))
        pen = bpy.context.object
        pen.scale = (1.5, 3, 2.5)

        glass_mat = bpy.data.materials.new(name="Pen_Glass")
        glass_mat.use_nodes = True
        bsdf = glass_mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs[0].default_value = (0.8, 0.9, 1.0, 1)
        bsdf.inputs[17].default_value = 1.0
        bsdf.inputs[7].default_value = 0.05
        pen.data.materials.append(glass_mat)

def setup_lighting():
    # Grand chandelier lighting
    for i in range(3):
        bpy.ops.object.light_add(type='POINT', location=(0, i * 10 - 10, 8))
        light = bpy.context.object
        light.data.energy = 1000.0
        light.data.color = (1.0, 0.9, 0.7)

def setup_camera():
    bpy.ops.object.camera_add(location=(0, -18, 5), rotation=(math.radians(85), 0, 0))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_mansion_hall()
    create_pens()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
