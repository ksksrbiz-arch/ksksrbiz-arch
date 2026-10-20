#!/usr/bin/env python3
"""Computational Field Notes: reproducible, self-contained SVG experiments.

Run: python3 tools/gen_research_lab.py
Check mathematical invariants without writing: python3 tools/gen_research_lab.py --check

Only Python's standard library is used. Computation happens here, never in a
visitor's browser. SVG SMIL replays the resulting samples. Each animation has
an independent static frame selected by prefers-reduced-motion.
"""
from collections import Counter
from html import escape
from math import sin, cos, pi, sqrt, floor, isfinite
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parents[1] / 'assets'
BG, PANEL, WHITE, MUTED = '#0B1017', '#101B23', '#EDF3EF', '#A7B6BA'
CYAN, LILAC, CORAL, GOLD = '#6CE5D1', '#C2AAEB', '#FF987A', '#E4BC78'
CSS = '''text{font-family:Arial,Helvetica,sans-serif}.mono{font-family:'DejaVu Sans Mono',Consolas,monospace}
.still{display:none}@media(prefers-reduced-motion:reduce){.motion{display:none}.still{display:inline}}
'''

def txt(x,y,s,size=18,color=WHITE,weight=400,attrs=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {attrs}>{escape(s)}</text>'

def path(points):
    return 'M'+'L'.join(f'{x:.1f},{y:.1f}' for x,y in points)

def animate(attr,values,dur,discrete=False):
    mode='discrete' if discrete else 'linear'
    return f'<animate attributeName="{attr}" values="{";".join(str(v) for v in values)}" dur="{dur}s" repeatCount="indefinite" calcMode="{mode}"/>'

def alternatives(motion,still):
    return '<g class="motion">'+motion+'</g><g class="still">'+still+'</g>'

def write(name,w,h,label,content,defs=''):
    (OUT/name).write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(label)}</title><desc id="desc">Computed in Python and replayed as SVG. Reduced motion displays a static study frame. Source: tools/gen_research_lab.py.</desc>
