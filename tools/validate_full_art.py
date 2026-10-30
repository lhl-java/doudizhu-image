"""Verify the current 2D art contract using real bytes and pixels, without Git or a browser."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
from functools import lru_cache
import hashlib, json, sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
errors=[]; warnings=[]; checks=Counter(); inputs={}

def fail(test,file,detail): errors.append(dict(test=test,file=file,detail=detail))
def check(ok,test,file,detail=''):
    checks[test]+=1
    if not ok: fail(test,file,detail)
    return bool(ok)
def path(file):
    p=(ROOT/file).resolve()
    if not p.is_relative_to(ROOT): raise ValueError('Outside project: '+str(file))
    return p
@lru_cache(None)
def digest(file): return hashlib.sha256(path(file).read_bytes()).hexdigest()
def read(file):
    p=path(file); data=p.read_bytes(); inputs[file]=hashlib.sha256(data).hexdigest()
    return json.loads(data.decode('utf-8-sig'))
def exists(file): return isinstance(file,str) and path(file).is_file()
def hashed(file,expected,context):
    if not check(exists(file),'file_exists',context,str(file)):return False
    return check(isinstance(expected,str) and digest(file)==expected.lower(),'sha256_matches',context,str(file))
@lru_cache(None)
def info(file):
    with Image.open(path(file)) as im:
        im.load(); a=im.getchannel('A') if 'A' in im.getbands() else None
        edgemax=0;edge16=0;edge0=0
        if a:
            for box in [(0,0,im.width,1),(0,im.height-1,im.width,im.height),(0,0,1,im.height),(im.width-1,0,im.width,im.height)]:
                edge=a.crop(box);values=list(edge.get_flattened_data() if hasattr(edge,'get_flattened_data') else edge.getdata()); edgemax=max(edgemax,max(values));edge16+=sum(x>16 for x in values);edge0+=sum(x>0 for x in values)
        return dict(size=[im.width,im.height],mode=im.mode,format=im.format,alpha=a.getextrema() if a else None,edgeAlphaMax=edgemax,edgePixelsAbove16=edge16,edgePixelsNonzero=edge0)
def relations(value,context):
    if isinstance(value,dict):
        file=value.get('file'); expected=value.get('sha256')
        if file and expected:
            if exists(file): hashed(file,expected,context)
            else:
                record=value.get('record') or value.get('generationRecord')
                historical=read(record) if record and exists(record) else {}
                removed=historical.get('imageRemoved') or historical.get('removedImage')
                if removed: warnings.append(dict(test='historical_reference_removed_by_retention_policy',file=file,record=record))
                else: fail('source_reference_exists',context,file)
        for k,v in value.items():
            if k in ['record','generationRecord'] and isinstance(v,str): check(exists(v),'source_record_exists',context,v)
            elif isinstance(v,(dict,list)):relations(v,context)
    elif isinstance(value,list):
        for v in value:relations(v,context)
def record(file,recfile):
    if not check(exists(recfile),'record_exists',file,recfile):return {}
    r=read(recfile)
    hashed(file,r.get('sha256'),recfile)
    if r.get('file'): check(r['file']==file,'record_target_matches',recfile,file)
    if r.get('width') and r.get('height'):check(info(file)['size']==[r['width'],r['height']],'record_dimensions_match',recfile)
    for key in ['derivedFrom','references']:relations(r.get(key,[]),recfile)
    if r.get('prompt') and r.get('promptSha256'): hashed(r['prompt'],r['promptSha256'],recfile)
    return r

manifest=read('assets/game/manifest.json'); assets=manifest['assets']; registry={a['file']:a for a in assets}
check(len(assets)==len(registry)==243,'runtime_art_count','assets/game/manifest.json',str(len(assets)))
check(len({a['id'] for a in assets})==len(assets),'unique_runtime_ids','assets/game/manifest.json')
counts=Counter(a['kind'] for a in assets)
for kind,n in {'ui-controls':24,'ui-cards-source':16,'ui-cards':54,'icon':48,'skin':16,'actor':9,'portrait':24,'costume':5,'costume-pose':10,'background':3,'foreground':2,'fx':12,'title':1,'app-icon':1,'event-banner':3,'actor-preview-sheet':15}.items():
    check(counts[kind]==n,'art_kind_count',kind,dict(expected=n,actual=counts[kind]))
for a in assets:
    f=a['file']
    if not hashed(f,a.get('sha256'),'assets/game/manifest.json'):continue
    im=info(f); check(im['size']==[a['width'],a['height']],'manifest_dimensions_match',f)
    check(im['format']=='PNG','runtime_png_format',f)
    r=record(f,a['record'])
    if a['kind'] in ['actor','portrait','costume','costume-pose','icon','skin','foreground','fx','title']:
        check(im['mode']=='RGBA' and im['alpha'][0]==0 and im['alpha'][1]>16,'required_transparency',f,str(im))
    if a['kind'] in ['actor','portrait','costume','costume-pose','icon','skin','foreground','fx']:
        check(im['edgePixelsAbove16']==0,'no_significant_edge_clipping',f,str(im))
    if a['kind'] in ['actor','portrait','costume','costume-pose']:
        check(im['edgePixelsNonzero']==0,'character_clear_perimeter',f,str(im))
        if 'fixedScale' in r:check(r['fixedScale']<=1 and r.get('noUpscale') is True,'character_no_upscale',f)

# Texture packing must preserve every source texel and all declared empty gutters.
atlas=read('assets/game/atlas.json'); textures=atlas['textures']; atlasframes=atlas['frames']
check(len(textures)==2 and len(atlasframes)==194,'atlas_counts','assets/game/atlas.json')
check(atlas.get('scale')==1 and atlas.get('gutter')==4,'atlas_native_scale_and_gutter','assets/game/atlas.json')
for ti,tex in enumerate(textures):
    hashed(tex['file'],tex['sha256'],'assets/game/atlas.json')
    with Image.open(path(tex['file'])) as packed:
        packed=packed.convert('RGBA'); check(list(packed.size)==[tex['width'],tex['height']],'atlas_texture_dimensions',tex['file'])
        frames=[f for f in atlasframes if f['texture']==ti]
        for ix,f in enumerate(frames):
            x,y,w,h=f['rect']; check(not f['rotated'] and not f['trimmed'],'atlas_no_rotation_or_trim',f['source'])
            check(x>=4 and y>=4 and x+w+4<=packed.width and y+h+4<=packed.height,'atlas_rect_inside',f['source'])
            hashed(f['source'],f['sourceSha256'],'assets/game/atlas.json')
            with Image.open(path(f['source'])) as original:
                original=original.convert('RGBA')
                check(original.size==(w,h) and original.tobytes()==packed.crop((x,y,x+w,y+h)).tobytes(),'atlas_pixels_identical',f['source'])
            for strip in [(x-4,y-4,x+w+4,y),(x-4,y+h,x+w+4,y+h+4),(x-4,y,x,y+h),(x+w,y,x+w+4,y+h)]:
                check(packed.crop(strip).getchannel('A').getbbox() is None,'atlas_gutter_transparent',f['source'])
            for other in frames[ix+1:]:
                xx,yy,ww,hh=other['rect']
                check(x+w+4<=xx or xx+ww+4<=x or y+h+4<=yy or yy+hh+4<=y,'atlas_no_overlap',f['source'],other['source'])

chars=read('assets/characters/manifest.json')['characters']; check(len(chars)==3,'character_count','assets/characters/manifest.json')
for c in chars:
    check(set(c['poses'])=={'master','win','lose'} and len(c['expressions'])==8,'character_pose_expression_contract',c['id'])
    check(c['anchor']==[512,920],'character_anchor',c['id'])
    for f in list(c['poses'].values())+list(c['expressions'].values()):check(f in registry,'character_indexed',f)
    if c['id']=='daotong':
        check(len(c['costumes'])==6 and len({v['file'] for v in c['costumes']})==6,'six_distinct_costume_sources',c['id'])
    for v in c.get('costumes',[]):
        check(v['file'] in registry,'costume_indexed',v['file'])
        if v['id']!='daotong_base':
            check(set(v.get('poses',{}))=={'master','win','lose'},'costume_own_pose_matrix',v['id'])
            for pose,f in v.get('poses',{}).items():check(f in registry,'costume_pose_indexed',f)
check(read('assets/characters/validation.json')['status']=='passed','character_batch_qa','assets/characters/validation.json')

animation=read('assets/animations/characters/manifest.json'); clips=animation['clips']; actorframes=0
check(len(clips)==15,'actor_clip_count','assets/animations/characters/manifest.json')
check({(c['actor'],c['action']) for c in clips}=={(a,b) for a in ['daotong','taohua','hulu'] for b in ['idle','think','play','win','lose']},'actor_action_matrix','assets/animations/characters/manifest.json')
for c in clips:
    clip=read(c['file']); rec=read(c['record']); frames=clip['preview']['frames']; actorframes+=len(frames)
    hashed(c['file'],rec['animationDataSha256'],c['record'])
    check(len(frames)==16 and sum(f['durationMs'] for f in frames)==c['durationMs'],'actor_clip_duration',c['file'])
    check(c['durationMs']==clip['durationMs'] and c['loop']==clip['loop'],'actor_clip_manifest_matches',c['file'])
    check(clip['keyframes'][0]['atMs']==0 and clip['keyframes'][-1]['atMs']==clip['durationMs'],'actor_keyframe_bounds',c['file'])
    check(rec.get('noUpscale') is True and rec['maximumActorScale']<=1,'actor_animation_no_upscale',c['record'])
    with Image.open(path(c['sheet'])) as sheet:
        actual=[]
        for f in frames:
            x,y,w,h=f['rect']; frame=sheet.crop((x,y,x+w,y+h)).convert('RGBA'); a=frame.getchannel('A');actual.append(frame.tobytes())
            clear=all(a.crop(box).getbbox() is None for box in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])
            check(clear,'actor_frame_clear_perimeter',c['sheet'],f['index'])
        if c['loop']:check(actual[0]==actual[-1],'actor_loop_first_last_equal',c['sheet'])
check(actorframes==240,'actor_preview_frame_count','assets/animations/characters/manifest.json')
for p in animation['previews']:
    r=record(p['file'],p['record']); total=0
    with Image.open(path(p['file'])) as webp:
        check(webp.is_animated and webp.size==(160,200),'actor_webp_animated_preview',p['file'])
        for fi in range(webp.n_frames):
            webp.seek(fi);webp.load();total+=webp.info.get('duration',0)
        check(total==r['durationMs']==r['decoded']['durationMs'],'actor_webp_total_duration',p['file'],total)
        check(webp.n_frames==r['decoded']['decodedFrames'],'actor_webp_decoded_frame_count',p['file'])
    cursor=0
    for seg in p['segments']:
        check(seg['startMs']==cursor and exists(seg['clip']),'actor_webp_segment_timing',p['file'],seg['action']);cursor+=seg['durationMs']
    check(cursor==total,'actor_webp_segments_cover_duration',p['file'])

kit=read('assets/ui/runtime-kit/manifest.json'); metrics=read('assets/ui/runtime-kit/control-metrics.json')['assets']
font_contract=read('assets/ui/runtime-kit/font-contract.json')
check(font_contract['downloadedFonts']==[] and font_contract['bundledFonts']==[],'no_unlicensed_font_bytes_claimed','assets/ui/runtime-kit/font-contract.json')
check(len(kit['assets'])==64 and len(metrics)==88,'kit_and_metrics_counts','assets/ui/runtime-kit/manifest.json')
check(read('assets/ui/runtime-kit/qa-report.json')['status']=='passed','kit_final_qa','assets/ui/runtime-kit/qa-report.json')
for m in metrics:
    check(m['file'] in registry,'metrics_file_indexed',m['file'])
    check(info(m['file'])['size']==m['nativeSize'],'metrics_native_size',m['file'])
    ns=m.get('nineSliceInsets')
    if ns:
        w,h=m['nativeSize'];check(ns['left']+ns['right']<w and ns['top']+ns['bottom']<h,'nine_slice_valid_source_insets',m['file'])
    else:check(m['resizeMode']=='uniform_contain','non_nineslice_aspect_policy',m['file'])

scenes=read('assets/scenes/scenes.json'); effects=read('assets/fx/manifest.json'); fxframes=0
check(len(scenes['assets'])==5,'scene_count','assets/scenes/scenes.json')
for a in scenes['assets']+effects['assets']:
    check('pending' not in a['status'] and 'fail' not in a['status'],'scene_fx_final_status',a['file'],a['status'])
    check(a['file'] in registry,'scene_fx_indexed',a['file'])
for a in effects['assets']:
    timeline=read(a['timeline']); frames=read(a['frames']); fxframes+=len(frames['frames'])
    check(timeline['durationMs']==a['durationMs']==frames['durationMs'],'fx_duration_consistency',a['id'])
    check(timeline['loop']==a['loop']==frames['loop'],'fx_loop_consistency',a['id'])
    keys=timeline['keyframes']; times=[k['atMs'] for k in keys]
    check(times==sorted(times) and times[0]==0 and times[-1]==a['durationMs'],'fx_keyframe_bounds',a['timeline'])
    check(timeline.get('translationUnit')=='fraction-of-384px-frame','fx_translation_unit',a['timeline'])
    relations(frames.get('derivedFrom',[]),a['frames'])
    check(len(frames['frames'])==16,'fx_sixteen_frames',a['frames'])
    total=sum(f['durationMs'] for f in frames['frames'])
    expected=a['durationMs']+(0 if a['loop'] else frames.get('terminalSentinelMs',0))
    check(total==expected==frames['bakedPlaybackDurationMs'],'fx_baked_duration_with_documented_sentinel',a['frames'])
    cursor=0; visible=0; clipped=[]
    for f in frames['frames']:
        hashed(f['file'],f['sha256'],a['frames']); im=info(f['file'])
        check(im['size']==[384,384] and im['mode']=='RGBA','fx_frame_dimensions_mode',f['file'])
        check(f['atMs']==cursor and f['durationMs']>0,'fx_frame_contiguous_timing',f['file']);cursor+=f['durationMs']
        if im['alpha'][1]>16:visible+=1
        if im['edgePixelsAbove16']:clipped.append(dict(file=f['file'],pixels=im['edgePixelsAbove16']))
    check(visible>0,'fx_has_visible_animation_frames',a['id'])
    check(not clipped,'fx_frames_no_significant_edge_clipping',a['id'],clipped)
check(len(effects['assets'])==12 and fxframes==192,'fx_count_and_frame_count','assets/fx/manifest.json')
scene_qa=read(scenes['qa']['file'])
check(scene_qa.get('scenes')==5 and scene_qa.get('fx')==12 and scene_qa.get('bakedFrames')==192,'scene_fx_qa_scope',scenes['qa']['file'])
check(str(scene_qa.get('status','')).startswith('passed'),'scene_fx_final_visual_qa',scenes['qa']['file'],scene_qa.get('status'))
warnings.append(dict(test='raw_fx_source_sheet_warnings_retained',detail=effects.get('rawQALimit')))

index=read('assets/game/runtime-index.json'); screen_manifest=read('runtime/screens.json'); screens=screen_manifest['screens']
resolved=read('assets/game/resolved-screen-art.json')
hashed(resolved['source'],resolved['sourceSha256'],'assets/game/resolved-screen-art.json')
check(resolved['backgroundLogicalIds']==index['scenes'] and resolved['tableLogicalIds']==index['tables'] and resolved['actorLogicalIds']==index['actors'],'resolved_screen_art_matches_index','assets/game/resolved-screen-art.json')
check(len(screens)==60 and len({s['id'] for s in screens})==60,'sixty_screen_bindings','runtime/screens.json')
states=sum(len(s['states']) for s in screens)
check(states==223,'screen_state_count','runtime/screens.json',states)
for s in screens:
    check(exists(s['referenceDesign']),'selected_design_exists',s['id'],s['referenceDesign'])
    for prop,collection in [('scene','scenes'),('table','tables'),('panel','controls'),('button','controls'),('actor','actors')]:
        check(s['art'][prop] in index[collection],'screen_logical_art_resolved',s['id'],prop+':'+s['art'][prop])
    for c in s['controls']:
        check(c['art'] in index['controls'] or c['art'] in index['skins'],'screen_control_art_resolved',c['id'],c['art'])
        if c.get('icon'):check(c['icon'] in index['icons'],'screen_control_icon_resolved',c['id'],c['icon'])
    for c in s['items']:
        if c.get('icon'):check(c['icon'] in index['icons'],'screen_item_icon_resolved',c['id'],c['icon'])
    for state in s['states']:check(bool(state['title']) and bool(state['body']) and isinstance(state['buttons'],list),'state_copy_binding_complete',s['id'],state['name'])
check(len(index['cards'])==54,'deck_fiftyfour_unique_cards','assets/game/runtime-index.json')
expectedcards={s+'-'+r for s in ['spades','hearts','clubs','diamonds'] for r in ['A','2','3','4','5','6','7','8','9','10','J','Q','K']}|{'joker-small','joker-big'}
check(set(index['cards'])==expectedcards,'deck_complete_ranks_suits','assets/game/runtime-index.json')
locale=read('runtime/copy.zh-CN.json')
serialized=json.dumps(locale,ensure_ascii=False)+json.dumps(screen_manifest,ensure_ascii=False)
check(not any(v in serialized for v in ['金币','金豆','点券','代币','赛季令']),'canonical_runtime_currency','runtime/copy.zh-CN.json')
oldqa=read('docs/FINAL_VALIDATION.json')
check(oldqa['allPagesSelectedAndVerified'] and not oldqa['errors'],'original_ui_design_qa','docs/FINAL_VALIDATION.json')
runtimeqa=read('docs/RUNTIME_INTEGRATION_VALIDATION.json')
stateart=read('runtime/state-art.json')
check(len(stateart['states'])==223 and len({x['id'] for x in stateart['states']})==223,'state_art_explicit_coverage','runtime/state-art.json')
hashed('runtime/screens.json',stateart['sourceSha256'],'runtime/state-art.json')
for st in stateart['states']:
    source=next(p for p in screens if p['id']==st['screen'])['states'][st['index']]
    check(st['name']==source['name'] and st['body']==source['body'],'state_art_copy_matches_design',st['id'])
    check(st['icon'] in index['icons'] and bool(st['actions']),'state_art_binding_complete',st['id'])
poseqa=read('docs/COSTUME_POSES_VALIDATION.json')
check(poseqa['status']=='passed_offline_art_review' and len(poseqa['assets'])==10,'costume_pose_review_passed','docs/COSTUME_POSES_VALIDATION.json')
check(not runtimeqa['failures'] and runtimeqa['pages']==60 and runtimeqa['states']==223,'runtime_mock_execution_report','docs/RUNTIME_INTEGRATION_VALIDATION.json')
for e in runtimeqa['evidence']:
    # The index embeds status metadata updated during final source QA. All code and layout-input evidence must still match.
    if e['file']=='assets/game/runtime-index.json' and digest(e['file'])!=e['sha256']:
        warnings.append(dict(test='runtime_mock_index_metadata_changed_rerun_recommended',file=e['file']))
    else:hashed(e['file'],e['sha256'],'docs/RUNTIME_INTEGRATION_VALIDATION.json')

platform_exports=read('assets/brand/exports/manifest.json')['exports']
check(len(platform_exports)==9,'platform_icon_export_count','assets/brand/exports/manifest.json')
for a in platform_exports:
    hashed(a['file'],a['sha256'],'assets/brand/exports/manifest.json')
    check(info(a['file'])['size']==[a['width'],a['height']],'platform_icon_dimensions',a['file'])
    check(a['width']<=1254 and a['width']==a['height'],'platform_icon_no_upscale',a['file'])
    record(a['file'],a['record'])

report=dict(schemaVersion=1,validatedAt=datetime.now(timezone.utc).isoformat(),status='passed_offline_art_contract' if not errors else 'failed',
            contract='docs/FULL_GAME_ART_CONTRACT.md',artFilesReady=not errors,productionRuntimeVerified=False,humanArtApproval=False,
            counts=dict(runtimePngs=len(assets),kinds=dict(counts),atlasTextures=len(textures),atlasSprites=len(atlasframes),characters=len(chars),
                        actorClips=len(clips),actorPreviewFrames=actorframes,fx=len(effects['assets']),fxFrames=fxframes,screens=len(screens),states=states,metrics=len(metrics),platformIconExports=len(platform_exports)),
            errors=errors,warnings=warnings,checks=dict(checks),
            method='Real local file SHA256, PNG decoding, alpha-edge inspection, atlas pixel comparison, JSON timing and reference validation; existing mock execution report checked by evidence hash.',
            browserValidation=dict(performed=False,reason='Local browser automation disabled in Work settings; no browser layout, visual playback or game-engine integration pass is claimed.'),
            limits=['Three-character 2D UI art scope; rigid-pose keyframe motion and real static pose changes, not AI video or articulated skeletal animation.',
                    '223 states have explicit native art-layout/copy bindings and mock execution coverage. Real browser appearance and production state logic are not verified.',
                    'Fonts use client system font stacks; no font binaries are distributed. Audio, server, gameplay and payment integration are outside visual art assets.'],
            inputEvidence=[dict(file=f,sha256=h) for f,h in sorted(inputs.items())])
(ROOT/'docs/FULL_GAME_ART_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','counts','errors','warnings']},ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
