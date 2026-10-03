import bpy, os, json, csv, math
from mathutils import Vector
from math import radians

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..','..'))
BASE=os.path.join(ROOT,'Art','City','63rd_Street_Batch')
BLEND_DIR=os.path.join(BASE,'Blender'); EXPORT_DIR=os.path.join(BASE,'Exports'); PREVIEW_DIR=os.path.join(BASE,'Previews'); MANIFEST_DIR=os.path.join(BASE,'Manifests'); COLL_DIR=os.path.join(BASE,'Collision')
for d in [BLEND_DIR,EXPORT_DIR,PREVIEW_DIR,MANIFEST_DIR,COLL_DIR]: os.makedirs(d,exist_ok=True)

def clear(): bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def collection(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children.keys(): bpy.context.scene.collection.children.link(c)
    return c
def move(o,c):
    for old in list(o.users_collection): old.objects.unlink(o)
    c.objects.link(o)
def mat(name,color,metallic=0.0,rough=0.45,emission=None):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metallic; bs.inputs['Roughness'].default_value=rough
    if emission: bs.inputs['Emission Color'].default_value=(*emission,1); bs.inputs['Emission Strength'].default_value=4
    return m
ASPHALT=mat('M_BHC_Asphalt',(0.035,0.04,0.045),0.05,0.9); CONCRETE=mat('M_BHC_Concrete',(0.22,0.24,0.26),0.0,0.85); CURB=mat('M_BHC_Curb',(0.34,0.36,0.38),0.0,0.7); LANE=mat('M_BHC_LaneMark',(0.87,0.8,0.52),0.0,0.45); BRICK=mat('M_BHC_Brick',(0.28,0.045,0.025),0.0,0.8); PLASTER=mat('M_BHC_Plaster',(0.55,0.49,0.40),0.0,0.75); STONE=mat('M_BHC_Stone',(0.16,0.17,0.18),0.05,0.72); WOOD=mat('M_BHC_Wood',(0.18,0.06,0.02),0.05,0.5); DARKWOOD=mat('M_BHC_DarkWood',(0.055,0.02,0.01),0.1,0.42); METAL=mat('M_BHC_Metal',(0.17,0.19,0.22),0.72,0.3); GLASS=mat('M_BHC_Glass',(0.03,0.08,0.12),0.1,0.15); RED=mat('M_BHC_RedAccent',(0.52,0.02,0.025),0.2,0.35,(0.8,0.01,0.01)); GOLD=mat('M_BHC_Brass',(0.64,0.30,0.05),0.82,0.25); GREEN=mat('M_BHC_Felt',(0.02,0.22,0.09),0.0,0.88); TILE=mat('M_BHC_Tile',(0.38,0.40,0.42),0.0,0.62); SKIN=mat('M_BHC_Skin',(0.48,0.16,0.09),0.0,0.52); WHITE=mat('M_BHC_White',(0.8,0.82,0.78),0.0,0.34); FOOD=mat('M_BHC_Food',(0.63,0.24,0.06),0.0,0.62); LEMON=mat('M_BHC_Lemon',(0.9,0.65,0.08),0.0,0.5); SEA=mat('M_BHC_Seafood',(0.26,0.42,0.46),0.0,0.48); BLACK=mat('M_BHC_Black',(0.004,0.005,0.006),0.0,0.6)
def assign(o,m):
    if m: o.data.materials.append(m)
    return o
def smooth(o):
    if hasattr(o.data,'polygons'):
        for p in o.data.polygons:p.use_smooth=True
    return o
def bevel(o,w=0.04,s=3):
    if o.type=='MESH': mod=o.modifiers.new('BHC_Bevel','BEVEL'); mod.width=w; mod.segments=s
    return o
def cube(n,loc,scale,m=None,c=None,bev=0.03):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); assign(o,m); bevel(o,bev,3); move(o,c) if c else None; return o
def cyl(n,loc,r,depth,m=None,c=None,rot=(0,0,0),verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot); o=bpy.context.object; o.name=n; assign(o,m); smooth(o); move(o,c) if c else None; return o
def sphere(n,loc,scale,m=None,c=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); assign(o,m); smooth(o); move(o,c) if c else None; return o
def torus(n,loc,major,minor,m=None,c=None,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=48,minor_segments=12,location=loc,rotation=rot); o=bpy.context.object; o.name=n; assign(o,m); smooth(o); move(o,c) if c else None; return o
def text(n,body,loc,size,m,c,rot=(radians(90),0,0),extrude=0.01):
    cu=bpy.data.curves.new(n,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=extrude; cu.bevel_depth=0.003; o=bpy.data.objects.new(n,cu); c.objects.link(o); o.location=loc; o.rotation_euler=rot; assign(o,m); return o
def marker(n,loc,c): o=cube(n,loc,(0.03,0.03,0.03),GOLD,c,0.005); o.hide_render=True; return o
def uv(o):
    if o.type=='MESH': bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=0.03); bpy.ops.object.mode_set(mode='OBJECT'); o.select_set(False)

