"""
Excavator Rigging & Animation Master Script for Blender 5.1.1
==============================================================
Author: Technical Automation
Description:
    Fully automated Python script for rigging and animating a 26-part excavator model
    in Blender 5.1.1 without external add-ons or dependencies.

Features:
    1. Validation of all 26 scene objects.
    2. Dynamic pivot calculation from scene mesh objects.
    3. Creation of an Armature with hierarchy: base -> boom -> arm -> bucket.
    4. Stable hydraulic piston mechanics using Damped Track constraints and target empties
       (eliminates dependency cycles).
    5. Mechanical rotation limits for realistic operation.
    6. Complete 250-frame animation sequence (Base Turn -> Boom Lift -> Arm Extend ->
       Bucket Dig -> Dump -> Return to Rest) with smooth Bezier interpolation.
"""

import bpy
import math
from mathutils import Vector

# =============================================================================
# 1. OBJECT VALIDATION
# =============================================================================
REQUIRED_OBJECTS = [
    "Arm", "Base", "Boom", "Bucket",
    "Cylinder", "Cylinder.007", "Cylinder.010", "Cylinder.019",
    "Cylinder.023", "Cylinder.024", "Cylinder.027", "Cylinder.029",
    "Cylinder.032", "Cylinder.040", "Cylinder.048", "Cylinder.049",
    "Linkage_02", "Linkage_1",
    "Piston_Base_Arm", "Piston_Base_Boom.L", "Piston_Base_Boom.R", "Piston_Base_Bucket",
    "Piston_Rod_Arm", "Piston_Rod_Boom.L", "Piston_Rod_Boom.R", "Piston_Rod_Bucket"
]

def validate_scene():
    missing = [name for name in REQUIRED_OBJECTS if name not in bpy.data.objects]
    if missing:
        raise ValueError(
            f"\n[CRITICAL ERROR] Missing required excavator objects in scene: {missing}\n"
            "Please ensure all 26 objects exist before executing the script."
        )
    print("✓ Scene Validation Passed: All 26 Excavator objects located.")

validate_scene()

# =============================================================================
# 2. PIVOT COORDINATE EXTRACTION
# =============================================================================
def get_world_pos(obj_name):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        raise KeyError(f"Object '{obj_name}' missing from scene.")
    return obj.matrix_world.translation.copy()

# Primary Hinge & Pivot Vectors
p_base_ground    = get_world_pos("Cylinder.040") # Base swivel center
p_boom_hinge     = get_world_pos("Cylinder.010") # Base-to-Boom pivot
p_arm_hinge      = get_world_pos("Cylinder.007") # Boom-to-Arm pivot
p_bucket_hinge   = get_world_pos("Cylinder.019") # Arm-to-Bucket pivot

# Arm Hydraulic Cylinder Pivots
p_arm_pst_base   = get_world_pos("Cylinder.027") # Arm piston base hinge on Boom
p_arm_pst_rod    = get_world_pos("Cylinder.024") # Arm piston rod hinge on Arm

# Bucket Hydraulic Cylinder & Linkage Pivots
p_bkt_pst_base   = get_world_pos("Cylinder.023") # Bucket piston base hinge on Arm
p_link_arm       = get_world_pos("Cylinder.048") # Upper linkage pivot on Arm
p_link_bkt       = get_world_pos("Cylinder")     # Lower linkage pivot on Bucket
p_link_junction  = get_world_pos("Cylinder.049") # Central linkage junction point

# Boom Hydraulic Cylinders (Left & Right) Pivots
p_bm_pst_rod_R   = get_world_pos("Cylinder.029") # Boom piston rod hinge on Base (Right)
p_bm_pst_rod_L   = get_world_pos("Cylinder.032") # Boom piston rod hinge on Base (Left)
p_bm_pst_base_R  = get_world_pos("Piston_Base_Boom.R") # Boom piston base hinge on Boom (Right)
p_bm_pst_base_L  = get_world_pos("Piston_Base_Boom.L") # Boom piston base hinge on Boom (Left)

# =============================================================================
# 3. ARMATURE & BONE STRUCTURE CREATION
# =============================================================================
# Remove existing armature if present to allow re-runs
if "Excavator_Armature" in bpy.data.objects:
    arm_to_remove = bpy.data.objects["Excavator_Armature"]
    bpy.data.objects.remove(arm_to_remove, do_unlink=True)

