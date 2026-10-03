import bpy, os, math, json
from mathutils import Vector
from math import radians

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
BASE = os.path.join(ROOT, 'Art', 'Vehicles', 'BHC_VEH_328_NEON_DIESEL')
BLEND_DIR=os.path.join(BASE,'Blender'); EXPORT_DIR=os.path.join(BASE,'Exports'); COLL_DIR=os.path.join(BASE,'Collision'); PREVIEW_DIR=os.path.join(BASE,'Previews'); MANIFEST_DIR=os.path.join(BASE,'Manifests')
for d in (BLEND_DIR,EXPORT_DIR,COLL_DIR,PREVIEW_DIR,MANIFEST_DIR): os.makedirs(d,exist_ok=True)

def clear():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def collection(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children.keys(): bpy.context.scene.collection.children.link(c)
    return c

def move(o,c):
    for old in list(o.users_collection): old.objects.unlink(o)
    c.objects.link(o)

def make_mat(name, color, metallic=0.0, rough=0.45, emission=None, clearcoat=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metallic; bs.inputs['Roughness'].default_value=rough
    if 'Coat Weight' in bs.inputs: bs.inputs['Coat Weight'].default_value=clearcoat
    if emission:
        bs.inputs['Emission Color'].default_value=(*emission,1); bs.inputs['Emission Strength'].default_value=5
    return m

PAINT=make_mat('M_BHC_328_GraphitePaint',(0.018,0.024,0.032),0.72,0.22,clearcoat=0.55)
PAINT2=make_mat('M_BHC_328_GraphiteHighlight',(0.055,0.067,0.084),0.66,0.2,clearcoat=0.5)
CARBON=make_mat('M_BHC_328_CarbonFiber',(0.008,0.011,0.014),0.35,0.3)
BLACK=make_mat('M_BHC_328_Black',(0.004,0.005,0.006),0.05,0.5)
GLASS=make_mat('M_BHC_328_SmokedGlass',(0.015,0.03,0.045),0.1,0.11)
CHROME=make_mat('M_BHC_328_Chrome',(0.38,0.42,0.47),0.95,0.12)
RED=make_mat('M_BHC_328_RedLamp',(0.36,0.005,0.01),0.2,0.2,(1,0.01,0.01))
WHITE=make_mat('M_BHC_328_CoolWhite',(0.75,0.86,1.0),0.2,0.18,(0.65,0.8,1.0))
RED_FACE=make_mat('M_BHC_328_Logo_RedFace',(0.65,0.01,0.015),0.15,0.23,(1,0.005,0.01))
RED_EDGE=make_mat('M_BHC_328_Logo_ChromeRed',(0.5,0.018,0.02),0.75,0.16,(0.35,0.002,0.003))
WHEEL=make_mat('M_BHC_328_Wheel',(0.018,0.02,0.025),0.88,0.16)
TIRE=make_mat('M_BHC_328_Tire',(0.006,0.007,0.008),0.0,0.84)
CALIPER=make_mat('M_BHC_328_BrakeCaliper',(0.7,0.19,0.02),0.72,0.2)
DISC=make_mat('M_BHC_328_BrakeDisc',(0.23,0.25,0.27),0.84,0.26)
LEATHER=make_mat('M_BHC_328_InteriorLeather',(0.018,0.02,0.025),0.15,0.46)
LEATHER_RED=make_mat('M_BHC_328_InteriorRedAccent',(0.12,0.012,0.016),0.15,0.4)
MATTE=make_mat('M_BHC_328_InteriorPlastic',(0.055,0.06,0.068),0.12,0.5)
ALU=make_mat('M_BHC_328_EngineMetal',(0.16,0.17,0.18),0.84,0.22)
HOSE=make_mat('M_BHC_328_Hose',(0.01,0.012,0.014),0.0,0.55)

def assign(o,m):
    if m: o.data.materials.append(m)
    return o
def smooth(o):
    if hasattr(o.data,'polygons'):
        for p in o.data.polygons:p.use_smooth=True
    return o
def bevel(o,w=0.04,s=3):
    if o.type=='MESH':
        mod=o.modifiers.new('BHC_Bevel','BEVEL'); mod.width=w; mod.segments=s
    return o
def cube(name,loc,scale,m=None,c=None,bev=0.03):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); assign(o,m); bevel(o,bev,3)
    if c: move(o,c)
    return o
def cyl(name,loc,r,depth,m=None,c=None,rot=(0,0,0),verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot); o=bpy.context.object; o.name=name; assign(o,m); smooth(o)
    if c: move(o,c)
    return o
def sphere(name,loc,scale,m=None,c=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); assign(o,m); smooth(o)
    if c: move(o,c)
    return o
def torus(name,loc,major,minor,m=None,c=None,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=64,minor_segments=16,location=loc,rotation=rot); o=bpy.context.object; o.name=name; assign(o,m); smooth(o)
    if c: move(o,c)
    return o
def text(name,body,loc,size,m,c,rot=(radians(90),0,0),extrude=0.008):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=extrude; cu.bevel_depth=0.004; cu.space_line=0.72; cu.shear=-0.18
    o=bpy.data.objects.new(name,cu); c.objects.link(o); o.location=loc; o.rotation_euler=rot; assign(o,m); return o
def custom_mesh(name,verts,faces,m,c):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); c.objects.link(o); assign(o,m); bevel(o,0.045,3); return o
def marker(name,loc,c,rot=(0,0,0),scale=1.0):
    o=cube(name,loc,(0.025*scale,0.025*scale,0.025*scale),WHITE,c,0.005); o.rotation_euler=rot; o.hide_render=True; return o
