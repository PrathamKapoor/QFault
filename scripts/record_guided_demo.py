"""Record the real guide silently, then verify full normal-speed browser playback."""
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import subprocess
from time import perf_counter
from urllib.parse import urlsplit

from playwright.sync_api import expect,sync_playwright
from qfault.evidence import canonical
from qfault.storage import verify_export

ROOT=Path(__file__).resolve().parents[1]


def stamp(seconds):
    if not math.isfinite(seconds) or seconds<0:raise ValueError('Caption time must be finite and nonnegative')
    total=round(seconds*1000);hours,total=divmod(total,3600000);minutes,total=divmod(total,60000);secs,millis=divmod(total,1000)
    return f'{hours:02}:{minutes:02}:{secs:02}.{millis:03}'


def captions(milestones,duration):
    stamp(duration)
    if not milestones:raise ValueError('No recorded milestones')
    values=[float(m['seconds']) for m in milestones]
    if any(not math.isfinite(v) or v<0 or v>=duration for v in values) or any(a>=b for a,b in zip(values,values[1:])):
        raise ValueError('Caption intervals must be ordered within actual recording duration')
    lines=['WEBVTT','']
    for i,m in enumerate(milestones):
        end=values[i+1] if i+1<len(values) else duration
        lines += [str(i+1),f'{stamp(values[i])} --> {stamp(end)}',m['text'],'']
    return '\n'.join(lines)


def git(*args):
    return subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),*args],cwd=ROOT,text=True).strip()


