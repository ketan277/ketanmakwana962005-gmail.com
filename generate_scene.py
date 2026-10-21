import bpy
import math
import os

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def setup_render_settings():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE' # Fast and good for neon/reflections
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080 # 16:9 ratio
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 240

    # Render format output setup
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.filepath = os.path.abspath("neon_alley_parkour.mp4")

    # EEVEE settings for bloom and reflections
    if hasattr(scene, 'eevee'):
        if hasattr(scene.eevee, 'taa_render_samples'):
            scene.eevee.taa_render_samples = 32
        if hasattr(scene.eevee, 'use_bloom'):
            scene.eevee.use_bloom = True
        if hasattr(scene.eevee, 'use_ssr'):
            scene.eevee.use_ssr = True # Screen Space Reflections
        if hasattr(scene.eevee, 'use_ssr_refraction'):
            scene.eevee.use_ssr_refraction = True

def create_material(name, color=(0.8, 0.8, 0.8, 1), metallic=0.0, roughness=0.5, emission=(0,0,0,1), emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    if bsdf:
        # Base Color
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        # Metallic
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        # Roughness
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        # Emission
        if emission_strength > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = color if emission == (0,0,0,1) else emission
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = color if emission == (0,0,0,1) else emission

            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def build_environment():
    # Materials
    wet_asphalt_mat = create_material("WetAsphalt", color=(0.03, 0.03, 0.04, 1), metallic=0.2, roughness=0.1)
    brick_mat = create_material("BrickWall", color=(0.15, 0.08, 0.06, 1), metallic=0.0, roughness=0.7)
    dumpster_mat = create_material("DumpsterMat", color=(0.02, 0.15, 0.08, 1), metallic=0.6, roughness=0.4)
    dumpster_lid_mat = create_material("DumpsterLidMat", color=(0.02, 0.02, 0.02, 1), metallic=0.1, roughness=0.5)
    fire_escape_mat = create_material("FireEscapeMat", color=(0.1, 0.1, 0.12, 1), metallic=0.8, roughness=0.3)

    # Neon materials
    neon_cyan = create_material("NeonCyan", color=(0.0, 0.8, 1.0, 1), emission=(0.0, 0.8, 1.0, 1), emission_strength=15.0)
    neon_magenta = create_material("NeonMagenta", color=(1.0, 0.0, 0.5, 1), emission=(1.0, 0.0, 0.5, 1), emission_strength=15.0)
    neon_orange = create_material("NeonOrange", color=(1.0, 0.4, 0.0, 1), emission=(1.0, 0.4, 0.0, 1), emission_strength=15.0)

    # Ground Plane 1 (Straight Alley: Y = -5 to 33, X = -3.5 to 3.5)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 14, 0))
    ground1 = bpy.context.active_object
    ground1.name = "Ground_Straight"
    ground1.scale = (7.0, 38.0, 1.0)
    ground1.data.materials.append(wet_asphalt_mat)

    # Ground Plane 2 (Corner Alley: X = 3 to 30, Y = 30)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(16.5, 30, 0))
    ground2 = bpy.context.active_object
    ground2.name = "Ground_Corner"
    ground2.scale = (27.0, 6.0, 1.0)
    ground2.data.materials.append(wet_asphalt_mat)

    # Walls for Straight Alley
    # Left Wall (X = -3.5, Y = -5 to 33, Z = 0 to 12)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-3.6, 14, 6))
    w_left = bpy.context.active_object
    w_left.scale = (0.2, 38.0, 12.0)
    w_left.data.materials.append(brick_mat)

    # Right Wall Part 1 (X = 3.5, Y = -5 to 27, Z = 0 to 12)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(3.6, 11, 6))
    w_right1 = bpy.context.active_object
    w_right1.scale = (0.2, 32.0, 12.0)
    w_right1.data.materials.append(brick_mat)

    # Far Wall (Y = 33.1, X = -3.5 to 30, Z = 0 to 12)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(13.25, 33.1, 6))
    w_far = bpy.context.active_object
    w_far.scale = (33.7, 0.2, 12.0)
    w_far.data.materials.append(brick_mat)

    # Corner Wall South (Y = 26.9, X = 3.5 to 30, Z = 0 to 12)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(16.75, 26.9, 6))
    w_south = bpy.context.active_object
    w_south.scale = (26.7, 0.2, 12.0)
    w_south.data.materials.append(brick_mat)

    # Props: Dumpster (Location X = 1.2, Y = 13.0, Z = 0.6)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(1.2, 13.0, 0.6))
    dumpster = bpy.context.active_object
    dumpster.name = "Dumpster"
    dumpster.scale = (1.6, 2.2, 1.2)
    dumpster.data.materials.append(dumpster_mat)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(1.2, 13.0, 1.25))
    lid = bpy.context.active_object
    lid.name = "DumpsterLid"
    lid.scale = (1.7, 2.3, 0.1)
    lid.data.materials.append(dumpster_lid_mat)

    # Props: Fire Escape Ladder & Structure at X = 25.0, Y = 32.8
    # Platform 1
    bpy.ops.mesh.primitive_cube_add(size=1, location=(25.0, 32.2, 2.5))
    fe_plat1 = bpy.context.active_object
    fe_plat1.scale = (3.0, 1.2, 0.1)
    fe_plat1.data.materials.append(fire_escape_mat)

    # Platform 2
    bpy.ops.mesh.primitive_cube_add(size=1, location=(25.0, 32.2, 5.0))
    fe_plat2 = bpy.context.active_object
    fe_plat2.scale = (3.0, 1.2, 0.1)
    fe_plat2.data.materials.append(fire_escape_mat)

    # Ladder side bars & rungs
    for x_off in [-0.4, 0.4]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=3.5, location=(25.0 + x_off, 32.6, 1.75))
        bar = bpy.context.active_object
        bar.data.materials.append(fire_escape_mat)

    for rung_z in [0.3, 0.7, 1.1, 1.5, 1.9, 2.3, 2.7, 3.1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.8, location=(25.0, 32.6, rung_z))
        rung = bpy.context.active_object
        rung.rotation_euler = (0, math.pi/2, 0)
        rung.data.materials.append(fire_escape_mat)

    # Neon Signs
    # Neon Sign 1 (Cyan) - Left wall Y = 6
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-3.4, 6.0, 4.0))
    sign1 = bpy.context.active_object
    sign1.scale = (0.1, 3.0, 1.2)
    sign1.data.materials.append(neon_cyan)

    # Neon Sign 2 (Magenta) - Right wall Y = 18
    bpy.ops.mesh.primitive_cube_add(size=1, location=(3.4, 18.0, 4.5))
    sign2 = bpy.context.active_object
    sign2.scale = (0.1, 2.5, 1.5)
    sign2.data.materials.append(neon_magenta)

    # Neon Sign 3 (Orange) - Corner Wall Far Y = 32.9, X = 12
    bpy.ops.mesh.primitive_cube_add(size=1, location=(12.0, 32.9, 5.0))
    sign3 = bpy.context.active_object
    sign3.scale = (4.0, 0.1, 1.5)
    sign3.data.materials.append(neon_orange)

    # Lighting
    # Dark atmospheric moonlight/ambient
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 20))
    sun = bpy.context.active_object
    sun.data.energy = 0.3
    sun.data.color = (0.1, 0.15, 0.3)

    # Neon Point Lights for ambient glow & fill
    bpy.ops.object.light_add(type='POINT', location=(0.0, 2.0, 1.5))
    p0 = bpy.context.active_object
    p0.data.color = (0.2, 0.6, 1.0)
    p0.data.energy = 300 # Illuminates running shoes in Shot 1

    bpy.ops.object.light_add(type='POINT', location=(-2.5, 6.0, 3.5))
    p1 = bpy.context.active_object
    p1.data.color = (0.0, 0.8, 1.0)
    p1.data.energy = 400

    bpy.ops.object.light_add(type='POINT', location=(2.5, 18.0, 4.0))
    p2 = bpy.context.active_object
    p2.data.color = (1.0, 0.0, 0.5)
    p2.data.energy = 400

    bpy.ops.object.light_add(type='POINT', location=(12.0, 31.5, 4.5))
    p3 = bpy.context.active_object
    p3.data.color = (1.0, 0.4, 0.0)
    p3.data.energy = 500

    bpy.ops.object.light_add(type='POINT', location=(24.0, 31.5, 4.0))
    p4 = bpy.context.active_object
    p4.data.color = (0.0, 0.8, 1.0)
    p4.data.energy = 400 # Fire escape accent light

