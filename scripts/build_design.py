from pathlib import Path
import json,re,uuid,copy,math,shutil
from sexpr import *
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'sources/catalog.json').read_text())
LIB=loads((ROOT/'lib/astra_piNas.kicad_sym').read_text())
IMPORTED={s[1]:s for s in children(LIB,'symbol')}
PARTS={}
for name,s in IMPORTED.items():
 props={p[1]:p[2] for p in children(s,'property')}
 n=props.get('LCSC Part')
 if n:PARTS[n]={'name':name,'fp':props['Footprint'].split(':')[-1],'pins':{child(p,'number')[1]:child(p,'name')[1] for u in children(s,'symbol') for p in children(u,'pin')}}
# Retain downloaded originals; generated readable symbols live separately.
Q=lambda s:json.dumps(str(s),ensure_ascii=False)
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'astra_piNas/'+s))
F=lambda n:f'{float(n):.4f}'.rstrip('0').rstrip('.')
SCHEETS={};COMP={};SYMS={};COUNTS={};NOTES={}
def txt(s,x,y,size=1.27):return f'(text {Q(s)} (at {F(x)} {F(y)} 0) (effects (font (size {size} {size})) (justify left)) (uuid {uid(s+str(x)+str(y))}))'
def sheet(name,title,notes=''):
 SCHEETS[name]=[];NOTES[name]=(title,notes)
 SCHEETS[name].append(txt(title,12.7,15.24,2.54))
 if notes:SCHEETS[name].append(txt(notes,12.7,24.13,1.05))
def passive_part(n,kind):
 # Standard KiCad footprints are vendored into the project.
 pkg=CAT[n]['package'];size='1206' if '1206' in pkg else '0805' if '0805' in pkg else '0603'
 metric={'0603':'1608','0805':'2012','1206':'3216'}[size]
 src=f'{"Resistor" if kind=="R" else "Capacitor"}_SMD.pretty/{kind}_{size}_{metric}Metric.kicad_mod'
 fp=Path(src).name[:-10]
 p=ROOT/'lib/astra_piNas.pretty'/Path(src).name
 if not p.exists():
  data=(Path('/usr/share/kicad/footprints')/src).read_text()
  # Remove stock-library 3D paths so the project has no external model dependency.
  v=loads(data);v=[a for a in v if not (isinstance(a,list) and a[0]=='model')];p.write_text(dumps(v))
 return {'name':kind+'_'+n,'fp':fp,'pins':{'1':kind+'1','2':kind+'2'},'kind':kind}
def register(n,kind=None):
 if n in PARTS:return PARTS[n]
 if kind:PARTS[n]=passive_part(n,kind);return PARTS[n]
 raise ValueError(n)
def symbol(symname,p,groups,types):
 if symname in SYMS:return
 props=''.join(f'(property {Q(k)} {Q(v)} (at 0 0 0) (effects (font (size 1 1)) hide))' for k,v in [('Reference','U'),('Value',symname),('Footprint','astra_piNas:'+p['fp'])])
 ss=f'(symbol {Q(symname)} (pin_names (offset 0.8)) (in_bom yes) (on_board yes) {props}'
 locs={}
 for unit,nums in enumerate(groups,1):
  ps=[];kind=p.get('kind')
  if kind:
   # Horizontal two-terminal IEC resistor/capacitor.
   positions=[(-5.08,0,0),(5.08,0,180)];h=5.08;w=2.54
   if kind=='R':shape='(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))'
   else:shape=''.join(f'(polyline (pts (xy {x} -1.778) (xy {x} 1.778)) (stroke (width 0.254) (type default)) (fill (type none)))' for x in [-0.635,0.635])
  else:
   half=math.ceil(len(nums)/2);h=max(7.62,(half+1)*2.54);w=17.78 if max(map(lambda k:len(p['pins'][k]),nums),default=0)<18 else 24.13
   positions=[(-w-5.08,h/2-2.54-j*2.54,0) for j in range(half)]+[(w+5.08,h/2-2.54-j*2.54,180) for j in range(len(nums)-half)]
   shape=f'(rectangle (start {-w} {h/2}) (end {w} {-h/2}) (stroke (width 0.254) (type default)) (fill (type background)))'
  for k,(x,y,a) in zip(nums,positions):
   length=2.54 if kind=='R' else 4.445 if kind=='C' else 5.08
   ps.append(f'(pin {types.get(k,"passive")} line (at {F(x)} {F(y)} {a}) (length {length}) (name {Q("~" if kind else p["pins"][k])} (effects (font (size 0.95 0.95)))) (number {Q(k)} (effects (font (size 0.9 0.9)))))')
   locs[(unit,k)]=(x,y,a)
  ss+=f'(symbol {Q(symname+"_"+str(unit)+"_1")} {shape} '+''.join(ps)+')'
 SYMS[symname]={'sexpr':ss+')','locs':locs,'groups':groups,'part':p}
