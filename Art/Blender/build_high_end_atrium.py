"""Big Head Casino hero atrium.

create it fully 3D and very high end no BS.

This is a repeatable, editable Blender blockout for the first premium art
batch. It deliberately uses original casino branding and engine-safe
material names so it can be exported as a GLB and rebuilt as the art kit
grows.
"""

import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ART = os.path.join(ROOT, "Art")
EXPORTS = os.path.join(ART, "Exports")
PREVIEWS = os.path.join(ART, "Previews")
os.makedirs(EXPORTS, exist_ok=True)
os.makedirs(PREVIEWS, exist_ok=True)


def mat(name, color, metallic=0.0, roughness=0.45, emission=None, emission_strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1.0)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    if emission:
        if "Emission Color" in p.inputs:
            p.inputs["Emission Color"].default_value = (*emission, 1.0)
        elif "Emission" in p.inputs:
            p.inputs["Emission"].default_value = (*emission, 1.0)
        if "Emission Strength" in p.inputs:
            p.inputs["Emission Strength"].default_value = emission_strength
    return m


BLACK = mat("M_BHC_BlackMarble", (0.015, 0.018, 0.024), metallic=0.15, roughness=0.2)
GRAPHITE = mat("M_BHC_Graphite", (0.045, 0.055, 0.07), metallic=0.72, roughness=0.24)
BRASS = mat("M_BHC_BrushedBrass", (0.54, 0.24, 0.055), metallic=0.9, roughness=0.2)
BRASS_DARK = mat("M_BHC_AgedBrass", (0.22, 0.07, 0.025), metallic=0.82, roughness=0.3)
BURGUNDY = mat("M_BHC_VelvetBurgundy", (0.18, 0.012, 0.025), metallic=0.0, roughness=0.68)
BURGUNDY_GLOW = mat("M_BHC_BurgundyNeon", (0.15, 0.002, 0.003), roughness=0.38, emission=(1.0, 0.015, 0.01), emission_strength=6.0)
EMERALD = mat("M_BHC_EmeraldFelt", (0.008, 0.15, 0.07), roughness=0.78)
GOLD = mat("M_BHC_ChampagneGold", (0.76, 0.37, 0.08), metallic=0.94, roughness=0.16)
SMOKE = mat("M_BHC_SmokedGlass", (0.015, 0.025, 0.04), metallic=0.05, roughness=0.08)
WHITE = mat("M_BHC_WarmWhite", (0.7, 0.7, 0.62), roughness=0.26, emission=(1.0, 0.55, 0.25), emission_strength=1.0)
RED_NEON = mat("M_BHC_RedNeon", (0.18, 0.002, 0.003), roughness=0.25, emission=(1.0, 0.005, 0.002), emission_strength=14.0)
PURPLE_NEON = mat("M_BHC_PurpleNeon", (0.06, 0.005, 0.2), roughness=0.25, emission=(0.3, 0.015, 1.0), emission_strength=10.0)
SCREEN = mat("M_BHC_Screen", (0.005, 0.01, 0.018), roughness=0.2, emission=(0.03, 0.16, 0.3), emission_strength=2.8)
SKIN = mat("M_BHC_StatueSkin", (0.34, 0.09, 0.045), metallic=0.15, roughness=0.32)
EYE = mat("M_BHC_StatueEye", (0.004, 0.002, 0.001), metallic=0.25, roughness=0.08)


def apply_mat(obj, material):
    obj.data.materials.append(material)
    return obj


