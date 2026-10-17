import sys,math,json,struct,base64
from pathlib import Path
sys.path.insert(0,"/Users/ameli/CLAUDE/Служебные файлы Codex/tmp/seating-python-libs")
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/"assets";O=ROOT/"review";O.mkdir(exist_ok=True)
FONT=A/"Montserrat-Regular.ttf";MED=A/"Montserrat-Medium.ttf"
def font(n,medium=False):return ImageFont.truetype(str(MED if medium else FONT),n)
ink="#303330";muted="#666862";line="#c9cbc4";paper="#f5f5f0";yellow="#fed330"
def text(d,xy,t,size=26,fill=ink,medium=False):d.text(xy,t,font=font(size,medium),fill=fill)
def dash(d,a,b,fill=line,width=2,step=16):
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    for t in range(0,int(length),step):d.line((a[0]+dx*t/length,a[1]+dy*t/length,a[0]+dx*min(t+step*.5,length)/length,a[1]+dy*min(t+step*.5,length)/length),fill=fill,width=width)
def chair2d(d,cx,cy,a,w=43,dep=47,scale=3.3):
    ca,sa=math.cos(a),math.sin(a)
    def p(x,y):return (cx+scale*(x*ca-y*sa),cy+scale*(x*sa+y*ca))
    pts=[p(-w/2,-dep/2),p(w/2,-dep/2),p(w/2,dep/2),p(-w/2,dep/2)]
    d.polygon(pts,fill="#e7dfcf",outline="#95846a",width=2)
    d.line([p(-w*.43,dep*.38),p(w*.43,dep*.38)],fill="#a69269",width=9)
def plan(n=8):
    im=Image.new("RGB",(1800,1500),"white");d=ImageDraw.Draw(im)
    text(d,(72,55),"АМЕЛИ РЕНТАЛ  /  ГАЙД ПО РАССАДКЕ",21)
    text(d,(72,106),"Круглый «Вольф» · Ø180 см",53,medium=True)
    text(d,(72,184),f"{n} гостей · стулья «Марсель» · вид сверху",28,muted)
    d.line((72,250,1728,250),fill=line,width=2)
    cx,cy=670,800;s=3.3;r=90*s
    for k in range(180):
        a=k*2*math.pi/180;b=a+.018
        if k%2==0:d.arc((cx-150*s,cy-150*s,cx+150*s,cy+150*s),math.degrees(a),math.degrees(b),fill=line,width=2)
    for i in range(n):
        a=2*math.pi*i/n+math.pi/8
        px=cx-123.5*s*math.sin(a);py=cy+123.5*s*math.cos(a)
        chair2d(d,px,py,a)
        nx=cx-163*s*math.sin(a);ny=cy+163*s*math.cos(a)
        label=str(i+1); box=d.textbbox((0,0),label,font=font(22));text(d,(nx-(box[2]-box[0])/2,ny-14),label,22,muted)
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill="#f7f7f3",outline=ink,width=3)
    for i in range(n):
        a=2*math.pi*i/n+math.pi/8
        px=cx-67*s*math.sin(a);py=cy+67*s*math.cos(a)
        rr=13*s;d.ellipse((px-rr,py-rr,px+rr,py+rr),outline="#b7b7af",width=2)
    d.rounded_rectangle((cx-138,cy-62,cx+138,cy+62),radius=16,fill="#f7f7f3")
    d.line((cx-r+15,cy,cx-145,cy),fill=ink,width=2);d.line((cx+145,cy,cx+r-15,cy),fill=ink,width=2)
    for x,sign in [(cx-r+15,1),(cx+r-15,-1)]:d.polygon([(x,cy),(x+sign*15,cy-6),(x+sign*15,cy+6)],fill=ink)
    text(d,(cx-110,cy-48),"Ø180 см",38,medium=True);text(d,(cx-94,cy+8),"высота 75 см",22,muted)
    lx=1240
    text(d,(lx,368),f"{n:02d}",116,medium=True);text(d,(lx,505),"мест в этой схеме",25,muted)
    for y,title,value in [(606,"Дуга столешницы на гостя",f"{180*math.pi/n:.1f}".replace(".",",")+" см"),(754,"Стул «Марсель»","43 × 47 см"),(902,"Габарит мебели","около 3 × 3 м")]:
        d.line((lx,y-22,1728,y-22),fill=line,width=2);text(d,(lx,y),title,23,muted);text(d,(lx,y+45),value,36,medium=True)
    text(d,(lx,1055),"Скатерть «Альфа»",23,muted)
    text(d,(lx,1098),"Ø330 см · свес 75 см",29,medium=True)
    text(d,(lx,1190),"Проходы считаются",23,muted);text(d,(lx,1228),"дополнительно.",23,muted)
    d.line((72,1370,1728,1370),fill=line,width=2)
    text(d,(72,1390),"Размер стола и стула взят из каталога. Положение стульев и сервировка условные.",21,muted)
    text(d,(72,1430),"Пробная схема для выбора подачи. Вместимость уточняется с учётом сервировки и площадки.",21,muted)
    im.save(O/f"plan-marseille-{n}.png")
    return im
