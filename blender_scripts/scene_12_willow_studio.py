import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_studio():
    # Tree interior room
    bpy.ops.mesh.primitive_cylinder_add(radius=8, depth=10, location=(0, 0, 5))
    room = bpy.context.object
    room.scale = (-1, -1, -1) # Invert

    wood_mat = bpy.data.materials.new(name="Tree_Interior")
    wood_mat.use_nodes = True
    wood_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.05, 0.02, 1)
    room.data.materials.append(wood_mat)

def create_desk():
    # Slanted desk built into the wall
    bpy.ops.mesh.primitive_cube_add(location=(6, 0, 3))
    desk = bpy.context.object
    desk.scale = (1, 3, 0.1)
    desk.rotation_euler[1] = math.radians(-30) # Slanted

    # Paint dips in the desk
    for i in range(5):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(6.2, i-2, 3.2))
        paint = bpy.context.object

        mat = bpy.data.materials.new(name=f"Paint_{i}")
        mat.use_nodes = True
        color = [(1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1), (1,0,1,1)][i]
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
        paint.data.materials.append(mat)

def create_paintings():
    # Large canvases on the walls
    for i in range(3):
        angle = (i + 1) * math.pi / 2
        bpy.ops.mesh.primitive_plane_add(size=2, location=(7 * math.cos(angle), 7 * math.sin(angle), 5))
        canvas = bpy.context.object
        canvas.rotation_euler[1] = math.radians(90)
        canvas.rotation_euler[2] = angle

        mat = bpy.data.materials.new(name=f"Painting_{i}")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.5, 0.5, 0.5, 1)
        canvas.data.materials.append(mat)

def create_spiral_staircase():
    # Simple spiral staircase
    for i in range(10):
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, i * 0.5))
        step = bpy.context.object
        step.scale = (3, 1, 0.1)
        step.rotation_euler[2] = i * math.radians(30)
        step.location[0] = 3 * math.cos(i * math.radians(30))
        step.location[1] = 3 * math.sin(i * math.radians(30))

        step.data.materials.append(bpy.data.materials["Tree_Interior"])

def setup_lighting():
    # Window light (warm)
    bpy.ops.object.light_add(type='AREA', location=(7.5, 0, 5))
    window_light = bpy.context.object
    window_light.rotation_euler[1] = math.radians(-90)
    window_light.data.energy = 500.0
    window_light.data.color = (1.0, 0.8, 0.6)

def setup_camera():
    bpy.ops.object.camera_add(location=(-5, -5, 6), rotation=(math.radians(70), 0, math.radians(-45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_studio()
    create_desk()
    create_paintings()
    create_spiral_staircase()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