def build_character():
    # Readable Blocky Character in Hoodie and Running Shoes
    hoodie_mat = create_material("HoodieYellow", color=(0.95, 0.8, 0.05, 1), metallic=0.0, roughness=0.6)
    pants_mat = create_material("PantsDark", color=(0.05, 0.05, 0.08, 1), metallic=0.0, roughness=0.8)
    shoe_mat = create_material("ShoeWhite", color=(0.95, 0.95, 0.95, 1), metallic=0.1, roughness=0.2)
    skin_mat = create_material("SkinDark", color=(0.15, 0.1, 0.08, 1), metallic=0.0, roughness=0.5)

    # Character Root Empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    char_root = bpy.context.active_object
    char_root.name = "Character_Root"

    # Torso (Hoodie)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.1))
    torso = bpy.context.active_object
    torso.name = "Char_Torso"
    torso.scale = (0.5, 0.35, 0.6)
    torso.data.materials.append(hoodie_mat)
    torso.parent = char_root

    # Head (Hooded)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0, 0, 1.55))
    head = bpy.context.active_object
    head.name = "Char_Head"
    head.data.materials.append(hoodie_mat)
    head.parent = char_root

    # Face mask / inner head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0, 0.05, 1.55))
    face = bpy.context.active_object
    face.name = "Char_Face"
    face.data.materials.append(skin_mat)
    face.parent = char_root

    # Legs (Pants)
    for side, x_off in [("L", -0.15), ("R", 0.15)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_off, 0, 0.45))
        leg = bpy.context.active_object
        leg.name = f"Char_Leg_{side}"
        leg.scale = (0.18, 0.2, 0.7)
        leg.data.materials.append(pants_mat)
        leg.parent = char_root

    # Running Shoes (Bright White)
    for side, x_off in [("L", -0.15), ("R", 0.15)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_off, 0.08, 0.1))
        shoe = bpy.context.active_object
        shoe.name = f"Char_Shoe_{side}"
        shoe.scale = (0.2, 0.38, 0.18)
        shoe.data.materials.append(shoe_mat)
        shoe.parent = char_root

    # Arms
    for side, x_off in [("L", -0.32), ("R", 0.32)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_off, 0, 1.05))
        arm = bpy.context.active_object
        arm.name = f"Char_Arm_{side}"
        arm.scale = (0.14, 0.18, 0.55)
        arm.data.materials.append(hoodie_mat)
        arm.parent = char_root

    return char_root

