from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,ast,sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
root=Path(__file__).resolve().parents[1]
scope=json.loads((root/'docs/UI_SCOPE.json').read_text(encoding='utf-8-sig'))
errors=[];state_counts=Counter();page_results=[];unknown_versions=0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in scope['pages']:
    row=dict(id=p['id'],image=p['output'],errors=[])
    image=root/p['output'];record=root/p['generation'];spec=root/p['stateSpec']
    if not image.exists() or not record.exists() or not spec.exists():
        row['errors'].append('selected image/record/states missing')
    else:
        rec=json.loads(record.read_text(encoding='utf-8-sig'))
        st=json.loads(spec.read_text(encoding='utf-8-sig'))
        qa=rec.get('visualQA') or rec.get('visualReview') or rec.get('inspection') or rec.get('qa') or rec.get('review') or {}
        qa_status=(str(rec.get('status',''))+' / '+str(qa.get('status',''))).lower()
        if any(x in qa_status for x in ['needs_fix','pending','rejected','failed','待实际','待检查','需修']):row['errors'].append('visual QA incomplete: '+qa_status)
        if sha(image)!=rec.get('sha256','').lower():row['errors'].append('image SHA256 differs from generation')
        with Image.open(image) as im:
            if [im.width,im.height]!=[rec.get('width'),rec.get('height')]:row['errors'].append('native dimensions differ')
            im.verify()
        states={x.get('name',x.get('state')):x for x in st.get('states',[]) if isinstance(x,dict)}
        for needed in p['requiredStates']:
            v=states.get(needed)
            if not v:row['errors'].append('required state missing: '+needed);continue
            cov=v.get('coverage','unspecified');state_counts[cov]+=1
            if cov not in ['rendered','shared_component']:row['errors'].append('required state not designed: '+needed+' / '+cov)
        route=rec.get('route')
        if route=='builtin':
            if rec.get('actualModel') is None or rec.get('actualQuality') is None:unknown_versions+=1
            if not rec.get('configSnapshot'):row['errors'].append('configuration snapshot absent')
        prompt=rec.get('prompt') or rec.get('promptFile')
        if isinstance(prompt,dict):prompt=prompt.get('file') or prompt.get('path')
        if prompt:
            pp=root/prompt
            if not pp.exists():row['errors'].append('prompt missing')
            elif rec.get('promptSha256') and rec['promptSha256'].lower()!=sha(pp):row['errors'].append('prompt hash differs')
        for r in rec.get('references',[]):
            if not isinstance(r,dict):continue
            ref=r.get('file') or r.get('path')
            if ref and r.get('sha256'):
                path=root/ref
                if path.exists() and sha(path)!=r['sha256'].lower():row['errors'].append('reference hash differs: '+ref)
                elif not path.exists() and not r.get('imageRemoved'):row['errors'].append('reference missing: '+ref)
    errors.extend(dict(id=p['id'],reason=e) for e in row['errors']);page_results.append(row)
assets=json.loads((root/'assets/ui/manifest.json').read_text(encoding='utf-8-sig'))
for a in assets['assets']:
    p=root/a['file']
    if not p.exists() or sha(p)!=a['sha256']:errors.append(dict(id='assets',reason='missing or mismatched '+a['file']))
deck=[a for a in assets['assets'] if a['file'].startswith('assets/ui/cards/')]
if len(deck)!=54 or len({a['file'] for a in deck})!=54:errors.append(dict(id='cards',reason='deck must contain 54 unique cards'))
for suit in ['spades','hearts','clubs','diamonds']:
    if {a['rank'] for a in deck if a.get('suit')==suit}!={'A','2','3','4','5','6','7','8','9','10','J','Q','K'}:errors.append(dict(id='cards',reason='rank set incomplete '+suit))
for script in (root/'tools').glob('*.py'):
    try:ast.parse(script.read_text(encoding='utf-8-sig'))
    except SyntaxError as e:errors.append(dict(id='script',reason=str(e)))
report=dict(verifiedAt=datetime.now(timezone.utc).isoformat(),selectedPageCount=len(scope['pages']),allPagesSelectedAndVerified=not errors,requiredStateCoverage=dict(state_counts),sharedAssetCount=len(assets['assets']),deckCount=len(deck),selectedBuiltinWithUndisclosedModelOrQuality=unknown_versions,errors=errors,pages=page_results,note='Visual review supplied per selected generation record and batch reports; mechanical checks validate selected files, hashes, native dimensions, state presence and asset completeness. Shared component states are design reuse, not separate native AI renders.')
(root/'docs/FINAL_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='pages'},ensure_ascii=False))

