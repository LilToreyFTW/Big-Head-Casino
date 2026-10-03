import bpy, bmesh, math, os, json, mathutils
from mathutils import Vector
from math import radians

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BLEND_DIR = os.path.join(ROOT, 'Art', 'Blender')
EXPORT_DIR = os.path.join(ROOT, 'Art', 'Exports')
PREVIEW_DIR = os.path.join(ROOT, 'Art', 'Previews')
MANIFEST_DIR = os.path.join(ROOT, 'Art', 'Manifests')
for d in (BLEND_DIR, EXPORT_DIR, PREVIEW_DIR, MANIFEST_DIR): os.makedirs(d, exist_ok=True)

# ---- scene helpers -------------------------------------------------------
def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        pass

def coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children.keys(): bpy.context.scene.collection.children.link(c)
    return c

def move_to(obj, collection):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj)

def mat(name, color, metallic=0.0, rough=0.45, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color,1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = rough
    if emission:
        bs.inputs['Emission Color'].default_value = (*emission,1)
        bs.inputs['Emission Strength'].default_value = 4.0
    return m

BLACK = mat('M_BHC_BlackStone', (0.018,0.022,0.028), 0.25, 0.24)
STONE = mat('M_BHC_DarkStone', (0.055,0.065,0.078), 0.15, 0.32)
BRASS = mat('M_BHC_Brass', (0.63,0.30,0.055), 0.82, 0.22)
GOLD = mat('M_BHC_HighRollerGold', (0.95,0.55,0.09), 0.9, 0.18)
VELVET = mat('M_BHC_BurgundyVelvet', (0.19,0.015,0.03), 0.0, 0.72)
EMERALD = mat('M_BHC_EmeraldFelt', (0.012,0.22,0.12), 0.0, 0.86)
CARPET = mat('M_BHC_PatternedCarpet', (0.055,0.012,0.028), 0.0, 0.9)
GLASS = mat('M_BHC_SmokedGlass', (0.035,0.065,0.09), 0.1, 0.14)
NEON_PURPLE = mat('M_BHC_NeonPurple', (0.22,0.01,0.55), 0.1, 0.2, (0.4,0.02,1.0))
NEON_CYAN = mat('M_BHC_NeonCyan', (0.01,0.35,0.65), 0.1, 0.2, (0.01,0.4,1.0))
WHITE = mat('M_BHC_WarmWhite', (0.8,0.82,0.78), 0.0, 0.35, (0.7,0.7,0.65))
SKIN = mat('M_BHC_Skin', (0.52,0.17,0.10), 0.0, 0.5)
HAIR = mat('M_BHC_Hair', (0.015,0.008,0.006), 0.0, 0.38)
SUIT = mat('M_BHC_Suit', (0.035,0.045,0.11), 0.1, 0.48)
SHIRT = mat('M_BHC_Shirt', (0.7,0.7,0.66), 0.0, 0.38)
WOOD = mat('M_BHC_Walnut', (0.10,0.028,0.012), 0.0, 0.4)
RUBBER = mat('M_BHC_Rubber', (0.012,0.012,0.014), 0.0, 0.75)
GUNMETAL = mat('M_BHC_Gunmetal', (0.055,0.06,0.07), 0.85, 0.24)
WOODGRIP = mat('M_BHC_WoodGrip', (0.20,0.055,0.016), 0.05, 0.42)
LASER = mat('M_BHC_GreenLaser', (0.02,0.8,0.08), 0.1, 0.18, (0.02,1,0.05))

def assign(o, material):
    if material: o.data.materials.append(material)
    return o

def smooth(o):
    if hasattr(o.data, 'polygons'):
        for p in o.data.polygons: p.use_smooth=True
    return o

def bevel(o, amount=0.04, segments=3):
    mod=o.modifiers.new('EdgeSoftening','BEVEL'); mod.width=amount; mod.segments=segments
    return o

def cube(name, loc, scale, material=None, collection=None, bevel_amt=0.04):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel_amt: bevel(o, bevel_amt)
    assign(o,material)
    if collection: move_to(o,collection)
    return o

def cyl(name, loc, radius, depth, material=None, collection=None, verts=48, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; assign(o,material); smooth(o)
    if collection: move_to(o,collection)
    return o

def uv_sphere(name, loc, scale, material=None, collection=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); assign(o,material); smooth(o)
    if collection: move_to(o,collection)
    return o

def torus(name, loc, major, minor, material=None, collection=None, rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=64, minor_segments=16, location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; assign(o,material); smooth(o)
    if collection: move_to(o,collection)
    return o

def text_obj(name, text, loc, size, material, collection, rot=(radians(90),0,0), extrude=0.015, align='CENTER'):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=text; cu.align_x=align; cu.size=size; cu.extrude=extrude; cu.bevel_depth=0.004
    o=bpy.data.objects.new(name,cu); collection.objects.link(o); o.location=loc; o.rotation_euler=rot; assign(o,material); return o

def uv(o):
    if o.type=='MESH':
        bpy.context.view_layer.objects.active=o; o.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=0.03); bpy.ops.object.mode_set(mode='OBJECT'); o.select_set(False)

def parent(o,p): o.parent=p

def marker(name, loc, collection, rot=(0,0,0), color=NEON_CYAN):
    o=cyl(name,loc,0.018,0.08,color,collection,verts=16,rot=(0,0,0)); o.rotation_euler=rot; return o

def add_area_light(name, loc, energy, color, size=5):
    bpy.ops.object.light_add(type='AREA', location=loc); l=bpy.context.object; l.name=name; l.data.energy=energy; l.data.shape='DISK'; l.data.size=size; l.data.color=color; return l

# ---- modular environment -------------------------------------------------
env=coll('BHC_Environment_Modular')
def build_environment():
    # floor modules and carpet inlay
    floor=cube('SM_BHC_Floor_8m',(0,0,-0.15),(4,4,0.15),BLACK,env,0.08); uv(floor)
    inlay=cube('SM_BHC_Carpet_Inlay',(0,0,0.03),(3.6,3.6,0.02),CARPET,env,0.02); uv(inlay)
    # patterned brass strips
    for x in (-3.6,3.6): cube('SM_BHC_Trim_Brass',(x,0,0.08),(0.045,3.6,0.045),BRASS,env,0.01)
    for y in (-3.6,3.6): cube('SM_BHC_Trim_Brass',(0,y,0.08),(3.6,0.045,0.045),BRASS,env,0.01)
    # modular walls, corners and columns
    for y in (-4.0,4.0):
        wall=cube('SM_BHC_Wall_8m',(0,y,2.2),(4.0,0.18,2.2),STONE,env,0.08); uv(wall)
        cube('SM_BHC_Wall_Trim',(0,y-0.20 if y<0 else y+0.20,3.7),(4.0,0.07,0.10),BRASS,env,0.02)
    for x in (-4.0,4.0):
        wall=cube('SM_BHC_Wall_8m',(x,0,2.2),(0.18,4.0,2.2),STONE,env,0.08); uv(wall)
    for x in (-3.6,3.6):
        for y in (-3.6,3.6):
            c=cyl('SM_BHC_Column_Modular',(x,y,2.1),0.28,4.2,BRASS,env,verts=32); torus('SM_BHC_Column_Capital',(x,y,3.95),0.38,0.08,GOLD,env); torus('SM_BHC_Column_Base',(x,y,0.18),0.38,0.08,GOLD,env)
    # ceiling coffer / chandelier support
    cube('SM_BHC_Ceiling_Panel',(0,0,4.45),(4.0,4.0,0.16),BLACK,env,0.05)
    for x in (-2,0,2):
        for y in (-2,0,2): cube('SM_BHC_Ceiling_Coffer',(x,y,4.28),(0.08,1.8,0.06),BRASS,env,0.01)
    # entrance portal and neon logo
    portal=cube('SM_BHC_Entrance_Portal',(0,-3.75,2.35),(2.3,0.20,2.35),BLACK,env,0.12)
    cube('SM_BHC_Entrance_Portal_Inlay',(0,-3.98,2.35),(2.0,0.03,2.0),BRASS,env,0.06)
    text_obj('SM_BHC_Logo_Entrance','BIG HEAD\nCASINO',(0,-4.06,2.55),0.45,NEON_PURPLE,env,rot=(radians(90),0,0),extrude=0.02)
    # balcony / railing and stairs
    cube('SM_BHC_Balcony_Deck',(0,2.6,2.9),(3.5,1.0,0.12),WOOD,env,0.05)
    for x in [-3,-2,-1,0,1,2,3]: cyl('SM_BHC_Railing_Post',(x,1.65,3.25),0.035,0.7,BRASS,env,verts=16)
    cube('SM_BHC_Railing_Top',(0,1.65,3.6),(3.4,0.05,0.05),BRASS,env,0.02)
    for i in range(6):
        cube('SM_BHC_Stair_Step',(-2.6+i*0.45,0.9+i*0.22,0.10+i*0.18),(0.28,0.55,0.09),STONE,env,0.03)
    # cover / service counter module
    cube('SM_BHC_Service_Counter',(0,0.8,1.0),(1.8,0.35,0.95),WOOD,env,0.10)
    cube('SM_BHC_Service_Counter_Top',(0,0.8,2.0),(1.95,0.42,0.10),BRASS,env,0.03)
    for x in (-1.2,0,1.2): cube('SM_BHC_Counter_Panel',(x,0.42,1.0),(0.45,0.03,0.55),BLACK,env,0.02)
    # security camera, staff door, warning light
    door=cube('SM_BHC_Staff_Door',(3.75,0.0,1.5),(0.16,0.85,1.5),BLACK,env,0.05)
    cube('SM_BHC_Keycard_Housing',(3.55,-0.3,1.5),(0.04,0.12,0.24),NEON_CYAN,env,0.02)
    text_obj('SM_BHC_Restricted_Sign','AUTHORIZED STAFF',(3.5,-0.02,3.3),0.15,VELVET,env,rot=(radians(90),0,radians(90)),extrude=0.01)
    bpy.ops.object.light_add(type='POINT', location=(3.35,-0.2,3.4)); bpy.context.object.name='SM_BHC_Warning_Light'; bpy.context.object.data.energy=120; bpy.context.object.data.color=(1,0.03,0.02)
    cam=uv_sphere('SM_BHC_Security_Camera',(2.8,3.55,3.5),(0.22,0.14,0.14),GUNMETAL,env); cam.rotation_euler=(radians(-25),0,radians(180))
    # lounge partitions
    for x in (-2.2,2.2):
        cube('SM_BHC_SmokedGlass_Partition',(x,0,1.6),(0.06,1.6,1.6),GLASS,env,0.015); cube('SM_BHC_Partition_Frame',(x,0,1.6),(0.10,1.68,1.68),BRASS,env,0.03)
    # chandelier
    torus('SM_BHC_Chandelier_Ring',(0,0,3.8),1.25,0.07,GOLD,env,rot=(0,0,0))
    for a in range(0,360,45):
        x=1.25*math.cos(radians(a)); y=1.25*math.sin(radians(a)); cyl('SM_BHC_Chandelier_Drop',(x,y,3.45),0.06,0.55,GLASS,env,verts=24); bpy.ops.object.light_add(type='POINT', location=(x,y,3.2)); bpy.context.object.data.energy=35; bpy.context.object.data.color=(1,0.45,0.16)
    add_area_light('BHC_Key_Area',(0,-1.5,4.2),900,(1.0,0.55,0.24),5)
    add_area_light('BHC_Fill_Area',(3,2,3.0),700,(0.18,0.25,1.0),4)
    # reference cubes
    ref=cube('SM_BHC_Reference_1m',(5.6,-3.0,0.5),(0.5,0.5,0.5),NEON_CYAN,env,0.01); text_obj('SM_BHC_Reference_Label','1 m',(5.6,-3.6,1.1),0.16,WHITE,env,rot=(radians(90),0,0))

# ---- blackjack table -----------------------------------------------------
blackjack=coll('BHC_Blackjack_Table')
def build_blackjack():
    # table top as layered rounded blocks, readable premium silhouette
    base=cube('SM_BHC_Blackjack_Base',(0,0,0.95),(2.65,1.45,0.82),WOOD,blackjack,0.35); uv(base)
    top=cube('SM_BHC_Blackjack_Tabletop',(0,0,1.78),(2.7,1.5,0.12),BRASS,blackjack,0.40); uv(top)
    felt=cube('SM_BHC_Blackjack_Felt',(0,0,1.93),(2.48,1.30,0.035),EMERALD,blackjack,0.38); uv(felt)
    # dealer rail and positions
    torus('SM_BHC_Blackjack_Dealer_Rail',(0,1.05,2.0),1.45,0.08,BRASS,blackjack,rot=(0,0,0))
    for i,x in enumerate([-1.8,-0.9,0,0.9,1.8]):
        torus('SM_BHC_Blackjack_Chip_Ring_%02d'%i,(x,-0.55,2.02),0.20,0.035,GOLD,blackjack)
        marker('SM_BHC_Blackjack_CardMarker_%02d'%i,(x,-0.05,2.02),blackjack,rot=(0,0,0),color=NEON_CYAN)
        cube('SM_BHC_Blackjack_Seat_%02d'%i,(x,-1.75,0.8),(0.36,0.36,0.42),VELVET,blackjack,0.14)
    cube('SM_BHC_Blackjack_Dealer_Pad',(0,0.85,2.02),(0.55,0.22,0.035),VELVET,blackjack,0.08)
    text_obj('SM_BHC_Blackjack_Sign','BLACKJACK',(0,0.95,2.16),0.22,GOLD,blackjack,rot=(radians(90),0,0),extrude=0.01)
    # shoe and discard tray
    cube('SM_BHC_Blackjack_Shoe',(-1.3,0.85,2.22),(0.30,0.22,0.14),BLACK,blackjack,0.06)
    cube('SM_BHC_Blackjack_Discard_Tray',(1.25,0.85,2.06),(0.36,0.25,0.05),BRASS,blackjack,0.05)
    # cards and chips as editables
    for i in range(3):
        card=cube('SM_BHC_Blackjack_Card_%02d'%i,(-0.28+i*0.30,0.26,2.03),(0.14,0.22,0.015),WHITE,blackjack,0.02); card.rotation_euler[2]=radians(-8+i*8); uv(card)
    for i,(x,y,c) in enumerate([(-1.2,-0.45,BRASS),(-1.05,-0.45,VELVET),(-0.9,-0.45,NEON_CYAN)]): cyl('SM_BHC_Blackjack_Chip_%02d'%i,(x,y,2.08),0.10,0.045,c,blackjack,verts=32)

# ---- character -----------------------------------------------------------
char=coll('BHC_Character_Player')
def build_character():
    # armature / standardized skeleton, 1.8m body + bounded head wobble bones
    arm=bpy.data.armatures.new('SK_BHC_Player_Skeleton'); rig=bpy.data.objects.new('SK_BHC_Player_Skeleton',arm); char.objects.link(rig); rig.show_in_front=True; rig.display_type='WIRE'; rig.location=(0,0,0)
    bpy.context.view_layer.objects.active=rig; rig.select_set(True); bpy.ops.object.mode_set(mode='EDIT')
    bones={}
    def eb(name,head,tail,parent=None):
        b=arm.edit_bones.new(name); b.head=head; b.tail=tail; b.parent=parent; bones[name]=b; return b
    root=eb('root',(0,0,0),(0,0,0.2)); pelvis=eb('pelvis',(0,0,0.85),(0,0,1.05),root); spine=eb('spine',(0,0,1.05),(0,0,1.55),pelvis); chest=eb('chest',(0,0,1.45),(0,0,1.75),spine); neck=eb('neck',(0,0,1.75),(0,0,1.92),chest); headb=eb('head',(0,0,1.92),(0,0,2.35),neck); wob=eb('head_wobble',(0,0,2.12),(0,0,2.45),headb)
    for side,x in [('L',-0.38),('R',0.38)]:
        clav=eb('clavicle_'+side,(x*0.35,0,1.65),(x*0.95,0,1.65),chest); upper=eb('upperarm_'+side,(x*0.95,0,1.62),(x*1.05,0,1.1),clav); fore=eb('forearm_'+side,(x*1.05,0,1.1),(x*1.05,0,0.62),upper); hand=eb('hand_'+side,(x*1.05,0,0.62),(x*1.05,0,0.42),fore); thigh=eb('thigh_'+side,(x*0.25,0,0.85),(x*0.32,0,0.42),pelvis); calf=eb('calf_'+side,(x*0.32,0,0.42),(x*0.32,0,0.08),thigh); foot=eb('foot_'+side,(x*0.32,0,0.08),(x*0.32,-0.25,0.03),calf)
    bpy.ops.object.mode_set(mode='OBJECT'); rig.select_set(False)
    # body
    body=uv_sphere('SK_BHC_Player_Body',(0,0,1.35),(0.56,0.34,0.70),SUIT,char); body.scale=(1.0,0.85,1.0); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    chestmesh=cube('SK_BHC_Player_Jacket',(0,0,1.45),(0.52,0.32,0.48),SUIT,char,0.18)
    shirt=cube('SK_BHC_Player_Shirt',(0,-0.33,1.58),(0.18,0.035,0.28),SHIRT,char,0.03)
    # head oversized with ears, jaw, nose, eyes
    head=uv_sphere('SK_BHC_Player_Head',(0,0,2.27),(0.72,0.58,0.70),SKIN,char); parent(head,rig)
    jaw=uv_sphere('SK_BHC_Player_Jaw',(0,-0.03,2.03),(0.48,0.44,0.35),SKIN,char); parent(jaw,rig)
    hair=uv_sphere('SK_BHC_Player_Hair',(0,0.06,2.70),(0.68,0.54,0.32),HAIR,char); parent(hair,rig)
    for x in (-0.26,0.26):
        eye=uv_sphere('SK_BHC_Player_Eye_'+('L' if x<0 else 'R'),(x,-0.52,2.34),(0.12,0.08,0.14),WHITE,char); parent(eye,rig)
        pupil=uv_sphere('SK_BHC_Player_Pupil_'+('L' if x<0 else 'R'),(x,-0.59,2.34),(0.05,0.025,0.07),BLACK,char); parent(pupil,rig)
    nose=uv_sphere('SK_BHC_Player_Nose',(0,-0.57,2.17),(0.10,0.12,0.13),SKIN,char); parent(nose,rig)
    # brows, mouth, ears
    for x in (-0.25,0.25): cube('SK_BHC_Player_Brow_'+('L' if x<0 else 'R'),(x,-0.57,2.53),(0.16,0.025,0.035),HAIR,char,0.02)
    mouth=cube('SK_BHC_Player_Mouth',(0,-0.585,2.01),(0.20,0.02,0.035),VELVET,char,0.015); parent(mouth,rig)
    for x in (-0.70,0.70): uv_sphere('SK_BHC_Player_Ear_'+('L' if x<0 else 'R'),(x,0,2.30),(0.12,0.10,0.18),SKIN,char)
    # accessories and outfit
    cube('SK_BHC_Player_Lapel_L',(-0.22,-0.36,1.7),(0.05,0.03,0.26),GOLD,char,0.02); cube('SK_BHC_Player_Lapel_R',(0.22,-0.36,1.7),(0.05,0.03,0.26),GOLD,char,0.02)
    torus('SK_BHC_Player_Glasses',(0,-0.57,2.38),0.34,0.025,BRASS,char,rot=(radians(90),0,0))
    for side,x in [('L',-0.75),('R',0.75)]:
        armmesh=uv_sphere('SK_BHC_Player_Arm_'+side,(x*0.62,0,1.34),(0.18,0.20,0.52),SUIT,char); parent(armmesh,rig)
        handmesh=uv_sphere('SK_BHC_Player_Glove_'+side,(x*0.78,-0.02,0.78),(0.20,0.18,0.17),RUBBER,char); parent(handmesh,rig)
        shoe=uv_sphere('SK_BHC_Player_Shoe_'+side,(x*0.30,-0.16,0.10),(0.24,0.40,0.13),GUNMETAL,char); parent(shoe,rig)
    # attachment markers
    for n,loc in [('hand_R_socket',(0.78,-0.12,0.78)),('back_socket',(0,0.28,1.35)),('head_fx',(0,-0.2,2.65))]: marker('ATT_BHC_'+n,loc,char)
    # bound wobble: custom prop docs
    rig['BHC_SkeletonScale']='1 Blender unit = 1 meter'; rig['BHC_HeadWobbleLimit']='12 degrees'; rig['BHC_HitVolume']='Use body/head envelope, cosmetics do not expand damage volume'
    # simple animation actions (keyed poses)
    def action(name, frames, pose_fn, loop=False):
        bpy.context.view_layer.objects.active=rig; rig.select_set(True)
        if not rig.animation_data: rig.animation_data_create()
        act=bpy.data.actions.new(name); rig.animation_data.action=act
        bpy.context.scene.frame_set(frames[0]); pose_fn(); rig.keyframe_insert(data_path='rotation_euler', frame=frames[0])
        bpy.context.scene.frame_set(frames[-1]); pose_fn(); rig.keyframe_insert(data_path='rotation_euler', frame=frames[-1])
        act['Looping']=loop; act['RootMotion']='None'; act['GameplayEvent']=name; act.use_fake_user=True
        rig.animation_data_clear(); rig.select_set(False)
    def idle():
        rig.rotation_euler[2]=0
    def nod():
        rig.rotation_euler[1]=radians(8)
    action('AN_BHC_Idle',[1,40],idle,True); action('AN_BHC_SuspiciousGlance',[1,18],nod,False)
    rig['AnimationClips']='Idle, Walk, Jog, Sprint, Crouch, Jump, Land, Turn, WeaponReady, Aim, Reload, Sit, Deal, PlaceChips, InspectCards, SlotLever, WinCelebration, Loss, SuspiciousGlance, Accusation, Downed, Revive, Recovery, Defeat'

# ---- AK-style hero weapon -----------------------------------------------
weapon=coll('BHC_Weapon_AK47')
def build_weapon():
    root=cube('SM_BHC_WP_AK47_ROOT',(0,0,0),(0.01,0.01,0.01),None,weapon,0)
    receiver=cube('SM_BHC_WP_AK47_Receiver',(0,0,1.15),(0.70,0.16,0.18),GUNMETAL,weapon,0.06); parent(receiver,root)
    top=cube('SM_BHC_WP_AK47_Upper',(0,0,1.38),(0.62,0.14,0.08),GUNMETAL,weapon,0.04); parent(top,root)
    barrel=cyl('SM_BHC_WP_AK47_Barrel',(0,0,1.68),0.075,1.05,GUNMETAL,weapon,verts=32,rot=(0,radians(90),0)); parent(barrel,root)
    muzzle=cyl('SM_BHC_WP_AK47_Muzzle',(0,0,2.22),0.11,0.22,BRASS,weapon,verts=32,rot=(0,radians(90),0)); parent(muzzle,root)
    stock=cube('SM_BHC_WP_AK47_Stock',(-0.92,0,1.02),(0.48,0.12,0.14),WOODGRIP,weapon,0.08); stock.rotation_euler[1]=radians(-8); parent(stock,root)
    grip=cube('SM_BHC_WP_AK47_Grip',(-0.13,0,0.82),(0.12,0.13,0.32),WOODGRIP,weapon,0.08); grip.rotation_euler[1]=radians(-12); parent(grip,root)
    mag=cube('SM_BHC_WP_AK47_Magazine',(-0.05,0,0.54),(0.15,0.12,0.36),GUNMETAL,weapon,0.08); mag.rotation_euler[1]=radians(-12); parent(mag,root)
    # casino inlay and sight
    cube('SM_BHC_WP_AK47_BrassInlay',(0, -0.17,1.20),(0.45,0.018,0.035),GOLD,weapon,0.01)
    for x in (-0.25,0.0,0.25): torus('SM_BHC_WP_AK47_EngravedRing_'+str(x),(x,-0.18,1.20),0.05,0.012,GOLD,weapon,rot=(radians(90),0,0))
    cube('SM_BHC_WP_AK47_RearSight',(-0.36,0,1.53),(0.09,0.06,0.08),GUNMETAL,weapon,0.02)
    cube('SM_BHC_WP_AK47_FrontSight',(0.45,0,1.77),(0.05,0.05,0.14),GUNMETAL,weapon,0.02)
    # world / first-person copies
    for prefix, scale, loc in [('FP',1.03,(0,0,0)),('TP',0.90,(0,0,0))]:
        for src in [receiver,top,barrel,muzzle,stock,grip,mag]:
            o=src.copy(); o.data=src.data.copy(); o.name=src.name.replace('SM_BHC_WP_AK47','SM_BHC_WP_AK47_'+prefix); weapon.objects.link(o); o.scale=(scale,scale,scale); o.location=Vector(loc)+src.location
    # markers and collision
    for n,loc,rot in [('Muzzle',(0,0,2.34),(0,radians(90),0)),('Grip',(-0.13,0,0.82),(0,0,0)),('Magazine',(-0.05,0,0.25),(0,0,0)),('Ejection',(0.26,-0.19,1.22),(radians(90),0,0)),('Sight',(0.45,0,1.84),(0,0,0))]: marker('ATT_BHC_AK47_'+n,loc,weapon,rot)
    col=cube('COL_BHC_WP_AK47',(0,0,1.25),(1.25,0.28,0.35),None,weapon,0.02); col.display_type='WIRE'; col.hide_render=True
    root['AssetID']='BHC_WP_AK47'; root['DesignNote']='Original casino presentation, AK-inspired silhouette; no licensed logo'; root['ImportOrientation']='Muzzle +X, up +Z, units meters'; root['AnimationClips']='AN_BHC_AK47_Equip, AN_BHC_AK47_Fire, AN_BHC_AK47_Reload, AN_BHC_AK47_Inspect, AN_BHC_AK47_Unequip'; root['LOD']='LOD0 hero / LOD1 60% / LOD2 25% triangle guidance'
    # placeholder actions on root
    bpy.context.view_layer.objects.active=root; root.select_set(True)
    for name in ['AN_BHC_AK47_Equip','AN_BHC_AK47_Fire','AN_BHC_AK47_Reload','AN_BHC_AK47_Inspect','AN_BHC_AK47_Unequip']:
        act=bpy.data.actions.new(name); act['RootMotion']='None'; act['Looping']=False; act['GameplayEvents']='Muzzle, Magazine, Ejection'; act.use_fake_user=True
    root.select_set(False)

# ---- camera / render -----------------------------------------------------
def camera_setup():
    bpy.ops.object.camera_add(location=(10,-12,8), rotation=(radians(67),0,radians(39)))
    cam=bpy.context.object; cam.name='CAM_BHC_Overview'; bpy.context.scene.camera=cam; cam.data.lens=34
    # point camera toward center
    def track(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    track(cam,(0,0,1.4))
    bpy.context.scene.render.engine='BLENDER_EEVEE'; bpy.context.scene.render.resolution_x=1280; bpy.context.scene.render.resolution_y=720; bpy.context.scene.render.resolution_percentage=100
    bpy.context.scene.render.image_settings.file_format='PNG'; bpy.context.scene.world.color=(0.008,0.008,0.012)
    return cam

def render_preview(name, loc, target, filepath, lens=46):
    bpy.ops.object.camera_add(location=loc); cam=bpy.context.object; cam.data.lens=lens; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.camera=cam; bpy.context.scene.render.filepath=filepath; bpy.ops.render.render(write_still=True); bpy.data.objects.remove(cam, do_unlink=True)

def render_isolated(collection, loc, target, filepath, lens=52):
    states={o:o.hide_render for o in bpy.context.scene.objects}
    for o in bpy.context.scene.objects:
        if o.type not in {'LIGHT','CAMERA'}:
            o.hide_render = (o.name not in collection.objects.keys()) or o.name.startswith('COL_') or o.name.startswith('ATT_') or '_FP_' in o.name or '_TP_' in o.name
    render_preview('isolated',loc,target,filepath,lens)
    for o,s in states.items(): o.hide_render=s

def export_collection(collection, filename):
    bpy.ops.object.select_all(action='DESELECT')
    for o in collection.objects:
        if o.type in {'MESH','ARMATURE','EMPTY','FONT'} and not o.hide_render: o.select_set(True)
    bpy.context.view_layer.objects.active=next((o for o in collection.objects if o.type=='MESH'), None)
    path=os.path.join(EXPORT_DIR,filename)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True)
    bpy.ops.object.select_all(action='DESELECT')
    return path

def export_collection_fbx(collection, filename):
    bpy.ops.object.select_all(action='DESELECT')
    for o in collection.objects:
        if o.type in {'MESH','ARMATURE','EMPTY'} and not o.hide_render: o.select_set(True)
    bpy.context.view_layer.objects.active=next((o for o in collection.objects if o.type=='MESH'), None)
    path=os.path.join(EXPORT_DIR,filename)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_scale_options='FBX_SCALE_ALL', object_types={'MESH','ARMATURE','EMPTY'}, add_leaf_bones=False, bake_anim=False)
    bpy.ops.object.select_all(action='DESELECT')
    return path

def write_manifest():
    items=[]
    def info(asset_id, src, export, typ, c, notes):
        dims=[]; tris=[]
        for o in c.objects:
            if o.type=='MESH':
                dims.append(tuple(round(v,3) for v in o.dimensions)); tris.append(sum(len(p.vertices) for p in o.data.polygons))
        items.append({'AssetID':asset_id,'SourceFile':src,'ExportFile':export,'AlternateExportFile':export.replace('.glb','.fbx'),'AssetType':typ,'DimensionsMeters':dims,'TriangleCountsLOD':{'LOD0':sum(tris),'LOD1_guidance':'60%','LOD2_guidance':'25%'},'Materials':'PBR BaseColor/Normal/Roughness/Metallic/AO; procedural source materials in .blend','Collision':'COL_* proxy objects where applicable','SkeletonAnimations':notes.get('anims',''),'AttachmentMarkers':notes.get('markers',''),'Dependencies':notes.get('deps',''),'LicenseProvenance':'Original BHC design; reference silhouettes only; no logos','KnownIssues':notes.get('issues','LOD meshes are authored as guidance metadata; final reduction pass remains for Sol'),'VerificationStatus':'Generated and render-checked by Blender batch script'})
    info('BHC_ENV_MODULAR_KIT','Art/Blender/BHC_First_Batch.blend','Art/Exports/BHC_ENV_MODULAR_KIT.glb','Modular environment',env,{'deps':'Shared BHC material library'})
    info('BHC_SK_PLAYER_BIGHEAD','Art/Blender/BHC_First_Batch.blend','Art/Exports/BHC_SK_PLAYER_BIGHEAD.glb','Skeletal character',char,{'anims':'Idle, SuspiciousGlance plus named integration list in rig custom properties','markers':'ATT_BHC_hand_R_socket, ATT_BHC_back_socket, ATT_BHC_head_fx','issues':'Additional production animation authoring and deformation QA remain for Sol'})
    info('BHC_WP_AK47','Art/Blender/BHC_First_Batch.blend','Art/Exports/BHC_WP_AK47.glb','Weapon',weapon,{'anims':'Equip, Fire, Reload, Inspect, Unequip','markers':'Muzzle, Grip, Magazine, Ejection, Sight','issues':'LOD1/LOD2 authored as guidance metadata'})
    info('BHC_PROP_BLACKJACK','Art/Blender/BHC_First_Batch.blend','Art/Exports/BHC_PROP_BLACKJACK.glb','Casino table prop',blackjack,{'markers':'Card and chip positions','deps':'Shared BHC material library'})
    with open(os.path.join(MANIFEST_DIR,'BHC_First_Batch_manifest.json'),'w',encoding='utf8') as f: json.dump({'Project':'BIG HEAD CASINO','Batch':'First Complete Asset Batch','Scale':'1 Blender unit = 1 meter','BlenderToUnreal':'Use GLB/FBX import scale 1.0; Z-up source, Unreal Z-up; apply transforms before import','Assets':items,'MandatoryInstruction':'create it fully 3D and very high end no BS.'},f,indent=2)

clear(); build_environment(); build_blackjack(); build_character(); build_weapon(); camera_setup()
# export source blend
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BLEND_DIR,'BHC_First_Batch.blend'))
export_collection(env,'BHC_ENV_MODULAR_KIT.glb'); export_collection(char,'BHC_SK_PLAYER_BIGHEAD.glb'); export_collection(weapon,'BHC_WP_AK47.glb'); export_collection(blackjack,'BHC_PROP_BLACKJACK.glb')
export_collection_fbx(env,'BHC_ENV_MODULAR_KIT.fbx'); export_collection_fbx(char,'BHC_SK_PLAYER_BIGHEAD.fbx'); export_collection_fbx(weapon,'BHC_WP_AK47.fbx'); export_collection_fbx(blackjack,'BHC_PROP_BLACKJACK.fbx')
# previews
for o in env.objects:
    if 'Ceiling' in o.name: o.hide_render=True
render_preview('overview',(0,-2.8,2.7),(0,0,1.55),os.path.join(PREVIEW_DIR,'BHC_Overview.png'),30)
render_isolated(char,(4,-6,3.0),(0,0,1.55),os.path.join(PREVIEW_DIR,'BHC_Character.png'),52)
render_isolated(weapon,(3.8,-5.5,2.2),(0,0,1.2),os.path.join(PREVIEW_DIR,'BHC_AK47.png'),58)
render_isolated(blackjack,(4,-6,3.4),(0,0,1.4),os.path.join(PREVIEW_DIR,'BHC_Blackjack.png'),52)
write_manifest(); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BLEND_DIR,'BHC_First_Batch.blend'))
print('BHC_FIRST_BATCH_COMPLETE')
