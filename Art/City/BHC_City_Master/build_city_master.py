"""Build the connected Big Head Casino night-city presentation scene.

create it fully 3D and very high end no BS.

This is a visual master scene for the connected city experience. It is
procedural, modular, and exportable; Unreal can replace each block with its
production asset while preserving the composition and circulation plan.
"""
import bpy, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BASE = os.path.join(ROOT, "Art", "City", "BHC_City_Master")
os.makedirs(os.path.join(BASE, "Blender"), exist_ok=True)
os.makedirs(os.path.join(BASE, "Exports"), exist_ok=True)
os.makedirs(os.path.join(BASE, "Previews"), exist_ok=True)
os.makedirs(os.path.join(BASE, "Manifests"), exist_ok=True)

def material(name, color, metallic=0.0, rough=0.5, emission=None, strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1); p.inputs["Metallic"].default_value = metallic; p.inputs["Roughness"].default_value = rough
    if emission:
        if "Emission Color" in p.inputs: p.inputs["Emission Color"].default_value = (*emission, 1)
        if "Emission Strength" in p.inputs: p.inputs["Emission Strength"].default_value = strength
    return m

ASPHALT=material("M_BHC_City_Asphalt",(0.008,0.012,0.02),0.1,0.78); SIDEWALK=material("M_BHC_City_Sidewalk",(0.16,0.17,0.2),0.05,0.72); CONCRETE=material("M_BHC_City_Concrete",(0.06,0.07,0.09),0.1,0.65); GLASS=material("M_BHC_City_SmokedGlass",(0.02,0.045,0.11),0.32,0.12,(0.015,0.05,0.2),1.4); GLASS_BLUE=material("M_BHC_City_BlueGlass",(0.01,0.12,0.3),0.4,0.1,(0.02,0.16,0.8),2.0); DARK=material("M_BHC_City_DarkMetal",(0.02,0.025,0.04),0.82,0.24); GOLD=material("M_BHC_City_Brass",(0.6,0.2,0.035),0.9,0.16); RED=material("M_BHC_City_RedNeon",(0.17,0.001,0.002),0.2,0.25,(1,0.001,0),12); CYAN=material("M_BHC_City_CyanNeon",(0.002,0.05,0.2),0.1,0.24,(0.01,0.25,1),10); PURPLE=material("M_BHC_City_PurpleNeon",(0.03,0.002,0.17),0.1,0.24,(0.2,0.01,1),9); GREEN=material("M_BHC_City_Green",(0.01,0.06,0.025),0.0,0.95); TREE=material("M_BHC_City_Tree",(0.008,0.03,0.012),0.0,0.92); WHITE=material("M_BHC_City_Light",(0.7,0.7,0.55),0.0,0.2,(1,0.5,0.18),5)

def apply(o,m): o.data.materials.append(m); return o
def cube(name, loc, dims, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); apply(o,m)
    if bevel:
        b=o.modifiers.new("BHC_Edge", "BEVEL"); b.width=bevel; b.segments=3
    return o
def cyl(name, loc, radius, depth, m, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc); o=bpy.context.object; o.name=name; apply(o,m); return o
def sphere(name, loc, scale, m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); apply(o,m); return o
def text(name, body, loc, size, m, rot=(math.pi/2,0,0)):
    c=bpy.data.curves.new(name+"_Curve","FONT"); c.body=body; c.align_x="CENTER"; c.size=size; c.extrude=0.05; c.bevel_depth=0.01; o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=rot; apply(o,m); return o
def look(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,typ,loc,energy,color,size=2,target=(0,0,0)):
    d=bpy.data.lights.new(name,typ); d.energy=energy; d.color=color
    if typ=='AREA': d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); bpy.context.collection.objects.link(o); o.location=loc; look(o,target); return o

