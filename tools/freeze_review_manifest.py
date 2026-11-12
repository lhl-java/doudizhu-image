"""Freeze the authorized candidate increment; no commit, push, browser or GUI actions."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
TARGET='docs/REVIEW_PUBLICATION_MANIFEST_20261111.json'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
names=set(git('diff','--name-only','-z','HEAD').decode('utf-8').split('\0'))
names.update(git('ls-files','--others','--exclude-standard','-z').decode('utf-8').split('\0'))
rows=[]
for name in sorted(names-{'',TARGET}):
    p=(ROOT/name).resolve()
    if not p.is_relative_to(ROOT) or not p.is_file():raise ValueError('Missing or outside candidate file: '+name)
    data=p.read_bytes()
    if data.startswith(b'version https://git-lfs.github.com/spec/v1'):raise ValueError('LFS pointer: '+name)
    rows.append({'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'gitBlob':git('hash-object','--',name).decode().strip()})
doc={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'userFacingDate':'2026-11-11','status':'candidate_pending_user_review','userArtApproval':False,'productionRuntimeVerified':False,'wholeGameArtCompletion':False,'repository':'https://github.com/lhl-java/doudizhu-image','baseCommit':git('rev-parse','HEAD').decode().strip(),'method':'Exact current increment only; this manifest excludes itself to avoid a self-hash cycle. Original historical publication snapshots retain their fixed meaning.','files':rows,'fileCountExcludingManifest':len(rows),'totalBytesExcludingManifest':sum(r['bytes'] for r in rows),'pushMode':'normal commit and ordinary push; never force or rewrite history'}
(ROOT/TARGET).write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:doc[k] for k in ['status','baseCommit','fileCountExcludingManifest','totalBytesExcludingManifest']}))
