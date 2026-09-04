from pathlib import Path
import pcbnew as p,json,sys
ROOT=Path(__file__).resolve().parents[1];M=json.loads((ROOT/'sources/design_manifest.json').read_text());b=p.LoadBoard(str(ROOT/'astra_piNas.kicad_pcb'));F={f.GetReference():f for f in b.GetFootprints()};assert set(F)==set(M),(set(F)^set(M))
checked=0
for r,c in M.items():
 f=F[r];pads={}
 for pad in f.Pads():pads.setdefault(pad.GetNumber(),[]).append(pad)
 for pin,n in c['nets'].items():
  assert pin in pads,(r,pin,'missing pad')
  for pad in pads[pin]:assert pad.GetNetname()==n,(r,pin,n,pad.GetNetname());checked+=1
 assert f.GetPath().AsString().endswith(c['uuid']),r
# Placement orientation and high-consequence geometry checks.
for r in ['J3','J4']:
 f=F[r];assert f.GetLayer()==p.B_Cu
 peg=[a for a in f.Pads() if a.GetNumber()=='' and a.GetDrillSize().x>0][0]
 assert peg.GetPosition().y>f.GetPosition().y,'SSD insertion direction inverted'
assert abs(p.ToMM(F['J2'].GetPosition().x-F['J1'].GetPosition().x)-34)<1e-6
assert F['J2'].GetPosition().y==F['J1'].GetPosition().y
from sexpr import loads,children,child
bs=loads((ROOT/'astra_piNas.kicad_pcb').read_text());tracks=len(children(bs,'segment'))+len(children(bs,'via'));assert tracks>0
assert b.GetCopperLayerCount()==6
for f in F.values():
 assert f.GetField('MANUFACTURER PART NUMBER').GetText().strip(),f.GetReference()
assert not any(child(q,'net')[1]==next(pd.GetNetname() for pd in F['U1'].Pads() if pd.GetNumber()=='24') for q in children(bs,'segment')+children(bs,'via')),'RXPOLINV_DIS must remain untraced'
out={'footprints':len(F),'connected_pads_checked':checked,'copper_layers':b.GetCopperLayerCount(),'tracks_and_vias':tracks,'schematic_paths_match':True,'cm5_connector_separation_mm':34,'ssd_insertion_direction':'positive Y, underside','provisional_missing_poe_support_pads':['U7.9','U7.10']}
(ROOT/'docs/board_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