CITY=collection('BHC_CITY_Overview_20x20km'); ROADS=collection('BHC_63RD_Roads'); HOUSE=collection('BHC_BLD_63RD_HOUSE_010'); SUB=collection('BHC_BLD_63RD_SUBURBAN_011'); REST=collection('BHC_REST_63RD_CHOPHOUSE'); FOODCOL=collection('BHC_Food_63rdChophouse'); STAFF=collection('BHC_NPC_RestaurantStaff'); COLL=collection('BHC_Collision')

def build_roads():
    # 63rd Street east-west, cross street, sidewalks, and parking designed around 5.05m car
    cube('SM_BHC_63rd_Asphalt',(0,0,0),(60,5.5,0.08),ASPHALT,ROADS,0.01); cube('SM_BHC_63rd_Sidewalk_N',(0,7.0,0.12),(60,1.2,0.12),CONCRETE,ROADS,0.03); cube('SM_BHC_63rd_Sidewalk_S',(0,-7.0,0.12),(60,1.2,0.12),CONCRETE,ROADS,0.03)
    cube('SM_BHC_63rd_CrossRoad',(0,0,0),(5.5,28,0.08),ASPHALT,ROADS,0.01)
    for y in (-1.85,1.85):
        for x in range(-55,56,10): cube('SM_BHC_63rd_LaneDash',(x,y,0.09),(2.8,0.055,0.012),LANE,ROADS,0.005)
    for x in (-5,-4,-3,-2,-1,0,1,2,3,4,5): cube('SM_BHC_63rd_Crosswalk',(x,0,0.10),(0.28,5.4,0.012),WHITE,ROADS,0.004)
    for y in (-5.5,5.5): cube('SM_BHC_63rd_Curb',(0,y,0.18),(60,0.18,0.18),CURB,ROADS,0.02)
    # drains, manholes, ramps, streetlights, signs, benches, planters
    for x in (-35,-15,15,35): cyl('SM_BHC_63rd_Manhole',(x,-4.8,0.18),0.35,0.04,METAL,ROADS,verts=32); cyl('SM_BHC_63rd_StormDrain',(x,5.0,0.20),0.18,0.03,BLACK,ROADS,verts=24)
    for x in (-48,-24,0,24,48):
        for y in (-8.6,8.6): cyl('SM_BHC_63rd_StreetlightPole',(x,y,3.2),0.08,6.4,METAL,ROADS,verts=20); sphere('SM_BHC_63rd_Streetlight',(x,y,6.45),(0.22,0.22,0.12),WHITE,ROADS)
    for y in (-8.1,8.1): text('SM_BHC_63rd_StreetSign','63RD STREET',(0,y,2.8),0.32,WHITE,ROADS,rot=(radians(90),0,0),extrude=0.015)
    # diagonal parking north and south, 6m bays; widebody reference metadata
    for x in range(-45,46,9):
        cube('SM_BHC_63rd_ParkingBay_N',(x,9.3,0.14),(3.8,1.0,0.02),LANE,ROADS,0.01); cube('SM_BHC_63rd_ParkingBay_S',(x,-9.3,0.14),(3.8,1.0,0.02),LANE,ROADS,0.01)
    for y in (-8.1,8.1):
        for x in (-40,-20,0,20,40): cube('SM_BHC_63rd_Planter',(x,y,0.45),(0.35,0.35,0.25),STONE,ROADS,0.05); sphere('SM_BHC_63rd_Tree',(x,y,1.7),(0.8,0.8,1.2),GREEN,ROADS)
    cube('SM_BHC_63rd_BusStop',(30,8.5,1.4),(1.6,0.08,1.2),GLASS,ROADS,0.04); cube('SM_BHC_63rd_BusBench',(30,8.1,0.65),(0.8,0.22,0.08),WOOD,ROADS,0.03); text('SM_BHC_63rd_BusSign','63RD / CHOPHOUSE',(30,8.35,2.6),0.15,WHITE,ROADS,rot=(radians(90),0,0),extrude=0.008)
    # route checks and collision proxies
    col=cube('COL_BHC_63rd_RoadSurface',(0,0,0),(60,5.5,0.08),None,COLL,0.01); col.display_type='WIRE'; col.hide_render=True
    ROADS['VehicleClearance']='Designed for BHC_VEH_328_NEON_DIESEL: 5.05m length, 2.06m width; 11m intersection radius and 6m parking bays'; ROADS['WorldCoordinates']='63rd Street east-west x=-60..60, y=0; connected crossroad at x=0'

def room_shell(c,prefix,origin,w,d,h,material):
    x,y=origin; cube(prefix+'_Floor',(x,y,0.25),(w/2,d/2,0.12),material,c,0.04); cube(prefix+'_Ceiling',(x,y,h),(w/2,d/2,0.10),material,c,0.04)
    cube(prefix+'_Wall_N',(x,y+d/2, h/2),(w/2,0.10,h/2),material,c,0.03); cube(prefix+'_Wall_S',(x,y-d/2,h/2),(w/2,0.10,h/2),material,c,0.03); cube(prefix+'_Wall_E',(x+w/2,y,h/2),(0.10,d/2,h/2),material,c,0.03); cube(prefix+'_Wall_W',(x-w/2,y,h/2),(0.10,d/2,h/2),material,c,0.03)

