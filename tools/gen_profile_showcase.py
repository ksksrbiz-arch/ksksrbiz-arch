#!/usr/bin/env python3
"""Build the profile's hand-drawn SVG showcase. No network or dependencies.

Run from any directory: python3 tools/gen_profile_showcase.py
Artwork is illustrative; these cards are not screenshots or live telemetry.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parents[1] / 'assets'
BG = '#0B1017'
FG = '#EDF3EF'
MUTED = '#A7B6BA'
CYAN = '#6CE5D1'
CORAL = '#FF987A'

STYLE = '''
text{font-family:Arial,Helvetica,sans-serif}
.mono{font-family:'DejaVu Sans Mono',Consolas,monospace}
.orbit{transform-origin:765px 272px;animation:orbit 42s linear infinite}
.float{animation:float 7s ease-in-out infinite}
.signal{stroke-dasharray:5 12;animation:signal 18s linear infinite}
.pulse{animation:pulse 4s ease-in-out infinite}
.book{animation:book 9s ease-in-out infinite}
.draw{stroke-dasharray:900;stroke-dashoffset:0;animation:draw 10s ease-in-out infinite}
.shine{animation:shine 8s ease-in-out infinite}
.bottle{animation:bottle 7s ease-in-out infinite}
@keyframes orbit{to{transform:rotate(360deg)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes signal{to{stroke-dashoffset:-170}}
@keyframes pulse{0%,100%{opacity:.45}50%{opacity:1}}
@keyframes book{0%,12%,100%{transform:translateY(0)}5%,9%{transform:translateY(-12px)}}
@keyframes draw{0%,100%{stroke-dashoffset:0}55%{stroke-dashoffset:0}75%{stroke-dashoffset:900}95%{stroke-dashoffset:0}}
@keyframes shine{0%,15%{transform:translateX(-180px);opacity:0}30%{opacity:.7}70%{transform:translateX(180px);opacity:0}100%{opacity:0}}
@keyframes bottle{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
'''

def text(x,y,value,size=16,fill=FG,weight=400,extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" {extra}>{escape(value)}</text>'

def svg(name,w,h,label,body,defs=''):
    (OUT / name).write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(label)}</title><desc id="desc">Handcrafted animated vector artwork. Motion is disabled when reduced motion is requested.</desc>
<style>{STYLE}</style><defs><clipPath id="frame"><rect width="{w}" height="{h}" rx="20"/></clipPath>{defs}</defs>
<g clip-path="url(#frame)"><rect width="{w}" height="{h}" fill="{BG}"/>{body}</g>
<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="20" fill="none" stroke="#2B3B43" stroke-width="1.5"/>
</svg>\n''')

def architecture():
    s = '<circle cx="765" cy="272" r="182" fill="url(#halo)"/><circle cx="765" cy="272" r="166" fill="none" stroke="#2C454C"/>'
    s += '<ellipse cx="765" cy="272" rx="198" ry="86" transform="rotate(-35 765 272)" fill="none" stroke="#526C6D" stroke-opacity=".6"/>'
    s += '<g class="orbit"><circle cx="765" cy="106" r="5" fill="#FF987A"/><circle cx="765" cy="438" r="4" fill="#6CE5D1"/></g>'
    # An exploded isometric computing stack. Shapes remain legible without animation.
    s += '<g class="float">'
    for y, color, opacity in [(344,'#6CE5D1','.25'),(292,'#6CE5D1','.5'),(240,'#FF987A','1')]:
        s += f'<path d="M625 {y} L765 {y-71} L905 {y} L765 {y+71}Z" fill="#14252C" stroke="{color}" stroke-opacity="{opacity}" stroke-width="1.5"/>'
        s += f'<path d="M625 {y} V{y+14} L765 {y+85} L905 {y+14} V{y} M765 {y+71} V{y+85}" fill="none" stroke="{color}" stroke-opacity="{opacity}"/>'
    s += '<path d="M698 239 L765 205 L832 239 L765 273Z" fill="#FF987A"/>'
    s += '<path d="M744 237 L764 226 V251 M751 257 L778 243" fill="none" stroke="#162128" stroke-width="6" stroke-linecap="square"/>'
    s += '<path class="signal" d="M625 240 V344 M765 311 V415 M905 240 V344" fill="none" stroke="#6CE5D1" stroke-width="2"/>'
    s += '</g>'
    for x,y in [(600,145),(927,355),(875,128),(646,418)]:
        s += f'<path d="M{x-4} {y}h8 M{x} {y-4}v8" stroke="#6B858C"/>'
    return s


def hero(mobile=False):
    w,h = (600,780) if mobile else (1000,550)
    grid = ''.join(f'<path d="M{x} 0 V{h}"/>' for x in range(0,w,40))
    grid += ''.join(f'<path d="M0 {y} H{w}"/>' for y in range(0,h,40))
    s = f'<g stroke="#A7B6BA" stroke-opacity=".035">{grid}</g>'
    s += '<path d="M30 31h20v20H30z" fill="#FF987A"/>' + text(37,46,'1',15,BG,800)
    s += text(63,48,'1COMMERCE',23,FG,700, 'letter-spacing="2"')
    s += text(w-30,46,'INDEPENDENT BUILDER',12,MUTED,400,'class="mono" text-anchor="end"')
    if mobile:
        s += '<g transform="translate(-366 282) scale(.86)">' + architecture() + '</g>'
        s += text(32,112,'KEITH J. SKAGGS',18,CYAN,700,'letter-spacing="3"')
        for y,line in [(179,'GOOD IDEAS.'),(243,'WORKING'),(307,'SOFTWARE.')]:
            s += text(28,y,line,62,FG,800,'letter-spacing="-2"')
        s += text(32,348,'Websites. Commerce. Connected systems.',22,MUTED)
        s += text(32,723,'FOUNDER, 1COMMERCE LLC',17,CYAN,700,'class="mono"')
        s += text(32,753,'PACIFIC NORTHWEST / WORKING EVERYWHERE',15,MUTED,400,'class="mono"')
    else:
        s += architecture()
        s += text(40,118,'KEITH J. SKAGGS',18,CYAN,700,'letter-spacing="3"')
        for y,line in [(194,'GOOD IDEAS.'),(262,'WORKING'),(330,'SOFTWARE.')]:
            s += text(35,y,line,64,FG,800,'letter-spacing="-2.5"')
        s += text(40,379,'Websites. Commerce. Connected systems.',23,MUTED)
        s += '<path d="M40 423H960" stroke="#2B3B43"/>'
        s += text(40,465,'FOUNDER, 1COMMERCE LLC',17,CYAN,700,'class="mono"')
        s += text(40,500,'PACIFIC NORTHWEST / WORKING EVERYWHERE',14,MUTED,400,'class="mono"')
        s += text(960,465,'DESIGN → BUILD → SHIP',17,FG,500,'class="mono" text-anchor="end"')
        s += text(960,500,'skdev@1commerce.online',17,MUTED,400,'class="mono" text-anchor="end"')
    svg('os-identity-mobile.svg' if mobile else 'os-identity.svg',w,h,'Keith J. Skaggs · 1COMMERCE — Good ideas. Working software. Websites, commerce and connected systems.',s,'<radialGradient id="halo"><stop stop-color="#244849" stop-opacity=".6"/><stop offset="1" stop-color="#0B1017" stop-opacity="0"/></radialGradient>')


def card(name,index,title,category,desc,domain,stack,color,art,defs=''):
    s = f'<rect width="480" height="246" fill="{color}" fill-opacity=".07"/>'
    s += text(26,32,f'0{index} / CLIENT WORK',12,MUTED,400,'class="mono" letter-spacing="1"')
    s += text(454,32,stack,12,color,700,'class="mono" text-anchor="end"')
    s += art
    s += '<path d="M26 246H454" stroke="#2B3B43"/>'
    s += text(26,278,category,11,color,700,'class="mono" letter-spacing="1.5"')
    s += text(24,315,title,30,FG,700,'letter-spacing="-.8"')
    s += text(26,345,desc,17,MUTED)
    s += text(26,388,domain,14,FG,400,'class="mono"')
    s += f'<circle cx="440" cy="381" r="17" fill="{color}"/><path d="M434 387L446 375 M436 375h10v10" fill="none" stroke="{BG}" stroke-width="1.7"/>'
    svg(name,480,416,f'{title} — {category}. {desc} Built with {stack}. {domain}',s+ '<path d="M26 409H454" stroke="#1C2D35"/>',defs)


def clients():
    # Book spines retain the original pulling-book choreography, now given room to breathe.
    a = '<circle cx="353" cy="137" r="77" fill="#F6AD55" fill-opacity=".07"/>'
    for i,(x,y,w,c) in enumerate([(72,94,30,'#B49CCA'),(107,112,24,'#6CE5D1'),(136,78,34,'#E4BC78'),(175,105,23,'#FF987A'),(204,91,30,'#87AD91'),(239,110,27,'#91B5CB'),(271,83,33,'#D8CD96'),(309,102,27,'#B49CCA')]):
        a += f'<g class="book" style="animation-delay:{i}s"><rect x="{x}" y="{y}" width="{w}" height="{201-y}" rx="3" fill="{c}"/><path d="M{x+5} {y+15}h{w-10} M{x+5} {y+20}h{w-10} M{x+5} 185h{w-10}" stroke="{BG}" stroke-opacity=".3"/></g>'
    a += '<path d="M55 204H382" stroke="#E4BC78" stroke-width="4"/><path d="M65 212H372" stroke="#E4BC78" stroke-opacity=".25"/>'
    a += '<path d="M354 90l19 111h26L379 86Z" fill="#6CE5D1" fill-opacity=".6"/>'
    card('client-tbr.svg',1,'To Be Read','BOOKSHOP / COMMUNITY','A digital home for a local book exchange.','tobereadshop.com','Next.js','#E4BC78',a)

    a = '<g stroke="#6CE5D1" stroke-opacity=".09">' + ''.join(f'<path d="M{x} 59V224"/>' for x in range(40,451,20)) + ''.join(f'<path d="M40 {y}H450"/>' for y in range(60,225,20)) + '</g>'
    house = 'M95 201V128L237 65L379 128V201Z M95 128H379 M143 201V145H197V201 M276 201V145H332V201 M237 65V111'
    a += f'<path d="{house}" fill="none" stroke="#6CE5D1" stroke-opacity=".2" stroke-width="2"/>'
    a += f'<path class="draw" d="{house}" fill="none" stroke="#6CE5D1" stroke-width="2" stroke-linejoin="round"/>'
    a += '<path d="M95 217H379 M95 212V222 M379 212V222 M237 58V45" stroke="#E4BC78"/>'
    a += text(237,238,'FROM BLUEPRINT TO BROWSER',10,'#E4BC78',400,'class="mono" text-anchor="middle" letter-spacing="1.5"')
    card('client-pcb.svg',2,'Precision Core Builders','CONSTRUCTION / LOCAL BUSINESS','Custom homes. A clear path to an estimate.','precisioncorebuilders.com','React',CYAN,a)

    a = '<circle cx="242" cy="139" r="84" fill="#B49CCA" fill-opacity=".09"/><path d="M42 218H438" stroke="#B49CCA" stroke-opacity=".4"/>'
    for i,(x,y,c) in enumerate([(110,100,'#E4BC78'),(222,72,'#B49CCA'),(334,100,'#87AD91')]):
        a += f'<g class="bottle" style="animation-delay:{i}s"><ellipse cx="{x+18}" cy="211" rx="43" ry="7" fill="#000" fill-opacity=".3"/><path d="M{x} {y}h36v24c19 7 25 24 25 42v32q0 9-9 9h-68q-9 0-9-9v-32c0-18 6-35 25-42Z" fill="{c}"/><rect x="{x+3}" y="{y-9}" width="30" height="12" rx="3" fill="#D5D6C4"/><rect x="{x-14}" y="{y+57}" width="64" height="31" rx="2" fill="{BG}" fill-opacity=".8"/>'
        a += text(x+18,y+77,'M / M',12,c,700,'class="mono" text-anchor="middle"')+'</g>'
    card('client-montucky.svg',3,'Montucky Moonshine','COMMERCE / CRAFT SPIRITS','Brand, product discovery and Shopify checkout.','montuckymoonshine.com','Shopify','#B49CCA',a)

    a = '<circle cx="247" cy="137" r="92" fill="#91C9DE" fill-opacity=".07"/><path d="M78 220V82L241 46L402 82V220" fill="none" stroke="#91C9DE" stroke-opacity=".16"/>'
    a += '<rect x="151" y="62" width="178" height="160" rx="3" fill="#162A35" stroke="#91C9DE" stroke-width="2"/>'
    a += '<g clip-path="url(#glassclip)"><rect x="161" y="72" width="158" height="140" fill="url(#glass)"/><path d="M161 164L198 126L233 151L272 108L319 154V212H161Z" fill="#427984"/><path d="M161 185L205 157L246 185L287 149L319 173V212H161Z" fill="#285663"/><path class="shine" d="M155 72h35l-35 140h-35Z" fill="#fff" fill-opacity=".4"/></g>'
    a += '<path d="M240 72V212 M161 142H319" stroke="#C5E2E7" stroke-width="7"/><path d="M135 225H345" stroke="#91C9DE" stroke-width="4"/>'
    card('client-clearview.svg',4,'ClearView Windows','HOME SERVICES / LEAD GENERATION','A brighter storefront for window installation.','windowsbyclearview.com','Astro','#91C9DE',a,'<linearGradient id="glass" x2="0" y2="1"><stop stop-color="#94C7D9"/><stop offset="1" stop-color="#D3E9DD"/></linearGradient><clipPath id="glassclip"><rect x="161" y="72" width="158" height="140"/></clipPath>')


def atlas():
    s = '<rect x="500" width="500" height="420" fill="#172322"/>'
    # Abstract geographic contours: illustrative, not a claimed exact map.
    for i in range(9):
        x=510+i*19
        s += f'<path d="M{x} -30C{x+115} 65 {x-75} 105 {x+80} 193S{x+12} 326 {x+170} 450" stroke="#91A58A" stroke-opacity=".15" fill="none"/>'
    s += '<path class="signal" d="M580 272L649 174L761 231L859 120L935 179" fill="none" stroke="#FF987A" stroke-width="2"/>'
    for i,(x,y) in enumerate([(580,272),(649,174),(761,231),(859,120),(935,179)]):
        s += f'<circle class="pulse" cx="{x}" cy="{y}" r="17" fill="#FF987A" fill-opacity=".1" stroke="#FF987A" stroke-opacity=".3" style="animation-delay:{i*.6}s"/><circle cx="{x}" cy="{y}" r="5" fill="#FF987A"/>'
    s += text(649,148,'ALEXANDRIA',12,'#C9D6CC',500,'class="mono" text-anchor="middle"')
    s += text(761,265,'THE KINGDOM',12,'#C9D6CC',500,'class="mono" text-anchor="middle"')
    s += text(859,93,'HILLTOP',12,'#C9D6CC',500,'class="mono" text-anchor="middle"')
    s += text(532,381,'MAP / TIMELINE / CHARACTERS',13,'#AFC0B0',400,'class="mono" letter-spacing="1"')
    s += text(32,45,'PERSONAL BUILD / FEATURED PROJECT',13,CORAL,700,'class="mono" letter-spacing="1"')
    s += text(28,119,'THE WALKING',48,FG,800,'letter-spacing="-1.5"')
    s += text(28,170,'DEAD UNIVERSE',48,FG,800,'letter-spacing="-1.5"')
    s += text(28,224,'ATLAS',56,CORAL,800,'letter-spacing="-1.5"')
    s += text(32,270,'A sprawling universe. One connected view.',19,MUTED)
    s += text(32,301,'Interactive maps, timelines and character data.',18,MUTED)
    s += text(32,344,'REACT + TYPESCRIPT',13,CYAN,700,'class="mono" letter-spacing="1"')
    s += text(32,384,'Explore the atlas',18,FG,700) + '<path d="M202 379h28l-7-7 M230 379l-7 7" stroke="#FF987A" fill="none" stroke-width="2"/>'
    svg('project-atlas-feature.svg',1000,420,'The Walking Dead Universe Atlas — a personal React and TypeScript project with interactive maps, timelines and character data.',s)

if __name__ == '__main__':
    hero()
    hero(mobile=True)
    clients()
    atlas()
    print('Generated 7 self-contained showcase SVGs.')
