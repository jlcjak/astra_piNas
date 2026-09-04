from pathlib import Path
import pcbnew as p,json,math,sys,uuid
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from sexpr import *
M=json.loads((ROOT/'sources/design_manifest.json').read_text());CAT=json.loads((ROOT/'sources/catalog.json').read_text());b=p.BOARD();b.SetCopperLayerCount(6)
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
N={};PADNET={}
netlist=loads((ROOT/'sources/astra_piNas.net').read_text())
for nn in children(child(netlist,'nets'),'net'):
 name=child(nn,'name')[1]
 z=p.NETINFO_ITEM(b,name);b.Add(z);N[name]=z
 for node in children(nn,'node'):PADNET[(child(node,'ref')[1],child(node,'pin')[1])]=name
F={};placed=set();boxes=[]
def box(fp,margin=.35):
 q=fp.GetBoundingBox(False,False);return [p.ToMM(q.GetX())-margin,p.ToMM(q.GetY())-margin,p.ToMM(q.GetRight())+margin,p.ToMM(q.GetBottom())+margin]
def place(r,x,y,a=0,back=False):
 f=F[r];f.SetPosition(V(x,y));f.SetOrientationDegrees(a)
 if back and f.GetLayer()!=p.B_Cu:f.Flip(f.GetPosition(),False)
 placed.add(r);boxes.append((r,back,box(f)))
 return f
for r,c in M.items():
 f=p.FootprintLoad(str(ROOT/'lib/astra_piNas.pretty'),c['part']['fp']);assert f,r
 f.SetReference(r);f.SetValue(c['value']);f.GetField(p.FIELD_T_DATASHEET).SetText(CAT[c['lcsc']]['url']);f.SetFPID(p.LIB_ID('astra_piNas',c['part']['fp']))
 f.SetPath(p.KIID_PATH('/'+str(uuid.uuid5(uuid.NAMESPACE_URL,'astra_piNas/root'))+'/'+str(uuid.uuid5(uuid.NAMESPACE_URL,'astra_piNas/sheet_'+c['sheet']))+'/'+c['uuid']))
 for k,v in [('MANUFACTURER PART NUMBER',CAT[c['lcsc']]['model']),('Manufacturer',CAT[c['lcsc']]['brand']),('LCSC Part Number',c['lcsc']),('LCSC Stock',str(CAT[c['lcsc']]['lcsc_stock']))]:
  field=p.PCB_FIELD(f,p.FIELD_T_USER,k);field.SetText(v);field.SetVisible(False);f.Add(field)
 for pad in f.Pads():
  n=PADNET.get((r,pad.GetNumber()))
  if n:pad.SetNet(N[n])
 f.Value().SetVisible(False);f.Reference().SetTextSize(V(.8,.8));f.Reference().SetTextThickness(p.FromMM(.12));b.Add(f);F[r]=f
for r,xy in {'J1':(4.5,73.5),'J2':(38.5,73.5),'U1':(55,67),'U2':(53,91),'U3':(81,49),'U4':(81,73),'U5':(81,95),'U6':(72,107),'U9':(90,105),'U10':(91,109),'U8':(19,101)}.items():place(r,*xy)
place('J3',20,35,0,True);place('J4',52,35,0,True)
# Flip about horizontal axis and rotate 180 keeps drive insertion direction toward +Y.
place('J5',89.4,38,180);place('J6',73,114.8);place('J7',90,114.8);place('J8',86,16,180);place('J9',7.4,108,270);place('U7',3,3)
for r,xy in {'H1':(20,113.75),'H2':(52,113.75),'H3':(5,47),'H4':(38,47),'H5':(5,95),'H6':(38,95)}.items():place(r,*xy,back=r in ['H1','H2'])
# Place the power-stage loops explicitly. Feedback/compensation stay on quiet side.
place('L1',57,91);place('C9',60.5,91,90);place('C10',49,91,90);place('R27',54,94);place('R28',54,96)
for j,(u,l,y) in enumerate([('U3','L2',49),('U4','L3',73),('U5','L4',95)]):
 place(l,88,y)
 cs=43+j*7;rs=29+j*3
 for r,x,yy,a in [(f'C{cs}',81,y-5,0),(f'C{cs+1}',76,y-2,90),(f'C{cs+2}',76,y+4,90),(f'C{cs+6}',81,y-8,0),(f'R{rs}',80,y+5,0),(f'R{rs+1}',80,y+7,0),(f'R{rs+2}',76,y+1,90)]:place(r,x,yy,a)
 for i in range(3):place(f'C{cs+3+i}',94,y-3.8+i*3.8,90)
