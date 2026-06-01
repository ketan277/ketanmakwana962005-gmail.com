import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_balloon():
    # Basket
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
    basket = bpy.context.object
    basket.scale = (1.5, 1.5, 1)

    wicker_mat = bpy.data.materials.new(name="Wicker")
    wicker_mat.use_nodes = True
    wicker_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.2, 0.1, 1)
    basket.data.materials.append(wicker_mat)

    # Burner / Cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1, location=(0, 0, 2.5))
    burner = bpy.context.object

    # Flame (Point light)
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 3))
    flame = bpy.context.object
    flame.data.energy = 1000.0
    flame.data.color = (1.0, 0.4, 0.1)

    # Patchwork Quilt Balloon
    bpy.ops.mesh.primitive_uv_sphere_add(radius=8, location=(0, 0, 12))
    balloon = bpy.context.object
    balloon.scale[2] = 1.2

    quilt_mat = bpy.data.materials.new(name="Patchwork_Quilt")
    quilt_mat.use_nodes = True
    quilt_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.2, 0.2, 1) # Primarily red for visualization
    balloon.data.materials.append(quilt_mat)

def setup_background():
    # Starry night
    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    nodes["Background"].inputs[0].default_value = (0.005, 0.005, 0.01, 1)

def setup_camera():
    bpy.ops.object.camera_add(location=(20, -20, 15), rotation=(math.radians(70), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_balloon()
    setup_background()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
