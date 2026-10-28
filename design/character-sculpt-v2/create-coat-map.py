"""Author a flat pigment map from measured regions, not a photo projection.
This bitmap contains only fur colors; no eyes, shadows, instrument or source pixels.
"""
from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import math,random
N=2048
im=Image.new('RGB',(N,N),(255,124,36));d=ImageDraw.Draw(im);arm=im.copy();ad=ImageDraw.Draw(arm)
def p(x,z):return ((x+2)/4.3*N,(3.6-z)/3.6*N)
def smooth(poly):
 out=[]
 for i in range(len(poly)):
  a,b,c,e=[poly[k%len(poly)] for k in [i-1,i,i+1,i+2]]
  for j in range(16):
   t=j/16;out.append(tuple(.5*(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-e[k])*t*t+(-a[k]+3*b[k]-3*c[k]+e[k])*t*t*t) for k in [0,1]))
 return out
def poly(pts,c):
 points=[p(x,z) for x,z in smooth(pts)];d.polygon(points,fill=c)
 if c==(215,73,10):ad.polygon(points,fill=c)
cream=(255,221,165);stripe=(215,73,10)
poly([(.04,2.54),(.36,2.50),(.70,2.24),(.91,1.83),(1.01,1.24),(.98,.79),(.72,.47),(.28,.35),(-.17,.39),(-.52,.60),(-.66,1.04),(-.61,1.61),(-.45,2.12),(-.22,2.43)],cream)
# Soft rectangular muzzle pigment follows the existing facial surface.
poly([(-.20,2.87),(.34,2.87),(.36,2.61),(.30,2.57),(-.19,2.57),(-.23,2.61)],cream)
def oval(x,z,rx,rz,angle=0):
 cs=math.cos(angle);sn=math.sin(angle);poly([(x+rx*math.cos(a)*cs-rz*math.sin(a)*sn,z+rx*math.cos(a)*sn+rz*math.sin(a)*cs) for a in [2*math.pi*i/20 for i in range(20)]],stripe)
for x,z,rx,rz,an in [(-.22,3.34,.040,.065,.2),(.24,3.34,.040,.065,-.1),(-.58,3.05,.17,.055,.15),(-.58,2.85,.17,.06,.1),(.61,3.04,.16,.055,-.15),(.62,2.83,.15,.05,-.12),(-1.2,2.02,.24,.065,.35),(-1.31,1.70,.23,.065,.36),(-1.36,1.29,.25,.075,.3),(-1.32,.92,.26,.07,.15),(1.14,2.07,.24,.065,-.4),(1.28,1.73,.27,.07,-.4),(1.34,1.28,.25,.08,-.28),(1.30,.88,.25,.075,-.22),(-.90,1.94,.08,.20,-.58),(-.70,1.70,.075,.18,-.55),(-1.59,.67,.055,.17,-.6),(-1.45,.57,.055,.18,-.4)]:oval(x,z,rx,rz,an)
poly([(-.10,3.39),(.13,3.39),(.085,3.23),(.04,3.19),(-.015,3.22)],stripe)
im=im.filter(ImageFilter.GaussianBlur(4.5));out=Path(__file__).with_name('coat-pigment.png');im.save(out);arm.filter(ImageFilter.GaussianBlur(4.5)).save(Path(__file__).with_name('coat-arm-pigment.png'));print(out)