def add(sh,ref,n,nets,x,y,kind=None,groups=None,unit=1,types=None,symname=None,value=None):
 x=round(x/1.27)*1.27;y=round(y/1.27)*1.27
 p=register(n,kind);pins=p['pins']
 if groups is None:groups=[list(pins)]
 types=types or {};symname=symname or p['name'];symbol(symname,p,groups,types)
 sy=SYMS[symname];h=max([abs(v[1]) for (u,k),v in sy['locs'].items() if u==unit]+[3])+5.08
 if ref not in COMP:COMP[ref]={'ref':ref,'lcsc':n,'part':p,'nets':{str(k):v for k,v in nets.items()},'uuid':uid(ref+'_u'+str(unit)),'sheet':sh,'sym':symname,'value':value or CAT[n]['model']}
 else:assert COMP[ref]['nets']=={str(k):v for k,v in nets.items()}
 c=COMP[ref];mpn=CAT[n]['model'];val=value or mpn
 props=[('Reference',ref,x,y-h,False),('Value',val,x,y-h+2.54,False),('Footprint','astra_piNas:'+p['fp'],x,y,True),('Datasheet',CAT[n]['url'],x,y,True),('MANUFACTURER PART NUMBER',mpn,x,y,True),('Manufacturer',CAT[n]['brand'],x,y,True),('LCSC Part Number',n,x,y,True),('LCSC Stock',str(CAT[n]['lcsc_stock']),x,y,True)]
 ss=f'(symbol (lib_id {Q("astra_piNas:"+symname)}) (at {F(x)} {F(y)} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid {uid(ref+"_u"+str(unit))})'
 for k,v,px,py,hide in props:ss+=f'(property {Q(k)} {Q(v)} (at {F(px)} {F(py)} 0) (effects (font (size 1.0 1.0)){" hide" if hide else ""}))'
 for k in groups[unit-1]:ss+=f'(pin {Q(k)} (uuid {uid(ref+"pin"+k)}))'
 ss+=f'(instances (project "astra_piNas" (path {Q("/"+uid("root")+"/"+uid("sheet_"+sh))} (reference {Q(ref)}) (unit {unit})))))'
 SCHEETS[sh].append(ss)
 for k in groups[unit-1]:
  dx,dy,a=sy['locs'][(unit,k)];px=x+dx;py=y-dy;net=nets.get(k)
  if net is None:SCHEETS[sh].append(f'(no_connect (at {F(px)} {F(py)}) (uuid {uid(ref+k+"nc")}))');continue
  end=px+(-5.08 if a==0 else 5.08)
  SCHEETS[sh].append(f'(wire (pts (xy {F(px)} {F(py)}) (xy {F(end)} {F(py)})) (stroke (width 0) (type default)) (uuid {uid(ref+k+"wire")}))')
  # Global label extends away from the symbol.
  rot=0 if a==0 else 180
  SCHEETS[sh].append(f'(global_label {Q(net)} (shape bidirectional) (at {F(end)} {F(py)} {rot}) (effects (font (size 0.9 0.9)) (justify {"right" if a==0 else "left"})) (uuid {uid(ref+k+"label")}) (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {F(end)} {F(py)} {rot}) (effects (font (size 0.8 0.8)) hide)))')
 return c

def passive(sh,kind,n,value,a,b,x,y,ref=None):
 if ref is None:COUNTS[kind]=COUNTS.get(kind,0)+1;ref=kind+str(COUNTS[kind])
 return add(sh,ref,n,{'1':a,'2':b},x,y,kind=kind,value=value)
RIDS={'330':'C23138','5.1k':'C23186','10k':'C98220','100k':'C25803','1.43k':'C22840','475':'C23181','49.9':'C23185','69.8k':'C23098','22.1k':'C25961','115k':'C22783','15.8k':'C22880','10.5k':'C22855','200k':'C25811','300k':'C23024','1k':'C21190','68k':'C23231','33.2':'C23004'}
CIDS={'100n':'C1591','22u':'C45783','10u50':'C14860','10n':'C1589','2.7n':'C84713','1u':'C29936'}
def res(sh,v,a,b,x,y):return passive(sh,'R',RIDS[v],v,a,b,x,y)
def cap(sh,v,a,b,x,y):return passive(sh,'C',CIDS[v],{'10u50':'10u / 50V','22u':'22u / 25V','100n':'100n / 50V','1u':'1u / 25V'}.get(v,v),a,b,x,y)
# CM5 connector footprint: exact pad coordinates from Raspberry Pi revision 2 design data.
of=loads((ROOT/'sources/cm5io_official/CM5IO.pretty/Raspberry-Pi-5-Compute-Module.kicad_mod').read_text())
fpname='CM5_Amphenol_10164227_1004_OfficialPads'
fp=f'(footprint "{fpname}" (version 20241229) (generator "astra_piNas") (layer "F.Cu") (attr smd) (descr "4mm stacking connector; pad geometry and orientation from official CM5IO rev2. Body 22.6x3.38mm.") (fp_text reference "REF**" (at 0 -12.7) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)))) (fp_text value "10164227-1004A1RLF" (at 0 12.7) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))'
for p0 in children(of,'pad'):
 if p0[1].isdigit() and 1<=int(p0[1])<=100:
  p=copy.deepcopy(p0);a=child(p,'at');a[1]=Atom(F(float(a[1])+0.5));a[2]=Atom(F(float(a[2])+21.5));fp+=dumps(p)
