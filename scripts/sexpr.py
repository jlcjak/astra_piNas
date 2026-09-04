import re,json
class Atom(str):pass
def loads(t):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',t);stack=[];r=None
 for v in ts:
  if v=='(':
   n=[]
   if stack:stack[-1].append(n)
   stack.append(n)
  elif v==')':r=stack.pop()
  else:stack[-1].append(json.loads(v) if v.startswith('"') else Atom(v))
 if stack:raise ValueError("Unbalanced expression")
 return r
def dumps(x):
 if isinstance(x,list):return '('+' '.join(dumps(y) for y in x)+')'
 if isinstance(x,Atom):return str(x)
 return json.dumps(x,ensure_ascii=False)
def children(x,k):return [y for y in x if isinstance(y,list) and y and y[0]==k]
def child(x,k,default=None):return next(iter(children(x,k)),default)
