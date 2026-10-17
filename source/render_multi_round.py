import sys,math,json,html
from pathlib import Path
sys.path.insert(0,"/Users/ameli/CLAUDE/Служебные файлы Codex/tmp/seating-python-libs")
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];DATA=json.loads((ROOT/"source/multi-round-layouts.json").read_text());OUT=ROOT/"review/multi-round";OUT.mkdir(exist_ok=True)
A=ROOT/"assets";INK="#303330";MUTED="#666862";LINE="#c9cbc4";BG="#f5f5f0"
def font(size,weight=400):return ImageFont.truetype(str(A/("Montserrat-Medium.ttf"if weight==500 else"Montserrat-Regular.ttf")),size)
def tx(d,x,y,s,size=25,weight=400,color=INK):d.text((x,y),s,font=font(size,weight),fill=color)
def pt(x,y,t,w=45,dep=47):
    u=(math.cos(t),math.sin(t));v=(-u[1],u[0])
    return [(x+a*v[0]+b*u[0],y+a*v[1]+b*u[1])for a,b in [(-w/2,-dep/2),(w/2,-dep/2),(w/2,dep/2),(-w/2,dep/2)]]
def ceil_m(n):return math.ceil(n/10-1e-7)/10
def mstr(n):return f"{n:.1f}".replace(".",",")
def arrow(d,x0,y0,x1,y1,width=2):
    d.line((x0,y0,x1,y1),fill=MUTED,width=width)
    angle=math.atan2(y1-y0,x1-x0)
    for x,y,a in [(x0,y0,angle),(x1,y1,angle+math.pi)]:
        points=[(x,y),(x+15*math.cos(a+.4),y+15*math.sin(a+.4)),(x+15*math.cos(a-.4),y+15*math.sin(a-.4))]
        d.polygon(points,fill=MUTED)