place('D1',83,34,0,True)
place('D2',94,46,0,True)
place('F1',95,33,0)
# Input source and USB-PD controller cluster.
for r,x,y,a in [('D4',67,107,90),('D5',63,31,0),('C71',57,31,0),('Q1',69,112,90),('D3',65,112,90),('R40',72,103,0),('R41',75,103,0),('C64',69,103,90),('R42',65,116,0),('R43',65,119,0),('C65',77,111,90),('C66',67,99,90),('R38',72,47,90),('R39',72,51,90)]:place(r,x,y,a)
# Close local switch decoupling: target the corresponding package edge, allowing staggered rows.
def clear(bb,back,ignore=()):
 if bb[0]<1 or bb[1]<1 or bb[2]>99 or bb[3]>119:return False
 for r,side,q in boxes:
  if r in ignore:continue
  if side!=back:
   for pad in F[r].Pads():
    if pad.GetAttribute() not in [p.PAD_ATTRIB_PTH,p.PAD_ATTRIB_NPTH]:continue
    v=pad.GetBoundingBox();px1=p.ToMM(v.GetX())-.3;py1=p.ToMM(v.GetY())-.3;px2=p.ToMM(v.GetRight())+.3;py2=p.ToMM(v.GetBottom())+.3
    if bb[0]<px2 and bb[2]>px1 and bb[1]<py2 and bb[3]>py1:return False
   continue
  if bb[0]<q[2] and bb[2]>q[0] and bb[1]<q[3] and bb[3]>q[1]:return False
 return True
def auto(r,x,y,back=False,a=0,maxrad=22):
 f=F[r];f.SetOrientationDegrees(a)
 if back:f.Flip(f.GetPosition(),False)
 candidates=[]
 for dx in range(-int(maxrad*2),int(maxrad*2)+1):
  for dy in range(-int(maxrad*2),int(maxrad*2)+1):candidates.append((dx*dx+dy*dy,dx*.5,dy*.5))
 for _,dx,dy in sorted(candidates):
  f.SetPosition(V(x+dx,y+dy))
  if clear(box(f),back):
   placed.add(r);boxes.append((r,back,box(f)));return
 raise RuntimeError('No legal placement '+r)
for r,c in M.items():
 if r in placed or c.get('near')!='U1':continue
 pad=next(z for z in F['U1'].Pads() if z.GetNumber()==c['supply_pin']);pos=pad.GetPosition();px,py=p.ToMM(pos.x),p.ToMM(pos.y);dx=px-55;dy=py-67
 if abs(dx)>abs(dy):x=55+math.copysign(11.5,dx);y=py;a=0
 else:x=px;y=67+math.copysign(11.5,dy);a=90
 auto(r,x,y,a=a,maxrad=8)