def furniture_house(c,origin,kind):
    x,y=origin
    # living, kitchen, bedrooms, bath, utility and furniture; local floor plans are walkable
    room_shell(c,'SM_'+kind+'_Living',(x,y+3.2),4.8,3.6,2.8,PLASTER); room_shell(c,'SM_'+kind+'_Kitchen',(x,y-1.0),4.8,2.2,2.8,PLASTER); room_shell(c,'SM_'+kind+'_BedroomA',(x-2.2,y+7.0),2.0,2.6,2.8,PLASTER); room_shell(c,'SM_'+kind+'_BedroomB',(x+2.2,y+7.0),2.0,2.6,2.8,PLASTER); room_shell(c,'SM_'+kind+'_Bath',(x+2.2,y+4.7),2.0,1.6,2.8,TILE); room_shell(c,'SM_'+kind+'_Utility',(x-2.2,y-2.8),2.0,1.4,2.8,PLASTER)
    cube('SM_'+kind+'_Sofa',(x,y+3.0,0.65),(1.3,0.4,0.35),WOOD,c,0.10); cube('SM_'+kind+'_CoffeeTable',(x,y+2.0,0.45),(0.7,0.45,0.10),WOOD,c,0.04); cube('SM_'+kind+'_KitchenCounter',(x,y-1.55,1.0),(2.0,0.28,0.4),DARKWOOD,c,0.05); cube('SM_'+kind+'_Fridge',(x-1.7,y-0.8,1.1),(0.28,0.30,0.85),METAL,c,0.05); cube('SM_'+kind+'_DiningTable',(x,y-0.3,0.55),(0.7,0.5,0.12),WOOD,c,0.04)
    for bx in (x-2.2,x+2.2): cube('SM_'+kind+'_Bed',(bx,y+7.0,0.48),(0.75,1.0,0.18),WOOD,c,0.04); cube('SM_'+kind+'_BedPillow',(bx,y+6.35,0.70),(0.55,0.28,0.12),WHITE,c,0.03)
    cube('SM_'+kind+'_Toilet',(x+2.2,y+4.65,0.45),(0.26,0.40,0.35),WHITE,c,0.05); cube('SM_'+kind+'_Shower',(x+2.2,y+5.25,1.1),(0.65,0.5,1.0),GLASS,c,0.04); cube('SM_'+kind+'_Washer',(x-2.2,y-2.8,0.7),(0.35,0.35,0.55),WHITE,c,0.04); cube('SM_'+kind+'_DiningChair',(x-0.8,y-0.3,0.55),(0.22,0.22,0.45),WOOD,c,0.03); cube('SM_'+kind+'_DiningChair2',(x+0.8,y-0.3,0.55),(0.22,0.22,0.45),WOOD,c,0.03)
    for n,loc in [('FrontDoor',(x,y-4.9,1.2)),('BackDoor',(x,y+9.0,1.2)),('KitchenSink',(x+1.3,y-1.8,1.2))]: marker('LOC_'+kind+'_'+n,loc,c)

def build_houses():
    # single-story detached at 63rd / Alder, complete walk-in plan
    cube('SM_BHC_63rd_House_010_Exterior',(46,17,1.6),(4.7,4.0,1.6),PLASTER,HOUSE,0.10); cube('SM_BHC_63rd_House_010_Roof',(46,17,3.4),(5.0,4.3,0.18),DARKWOOD,HOUSE,0.08); cube('SM_BHC_63rd_House_010_Porch',(46,12.5,0.55),(2.0,0.75,0.15),WOOD,HOUSE,0.04); cube('SM_BHC_63rd_House_010_Driveway',(46,10.5,0.10),(2.3,2.5,0.03),CONCRETE,HOUSE,0.02); furniture_house(HOUSE,(46,17),'BHC_63rd_House_010'); text('SM_BHC_63rd_House_010_Address','63RD STREET 101',(46,12.3,2.1),0.17,WHITE,HOUSE,rot=(radians(90),0,0),extrude=0.008); HOUSE['BuildingID']='BHC_BLD_63RD_HOUSE_010'; HOUSE['Address']='101 63rd Street'; HOUSE['Rooms']='Living,K​​itchen,Dining,BedroomA,BedroomB,Bath,Utility'; HOUSE['AccessRoute']='Sidewalk->FrontDoor->Living->Hallway->All rooms; BackDoor';
    # two-story suburban house with stair and garage
    cube('SM_BHC_63rd_Suburban_011_Exterior',(67,17,2.3),(5.2,4.4,2.3),BRICK,SUB,0.12); cube('SM_BHC_63rd_Suburban_011_Roof',(67,17,4.9),(5.4,4.6,0.22),DARKWOOD,SUB,0.10); cube('SM_BHC_63rd_Suburban_011_Garage',(67,12.2,1.25),(2.0,1.7,1.25),STONE,SUB,0.08); cube('SM_BHC_63rd_Suburban_011_Driveway',(67,9.7,0.10),(2.1,2.2,0.03),CONCRETE,SUB,0.02)
    furniture_house(SUB,(67,17),'BHC_63rd_Suburban_011'); cube('SM_BHC_63rd_Suburban_011_Stair',(67,19.0,1.6),(0.45,1.3,1.6),WOOD,SUB,0.04); room_shell(SUB,'SM_BHC_63rd_Suburban_011_UpperHall',(67,17),9.2,8.0,4.8,PLASTER); text('SM_BHC_63rd_Suburban_011_Address','63RD STREET 103',(67,12.3,2.2),0.17,WHITE,SUB,rot=(radians(90),0,0),extrude=0.008); SUB['BuildingID']='BHC_BLD_63RD_SUBURBAN_011'; SUB['Address']='103 63rd Street'; SUB['Rooms']='Ground:Living,Kitchen,Dining,Bath,Utility,Garage; Upper:BedroomA,BedroomB,Bath,Hall'; SUB['AccessRoute']='Sidewalk->FrontDoor->GroundHall->Stair->UpperHall; GarageDoor'