def animate_character(char_root):
    # Retrieve limb objects for gait animation
    leg_l = bpy.data.objects.get("Char_Leg_L")
    leg_r = bpy.data.objects.get("Char_Leg_R")
    arm_l = bpy.data.objects.get("Char_Arm_L")
    arm_r = bpy.data.objects.get("Char_Arm_R")
    torso = bpy.data.objects.get("Char_Torso")

    # Root motion keyframes across 240 frames
    # Frame 1
    char_root.location = (0.0, 0.0, 0.0)
    char_root.rotation_euler = (0.0, 0.0, 0.0)
    char_root.keyframe_insert(data_path="location", frame=1)
    char_root.keyframe_insert(data_path="rotation_euler", frame=1)

    # Frame 35 (Approach dumpster)
    char_root.location = (0.0, 9.5, 0.0)
    char_root.rotation_euler = (0.0, 0.0, 0.0)
    char_root.keyframe_insert(data_path="location", frame=35)
    char_root.keyframe_insert(data_path="rotation_euler", frame=35)

    # Frame 50 (Apex of vault over dumpster at Y=13.0, Z=2.2)
    char_root.location = (0.2, 13.0, 2.2)
    char_root.rotation_euler = (math.radians(-15), 0.0, 0.0)
    char_root.keyframe_insert(data_path="location", frame=50)
    char_root.keyframe_insert(data_path="rotation_euler", frame=50)

    # Frame 70 (Landing after dumpster)
    char_root.location = (0.0, 17.5, 0.0)
    char_root.rotation_euler = (0.0, 0.0, 0.0)
    char_root.keyframe_insert(data_path="location", frame=70)
    char_root.keyframe_insert(data_path="rotation_euler", frame=70)

    # Frame 130 (Reaching corner turn entry point Y=29.0)
    char_root.location = (0.0, 29.0, 0.0)
    char_root.rotation_euler = (0.0, 0.0, 0.0)
    char_root.keyframe_insert(data_path="location", frame=130)
    char_root.keyframe_insert(data_path="rotation_euler", frame=130)

    # Frame 150 (Banking sharp corner turn at X=4.0, Y=30.0)
    char_root.location = (4.0, 30.0, 0.0)
    char_root.rotation_euler = (0.0, math.radians(-15), math.radians(-90)) # banked turn facing +X
    char_root.keyframe_insert(data_path="location", frame=150)
    char_root.keyframe_insert(data_path="rotation_euler", frame=150)

    # Frame 170 (Exiting corner turn onto straight leg X=12.0)
    char_root.location = (12.0, 30.0, 0.0)
    char_root.rotation_euler = (0.0, 0.0, math.radians(-90))
    char_root.keyframe_insert(data_path="location", frame=170)
    char_root.keyframe_insert(data_path="rotation_euler", frame=170)

    # Frame 210 (Approaching fire escape ladder X=21.0)
    char_root.location = (21.0, 30.0, 0.0)
    char_root.rotation_euler = (0.0, 0.0, math.radians(-90))
    char_root.keyframe_insert(data_path="location", frame=210)
    char_root.keyframe_insert(data_path="rotation_euler", frame=210)

    # Frame 240 (Leap towards fire escape ladder at X=24.2, Z=2.5)
    char_root.location = (24.2, 31.5, 2.5)
    char_root.rotation_euler = (math.radians(20), math.radians(-10), math.radians(-45))
    char_root.keyframe_insert(data_path="location", frame=240)
    char_root.keyframe_insert(data_path="rotation_euler", frame=240)

    # Limb gait cycles for high-energy running animation
    for f in range(1, 241, 6):
        stride_phase = math.sin(f * 0.4)
        leg_rot = stride_phase * math.radians(35)
        arm_rot = -stride_phase * math.radians(40)
        bob = abs(math.sin(f * 0.4)) * 0.1

        if leg_l and leg_r:
            leg_l.rotation_euler = (leg_rot, 0, 0)
            leg_r.rotation_euler = (-leg_rot, 0, 0)
            leg_l.keyframe_insert(data_path="rotation_euler", frame=f)
            leg_r.keyframe_insert(data_path="rotation_euler", frame=f)

        if arm_l and arm_r:
            arm_l.rotation_euler = (arm_rot, 0, 0)
            arm_r.rotation_euler = (-arm_rot, 0, 0)
            arm_l.keyframe_insert(data_path="rotation_euler", frame=f)
            arm_r.keyframe_insert(data_path="rotation_euler", frame=f)

        if torso and (f < 35 or (70 <= f <= 130) or (170 <= f <= 210)):
            torso.location = (0, 0, 1.1 + bob)
            torso.keyframe_insert(data_path="location", frame=f)

    # Specific parkour poses
    # Vault over dumpster (Frames 35 to 70)
    if leg_l and leg_r and arm_l and arm_r:
        # Tuck legs during vault
        leg_l.rotation_euler = (math.radians(-60), 0, 0)
        leg_r.rotation_euler = (math.radians(-40), 0, 0)
        arm_l.rotation_euler = (math.radians(45), 0, 0)
        arm_r.rotation_euler = (math.radians(45), 0, 0)
        for f in [45, 50, 55]:
            leg_l.keyframe_insert(data_path="rotation_euler", frame=f)
            leg_r.keyframe_insert(data_path="rotation_euler", frame=f)
            arm_l.keyframe_insert(data_path="rotation_euler", frame=f)
            arm_r.keyframe_insert(data_path="rotation_euler", frame=f)

        # Reach out during fire escape leap (Frames 220 to 240)
        arm_l.rotation_euler = (math.radians(-80), 0, 0)
        arm_r.rotation_euler = (math.radians(-75), 0, 0)
        leg_l.rotation_euler = (math.radians(40), 0, 0)
        leg_r.rotation_euler = (math.radians(20), 0, 0)
        for f in [225, 235, 240]:
            leg_l.keyframe_insert(data_path="rotation_euler", frame=f)
            leg_r.keyframe_insert(data_path="rotation_euler", frame=f)
            arm_l.keyframe_insert(data_path="rotation_euler", frame=f)
            arm_r.keyframe_insert(data_path="rotation_euler", frame=f)


