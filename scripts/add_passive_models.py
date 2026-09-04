"""Vendor KiCad passive STEP models and attach them without changing PCB geometry."""
from pathlib import Path
import copy, hashlib, json, re, shutil
from sexpr import loads, children
ROOT=Path(__file__).resolve().parents[1]
board=ROOT/'astra_piNas.kicad_pcb'
text=board.read_text(); before=loads(text)
models={}; references=[]
for fp in children(before,'footprint'):
    props={x[1]:x[2] for x in children(fp,'property')}
    if props['Reference'].startswith(('R','C')) and not children(fp,'model'):
        name=fp[1].split(':')[-1]
        assert re.fullmatch(r'[RC]_\d{4}_\d{4}Metric',name),name
        models[name]=f'${{KIPRJMOD}}/lib/astra_piNas.3dshapes/{name}.step'
        references.append(props['Reference'])
if not models:
    print('All resistor and capacitor models are already attached.')
    raise SystemExit(0)
for name in models:
    family='Resistor' if name.startswith('R') else 'Capacitor'
    source=Path('/usr/share/kicad/3dmodels')/f'{family}_SMD.3dshapes'/(name+'.step')
    dest=ROOT/'lib/astra_piNas.3dshapes'/source.name
    shutil.copyfile(source,dest)
def block(path,indent):
    return (f'{indent}(model "{path}"\n'
            f'{indent}\t(offset (xyz 0 0 0))\n'
            f'{indent}\t(scale (xyz 1 1 1))\n'
            f'{indent}\t(rotate (xyz 0 0 0))\n{indent})\n')
def patch(match):
    text=match.group();fp=loads(text);name=fp[1].split(':')[-1]
    if name not in models or children(fp,'model'):return text
    return text[:-2]+block(models[name],'\t\t')+'\t)'
new=re.sub(r'^\t\(footprint .*?^\t\)',patch,text,flags=re.M|re.S)
after=loads(new)
def without_models(tree):
    tree=copy.deepcopy(tree)
    for fp in children(tree,'footprint'):
        fp[:]=[x for x in fp if not(isinstance(x,list) and x and x[0]=='model')]
    return tree
assert without_models(before)==without_models(after),'Unexpected PCB change'
for name,path in models.items():
    file=ROOT/'lib/astra_piNas.pretty'/(name+'.kicad_mod')
    old=file.read_text();parsed=loads(old)
    assert not children(parsed,'model'),name
    newfp=old.rstrip()[:-1]+block(path,'\t')+')\n'
    assert loads(newfp)[:-1]==parsed
    file.write_text(newfp)
board.write_text(new)
report={'added_models':len(models),'updated_passives':len(references),'references':sorted(references),
        'board_geometry_and_connectivity_unchanged':True,
        'model_kind':'Generic KiCad package visualization, not manufacturer-specific mechanical certification',
        'pcb_sha256':hashlib.sha256(board.read_bytes()).hexdigest()}
(ROOT/'docs/passive_models.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='references'},indent=2))