# Coupling and clock parts remain by the switch; pair mates are placed together.
for i in range(8):auto('C'+str(i+1),43 if i<6 else 43,57+(i//2)*2.5,a=0,maxrad=12)
for r,c in M.items():
 if r in placed:continue
 sh=c['sheet'];back=False
 if sh=='02_pcie':
  x,y=(57,53) if int(r[1:]) in [2,3,4,5,6,7,8,21,22,23,24,25,26] else (60,82)
 elif sh=='03_aux_power':x,y=22,88
 elif sh=='04_nvme':
  j=1 if 'SSD1_3V3' in c['nets'].values() else 2;x,y=(20 if j==1 else 52),23;back=True
 elif sh=='06_inputs':x,y=64,103
 elif sh=='07_ethernet_poe':x,y=75,31
 elif sh=='08_sd_uart':
  if r.startswith('R') and 46<=int(r[1:])<=50:x,y=18,106
  elif r in ['C72','C73']:x,y=19,99
  else:x,y=85,107
 else:raise RuntimeError(r)
 auto(r,x,y,back=back)
# Check every manually placed passive against all other bodies and through-holes.
for r in list(F):
 if not r.startswith(('R','C','D','Q')):continue
 f=F[r];back=f.GetLayer()==p.B_Cu;x=p.ToMM(f.GetPosition().x);y=p.ToMM(f.GetPosition().y);a=f.GetOrientationDegrees()
 boxes[:]=[z for z in boxes if z[0]!=r]
 if clear(box(f),back):boxes.append((r,back,box(f)));continue
 if back:f.Flip(f.GetPosition(),False)
 auto(r,x,y,back=back,a=a,maxrad=14)
# Reposition reference text consistently, away from pads; values remain in fabrication properties.
for r,f in F.items():
 q=f.GetBoundingBox(False,False);f.Reference().SetPosition(V(p.ToMM(f.GetPosition().x),p.ToMM(q.GetY())-.7));f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));f.Reference().SetLayer(p.B_SilkS if f.GetLayer()==p.B_Cu else p.F_SilkS);f.Reference().SetMirrored(f.GetLayer()==p.B_Cu)
 # Hide references inside the CM5 module footprint except the connectors.
 if r not in ['J1','J2','H3','H4','H5','H6'] and 2<f.GetPosition().x/1000000<41 and 44<f.GetPosition().y/1000000<99:f.Reference().SetVisible(False)
# Fabrication layers carry dense component outlines and passive reference designators.
# Assembly/routing views include F.Fab and B.Fab; silkscreen stays legible.
for r,f in F.items():
 back=f.GetLayer()==p.B_Cu;fab=p.B_Fab if back else p.F_Fab
 if r.startswith(('R','C','D','Q','H')) or r in ['J5','J6','J7','U10']:f.Reference().SetLayer(fab);f.Reference().SetVisible(True)
def line(x1,y1,x2,y2,layer,width=.15):
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(V(x1,y1));s.SetEnd(V(x2,y2));s.SetLayer(layer);s.SetWidth(p.FromMM(width));b.Add(s)
def rect(x1,y1,x2,y2,layer):
 for a in [(x1,y1,x2,y1),(x2,y1,x2,y2),(x2,y2,x1,y2),(x1,y2,x1,y1)]:line(*a,layer)
def text(t,x,y,layer=p.F_SilkS,size=1):
 z=p.PCB_TEXT(b);z.SetText(t);z.SetPosition(V(x,y));z.SetLayer(layer);z.SetTextSize(V(size,size));z.SetTextThickness(p.FromMM(.15));b.Add(z)
rect(0,0,100,120,p.Edge_Cuts);rect(1.5,43.5,41.5,98.5,p.Dwgs_User)
text('CM5 / 4 mm standoffs',22,52,p.Dwgs_User,1.4)
for j,x in enumerate([20,52],1):
 rect(x-11,34.75,x+11,114.75,p.Dwgs_User);text(f'BOTTOM: SSD {j} / 2280',x,96,p.Dwgs_User,1)
text('ASTRA piNas',48,103,p.F_SilkS,1.4);text('REVIEW DRAFT',47,107,p.F_SilkS,1);text('9-25V',94,46,p.F_SilkS,.8);text('PD 20V',73,119,p.F_SilkS,.8);text('UART',90,119,p.F_SilkS,.8)
text('PoE MODULE MECHANICS UNRESOLVED',34,16,p.Dwgs_User,1)
# Unrouted study: no copper pours or fabrication exports. Ground planes planned on In1 and In4.
b.GetDesignSettings().SetBoardThickness(p.FromMM(1.6));p.SaveBoard(str(ROOT/'astra_piNas.kicad_pcb'),b)
(ROOT/'sources/placement.json').write_text(json.dumps({r:{'x':p.ToMM(f.GetPosition().x),'y':p.ToMM(f.GetPosition().y),'angle':f.GetOrientationDegrees(),'side':'B' if f.GetLayer()==p.B_Cu else 'F'} for r,f in F.items()},indent=2))
print('Placed',len(F),'footprints; 100 x 120 mm, six copper layers; unrouted')
