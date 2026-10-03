import bpy, os
from mathutils import Vector

BASE = os.path.dirname(__file__)
blend = os.path.join(BASE, "Blender", "BHC_City_Master_Night.blend")
bpy.ops.wm.open_mainfile(filepath=blend)
for o in bpy.data.objects:
    if o.type == 'LIGHT':
        o.data.energy *= 3.0
world = bpy.context.scene.world
if world and world.use_nodes:
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.55

def point_at(o, target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for name, loc, energy, color, size in [
    ('BHC_HeroWarm', (40,-110,140), 90000, (1.0,0.28,0.08), 90),
    ('BHC_HeroCool', (-120,40,120), 80000, (0.04,0.18,1.0), 80),
    ('BHC_HeroEdge', (140,100,110), 85000, (0.5,0.04,1.0), 70),
]:
    d=bpy.data.lights.new(name,'AREA'); d.energy=energy; d.color=color; d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); bpy.context.collection.objects.link(o); o.location=loc; point_at(o,(0,30,20))

s=bpy.context.scene; s.render.filepath=os.path.join(BASE,'Previews','BHC_City_Master_Hero.png'); bpy.ops.wm.save_as_mainfile(filepath=blend); bpy.ops.render.render(write_still=True)
print('BHC_CITY_RENDER_UPGRADED')
