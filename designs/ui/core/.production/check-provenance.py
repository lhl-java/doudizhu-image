import json
import hashlib
import struct
from pathlib import Path
from datetime import datetime, timezone

root = Path(r'D:\work\doudizhu-image')
def read(path):
    return json.loads((root/path).read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256((root/path).read_bytes()).hexdigest()
rows = []
for page in read('docs/UI_SCOPE.json')['pages']:
    if page['batch'] != 'core':
        continue
    g = read(page['generation'])
    raw = (root/page['output']).read_bytes()
    native = struct.unpack('>II', raw[16:24])
    assert list(native) == [g['width'],g['height']], page['id']
    assert sha(page['output']) == g['sha256'], page['id']
    assert g['nativeResolution'] == {'width':native[0],'height':native[1]}
    assert g['exportResolution']['width'] == native[0]
    assert g['exportResolution']['height'] == native[1]
    assert len(g['references']) == 4
    for ref in g['references']:
        assert sha(ref['file']) == ref['sha256'], ref['file']
    prompt = root/g['prompt']
    assert sha(g['prompt']) == g['promptSha256']
    assert prompt.read_text(encoding='utf-8-sig').rstrip('\r\n') == g['submittedParameters']['prompt'].rstrip('\r\n')
    receipt = read(g['evidence']['receipt'])
    assert sha(g['evidence']['receipt']) == g['evidence']['receiptSha256']
    returned = g['evidence']['returnedEvidence']
    source = Path(returned['hostOutputFile'])
    assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == g['sha256']
    args = returned['submittedArguments']
    assert args['prompt'] == g['submittedParameters']['prompt']
    assert args['referenced_image_paths'] == g['submittedParameters']['referenced_image_paths']
    assert args['transparent_background'] is False
    assert g['actualModel'] is None and g['actualQuality'] is None
    assert g['submittedParameters']['model'] is None and g['submittedParameters']['quality'] is None
    assert g['status'] == 'design_ready_user_review' and g['userApproval'] is False
    assert not g['visualQA'].get('blockingIssues',[])
    rows.append(dict(pageId=page['id'],sha256=g['sha256'],nativeResolution=list(native),
                     originalHostOutputMatched=True,promptAndReceiptMatched=True,
                     allFourReferencesMatched=True,modelQualityUnknownPreserved=True))
assert len(rows) == 13
result = dict(batch='core',checkedAt=datetime.now(timezone.utc).isoformat(),status='passed',
              pagesChecked=len(rows),method='Read-only byte hashes, PNG header, JSON provenance checks; no image mutation.',
              pages=rows)
(root/'designs/ui/core/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 13 PNG/source/prompt/receipt/4-reference provenance chains; native sizes and unknown model fields preserved.')