armature_data = bpy.data.armatures.new("Excavator_Rig")
armature_obj = bpy.data.objects.new("Excavator_Armature", armature_data)
bpy.context.scene.collection.objects.link(armature_obj)

bpy.context.view_layer.objects.active = armature_obj
armature_obj.select_set(True)

# Viewport Display Settings
armature_data.display_type = 'STICK'
armature_obj.show_in_front = True

bpy.ops.object.mode_set(mode='EDIT')
edit_bones = armature_data.edit_bones

def add_bone(name, head, tail, parent_name=None):
    b = edit_bones.new(name)
    b.head = head
    b.tail = tail
    if parent_name and parent_name in edit_bones:
        b.parent = edit_bones[parent_name]
        b.use_connect = False
    return b

# Core Kinematic Chain
b_base = add_bone("base", p_base_ground, p_boom_hinge)
b_boom = add_bone("boom", p_boom_hinge, p_arm_hinge, "base")
b_arm  = add_bone("arm", p_arm_hinge, p_bucket_hinge, "boom")
b_bkt  = add_bone("bucket", p_bucket_hinge, p_link_bkt, "arm")

# Arm Hydraulic Cylinder Bones
b_arm_pst_base = add_bone("arm_piston_base", p_arm_pst_base, p_arm_pst_rod, "boom")
b_arm_pst_rod  = add_bone("arm_piston_rod", p_arm_pst_rod, p_arm_pst_base, "arm")

# Bucket Linkage & Cylinder Bones
b_link_02 = add_bone("linkage_02", p_link_arm, p_link_junction, "arm")
b_link_1  = add_bone("linkage_1", p_link_bkt, p_link_junction, "bucket")
b_bkt_pst_base = add_bone("bucket_piston_base", p_bkt_pst_base, p_link_junction, "arm")
b_bkt_pst_rod  = add_bone("bucket_piston_rod", p_link_junction, p_bkt_pst_base, "linkage_1")

# Boom Dual Hydraulic Cylinders Bones
b_bm_pst_base_R = add_bone("boom_piston_base.R", p_bm_pst_base_R, p_bm_pst_rod_R, "boom")
b_bm_pst_rod_R  = add_bone("boom_piston_rod.R", p_bm_pst_rod_R, p_bm_pst_base_R, "base")

b_bm_pst_base_L = add_bone("boom_piston_base.L", p_bm_pst_base_L, p_bm_pst_rod_L, "boom")
b_bm_pst_rod_L  = add_bone("boom_piston_rod.L", p_bm_pst_rod_L, p_bm_pst_base_L, "base")

bpy.ops.object.mode_set(mode='OBJECT')

# =============================================================================
# 4. DEPENDENCY-FREE TARGET EMPTIES CREATION
# =============================================================================
def create_empty(name, pos, parent_obj_name):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = 'PLAIN_AXES'
    empty.empty_display_size = 0.4
    empty.location = pos
    bpy.context.scene.collection.objects.link(empty)

    parent_obj = bpy.data.objects.get(parent_obj_name)
    if parent_obj:
        w_mat = empty.matrix_world.copy()
        empty.parent = parent_obj
        empty.matrix_parent_inverse = parent_obj.matrix_world.inverted()
        empty.matrix_world = w_mat
    return empty

# Target Empties attached to mesh components to guide hydraulic cylinder tracking
emp_arm_pst_rod_target   = create_empty("Target_Arm_Piston_Rod", p_arm_pst_rod, "Arm")
emp_arm_pst_base_target  = create_empty("Target_Arm_Piston_Base", p_arm_pst_base, "Boom")

emp_bkt_pst_junc_target  = create_empty("Target_Bucket_Piston_Junc", p_link_junction, "Linkage_1")
emp_bkt_pst_base_target  = create_empty("Target_Bucket_Piston_Base", p_bkt_pst_base, "Arm")

emp_bm_pst_rod_R_target  = create_empty("Target_Boom_Piston_Rod_R", p_bm_pst_rod_R, "Base")
emp_bm_pst_base_R_target = create_empty("Target_Boom_Piston_Base_R", p_bm_pst_base_R, "Boom")