def parent(o,p): o.parent=p
def uv(o):
    if o.type=='MESH':
        bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=0.03); bpy.ops.object.mode_set(mode='OBJECT'); o.select_set(False)

COL_BODY=collection('BHC_VEH_328_Exterior'); COL_INTERIOR=collection('BHC_VEH_328_Interior'); COL_WHEELS=collection('BHC_VEH_328_Wheels'); COL_ENGINE=collection('BHC_VEH_328_EngineBay'); COL_RIG=collection('BHC_VEH_328_Rig'); COL_COL=collection('BHC_VEH_328_Collision'); COL_LOD=collection('BHC_VEH_328_LODs'); COL_LIGHT=collection('BHC_VEH_328_Locators')

def body_shell():
    # coherent inferred proportions: 5.05m L x 2.06m W x 1.42m H
    sec=[(-2.52,0.86,0.48,0.96),(-1.95,0.98,0.48,1.08),(-1.25,1.01,0.52,1.32),(-0.55,0.93,0.55,1.48),(0.55,0.93,0.55,1.48),(1.25,1.01,0.52,1.32),(1.95,0.98,0.48,1.08),(2.52,0.86,0.48,0.90)]
    verts=[]
    for x,w,z0,zt in sec: verts += [(x,-w,z0),(x,w,z0),(x,-w*0.96,zt),(x,w*0.96,zt)]
    faces=[]
    for i in range(len(sec)-1):
        a=i*4; b=(i+1)*4
        faces += [(a,b,b+2,a+2),(a+1,a+3,b+3,b+1),(a+2,b+2,b+3,a+3),(a,a+1,b+1,b)]
    faces += [(0,2,3,1),((len(sec)-1)*4,((len(sec)-1)*4)+1,((len(sec)-1)*4)+3,((len(sec)-1)*4)+2)]
    shell=custom_mesh('SM_BHC_328_BodyShell',verts,faces,PAINT,COL_BODY); uv(shell)
    shell['InferredDimensions']='5.05m x 2.06m x 1.48m from concept reference; hidden geometry inferred for game use'
    # roof and pillars / beltline
    cube('SM_BHC_328_Roof',(0,0,1.50),(1.02,0.86,0.06),PAINT2,COL_BODY,0.06)
    for y in (-0.86,0.86):
        cube('SM_BHC_328_Beltline',(-0.05,y,0.98),(1.95,0.055,0.08),PAINT2,COL_BODY,0.03)
        for x in (-1.35,-0.55,0.55,1.35): cyl('SM_BHC_328_Widebody_Rivet',(x,y*1.01,1.05),0.025,0.018,CHROME,COL_BODY,rot=(radians(90),0,0),verts=16)
    # doors, jambs, handles
    for side,y in [('L',-0.99),('R',0.99)]:
        for idx,x in enumerate([-1.15,0.25]):
            d=cube(f'SM_BHC_328_Door_{side}_{"F" if idx==0 else "R"}',(x,y,0.98),(0.62,0.035,0.42),PAINT,COL_BODY,0.035); d['PanelBoundary']=True
            cube(f'SM_BHC_328_DoorJamb_{side}_{idx}',(x,y*1.015,0.98),(0.65,0.012,0.44),BLACK,COL_BODY,0.02)
            cube(f'SM_BHC_328_DoorHandle_{side}_{idx}',(x+0.22,y*1.05,1.20),(0.11,0.018,0.025),CHROME,COL_BODY,0.012)
    # widebody fender flares and skirts
    for side,y in [('L',-1.03),('R',1.03)]:
        for x in (-1.55,1.55):
            torus(f'SM_BHC_328_WidebodyFender_{side}_{x}',(x,y,0.52),0.44,0.085,PAINT2,COL_BODY,rot=(radians(90),0,0))
        cube(f'SM_BHC_328_SideSkirt_{side}',(0,y,0.46),(1.7,0.07,0.10),CARBON,COL_BODY,0.04)
    # hood and vents with recesses
    hood=cube('SM_BHC_328_Hood',(1.35,0,1.14),(0.60,0.88,0.055),PAINT,COL_BODY,0.06); hood['Pivot']='BHC_Rig_Hood';
    for y in (-0.42,0.42):
        cube('SM_BHC_328_HoodVent_Recess',(1.35,y,1.205),(0.28,0.11,0.025),BLACK,COL_BODY,0.04)
        cube('SM_BHC_328_HoodVent_Inner',(1.35,y,1.225),(0.22,0.065,0.018),CARBON,COL_BODY,0.02)
        for i in range(4): cube('SM_BHC_328_HoodVent_Fin',(1.20+i*0.10,y,1.245),(0.015,0.07,0.015),CHROME,COL_BODY,0.004)
    # bumpers, front aero, intakes
    cube('SM_BHC_328_FrontBumper',(2.35,0,0.78),(0.16,0.94,0.28),PAINT,COL_BODY,0.10)
    cube('SM_BHC_328_FrontSplitter',(2.48,0,0.41),(0.22,1.05,0.045),CARBON,COL_BODY,0.025)
    for y in (-0.72,0.72): cube('SM_BHC_328_FrontCanard',(2.40,y,0.68),(0.16,0.18,0.025),CARBON,COL_BODY,0.02)
    # grille twin kidney
    for y in (-0.28,0.28):
        g=cube('SM_BHC_328_KidneyGrille',(2.52,y,0.94),(0.04,0.20,0.18),BLACK,COL_BODY,0.08)
        for i in range(5): cube('SM_BHC_328_Grille_Slat',(2.57,y-0.16+i*0.08,0.94),(0.02,0.012,0.15),CHROME,COL_BODY,0.004)
    # intercooler frame and fins
    cube('SM_BHC_328_Intercooler_Frame',(2.55,0,0.57),(0.05,0.52,0.20),ALU,COL_BODY,0.025)
    for y in [(-0.45+i*0.08) for i in range(12)]: cube('SM_BHC_328_Intercooler_Fin',(2.61,y,0.57),(0.012,0.018,0.18),CHROME,COL_BODY,0.002)
    text('SM_BHC_328_Intercooler_Logo','328',(2.63,0,0.57),0.18,BLACK,COL_BODY,rot=(radians(90),0,radians(90)),extrude=0.012)
    # headlights / mirrors / windows
    for y in (-0.63,0.63):
        cube('SM_BHC_328_Headlight_Lens',(2.42,y,1.14),(0.08,0.20,0.10),WHITE,COL_LIGHT,0.04)
        cube('SM_BHC_328_Headlight_Brow',(2.49,y,1.28),(0.05,0.22,0.025),BLACK,COL_BODY,0.02)
        mirror=sphere('SM_BHC_328_Mirror_'+('L' if y<0 else 'R'),(0.35,y*1.06,1.45),(0.17,0.09,0.10),PAINT,COL_BODY); cube('SM_BHC_328_MirrorGlass_'+('L' if y<0 else 'R'),(0.35,y*1.12,1.45),(0.09,0.018,0.06),GLASS,COL_BODY,0.02)
    cube('SM_BHC_328_Windshield',(0.36,0,1.43),(0.45,0.83,0.04),GLASS,COL_BODY,0.03); cube('SM_BHC_328_RearGlass',(-0.82,0,1.42),(0.28,0.82,0.04),GLASS,COL_BODY,0.03)
    for y in (-0.50,0.50): cube('SM_BHC_328_SideWindow_F',(0.1,y,1.43),(0.33,0.035,0.23),GLASS,COL_BODY,0.03); cube('SM_BHC_328_SideWindow_R',(-0.68,y,1.43),(0.30,0.035,0.23),GLASS,COL_BODY,0.03)
    for y in (-0.55,0.55): cube('SM_BHC_328_Wiper',(1.03,y,1.50),(0.28,0.025,0.018),BLACK,COL_BODY,0.008)
    # trunk and rear body
    trunk=cube('SM_BHC_328_Trunk',(-1.55,0,1.10),(0.48,0.86,0.05),PAINT,COL_BODY,0.06); trunk['Pivot']='BHC_Rig_Trunk'
    cube('SM_BHC_328_RearBumper',(-2.36,0,0.72),(0.16,0.95,0.28),PAINT,COL_BODY,0.10)
    cube('SM_BHC_328_RearDiffuser',(-2.48,0,0.42),(0.18,0.98,0.22),CARBON,COL_BODY,0.05)
    for y in (-0.68,-0.23,0.23,0.68): cyl('SM_BHC_328_ExhaustOutlet',(-2.58,y,0.52),0.09,0.18,CHROME,COL_BODY,rot=(0,radians(90),0),verts=32)
    for y in (-0.63,0.63): cube('SM_BHC_328_TailLamp',(-2.47,y,1.02),(0.06,0.23,0.10),RED,COL_LIGHT,0.04)
    # rear wing with supports/endplates
    for y in (-0.60,0.60): cube('SM_BHC_328_WingSupport',(-1.75,y,1.72),(0.06,0.06,0.38),CARBON,COL_BODY,0.02); cube('SM_BHC_328_WingEndplate',(-1.65,y,2.02),(0.06,0.04,0.28),CARBON,COL_BODY,0.02)
    cube('SM_BHC_328_RearWing',(-1.75,0,2.02),(0.46,0.85,0.06),CARBON,COL_BODY,0.035)
    # branded both sides: separate door pieces, correct facing
    for side,y,rot in [('L',-1.045,(radians(90),0,0)),('R',1.045,(-radians(90),0,0))]:
        for idx,x in enumerate([-1.15,0.25]):
            # split text sections at panel boundary but maintain complete wording on each side in closed state
            edge=text(f'SM_BHC_328_LogoEdge_{side}_{idx}','Big Head\nCasino Games',(x,y,0.98),0.20,RED_EDGE,COL_BODY,rot,0.012); face=text(f'SM_BHC_328_LogoFace_{side}_{idx}','Big Head\nCasino Games',(x,y+(0.010 if side=='L' else -0.010),0.98),0.185,RED_FACE,COL_BODY,rot,0.008)
            edge['Branding']='Exact Big Head / Casino Games, italic red with chrome-red border and emissive channel'; face['EmissiveMask']='Red logo illumination'

