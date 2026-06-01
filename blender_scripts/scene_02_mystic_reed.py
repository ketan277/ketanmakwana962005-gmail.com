import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_ocean():
    # Large plane for the ocean
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
    ocean = bpy.context.object
    ocean.name = "Ocean"

    # Ocean Modifier for displacement
    mod = ocean.modifiers.new(name="Ocean", type='OCEAN')
    mod.resolution = 12
    mod.scale = 1.0
    mod.choppiness = 2.0

    # Material
    mat = bpy.data.materials.new(name="Ocean_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0.01, 0.05, 0.2, 1) # Deep blue
    bsdf.inputs[7].default_value = 0.1 # Low roughness
    bsdf.inputs[15].default_value = 1.33
    bsdf.inputs[17].default_value = 0.1 # Slight transmission
    ocean.data.materials.append(mat)

def create_boat():
    # Simple boat hull representation (scaled cube with subdivision)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.5))
    boat = bpy.context.object
    boat.name = "Mystic_Reed"
    boat.scale = (4, 1.5, 0.8)

    # Wooden Material
    mat = bpy.data.materials.new(name="Boat_Wood")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.05, 0.02, 1)
    boat.data.materials.append(mat)

    # Mast
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=6, location=(0, 0, 3.5))
    mast = bpy.context.object
    mast.data.materials.append(mat)

    # Sail
    bpy.ops.mesh.primitive_plane_add(size=4, location=(0.1, 0, 4.5))
    sail = bpy.context.object
    sail.rotation_euler[1] = math.radians(90)
    sail.scale[0] = 1.5

    sail_mat = bpy.data.materials.new(name="Sail_Cloth")
    sail_mat.use_nodes = True
    sail_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.75, 0.7, 1)
    sail.data.materials.append(sail_mat)

def setup_lighting():
    # Sun for mid-day
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 20))
    sun = bpy.context.object
    sun.data.energy = 10.0

    # Sky
    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    nodes["Background"].inputs[0].default_value = (0.2, 0.5, 1.0, 1) # Bright blue sky

def setup_camera():
    bpy.ops.object.camera_add(location=(15, -15, 8), rotation=(math.radians(65), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.object

def main():
    clear_scene()
    create_ocean()
    create_boat()
    setup_lighting()
    setup_camera()
    bpy.context.scene.render.engine = 'CYCLES'

if __name__ == "__main__":
    main()