def table_setting(c,x,y,idx,crew=True):
    cube('SM_BHC_REST_63RD_Table_%02d'%idx,(x,y,1.0),(0.85 if crew else 0.55,0.55,0.08),WOOD,c,0.05); cyl('SM_BHC_REST_63RD_Plate_%02d'%idx,(x,y,1.14),0.20,0.025,WHITE,c,verts=32); marker('LOC_BHC_REST_63RD_Table_%02d_ServicePass'%idx,(x+0.95,y,1.05),c)
    seats=4 if crew else 2
    for s in range(seats):
        a=2*math.pi*s/seats; cube('SM_BHC_REST_63RD_Seat_%02d_%02d'%(idx,s),(x+1.2*math.cos(a),y+0.9*math.sin(a),0.6),(0.25,0.25,0.35),RED,c,0.08); marker('LOC_BHC_REST_63RD_Table_%02d_Seat_%02d'%(idx,s),(x+1.2*math.cos(a),y+0.9*math.sin(a),0.95),c)

def build_restaurant():
    # 63rd Street Chophouse at (15,-18), open interior shell, connected to sidewalk and rear service lane
    cube('SM_BHC_REST_63RD_Exterior',(15,-18,2.4),(7.8,4.8,2.4),BRICK,REST,0.12); cube('SM_BHC_REST_63RD_FacadeTrim',(15,-13.1,2.4),(7.3,0.08,2.1),WOOD,REST,0.04); cube('SM_BHC_REST_63RD_Entrance',(15,-13.25,1.4),(1.2,0.08,1.4),GLASS,REST,0.03); text('SM_BHC_REST_63RD_Sign','63RD STREET CHOPHOUSE',(15,-13.35,4.0),0.34,RED,REST,rot=(radians(90),0,0),extrude=0.012)
    # floorplan: host/waiting, dining, restroom, kitchen, storage, dish, rear door
    room_shell(REST,'SM_BHC_REST_63RD_Dining',(15,-17),7.2,4.0,4.2,DARKWOOD); room_shell(REST,'SM_BHC_REST_63RD_Kitchen',(15,-21.3),7.2,2.4,4.2,STONE); room_shell(REST,'SM_BHC_REST_63RD_Storage',(20.8,-21.3),1.7,2.4,4.2,STONE); room_shell(REST,'SM_BHC_REST_63RD_Restroom_M',(9.2,-21.3),1.7,1.2,4.2,TILE); room_shell(REST,'SM_BHC_REST_63RD_Restroom_F',(11.0,-21.3),1.7,1.2,4.2,TILE)
    cube('SM_BHC_REST_63RD_HostDesk',(15,-14.9,1.1),(0.8,0.25,0.5),WOOD,REST,0.05); marker('LOC_BHC_REST_63RD_Host',(15,-14.5,1.3),REST); cube('SM_BHC_REST_63RD_WaitingBench',(12.4,-14.8,0.65),(1.0,0.28,0.3),RED,REST,0.08)
    table_setting(REST,12.5,-17.5,1,False); table_setting(REST,17.5,-17.5,2,False); table_setting(REST,15,-16.5,3,True); table_setting(REST,15,-18.7,4,True)
    # booths and open-view grill
    for x in (11.2,18.8): cube('SM_BHC_REST_63RD_BoothSeat',(x,-18.8,0.65),(1.1,0.38,0.35),RED,REST,0.10); cube('SM_BHC_REST_63RD_BoothBack',(x,-19.2,1.25),(1.1,0.08,0.8),RED,REST,0.04)
    cube('SM_BHC_REST_63RD_GrillLine',(15,-20.25,1.0),(2.8,0.55,0.5),METAL,REST,0.05); cube('SM_BHC_REST_63RD_GrillFire',(15,-20.25,1.58),(2.2,0.3,0.05),RED,REST,0.02); text('SM_BHC_REST_63RD_GrillSign','OPEN VIEW GRILL',(15,-19.62,2.0),0.18,WHITE,REST,rot=(radians(90),0,0),extrude=0.008)
    # kitchen workflow storage -> prep -> cook -> plating -> pass -> dining
    cube('SM_BHC_REST_63RD_ColdStorage',(20.8,-21.3,1.1),(0.65,0.55,0.9),GLASS,REST,0.04); cube('SM_BHC_REST_63RD_DryStorage',(19.8,-21.3,1.2),(0.45,0.55,1.0),WOOD,REST,0.04); cube('SM_BHC_REST_63RD_PrepCounter',(17.7,-21.3,1.0),(1.1,0.45,0.45),WOOD,REST,0.04); cube('SM_BHC_REST_63RD_Oven',(15.8,-21.3,1.1),(0.5,0.45,0.8),METAL,REST,0.04); cube('SM_BHC_REST_63RD_PanStation',(14.2,-21.3,1.0),(0.6,0.45,0.45),METAL,REST,0.04); cube('SM_BHC_REST_63RD_Plating',(12.6,-21.3,1.0),(0.6,0.45,0.45),WHITE,REST,0.04); cube('SM_BHC_REST_63RD_ServicePass',(12.6,-19.95,1.3),(1.8,0.12,0.8),WOOD,REST,0.03); cube('SM_BHC_REST_63RD_Dishwash',(19.7,-19.95,1.0),(0.8,0.4,0.45),TILE,REST,0.04); cube('SM_BHC_REST_63RD_RearDeliveryDoor',(22.7,-21.3,1.4),(0.08,0.8,1.4),METAL,REST,0.03)
    for n,loc in [('Entrance',(15,-13.6,1.0)),('Host',(15,-14.5,1.2)),('KitchenDoor',(15,-19.1,1.2)),('RearDelivery',(22.4,-21.3,1.2)),('ServicePass',(12.6,-19.6,1.2)),('DishReturn',(19.7,-19.6,1.2))]: marker('LOC_BHC_REST_63RD_'+n,loc,REST)
    REST['RestaurantID']='BHC_REST_63RD_CHOPHOUSE'; REST['Name']='63RD STREET CHOPHOUSE'; REST['Address']='15 63rd Street'; REST['Workflow']='Storage -> Preparation -> Cooking -> Plating -> ServicePass -> Dining -> DishReturn'; REST['Tables']='Table_01(2), Table_02(2), Table_03(4), Table_04(4)'; REST['StaffRoutes']='Entrance/Host -> Dining -> KitchenDoor -> ServicePass -> Dining'

