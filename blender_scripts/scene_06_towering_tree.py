import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_towering_tree():
    # Massive trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=10, depth=100, location=(0, 0, 50))
    trunk = bpy.context.object
    trunk.name = "Giant_Willow_Tree"

    # Bark Material
    bark_mat = bpy.data.materials.new(name="Ancient_Bark")
    bark_mat.use_nodes = True
    bark_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.03, 0.02, 1)
    trunk.data.materials.append(bark_mat)

    # Glowing Roots
    for i in range(8):
        angle = (i/8) * 2 * math.pi
        bpy.ops.mesh.primitive_cylinder_add(radius=2, depth=20, location=(15 * math.cos(angle), 15 * math.sin(angle), 0))
        root = bpy.context.object
        root.rotation_euler[0] = math.radians(90)
        root.rotation_euler[2] = angle

        glow_mat = bpy.data.materials.new(name="Orange_Glow")
        glow_mat.use_nodes = True
        bsdf = glow_mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs[0].default_value = (1.0, 0.3, 0.0, 1)
        bsdf.inputs[19].default_value = (1.0, 0.3, 0.0, 1) # Emission
        bsdf.inputs[20].default_value = 5.0 # Strength
        root.data.materials.append(glow_mat)

def create_doors():
    # Blue Door
    bpy.ops.mesh.primitive_cube_add(location=(10, 0, 2))
    door1 = bpy.context.object
    door1.scale = (0.2, 1, 2)

    blue_mat = bpy.data.materials.new(name="Blue_Door")
    blue_mat.use_nodes = True
    blue_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.0, 0.1, 0.5, 1)
    door1.data.materials.append(blue_mat)

    # "Not Blue" Door (Let's make it Red/Brown)
    bpy.ops.mesh.primitive_cube_add(location=(9.8, 3, 2)) # Slightly offset
    door2 = bpy.context.object
    door2.scale = (0.2, 1, 2)
    door2.rotation_euler[2] = math.radians(20)

    other_mat = bpy.data.materials.new(name="Not_Blue_Door")
    other_mat.use_nodes = True
    other_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.05, 0.05, 1)
    door2.data.materials.append(other_mat)

def setup_lighting():
    # Night time forest
    bpy.ops.object.light_add(type='POINT', location=(15, 0, 5))
    lamp = bpy.context.object
    lamp.data.energy = 1000.0

    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    nodes["Background"].inputs[0].default_value = (0.01, 0.01, 0.02, 1)

def setup_camera():
    bpy.ops.object.camera_add(location=(30, -20, 10), rotation=(math.radians(80), 0, math.radians(60)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_towering_tree()
    create_doors()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