fp+='(fp_rect (start -1.69 -11.3) (end 1.69 11.3) (stroke (width 0.1) (type default)) (layer "F.Fab")) (fp_rect (start -2.2 -11.6) (end 2.2 11.6) (stroke (width 0.05) (type default)) (layer "F.CrtYd")) (fp_line (start -2 -11.5) (end -0.8 -11.5) (stroke (width 0.2) (type default)) (layer "F.SilkS")))'
(ROOT/'lib/astra_piNas.pretty'/f'{fpname}.kicad_mod').write_text(fp)
cmnames={str(int(m.group(1))):m.group(2) for m in re.finditer(r'^\s*(\d{1,3})\s+([A-Za-z][A-Za-z0-9_.+\-]*(?:\s*\(Input\)|\s*\(Output\))?)\s{2,}','\n'.join((ROOT/'sources/cm5.txt').read_text().split('\n')[950:1250]),re.M) if 1<=int(m.group(1))<=200}
# Five-volt entries start with a digit and are supplied explicitly.
for k in [77,79,81,83,85,87]:cmnames[str(k)]='5V_IN'
assert len(cmnames)==200,len(cmnames)
sheet('01_cm5','01 / CM5 Lite interface','4 mm official Amphenol connectors. CM5 Lite required for native microSD. No eMMC module.\nConnector J2 local pin 1 corresponds to module pin 101. UART uses GPIO14/15 with OS configuration.')
cmnets={k:'GND' for k,v in cmnames.items() if v=='GND'}
cmnets.update({str(k):'SYS_5V' for k in [77,79,81,83,85,87]})
cmnets.update({'84':'CM_3V3','86':'CM_3V3','78':'CM_3V3','88':'CM_1V8','90':'CM_1V8','3':'ETH3_P','5':'ETH3_N','4':'ETH1_P','6':'ETH1_N','9':'ETH2_N','11':'ETH2_P','10':'ETH0_N','12':'ETH0_P','15':'ETH_LED_ACT_N','17':'ETH_LED_LINK_N','51':'UART_RX_CM','55':'UART_TX_CM','57':'SD_CLK','61':'SD_DAT3','62':'SD_CMD','63':'SD_DAT0','67':'SD_DAT1','69':'SD_DAT2','75':'SD_PWR_EN','102':'GND','106':'PCIE_PWR_EN','109':'PCIE_RESET_N','110':'HOST_CLK_P','112':'HOST_CLK_N','116':'HOST_RX_P','118':'HOST_RX_N','122':'HOST_TX_P','124':'HOST_TX_N'})
for j,off in [(1,0),(2,100)]:
 p={'name':f'CM5_Connector_J{j}','fp':fpname,'pins':{str(k):cmnames[str(k+off)] for k in range(1,101)}}
 # Each connector is a distinct physical BOM item.
 key='C7435219';PARTS[key]=p
 ns={str(int(k)-off):v for k,v in cmnets.items() if off<int(k)<=off+100}
 supply=[k for k,v in p['pins'].items() if v in ['GND','5V_IN','CM5_3.3V','CM5_1.8V'] or v.startswith('CM5_3.3V') or v.startswith('CM5_1.8V')]
 used=[k for k in ns if k not in supply];unused=[k for k in p['pins'] if k not in supply+used]
 groups=[used,supply,unused]
 for un,x in [(1,70),(2,205),(3,340)]:add('01_cm5','J'+str(j),key,ns,x,80 if j==1 else 205,groups=groups,unit=un,symname=p['name'])
# PCIe switch: ports, configuration and power as independently drawn units.
p=PARTS['C500767'];ns={}
for k,v in p['pins'].items():
 if v in ['VSS','CGND','EP','REXT_GND']:ns[k]='GND'
 elif v in ['VDDC','VDDCAUX','AVDD']:ns[k]='SW_1V0'
 elif v in ['VDDR','VAUX','CVDDR','AVDDH']:ns[k]='CM_3V3'