# Mesh primitives use metres, Z up; actual overall dimensions, simplified internal construction.
materials={"table":[.91,.92,.89,1],"gold":[.65,.50,.24,1],"velvet":[.83,.78,.68,1],"feet":[.17,.18,.16,1],"cloth":[.985,.98,.96,1]}
def cylinder(rad,z0,z1,segments=32,xy=(0,0),mat="table"):
    v=[]
    for z in [z0,z1]:
        for i in range(segments):
            a=i*2*math.pi/segments;v.append([xy[0]+rad*math.cos(a),xy[1]+rad*math.sin(a),z])
    faces=[list(reversed(range(segments))),list(range(segments,2*segments))]
    faces += [[i,(i+1)%segments,(i+1)%segments+segments,i+segments]for i in range(segments)]
    return {"v":v,"f":faces,"m":mat}
def rod(a,b,rad=.012,mat="gold",segments=8):
    ax=[b[i]-a[i]for i in range(3)];length=math.sqrt(sum(t*t for t in ax));w=[t/length for t in ax]
    t=[0,0,1] if abs(w[2])<.9 else [1,0,0]
    u=[w[1]*t[2]-w[2]*t[1],w[2]*t[0]-w[0]*t[2],w[0]*t[1]-w[1]*t[0]];l=math.sqrt(sum(t*t for t in u));u=[t/l for t in u]
    v=[w[1]*u[2]-w[2]*u[1],w[2]*u[0]-w[0]*u[2],w[0]*u[1]-w[1]*u[0]]
    verts=[]
    for p in [a,b]:
        for i in range(segments):
            th=2*math.pi*i/segments;verts.append([p[j]+rad*(math.cos(th)*u[j]+math.sin(th)*v[j])for j in range(3)])
    faces=[[i,(i+1)%segments,(i+1)%segments+segments,i+segments]for i in range(segments)]
    faces.extend([list(reversed(range(segments))),list(range(segments,2*segments))])
    return {"v":verts,"f":faces,"m":mat}
def back(w,h,z,rounded=True):
    n=32;v=[]
    for y in [.185,.235]:
        for i in range(n):
            t=2*math.pi*i/n
            power=.6 if rounded else 1
            x=w/2*math.copysign(abs(math.cos(t))**power,math.cos(t))
            zz=z+h/2*math.copysign(abs(math.sin(t))**power,math.sin(t))
            v.append([x,y,zz])
    return {"v":v,"f":[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)],"m":"velvet"}
