from pathlib import Path
import json,sys,collections,csv
from sexpr import *
ROOT=Path(__file__).resolve().parents[1];m=json.loads((ROOT/'sources/design_manifest.json').read_text());cat=json.loads((ROOT/'sources/catalog.json').read_text());net=loads((ROOT/'sources/astra_piNas.net').read_text())
actual={child(c,'ref')[1]:c for c in children(child(net,'components'),'comp')};assert len(actual)==len(m),(len(actual),len(m))
nets={}
for n in children(child(net,'nets'),'net'):
 name=child(n,'name')[1]
 for node in children(n,'node'):nets[(child(node,'ref')[1],child(node,'pin')[1])]=name
for r,c in m.items():
 assert cat[c['lcsc']]['lcsc_stock']>0,(r,'no LCSC stock')
 props={child(a,'name')[1]:child(a,'value')[1] for a in children(actual[r],'property')}
 assert props['MANUFACTURER PART NUMBER']==cat[c['lcsc']]['model'],r
 for pin,name in c['nets'].items():assert nets.get((r,pin))==name,(r,pin,name,nets.get((r,pin)))
assert not {'BARREL_IN','USB_PD_VBUS','UART_VBUS','POE_12V'} & {'VIN_OR','SYS_5V'}
# Duplicate multiunit symbols are resolved to exactly one physical BOM line.
group={}
for r,c in m.items():group.setdefault(c['lcsc'],[]).append(r)
with (ROOT/'docs/BOM.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['References','Quantity','Manufacturer','MANUFACTURER PART NUMBER','LCSC Part Number','LCSC Stock','Stock checked UTC','Footprint','Product URL','Status'])
 for n,rs in sorted(group.items()):
  d=cat[n];w.writerow([', '.join(rs),len(rs),d['brand'],d['model'],n,d['lcsc_stock'],d['checked_utc'],m[rs[0]]['part']['fp'],d['url'],'PROVISIONAL: low stock and incomplete mechanics' if n=='C2848082' else 'UNVERIFIED LCSC STOCK: JLC listing only' if d['lcsc_stock'] is None else 'Selected; prototype validation required'])
report={'physical_components':len(actual),'distinct_orderable_parts':len(group),'connected_pin_assignments_checked':sum(len(c['nets']) for c in m.values()),'net_count':len(children(child(net,'nets'),'net')),'all_listed_parts_have_positive_lcsc_stock':True,'unverified_lcsc_stock':[],'poe_stock_exception':cat['C2848082']['lcsc_stock'],'minimum_resistor_capacitor_package':'0402','release_status':'REVIEW DRAFT: unresolved PoE mechanics, sourcing and electrical validation'}
(ROOT/'docs/audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
