from pathlib import Path
from sexpr import *
root=Path(__file__).resolve().parents[1]
for f in (root/'lib/astra_piNas.pretty').glob('*.kicad_mod'):
 s=loads(f.read_text())
 for pad in children(s,'pad'):
  if pad[1]=='' and pad[2]=='thru_hole':
   size=child(pad,'size');drill=child(pad,'drill')
   if len(drill)==2 and float(size[1])==float(drill[1]) and float(size[2])==float(drill[1]):pad[2]=Atom('np_thru_hole')
   elif f.name.startswith('SOIC-8_L4.9'):
    pad[1]='9';child(pad,'layers')[1:]=['*.Cu','*.Mask']
  if f.name.startswith('USB-C_') and pad[2]=='smd':
   pad[:]=[x for x in pad if not(isinstance(x,list) and x[0] in ['clearance','solder_mask_margin'])]
   pad.extend([[Atom('clearance'),Atom('0.09')],[Atom('solder_mask_margin'),Atom('0')]])
 for g in s:
  if isinstance(g,list) and str(g[0]).startswith('fp_') and not (g[0]=='fp_text' and g[1]=='reference'):
   l=child(g,'layer')
   if l and l[1]=='F.SilkS':l[1]='F.Fab'
 f.write_text(dumps(s))