emp_bm_pst_rod_L_target  = create_empty("Target_Boom_Piston_Rod_L", p_bm_pst_rod_L, "Base")
emp_bm_pst_base_L_target = create_empty("Target_Boom_Piston_Base_L", p_bm_pst_base_L, "Boom")

# =============================================================================
# 5. MESH PARENTING TO ARMATURE BONES
# =============================================================================
def parent_obj_to_bone(obj_name, armature_obj, bone_name):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        return
    w_mat = obj.matrix_world.copy()
    obj.parent = armature_obj
    obj.parent_type = 'BONE'
    obj.parent_bone = bone_name

    bone_world_matrix = armature_obj.matrix_world @ armature_obj.pose.bones[bone_name].matrix
    obj.matrix_parent_inverse = bone_world_matrix.inverted()
    obj.matrix_world = w_mat

# Main Body Components
parent_obj_to_bone("Base", armature_obj, "base")
parent_obj_to_bone("Boom", armature_obj, "boom")
parent_obj_to_bone("Arm", armature_obj, "arm")
parent_obj_to_bone("Bucket", armature_obj, "bucket")

# Hydraulic Cylinders & Pistons
parent_obj_to_bone("Piston_Base_Arm", armature_obj, "arm_piston_base")
parent_obj_to_bone("Piston_Rod_Arm", armature_obj, "arm_piston_rod")

parent_obj_to_bone("Linkage_02", armature_obj, "linkage_02")
parent_obj_to_bone("Linkage_1", armature_obj, "linkage_1")
parent_obj_to_bone("Piston_Base_Bucket", armature_obj, "bucket_piston_base")
parent_obj_to_bone("Piston_Rod_Bucket", armature_obj, "bucket_piston_rod")

parent_obj_to_bone("Piston_Base_Boom.R", armature_obj, "boom_piston_base.R")
parent_obj_to_bone("Piston_Rod_Boom.R", armature_obj, "boom_piston_rod.R")
parent_obj_to_bone("Piston_Base_Boom.L", armature_obj, "boom_piston_base.L")
parent_obj_to_bone("Piston_Rod_Boom.L", armature_obj, "boom_piston_rod.L")

# Pin Cylinders Parenting
def parent_obj_to_mesh(child_name, parent_name):
    child = bpy.data.objects.get(child_name)
    parent = bpy.data.objects.get(parent_name)
    if child and parent:
        w_mat = child.matrix_world.copy()
        child.parent = parent
        child.matrix_parent_inverse = parent.matrix_world.inverted()
        child.matrix_world = w_mat

parent_obj_to_mesh("Cylinder.040", "Base")
parent_obj_to_mesh("Cylinder.010", "Base")
parent_obj_to_mesh("Cylinder.029", "Base")
parent_obj_to_mesh("Cylinder.032", "Base")

parent_obj_to_mesh("Cylinder.027", "Boom")
parent_obj_to_mesh("Cylinder.007", "Boom")

parent_obj_to_mesh("Cylinder.024", "Arm")
parent_obj_to_mesh("Cylinder.023", "Arm")
parent_obj_to_mesh("Cylinder.048", "Arm")

parent_obj_to_mesh("Cylinder.019", "Bucket")
parent_obj_to_mesh("Cylinder", "Bucket")
parent_obj_to_mesh("Cylinder.049", "Linkage_1")

# =============================================================================
# 6. POSE CONSTRAINTS & LIMIT ROTATIONS
# =============================================================================
bpy.context.view_layer.objects.active = armature_obj
bpy.ops.object.mode_set(mode='POSE')
pose_bones = armature_obj.pose.bones

for pb in pose_bones:
    pb.rotation_mode = 'XYZ'

def add_damped_track(pb_name, target_obj_name, track_axis='TRACK_Y'):
    pb = pose_bones.get(pb_name)
    target = bpy.data.objects.get(target_obj_name)
    if pb and target:
        c = pb.constraints.new('DAMPED_TRACK')
        c.target = target
        c.track_axis = track_axis

# Apply Damped Track Constraints
add_damped_track("arm_piston_base", "Target_Arm_Piston_Rod", 'TRACK_Y')
add_damped_track("arm_piston_rod", "Target_Arm_Piston_Base", 'TRACK_Y')

add_damped_track("bucket_piston_base", "Target_Bucket_Piston_Junc", 'TRACK_Y')
add_damped_track("bucket_piston_rod", "Target_Bucket_Piston_Base", 'TRACK_Y')

