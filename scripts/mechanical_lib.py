from pathlib import Path
from sexpr import *
ROOT=Path(__file__).resolve().parents[1];dest=ROOT/'lib/astra_piNas.pretty'
for h,num in [('2.5','9774025243'),('4','9774040243')]:
 name=f'Mounting_Wuerth_WA-SMSI-M2_H{h}mm_{num}'
 s=loads((Path('/usr/share/kicad/footprints/Mounting_Wuerth.pretty')/(name+'.kicad_mod')).read_text());s=[a for a in s if not(isinstance(a,list) and a[0]=='model')];(dest/(name+'.kicad_mod')).write_text(dumps(s))
# Deliberately incomplete candidate footprint. Never infer undimensioned support-pin coordinates.
s='(footprint "WC_PD60B120A_MECHANICAL_REVIEW" (version 20241229) (generator "astra_piNas") (layer "F.Cu") (attr through_hole) (descr "INCOMPLETE: electrical pins only. Support pins 9/10 absent pending manufacturer dimensions. DO NOT FABRICATE.") (fp_text reference "REF**" (at 31 -1.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)))) (fp_text value "POE CANDIDATE - NOT RELEASED" (at 31 13.5) (layer "F.Fab") (effects (font (size 1.2 1.2) (thickness 0.15)))) (fp_rect (start 0 0) (end 62 27) (stroke (width 0.2) (type default)) (layer "F.SilkS")) (fp_rect (start -1 -1) (end 63 28) (stroke (width 0.05) (type default)) (layer "F.CrtYd"))'
for i,x in enumerate([1.22,3.76,6.3,8.84,48.07,50.61,53.15,55.69],1):s+=f'(pad "{i}" thru_hole {"rect" if i==1 else "circle"} (at {x} 24.5) (size 2 2) (drill 1.0) (layers "*.Cu" "*.Mask"))'
s+='(fp_text user "SUPPORT PINS 9/10 UNRESOLVED" (at 31 5) (layer "F.Fab") (effects (font (size 1.2 1.2) (thickness 0.15)))))';(dest/'WC_PD60B120A_MECHANICAL_REVIEW.kicad_mod').write_text(s)