<style>{CSS}</style><defs><clipPath id="outer"><rect width="{w}" height="{h}" rx="20"/></clipPath><clipPath id="stage"><rect x="24" y="65" width="552" height="290" rx="8"/></clipPath>{defs}</defs>
<g clip-path="url(#outer)"><rect width="{w}" height="{h}" fill="{BG}"/>{content}</g>
<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="20" fill="none" stroke="#2B3B43" stroke-width="1.5"/>
</svg>\n''')

def card(name,n,field,title,lines,method,color,art):
    s=txt(28,35,f'FIELD NOTE / 0{n}',13,MUTED,400,'class="mono" letter-spacing="1"')
    s+=txt(572,35,field,13,color,700,'class="mono" text-anchor="end" letter-spacing="1.5"')
    s+='<rect x="24" y="65" width="552" height="290" rx="8" fill="#101B23"/>'
    s+='<g clip-path="url(#stage)">'+art+'</g>'
    s+='<path d="M28 381H572" stroke="#2B3B43"/>'
    s+=txt(27,428,title,37,WHITE,700,'letter-spacing="-1"')
    for i,line in enumerate(lines): s+=txt(28,465+i*28,line,24,MUTED)
    s+=txt(28,535,method,13,color,400,'class="mono" letter-spacing=".4"')
    s+=f'<path d="M545 530h25" stroke="{color}" stroke-width="2"/><circle cx="570" cy="530" r="3" fill="{color}"/>'
    write(name,600,560,f'{title}. {" ".join(lines)} {method}',s)


def lorenz_points(steps=7200,dt=.006):
    def f(p):
        x,y,z=p
        return (10*(y-x),x*(28-z)-y,x*y-(8/3)*z)
    def add(p,q,t): return tuple(a+t*b for a,b in zip(p,q))
    p=(.1,0,0); points=[]
    for i in range(steps):
        a=f(p);b=f(add(p,a,dt/2));c=f(add(p,b,dt/2));d=f(add(p,c,dt))
        p=tuple(v+dt*(aa+2*bb+2*cc+dd)/6 for v,aa,bb,cc,dd in zip(p,a,b,c,d))
        if i>=1200 and i%2==0: points.append(p)
    return points

def lorenz():
    pts=lorenz_points(); xmin=min(p[0] for p in pts);xmax=max(p[0] for p in pts)
    zmin=min(p[2] for p in pts);zmax=max(p[2] for p in pts)
    projected=[(64+(x-xmin)/(xmax-xmin)*472,333-(z-zmin)/(zmax-zmin)*246) for x,y,z in pts]
    d=path(projected)
    base=f'<path d="{d}" fill="none" stroke="{LILAC}" stroke-width=".8" stroke-opacity=".4"/>'
    tracer=f'<path d="{d}" fill="none" stroke="{CYAN}" stroke-width="1.6" pathLength="100" stroke-dasharray="9 91">'+animate('stroke-dashoffset',[0,-100],20)+'</path>'
    still=f'<path d="{path(projected[1100:1600])}" fill="none" stroke="{CYAN}" stroke-width="1.5"/>'
    grid='<g stroke="#C2AAEB" stroke-opacity=".06">'+''.join(f'<path d="M{x} 65V355"/>' for x in range(60,560,40))+''.join(f'<path d="M24 {y}H576"/>' for y in range(75,350,40))+'</g>'
    card('lab-study-chaos.svg',1,'DYNAMICS','Order inside chaos.',('One deterministic system.', 'A path that never quite repeats.'),'LORENZ / RK4 / σ 10 · ρ 28 · β 8/3',LILAC,grid+base+alternatives(tracer,still))


def life_step(cells,width=48,height=27):
    neighbors=Counter((x+dx,y+dy) for x,y in cells for dx in [-1,0,1] for dy in [-1,0,1] if dx or dy)
    return {p for p,n in neighbors.items() if (n==3 or (n==2 and p in cells)) and 0<=p[0]<width and 0<=p[1]<height}

def life_frames():
    gun={(0,4),(0,5),(1,4),(1,5),(10,4),(10,5),(10,6),(11,3),(11,7),(12,2),(12,8),(13,2),(13,8),(14,5),(15,3),(15,7),(16,4),(16,5),(16,6),(17,5),(20,2),(20,3),(20,4),(21,2),(21,3),(21,4),(22,1),(22,5),(24,0),(24,1),(24,5),(24,6),(34,2),(34,3),(35,2),(35,3)}
    cells={(x+4,y+3) for x,y in gun};frames=[cells]
    for _ in range(120): frames.append(life_step(frames[-1]))
    return frames

def life():
    frames=life_frames(); touched=sorted(set.union(*frames))
    grid='<defs><pattern id="dots" x="60" y="76" width="10" height="10" patternUnits="userSpaceOnUse"><circle cx="5" cy="5" r=".7" fill="#34514E"/></pattern></defs><rect x="60" y="76" width="480" height="270" fill="url(#dots)"/>'
    moving='';still=''
    for x,y in touched:
        shape=f'<rect x="{61+x*10}" y="{77+y*10}" width="8" height="8" rx="1.5" fill="{CYAN}"'
        vals=[int((x,y) in frame) for frame in frames]
        changes=[0]+[i for i in range(1,len(vals)) if vals[i]!=vals[i-1]]
        if changes[-1]!=120: changes.append(120)
        times=';'.join(f'{i/120:.6f}' for i in changes)
        states=';'.join(str(vals[i]) for i in changes)
        moving+=shape+f' opacity="{vals[0]}"><animate attributeName="opacity" values="{states}" keyTimes="{times}" dur="18s" calcMode="discrete" repeatCount="indefinite"/></rect>'
        if (x,y) in frames[60]: still+=shape+'/>'
    card('lab-study-life.svg',2,'EMERGENCE','Small rules. New worlds.',('A glider gun wakes the grid.', 'Every cell follows the same rules.'),'CONWAY / B3/S23 / 120 GENERATIONS',CYAN,grid+alternatives(moving,still))


def sphere(lon,lat,phase=0):
    x=cos(lat)*sin(lon+phase); y=sin(lat);z=cos(lat)*cos(lon+phase)
    tilt=.29; yy=y*cos(tilt)-z*sin(tilt)
    roll=-.25
    return (300+124*(x*cos(roll)-yy*sin(roll)),210-124*(x*sin(roll)+yy*cos(roll)))

def globe():
    motion='';still=''
    for m in range(8):
        curves=[path([sphere(m*pi/4,-pi/2+i*pi/24,k*2*pi/32) for i in range(25)]) for k in range(33)]
        motion+=f'<path d="{curves[0]}" stroke="{LILAC}" stroke-width="1.1" fill="none" stroke-opacity=".65">'+animate('d',curves,24)+'</path>'
        still+=f'<path d="{curves[8]}" stroke="{LILAC}" stroke-width="1.1" fill="none" stroke-opacity=".65"/>'
    common='<circle cx="300" cy="210" r="124" fill="#C2AAEB" fill-opacity=".035" stroke="#C2AAEB" stroke-opacity=".3"/>'
    for lat in [-pi/3,-pi/6,0,pi/6,pi/3]:
        common+=f'<path d="{path([sphere(i*2*pi/64,lat) for i in range(65)])}" fill="none" stroke="{CYAN}" stroke-opacity=".5"/>'
    common+='<ellipse cx="300" cy="210" rx="195" ry="61" transform="rotate(-24 300 210)" fill="none" stroke="#6CE5D1" stroke-opacity=".25"/>'
    orbit=[(300+195*cos(a)*cos(-.42)-61*sin(a)*sin(-.42),210+195*cos(a)*sin(-.42)+61*sin(a)*cos(-.42)) for a in [k*2*pi/80 for k in range(81)]]
    motion+=f'<circle cx="{orbit[0][0]}" cy="{orbit[0][1]}" r="5" fill="{CORAL}">'+animate('cx',[f'{x:.2f}' for x,y in orbit],12)+animate('cy',[f'{y:.2f}' for x,y in orbit],12)+'</circle>'
    still+=f'<circle cx="{orbit[10][0]}" cy="{orbit[10][1]}" r="5" fill="{CORAL}"/>'
    card('lab-study-globe.svg',3,'GEOMETRY','A world in projection.',('A sphere becomes a flat image.', 'Meridians turn. Geometry holds.'),'ORTHOGRAPHIC / 3D → 2D',LILAC,common+alternatives(motion,still))


def breakout_frames(duration=42):
    # Fixed-step circle/AABB collisions. Paddle follows with bounded speed.
    dt=1/120;x,y=300.,292.;vx,vy=145.,-190.;paddle=300.;r=5
    bricks=[(61+c*60,89+row*22,54,15) for row in range(5) for c in range(8)]
    active=set(range(40));hits={};frames=[];bounces=0
    for step in range(int(duration/dt)+1):
        t=step*dt; paddle+=max(-360*dt,min(360*dt,x-paddle));paddle=max(99,min(501,paddle))
        ox,oy=x,y;x+=vx*dt;y+=vy*dt
        if x<55+r: x=55+r;vx=abs(vx)
        elif x>545-r: x=545-r;vx=-abs(vx)
        if y<76+r: y=76+r;vy=abs(vy)
        if vy>0 and oy+r<=330 and y+r>=330 and abs(x-paddle)<=45+r:
            y=330-r;bounces+=1;vx=150*sin(bounces*1.91)+35;vy=-sqrt(240**2-vx**2)
        for i in sorted(active):
            bx,by,bw,bh=bricks[i]
            # Closest-point collision rejects the false square-corner hits of a loose AABB test.
            qx=max(bx,min(bx+bw,x));qy=max(by,min(by+bh,y))
            if (x-qx)**2+(y-qy)**2<=r*r:
                if ox+r<=bx or ox-r>=bx+bw: vx=-vx;x=ox
                else: vy=-vy;y=oy
                active.remove(i);hits[i]=t;break
        assert 59.99<=x<=540.01 and 80.99<=y<=330, 'Ball escaped the simulated arena'
        if step%6==0: frames.append((t,x,y,paddle))
    return bricks,hits,frames

def breakout():
    bricks,hits,frames=breakout_frames();dur=42;motion='';still='';colors=[LILAC,LILAC,CYAN,CYAN,GOLD]
    for i,(x,y,w,h) in enumerate(bricks):
        rect=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{colors[i//8]}"'
        if i in hits:
            t=hits[i]/dur
            motion+=rect+'>'+f'<animate attributeName="opacity" values="1;0;0" keyTimes="0;{t:.6f};1" calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/></rect>'
        else: motion+=rect+'/>'
        if hits.get(i,dur)>dur/2: still+=rect+'/>'
    motion+=f'<circle cx="300" cy="292" r="5" fill="{WHITE}">'+animate('cx',[f'{f[1]:.2f}' for f in frames],dur)+animate('cy',[f'{f[2]:.2f}' for f in frames],dur)+'</circle>'
    motion+=f'<rect x="255" y="330" width="90" height="7" rx="3.5" fill="{CORAL}">'+animate('x',[f'{f[3]-45:.2f}' for f in frames],dur)+'</rect>'
    _,x,y,p=frames[len(frames)//2]
    still+=f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="{WHITE}"/><rect x="{p-45:.2f}" y="330" width="90" height="7" rx="3.5" fill="{CORAL}"/>'
    arena='<path d="M55 337V76H545V337" fill="none" stroke="#3C5059"/><path d="M55 257H545" stroke="#253941" stroke-dasharray="3 8"/>'
    card('lab-study-physics.svg',4,'PHYSICS','Play is a physics problem.',('Ball. Bricks. A tracking paddle.', 'Every collision is computed.'),'FIXED STEP / 120 HZ / 42-SECOND REPLAY',CORAL,arena+alternatives(motion,still))


def noise(x,z):
    # Periodic integer hash + cubic smoothstep interpolation, deterministic across runs.
    def value(a,b): return ((a*374761393+(b%4)*668265263+1274126177)^((a+31)*1274126177))%65536/65535
    ix,iz=floor(x),floor(z);u=x-ix;v=z-iz;u=u*u*(3-2*u);v=v*v*(3-2*v)
    return (1-v)*((1-u)*value(ix,iz)+u*value(ix+1,iz))+v*((1-u)*value(ix,iz+1)+u*value(ix+1,iz+1))

def terrain_point(col,row,phase):
    depth=1+row*.7
    return (300+(col-9)*117/depth,140+230/depth-(noise(col/2.25,row/2.4+phase)*70)/sqrt(depth))

def terrain():
    moving='';still=''
    lines=[[(c,r) for c in range(19)] for r in range(16)]+[[(c,r) for r in range(16)] for c in range(19)]
    for i,line in enumerate(lines):
        curves=[path([terrain_point(c,r,k*4/24) for c,r in line]) for k in range(25)]
        opacity=.55 if i<16 else .28
        moving+=f'<path d="{curves[0]}" fill="none" stroke="{CYAN}" stroke-width="1.1" stroke-opacity="{opacity}">'+animate('d',curves,12)+'</path>'
        still+=f'<path d="{curves[10]}" fill="none" stroke="{CYAN}" stroke-width="1.1" stroke-opacity="{opacity}"/>'
    sky=f'<circle cx="300" cy="120" r="31" fill="{CORAL}" fill-opacity=".8"/><path d="M24 157H576" stroke="#FF987A" stroke-opacity=".2"/>'
    card('lab-study-terrain.svg',5,'PROCEDURAL','Build a place from noise.',('Noise becomes a wireframe world.', 'Depth and elevation shape the horizon.'),'VALUE NOISE / PERSPECTIVE / PERIODIC FIELD',CYAN,sky+alternatives(moving,still))


def signals():
    layers=[[(75,116+j*61) for j in range(4)],[(220,89+j*49) for j in range(6)],[(370,89+j*49) for j in range(6)],[(520,211)]]
    lines='';moving=''
    for li in range(3):
        for ai,(x,y) in enumerate(layers[li]):
            for bi,(xx,yy) in enumerate(layers[li+1]):
                d=f'M{x} {y}L{xx} {yy}'
                lines+=f'<path d="{d}" stroke="{LILAC}" stroke-opacity=".13"/>'
                # A deliberately illustrated signal sweep, not learned weights or inference.
                delay=li*1.1+(ai+bi)*.025
                moving+=f'<circle r="2" fill="{CYAN}" opacity="0"><animateMotion path="{d}" dur="4.8s" keyPoints="0;0;1;1" keyTimes="0;{.1+delay/4.8:.4f};{.25+delay/4.8:.4f};1" calcMode="linear" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0;.85;0;0" keyTimes="0;{.1+delay/4.8:.4f};{.11+delay/4.8:.4f};{.25+delay/4.8:.4f};1" dur="4.8s" repeatCount="indefinite"/></circle>'
    nodes=''
    for li,layer in enumerate(layers):
        for x,y in layer: nodes+=f'<circle cx="{x}" cy="{y}" r="8" fill="{BG}" stroke="{CORAL if li==3 else LILAC}" stroke-width="1.8"/>'
    card('lab-study-signals.svg',6,'INFORMATION','Follow the signal.',('A visual model of connections.', 'Follow a pulse from input to output.'),'4 → 6 → 6 → 1 / SIGNAL-FLOW ILLUSTRATION',LILAC,lines+alternatives(moving,'')+nodes)


def masthead():
    s='<path d="M32 45H66" stroke="#6CE5D1" stroke-width="3"/>'+txt(80,50,'1COMMERCE / COMPUTATIONAL FIELD NOTES',14,CYAN,400,'class="mono" letter-spacing="1"')
    s+=txt(28,134,'research.lab',78,WHITE,700,'letter-spacing="-4"')
    s+=txt(32,182,'Rules. Motion. Emergence.',25,MUTED)
    s+=txt(32,222,'SIX STUDIES / MATH + CODE + CURIOSITY',13,LILAC,400,'class="mono" letter-spacing="1"')
    curves=[]
    for j in range(3):
        points=[(820+(107+j*9)*sin(3*t+.2*j),130+(78+j*8)*sin(2*t)) for t in [i*2*pi/260 for i in range(261)]]
        curves.append(f'<path d="{path(points)}" stroke="{[CYAN,LILAC,CORAL][j]}" stroke-width="1" stroke-opacity=".55" fill="none"/>')
    s+=''.join(curves)+'<circle cx="820" cy="130" r="3" fill="#EDF3EF"/>'
    write('lab-masthead.svg',1000,260,'Research lab — computational field notes. Six studies in rules, motion and emergence.',s)


def check():
    pts=lorenz_points()
    assert all(isfinite(v) and abs(v)<100 for p in pts for v in p)
    block={(5,5),(5,6),(6,5),(6,6)}
    assert life_step(block)==block
    blinker={(4,5),(5,5),(6,5)}
    assert life_step(life_step(blinker))==blinker
    assert life_step(blinker)=={(5,4),(5,5),(5,6)}
    assert len(life_frames()[0])==36 and len(life_frames())==121
    for lon in range(36):
        for lat in range(-9,10):
            x,y=sphere(lon*pi/18,lat*pi/18)
            assert (x-300)**2+(y-210)**2<=124**2+.001
    assert all(abs(noise(x/3,z/7)-noise(x/3,z/7+4))<1e-12 for x in range(10) for z in range(10))
    bricks,hits,frames=breakout_frames()
    assert len(bricks)==40 and len(hits)>10 and len(frames)==841
    assert all(0<=t<=42 for t in hits.values())
    print(f'PASS: bounded Lorenz, Life block/blinker/gun, sphere projection, periodic noise, breakout arena ({len(hits)} computed brick collisions).')

if __name__=='__main__':
    check()
    if '--check' not in sys.argv:
        masthead();lorenz();life();globe();breakout();terrain();signals()
        print('Generated the masthead and six research studies.')