add_damped_track("boom_piston_base.R", "Target_Boom_Piston_Rod_R", 'TRACK_Y')
add_damped_track("boom_piston_rod.R", "Target_Boom_Piston_Base_R", 'TRACK_Y')

add_damped_track("boom_piston_base.L", "Target_Boom_Piston_Rod_L", 'TRACK_Y')
add_damped_track("boom_piston_rod.L", "Target_Boom_Piston_Base_L", 'TRACK_Y')

# Apply Limit Rotation Constraints
def add_limit_rotation(pb_name, min_x, max_x):
    pb = pose_bones.get(pb_name)
    if pb:
        c = pb.constraints.new('LIMIT_ROTATION')
        c.use_limit_x = True
        c.min_x = math.radians(min_x)
        c.max_x = math.radians(max_x)
        c.use_limit_y = True
        c.min_y = 0
        c.max_y = 0
        c.use_limit_z = True
        c.min_z = 0
        c.max_z = 0
        c.owner_space = 'LOCAL'

add_limit_rotation("boom", -25, 30)
add_limit_rotation("arm", -35, 35)
add_limit_rotation("bucket", -50, 50)

# Base Rotation Limit (Lock X and Y axes, allow Z axis rotation)
pb_base = pose_bones.get("base")
if pb_base:
    c = pb_base.constraints.new('LIMIT_ROTATION')
    c.use_limit_x = True
    c.min_x = 0
    c.max_x = 0
    c.use_limit_y = True
    c.min_y = 0
    c.max_y = 0
    c.use_limit_z = False
    c.owner_space = 'LOCAL'

bpy.ops.object.mode_set(mode='OBJECT')

# =============================================================================
# 7. AUTOMATIC KEYFRAME ANIMATION (FRAMES 1 - 250)
# =============================================================================
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 250

bpy.context.view_layer.objects.active = armature_obj
bpy.ops.object.mode_set(mode='POSE')

if armature_obj.animation_data:
    armature_obj.animation_data_clear()

# Animation Keyframe Sequence Definitions
# Format: (Frame, {bone_name: (rot_x_deg, rot_y_deg, rot_z_deg)})
anim_keyframes = [
    (1,   {"base": (0, 0, 0),   "boom": (0, 0, 0),   "arm": (0, 0, 0),   "bucket": (0, 0, 0)}),
    (30,  {"base": (0, 0, 45),  "boom": (0, 0, 0),   "arm": (0, 0, 0),   "bucket": (0, 0, 0)}),
    (70,  {"base": (0, 0, 45),  "boom": (18, 0, 0),  "arm": (-20, 0, 0), "bucket": (-15, 0, 0)}),
    (110, {"base": (0, 0, 45),  "boom": (-10, 0, 0), "arm": (15, 0, 0),  "bucket": (40, 0, 0)}),
    (150, {"base": (0, 0, 45),  "boom": (22, 0, 0),  "arm": (-10, 0, 0), "bucket": (30, 0, 0)}),
    (190, {"base": (0, 0, -45), "boom": (15, 0, 0),  "arm": (0, 0, 0),   "bucket": (-45, 0, 0)}),
    (220, {"base": (0, 0, -45), "boom": (5, 0, 0),   "arm": (-15, 0, 0), "bucket": (0, 0, 0)}),
    (250, {"base": (0, 0, 0),   "boom": (0, 0, 0),   "arm": (0, 0, 0),   "bucket": (0, 0, 0)})
]

for frame, key_dict in anim_keyframes:
    scene.frame_set(frame)
    for b_name, rot in key_dict.items():
        pb = pose_bones.get(b_name)
        if pb:
            pb.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))
            pb.keyframe_insert(data_path="rotation_euler", frame=frame)

# Apply BEZIER Interpolation to F-Curves
if armature_obj.animation_data and armature_obj.animation_data.action:
    action = armature_obj.animation_data.action
    for fcurve in action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.easing = 'AUTO'

bpy.ops.object.mode_set(mode='OBJECT')
scene.frame_set(1)

print("======================================================================")
print("SUCCESS: Excavator Rigging & Keyframe Animation Completed!")
print("Armature Name    : Excavator_Armature")
print("Animation Timeline: Frames 1 to 250")
print("======================================================================")
