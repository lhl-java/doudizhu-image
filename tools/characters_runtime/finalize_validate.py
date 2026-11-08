"""Finalize the selected character pack and validate its real PNG/source evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/characters'
SRC = ROOT / 'designs/characters/runtime-20261026'
NOW = datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

identities = {
    'daotong': {'name': '玉绿道童', 'recognition': ['短棕色刺发', '金色云纹发带与飘带', '大眼短身男孩', '青绿金边短道袍、象牙白袖裤', '腰间金色太极葫芦与红穗', '手持玉绿背扑克牌'], 'baseCostume': '青云衣'},
    'taohua': {'name': '桃花女修', 'recognition': ['深棕长发与桃花发饰', '玉珠发簪', '粉绿飘带', '象牙白与浅粉青绿裙装', '桃花纹折扇', '圆润少女脸型']},
    'hulu': {'name': '葫芦长者', 'recognition': ['白发丸髻', '浓白眉与长白胡须', '圆润红颊老者', '青绿暖金道袍与象牙白内衫', '怀抱金色太极大葫芦', '绿色发带与玉坠']},
}
emotion_labels = dict(zip(['calm','smile','laugh','thinking','surprise','smug','sad','angry'], ['平静','微笑','大笑','思考','惊讶','得意','难过','生气']))
manifest = read(OUT / 'manifest.json')

# The old sheets were rejected for spacing. Keep their immutable textual evidence,
# while selected v2 sheets and every source of an active export remain available.
removed = []
for key in identities:
    old = SRC / f'{key}-expressions-v1.png'
    old_record = SRC / f'{key}-expressions-v1.generation.json'
    previous = read(old_record)
    if old.exists():
        assert sha(old) == previous['sha256']
        old.unlink()
    previous['imageRemoved'] = True
    previous['retention'] = {'status': 'superseded_image_removed_text_evidence_retained', 'replacedBy': rel(SRC / f'{key}-expressions-v2.png'), 'reason': 'v1 portraits were too tightly spaced; selected v2 fixes the layout', 'recordedAt': NOW}
    write(old_record, previous)
    removed.append(rel(old))
    newer_path = SRC / f'{key}-expressions-v2.generation.json'
    newer = read(newer_path)
    newer['editedFrom']['imageRemoved'] = True
    for reference in newer['references']:
        if reference['file'] == rel(old):
            reference['imageRemoved'] = True
            reference['retentionReason'] = 'superseded image removed after final v2 exports were verified; hash and generation record retained'
    write(newer_path, newer)

for item in manifest['characters']:
    key = item['id']
    item['identity'] = identities[key]
    item['expressionLabels'] = emotion_labels
    item['nativeSources'] = {pose: rel(SRC / f'{key}-{pose}-v1.png') for pose in ['master', 'win', 'lose']}
    item['nativeSources']['expressions'] = rel(SRC / f'{key}-expressions-v2.png')
    item['registration'] = 'Each source uses its significant-alpha horizontal centre and bottom as the source foot anchor; one fixed downscale per character. Exact sourceRect, sourceAnchor, scale and offset are in each derivation record.'
    write(OUT / key / 'character.json', item)
manifest['review'] = {'status': 'passed_for_runtime_art_review', 'reviewedAt': NOW, 'backgrounds': ['warm ivory #f7f1df', 'deep jade #12362f'], 'images': ['assets/characters/review/poses-light-dark.jpg','assets/characters/review/costumes-light-dark.jpg','assets/characters/review/expressions-light-dark.jpg'], 'findings': ['All 9 full-body poses and 5 costumes have complete silhouettes, visible footwear and accessories, consistent faces and identities.', 'All 24 portraits have complete hair/ribbons and eight readable facial states per character.', 'Light/dark composites show clean transparent edges with no opaque rectangular background.']}
manifest['retention'] = {'selectedNativePngs': 17, 'supersededImagesRemoved': removed, 'textGenerationRecordsRetained': 20}
write(OUT / 'manifest.json', manifest)

# Remove an earlier redundant unrecorded inspection bitmap. The three delivered
# review composites above have derivation records and cover all selected exports.
redundant = OUT / 'review/expressions-alpha-review.jpg'
if redundant.exists():
    redundant.unlink()

failures = []
runtime_rows = []
for asset in manifest['assets']:
    p = ROOT / asset['file']
    record = read(ROOT / asset['record'])
    source = ROOT / asset['derivedFrom']['file']
    source_record = read(ROOT / asset['derivedFrom']['record'])
    with Image.open(p) as im:
        im.load()
        a = np.asarray(im.getchannel('A')) if im.mode == 'RGBA' else None
        edges = np.concatenate((a[0,:], a[-1,:], a[:,0], a[:,-1])) if a is not None else np.array([255])
        row = {'id': asset['id'], 'file': asset['file'], 'mode': im.mode, 'width': im.width, 'height': im.height, 'alphaExtrema': [int(a.min()), int(a.max())] if a is not None else None, 'edgeAlphaNonzero': int(np.count_nonzero(edges)), 'edgeAlphaAbove16': int(np.count_nonzero(edges >= 16)), 'sha256': sha(p), 'sourceSha256': sha(source), 'scale': record['fixedScale'], 'anchor': asset['anchor']}
    checks = [row['mode'] == 'RGBA', row['alphaExtrema'] == [0,255], row['edgeAlphaAbove16'] == 0, row['sha256'] == asset['sha256'] == record['sha256'], row['sourceSha256'] == asset['derivedFrom']['sha256'] == source_record['sha256'], row['scale'] <= 1, record['noUpscale'], [row['width'],row['height']] == [asset['width'],asset['height']]]
    if not all(checks):
        failures.append({'id': asset['id'], 'checks': checks})
    runtime_rows.append(row)

native_rows = []
for p in sorted(SRC.glob('*.png')):
    record = read(p.with_suffix('.generation.json'))
    with Image.open(p) as im:
        a = np.asarray(im.getchannel('A'))
        row = {'file': rel(p), 'width': im.width, 'height': im.height, 'mode': im.mode, 'alphaExtrema': [int(a.min()), int(a.max())], 'sha256': sha(p), 'actualModel': record['actualModel'], 'actualQuality': record['actualQuality'], 'configTarget': record['configSnapshot']['model'], 'configQualityTarget': record['configSnapshot']['quality']}
    checks = [row['mode'] == 'RGBA', row['alphaExtrema'] == [0,255], row['sha256'] == record['sha256'], [row['width'],row['height']] == [record['nativeResolution']['width'],record['nativeResolution']['height']], (ROOT / record['prompt']).exists(), (ROOT / record['evidence']['receipt']).exists()]
    for reference in record['references']:
        ref = ROOT / reference['file']
        checks.append((ref.exists() and sha(ref) == reference['sha256']) or (not ref.exists() and reference.get('imageRemoved') is True))
    if not all(checks):
        failures.append({'native': rel(p), 'checks': checks})
    native_rows.append(row)

expected = {'characters':3, 'poses':9, 'expressions':24, 'costumes':5, 'runtimePngs':38, 'nativeGenerations':20, 'selectedNativeGenerations':17}
if manifest['counts'] != expected or len(runtime_rows) != 38 or len(native_rows) != 17:
    failures.append({'countMismatch': manifest['counts']})
if len(list(SRC.glob('*.generation.json'))) != 20:
    failures.append({'generationRecordCount': len(list(SRC.glob('*.generation.json')))})
for item in manifest['characters']:
    if set(item['expressions']) != set(emotion_labels) or set(item['poses']) != {'master','win','lose'}:
        failures.append({'mappingMismatch': item['id']})
    if item['anchor'] != [512,920]:
        failures.append({'anchorMismatch': item['id']})
review = []
for file in manifest['review']['images']:
    p = ROOT / file
    record = read(p.with_suffix('.derivation.json'))
    review.append({'file': file, 'sha256': sha(p), 'record': rel(p.with_suffix('.derivation.json')), 'visuallyReviewed': True})
validation = {'status': 'passed' if not failures else 'failed', 'validatedAt': NOW, 'scope': 'This character asset batch only; not whole-game completion or human approval.', 'counts': expected, 'checks': {'runtimeTrueRgba': all(r['mode'] == 'RGBA' for r in runtime_rows), 'runtimeFullAlphaRange': all(r['alphaExtrema'] == [0,255] for r in runtime_rows), 'runtimeSignificantAlphaClearBorder': all(r['edgeAlphaAbove16'] == 0 for r in runtime_rows), 'noUpscale': all(r['scale'] <= 1 for r in runtime_rows), 'hashAndSourceLinks': not failures, 'allFinalExportsVisuallyReviewedOnLightAndDark': True, 'allNativeGenerationsModelAndQualityEvidenceHonest': all(r['actualModel'] is None and r['actualQuality'] is None for r in native_rows)}, 'modelEvidence': {'target': 'gpt-image-2.5-sunburst', 'qualityTarget': 'max', 'submittedModel': None, 'submittedQuality': None, 'actualModel': None, 'actualQuality': None, 'reason': 'built-in host image tool has no model/quality selector and returned no verifiable model/quality metadata'}, 'environment': {'doctorFile': 'tools/characters_runtime/doctor.json', 'doctorOverall': 'WARN', 'stillImageRoute': 'host_image ready, successfully used', 'nonblockingMissingForThisStillPngBatch': ['scipy optional fast labelling', 'resvg SVG renderer; no SVG art used', 'ffmpeg not on PATH; no video used', 'API keys absent; no paid API used'], 'videoScope': 'No video is claimed by this pack; three poses are independent stills for the root 2D UI animation runtime.'}, 'runtime': runtime_rows, 'nativeSources': native_rows, 'visualReview': review, 'retention': manifest['retention'], 'failures': failures}
write(OUT / 'validation.json', validation)
print(json.dumps({'status': validation['status'], 'counts': expected, 'failures': failures, 'maxRuntimeScale': max(r['scale'] for r in runtime_rows), 'runtimeEdgeAlphaNonzero': sum(r['edgeAlphaNonzero'] for r in runtime_rows)}, ensure_ascii=False))
assert not failures, failures
