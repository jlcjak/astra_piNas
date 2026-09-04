import json,re,requests,concurrent.futures,datetime
from pathlib import Path
ids='C7435219 C500767 C590854 C19724762 C2848082 C165948 C91145 C2846043 C970725 C2071517 C141836 C250547 C7428653 C123946 C23186 C23138 C98220 C25803 C22840 C23181 C23185 C23098 C25961 C22783 C22880 C22855 C25811 C23024 C1591 C45783 C14860 C1589 C84713 C2847540 C88211 C7519 C123820 C15127 C2103 C21190 C29936 C23231 C23004 C5301773 C19626599 C53444 C8545 C2074262 C48467'.split()
records={}
for p in Path('sources').glob('search_*.json'):
 for i in json.loads(p.read_text())['results']:
  if i['lcsc'] in ids:records[i['lcsc']]=i
H={'User-Agent':'Mozilla/5.0','Referer':'https://www.lcsc.com/'}
def f(n):
 u=f'https://www.lcsc.com/product-detail/{n}.html'
 r=requests.get(u,headers=H,timeout=20);s=r.text
 Path('sources/'+n+'_lcsc.html').write_text(s)
 m=re.search(r'In-Stock(?:<!-- -->)*:\s*(?:<!-- -->)*([\d,]+)',s)
 if not m:m=re.search(r'"stockNumber":(\d+)',s)
 if re.search(r'<title>Page Not Found',s) or records[n]['model'] not in s:m=None
 d=records[n].copy();d['lcsc_stock']=int(m.group(1).replace(',','')) if m else None;d['checked_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();d['url']=u
 print(n,d['lcsc_stock'],flush=True);return n,d
with concurrent.futures.ThreadPoolExecutor(6) as e:records=dict(e.map(f,ids))
Path('sources/catalog.json').write_text(json.dumps(records,indent=2))