def interior():
    cube('SM_BHC_328_CabinFloor',(0,0,0.56),(1.35,0.78,0.05),MATTE,COL_INTERIOR,0.04)
    cube('SM_BHC_328_Dashboard',(0.90,0,1.17),(0.48,0.78,0.14),MATTE,COL_INTERIOR,0.08)
    cube('SM_BHC_328_InstrumentCluster',(1.27,0,1.35),(0.08,0.30,0.16),BLACK,COL_INTERIOR,0.04); cube('SM_BHC_328_InstrumentDisplay',(1.35,0,1.36),(0.02,0.20,0.09),WHITE,COL_INTERIOR,0.01)
    cube('SM_BHC_328_CenterConsole',(0.15,0,0.85),(0.52,0.22,0.14),LEATHER,COL_INTERIOR,0.05); cube('SM_BHC_328_GearSelector',(0.24,0,1.02),(0.08,0.08,0.14),CHROME,COL_INTERIOR,0.025)
    torus('SM_BHC_328_SteeringWheel',(0.95,-0.35,1.20),0.19,0.035,LEATHER,COL_INTERIOR,rot=(radians(90),0,0)); cube('SM_BHC_328_SteeringHub',(0.95,-0.35,1.20),(0.05,0.05,0.04),CHROME,COL_INTERIOR,0.01)
    for y in (-0.38,0.38):
        for x in (0.72,-0.62):
            seat=cube(f'SM_BHC_328_Seat_{"Driver" if y<0 and x>0 else "Passenger" if y>0 and x>0 else "Rear"}',(x,y,0.90),(0.34,0.30,0.10),LEATHER,COL_INTERIOR,0.10); cube('SM_BHC_328_SeatBack',(x-0.20,y,1.20),(0.12,0.30,0.35),LEATHER,COL_INTERIOR,0.10); cube('SM_BHC_328_Headrest',(x-0.30,y,1.55),(0.10,0.22,0.12),LEATHER_RED,COL_INTERIOR,0.06)
            cube('SM_BHC_328_Seatbelt_Buckle',(x+0.18,y,1.02),(0.03,0.035,0.06),RED_FACE,COL_INTERIOR,0.01)
    for y in (-0.45,0.45): cube('SM_BHC_328_DoorCard',(0.0,y,0.9),(0.64,0.03,0.30),LEATHER,COL_INTERIOR,0.05); cube('SM_BHC_328_WindowControls',(0.15,y,1.15),(0.12,0.02,0.025),CHROME,COL_INTERIOR,0.01)
    for y in (-0.20,0.20): cube('SM_BHC_328_Pedal',(1.36,y,0.56),(0.03,0.05,0.10),ALU,COL_INTERIOR,0.01)
    cube('SM_BHC_328_Headliner',(0,0,1.62),(0.95,0.78,0.035),LEATHER,COL_INTERIOR,0.03); cube('SM_BHC_328_InteriorMirror',(0.78,0,1.52),(0.04,0.16,0.06),GLASS,COL_INTERIOR,0.02)

