import requests,json,concurrent.futures,re,html
from pathlib import Path
jobs={}
for p in Path('sources').glob('search_*.json'):
 for i in json.loads(p.read_text())['results']:
  if i['stock']>0 and i['datasheet']:jobs[i['lcsc']]=i['datasheet'].replace('https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2','https://datasheet.lcsc.com')
jobs['C7435219']='https://datasheet.lcsc.com/datasheet/pdf/f541aaa18865d3ac3bcd9b3e669f9a59.pdf?productCode=C7435219'
jobs['C970725']='https://datasheet.lcsc.com/datasheet/pdf/4f12eebccb4eda2c0038806df0155265.pdf?productCode=C970725'
def f(t):
 n,u=t
 try:
  r=requests.get(u,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.lcsc.com/'},timeout=15)
  if not r.content.startswith(b'%PDF'):
   m=re.search(r'<iframe[^>]*src="(https://datasheet[^"]+)' ,r.text)
   if m:r=requests.get(html.unescape(m.group(1)),headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.lcsc.com/'},timeout=15)
  if r.content.startswith(b'%PDF'):Path('sources/'+n+'.pdf').write_bytes(r.content);return n,'OK'
  return n,r.status_code
 except Exception:return n,'failed'
with concurrent.futures.ThreadPoolExecutor(8) as e:print(list(e.map(f,jobs.items())))
