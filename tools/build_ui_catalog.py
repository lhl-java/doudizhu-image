from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
root=Path(__file__).resolve().parents[1]
scopepath=root/'docs/UI_SCOPE.json'
scope=json.loads(scopepath.read_text(encoding='utf-8-sig'))
selected={}
for mp in ['designs/ui/table/manifest.json','designs/ui/core/manifest.json','designs/ui/support/batch-result.json','designs/ui/modes/audit-existing.json']:
    if (root/mp).exists():
        manifest=json.loads((root/mp).read_text(encoding='utf-8-sig'))
        for item in manifest.get('pages',manifest.get('selected',[])):
            if isinstance(item,dict) and item.get('id'):selected[item['id']]=item
rows=[];issues=[]
for p in scope['pages']:
    choice=selected.get(p['id'],{})
    if choice.get('output') or choice.get('image') or choice.get('file'):
        p['output']=choice.get('output') or choice.get('image') or choice.get('file')
        p['generation']=choice.get('generation',p['output'].replace('.png','.generation.json'))
    f=root/p['output'];g=root/p['generation'];s=root/p['stateSpec']
    row=dict(p);row['exists']=f.exists();row['issues']=[];row['stateDetails']=[]
    rec={}
    if f.exists():
        try:
            with Image.open(f) as im: row.update(width=im.width,height=im.height,pixelMode=im.mode);im.verify()
            row['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
        except Exception as e:row['issues'].append('PNG invalid: '+str(e))
    if f.exists() and g.exists():
        try:
            rec=json.loads(g.read_text(encoding='utf-8-sig'))
            if rec.get('sha256','').lower()!=row.get('sha256'):row['issues'].append('Hash mismatch')
            if (rec.get('width'),rec.get('height'))!=(row.get('width'),row.get('height')):row['issues'].append('Dimension mismatch')
            prompt=rec.get('prompt') or rec.get('promptFile')
            if isinstance(prompt,dict):prompt=prompt.get('file') or prompt.get('path')
            if prompt and not (root/prompt).exists():row['issues'].append('Prompt file missing')
            row['actualModel']=rec.get('actualModel');row['actualQuality']=rec.get('actualQuality')
            row['configTarget']=rec.get('configSnapshot',{})
            row['review']=rec.get('visualQA') or rec.get('visualReview') or rec.get('inspection') or rec.get('qa') or rec.get('review') or {}
            review_status=' / '.join([str(rec.get('status','')),str(row['review'].get('status',''))]).lower()
            if any(x in review_status for x in ['needs_fix','pending','rejected','failed','待实际','待检查','需修']):row['issues'].append('Visual review: '+review_status)
        except Exception as e:row['issues'].append('Generation record invalid: '+str(e))
    elif f.exists():row['issues'].append('Generation record missing')
    if s.exists():
        try:
            state=json.loads(s.read_text(encoding='utf-8-sig'));row['stateDetails']=state.get('states',[])
            names={x.get('name',x.get('state')) for x in row['stateDetails'] if isinstance(x,dict)}
            missing=set(p['requiredStates'])-names
            if missing:row['issues'].append('States missing: '+','.join(sorted(missing)))
        except Exception as e:row['issues'].append('State record invalid: '+str(e))
    elif f.exists():row['issues'].append('State specification missing')
    if not f.exists():row['status']='pending'
    elif row['issues']:row['status']='needs_check'
    else:row['status']='design_ready_user_review'
    p['status']=row['status']
    row['searchText']=' '.join([p['id'],p['title'],p['batch']]+p['controls']+p['requiredStates'])
    rows.append(row)
    issues.extend(dict(id=p['id'],message=x) for x in row['issues'])
now=datetime.now(timezone.utc).isoformat()
batch={b:dict(total=sum(p['batch']==b for p in rows),generated=sum(p['batch']==b and p['exists'] for p in rows),ready=sum(p['batch']==b and p['status']=='design_ready_user_review' for p in rows)) for b in ['core','table','modes','support','components']}
report=dict(updatedAt=now,total=len(rows),generated=sum(p['exists'] for p in rows),readyForUserReview=sum(p['status']=='design_ready_user_review' for p in rows),remaining=[p['id'] for p in rows if p['status']!='design_ready_user_review'],batches=batch,issues=issues,pages=rows)
preview=root/'preview';preview.mkdir(exist_ok=True)
(preview/'catalog.js').write_text('window.UI_CATALOG='+json.dumps(report,ensure_ascii=False)+';\n',encoding='utf-8')
(root/'docs/UI_DELIVERY_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scope['updatedAt']=now
scopepath.write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(total=report['total'],generated=report['generated'],readyForUserReview=report['readyForUserReview'],batches=batch,issues=issues),ensure_ascii=False))