def build_and_animate_camera(char_root):
    # Camera creation & setup
    bpy.ops.object.camera_add(location=(0, 0, 0))
    cam = bpy.context.active_object
    cam.name = "Parkour_Camera"
    bpy.context.scene.camera = cam

    cam.data.lens = 22 # Dynamic wide angle focal length for speed perception

    # Target Empty for Camera tracking
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    cam_target = bpy.context.active_object
    cam_target.name = "Camera_Target"

    # Add Track To constraint on Camera pointing at Target
    track = cam.constraints.new(type='TRACK_TO')
    track.target = cam_target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Camera target keyframes (tracks character center / legs)

    # SHOT 1 (Frames 1-35): Low-angle close-up of running shoes
    cam_target.location = (0.0, 1.0, 0.15)
    cam_target.keyframe_insert(data_path="location", frame=1)
    cam.location = (0.0, 2.5, 0.35)
    cam.keyframe_insert(data_path="location", frame=1)

    cam_target.location = (0.0, 8.5, 0.15)
    cam_target.keyframe_insert(data_path="location", frame=35)
    cam.location = (0.0, 10.0, 0.35)
    cam.keyframe_insert(data_path="location", frame=35)

    # SHOT 2 (Frames 36-110): Pull back ahead of character, tracking leap over dumpster
    cam_target.location = (0.0, 12.0, 1.2)
    cam_target.keyframe_insert(data_path="location", frame=40)
    cam.location = (-0.5, 17.5, 1.6)
    cam.keyframe_insert(data_path="location", frame=40)

    # Peak of jump over dumpster (Frame 55)
    cam_target.location = (0.2, 13.5, 2.0)
    cam_target.keyframe_insert(data_path="location", frame=55)
    cam.location = (-0.8, 19.5, 1.5)
    cam.keyframe_insert(data_path="location", frame=55)

    # Character running towards camera after jump landing (Frame 110)
    cam_target.location = (0.0, 26.0, 1.2)
    cam_target.keyframe_insert(data_path="location", frame=110)
    cam.location = (-0.8, 30.5, 1.5)
    cam.keyframe_insert(data_path="location", frame=110)

    # SHOT 3 (Frames 111-175): Dynamic wide profile swing at sharp corner turn (safe inside alley space)
    cam_target.location = (1.5, 29.5, 1.0)
    cam_target.keyframe_insert(data_path="location", frame=115)
    cam.location = (-1.2, 28.0, 1.8)
    cam.keyframe_insert(data_path="location", frame=115)

    cam_target.location = (6.0, 30.0, 1.0)
    cam_target.keyframe_insert(data_path="location", frame=150)
    cam.location = (-1.2, 28.0, 1.8)
    cam.keyframe_insert(data_path="location", frame=150)

    cam_target.location = (13.0, 30.0, 1.0)
    cam_target.keyframe_insert(data_path="location", frame=175)
    cam.location = (-0.5, 28.5, 1.8)
    cam.keyframe_insert(data_path="location", frame=175)

    # SHOT 4 (Frames 176-240): Smooth push-in as character leaps toward fire escape ladder
    cam_target.location = (19.0, 30.0, 1.2)
    cam_target.keyframe_insert(data_path="location", frame=180)
    cam.location = (14.0, 28.2, 1.8)
    cam.keyframe_insert(data_path="location", frame=180)

    cam_target.location = (24.5, 31.5, 2.8)
    cam_target.keyframe_insert(data_path="location", frame=240)
    cam.location = (20.5, 28.5, 2.0)
    cam.keyframe_insert(data_path="location", frame=240)


def main():
    print("--- Starting Neon Alley Parkour Scene Generation ---")
    reset_scene()
    setup_render_settings()
    build_environment()
    char_root = build_character()
    animate_character(char_root)
    build_and_animate_camera(char_root)

    # Save full project blend file
    blend_path = os.path.abspath("neon_alley_parkour.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved project file to: {blend_path}")

    # Optimize render speed for fast preview MP4 generation in headless CPU mode
    scene = bpy.context.scene
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540 # 16:9 ratio preview
    if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
        scene.eevee.taa_render_samples = 1

    # Render animation preview MP4
    print("Starting animation preview render...")
    bpy.ops.render.render(animation=True)
    print(f"Render completed. Output MP4 saved to: {bpy.context.scene.render.filepath}")

if __name__ == "__main__":
    main()
