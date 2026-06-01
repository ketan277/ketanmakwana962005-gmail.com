import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_ruins():
    # Sandy ground
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.object

    mat = bpy.data.materials.new(name="Dusty_Ground")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.4, 0.3, 0.2, 1)
    ground.data.materials.append(mat)

    # Broken stone pillars
    for i in range(6):
        x = (i % 3) * 5 - 5
        y = (i // 3) * 8 - 4
        height = [3, 1, 4, 0.5, 2, 5][i]

        bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=height, location=(x, y, height/2))
        pillar = bpy.context.object

        stone_mat = bpy.data.materials.new(name="Weathered_Stone")
        stone_mat.use_nodes = True
        stone_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.2, 0.2, 1)
        pillar.data.materials.append(stone_mat)

def create_phoenix_footprint():
    # Emissive footprint on the ground
    bpy.ops.mesh.primitive_plane_add(size=0.5, location=(0, 0, 0.01))
    footprint = bpy.context.object

    glow_mat = bpy.data.materials.new(name="Phoenix_Glow")
    glow_mat.use_nodes = True
    bsdf = glow_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (1.0, 0.5, 0.0, 1)
    bsdf.inputs[19].default_value = (1.0, 0.5, 0.0, 1)
    bsdf.inputs[20].default_value = 10.0
    footprint.data.materials.append(glow_mat)

def setup_lighting():
    # Evening light
    bpy.ops.object.light_add(type='SUN', location=(10, 0, 10))
    sun = bpy.context.object
    sun.data.energy = 5.0
    sun.rotation_euler[1] = math.radians(45)

def setup_camera():
    bpy.ops.object.camera_add(location=(12, -12, 8), rotation=(math.radians(65), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_ruins()
    create_phoenix_footprint()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