def scene(n=8,wash=False):
    objs=[cylinder(.9,.725,.75,64)]
    for x in [-.57,.57]:
        for y in [-.30,.30]:
            objs.append(rod([x,y,.725],[x,y,.18],.014,"table"))
            objs.append(rod([x,y,.18],[x,y*1.5,.02],.014,"table"))
        objs.append(rod([x,-.30,.38],[x,.30,.38],.012,"table"))
        objs.append(rod([x,-.30,.42],[x,.30,.69],.009,"table"))
    # White round 330cm cloth: theoretical 75cm drop on a 180cm table.
    # The folds are illustrative; overall cloth dimensions are catalogue based.
    objs.append(cylinder(.905,.751,.754,96,mat='cloth'))
    rings=[];segments=192
    for z,radius,amp in [(.752,.905,0),(.58,.92,.008),(.32,.925,.018),(.015,.93,.027)]:
        for k in range(segments):
            a=k*2*math.pi/segments;r=radius+amp*math.sin(24*a)
            rings.append([r*math.cos(a),r*math.sin(a),z])
    faces=[]
    for j in range(3):
        for k in range(segments):
            a=j*segments+k;b=j*segments+(k+1)%segments
            faces.append([a,b,b+segments,a+segments])
    objs.append({'v':rings,'f':faces,'m':'cloth'})
    for i in range(n):
        a=2*math.pi*i/n+math.pi/8;ca,sa=math.cos(a),math.sin(a);px=-1.235*sa;py=1.235*ca
        parts=[cylinder(.215,.43,.49,32,xy=(0,-.01),mat="velvet")]
        for xx in [-.18,.18]:
            for yy in [-.18,.18]:
                height=.69 if yy>0 else .455
                parts.append(rod([xx,yy,.012],[xx,yy,height],.012))
                parts.append(cylinder(.013,0,.018,8,xy=(xx,yy),mat="feet"))
            parts.append(rod([xx,-.18,.435],[xx,.18,.435],.01))
        parts.append(back(.36 if wash else .43,.45 if wash else .26,.695 if wash else .72,not wash))
        for part in parts:
            part["v"]=[[px+v[0]*ca-v[1]*sa,py+v[0]*sa+v[1]*ca,v[2]]for v in part["v"]];objs.append(part)
    return objs