ns.update({'10':'PCIE_RESET_N','128':'HOST_TX_P','127':'HOST_TX_N','124':'SW_TX0_P','123':'SW_TX0_N','74':'HOST_CLK_P','73':'HOST_CLK_N','110':'SW_REF_P','111':'SW_REF_N','85':'CLK0_P_RAW','83':'CLK0_N_RAW','81':'CLK1_P_RAW','80':'CLK1_N_RAW','78':'CLK2_P_RAW','77':'CLK2_N_RAW','5':'SSD1_RESET_N','6':'SSD2_RESET_N','97':'SSD1_TX_P','98':'SSD1_TX_N','100':'SW_TX1_P','101':'SW_TX1_N','102':'SSD2_TX_P','103':'SSD2_TX_N','106':'SW_TX2_P','107':'SW_TX2_N','86':'SW_IREF','116':'SW_REXT','19':'GND','20':'GND','21':'CM_3V3','33':'SW_SLOTCLK','26':'SW_SMBCLK','27':'SW_SMBDATA','9':'SW_TEST1','16':'SW_TEST2','17':'SW_TEST3','22':'SW_TEST4','25':'SW_TEST5','51':'SW_TEST6','28':'SW_PWR_SAVE','92':'SW_TMS','94':'SW_TRST_N'})
power=[k for k,v in p['pins'].items() if v in ['VSS','CGND','EP','VDDC','VDDCAUX','AVDD','VDDR','VAUX','CVDDR','AVDDH']]
ports=[k for k,v in p['pins'].items() if any(v.startswith(a) for a in ['PERP','PERN','PETP','PETN','REFCLK','DWNRST','PERST','IREF','REXT'])]
config=[k for k in p['pins'] if k not in power+ports];sg=[ports,config,power]
st={k:'power_in' for k in power};st.update({k:'output' for k,v in p['pins'].items() if v.startswith(('PET','DWNRST','REFCLKO','PORTSTATUS'))});st.update({k:'input' for k,v in p['pins'].items() if v.startswith(('PERP','PERN','REFCLKI','REFCLKP','REFCLKN','PERST'))})
sheet('02_pcie','02 / PCIe switch and clock distribution','One upstream x1 Gen 2 link shared by two x1 NVMe links. Port 3 absent. Integrated HCSL clock buffer enabled.\nDefaults intentionally left open where the datasheet permits internal straps. No EEPROM required for default enumeration.')
add('02_pcie','U1','C500767',ns,90,80,groups=sg,unit=1,types=st)
add('02_pcie','U1','C500767',ns,285,80,groups=sg,unit=2,types=st)
# HCSL outputs: 49.9-ohm shunts at source, 33-ish series (use 330 not suitable; use 0 omitted per short-trace study).
# Per datasheet output reference resistor is 475ohm; HCSL termination at source is mandatory.
for i,(a,b) in enumerate([('SW_TX0_P','HOST_RX_P'),('SW_TX0_N','HOST_RX_N'),('SW_TX1_P','SSD1_RX_P'),('SW_TX1_N','SSD1_RX_N'),('SW_TX2_P','SSD2_RX_P'),('SW_TX2_N','SSD2_RX_N'),('CLK0_P_TERM','SW_REF_P'),('CLK0_N_TERM','SW_REF_N')]):cap('02_pcie','100n',a,b,45+(i%4)*95,155+(i//4)*25)
# SSD REFCLK is DC coupled HCSL.
# Net aliases are implemented later by joining the named nodes at switch pins.
for i,(v,a,b) in enumerate([('1.43k','SW_REXT','GND'),('475','SW_IREF','GND')]+[('49.9',f'CLK{k}_{pn}_RAW','GND') for k in range(3) for pn in ['P','N']]+[('5.1k',n,'CM_3V3') for n in ['SW_TEST1','SW_TEST2','SW_SLOTCLK','SW_SMBCLK','SW_SMBDATA']]+[('330',n,'GND') for n in ['SW_TEST3','SW_TEST4','SW_TEST5','SW_TEST6','SW_PWR_SAVE','SW_TMS','SW_TRST_N']]):res('02_pcie',v,a,b,45+(i%4)*95,205+(i//4)*14)
for i,(k,pn) in enumerate([(k,pn) for k in range(3) for pn in ['P','N']]):res('02_pcie','33.2',f'CLK{k}_{pn}_RAW',f'CLK{k}_{pn}_TERM',45+(i%3)*135,280+(i//3)*14)
# Auxiliary power and local bypassing.
sheet('03_aux_power','03 / PCIe core power and bypassing','1.0 V regulator enabled by CM5 3.3 V: I/O supply precedes switch core. Keep each bypass capacitor at its associated supply pin.\nCM5 3.3 V auxiliary load includes switch I/O, clock buffer, microSD and UART I/O; never use it to power SSDs.')
add('03_aux_power','U1','C500767',ns,90,85,groups=sg,unit=3,types=st)
add('03_aux_power','U2','C141836',{'1':'CM_3V3','2':'GND','3':'CORE_SW','4':'SYS_5V','5':'CORE_FB'},285,65,types={'1':'input','2':'power_in','3':'power_out','4':'power_in','5':'input'})
add('03_aux_power','L1','C88211',{'1':'CORE_SW','2':'SW_1V0'},285,100,value='1uH / 3A')
res('03_aux_power','200k','SW_1V0','CORE_FB',235,125);res('03_aux_power','300k','CORE_FB','GND',340,125)
cap('03_aux_power','22u','SW_1V0','GND',285,145);cap('03_aux_power','10u50','SYS_5V','GND',285,165)
for i,k in enumerate([k for k in power if ns[k]!='GND']):
 c=cap('03_aux_power','100n',ns[k],'GND',40+(i%6)*66,200+(i//6)*16);c['near']='U1';c['supply_pin']=k
# SSD connectors: M key, only lane 0 populated. Disable optional sidebands with NC.
sheet('04_nvme','04 / Two M.2 2280 NVMe sockets','NVMe / PCIe SSDs only. SATA M.2 devices are not supported. Both drives run at x1 and share the host Gen 2 x1 link.\nThree 22u capacitors at each socket supplement regulator output capacitors. 2280 retention hardware is a separate mechanical item.')
mp=PARTS['C590854'];mp['pins']={k:k for k in mp['pins']}
for j in [1,2]:
 net={str(k):'GND' for k in [1,3,9,15,21,27,33,39,45,51,57,71,73,75,76,77]};net.update({str(k):f'SSD{j}_3V3' for k in [2,4,12,14,16,18,70,72,74]})
 net.update({'41':f'SSD{j}_RX_P','43':f'SSD{j}_RX_N','47':f'SSD{j}_TX_P','49':f'SSD{j}_TX_N','53':f'CLK{j}_P_TERM','55':f'CLK{j}_N_TERM','50':f'SSD{j}_RESET_N'})
 for k,v in {'41':'PERp0','43':'PERn0','47':'PETp0','49':'PETn0','53':'REFCLKp','55':'REFCLKn','50':'PERST#','52':'CLKREQ#','54':'PEWAKE#','10':'DAS_DSS#'}.items():mp['pins'][k]=v
 for k in net:
  if net[k]=='GND':mp['pins'][k]='GND'
  if net[k].endswith('3V3'):mp['pins'][k]='3V3'
 add('04_nvme','J'+str(j+2),'C590854',net,105 if j==1 else 310,120)
 for i in range(3):cap('04_nvme','22u',f'SSD{j}_3V3','GND',(65 if j==1 else 260)+i*45,240)
# Local power conversion: three independent 5A buck converters.
sheet('05_regulators','05 / Main 5 V and independent SSD power rails','AP64501, 40 V rated synchronous bucks. 5 V input regulator UVLO ~6.5 V; SSD converters enabled by CM5 PCIe power enable.\nSSD supply design target: 3 A per socket. Overall available power remains limited by the selected input source and thermal design.')
for idx,(ref,out,rhi,rc,enable) in enumerate([('U3','SYS_5V','115k','15.8k','MAIN_EN'),('U4','SSD1_3V3','69.8k','10.5k','PCIE_PWR_EN'),('U5','SSD2_3V3','69.8k','10.5k','PCIE_PWR_EN')]):
 x=70+idx*135;pre=ref+'_';net={'1':pre+'BST','2':'VIN_OR','3':enable,'4':pre+'SS','5':pre+'FB','6':pre+'COMP','7':'GND','8':pre+'SW','9':'GND'}
 add('05_regulators',ref,'C2071517',net,x,65,types={'1':'passive','2':'power_in','3':'input','4':'passive','5':'input','6':'passive','7':'power_in','8':'power_out','9':'power_in'})
 add('05_regulators','L'+str(idx+2),'C2847540',{'1':pre+'SW','2':out},x,100,value='3.3uH / 8A')
 cap('05_regulators','100n',pre+'BST',pre+'SW',x,125);cap('05_regulators','10n',pre+'SS','GND',x,145)
 res('05_regulators',rhi,out,pre+'FB',x,165);res('05_regulators','22.1k',pre+'FB','GND',x,185)
 res('05_regulators',rc,pre+'COMP',pre+'COMP_RC',x,205);cap('05_regulators','2.7n',pre+'COMP_RC','GND',x,225)
 for i in range(3):cap('05_regulators','22u',out,'GND',x-40+i*40,245)
 cap('05_regulators','10u50','VIN_OR','GND',x,265)
# Power inputs. PG-controlled MOSFET disconnects USB-C power load until negotiation completes.
sheet('06_inputs','06 / Barrel and USB-C PD power inputs','Center-positive barrel input: 9-25 V DC. USB-C requires a 20 V / 3 A PD supply; its data contacts are unconnected.\nSchottky source OR-ing prevents reverse feed. The highest source normally supplies the load; seamless changeover is not guaranteed.')
add('06_inputs','J5','C7428653',{'4':'BARREL_RAW','2':'GND'},55,65)
add('06_inputs','D1','C123946',{'2':'BARREL_IN','1':'VIN_OR'},155,65)
add('06_inputs','D2','C123820',{'2':'GND','1':'BARREL_IN'},55,110)
res('06_inputs','100k','VIN_OR','MAIN_EN',155,105);res('06_inputs','22.1k','MAIN_EN','GND',155,125)
usb={k:'GND' for k in ['A1B12','B1A12','1','2','3','4']};usb.update({'A4B9':'USB_PD_VBUS','B4A9':'USB_PD_VBUS','A5':'PD_CC1','B5':'PD_CC2'})
add('06_inputs','J6','C165948',usb,280,65)
add('06_inputs','U6','C970725',{'1':'PD_VDD','2':'PD_VDD','3':'GND','6':'PD_CC2','7':'PD_CC1','8':'PD_SENSE','9':'GND','10':'PD_GOOD_N','11':'GND'},280,145,types={'1':'power_in','2':'input','3':'input','4':'bidirectional','5':'bidirectional','6':'bidirectional','7':'bidirectional','8':'input','9':'input','10':'open_collector','11':'power_in'})
passive('06_inputs','R','C2074262','1k / 0.5W','USB_PD_VBUS','PD_VDD',55,180);cap('06_inputs','1u','PD_VDD','GND',155,180);res('06_inputs','10k','USB_PD_VBUS','PD_SENSE',55,205)
add('06_inputs','Q1','C15127',{'1':'PD_GATE','2':'USB_PD_VBUS','3':'USB_PD_SWITCHED'},155,220)
res('06_inputs','100k','USB_PD_VBUS','PD_GATE',55,245);res('06_inputs','10k','PD_GATE','PD_GATE_SINK',155,255)
add('06_inputs','D3','C2103',{'1':'USB_PD_VBUS','2':'PD_GATE'},280,215,value='10V gate clamp')
add('06_inputs','D4','C123946',{'2':'USB_PD_SWITCHED','1':'VIN_OR'},375,215)
cap('06_inputs','1u','USB_PD_VBUS','GND',280,255);cap('06_inputs','10u50','VIN_OR','GND',375,255)
# Ethernet and PoE. Footprint provisional pending manufacturer confirmation of support-foot coordinates.
sheet('07_ethernet_poe','07 / Gigabit Ethernet and PoE++ candidate','PoE module is a PROVISIONAL sourcing choice: only 15 in LCSC stock at capture. Low stock does not satisfy the original deep-stock requirement.\nDo not release this sheet for manufacture until module pin 9/10 mechanical coordinates and 802.3bt class power are confirmed.')
et={'21':'GND','22':'GND','11':'ETH0_P','10':'ETH0_N','4':'ETH1_P','5':'ETH1_N','3':'ETH2_P','2':'ETH2_N','8':'ETH3_P','9':'ETH3_N','12':'ETH_CT0','6':'ETH_CT1','1':'ETH_CT2','7':'ETH_CT3','13':'POE_VA1','14':'POE_VA2','15':'POE_VB1','16':'POE_VB2','17':'ETH_LED_A','18':'ETH_LED_ACT_N','19':'ETH_LED_Y','20':'ETH_LED_LINK_N'}
add('07_ethernet_poe','J8','C19724762',et,90,90)
for i in range(4):cap('07_ethernet_poe','100n',f'ETH_CT{i}','GND',45+i*100,165)
res('07_ethernet_poe','330','CM_3V3','ETH_LED_A',90,200);res('07_ethernet_poe','330','CM_3V3','ETH_LED_Y',235,200)
PARTS['C2848082']={'name':'WC_PD60B120A_CANDIDATE','fp':'WC_PD60B120A_MECHANICAL_REVIEW','pins':{'1':'VA1','2':'VA2','3':'VB1','4':'VB2','5':'VOUT-','6':'VOUT-','7':'VOUT+','8':'VOUT+','9':'SUPPORT_NC','10':'SUPPORT_NC'}}
add('07_ethernet_poe','U7','C2848082',{'1':'POE_VA1','2':'POE_VA2','3':'POE_VB1','4':'POE_VB2','5':'GND','6':'GND','7':'POE_12V','8':'POE_12V'},300,85,types={'7':'power_out','8':'passive'})
add('07_ethernet_poe','D5','C123946',{'2':'POE_12V','1':'VIN_OR'},340,140)
cap('07_ethernet_poe','10u50','POE_12V','GND',90,235)
# SD and USB-UART.
sheet('08_sd_uart','08 / microSD and USB-UART','USB-UART is independently powered by its USB cable; VIO follows CM5 3.3 V. No connection between debug VBUS and SYS_5V.\nGPIO14/15 UART requires OS configuration; this is not the separate CM5 on-module boot-debug UART.')
add('08_sd_uart','J9','C91145',{'1':'SD_DAT2','2':'SD_DAT3','3':'SD_CMD','4':'SD_3V3','5':'SD_CLK','6':'GND','7':'SD_DAT0','8':'SD_DAT1','10':'GND','11':'GND','12':'GND','13':'GND'},65,85)
add('08_sd_uart','U8','C250547',{'1':'SD_3V3','2':'GND','4':'SD_PWR_EN','5':'CM_3V3'},65,145,types={'1':'power_out','2':'power_in','3':'open_collector','4':'input','5':'power_in'})
cap('08_sd_uart','100n','CM_3V3','GND',45,190);cap('08_sd_uart','22u','SD_3V3','GND',130,190)
for i,k in enumerate(['SD_CMD','SD_DAT0','SD_DAT1','SD_DAT2','SD_DAT3']):res('08_sd_uart','10k','SD_3V3',k,45+(i%2)*85,215+(i//2)*20)
usb={k:'GND' for k in ['A1B12','B1A12','1','2','3','4']};usb.update({'A4B9':'UART_VBUS','B4A9':'UART_VBUS','A5':'UART_CC1','B5':'UART_CC2','A6':'UART_USB_P','B6':'UART_USB_P','A7':'UART_USB_N','B7':'UART_USB_N'})
add('08_sd_uart','J7','C165948',usb,245,75)
add('08_sd_uart','U9','C2846043',{'1':'CM_3V3','2':'GND','3':'UART_VBUS','4':'UART_TX_BRIDGE','5':'UART_RX_BRIDGE','6':'UART_V3','7':'UART_USB_P','8':'UART_USB_N','9':'UART_VBUS','17':'GND'},350,75,types={'1':'power_in','2':'power_in','3':'power_in','4':'output','5':'input','6':'power_out','7':'bidirectional','8':'bidirectional','9':'input','17':'power_in'})
add('08_sd_uart','U10','C7519',{'1':'UART_USB_P','2':'GND','3':'UART_USB_N','4':'UART_USB_N','5':'UART_VBUS','6':'UART_USB_P'},300,145)
for i,(v,a,b) in enumerate([('5.1k','UART_CC1','GND'),('5.1k','UART_CC2','GND'),('330','UART_TX_BRIDGE','UART_RX_CM'),('330','UART_TX_CM','UART_RX_BRIDGE')]):res('08_sd_uart',v,a,b,245+(i%2)*105,200+(i//2)*22)
for i,(a,b) in enumerate([('UART_VBUS','GND'),('UART_V3','GND'),('CM_3V3','GND')]):cap('08_sd_uart','100n',a,b,225+i*75,260)
# CM5 input bulk decoupling kept on board under the module.
for i in range(3):
 c=cap('03_aux_power','22u','SYS_5V','GND',270+i*55,180);c['near']='J1'
# Stocked soldered retention spacers. M2 screws pass through the CM5 2.7mm holes.
for n,h,num,sh in [('C5301773','2.5','SMTSOM225BTR','04_nvme'),('C19626599','4','SMTSOM240BTR','01_cm5')]:
 PARTS[n]={'name':'Spacer_'+num,'fp':f'YIYUAN_{num}','pins':{'1':'CHASSIS_GND'}}
 for i in range(2 if h=='2.5' else 4):add(sh,'H'+str(i+1 if h=='2.5' else i+3),n,{'1':'GND'},450+(i%2)*70,160+(i//2)*30,value='M2 spacer / '+h+'mm')
add('06_inputs','F1','C48467',{'1':'BARREL_RAW','2':'BARREL_IN'},455,70,value='5A / 125V fast fuse')
# Low-voltage PG is isolated from the 20V PMOS gate by a level shifter.
add('06_inputs','Q2','C53444',{'1':'PD_PNP_BASE','2':'PD_VDD','3':'PD_GATE_ENABLE'},460,145)
add('06_inputs','Q3','C8545',{'1':'PD_GATE_ENABLE','2':'GND','3':'PD_GATE_SINK'},530,160)
res('06_inputs','10k','PD_PNP_BASE','PD_GOOD_N',460,185)
res('06_inputs','100k','PD_PNP_BASE','PD_VDD',530,185)
res('06_inputs','100k','PD_GATE_ENABLE','GND',460,215)
cap('06_inputs','100n','PD_GATE','USB_PD_VBUS',530,215)
# Sustain the PoE converter minimum output load when another input wins the OR circuit.
passive('07_ethernet_poe','R','C2074262','1k / 0.5W','POE_12V','GND',250,240)
# Power flags document supplies driven through connectors, inductors and resistors.
flag='(symbol "Power_Source" (power) (pin_names (offset 0)) (in_bom no) (on_board no) (property "Reference" "#FLG" (at 0 0 0) (effects (font (size 1 1)) hide)) (property "Value" "Power_Source" (at 0 2.54 0) (effects (font (size 1 1)) hide)) (symbol "Power_Source_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))))'
SYMS['Power_Source']={'sexpr':flag}
for i,(sh,net) in enumerate([('03_aux_power','CM_3V3'),('03_aux_power','GND'),('03_aux_power','SW_1V0'),('03_aux_power','SYS_5V'),('06_inputs','VIN_OR'),('06_inputs','PD_VDD'),('08_sd_uart','UART_VBUS')]):
 x=round((450+i%4*30)/1.27)*1.27;y=round((80+i//4*20)/1.27)*1.27
 SCHEETS[sh].append(f'(symbol (lib_id "astra_piNas:Power_Source") (at {F(x)} {F(y)} 0) (unit 1) (in_bom no) (on_board no) (uuid {uid("flag"+net)}) (property "Reference" "#FLG0{i+1}" (at {F(x)} {F(y)} 0) (effects (font (size 1 1)) hide)) (property "Value" "Power_Source" (at {F(x)} {F(y)} 0) (effects (font (size 1 1)) hide)) (instances (project "astra_piNas" (path {Q("/"+uid("root")+"/"+uid("sheet_"+sh))} (reference "#FLG0{i+1}") (unit 1)))))')
 SCHEETS[sh].append(f'(global_label {Q(net)} (shape input) (at {F(x)} {F(y)} 0) (effects (font (size 1 1)) (justify right)) (uuid {uid("flaglabel"+net)}))')
# Export a self-contained symbol library and hierarchical schematics.
symlib='(kicad_symbol_lib (version 20231120) (generator "astra_piNas") '+''.join(s['sexpr'] for s in SYMS.values())+')'
(ROOT/'lib/design.kicad_sym').write_text(symlib)
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "astra_piNas") (type "KiCad") (uri "${KIPRJMOD}/lib/design.kicad_sym") (options "") (descr "Self-contained validated and provisional design symbols")))')
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "astra_piNas") (type "KiCad") (uri "${KIPRJMOD}/lib/astra_piNas.pretty") (options "") (descr "Project-local footprints")))')
root=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid("root")}) (paper "A3") (title_block (title "Astra piNas / CM5 dual NVMe carrier") (rev "0.1 REVIEW DRAFT") (company "Project-local libraries / LCSC sourcing")) (lib_symbols)'
root+=txt('ASTRA piNas',20,20,5)+txt('CM5 LITE / DUAL 2280 NVMe / GIGABIT ETHERNET',20,33,2)
root+=txt('REVIEW DRAFT — POE SOURCING AND MECHANICAL VERIFICATION OPEN\nUnrouted placement study. Do not fabricate. See docs/REVIEW.md.',20,48,1.5)
for i,(sh,items) in enumerate(SCHEETS.items()):
 x=25+(i%3)*130;y=80+(i//3)*55
 root+=f'(sheet (at {x} {y}) (size 110 38) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {uid("sheet_"+sh)}) (property "Sheetname" {Q(NOTES[sh][0])} (at {x} {y-1.27} 0) (effects (font (size 1.27 1.27)) (justify left bottom))) (property "Sheetfile" {Q(sh+".kicad_sch")} (at {x} {y+39.27} 0) (effects (font (size 1.0 1.0)) (justify left top))) (instances (project "astra_piNas" (path {Q("/"+uid("root"))} (page {Q(i+2)})))))'
 used={n for n in SYMS if any('(lib_id '+Q('astra_piNas:'+n)+')' in z for z in items)}
 cached=''.join(SYMS[n]['sexpr'].replace('(symbol '+Q(n),'(symbol '+Q('astra_piNas:'+n),1) for n in used)
 s=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid("file_"+sh)}) (paper "A2") (title_block (title {Q(NOTES[sh][0])}) (rev "0.1 REVIEW DRAFT")) (lib_symbols {cached}) '+''.join(items)+')'
 (ROOT/(sh+'.kicad_sch')).write_text(s)
root+=f'(sheet_instances (path "/" (page "1"))))'
(ROOT/'astra_piNas.kicad_sch').write_text(root)
(ROOT/'astra_piNas.kicad_pro').write_text(json.dumps({'meta':{'filename':'astra_piNas.kicad_pro','version':1},'board':{'design_settings':{'defaults':{'board_outline_line_width':0.05},'rules':{'min_clearance':0.127,'min_track_width':0.127,'min_via_diameter':0.6,'min_through_hole_diameter':0.3}}}},indent=2))
(ROOT/'sources/design_manifest.json').write_text(json.dumps(COMP,indent=2))
print('Generated',len(COMP),'components,',len(SYMS),'symbols,',len(SCHEETS)+1,'sheets')