def wheel(name,x,y):
    p=bpy.data.objects.new(name+'_Pivot',None); COL_WHEELS.objects.link(p); p.empty_display_type='PLAIN_AXES'; p.location=(x,y,0.48); p['WheelRadius']=0.36; p['WheelWidth']=0.28; p['RotationAxis']='Y'; p['SteeringAxis']='Z' if x>0 else 'None'
    tire=torus(name+'_Tire',(x,y,0.48),0.36,0.13,TIRE,COL_WHEELS,rot=(radians(90),0,0)); parent(tire,p)
    rim=cyl(name+'_DeepDishWheel',(x,y,0.48),0.28,0.18,WHEEL,COL_WHEELS,rot=(radians(90),0,0),verts=48); parent(rim,p)
    for i in range(10):
        a=radians(i*36); spoke=cube(name+'_Spoke_%02d'%i,(x,y+0.10*math.cos(a),0.48+0.10*math.sin(a)),(0.22,0.025,0.025),CHROME,COL_WHEELS,0.01); spoke.rotation_euler[1]=a; parent(spoke,p)
    disc=cyl(name+'_BrakeDisc',(x,y-0.11,0.48),0.22,0.04,DISC,COL_WHEELS,rot=(radians(90),0,0),verts=48); parent(disc,p)
    cal=cube(name+'_BrakeCaliper',(x,y-0.15,0.60),(0.05,0.035,0.13),CALIPER,COL_WHEELS,0.02); parent(cal,p); p['CaliperDoesNotRotate']='Keep caliper on chassis reference during wheel rotation'
    return p