def export_gltf(objs):
    chunks=[];views=[];access=[];meshes=[];nodes=[];off=0;matnames=list(materials)
    def buffer(values,fmt,component,count,typ,minmax=False):
        nonlocal off
        data=struct.pack("<"+fmt*len(values),*values);pad=(4-len(data)%4)%4
        views.append({"buffer":0,"byteOffset":off,"byteLength":len(data)})
        ac={"bufferView":len(views)-1,"componentType":component,"count":count,"type":typ}
        if minmax:ac.update(min=[min(values[k::3])for k in range(3)],max=[max(values[k::3])for k in range(3)])
        access.append(ac);chunks.append(data+b"\x00"*pad);off+=len(data)+pad;return len(access)-1
    for o in objs:
        # GLTF Y up, world Z becomes Y.
        pos=[v for p in o["v"]for v in [p[0],p[2],-p[1]]];ids=[]
        for f in o["f"]:
            for i in range(1,len(f)-1):ids.extend([f[0],f[i],f[i+1]])
        pa=buffer(pos,"f",5126,len(pos)//3,"VEC3",True);ia=buffer(ids,"I",5125,len(ids),"SCALAR")
        meshes.append({"primitives":[{"attributes":{"POSITION":pa},"indices":ia,"material":matnames.index(o["m"])}]});nodes.append({"mesh":len(meshes)-1})
    data=b"".join(chunks);doc={"asset":{"version":"2.0","generator":"Ameli Rental guide prototype"},"scene":0,"scenes":[{"nodes":list(range(len(nodes)))}],"nodes":nodes,"meshes":meshes,"accessors":access,"bufferViews":views,"buffers":[{"byteLength":len(data)}],"materials":[{"name":k,"doubleSided":True,"pbrMetallicRoughness":{"baseColorFactor":v,"metallicFactor":.55 if k=="gold" else 0,"roughnessFactor":.5 if k=="gold" else .85}}for k,v in materials.items()],"extras":{"units":"metres","status":"Approximate visual geometry, no hidden construction verified","tableDiameter":1.8,"tableHeight":.75,"chairOverallWidth":.43,"chairOverallDepth":.47,"chairOverallHeight":.85,"chairs":8}}
    js=json.dumps(doc,separators=(",",":")).encode();js+=b" "*((4-len(js)%4)%4)
    total=12+8+len(js)+8+len(data)
    (O/"wolf180-marseille8.glb").write_bytes(struct.pack("<III",0x46546C67,2,total)+struct.pack("<II",len(js),0x4E4F534A)+js+struct.pack("<II",len(data),0x004E4942)+data)
def render(objs):
    im=Image.new("RGB",(1800,1350),paper);d=ImageDraw.Draw(im)
    text(d,(72,55),"АМЕЛИ РЕНТАЛ  /  ГАЙД ПО РАССАДКЕ",21)
    text(d,(72,106),"Один стол. Восемь гостей.",51,medium=True)
    text(d,(72,182),"«Вольф» Ø180 + «Альфа» + 8 «Марселей» · объёмный вид",27,muted)
    az=.5;el=.63
    def transform(p):
        x=p[0]*math.cos(az)-p[1]*math.sin(az);y=p[0]*math.sin(az)+p[1]*math.cos(az)
        return (900+x*355,740+(y*math.sin(el)-(p[2]-.3)*math.cos(el))*355,y*math.cos(el)+p[2]*math.sin(el))
    polygons=[]
    for o in objs:
        for f in o["f"]:
            xyz=[o["v"][i]for i in f];q=[transform(p)for p in xyz]
            if len(xyz)<3:continue
            a=[xyz[1][i]-xyz[0][i]for i in range(3)];b=[xyz[2][i]-xyz[0][i]for i in range(3)]
            norm=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];ln=math.sqrt(sum(t*t for t in norm))or 1
            light=.64+.28*abs((norm[0]*-.4+norm[1]*-.5+norm[2]*.8)/ln)
            rgb=tuple(min(255,int(c*255*light))for c in materials[o["m"]][:3])
            polygons.append((sum(p[2]for p in q)/len(q),[(p[0],p[1])for p in q],rgb))
    import numpy as np
    pixels=np.array(im); depths=np.full((1350,1800),-np.inf)
    for o in objs:
        for f in o['f']:
            verts=[o['v'][i] for i in f]
            for k in range(1,len(verts)-1):
                tri=[verts[0],verts[k],verts[k+1]];q=[transform(p)for p in tri]
                aa=np.array(tri[1])-tri[0];bb=np.array(tri[2])-tri[0];normal=np.cross(aa,bb);ln=np.linalg.norm(normal)or 1
                light=.68+.32*abs(np.dot(normal,[-.4,-.5,.8])/ln)
                color=np.array([min(255,int(c*255*light))for c in materials[o['m']][:3]])
                x0=max(0,int(min(p[0]for p in q)));x1=min(1800,int(max(p[0]for p in q))+1)
                y0=max(0,int(min(p[1]for p in q)));y1=min(1350,int(max(p[1]for p in q))+1)
                if x1<=x0 or y1<=y0:continue
                xx,yy=np.meshgrid(np.arange(x0,x1)+.5,np.arange(y0,y1)+.5)
                a,b,c=q;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
                if abs(den)<1e-8:continue
                u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
                v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w=1-u-v
                zz=u*a[2]+v*b[2]+w*c[2];old=depths[y0:y1,x0:x1]
                mask=(u>=0)&(v>=0)&(w>=0)&(zz>old);old[mask]=zz[mask];pixels[y0:y1,x0:x1][mask]=color
    im=Image.fromarray(pixels);d=ImageDraw.Draw(im)
    d.line((72,1210,1728,1210),fill=line,width=2)
    text(d,(72,1240),"Габариты по каталогу. Детали каркасов и высота сидений восстановлены приблизительно.",22,muted)
    text(d,(72,1282),"Объёмный вид помогает оценить форму и расстановку; конструктивной моделью не является.",22,muted)
    im.save(O/"model-marseille-8.png")
plan()
objects=scene();render(objects);export_gltf(objects)
# JSON for the standalone interactive viewer.
(A/"scene-data.js").write_text("window.SCENE_DATA="+json.dumps({"objects":objects,"materials":materials},separators=(",",":"))+";")
print("Created plan, 3D view, GLB and browser mesh data.")

