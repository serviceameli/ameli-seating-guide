import sys,math,json,itertools
from pathlib import Path
sys.path.insert(0,"/Users/ameli/CLAUDE/Служебные файлы Codex/tmp/seating-python-libs")
from shapely.geometry import Point,Polygon
ROOT=Path(__file__).resolve().parents[1]
def chain(angles):
    out=[(0.,0.)]
    for deg in angles:
        a=math.radians(deg);x,y=out[-1];out.append((x+180*math.cos(a),y+180*math.sin(a)))
    return out
def s_curve():
    step=math.pi/5;r=180/(2*math.sin(step/2))
    a=[(r*math.cos(math.pi-i*step),r*math.sin(math.pi-i*step))for i in range(6)]
    b=[(2*r+r*math.cos(math.pi+i*step),r*math.sin(math.pi+i*step))for i in range(1,6)]
    return a+b
layouts=[
 dict(id="round-chain-4",number="02",title="Цепочка из четырёх столов",subtitle="Прямая композиция из круглых «Вольф» Ø180",centers=chain([0,0,0]),source="Принцип соединения круглых столов, слайд 7; прямая адаптация",note=["Подходит для вытянутого пространства.","На каждом столе отдельная скатерть.","Места у соединений исключены."]),
 dict(id="round-wave-6",number="03",title="Волна из шести столов",subtitle="Извилистая цепочка по примерам со слайда 7",centers=chain([30,-30,30,-30,30]),source="Слайд 7, оба фотопримера",note=["Круги образуют мягкую извилистую линию.","Стулья стоят по доступным дугам.","В стыках посадки нет."]),
 dict(id="round-s-11",number="04",title="S-композиция из 11 столов",subtitle="Два изгиба из круглых «Вольф» Ø180",centers=s_curve(),source="S-образная композиция, слайд 8; масштабированная адаптация",note=["По мотивам S-композиции из презентации.","Посадка с внешней и внутренней сторон.","Форма адаптирована под 11 наших столов."])
]
def chair_poly(x,y,t,width=43,depth=47):
    # radial outward direction (cos t,sin t); cross direction perpendicular.
    u=(math.cos(t),math.sin(t));v=(-u[1],u[0])
    return Polygon([(x+a*v[0]+b*u[0],y+a*v[1]+b*u[1])for a,b in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]])
for layout in layouts:
    centers=layout["centers"];tables=[Point(x,y).buffer(90,quad_segs=96)for x,y in centers]
    # Preserve an eight-position angular rhythm, choose phase per table.
    # Width60 includes 17cm total side allowance beyond the actual43cm chair footprint.
    chosen=[];counts=[];candidates=[]
    for i,(cx,cy)in enumerate(centers):
        options=[]
        for phase in range(0,45,3):
            seats=[]
            for k in range(8):
                a=math.radians(k*45+phase);x=cx+123.5*math.cos(a);y=cy+123.5*math.sin(a)
                p=chair_poly(x,y,a);env=chair_poly(x,y,a,width=60)
                if any(p.distance(table)<9.9 for table in tables):continue
                if any(env.distance(c["envelope"])<2 for c in seats):continue
                seats.append(dict(table=i+1,x=x,y=y,angle=a,polygon=p,envelope=env))
            # Favour a balanced placement, then a phase near22.5deg.
            target=6 if i in [0,len(centers)-1] else 4
            for subset in itertools.combinations(seats,target):
                options.append((-abs(phase-22.5),list(subset)))
        candidates.append(sorted(options,key=lambda o:o[0],reverse=True))
    def assign(i,current):
        if i==len(centers):return current
        for score,seats in candidates[i]:
            if any(c['envelope'].distance(p['envelope'])<2 for c in seats for p in current):continue
            answer=assign(i+1,current+seats)
            if answer is not None:return answer
        return None
    chosen=assign(0,[])
    assert chosen is not None,('no valid balanced placement',layout['id'])
    counts=[sum(c['table']==i+1 for c in chosen)for i in range(len(centers))]
    # Verify physical table and chair footprints, not only candidate centres.
    for i,t in enumerate(tables):
        for j in range(i):
            assert t.intersection(tables[j]).area<.02,("table overlap",layout["id"],i,j)
    for i,c in enumerate(chosen):
        assert min(c["polygon"].distance(t)for t in tables)>=9.9
        for p in chosen[:i]:assert c["envelope"].distance(p["envelope"])>=2-1e-6
    all_shapes=tables+[s["polygon"]for s in chosen]
    bounds=[min(p.bounds[0]for p in all_shapes),min(p.bounds[1]for p in all_shapes),max(p.bounds[2]for p in all_shapes),max(p.bounds[3]for p in all_shapes)]
    tb=[min(x-90 for x,y in centers),min(y-90 for x,y in centers),max(x+90 for x,y in centers),max(y+90 for x,y in centers)]
    layout.update(chairs=[{k:v for k,v in c.items()if k not in ["polygon","envelope"]}for c in chosen],counts=counts,seats=len(chosen),bounds=bounds,tableBounds=tb)
    print(layout["id"],"tables",len(centers),"seats",len(chosen),"by table",counts,"furniture",round((bounds[2]-bounds[0])/100,2),round((bounds[3]-bounds[1])/100,2))
data={"units":"cm","table":{"model":"Вольф круглый белый180","diameter":180,"height":75,"url":"https://catalog.ameli-rental.ru/catalog/banketnye-stoly-vfa-zoq-mlk-swm/3071"},"chair":{"model":"Марсель золотой, кокосовый раф","width":43,"widthSource":"Ameli correction 2026-10-17","depth":47,"height":85,"url":"https://catalog.ameli-rental.ru/catalog/stulja-marsel-zaq/11162"},"cloth":{"model":"Альфа снежная круглая","diameter":330,"drop":75,"url":"https://catalog.ameli-rental.ru/catalog/kruglye-skaterti-azl-nmg-ear/6449"},"assumptions":{"tableCenterDistance":180,"chairFrontGap":10,"sideAllowanceTotal":17,"chairEnvelopeWidth":60,"minEnvelopeClearance":2,"aisles":"not included","capacity":"count of drawn places, not certified maximum; no people-body comfort validation","junctions":"round tables touch at one point, not a continuous flat edge; each has its own cloth"},"layouts":layouts}
(ROOT/"source/multi-round-layouts.json").write_text(json.dumps(data,ensure_ascii=False,indent=2))

