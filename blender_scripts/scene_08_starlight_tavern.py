import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_tavern():
    # Interior room
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 5))
    room = bpy.context.object
    room.scale = (10, 10, 5)
    room.scale = (-1, -1, -1) # Flip normals

    wood_mat = bpy.data.materials.new(name="Dark_Wood")
    wood_mat.use_nodes = True
    wood_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.02, 0.01, 1)
    room.data.materials.append(wood_mat)

def create_furniture():
    # Tables and Chairs
    for i in range(4):
        x = (i % 2) * 6 - 3
        y = (i // 2) * 6 - 3

        # Table
        bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=0.1, location=(x, y, 1.5))
        table = bpy.context.object
        table.data.materials.append(bpy.data.materials["Dark_Wood"])

        # Table leg
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.5, location=(x, y, 0.75))
        leg = bpy.context.object
        leg.data.materials.append(bpy.data.materials["Dark_Wood"])

def setup_lighting():
    # Warm, dim lanterns
    for i in range(2):
        bpy.ops.object.light_add(type='POINT', location=(3 * ((-1)**i), 0, 4))
        lamp = bpy.context.object
        lamp.data.energy = 200.0
        lamp.data.color = (1.0, 0.6, 0.2)
        lamp.data.shadow_soft_size = 1.0

def setup_camera():
    bpy.ops.object.camera_add(location=(8, -8, 4), rotation=(math.radians(75), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_tavern()
    create_furniture()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