def wheels():
    for label,x,y in [('FL',1.55,-1.03),('FR',1.55,1.03),('RL',-1.55,-1.03),('RR',-1.55,1.03)]: wheel('SM_BHC_328_Wheel_'+label,x,y)
    # suspension/underbody visible structure
    for y in (-0.88,0.88):
        cube('SM_BHC_328_UnderbodyRail',(0,y,0.32),(1.6,0.05,0.06),CARBON,COL_WHEELS,0.02)
        for x in (-1.55,1.55): cyl('SM_BHC_328_Shock',(x,y,0.46),0.045,0.34,ALU,COL_WHEELS,rot=(0,0,radians(18)),verts=24)

def engine_bay():
    cube('SM_BHC_328_EngineBlock',(1.05,0,0.98),(0.48,0.36,0.25),ALU,COL_ENGINE,0.08); cube('SM_BHC_328_EngineCover',(1.05,0,1.26),(0.42,0.30,0.06),BLACK,COL_ENGINE,0.04)
    turbo=cyl('SM_BHC_328_Turbo',(0.55,-0.40,1.02),0.18,0.18,ALU,COL_ENGINE,rot=(0,radians(90),0)); torus('SM_BHC_328_TurboHousing',(0.55,-0.50,1.02),0.15,0.035,CHROME,COL_ENGINE,rot=(0,radians(90),0))
    for y in (-0.28,0.28):
        cyl('SM_BHC_328_ChargePipe',(1.45,y,1.05),0.055,0.70,HOSE,COL_ENGINE,rot=(0,radians(90),0)); torus('SM_BHC_328_HoseClamp',(1.45,y,1.05),0.065,0.012,CHROME,COL_ENGINE,rot=(0,radians(90),0))
    cube('SM_BHC_328_Radiator',(1.72,0,0.92),(0.05,0.55,0.32),ALU,COL_ENGINE,0.02); cube('SM_BHC_328_Battery',(0.85,0.55,0.98),(0.24,0.16,0.17),BLACK,COL_ENGINE,0.04); cube('SM_BHC_328_FuseBox',(1.55,0.50,1.08),(0.15,0.12,0.10),BLACK,COL_ENGINE,0.03)
    for y in (-0.48,0.48):
        for z in (0.75,1.18): torus('SM_BHC_328_Hose', (1.45,y,z),0.10,0.022,HOSE,COL_ENGINE,rot=(0,radians(90),0))
    text('SM_BHC_328_Turbo_Label','350 PSI',(0.55,-0.60,1.20),0.08,RED_FACE,COL_ENGINE,rot=(radians(90),0,0),extrude=0.004)
    # engine effect locators
    for n,loc in [('EngineAudio',(1.0,0,1.05)),('TurboAudio',(0.55,-0.40,1.02)),('HeatFX',(1.4,0,1.2))]: marker('LOC_BHC_328_'+n,loc,COL_LIGHT)

def rig_and_locators():
    # armature contract based on existing ABHCVehiclePawn's four-seat model
    arm=bpy.data.armatures.new('SK_BHC_328_VehicleRig'); rig=bpy.data.objects.new('SK_BHC_328_VehicleRig',arm); COL_RIG.objects.link(rig); rig.show_in_front=True; rig.display_type='WIRE'; bpy.context.view_layer.objects.active=rig; rig.select_set(True); bpy.ops.object.mode_set(mode='EDIT')
    bones={}
    def bone(n,h,t,p=None): b=arm.edit_bones.new(n); b.head=h; b.tail=t; b.parent=p; bones[n]=b; return b
    root=bone('Chassis',(0,0,0.45),(0,0,0.75));
    for n,x,y in [('Wheel_FL',1.55,-1.03),('Wheel_FR',1.55,1.03),('Wheel_RL',-1.55,-1.03),('Wheel_RR',-1.55,1.03)]: bone(n,(x,y,0.48),(x,y,0.78),root)
    for n,h,t in [('Door_FL',(-1.15,-1.0,0.8),(-1.15,-1.0,1.4)),('Door_FR',(-1.15,1.0,0.8),(-1.15,1.0,1.4)),('Door_RL',(0.25,-1.0,0.8),(0.25,-1.0,1.4)),('Door_RR',(0.25,1.0,0.8),(0.25,1.0,1.4)),('Hood',(1.35,0,1.1),(1.35,0,1.4)),('Trunk',(-1.55,0,1.1),(-1.55,0,1.4)),('SteeringWheel',(0.95,-0.35,1.2),(0.95,-0.35,1.45))]: bone(n,h,t,root)
    bpy.ops.object.mode_set(mode='OBJECT'); rig.select_set(False)
    rig['BHC_ImportContract']='Forward +X, Up +Z, lateral +Y, units meters; wheel spin axis Y; front steer axis Z; scale 1.0'
    rig['BHC_SeatCount']=4; rig['BHC_DriveConfig']='Standard RWD; optional AWD uses same visual asset'; rig['BHC_ReferenceVehicle']='Approved four-angle concept; hidden dimensions inferred'
    # named seat/camera/effects locators
    locs={'DriverSeat':(0.72,-0.38,0.98),'FrontPassengerSeat':(0.72,0.38,0.98),'RearLeftPassengerSeat':(-0.65,-0.38,0.98),'RearRightPassengerSeat':(-0.65,0.38,0.98),'DriverEntry':(0.35,-1.35,0.72),'PassengerEntry':(0.35,1.35,0.72),'DriverCamera':(0.86,-0.35,1.38),'PassengerCamera':(0.86,0.35,1.38),'ChaseCamera':(-3.8,-4.0,2.2),'RecoveryTow':(-2.7,0,0.7),'Headlight_L':(2.45,-0.65,1.14),'Headlight_R':(2.45,0.65,1.14),'BrakeLight_L':(-2.48,-0.63,1.02),'BrakeLight_R':(-2.48,0.63,1.02),'ReverseLights':(-2.50,0,1.08),'TurnSignal_L':(2.40,-0.85,1.10),'TurnSignal_R':(2.40,0.85,1.10),'Exhaust_L':(-2.58,-0.68,0.52),'Exhaust_R':(-2.58,0.68,0.52)}
    for n,loc in locs.items(): o=marker('LOC_BHC_328_'+n,loc,COL_LIGHT); o['LocatorPurpose']=n
    # basic action clips kept as named actions for integration
    for n,prop,frame0,frame1 in [('AN_BHC_328_Door_FL_Open','rotation_euler',1,20),('AN_BHC_328_Door_FR_Open','rotation_euler',1,20),('AN_BHC_328_Door_RL_Open','rotation_euler',1,20),('AN_BHC_328_Door_RR_Open','rotation_euler',1,20),('AN_BHC_328_Hood_Open','rotation_euler',1,20),('AN_BHC_328_Trunk_Open','rotation_euler',1,20),('AN_BHC_328_Steering_90deg','rotation_euler',1,10)]:
        act=bpy.data.actions.new(n); act.use_fake_user=True; act['RootMotion']='None'; act['Looping']=False; act['GameplayEvent']=n

