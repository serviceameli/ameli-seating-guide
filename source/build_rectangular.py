import ast, json, math, sys, html, shutil
from pathlib import Path
sys.path.insert(0,'/Users/ameli/CLAUDE/Служебные файлы Codex/tmp/seating-python-libs')
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import box
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets'; O=ROOT/'review/rectangular'; O.mkdir(exist_ok=True)
tables=[dict(x=x,y=y,w=100,d=240) for x in [-200,200] for y in [0,240,480]]+[dict(x=0,y=-340,w=240,d=100)]
chairs=[]
for t in tables[:6]:
    for sign in [-1,1]:
        for dy in [-90,-30,30,90]: chairs.append(dict(x=t['x']+sign*83.5,y=t['y']+dy,w=47,d=43,side=sign))
for x in [-90,-30,30,90]: chairs.append(dict(x=x,y=-423.5,w=43,d=47,side=0))
assert len(tables)==7 and len(chairs)==52
def bounds(item):return box(item['x']-item['w']/2,item['y']-item['d']/2,item['x']+item['w']/2,item['y']+item['d']/2)
tp=list(map(bounds,tables));cp=list(map(bounds,chairs))
assert all(a.intersection(b).area<1e-6 for a in cp for b in tp)
assert all(a.intersection(b).area<1e-6 for i,a in enumerate(cp) for b in cp[i+1:])
layout=dict(id='rect-parallel-7',title='Два ряда и отдельный президиум',tables=tables,chairs=chairs,seats=52,tableSizeCm=[240,100,75],tableMeters=[5,9.9],furnitureMeters=[6.2,10.5],centralClearanceMeters=1.86,headTableGapMeters=1.7,seatPitchCm=60,sourceSlide=10,notes=['6 гостевых столов, по 3 в каждом ряду. Один отдельный стол президиума.','48 гостевых мест вдоль длинных сторон + 4 места в президиуме.','Торцы гостевых рядов свободны. Проход между спинками центральных стульев 1,86 м.','Это адаптация принципа из презентации под реальные размеры Wolf 240, не точная копия фото.','Габарит мебели не включает внешние проходы и отодвигание стульев.'])
(ROOT/'source/rectangular-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2))
ink='#303330'; muted='#666862'
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-350 -500 700 1180" role="img" aria-label="7 прямоугольных столов, 52 места"><rect x="-350" y="-500" width="700" height="1180" fill="#f5f5f0"/>']
for c in chairs:
    svg.append(f'<rect x="{c["x"]-c["w"]/2}" y="{c["y"]-c["d"]/2}" width="{c["w"]}" height="{c["d"]}" rx="5" fill="#e7dfcf" stroke="#99896b"/>')
for i,t in enumerate(tables):
    svg.append(f'<rect x="{t["x"]-t["w"]/2}" y="{t["y"]-t["d"]/2}" width="{t["w"]}" height="{t["d"]}" fill="#fff" stroke="{ink}" stroke-width="1.5"/><text x="{t["x"]}" y="{t["y"]}" text-anchor="middle" font-family="Arial" font-size="19" fill="{ink}">Т{i+1}</text>')
svg.append('<g font-family="Arial" font-size="17" fill="#666862" text-anchor="middle"><text x="0" y="140">1,86 м</text><text x="0" y="168">между спинками</text><text x="0" y="650">≈ 6,2 × 10,5 м со стульями</text></g></svg>')
(O/'rect-parallel-7.svg').write_text(''.join(svg))
def ft(n,medium=False):return ImageFont.truetype(str(A/('Montserrat-Medium.ttf' if medium else 'Montserrat-Regular.ttf')),n)
im=Image.new('RGB',(2200,1800),'white');d=ImageDraw.Draw(im)
def tx(x,y,s,n=26,fill=ink,bold=False):d.text((x,y),s,font=ft(n,bold),fill=fill)
tx(76,52,'АМЕЛИ РЕНТАЛ  /  ГАЙД ПО РАССАДКЕ',22)
tx(76,105,'Два ряда и отдельный президиум',54,bold=True)
tx(76,188,'7 столов «Вольф» 240 × 100 × 75 см · 52 места по схеме',28,muted)
d.line((76,250,2124,250),fill='#c9cbc4',width=2)
s=1.12;ox=690;oy=850
def rect(item,fill,outline):
    x,y,w,h=item['x'],item['y'],item['w'],item['d']; bb=(ox+(x-w/2)*s,oy+(y-h/2)*s,ox+(x+w/2)*s,oy+(y+h/2)*s);d.rectangle(bb,fill=fill,outline=outline,width=2)
for c in chairs:rect(c,'#e7dfcf','#99896b')
for i,t in enumerate(tables):
    rect(t,'#f7f7f3',ink);tx(ox+t['x']*s-20,oy+t['y']*s-18,'Т'+str(i+1),23,bold=True)
tx(390,1575,'≈ 6,2 м со стульями',27);d.line((ox-307*s,1545,ox+307*s,1545),fill=ink,width=2)
tx(110,760,'≈ 10,5 м',26);tx(110,800,'со стульями',20,muted)
tx(ox-48,oy+130*s,'1,86 м',23);tx(ox-90,oy+165*s,'между спинками',18,muted)
for i,(k,v) in enumerate([('Места в гостевых рядах','48'),('Места в президиуме','4'),('Столы «Вольф» 240','7 шт.'),('Стулья «Марсель»','52 шт.'),('Только столы','5,0 × 9,9 м'),('Вся мебель','≈ 6,2 × 10,5 м'),('Шаг посадки','60 см')]):
    y=335+i*156;tx(1390,y,k,25,muted);tx(1390,y+45,v,44,bold=True);d.line((1390,y+120,2124,y+120),fill='#d8dad3',width=2)
tx(1390,1450,'На торцах рядов посадки нет.',23,muted);tx(1390,1490,'Внешние проходы добавляются',23,muted);tx(1390,1530,'по плану конкретной площадки.',23,muted)
d.line((76,1650,2124,1650),fill='#c9cbc4',width=2)
tx(76,1675,'52 показанных места, не максимальная вместимость. Каркасы и сервировку проверяют при комплектации.',22,muted)
tx(76,1720,'Столы и стулья по каталогу. Габариты округлены вверх до 10 см. Форма адаптирована со слайда 10.',22,muted)
im.save(O/'rect-parallel-7.png')
# Real-scale solid model, metres, Z up. Hidden support construction is approximate.
tree=ast.parse((ROOT/'source/build_pilot.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['rod','cylinder','export_gltf']]
materials={'table':[.93,.93,.91,1],'gold':[.65,.50,.24,1],'velvet':[.83,.78,.68,1],'cloth':[.99,.985,.97,1]}
exec(compile(ast.Module(body=defs,type_ignores=[]),'<primitives>','exec'))
def cube(x,y,z,w,dep,h,mat):
    return dict(v=[[x+a*w/2,y+b*dep/2,z+c*h/2]for c in [-1,1]for b in [-1,1]for a in [-1,1]],f=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]],m=mat)
bare=[];clothed=[]
for t in tables:
    x=t['x']/100;y=t['y']/100;w=t['w']/100;dep=t['d']/100
    bare.append(cube(x,y,.735,w,dep,.03,'table'))
    for a in [-1,1]:
        for b in [-1,1]:bare.append(rod([x+a*(w/2-.15),y+b*(dep/2-.25),.72],[x+a*(w/2-.12),y+b*(dep/2-.2),.02],.018,'table'))
    clothed.append(cube(x,y,.38,w+.02,dep+.02,.74,'cloth'))
objects=list(clothed)
for c in chairs:
    x=c['x']/100;y=c['y']/100;w=c['w']/100;dep=c['d']/100
    objects.append(cube(x,y,.46,w,dep,.07,'velvet'))
    if c['side']:objects.append(cube(x+c['side']*.20,y,.72,.05,.43,.26,'velvet'))
    else:objects.append(cube(x,y-.20,.72,.43,.05,.26,'velvet'))
    for a in [-1,1]:
        for b in [-1,1]:objects.append(rod([x+a*(w/2-.04),y+b*(dep/2-.04),0],[x+a*(w/2-.04),y+b*(dep/2-.04),.45],.012,'gold'))
import struct
export_gltf(objects)
(O/'wolf180-marseille8.glb').rename(O/'rect-parallel-7.glb')
p=O/'rect-parallel-7.glb';b=p.read_bytes();n=struct.unpack('<I',b[12:16])[0];doc=json.loads(b[20:20+n]);doc['extras']={'units':'metres','tables':7,'chairs':52,'tableDimensions':[2.4,1,.75],'status':'Approximate volume; supports simplified; cloth product unspecified'};j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4);tail=b[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(j)+len(tail))+struct.pack('<II',len(j),0x4e4f534a)+j+tail)
def volume(objs,path):
    W=H=1600;az=-.32;el=.85
    def cam(p):
        x,y,z=p;x1=x*math.cos(az)-y*math.sin(az);y1=x*math.sin(az)+y*math.cos(az);return x1,y1*math.sin(el)-z*math.cos(el),y1*math.cos(el)+z*math.sin(el)
    pts=[cam(p)for o in objs for p in o['v']];xs=[p[0]for p in pts];ys=[p[1]for p in pts];sc=min(1350/(max(xs)-min(xs)),1300/(max(ys)-min(ys)));cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
    polygons=[]
    for o in objs:
        for face in o['f']:
            q=[cam(o['v'][i])for i in face];light=.91 if len({round(o['v'][i][2],3)for i in face})==1 else .80
            color=tuple(int(v*255*light)for v in materials[o['m']][:3]);polygons.append((sum(p[2]for p in q)/len(q),[(800+(p[0]-cx)*sc,800+(p[1]-cy)*sc)for p in q],color))
    im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
    for _,p,c in sorted(polygons,key=lambda a:a[0]):d.polygon(p,fill=c)
    im.save(path)
