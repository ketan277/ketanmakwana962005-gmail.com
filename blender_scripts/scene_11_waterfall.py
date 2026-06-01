import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_waterfall():
    # Cliff
    bpy.ops.mesh.primitive_cube_add(location=(-5, 0, 5))
    cliff = bpy.context.object
    cliff.scale = (5, 10, 5)

    # Waterfall plane
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-0.1, 0, 5))
    fall = bpy.context.object
    fall.rotation_euler[1] = math.radians(90)
    fall.scale = (5, 3, 1)

    # Silver Glow Material for water
    water_mat = bpy.data.materials.new(name="Silvery_Water")
    water_mat.use_nodes = True
    bsdf = water_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0.8, 0.9, 1.0, 1)
    bsdf.inputs[19].default_value = (0.5, 0.6, 0.8, 1) # Emission
    bsdf.inputs[20].default_value = 2.0
    fall.data.materials.append(water_mat)

def create_stream_and_mud():
    # Stream below
    bpy.ops.mesh.primitive_plane_add(size=20, location=(5, 0, 0.1))
    stream = bpy.context.object

    # Mud with gold flecks (Procedural)
    mud_mat = bpy.data.materials.new(name="Gold_Mud")
    mud_mat.use_nodes = True
    nodes = mud_mat.node_tree.nodes
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0.1, 0.05, 0.02, 1) # Mud base

    # Add gold flecks using a Voronoi texture
    tex = nodes.new(type='ShaderNodeTexVoronoi')
    tex.inputs[2].default_value = 50.0 # Scale

    # Mix with gold color
    bsdf.inputs[19].default_value = (1.0, 0.8, 0.1, 1) # Gold Emission
    # Use Voronoi to drive emission strength
    mud_mat.node_tree.links.new(tex.outputs[0], bsdf.inputs[20])

    stream.data.materials.append(mud_mat)

def setup_lighting():
    # Moon light
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
    moon = bpy.context.object
    moon.data.energy = 2.0
    moon.data.color = (0.8, 0.9, 1.0)

    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    nodes["Background"].inputs[0].default_value = (0.01, 0.01, 0.02, 1)

def setup_camera():
    bpy.ops.object.camera_add(location=(15, -15, 8), rotation=(math.radians(70), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_waterfall()
    create_stream_and_mud()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