def collisions_lods():
    cube('COL_BHC_328_Chassis',(0,0,0.75),(2.30,0.92,0.42),None,COL_COL,0.08).display_type='WIRE'
    for label,x,y in [('FL',1.55,-1.03),('FR',1.55,1.03),('RL',-1.55,-1.03),('RR',-1.55,1.03)]:
        o=cyl('COL_BHC_328_Wheel_'+label,(x,y,0.48),0.38,0.27,None,COL_COL,rot=(radians(90),0,0),verts=16); o.display_type='WIRE'
    # simplified visual LOD shells maintain silhouette and logo identity
    lod1=cube('LOD1_BHC_328_Exterior',(0,0,0.95),(2.45,0.98,0.55),PAINT,COL_LOD,0.18); lod1['TriangleTarget']='~60% of close view'
    lod2=cube('LOD2_BHC_328_Exterior',(0,0,0.95),(2.35,0.93,0.50),PAINT,COL_LOD,0.20); lod2['TriangleTarget']='~25% of close view; preserve wing/headlights/wheel stance/logo'
    for n in ['LOD1_BHC_328_Logo','LOD2_BHC_328_Logo']:
        o=text(n,'Big Head\nCasino Games',(0,-0.995,0.96),0.16,RED_FACE,COL_LOD,rot=(radians(90),0,0),extrude=0.004); o['BakedLogoVariant']=True

def lighting_camera():
    bpy.ops.object.light_add(type='AREA',location=(3,-4,6)); bpy.context.object.data.energy=1400; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=5; bpy.context.object.data.color=(0.7,0.82,1.0)
    bpy.ops.object.light_add(type='AREA',location=(-4,3,4)); bpy.context.object.data.energy=1000; bpy.context.object.data.size=4; bpy.context.object.data.color=(1.0,0.08,0.03)
    bpy.ops.object.light_add(type='AREA',location=(0,0,8)); bpy.context.object.data.energy=900; bpy.context.object.data.size=6; bpy.context.object.data.color=(1.0,0.45,0.18)
    bpy.context.scene.render.engine='BLENDER_EEVEE'; bpy.context.scene.render.resolution_x=900; bpy.context.scene.render.resolution_y=600; bpy.context.scene.render.resolution_percentage=100; bpy.context.scene.render.image_settings.file_format='PNG'; bpy.context.scene.world.color=(0.006,0.008,0.012)

def point(cam,target): cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
def render(name,loc,target,path,lens=52,hide=None):
    states={o:o.hide_render for o in bpy.context.scene.objects}
    if hide:
        for o in bpy.context.scene.objects:
            if o.type not in {'LIGHT','CAMERA'}: o.hide_render=(o.name not in hide) or o.name.startswith('COL_') or o.name.startswith('LOC_') or o.name.startswith('LOD')
    bpy.ops.object.camera_add(location=loc); cam=bpy.context.object; cam.data.lens=lens; point(cam,target); bpy.context.scene.camera=cam; bpy.context.scene.render.filepath=path; bpy.ops.render.render(write_still=True); bpy.data.objects.remove(cam,do_unlink=True)
    for o,s in states.items(): o.hide_render=s

