import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_desert():
    # Large plane with subdivision and displacement for dunes
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
    ground = bpy.context.object

    # Subdivide
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=50)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Displace modifier for dunes
    tex = bpy.data.textures.new("DuneTex", type='CLOUDS')
    tex.noise_scale = 5.0
    mod = ground.modifiers.new(name="Dunes", type='DISPLACE')
    mod.texture = tex
    mod.strength = 5.0

    # Sand Material
    mat = bpy.data.materials.new(name="Sand")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.76, 0.6, 0.3, 1)
    ground.data.materials.append(mat)

def create_oasis_pond():
    # Small pond in the middle
    bpy.ops.mesh.primitive_circle_add(radius=8, fill_type='NGON', location=(0, 0, 1))
    pond = bpy.context.object

    water_mat = bpy.data.materials.new(name="Oasis_Water")
    water_mat.use_nodes = True
    bsdf = water_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0.05, 0.2, 0.2, 1)
    bsdf.inputs[17].default_value = 1.0
    pond.data.materials.append(water_mat)

def create_palm_trees():
    for i in range(5):
        angle = (i / 5) * 2 * math.pi
        x = 10 * math.cos(angle)
        y = 10 * math.sin(angle)

        # Simple palm trunk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=6, location=(x, y, 4))
        trunk = bpy.context.object

        # Simple fronds
        for j in range(8):
            bpy.ops.mesh.primitive_plane_add(size=3, location=(x, y, 7))
            frond = bpy.context.object
            frond.rotation_euler[0] = math.radians(45)
            frond.rotation_euler[2] = (j/8) * 2 * math.pi

            leaf_mat = bpy.data.materials.new(name="Palm_Leaf")
            leaf_mat.use_nodes = True
            leaf_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.2, 0.01, 1)
            frond.data.materials.append(leaf_mat)

def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
    sun = bpy.context.object
    sun.data.energy = 15.0
    sun.rotation_euler = (math.radians(10), 0, 0) # Hot mid-day sun

def setup_camera():
    bpy.ops.object.camera_add(location=(30, -30, 20), rotation=(math.radians(60), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_desert()
    create_oasis_pond()
    create_palm_trees()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
