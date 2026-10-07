import argparse
import datetime
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import uuid

if not __debug__:
    raise SystemExit('ASSERTIONS_DISABLED')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
import controls
from validate import PARAMS, PIN, require, sha, tau, validate

def main():
    ap=argparse.ArgumentParser(description='完整独立复验 / Complete independent replay')
    ap.add_argument('--runtime',type=Path,required=True,help='已准备依赖的运行目录 / Runtime with prepared dependencies')
    ap.add_argument('--workers',type=int,default=4,help='并行进程数 / Worker count')
    args=ap.parse_args()
    require(platform.system()=='Linux','LINUX_REQUIRED')
    require(1<=args.workers<=16,'WORKER_RANGE')
    require(not os.environ.get('PYTHONOPTIMIZE'),'ASSERTIONS_DISABLED')
    require(not os.environ.get('RUSTFLAGS') and not os.environ.get('CARGO_ENCODED_RUSTFLAGS'),'UNREVIEWED_RUST_FLAGS')
    runtime=args.runtime.resolve()
    out=runtime/'replay'
    out.mkdir(parents=True,exist_ok=False)
    require(not (runtime/'target').exists(),'FRESH_BUILD_REQUIRED')
    source=ROOT/'verifier/sqverify_fast'
    candidate=ROOT/'certificate/certified_candidate.json'
    require(sha(candidate)==PIN,'INPUT_IDENTITY')
    public_code=[p for folder in ('verifier','tests','certificate') for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    code_before={p.relative_to(ROOT).as_posix():sha(p) for p in public_code}
    run_id=uuid.uuid4().hex
    record={'status':'RUNNING','run_id':run_id,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'code_and_input_sha256':code_before,'commands':[]}
    def save():
        (out/'receipt.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    env=os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1',CARGO_HOME=str(runtime/'cargo'),CARGO_TARGET_DIR=str(runtime/'target'),CARGO_NET_OFFLINE='true')
    for key in ('CARGO_BUILD_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER'):
        require(not env.get(key),'UNREVIEWED_COMPILER_WRAPPER')
    def execute(name,command,cwd=ROOT):
        start=time.monotonic()
        print(name,flush=True)
        with (out/(name+'.stdout')).open('wb') as stdout,(out/(name+'.stderr')).open('wb') as stderr:
            result=subprocess.run(command,cwd=cwd,env=env,stdout=stdout,stderr=stderr)
        record['commands'].append({'stage':name,'exit_code':result.returncode,'seconds':time.monotonic()-start,'stdout_sha256':sha(out/(name+'.stdout')),'stderr_sha256':sha(out/(name+'.stderr'))})
        save()
        require(result.returncode==0,'STAGE_FAILED:'+name)
    save()
    vendor=runtime/'vendor'
    require(vendor.is_dir(),'RUN_PREPARE_FIRST')
    config=['--config','source.crates-io.replace-with="vendored-sources"','--config','source.vendored-sources.directory='+json.dumps(str(vendor))]
    execute('rust-tests',['cargo','test','--profile','gate-test','--locked','--offline',*config],source)
    execute('rust-build',['cargo','build','--release','--locked','--offline',*config],source)
    binary=runtime/'target/release/sqverify-fast'
    nodes={'status':'RUNNING','run_id':run_id,'candidate_sha256':PIN,'rows':[],'binary_sha256':sha(binary)}
    groups=[(0,0,'2503/2500'),(1,3,'10009/10000'),(4,33,'1251/1250'),(34,42,'2001/2000'),(43,200,'10001/10000')]
    for first,last,threshold in groups:
        name='nodes-%03d-%03d'%(first,last)
        folder=out/name
        execute(name,[str(binary),'--candidate',str(candidate),'--n','40','--side','67/10','--directions',str(first)+'-'+str(last),'--threshold',threshold,'--threads',str(args.workers),'--receipts',str(folder),'--confirm'])
        lines=[json.loads(line) for line in (out/(name+'.stdout')).read_text().splitlines()]
        summaries=[v for v in lines if v.get('kind')=='sqverify-fast-summary/v1']
        rows=[v for v in lines if 'r' in v]
        require(len(summaries)==1 and sorted(v['r'] for v in rows)==list(range(first,last+1)),'GROUP_COVERAGE')
        summary=summaries[0]
        require(summary['status']=='PARTIAL' and summary['refused_directions']==[] and summary['fault_injected_at_box'] is None,'GROUP_STATUS')
        premise=summary['premises']
        require(premise['n']==40 and premise['angle_count']==201 and premise['centre_domain']=='tokoharu' and premise['input_sha256']==PIN,'GROUP_PREMISES')
        for key,expected in [('L','67/10'),('B','9977/10000'),('D','83/40000'),('mass_exact','3999/100')]:
            require(Q(premise[key])==Q(expected),'GROUP_PARAMETER')
        require(Q(summary['threshold'])==Q(threshold),'GROUP_THRESHOLD')
        for row in rows:
            raw=json.loads((folder/('r%03d.json'%row['r'])).read_text())
            require(raw['certificate_sha256']==PIN and {k:v for k,v in raw.items() if k!='certificate_sha256'}==row,'RAW_NODE_IDENTITY')
            require(row['verdict']=='verified' and Q(row['threshold'])==tau(row['r']),'RAW_NODE_THRESHOLD')
            lower=Q.from_float(row['min_certified_lower_bound'])
            require(lower>=tau(row['r']),'LOWER_BOUND')
            nodes['rows'].append({'r':row['r'],'threshold':row['threshold'],'lower_exact':str(lower),'verdict':row['verdict'],'complete_continuous_domain':True,'method':row['method']})
    nodes['rows'].sort(key=lambda x:x['r'])
    nodes['status']='COMPLETE_CONTINUOUS_NODES'
    (out/'nodes.json').write_text(json.dumps(nodes,indent=2),encoding='utf-8')
    execute('caps',[sys.executable,'-B',str(ROOT/'verifier/caps.py'),'--workers',str(args.workers),'--out',str(out/'caps')])
    cap_summary=json.loads((out/'caps/summary.json').read_text())
    cap_summary['run_id']=run_id
    cap_rows=[json.loads(p.read_text()) for p in sorted((out/'caps').glob('r[0-9][0-9][0-9].json'))]
    parameters=json.loads((ROOT/'certificate/parameters.json').read_text())
    result=validate(nodes,cap_summary,cap_rows,parameters,run_id)
    negative=controls.run(nodes,cap_summary,cap_rows,parameters,run_id)
    (out/'controls.json').write_text(json.dumps(negative,indent=2),encoding='utf-8')
    require(code_before=={p.relative_to(ROOT).as_posix():sha(p) for p in public_code},'SOURCE_CHANGED_DURING_REPLAY')
    result.update(candidate_sha256=PIN,run_id=run_id,code_and_input_sha256=code_before,binary_sha256=sha(binary),controls=negative,
                  compiler=subprocess.check_output(['rustc','--version'],env=env,text=True).strip(),python=sys.version.split()[0],completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  original_full_runner='FAILED_OR_INCOMPLETE',formal_proof=False,peer_reviewed=False)
    (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    record.update(status='COMPLETED',result_sha256=sha(out/'result.json'),completed_utc=result['completed_utc'],outputs=[{'path':p.relative_to(out).as_posix(),'sha256':sha(p)} for p in sorted(out.rglob('*')) if p.is_file() and p.name!='receipt.json'])
    save()
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