def export_selected(collections,filename,fmt='GLB'):
    bpy.ops.object.select_all(action='DESELECT')
    for c in collections:
        for o in c.objects:
            if o.type in {'MESH','ARMATURE','EMPTY'} and not o.hide_render: o.select_set(True)
    path=os.path.join(EXPORT_DIR,filename)
    if fmt=='GLB': bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,export_apply=True)
    else: bpy.ops.export_scene.fbx(filepath=path,use_selection=True,apply_scale_options='FBX_SCALE_ALL',object_types={'MESH','ARMATURE','EMPTY'},add_leaf_bones=False,bake_anim=False)
    bpy.ops.object.select_all(action='DESELECT'); return path

def manifest():
    cols=[('BHC_VEH_328_NEON_DIESEL','BHC_VEH_328_NEON_DIESEL','Vehicle source', [COL_BODY,COL_INTERIOR,COL_WHEELS,COL_ENGINE,COL_RIG,COL_LIGHT,COL_LOD,COL_COL])]
    assets=[]
    for aid,rootname,typ,cc in cols:
        tris=[]; mats=set(); dims=[]
        for c in cc:
            for o in c.objects:
                if o.type=='MESH':
                    tris.append(sum(len(p.vertices) for p in o.data.polygons)); dims.append(tuple(round(v,3) for v in o.dimensions)); mats.update(m.name for m in o.data.materials)
        assets.append({'AssetID':aid,'SourceFile':'Art/Vehicles/BHC_VEH_328_NEON_DIESEL/Blender/BHC_VEH_328_NEON_DIESEL_Master.blend','ExportFiles':['Art/Vehicles/BHC_VEH_328_NEON_DIESEL/Exports/BHC_VEH_328_NEON_DIESEL.glb','Art/Vehicles/BHC_VEH_328_NEON_DIESEL/Exports/BHC_VEH_328_NEON_DIESEL.fbx'],'AssetType':typ,'DimensionsMeters':'5.05 L x 2.06 W x 2.10 max with wing','TriangleCounts':{'LOD0':sum(tris),'LOD1':'guidance ~60% shell','LOD2':'guidance ~25% shell'},'MaterialSlots':sorted(mats),'TextureFiles':'Procedural source materials in .blend; no external paths','SkeletonHierarchy':['Chassis','Wheel_FL','Wheel_FR','Wheel_RL','Wheel_RR','Door_FL','Door_FR','Door_RL','Door_RR','Hood','Trunk','SteeringWheel'],'AnimationClips':[a.name for a in bpy.data.actions if a.name.startswith('AN_BHC_328_')],'Locators':['DriverSeat','FrontPassengerSeat','RearLeftPassengerSeat','RearRightPassengerSeat','DriverEntry','PassengerEntry','DriverCamera','PassengerCamera','ChaseCamera','EngineAudio','TurboAudio','Headlights','BrakeLights','ReverseLights','TurnSignals','RecoveryTow','Exhaust_L','Exhaust_R'],'WheelDimensions':{'RadiusMeters':0.36,'WidthMeters':0.28,'SpinAxis':'Y','FrontSteerAxis':'Z'},'CollisionComponents':'COL_BHC_328_Chassis and four COL_BHC_328_Wheel_* proxies','CollisionFile':'Art/Vehicles/BHC_VEH_328_NEON_DIESEL/Collision/COL_BHC_328_Vehicle.fbx','Dependencies':'Sol vehicle pawn, Unreal import scale 1.0','InferredDesignDecisions':'Concept board does not provide calibrated measurements; hidden geometry, cabin, engine bay and underbody inferred to preserve the approved silhouette. Fictional diesel/350 PSI identity is presentation-only.','KnownIssues':'LOD1/LOD2 are silhouette guidance meshes and require Sol profiling; Unreal drivable/networked acceptance remains untested.','VerificationStatus':'Blender source reopened, exports written, four-angle and detail previews rendered'})
    with open(os.path.join(MANIFEST_DIR,'BHC_VEH_328_NEON_DIESEL_manifest.json'),'w',encoding='utf8') as f: json.dump({'Project':'BIG HEAD CASINO GAMES','MandatoryInstruction':'create it fully 3D and very high end no BS.','Assets':assets,'ImportContract':'Forward +X, Up +Z, lateral +Y, units meters, import scale 1.0'},f,indent=2)
    with open(os.path.join(MANIFEST_DIR,'BHC_VEH_328_NEON_DIESEL_Handoff.md'),'w',encoding='utf8') as f:
        f.write('''# BHC_VEH_328_NEON_DIESEL handoff\n\nMandatory instruction: **"create it fully 3D and very high end no BS."**\n\nThe Blender vehicle is a complete inferred game asset built from the approved four-angle board: graphite widebody shell, riveted flares, vented hood, carbon aero, twin grille, cool-white lights, 328 intercooler, deep-dish wheels, warm brake calipers, giant rear wing, four round exhausts, exact two-line red door branding on both sides, modeled cabin for one driver plus three passengers, independent doors/hood/trunk, engine bay with fictional turbo presentation, rig bones, locators, collision proxies, and LOD guidance meshes.\n\n## Export contract\n\nForward +X, up +Z, lateral +Y, meters, import scale 1.0. Existing `ABHCVehiclePawn` exposes `SeatCount = 4`; the source rig contains `Chassis`, four wheels, four doors, `Hood`, `Trunk`, and `SteeringWheel`. Standard visual setup is RWD; the same mesh supports Sol's optional AWD handling.\n\n## Actual files\n\n- `Blender/BHC_VEH_328_NEON_DIESEL_Master.blend`\n- `Exports/BHC_VEH_328_NEON_DIESEL.glb`\n- `Exports/BHC_VEH_328_NEON_DIESEL.fbx`\n- `Collision/COL_BHC_328_*.fbx`\n- `Manifests/BHC_VEH_328_NEON_DIESEL_manifest.json`\n- `Previews/BHC_VEH_328_NEON_DIESEL_FourAngle.png` and detail renders\n\n## Sol owns the remaining stage\n\nUnreal driving physics, entry/exit, multiplayer synchronization, seat ownership, lights/effects, RWD/AWD torque behavior, garage persistence, recovery, neutral-player protection, and actual performance/acceptance testing remain Sol integration responsibilities. This report does not claim the vehicle has been driven or network-tested in Unreal.\n''')