def render_one(layout):
    W,H=2200,1680;im=Image.new("RGB",(W,H),"white");d=ImageDraw.Draw(im)
    tx(d,76,52,"АМЕЛИ РЕНТАЛ  /  ГАЙД ПО РАССАДКЕ",22)
    tx(d,76,104,layout["title"],56,500)
    tx(d,76,184,layout["subtitle"],27,color=MUTED)
    tx(d,76,222,"Форма по референсам. Размеры пересчитаны под наши столы Ø180 см.",19,color=MUTED)
    d.line((76,250,W-76,250),fill=LINE,width=2)
    b=layout["bounds"];tb=layout["tableBounds"];layout["furnitureMeters"]=[ceil_m(b[2]-b[0]),ceil_m(b[3]-b[1])];layout["tableMeters"]=[ceil_m(tb[2]-tb[0]),ceil_m(tb[3]-tb[1])]
    # Exact furniture proportions are preserved. Horizontal and vertical scales are identical.
    box=(130,340,1510,1340);scale=min((box[2]-box[0])/(b[2]-b[0]),(box[3]-box[1])/(b[3]-b[1]))
    cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2;ox=(box[0]+box[2])/2;oy=(box[1]+box[3])/2
    def p(x,y):return (ox+(x-cx)*scale,oy+(y-cy)*scale)
    for c in layout["chairs"]:
        pts=[p(x,y)for x,y in pt(c["x"],c["y"],c["angle"])]
        d.polygon(pts,fill="#e7dfcf",outline="#99896b",width=2)
        u=(math.cos(c["angle"]),math.sin(c["angle"]));v=(-u[1],u[0])
        ends=[p(c["x"]+sgn*19*v[0]+18*u[0],c["y"]+sgn*19*v[1]+18*u[1])for sgn in [-1,1]]
        d.line(ends,fill="#a69269",width=max(3,round(scale*3)))
    for i,(x,y)in enumerate(layout["centers"]):
        a=p(x-90,y-90);z=p(x+90,y+90)
        d.ellipse((*a,*z),fill="#f7f7f3",outline=INK,width=2)
        xx,yy=p(x,y);label=f"Т{i+1}";fs=max(18,round(min(28,22*scale)))
        bb=d.textbbox((0,0),label,font=font(fs,500));tx(d,xx-(bb[2]-bb[0])/2,yy-fs*.9,label,fs,500)
        t="Ø180";fs2=max(15,round(min(23,17*scale)));bb=d.textbbox((0,0),t,font=font(fs2));tx(d,xx-(bb[2]-bb[0])/2,yy+fs*.4,t,fs2,color=MUTED)
    # Dimension refers to furniture, including the drawn chair positions.
    x0,y0=p(b[0],b[1]);x1,y1=p(b[2],b[3]);ay=min(1435,y1+60)
    d.line((x0,y1+10,x0,ay+12),fill=LINE,width=2);d.line((x1,y1+10,x1,ay+12),fill=LINE,width=2)
    arrow(d,x0,ay,x1,ay);label="≈ "+mstr(layout["furnitureMeters"][0])+" м со стульями"
    bb=d.textbbox((0,0),label,font=font(24));d.rectangle((ox-(bb[2]-bb[0])/2-15,ay-19,ox+(bb[2]-bb[0])/2+15,ay+20),fill="white");tx(d,ox-(bb[2]-bb[0])/2,ay-18,label,24)
    ax=x0-50
    d.line((ax-12,y0,x0-10,y0),fill=LINE,width=2);d.line((ax-12,y1,x0-10,y1),fill=LINE,width=2)
    arrow(d,ax,y0,ax,y1)
    height_label="≈ "+mstr(layout["furnitureMeters"][1])+" м со стульями"
    bb=d.textbbox((0,0),height_label,font=font(24));tile=Image.new("RGB",(bb[2]-bb[0]+30,48),"white")
    td=ImageDraw.Draw(tile);td.text((15,8),height_label,font=font(24),fill=MUTED);tile=tile.rotate(90,expand=True)
    im.paste(tile,(round(ax-tile.width/2),round((y0+y1)/2-tile.height/2)))
    sx=1645
    tx(d,sx,320,f'{layout["seats"]:02d}',116,500);tx(d,sx,458,"мест в этой схеме",25,color=MUTED)
    rows=[
     ("Столы «Вольф» Ø180",f'{len(layout["centers"])} шт.'),
     ("Скатерти «Альфа» Ø330",f'{len(layout["centers"])} шт.'),
     ("Стулья «Марсель»",f'{layout["seats"]} шт.'),
     ("Размер мебели со стульями",f'≈ {mstr(layout["furnitureMeters"][0])} × {mstr(layout["furnitureMeters"][1])} м'),
     ("Размер только столов",f'{mstr(layout["tableMeters"][0])} × {mstr(layout["tableMeters"][1])} м')]
    for k,(label,val)in enumerate(rows):
        yy=550+k*133;d.line((sx,yy-19,W-76,yy-19),fill=LINE,width=2);tx(d,sx,yy,label,23,color=MUTED);tx(d,sx,yy+43,val,34 if k<3 else 31,500)
    yy=1250
    tx(d,sx,yy,"Проходы добавляются",23,color=MUTED);tx(d,sx,yy+35,"по плану площадки.",23,color=MUTED)
    d.line((76,1515,W-76,1515),fill=LINE,width=2)
    tx(d,76,1540,"Столы соприкасаются краями. У стыков стульев нет. На каждом столе отдельная белая скатерть.",22,color=MUTED)
    tx(d,76,1580,"Количество мест относится к показанной схеме. Посадку и доступ гостей проверяют перед заказом.",22,color=MUTED)
    tx(d,76,1620,"Габариты округлены вверх до 10 см. Расстановка предварительная, без плана конкретной площадки.",20,color=MUTED)
    path=OUT/(layout["id"]+".png");im.save(path)
    # Compact vector for the website: diagram only; all text information stays readable in HTML.
    pad=45;vb=[b[0]-pad,b[1]-pad,b[2]-b[0]+2*pad,b[3]-b[1]+2*pad]
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(map(str,vb))}" role="img" aria-label="{html.escape(layout["title"])}: {len(layout["centers"])} столов, {layout["seats"]} мест">',f'<rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="{BG}"/>']
    for c in layout["chairs"]:
        coords=" ".join(f"{x:.3f},{y:.3f}"for x,y in pt(c["x"],c["y"],c["angle"]))
        svg.append(f'<polygon points="{coords}" fill="#e7dfcf" stroke="#99896b" stroke-width="1"/>')
        u=(math.cos(c["angle"]),math.sin(c["angle"]));v=(-u[1],u[0])
        ends=[(c["x"]+sgn*19*v[0]+18*u[0],c["y"]+sgn*19*v[1]+18*u[1])for sgn in [-1,1]]
        svg.append(f'<path d="M{ends[0][0]},{ends[0][1]}L{ends[1][0]},{ends[1][1]}" stroke="#a69269" stroke-width="3"/>')
    for i,(x,y)in enumerate(layout["centers"]):
        svg.append(f'<circle cx="{x}" cy="{y}" r="90" fill="#f7f7f3" stroke="{INK}" stroke-width="1.3"/><text x="{x}" y="{y+7}" text-anchor="middle" font-family="Arial,sans-serif" font-size="23" fill="{INK}">Т{i+1}</text>')
    svg.append("</svg>");(OUT/(layout["id"]+".svg")).write_text("".join(svg))
    print(path)
for layout in DATA["layouts"]:render_one(layout)
(ROOT/"source/multi-round-layouts.json").write_text(json.dumps(DATA,ensure_ascii=False,indent=2))