MENU=[('Loaded Potato Skins',15,'starter'),('Crispy Onion Rings',12,'starter'),('63rd Street Sirloin',65,'main'),('Chophouse Ribeye',85,'main'),('Steakhouse Burger',38,'main'),('Smoky Vegetable Skillet',34,'main'),('Mac and Cheese',12,'side'),('Garlic Mashed Potatoes',11,'side'),('Brownie Sundae',17,'dessert'),('Apple Crumble',16,'dessert'),('House Lemonade',7,'drink'),('Cola',6,'drink')]
def dish_asset(name,price,kind,i):
    x=(i%4)*1.9-2.85; y=(i//4)*1.5+2.0; z=0.3; plate=cyl('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Plate',(x,y,z),0.46,0.05,WHITE,FOODCOL,verts=32); plate['MenuItem']=name; plate['PriceCredits']=price; plate['PreparationState']='raw -> prep -> cook -> plate -> served -> eaten -> dirty'
    if kind=='drink': cyl('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Glass',(x,y,z+0.32),0.18,0.55,GLASS,FOODCOL,verts=24); cyl('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Liquid',(x,y,z+0.48),0.15,0.03,LEMON if 'Lemon' in name else RED,FOODCOL,verts=24)
    elif 'Burger' in name: cyl('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Bun',(x,y,z+0.22),0.28,0.12,FOOD,FOODCOL,verts=24); cube('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Patty',(x,y,z+0.33),(0.22,0.22,0.05),FOOD,FOODCOL,0.03)
    elif 'Ribeye' in name or 'Sirloin' in name: cube('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Steak',(x,y,z+0.13),(0.28,0.18,0.07),FOOD,FOODCOL,0.03); sphere('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_HerbButter',(x+0.14,y,z+0.23),(0.07,0.07,0.05),LEMON,FOODCOL)
    elif 'Potato' in name or 'Mac' in name: sphere('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Portion',(x,y,z+0.16),(0.25,0.20,0.14),FOOD,FOODCOL)
    elif 'Onion' in name: torus('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Rings',(x,y,z+0.16),0.20,0.06,FOOD,FOODCOL)
    elif 'Sundae' in name or 'Crumble' in name: sphere('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Dessert',(x,y,z+0.18),(0.22,0.22,0.18),FOOD,FOODCOL)
    else: sphere('SM_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Plated',(x,y,z+0.15),(0.22,0.20,0.12),FOOD,FOODCOL)
    marker('ATT_BHC_FOOD_63RD_'+name.replace(' ','_')+'_ChefHand',(x,y,z+0.4),FOODCOL); marker('ATT_BHC_FOOD_63RD_'+name.replace(' ','_')+'_Tray',(x,y,z+0.05),FOODCOL)
def build_food():
    for i,(n,p,k) in enumerate(MENU): dish_asset(n,p,k,i)
    # shared tableware and state props
    for i in range(4): cyl('SM_BHC_FOOD_63RD_EmptyPlate_%02d'%i,(8+i,4,0.3),0.46,0.05,WHITE,FOODCOL,verts=32); cyl('SM_BHC_FOOD_63RD_DirtyPlate_%02d'%i,(8+i,5.4,0.3),0.46,0.05,TILE,FOODCOL,verts=32); cube('SM_BHC_FOOD_63RD_Cutlery_%02d'%i,(8+i,6.6,0.35),(.4,.03,.02),METAL,FOODCOL,0.01); cube('SM_BHC_FOOD_63RD_ServingTray_%02d'%i,(8+i,8,0.35),(.55,.35,.03),WOOD,FOODCOL,0.03)

def build_staff():
    # three adult big-head service roles, shared rig and production clip inventory
    arm=bpy.data.armatures.new('SK_BHC_RestaurantStaff_Rig'); rig=bpy.data.objects.new('SK_BHC_RestaurantStaff_Rig',arm); STAFF.objects.link(rig); rig.show_in_front=True; rig.display_type='WIRE'; bpy.context.view_layer.objects.active=rig; rig.select_set(True); bpy.ops.object.mode_set(mode='EDIT'); b=arm.edit_bones.new('root'); b.head=(0,0,0); b.tail=(0,0,1); head=arm.edit_bones.new('head'); head.head=(0,0,1.6); head.tail=(0,0,2.1); head.parent=b; bpy.ops.object.mode_set(mode='OBJECT'); rig.select_set(False)
    rig['CharacterScale']='Big-head adult, 1 Blender unit = 1 meter'; rig['Sockets']='hand_L,hand_R,order_pad,tray,chef_tool';
    roles=[('Host',(14,-14.5,0),GOLD),('Server',(13,-17,0),RED),('Chef',(15,-20.8,0),WHITE)]
    for role,loc,cloth in roles:
        x,y,z=loc; sphere('SK_BHC_Staff_'+role+'_Head',(x,y,1.95),(0.35,0.30,0.36),SKIN,STAFF); sphere('SK_BHC_Staff_'+role+'_Body',(x,y,1.15),(0.32,0.24,0.55),cloth,STAFF); cube('SK_BHC_Staff_'+role+'_Hands',(x,y-0.06,0.85),(0.12,0.12,0.14),SKIN,STAFF,0.03); marker('ATT_BHC_Staff_'+role+'_Tray',(x,y-0.25,0.95),STAFF); marker('ATT_BHC_Staff_'+role+'_OrderPad',(x,y-0.15,1.25),STAFF)
    for n in ['AN_BHC_Staff_Idle','AN_BHC_Staff_Walk','AN_BHC_Staff_Turn','AN_BHC_Staff_DoorInteract','AN_BHC_Staff_Greet','AN_BHC_Staff_GuideCustomers','AN_BHC_Staff_TakeOrder','AN_BHC_Staff_WriteOrderPad','AN_BHC_Staff_HandOverTicket','AN_BHC_Staff_ReadTicket','AN_BHC_Staff_CollectIngredients','AN_BHC_Staff_PrepareIngredients','AN_BHC_Staff_UseCookingStation','AN_BHC_Staff_PlateDish','AN_BHC_Staff_LiftCarryTray','AN_BHC_Staff_PlaceDish','AN_BHC_Staff_ServeDrink','AN_BHC_Staff_ClearTable','AN_BHC_Staff_CarryDirtyDishes','AN_BHC_Staff_WashDishes','AN_BHC_Staff_RecoverInterrupted']:
        a=bpy.data.actions.new(n); a.use_fake_user=True; a['Looping']=n.endswith('Idle') or n.endswith('Walk'); a['RootMotion']='None'; a['TimingMarkers']='start,contact,end'

def city_overview():
    # lightweight master layout with explicit 20x20 tile authoring grid and district anchors
    cube('SM_BHC_City_Region_Reference',(0,0,-0.6),(10000,10000,0.5),ASPHALT,CITY,0.0); CITY['RegionFootprint']='20,000m x 20,000m = 400 km²'; CITY['AuthoringGrid']='20 x 20 tiles, each 1km; local tile coordinates kept near origins'
    districts=[('Central Casino District',(-250,0),RED),('63rd Street District',(0,0),GOLD),('North Suburbs',(0,5200),GREEN),('East Residential',(5200,0),PLASTER),('West Hills Suburbs',(-5200,1200),STONE),('Harbor Dining District',(0,-5200),SEA),('Commercial and Service District',(5200,-3200),METAL)]
    for name,(x,y),m in districts: cube('SM_BHC_District_'+name.replace(' ','_'),(x,y,0),(900,900,0.05),m,CITY,0.01); text('SM_BHC_DistrictLabel_'+name.replace(' ','_'),name,(x,y,0.1),0.35,WHITE,CITY,rot=(0,0,0),extrude=0.01)
    # lightweight arterial connections to mark full-plan road hierarchy
    for y in (-5200,0,5200): cube('SM_BHC_Arterial_EW',(0,y,0),(10000,12,0.08),ASPHALT,CITY,0.01)
    for x in (-5200,0,5200): cube('SM_BHC_Arterial_NS',(x,0,0),(12,10000,0.08),ASPHALT,CITY,0.01)

def setup_render():
    bpy.ops.object.light_add(type='AREA',location=(35,-45,35)); bpy.context.object.data.energy=2500; bpy.context.object.data.size=20; bpy.context.object.data.color=(1.0,0.42,0.18); bpy.ops.object.light_add(type='AREA',location=(-30,20,25)); bpy.context.object.data.energy=1800; bpy.context.object.data.size=16; bpy.context.object.data.color=(0.18,0.35,1.0)
    bpy.context.scene.render.engine='BLENDER_EEVEE'; bpy.context.scene.render.resolution_x=1000; bpy.context.scene.render.resolution_y=700; bpy.context.scene.render.resolution_percentage=100; bpy.context.scene.render.image_settings.file_format='PNG'; bpy.context.scene.world.color=(0.008,0.01,0.016)
def render(loc,target,path,lens=45,visible=None):
    states={o:o.hide_render for o in bpy.context.scene.objects}
    if visible:
        for o in bpy.context.scene.objects:
            if o.type not in {'LIGHT','CAMERA'}: o.hide_render=(o.name not in visible) or o.name.startswith('COL_') or o.name.startswith('LOC_')
    bpy.ops.object.camera_add(location=loc); cam=bpy.context.object; cam.data.lens=lens; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.camera=cam; bpy.context.scene.render.filepath=path; bpy.ops.render.render(write_still=True); bpy.data.objects.remove(cam,do_unlink=True)
    for o,s in states.items(): o.hide_render=s
def export(colls,filename,fmt):
    bpy.ops.object.select_all(action='DESELECT')
    for c in colls:
        for o in c.objects:
            if o.type in {'MESH','ARMATURE','EMPTY','FONT'} and not o.hide_render: o.select_set(True)
    p=os.path.join(EXPORT_DIR,filename)
    if fmt=='GLB': bpy.ops.export_scene.gltf(filepath=p,export_format='GLB',use_selection=True,export_apply=True)
    else: bpy.ops.export_scene.fbx(filepath=p,use_selection=True,apply_scale_options='FBX_SCALE_ALL',object_types={'MESH','ARMATURE','EMPTY'},add_leaf_bones=False,bake_anim=False)
    bpy.ops.object.select_all(action='DESELECT'); return p

def manifests():
    assets=[('BHC_63RD_STREET_SLICE',[ROADS],'Street geometry'),('BHC_BLD_63RD_HOUSE_010',[HOUSE],'Complete single-story house'),('BHC_BLD_63RD_SUBURBAN_011',[SUB],'Complete two-story suburban house'),('BHC_REST_63RD_CHOPHOUSE',[REST],'Complete restaurant and kitchen'),('BHC_FOOD_63RD_CHOPHOUSE', [FOODCOL],'Food and tableware'),('BHC_NPC_RESTAURANT_STAFF',[STAFF],'Host/server/chef characters and rig')]
    rows=[]
    for aid,cc,typ in assets:
        tris=sum(sum(len(p.vertices) for p in o.data.polygons) for c in cc for o in c.objects if o.type=='MESH'); rows.append({'AssetID':aid,'SourceFile':'Art/City/63rd_Street_Batch/Blender/BHC_63rd_Street_Batch_Master.blend','ExportGLB':'Art/City/63rd_Street_Batch/Exports/'+aid+'.glb','ExportFBX':'Art/City/63rd_Street_Batch/Exports/'+aid+'.fbx','AssetType':typ,'TriangleCountLOD0':tris,'Units':'meters','Collision':'COL_BHC_63rd_RoadSurface or shared house/restaurant proxies','Materials':'Procedural PBR source materials in .blend; no external paths','Verification':'Generated by Blender, reopened and render-checked'})
    city={'Project':'BIG HEAD CASINO GAMES','MandatoryInstruction':'create it fully 3D and very high end no BS.','WorldAssumption':'20,000m x 20,000m = 400 km²; 20x20 authoring tiles at 1km','CoordinateSystem':'World X east-west, Y north-south, Z up, meters, Unreal import scale 1.0','Districts':{'Central Casino District':'anchor (-250,0)','63rd Street District':'anchor (0,0)','North Suburbs':'anchor (0,5200)','East Residential':'anchor (5200,0)','West Hills Suburbs':'anchor (-5200,1200)','Harbor Dining District':'anchor (0,-5200)','Commercial and Service District':'anchor (5200,-3200)'},'DevelopedCoverage':'Tile 10/10: 63rd Street connected slice; 2 finished houses; 1 finished restaurant; food/staff assets. Remaining tiles are planned and explicitly unfinished.','Roads':'63rd Street east-west 120m, connected crossroad, parking, sidewalks, crosswalks, drains, lighting, signs, bus stop','Assets':rows,'RestaurantMenus':{'BHC_REST_63RD_CHOPHOUSE':[{'Name':n,'PriceCredits':p,'Category':k} for n,p,k in MENU]},'RestaurantWorkflow':'Arrival -> host -> reserved table -> server order -> kitchen ticket -> prep/cook/plating -> pass -> delivery -> eat/drink -> clear','UnrealIntegrationStatus':'Art assets ready for Sol; restaurant transactions, navigation, replication and acceptance tests not claimed complete'}
    with open(os.path.join(MANIFEST_DIR,'BHC_City_MasterPlan.json'),'w',encoding='utf8') as f: json.dump(city,f,indent=2)
    with open(os.path.join(MANIFEST_DIR,'BHC_63rd_Street_Batch_manifest.json'),'w',encoding='utf8') as f: json.dump({'Project':'BIG HEAD CASINO GAMES','Batch':'Verified Production Batch 2','WorldTile':'10,10 (63rd Street authoring slice)','Buildings':[{'BuildingID':'BHC_BLD_63RD_HOUSE_010','Address':'101 63rd Street','District':'63rd Street District','Rooms':'Living,Kitchen,Dining,BedroomA,BedroomB,Bath,Utility','Status':'Complete geometry and interior source'},{'BuildingID':'BHC_BLD_63RD_SUBURBAN_011','Address':'103 63rd Street','District':'63rd Street District','Rooms':'Ground and upper floor plan with garage','Status':'Complete geometry and interior source'}],'Restaurants':[{'RestaurantID':'BHC_REST_63RD_CHOPHOUSE','Address':'15 63rd Street','Tables':['Table_01','Table_02','Table_03','Table_04'],'Stations':['ColdStorage','DryStorage','PrepCounter','Oven','PanStation','Plating','ServicePass','Dishwash'],'MenuVersion':'63RD_CHOPHOUSE_v1','MenuItems':[{'Name':n,'PriceCredits':p,'Category':k,'FoodAsset':'BHC_FOOD_63RD_'+n.replace(' ','_')} for n,p,k in MENU],'Status':'Complete geometry and food/staff source; gameplay integration pending'}],'Assets':rows},f,indent=2)
    with open(os.path.join(MANIFEST_DIR,'BHC_63rd_Street_Batch_Handoff.md'),'w',encoding='utf8') as f: f.write('''# 63rd Street verified art batch\n\nMandatory art direction: **"create it fully 3D and very high end no BS."**\n\nThis batch contains a connected 120m 63rd Street segment, a cross intersection, sidewalks, parking sized for the BHC_VEH_328_NEON_DIESEL (5.05m x 2.06m), two furnished enterable houses, the complete 63RD STREET CHOPHOUSE with dining, restrooms, kitchen, storage, service pass and rear delivery route, the full 12-item initial menu as identifiable food assets, and host/server/chef staff source assets with named action inventory.\n\nThe 400 km² city is recorded as a 20x20 authoring grid of 1km tiles. Only the 63rd Street batch is marked developed; the master plan records all districts and the remaining scope as unfinished. Sol still owns Unreal navigation, restaurant state, order authority, credit settlement, NPC pathing, replication, persistence, streaming, and acceptance testing.\n''')

clear(); city_overview(); build_roads(); build_houses(); build_restaurant(); build_food(); build_staff(); setup_render()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BLEND_DIR,'BHC_63rd_Street_Batch_Master.blend'))
allcols=[CITY,ROADS,HOUSE,SUB,REST,FOODCOL,STAFF,COLL]
for aid,cc,typ in [('BHC_63RD_STREET_SLICE',[ROADS],'Street'),('BHC_BLD_63RD_HOUSE_010',[HOUSE],'House'),('BHC_BLD_63RD_SUBURBAN_011',[SUB],'Suburban'),('BHC_REST_63RD_CHOPHOUSE',[REST],'Restaurant'),('BHC_FOOD_63RD_CHOPHOUSE',[FOODCOL],'Food'),('BHC_NPC_RESTAURANT_STAFF',[STAFF],'Staff')]: export(cc,aid+'.glb','GLB'); export(cc,aid+'.fbx','FBX')
export([COLL],'COL_BHC_63RD_Slice.fbx','FBX')
visible=set(o.name for c in allcols for o in c.objects if o.type in {'MESH','FONT'}); interior_rest=set(o.name for o in REST.objects if all(k not in o.name for k in ['_Exterior','_Wall_','_Ceiling','Facade','Entrance'])); interior_house=set(o.name for o in HOUSE.objects if all(k not in o.name for k in ['_Exterior','_Wall_','_Ceiling','_Roof'])); render((25,-28,16),(15,-6,1.2),os.path.join(PREVIEW_DIR,'BHC_63rd_Overview.png'),44,visible); render((18,-15,2.2),(15,-18,1.6),os.path.join(PREVIEW_DIR,'BHC_63rd_Chophouse.png'),52,interior_rest); render((49,10,4.0),(46,17,1.2),os.path.join(PREVIEW_DIR,'BHC_63rd_House.png'),48,interior_house); render((16,-23,2.4),(15,-20.5,1.1),os.path.join(PREVIEW_DIR,'BHC_63rd_Kitchen.png'),42,interior_rest|set(o.name for o in FOODCOL.objects)); manifests(); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BLEND_DIR,'BHC_63rd_Street_Batch_Master.blend')); print('BHC_63RD_BATCH_COMPLETE')
