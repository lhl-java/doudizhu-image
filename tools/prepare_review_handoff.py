"""Record this candidate and existing evidence by file operations only; never launch a GUI."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'preview/review-20261111/evidence'
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(file):
    p=ROOT/file
    return {'file':file,'bytes':p.stat().st_size,'sha256':sha(p)}
copies={'.work/browser-art-audit/report.json':'browser-baseline.json','.work/browser-layout-regression/report.json':'layout-regression.json','.work/browser-visual-review/static-final.json':'state-binding-checks.json','.work/browser-visual-review/user-review-checklist.json':'state-review-checklist.json','.work/browser-visual-review/review.json':'agent-observations.json'}
historical=[]
for src,name in copies.items():
    p=ROOT/src
    if p.is_file():
        shutil.copyfile(p,OUT/name)
        historical.append(record((OUT/name).relative_to(ROOT).as_posix()))
source_files=['runtime/art-preview.js','runtime/art-preview.html','runtime/art-preview.css','runtime/state-art.mjs','runtime/state-art.css','runtime/state-art.json','runtime/screens.json','runtime/table-art.mjs','assets/game/manifest.json','assets/game/runtime-index.json','assets/animations/characters/player.mjs','tools/build_state_art.py','tools/build_review_portal.py','tools/prepare_review_handoff.py','preview/review-20261111/index.html','preview/review-20261111/batches.json','docs/RUNTIME_INTEGRATION_VALIDATION.json']
baseline=json.loads((ROOT/'.work/browser-art-audit/report.json').read_text(encoding='utf-8'))
motion='preview/review-20261111/motion/manifest.json'
for file in [motion,'preview/review-20261111/motion/export-validation.json']:
    if (ROOT/file).is_file():historical.append(record(file))
doc={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'userFacingDate':'2026-11-11','status':'candidate_pending_user_review','repository':'https://github.com/lhl-java/doudizhu-image','baseCommit':'033ddaaca9b6331d8fa67c88f5eda43674262ca9','entry':'preview/review-20261111/index.html','runtimeEntry':'runtime/art-preview.html','correctsHistoricalEntry':'docs/LOCAL_SOURCE_HANDOFF_20261108.json listed runtime/index.html, which does not exist; that historical record is retained unchanged.','userArtApproval':False,'productionRuntimeVerified':False,'wholeGameArtCompletion':False,'browserValidation':{'performed':True,'scope':'Historical desktop-Chrome captures and playback only; final candidate display requires user review.','baselineConditions':baseline['summary']['captureCount'],'baselineSourceChanged':baseline['summary']['sourceChanged'],'currentRevisionVisualApproved':False,'finalFullBrowserRerunPerformed':False,'reason':'User explicitly requested no computer use and to prepare batches for their review. All browser/desktop automation stopped; no replacement GUI automation used.'},'currentConstraints':{'noComputerUse':True,'noCuaSkyOrAlternativeGuiAutomation':True,'fileDataHashChecksAllowed':True,'humanVisualReviewByUser':True,'normalCommitsAndPushOnly':True},'referenceClient':{'userProvidedName':'QQ斗地主','platform':None,'version':None,'build':None,'trustedSource':None,'locked':False,'historicalResearch':'docs/REFERENCE_RESEARCH.md','boundary':'Historical 欢乐斗地主 webpage version is not a locked QQ斗地主 source client. Do not run untrusted installers.'},'scope':{'screens':60,'states':223,'actors':3,'baseActorActions':15,'costumesIncludingBase':6,'costumeActionCases':30,'fx':12,'newAiImagesThisBatch':0,'originalAdoptedArtBytesChanged':False},'changes':['Constrain panels, nested grid tracks, character cards, keypad and scrollable lists at both supported landscape ratios.','Cancel and invalidate in-flight FX on page change or newer playback.','Bind named actor/costume examples, negative result pose, incomplete progress, component states, card samples, chat/voice and vote visuals to existing assets.','Provide user-operated exact screen/state/aspect links and versioned motion recordings.'],'checks':{'currentStaticAndMockReport':'docs/RUNTIME_INTEGRATION_VALIDATION.json','historicalBrowserEvidenceIsNotFinalCandidateAcceptance':True,'stateOriginalCopyPreserved':True},'remaining':['User review of current 60 screens/223 states at both landscape ratios, 3 actors/6 costumes and 12 FX.','Lock QQ斗地主 platform, exact version/build and trusted source.','Target-client engine import, real fonts, alpha/anchors, performance and final user art approval.'],'candidateSourceEvidence':[record(f) for f in source_files],'historicalEvidence':historical,'preservedHistoricalOfflinePass':'docs/FULL_GAME_ART_VALIDATION.json remains an offline file/alpha/atlas/reference contract, not final game-client acceptance.'}
(ROOT/'docs/BROWSER_REVIEW_HANDOFF_20261111.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':doc['status'],'entry':doc['entry'],'candidateInputs':len(source_files),'historicalEvidence':len(historical)},ensure_ascii=False))
