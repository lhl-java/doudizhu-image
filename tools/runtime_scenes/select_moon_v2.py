"""Select independently reviewed AI repair; retain superseded image evidence only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def write(p,r):(ROOT/p).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
file='assets/scenes/courtyard-moon-v2.png';record=file+'.generation.json'
p=ROOT/file;im=Image.open(p)
assert hashlib.sha256(p.read_bytes()).hexdigest()=='066b7cc70e4c4bd3a19c9eaec57a10287ade566bc6a0204ddfbc320d130d0078'
r=read(record)
assert r['sha256']==hashlib.sha256(p.read_bytes()).hexdigest()
m=read('assets/scenes/scenes.json')
entry=next(x for x in m['assets'] if x['id']=='courtyard-moon')
entry.update(file=file,record=record,width=im.width,height=im.height,status='design_ready_user_review')
write('assets/scenes/scenes.json',m)
old=read('assets/scenes/courtyard-moon.png.generation.json')
old.update(imageRemoved=True,removedAt=datetime.now(timezone.utc).isoformat(),removalReason='Replaced after actual visual review: dark flat-topped artifact at moon upper-left rim corrected by AI edit. User retention rule keeps current final PNG and generation/source evidence only.',supersededBy=file)
write('assets/scenes/courtyard-moon.png.generation.json',old)
r['independentVisualReview']={'status':'passed_for_art_file_review','checkedAt':datetime.now(timezone.utc).isoformat(),'method':'Actual native image pixels viewed with view_image','note':'Moon rim is continuous with soft halo; upper-left dark rectangular intrusion is absent. Architecture, lighting, empty foreground, no baked UI/text/people and original art direction remain consistent.'}
for ref in r.get('references',[]):
    if ref['file']=='assets/scenes/courtyard-moon.png':ref.update(imageRemoved=True,sourceEvidenceRecord='assets/scenes/courtyard-moon.png.generation.json')
write(record,r)
print(json.dumps({'selected':file,'size':im.size,'oldImageEvidenceRecorded':True}))