def record(base,out):
    parsed=urlsplit(base)
    if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost') or parsed.username:
        raise ValueError('Recording requires the real local loopback service')
    if git('status','--porcelain'):raise ValueError('Commit reviewed source before recording a release-bound demonstration')
    revision=git('rev-parse','HEAD');out=Path(out).resolve()
    if not out.is_relative_to((ROOT/'artifacts').resolve()):raise ValueError('Record inside a new artifacts directory')
    out.mkdir(parents=True,exist_ok=False)
    milestones=[];rows=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce',
            record_video_dir=str(out/'raw-video'),record_video_size={'width':1440,'height':1000},accept_downloads=True)
        start=perf_counter();page=context.new_page();video=page.video;errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        def mark(text):
            seconds=perf_counter()-start;milestones.append({'seconds':seconds,'text':text})
            print(json.dumps({'stage':text,'elapsed_seconds':round(seconds,2)}),flush=True)
        def until(seconds):
            while (remaining:=seconds-(perf_counter()-start))>0:page.wait_for_timeout(min(remaining,20)*1000)
        def show(locator,name):
            locator.evaluate("e=>e.scrollIntoView({block:'start'})");page.wait_for_timeout(350)
            page.screenshot(path=str(out/(name+'.png')))
        def keep(key):
            state=page.evaluate("JSON.parse(sessionStorage.getItem('qfault-guided-demo-v1'))")
            eid=state['ids'][key]
            response=context.request.get(f'{base}/api/experiments/{eid}/report');assert response.ok
            report=response.json();assert verify_export(report)['valid']
            record=report['investigation'];assert record['experiment_id']==eid
            (out/(key+'-report.json')).write_bytes(canonical(report))
            rows.append({'stage':key,'experiment_id':eid,'status':record.get('status',record['diagnosis']['category']),
                'cost':record['cost'],'report_sha256':hashlib.sha256(canonical(report)).hexdigest()})
            return record
        page.goto(base);page.get_by_role('button',name='Guided demo',exact=True).first.click()
        expect(page.get_by_role('button',name='Start with Z measurements')).to_be_visible()
        mark('An imported external reference and a separate controlled candidate. No measurements have run yet.')
        show(page.locator('.guided-content'),'source');until(20)
        page.get_by_role('button',name='Start with Z measurements').click()
        page.get_by_role('button',name='Run Z-only measurement').click()
        z=page.get_by_test_id('outcome-z');expect(z).to_be_visible(timeout=120000)
        assert keep('z')['diagnosis']['category']=='NO_SIGNIFICANT_DISCREPANCY'
        mark('Real Z-only agreement supports this distribution only; it cannot see the relative phase.')
        show(z,'z-only');until(40)
        page.get_by_role('button',name='Add complementary evidence').click()
        page.get_by_role('button',name='Run complementary measurement').click()
        phase=page.get_by_test_id('outcome-phase');expect(phase).to_be_visible(timeout=120000)
        assert keep('phase')['diagnosis']['category']=='SIGNIFICANT_DISCREPANCY'
        mark('Independent complementary claims detect a discrepancy with finite-shot uncertainty and actual cost.')
        show(phase,'phase');until(60)
        page.get_by_role('button',name='Inspect bounded edits').click()
        mark('Bounded structural edit previews are not measured repairs. Untested edits and overlapping evidence remain possible.')
        show(page.get_by_test_id('candidate-preview'),'edits');until(80)
        page.get_by_role('button',name='Use these limits for fresh verification').click()
        page.get_by_role('button',name='Screen edits and freshly verify').click()
        result=page.get_by_test_id('outcome-recovery');expect(result).to_be_visible(timeout=180000)
        recovery=keep('recovery');assert recovery['status']=='VERIFIED_UNDER_DECLARED_CONTRACT'
        assert recovery['selection']['frozen_before_verification']
        original_ids={e['execution_id'] for e in recovery['executions'] if e['recovery_phase']=='verification_original'}
        candidate_ids={e['execution_id'] for e in recovery['executions'] if e['recovery_phase']=='verification_candidate'}
        assert original_ids and candidate_ids and not original_ids&candidate_ids
        mark('Selection is frozen before fresh original and candidate measurements. The verified conclusion covers only the declared contract and input.')
        show(result,'verified');until(96)
        show(page.get_by_role('heading',name='Fresh original and candidate measurements'),'fresh-pair');until(104)
        show(page.locator('.guided-ledger'),'fresh-cost');until(110)
        page.get_by_role('button',name='Inspect and export evidence').click()
        page.get_by_role('button',name='Check stored report integrity').click()
        expect(page.get_by_test_id('integrity-result')).to_contain_text('Stored hashes verified')
        with page.expect_download() as downloaded:page.get_by_role('link',name='Download recovery report').click()
        downloaded.value.save_as(out/'downloaded-recovery-report.json')
        assert verify_export(json.loads((out/'downloaded-recovery-report.json').read_bytes()))['valid']
        mark('Download the real report. Hash checks establish consistency, not authenticity or scientific truth.')
        show(page.get_by_test_id('integrity-result'),'export');until(122)
        page.get_by_role('button',name='Replay with the same seed').click()
        expect(page.get_by_test_id('replay-result')).to_be_visible(timeout=180000)
        mark('Same-seed replay creates a new parent-linked record. A new seed is a rerun under shared simulator assumptions.')
        show(page.get_by_test_id('replay-result'),'replay');until(135)
        page.get_by_role('button',name='Noise-control abstention',exact=True).click()
        page.get_by_role('button',name='Run noise-control abstention',exact=True).click()
        noise=page.get_by_test_id('outcome-noise');expect(noise).to_be_visible(timeout=120000)
        assert keep('noise')['status']=='NOISE_CONTROL_ABSTENTION'
        mark('The readout control disagrees significantly. Withholding an edit avoids presenting noise evidence as repair.')
        show(noise,'noise');until(160)
        page.get_by_role('button',name='Insufficient budget',exact=True).click()
        page.get_by_role('button',name='Run insufficient budget',exact=True).click()
        budget=page.get_by_test_id('outcome-budget');expect(budget).to_be_visible(timeout=120000)
        refused=keep('budget');assert refused['status']=='INSUFFICIENT_BUDGET' and refused['cost']['shots']==0 and refused['executions']==[]
        mark('The reserve cannot be funded: zero shots executed. Local simulation, one input, bounded edits and explicit uncertainty.')
        show(budget,'budget');until(180)
        assert not errors,errors
        context.close();recorded=Path(video.path()).resolve()
        if not recorded.is_relative_to(out):raise ValueError('Unexpected recording destination')
        recorded.rename(out/'guided-demo-silent.webm');browser.close()
    metadata={'schema_version':1,'source_commit':revision,'media':'guided-demo-silent.webm','narration':'SILENT: no voiceover recorded',
        'viewport':{'width':1440,'height':1000},'milestones':milestones,'rows':rows,'page_errors':errors,
        'sha256':hashlib.sha256((out/'guided-demo-silent.webm').read_bytes()).hexdigest(),
        'input_sha256':hashlib.sha256((ROOT/'examples/qrng-phase-demo.json').read_bytes()).hexdigest(),
        'scope':'Actual browser/API/Aer execution, not mocked outcomes or a frozen performance evaluation. Approximate three-minute presentation pacing.'}
    (out/'recording.json').write_text(json.dumps(metadata,indent=2));return metadata


