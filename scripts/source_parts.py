from easyeda2kicad.easyeda.easyeda_api import EasyedaApi
import json,concurrent.futures,urllib.request
from pathlib import Path
queries=['C7435219','C500767','C590854','C19724762','C2848082','C165948','C91145','C2846043','C970725','C2071517','C141836','C250547','C7428653','C123946','0603WAF5101T5E','0603WAF3300T5E','0603WAF1002T5E','0603WAF1003T5E','0603WAF1431T5E','0603WAF4750T5E','0603WAF499JT5E','0603WAF6982T5E','0603WAF2212T5E','0603WAF1153T5E','0603WAF1582T5E','0603WAF1052T5E','0603WAF2003T5E','0603WAF3003T5E','CL10B104KB8NNNC','CL21A226MAQNNNE','CL31B106KAHNNNE','CL10B103KB8NNNC','CL10B272KB8NNNC','SRP7050TA-3R3M','SRP7050TA-3R6M','1uH 3A','USBLC6-2SC6','SMBJ26A','SMBJ20A']
def f(q):
 p=Path('sources/search_'+q.replace('/','_')+'.json')
 r=json.loads(p.read_text()) if p.exists() else EasyedaApi().search_jlcpcb_components(q,page_size=5)
 p.write_text(json.dumps(r,indent=2))
 print(q,[(i['lcsc'],i['model'],i['stock']) for i in r['results']][:5],flush=True)
 if len(r['results'])==1:
  i=r['results'][0];u=i['datasheet'];o=Path('sources/'+i['lcsc']+'.pdf')
  if u and not o.exists():
   try:
    b=urllib.request.urlopen(u,timeout=20).read()
    if b.startswith(b'%PDF'):o.write_bytes(b)
   except Exception:pass
with concurrent.futures.ThreadPoolExecutor(6) as e:list(e.map(f,queries))
