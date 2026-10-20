#!/usr/bin/env python3
"""Generate the Atlas profile dossier and its companion illustrations.

The artwork is a schematic feature study, not a screenshot, a canonical route,
or a geographic claim. All animated state is baked into self-contained SVGs.
Run directly, or via gen_profile_showcase.py. No dependencies or network calls.
"""
from html import escape
from math import sin, cos, pi, hypot
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'assets'
BG, INK, TEXT, MUTED = '#0C1216', '#152124', '#F0F0E3', '#B3BEB2'
SAGE, CORAL, LILAC = '#B8C991', '#FF987A', '#C2AAEB'
TIMES = '0;.125;.3125;.4375;.625;.75;.875;1'
CSS = '''text{font-family:Arial,Helvetica,sans-serif}.mono{font-family:'DejaVu Sans Mono',Consolas,monospace}
.still{display:none}@media(prefers-reduced-motion:reduce){.motion{display:none}.still{display:inline}}
'''


def text(x,y,value,size=18,color=TEXT,weight=400,attrs=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {attrs}>{escape(value)}</text>'


def path(points):
    return 'M'+'L'.join(f'{x:.1f},{y:.1f}' for x,y in points)


def anim(attribute,values,times=TIMES,duration=16):
    return f'<animate attributeName="{attribute}" values="{";".join(str(v) for v in values)}" keyTimes="{times}" dur="{duration}s" repeatCount="indefinite"/>'


def states(moving,still):
    return '<g class="motion">'+moving+'</g><g class="still">'+still+'</g>'


def write(name,w,h,title,body):
    (OUT/name).write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">Schematic feature illustration for The Walking Dead Universe Atlas. Not a screenshot or canonical geography. Reduced motion shows a static composition.</desc>
<style>{CSS}</style><defs>
<clipPath id="outer"><rect width="{w}" height="{h}" rx="20"/></clipPath>
<clipPath id="map"><rect width="520" height="350" rx="10"/></clipPath>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#8FA78E" stroke-opacity=".1"/></pattern>
<pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0 0V9" stroke="#B3BEB2" stroke-opacity=".12" stroke-width="2"/></pattern>
<radialGradient id="vignette"><stop stop-color="#20352E"/><stop offset="1" stop-color="#152124"/></radialGradient>
</defs><g clip-path="url(#outer)"><rect width="{w}" height="{h}" fill="{BG}"/>{body}</g>
<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="20" fill="none" stroke="#34423C" stroke-width="1.5"/>
</svg>\n''')


def progress(points):
    lengths=[hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(points,points[1:])]
    total=sum(lengths);s=0;result=[0]
    for length in lengths: s+=length;result.append(s/total)
    return result


ROUTE=[(65,270),(180,155),(310,225),(438,86)]
PROGRESS=progress(ROUTE)
KEYPOINTS=';'.join(f'{v:.6f}' for p in PROGRESS for v in [p,p])


def contour(cx,cy,rx,ry,seed):
    # Nested perturbed contours imply terrain without claiming any real location.
    lines=''
    for k in range(1,9):
        scale=.24+k*.13
        points=[]
        for i in range(121):
            a=i*2*pi/120
            warp=1+.12*sin(3*a+seed)+.09*cos(5*a-seed)+.04*sin(9*a)
            points.append((cx+rx*scale*warp*cos(a),cy+ry*scale*warp*sin(a)))
        lines+=f'<path d="{path(points)}Z" fill="none" stroke="#91A58A" stroke-opacity="{.09+k*.011:.3f}" stroke-width=".8"/>'
    return lines


def map_art():
    s='<g clip-path="url(#map)"><rect width="520" height="350" fill="url(#vignette)"/><rect width="520" height="350" fill="url(#grid)"/>'
    s+=contour(110,88,115,67,.7)+contour(391,284,147,106,2.1)+contour(453,47,66,110,4)
    s+='<path d="M272 -10C200 75 320 103 243 183S238 288 165 368" fill="none" stroke="#7CABA5" stroke-width="13" stroke-opacity=".07"/><path d="M272 -10C200 75 320 103 243 183S238 288 165 368" fill="none" stroke="#7CABA5" stroke-opacity=".3" stroke-width="1.5"/>'
    s+='<path d="M-10 209L139 232L285 103L530 165 M100 362L160 244L342 126L376 -12" fill="none" stroke="#CDD1B2" stroke-opacity=".17" stroke-width="1" stroke-dasharray="3 5"/>'
    d=path(ROUTE)
    distance=sum(hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(ROUTE,ROUTE[1:]))
    relative=path([(x-ROUTE[0][0],y-ROUTE[0][1]) for x,y in ROUTE])
    s+=f'<path d="{d}" fill="none" stroke="{CORAL}" stroke-opacity=".25" stroke-width="2.5"/>'
    trace=f'<path d="{d}" fill="none" stroke="{CORAL}" stroke-width="2.5" stroke-dasharray="{distance:.3f} {distance:.3f}" stroke-dashoffset="{distance:.3f}">'+anim('stroke-dashoffset',[round(distance*(1-v),4) for p in PROGRESS for v in [p,p]])+'</path>'
    traveler=f'<circle cx="{ROUTE[0][0]}" cy="{ROUTE[0][1]}" r="5" fill="{TEXT}" stroke="{CORAL}" stroke-width="2"><animateMotion path="{relative}" keyPoints="{KEYPOINTS}" keyTimes="{TIMES}" dur="16s" repeatCount="indefinite" calcMode="linear"/></circle>'
    s+=states(trace,f'<path d="{path(ROUTE[:3])}" fill="none" stroke="{CORAL}" stroke-width="2.5"/>')
    for i,(x,y) in enumerate(ROUTE):
        s+=f'<circle cx="{x}" cy="{y}" r="12" fill="{BG}" fill-opacity=".8" stroke="{CORAL}" stroke-opacity=".55"/>'
        s+=f'<circle cx="{x}" cy="{y}" r="3" fill="{CORAL}"/>'
        s+=text(x+17,y-13,f'0{i+1}',13,TEXT,700,'class="mono"')
    # The route marker sits above station rings, using the same timing as the rail.
    s+=states(traveler,f'<circle cx="310" cy="225" r="5" fill="{TEXT}" stroke="{CORAL}" stroke-width="2"/>')
    s+=text(18,28,'JOURNEY / ROUTE STUDY',12,SAGE,400,'class="mono" letter-spacing="1"')
    s+=text(18,330,'SCHEMATIC · NOT CANON GEOGRAPHY',10,MUTED,400,'class="mono" letter-spacing=".5"')
    s+='<path d="M484 44V23M478 29L484 23L490 29" stroke="#B8C991" fill="none" stroke-width="1.4"/>'
    s+='</g><rect x=".5" y=".5" width="519" height="349" rx="10" fill="none" stroke="#3D5145"/>'
    return s


def timeline(width):
    # Four station positions correspond to the four route stops; no invented episode labels.
    xs=[22+(width-44)*i/3 for i in range(4)]
    distance=xs[-1]-xs[0]
    s=text(0,0,'JOURNEY PLAYBACK',13,SAGE,700,'class="mono" letter-spacing="1.4"')
    s+=text(width,0,'EPISODE EVIDENCE → ROUTE',11,MUTED,400,'class="mono" text-anchor="end"')
    s+=f'<path d="M{xs[0]} 33H{xs[-1]}" stroke="#35473D" stroke-width="2"/>'
    moving=f'<path d="M{xs[0]} 33H{xs[-1]}" stroke="{CORAL}" stroke-width="2" stroke-dasharray="{distance:.3f} {distance:.3f}" stroke-dashoffset="{distance:.3f}">'+anim('stroke-dashoffset',[round(distance*(1-p/3),4) for p in range(4) for _ in range(2)])+'</path>'
    moving+=f'<circle cx="{xs[0]}" cy="33" r="5" fill="{TEXT}">'+anim('cx',[round(x,2) for x in xs for _ in range(2)])+'</circle>'
    still=f'<path d="M{xs[0]} 33H{xs[2]}" stroke="{CORAL}" stroke-width="2"/><circle cx="{xs[2]}" cy="33" r="5" fill="{TEXT}"/>'
    for i,x in enumerate(xs):
        s+=f'<circle cx="{x}" cy="33" r="3" fill="{SAGE}"/>'
        s+=text(x,60,f'0{i+1}',12,MUTED,400,'class="mono" text-anchor="middle"')
    return s+states(moving,still)


def hero(mobile=False):
    w,h=(600,850) if mobile else (1000,590)
    s=text(32,40,'PERSONAL BUILD / UNIVERSE EXPLORER',12,SAGE,700,'class="mono" letter-spacing="1.2"')
    s+='<path d="M32 57H'+str(w-32)+'" stroke="#34423C"/>'
    s+=text(28,111,'THE WALKING DEAD',34,TEXT,700,'letter-spacing="-.8"')
    s+=text(28,153,'UNIVERSE',34,TEXT,700,'letter-spacing="-.8"')
    s+=text(24,236,'ATLAS',86,SAGE,800,'letter-spacing="-4"')
    s+=text(32,280,'Every place. Every timeline.',24,MUTED)
    s+=text(32,311,'One connected story.',24,MUTED)
    if mobile:
        s+='<g transform="translate(40 345)">'+map_art()+'</g>'
        s+='<g transform="translate(40 746)">'+timeline(520)+'</g>'
    else:
        s+=text(32,365,'MAP · TIMELINE · PEOPLE · WATCH',12,SAGE,400,'class="mono" letter-spacing=".4"')
        s+=text(32,415,'Explore the universe',22,TEXT,700)
        s+='<path d="M269 408h27l-7-7 M296 408l-7 7" fill="none" stroke="#FF987A" stroke-width="2"/>'
        s+='<g transform="translate(448 83)">'+map_art()+'</g>'
        s+='<path d="M32 463H968" stroke="#34423C"/>'
        s+='<g transform="translate(40 498)">'+timeline(920)+'</g>'
    write('project-atlas-mobile.svg' if mobile else 'project-atlas-feature.svg',w,h,'The Walking Dead Universe Atlas. Every place. Every timeline. One connected story. Animated schematic journey with synchronized timeline.',s)


def companion(name,kicker,title,lines,art):
    s=text(28,37,kicker,13,SAGE,700,'class="mono" letter-spacing="1"')
    s+='<rect x="24" y="60" width="552" height="209" rx="9" fill="#152124"/>'+art
    s+='<path d="M28 291H572" stroke="#34423C"/>'+text(27,334,title,32,TEXT,700,'letter-spacing="-.8"')
    for i,line in enumerate(lines):s+=text(28,371+i*27,line,23,MUTED)
    write(name,600,425,title+' '+' '.join(lines),s)


def journeys():
    routes=[[(61,221),(169,174),(293,209),(418,112),(537,141)],[(61,151),(178,116),(290,161),(418,112),(537,141)],[(61,91),(178,116),(293,209),(419,230),(537,141)]]
    colors=[CORAL,SAGE,LILAC];s='';moving='';still=''
    s+='<g stroke="#B3BEB2" stroke-opacity=".08">'+''.join(f'<path d="M{x} 74V255"/>' for x in range(60,550,40))+''.join(f'<path d="M38 {y}H562"/>' for y in range(90,250,40))+'</g>'
    for i,(points,color) in enumerate(zip(routes,colors)):
        d=path(points)
        startx,starty=points[0]
        relative=path([(x-startx,y-starty) for x,y in points])
        s+=f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2" stroke-opacity=".6" stroke-linejoin="round"/>'
        for x,y in points:s+=f'<circle cx="{x}" cy="{y}" r="3" fill="{BG}" stroke="{color}"/>'
        moving+=f'<circle cx="{startx}" cy="{starty}" r="5" fill="{color}" stroke="{BG}" stroke-width="2"><animateMotion path="{relative}" keyPoints="0;0;1;1" keyTimes="0;.1;.85;1" dur="{13+i}s" repeatCount="indefinite" calcMode="linear"/></circle>'
        x,y=points[2];still+=f'<circle cx="{x+i*4}" cy="{y+i*3}" r="5" fill="{color}" stroke="{BG}" stroke-width="2"/>'
        s+=text(70+i*161,255,f'JOURNEY {chr(65+i)}',10,color,700,'class="mono" letter-spacing=".5"')
    s+=states(moving,still)
    companion('project-atlas-journeys.svg','COMPARE / UP TO THREE JOURNEYS','Different paths. Shared world.',('Compare journeys side by side.', 'See where their stories intersect.'),s)


def spoilers():
    s=''
    # The visible window advances only through already-seen evidence. The future stays masked.
    for row in range(3):
        y=95+row*48
        s+=f'<path d="M58 {y+8}H543" stroke="#53624D" stroke-width="1"/>'
        for col in range(7):
            x=59+col*72
            s+=f'<rect x="{x}" y="{y}" width="48" height="16" rx="3" fill="{SAGE}" fill-opacity="{.25+(row+col)%3*.12}"/>'
    s+='<rect x="327" y="74" width="230" height="161" rx="6" fill="#111B20"/><rect x="327" y="74" width="230" height="161" rx="6" fill="url(#hatch)"/>'
    s+='<path d="M327 76V233" stroke="#FF987A" stroke-width="2"/>'
    s+=text(442,145,'STILL TO COME',13,MUTED,700,'class="mono" text-anchor="middle"')
    s+=text(442,170,'Kept out of view',15,MUTED,400,'text-anchor="middle"')
    moving='<g opacity=".8"><rect x="59" y="79" width="60" height="151" rx="5" fill="#B8C991" fill-opacity=".06" stroke="#B8C991" stroke-opacity=".6">'+anim('x',[59,59,131,131,203,203,257,257])+'</rect></g>'
    still='<rect x="203" y="79" width="60" height="151" rx="5" fill="#B8C991" fill-opacity=".06" stroke="#B8C991" stroke-opacity=".6"/>'
    s+=states(moving,still)
    s+=text(58,255,'YOUR PROGRESS',10,SAGE,700,'class="mono" letter-spacing=".5"')
    s+=text(542,255,'SPOILER BOUNDARY',10,CORAL,700,'class="mono" text-anchor="end" letter-spacing=".5"')
    companion('project-atlas-spoilers.svg','EXPLORE / SPOILER-AWARE JOURNEYS','Keep your place in the story.',('Follow the evidence step by step.', 'Explore without getting ahead.'),s)


def generate():
    hero();hero(mobile=True);journeys();spoilers()


if __name__=='__main__':
    generate()
    print('Generated four responsive Atlas showcase SVGs.')