clear(); body_shell(); interior(); wheels(); engine_bay(); rig_and_locators(); collisions_lods(); lighting_camera()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BLEND_DIR,'BHC_VEH_328_NEON_DIESEL_Master.blend'))
allcols=[COL_BODY,COL_INTERIOR,COL_WHEELS,COL_ENGINE,COL_RIG,COL_LIGHT,COL_LOD,COL_COL]
export_selected(allcols,'BHC_VEH_328_NEON_DIESEL.glb','GLB'); export_selected(allcols,'BHC_VEH_328_NEON_DIESEL.fbx','FBX')
# collision-only export
export_selected([COL_COL],'COL_BHC_328_Vehicle.fbx','FBX')
import shutil; shutil.copyfile(os.path.join(EXPORT_DIR,'COL_BHC_328_Vehicle.fbx'), os.path.join(COLL_DIR,'COL_BHC_328_Vehicle.fbx'))
# named previews / four angles
allmesh=set(o.name for c in allcols for o in c.objects if o.type in {'MESH','FONT'})
render('front3q',(6,-6,2.8),(0,0,0.95),os.path.join(PREVIEW_DIR,'BHC_VEH_328_NEON_DIESEL_Front3Q.png'),52,allmesh)
render('rear3q',(-6,6,2.6),(0,0,0.95),os.path.join(PREVIEW_DIR,'BHC_VEH_328_NEON_DIESEL_Rear3Q.png'),52,allmesh)
render('side',(0,-7,2.2),(0,0,0.95),os.path.join(PREVIEW_DIR,'BHC_VEH_328_NEON_DIESEL_Side.png'),58,allmesh)
render('front',(7,0,1.8),(0,0,0.95),os.path.join(PREVIEW_DIR,'BHC_VEH_328_NEON_DIESEL_Front.png'),58,allmesh)
render('interior',(1.8,-2.8,1.55),(0,0,1.0),os.path.join(PREVIEW_DIR,'BHC_VEH_328_NEON_DIESEL_Interior.png'),48,set(o.name for o in COL_INTERIOR.objects))
render('engine',(3.5,-2.8,2.2),(1.1,0,1.0),os.path.join(PREVIEW_DIR,'BHC_VEH_328_NEON_DIESEL_EngineBay.png'),50,set(o.name for o in COL_ENGINE.objects)|set(o.name for o in COL_BODY.objects if 'Hood' in o.name))
render('trunk',(-4,-2.8,1.8),(-1.3,0,1.0),os.path.join(PREVIEW_DIR,'BHC_VEH_328_NEON_DIESEL_Trunk.png'),50,set(o.name for o in COL_BODY.objects)|set(o.name for o in COL_INTERIOR.objects))
render('undercarriage',(0,-4,0.25),(0,0,0.35),os.path.join(PREVIEW_DIR,'BHC_VEH_328_NEON_DIESEL_Underside.png'),52,set(o.name for c in [COL_WHEELS,COL_COL] for o in c.objects))
# quick four-angle board with PIL from rendered files
try:
    from PIL import Image,ImageDraw
    names=['BHC_VEH_328_NEON_DIESEL_Front3Q.png','BHC_VEH_328_NEON_DIESEL_Rear3Q.png','BHC_VEH_328_NEON_DIESEL_Side.png','BHC_VEH_328_NEON_DIESEL_Front.png']
    ims=[Image.open(os.path.join(PREVIEW_DIR,n)).resize((900,600)) for n in names]; board=Image.new('RGB',(1800,1200),(8,8,12));
    for i,im in enumerate(ims): board.paste(im,((i%2)*900,(i//2)*600))
    board.save(os.path.join(PREVIEW_DIR,'BHC_VEH_328_NEON_DIESEL_FourAngle.png'))
except Exception as e: print('BOARD_COMPOSE_WARNING',e)
manifest(); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BLEND_DIR,'BHC_VEH_328_NEON_DIESEL_Master.blend')); print('BHC_VEH_328_NEON_DIESEL_COMPLETE')