volume(bare,O/'rect-parallel-7-blocking.png');volume(objects,O/'rect-parallel-7-model.png')
(A/'rect-scene-data.js').write_text('window.SCENE_DATA='+json.dumps(dict(objects=objects,materials=materials),separators=(',',':'))+';')
viewer=(ROOT/'viewer.js').read_text();viewer=viewer[viewer.index('const c=document.querySelector'):];viewer=viewer.rsplit('})();',1)[0];viewer=viewer.replace('1.7*asp','7.6*asp').replace('-yy/1.7','-yy/7.6').replace('-dep/6.0','-dep/25.0').replace('p.z-.35','p.z-.35').replace('let az=.5,el=.63','let active="model";let az=-.32,el=.85').replace('window.addEventListener("resize",resize);','window.addEventListener("resize",resize);new ResizeObserver(resize).observe(c);requestAnimationFrame(resize);')
viewer=viewer.replace('review/model-marseille-8.png','review/rectangular/rect-parallel-7-model.png')
viewer=viewer.replace('p.x*ca-p.y*sa','p.x*ca-(p.y-.75)*sa').replace('p.x*sa+p.y*ca','p.x*sa+(p.y-.75)*ca')
(ROOT/'rect-viewer.js').write_text('(()=>{'+viewer+'})();')
(ROOT/'rect-viewer.html').write_text('<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Объёмная схема из 7 столов</title><style>html,body{margin:0;height:100%;background:#f5f5f0}canvas{width:100%;height:88%;display:block;touch-action:none}nav{display:flex;justify-content:center;gap:12px}button{padding:10px 16px;border:1px solid #ccc;background:white;cursor:pointer}</style><canvas id="model" aria-label="Вращаемая схема прямоугольных столов"></canvas><nav><button id="rotate-left" aria-label="Повернуть влево">↶</button><button id="reset">Сбросить вид</button><button id="rotate-right" aria-label="Повернуть вправо">↷</button></nav><script src="assets/rect-scene-data.js"></script><script src="rect-viewer.js"></script></html>')
print(json.dumps(dict(tables=len(tables),chairs=len(chairs),chairCollisions=0,outputs=[str(x)for x in O.iterdir()]),ensure_ascii=False))