def playback(folder):
    folder=Path(folder).resolve();metadata=json.loads((folder/'recording.json').read_bytes());path=folder/metadata['media']
    if path.stat().st_size>128*1024*1024 or hashlib.sha256(path.read_bytes()).hexdigest()!=metadata['sha256']:
        raise ValueError('Recording size/digest mismatch')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1440,'height':1050})
        page.set_content('<body style="margin:0;background:#17131f"><video id="clip" controls muted preload="auto" style="width:1440px;height:1000px"></video></body>')
        # Decode the exact local bytes as a seekable Blob. A fulfilled HTTP route
        # without range responses exposes duration but a zero-length seekable range.
        page.evaluate('(encoded)=>{const bytes=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0));document.querySelector("video").src=URL.createObjectURL(new Blob([bytes],{type:"video/webm"}))}',base64.b64encode(path.read_bytes()).decode('ascii'))
        page.wait_for_function('Number.isFinite(document.querySelector("video").duration)',timeout=30000)
        duration=page.evaluate('document.querySelector("video").duration')
        assert duration>=170,'Recording is shorter than the advertised presentation'
        for label,target in [('source',10),('phase',50),('fresh',100),('noise',150),('budget',min(duration-1,175))]:
            page.evaluate('(t)=>{const v=document.querySelector("video");v.pause();v.currentTime=t}',target)
            page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&Math.abs(v.currentTime-t)<.2}',arg=target)
            page.wait_for_timeout(250);page.screenshot(path=str(folder/('decoded-'+label+'.png')))
        page.evaluate('async()=>{const v=document.querySelector("video");v.currentTime=0;v.playbackRate=1;await v.play()}')
        page.wait_for_timeout(300)
        audio_tracks=page.evaluate('document.querySelector("video").captureStream().getAudioTracks().length')
        page.wait_for_function('document.querySelector("video").ended',timeout=int((duration+45)*1000))
        quality=page.evaluate('()=>{const v=document.querySelector("video"),q=v.getVideoPlaybackQuality();return {duration:v.duration,ended:v.ended,error:v.error?.message??null,total_frames:q.totalVideoFrames,dropped_frames:q.droppedVideoFrames,corrupted_frames:q.corruptedVideoFrames,audio_tracks:v.captureStream().getAudioTracks().length}}')
        quality['audio_tracks']=audio_tracks
        assert quality['ended'] and quality['error'] is None and quality['total_frames']>0 and quality['corrupted_frames']==0
        assert quality['audio_tracks']==0
        browser.close()
    (folder/'guided-demo-captions.vtt').write_text(captions(metadata['milestones'],duration),encoding='utf8')
    (folder/'playback-verification.json').write_text(json.dumps({'valid':True,'source_commit':metadata['source_commit'],
        'sha256':metadata['sha256'],'playback_speed':1,'narration':'silent','quality':quality},indent=2))
    print(json.dumps({'playback_valid':True,'duration_seconds':duration,'quality':quality}),flush=True)
    return quality


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base',default='http://127.0.0.1:8000')
    parser.add_argument('--out',type=Path);parser.add_argument('--playback',type=Path);args=parser.parse_args()
    if args.playback:playback(args.playback)
    elif args.out:record(args.base.rstrip('/'),args.out);playback(args.out)
    else:parser.error('--out or --playback is required')


if __name__=='__main__':main()