def building(name,x,y,w,d,h,glass=GLASS,accent=GOLD,sign=None):
    cube(name+"_Core",(x,y,h/2),(w,d,h),DARK,0.35)
    cube(name+"_Crown",(x,y,h+0.7),(w*0.84,d*0.84,1.4),accent,0.18)
    # vertical window modules and horizontal floor bands
    for floor in range(max(1,min(8,int(h//4)))):
        z=2.0+floor*4.0
        for col in range(max(1,min(5,int(w//4)))):
            xx=x-w/2+2.0+col*4.0
            cube(f"{name}_Window_{floor}_{col}",(xx,y-d/2-0.025,z),(2.5,0.05,2.0),glass,0.05)
            cube(f"{name}_WindowBack_{floor}_{col}",(xx,y+d/2+0.025,z),(2.5,0.05,2.0),glass,0.05)
        cube(f"{name}_Band_{floor}",(x,y,z-1.4),(w*0.92,0.12,0.12),accent,0.03)
    if sign: text(name+"_Sign",sign,(x,y-d/2-0.08,h*0.55),min(1.5,w/len(sign)*0.5),RED)
    return h

def street_lamp(x,y):
    cyl(f"SM_BHC_LampPole_{x}_{y}",(x,y,4.8),0.09,9.6,DARK,24); cube(f"SM_BHC_LampArm_{x}_{y}",(x+0.7,y,9.25),(1.0,0.07,0.07),GOLD,0.03); sphere(f"SM_BHC_Lamp_{x}_{y}",(x+1.55,y,9.25),(0.18,0.18,0.12),WHITE)

def street_tree(x,y):
    cyl(f"SM_BHC_TreeTrunk_{x}_{y}",(x,y,1.3),0.22,2.6,DARK,24); sphere(f"SM_BHC_TreeCrown_{x}_{y}",(x,y,3.1),(1.25,1.25,1.6),TREE)

def neon_billboard(name,loc,dims,body,m):
    cube(name+"_Panel",loc,dims,DARK,0.12); text(name+"_Text",body,(loc[0],loc[1]-dims[1]/2-0.08,loc[2]),max(0.5,dims[0]/max(1,len(body))*0.55),m)

def build():
    print("BHC_CITY_BUILD_START", flush=True)
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    # city ground and primary boulevard.
    cube("SM_BHC_CITY_Ground",(0,0,-0.5),(220,220,1),ASPHALT,0.1)
    cube("SM_BHC_CITY_Boulevard_EW",(0,0,0.05),(220,12,0.12),ASPHALT,0.02)
    cube("SM_BHC_CITY_Boulevard_NS",(0,0,0.06),(12,220,0.12),ASPHALT,0.02)
    for x in range(-210,211,15): cube("SM_BHC_CITY_LaneDash_EW",(x,0,0.18),(5.0,0.14,0.03),GOLD,0.01)
    for y in range(-210,211,15): cube("SM_BHC_CITY_LaneDash_NS",(0,y,0.18),(0.14,5.0,0.03),GOLD,0.01)
    for s in (-1,1):
        cube("SM_BHC_CITY_Sidewalk_EW",(0,s*16,0.25),(220,2.6,0.25),SIDEWALK,0.1); cube("SM_BHC_CITY_Sidewalk_NS",(s*16,0,0.25),(2.6,220,0.25),SIDEWALK,0.1)
    for v in range(-180,181,30):
        for s in (-1,1): street_lamp(v,s*18); street_lamp(s*18,v)
    for v in range(-180,181,45): street_tree(v,22); street_tree(-22,v)
    print("BHC_CITY_ROADS_DONE", flush=True)

    # Casino district centerpiece with a readable silhouette.
    print("BHC_CITY_BUILDING_CASINO", flush=True)
    building("BHC_CasinoTower",0,42,54,30,42,GLASS_BLUE,GOLD,"BIG HEAD CASINO")
    print("BHC_CITY_BUILDING_CASINO_DONE", flush=True)
    cube("BHC_CasinoPodium",(0,30,6),(48,18,12),DARK,0.45); cube("BHC_CasinoEntrance",(0,20.7,5),(18,1.1,8),GLASS,0.15); text("BHC_CasinoEntranceSign","BIG HEAD CASINO",(0,20.0,8),1.3,RED)
    for x in (-19,-10,10,19): cube("BHC_CasinoPillar",(x,20,5),(0.7,1.0,10),GOLD,0.12)
    # surrounding connected neighborhoods and landmarks.
    building("BHC_Hotel",70,42,34,24,34,GLASS,GOLD,"THE GRAND")
    building("BHC_VIPTower",-70,45,28,24,29,GLASS,RED,"VIP")
    building("BHC_EquipmentShop",65,-45,28,22,16,GLASS,GOLD,"EQUIPMENT")
    building("BHC_ServiceDistrict",-65,-45,38,26,20,GLASS,CYAN,"SERVICE")
    building("BHC_CrewGarage",0,-74,42,30,15,GLASS,GOLD,"CREW GARAGE")
    for x,y,w,d,h in [(-118,85,22,20,28),(-88,95,30,18,52),(112,88,26,20,44),(90,-86,24,18,32),(-105,-82,22,18,25),(112,-20,20,18,21),(55,105,20,18,26),(-48,-110,30,18,37)]: building("BHC_DistrictBlock",x,y,w,d,h,GLASS, [GOLD,RED,CYAN,PURPLE][abs(x+y)%4])
    print("BHC_CITY_BUILDINGS_DONE", flush=True)

    # Raised transit bridge and rooftop route.
    cube("SM_BHC_TransitBridge",(0,-118,17),(170,4,1.2),CONCRETE,0.18); cube("SM_BHC_TransitBridgeTrim",(0,-113.7,19),(170,0.12,0.22),RED,0.03)
    for x in range(-160,161,16): cube("SM_BHC_BridgePillar",(x,-118,8),(0.45,1.0,8),DARK,0.08)
    neon_billboard("BHC_Billboard_WinBig",(-92,15,15),(24,0.6,8),"WIN BIG",RED)
    neon_billboard("BHC_Billboard_Midnight",(94,15,14),(22,0.6,7),"MIDNIGHT",PURPLE)
    neon_billboard("BHC_Billboard_Crew",(0,-92,11),(30,0.6,8),"CREW UP",CYAN)

    # cars and plaza dressing create scale and readable circulation.
    for i,(x,y) in enumerate([(-28,8),(27,-8),(33,18),(-34,-18)]):
        cube(f"SM_BHC_TrafficCar_{i}_Body",(x,y,0.9),(2.6,1.05,0.55),DARK,0.18); cube(f"SM_BHC_TrafficCar_{i}_Roof",(x,y,1.45),(1.25,0.85,0.42),GLASS,0.15)
        for wx in (-1.7,1.7):
            for wy in (-0.92,0.92): cyl(f"SM_BHC_TrafficCar_{i}_Wheel",(x+wx,y+wy,0.45),0.4,0.2,DARK,24).rotation_euler[0]=math.pi/2
    # city lighting.
    light("BHC_CityKey","AREA",(0,-80,120),65000,(1.0,0.32,0.12),75,(0,20,0)); light("BHC_CityFill","AREA",(-130,40,100),52000,(0.04,0.15,1.0),70,(0,30,15)); light("BHC_CityRim","AREA",(130,80,110),58000,(0.45,0.05,1.0),65,(0,30,20))
    for x,y,c in [(0,20,(1,0.01,0)),(0,-90,(0.01,0.18,1)),(-92,14,(1,0.01,0)),(94,14,(0.3,0.01,1))]: light("BHC_NeonPool","POINT",(x,y,5),3200,c,2)
    for x,y in [(0,42),(70,42),(-70,45),(65,-45),(-65,-45),(0,-74),(-118,85),(-88,95),(112,88),(90,-86),(-105,-82),(112,-20),(55,105),(-48,-110)]:
        light("BHC_BuildingUplight","POINT",(x,y-8,8),5200,(0.12,0.2,1.0),4)
    print("BHC_CITY_LIGHTS_DONE", flush=True)
    # camera and world.
    bpy.ops.object.camera_add(location=(158,-178,118)); cam=bpy.context.object; cam.name="CAM_BHC_CityHero"; cam.data.lens=42; look(cam,(0,18,22)); bpy.context.scene.camera=cam
    world=bpy.context.scene.world or bpy.data.worlds.new("BHC_CityWorld"); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.004,0.008,0.035,1); world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.42
    s=bpy.context.scene; s.render.engine="BLENDER_EEVEE" if "BLENDER_EEVEE" in s.render.bl_rna.properties["engine"].enum_items else "BLENDER_EEVEE_NEXT"; s.render.resolution_x=1280; s.render.resolution_y=720; s.render.resolution_percentage=100; s.render.image_settings.file_format="PNG"; s.render.filepath=os.path.join(BASE,"Previews","BHC_City_Master_Hero.png")
    try: s.view_settings.look="AgX - Medium High Contrast"
    except Exception: pass
    s["BHC_AssetID"]="BHC_CITY_MASTER_NIGHT_01"; s["BHC_Grid"]="20x20 authoring grid; this scene presents the connected central district"; s["BHC_Units"]="1 Blender unit = 1 meter"
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,"Blender","BHC_City_Master_Night.blend")); print("BHC_CITY_SAVED", flush=True); bpy.ops.render.render(write_still=True); print("BHC_CITY_RENDERED", flush=True); bpy.ops.export_scene.gltf(filepath=os.path.join(BASE,"Exports","BHC_CITY_MASTER_NIGHT.glb"),export_format="GLB",export_materials="EXPORT"); print("BHC_CITY_EXPORTED", flush=True)
    with open(os.path.join(BASE,"Manifests","BHC_CITY_MASTER_NIGHT_manifest.json"),"w",encoding="utf8") as f:
        import json; json.dump({"asset_id":"BHC_CITY_MASTER_NIGHT_01","source":"Art/City/BHC_City_Master/Blender/BHC_City_Master_Night.blend","export":"Art/City/BHC_City_Master/Exports/BHC_CITY_MASTER_NIGHT.glb","preview":"Art/City/BHC_City_Master/Previews/BHC_City_Master_Hero.png","scope":"Connected central city presentation scene with casino district, hotel, VIP tower, service district, crew garage, bridge, streets, street furniture, lighting, and landmarks","status":{"blender_rendered":True,"glb_exported":True,"unreal_imported":False,"unreal_streamed":False},"provenance":"original procedural geometry and branding"},f,indent=2)
    with open(os.path.join(BASE,"Manifests","BHC_CITY_MASTER_NIGHT_Handoff.md"),"w",encoding="utf8") as f: f.write('# BHC city master handoff\n\nThis is a connected central-city visual master scene built as modular 3D geometry: casino centerpiece, hotel and VIP tower, equipment and service districts, crew garage, street grid, transit bridge, lamps, trees, traffic silhouettes, and original neon landmarks. It is an art direction and assembly source for Unreal streaming.\n\nThe 400 km² target remains a 20x20 streamed authoring grid. This batch provides the premium central district composition and does not claim every tile is authored. Unreal import, collision, Nanite/LOD review, navmesh, streaming cells, and gameplay integration remain outstanding.\n')

if __name__=='__main__': build()
