from pathlib import Path
import math
root=Path(__file__).resolve().parents[1]
for name,h in [('SMTSOM225BTR',2.5),('SMTSOM240BTR',4.0)]:
 f=f'(footprint "YIYUAN_{name}" (version 20241229) (generator "astra_piNas") (layer "F.Cu") (attr smd) (descr "M2 soldered spacer H={h}mm. YIYUAN drawing: 6.2mm minimum land, 3.73mm finished hole. Plated hole selected; four paste sectors.") (fp_text reference "REF**" (at 0 -4) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15)))) (fp_text value "{name}" (at 0 4) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15)))) (fp_circle (center 0 0) (end 2.78 0) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab")) (fp_circle (center 0 0) (end 3.35 0) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd")) (pad "1" thru_hole circle (at 0 0) (size 6.2 6.2) (drill 3.73) (layers "*.Cu" "*.Mask"))'
 for q in range(4):
  pts=[]
  for r,angs in [(2.95,range(8,83,6)),(2.0,range(80,7,-6))]:
   for deg in angs:
    a=math.radians(q*90+deg);pts.append(f'(xy {r*math.cos(a):.5f} {r*math.sin(a):.5f})')
  f+='(fp_poly (pts '+''.join(pts)+') (stroke (width 0) (type default)) (fill solid) (layer "F.Paste"))'
 f+=')';(root/'lib/astra_piNas.pretty'/('YIYUAN_'+name+'.kicad_mod')).write_text(f)