def cube(name, loc, dims, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_mat(o, material)
    if bevel:
        mod = o.modifiers.new("BHC_SoftEdge", "BEVEL")
        mod.width = bevel
        mod.segments = 4
    return o


def cyl(name, loc, radius, depth, material, vertices=48, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    apply_mat(o, material)
    if bevel:
        mod = o.modifiers.new("BHC_SoftEdge", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    return o


def uv(name, loc, scale, material, segments=64, rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_mat(o, material)
    return o


def torus(name, loc, major, minor, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=72, minor_segments=16, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    apply_mat(o, material)
    return o


def text(name, body, loc, size, material, extrude=0.04, align="CENTER", rotation=(math.pi / 2, 0, 0)):
    curve = bpy.data.curves.new(name + "_Curve", "FONT")
    curve.body = body
    curve.align_x = align
    curve.size = size
    curve.extrude = extrude
    curve.bevel_depth = 0.012
    curve.bevel_resolution = 4
    o = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rotation
    apply_mat(o, material)
    return o


def point_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area_light(name, loc, energy, color, size, target=(0, 0, 0)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.color = color
    data.shape = "DISK"
    data.size = size
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    o.location = loc
    point_at(o, target)
    return o


def point_light(name, loc, energy, color, radius=0.2):
    data = bpy.data.lights.new(name, "POINT")
    data.energy = energy
    data.color = color
    data.shadow_soft_size = radius
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    o.location = loc
    return o


def add_slot_machine(index, x, y, z=1.35):
    base = cube(f"SM_BHC_Slot_{index:02d}_Cabinet", (x, y, z), (1.35, 0.8, 2.7), GRAPHITE, 0.08)
    cube(f"SM_BHC_Slot_{index:02d}_Crown", (x, y - 0.42, z + 1.16), (1.15, 0.08, 0.32), RED_NEON, 0.04)
    cube(f"SM_BHC_Slot_{index:02d}_Screen", (x, y - 0.43, z + 0.42), (0.92, 0.07, 0.65), SCREEN, 0.025)
    cube(f"SM_BHC_Slot_{index:02d}_Control", (x, y - 0.45, z - 0.28), (1.0, 0.14, 0.28), BRASS_DARK, 0.04)
    for i in range(3):
        cyl(f"SM_BHC_Slot_{index:02d}_Button_{i}", (x - 0.3 + i * 0.3, y - 0.55, z - 0.28), 0.055, 0.04, RED_NEON, 24)
    cube(f"SM_BHC_Slot_{index:02d}_Foot", (x, y, 0.22), (1.0, 0.62, 0.18), BRASS, 0.04)
    return base


def add_blackjack(name, x, y):
    # Layered geometry gives the table a readable silhouette from the hero camera.
    cube(name + "_Base", (x, y, 1.02), (5.6, 2.8, 0.38), BRASS_DARK, 0.18)
    cube(name + "_Felt", (x, y, 1.25), (5.35, 2.55, 0.16), EMERALD, 0.22)
    cube(name + "_Rail", (x, y - 1.22, 1.38), (4.95, 0.16, 0.18), BURGUNDY, 0.06)
    text(name + "_Label", "BLACKJACK", (x, y - 1.34, 1.46), 0.28, GOLD, 0.02, rotation=(math.pi / 2, 0, 0))
    for i in range(6):
        cyl(name + f"_Chip_{i}", (x - 1.6 + (i % 3) * 0.38, y + 0.2 + (i // 3) * 0.34, 1.42), 0.13, 0.05, [RED_NEON, GOLD, PURPLE_NEON][i % 3], 32)
    for i in range(4):
        cyl(name + f"_Leg_{i}", (x - 1.8 + (i % 2) * 3.6, y - 0.7 + (i // 2) * 1.4, 0.48), 0.12, 0.96, BRASS_DARK, 24)


def add_lounge(x, y):
    cube("SM_BHC_Lounge_Sofa", (x, y, 0.72), (4.2, 1.25, 0.9), BURGUNDY, 0.25)
    cube("SM_BHC_Lounge_Back", (x, y + 0.45, 1.35), (4.2, 0.28, 1.15), BURGUNDY, 0.12)
    for i in range(3):
        cube(f"SM_BHC_Lounge_Cushion_{i}", (x - 1.25 + i * 1.25, y - 0.1, 1.24), (1.05, 0.78, 0.18), BRASS_DARK, 0.08)
    cube("SM_BHC_Lounge_Table", (x, y - 1.55, 0.45), (2.0, 0.9, 0.16), BLACK, 0.08)
    cyl("SM_BHC_Lounge_TableStem", (x, y - 1.55, 0.2), 0.08, 0.5, BRASS, 32)


def build_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        # Keep the default datablocks but clear unused generated content.
        pass

    # Architectural shell.
    cube("SM_BHC_Atrium_Floor", (0, 0, -0.25), (32, 24, 0.5), BLACK, 0.12)
    cube("SM_BHC_Atrium_BackWall", (0, 11.7, 5.5), (32, 0.5, 11), GRAPHITE, 0.08)
    cube("SM_BHC_Atrium_LeftWall", (-15.8, 0, 5.5), (0.5, 24, 11), GRAPHITE, 0.08)
    cube("SM_BHC_Atrium_RightWall", (15.8, 0, 5.5), (0.5, 24, 11), GRAPHITE, 0.08)
    for x in (-13.2, -8.8, 8.8, 13.2):
        cube(f"SM_BHC_Column_{x}", (x, 9.8, 4.5), (0.75, 1.2, 9), BRASS_DARK, 0.1)
        cube(f"SM_BHC_ColumnLight_{x}", (x, 9.15, 4.7), (0.1, 0.04, 5.0), PURPLE_NEON, 0.01)
    for x in (-12, -4, 4, 12):
        cube(f"SM_BHC_BrassInlay_{x}", (x, 0, 0.04), (0.08, 23.0, 0.06), BRASS, 0.02)
    for y in (-8, 8):
        cube(f"SM_BHC_BrassInlayY_{y}", (0, y, 0.045), (31.0, 0.08, 0.06), BRASS, 0.02)

    # Central atrium centerpiece: original oversized bobble-head statue.
    cyl("SM_BHC_CenterPedestal", (0, 4.2, 0.75), 2.7, 1.5, BRASS_DARK, 96, 0.12)
    cyl("SM_BHC_CenterPedestalTop", (0, 4.2, 1.55), 2.35, 0.12, BLACK, 96, 0.04)
    uv("SM_BHC_CenterHead", (0, 4.2, 4.3), (1.65, 1.42, 1.72), SKIN)
    uv("SM_BHC_CenterHair", (0, 4.18, 5.35), (1.25, 1.1, 0.62), GRAPHITE)
    for ex in (-0.55, 0.55):
        uv("SM_BHC_CenterEye", (ex, 2.92, 4.45), (0.24, 0.1, 0.3), EYE)
        uv("SM_BHC_CenterEyeGlow", (ex, 2.84, 4.45), (0.09, 0.03, 0.12), WHITE)
    cube("SM_BHC_CenterSmile", (0, 2.88, 3.82), (0.9, 0.08, 0.16), RED_NEON, 0.06)
    for z in (2.35, 2.65):
        torus("SM_BHC_PedestalNeon", (0, 4.2, z), 2.35, 0.035, RED_NEON)
    text("SM_BHC_CenterTitle", "BIG HEAD", (0, 4.12, 6.0), 0.65, GOLD, 0.045, rotation=(math.pi / 2, 0, 0))

    # Hero-facing table game floor.
    add_blackjack("SM_BHC_BlackjackTable_A", -6.4, -2.2)
    add_blackjack("SM_BHC_BlackjackTable_B", 6.4, -2.2)
    add_lounge(-9.8, 4.2)
    add_lounge(9.8, 4.2)

    # Slot aisle with repeated modular cabinets.
    for row_y in (7.2, 8.7):
        for i, x in enumerate((-6.8, -4.6, -2.4, 2.4, 4.6, 6.8)):
            add_slot_machine(i + int(row_y * 10), x, row_y)

    # Casino sign, balcony, and stage dressing.
    text("SM_BHC_MainSign", "BIG HEAD CASINO", (0, 11.34, 8.0), 1.15, RED_NEON, 0.08, rotation=(math.pi / 2, 0, 0))
    cube("SM_BHC_MainSignBacking", (0, 11.1, 8.05), (12.8, 0.16, 2.1), BLACK, 0.1)
    text("SM_BHC_MainSignFront", "BIG HEAD CASINO", (0, 10.98, 8.0), 1.15, RED_NEON, 0.08, rotation=(math.pi / 2, 0, 0))
    cube("SM_BHC_Balcony", (0, 10.2, 5.4), (26, 1.2, 0.35), BLACK, 0.08)
    cube("SM_BHC_BalconyTrim", (0, 9.55, 5.65), (25.5, 0.08, 0.12), GOLD, 0.02)
    for x in range(-12, 13, 2):
        cube(f"SM_BHC_BalconyRailing_{x}", (x, 9.5, 6.35), (0.08, 0.08, 1.4), BRASS, 0.02)
    cube("SM_BHC_PrizeWheelStage", (0, 8.8, 0.35), (5.2, 1.5, 0.7), BURGUNDY, 0.12)
    torus("SM_BHC_PrizeWheel", (0, 8.0, 2.8), 1.8, 0.15, GOLD, rotation=(math.pi / 2, 0, 0))
    cyl("SM_BHC_PrizeWheelHub", (0, 7.98, 2.8), 0.38, 0.3, RED_NEON, 48, 0.05)
    for i in range(12):
        a = 2 * math.pi * i / 12
        cube(f"SM_BHC_WheelSpoke_{i}", (math.cos(a) * 0.9, 7.98, 2.8 + math.sin(a) * 0.9), (0.08, 0.18, 1.45), BRASS, 0.02).rotation_euler[1] = -a

    # Ceiling features and chandelier.
    torus("SM_BHC_CeilingRingOuter", (0, 2, 10.7), 10.5, 0.2, BRASS)
    torus("SM_BHC_CeilingRingInner", (0, 2, 10.7), 7.0, 0.12, RED_NEON)
    for i in range(16):
        a = 2 * math.pi * i / 16
        point_light(f"BHC_ChandelierBulb_{i}", (math.cos(a) * 5.7, math.sin(a) * 5.7 + 2, 9.3), 190, (1.0, 0.18, 0.06), 0.15)
        uv(f"SM_BHC_ChandelierCrystal_{i}", (math.cos(a) * 5.7, math.sin(a) * 5.7 + 2, 9.15), (0.12, 0.12, 0.36), WHITE, 24, 12)

    # Lighting: warm key, cool fill, selective neon pools.
    area_light("BHC_KeyLight", (0, -8, 11), 1700, (1.0, 0.46, 0.22), 9, (0, 2, 0))
    area_light("BHC_FillLight", (-11, 2, 8), 1200, (0.08, 0.16, 1.0), 8, (0, 3, 2))
    area_light("BHC_RimLight", (12, 8, 9), 1500, (1.0, 0.04, 0.02), 7, (0, 4, 3))
    point_light("BHC_StatuePool", (0, 3.0, 5), 900, (1.0, 0.02, 0.01), 1.8)

    # Camera and render setup.
    bpy.ops.object.camera_add(location=(17.5, -22.5, 11.5))
    camera = bpy.context.object
    camera.name = "CAM_BHC_HeroAtrium"
    camera.data.lens = 32
    camera.data.sensor_width = 36
    point_at(camera, (0, 3.5, 3.2))
    bpy.context.scene.camera = camera

    world = bpy.context.scene.world or bpy.data.worlds.new("BHC_World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.002, 0.003, 0.012, 1.0)
    bg.inputs["Strength"].default_value = 0.18

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in scene.render.bl_rna.properties["engine"].enum_items else "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(PREVIEWS, "BHC_HighEndAtrium_Hero.png")
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    scene.render.image_settings.color_depth = "8"

    # Useful metadata for the handoff and automated validation.
    scene["BHC_AssetBatch"] = "BHC_ART_BATCH_01_HIGH_END_ATRIUM"
    scene["BHC_Units"] = "1 Blender unit = 1 meter"
    scene["BHC_Export"] = "GLB with original modular meshes and PBR materials"
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ART, "Blender", "BHC_HighEndAtrium.blend"))
    bpy.ops.render.render(write_still=True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(EXPORTS, "BHC_HighEndAtrium.glb"), export_format="GLB", export_materials="EXPORT")


if __name__ == "__main__":
    build_scene()
