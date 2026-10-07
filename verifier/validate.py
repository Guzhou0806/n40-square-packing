from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PIN='71011d0356dd179c6e7e6e02c9a064ff30f6f13844016ce3b97463bf7ef53dc0'
PARAMS={'X':'33509/5000','L':'67/10','B':'9977/10000','q':'33500/33509','h':'1019088832887/1000000000000000','D':'83/40000','M':'3999/100'}

def require(test,reason):
    if not test:
        raise ValueError(reason)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def tau(r):
    return Q(2503,2500) if r==0 else Q(10009,10000) if r<=3 else Q(1251,1250) if r<=33 else Q(2001,2000) if r<=42 else Q(10001,10000)

def validate(nodes,summary,rows,parameters,expected_run):
    require(__debug__,'ASSERTIONS_DISABLED')
    require(parameters==PARAMS,'STALE_TARGET_PARAMETERS')
    require(nodes['run_id']==summary['run_id']==expected_run,'STALE_RECEIPT')
    require(nodes['candidate_sha256']==summary['candidate_sha256']==PIN,'INPUT_IDENTITY')
    require(nodes['status']=='COMPLETE_CONTINUOUS_NODES','NODE_STATUS')
    require(sorted(x['r'] for x in nodes['rows'])==list(range(201)),'EXACT_NODE_SET')
    for x in nodes['rows']:
        require(x['verdict']=='verified' and x['complete_continuous_domain'] is True,'NODE_SCOPE')
        require(Q(x['threshold'])==tau(x['r']) and Q(x['lower_exact'])>=tau(x['r']),'NODE_THRESHOLD')
    require(summary['status']=='FULL_FINITE_ONLY','FINITE_STATUS')
    require([x['r'] for x in summary['classification']]==list(range(200)),'INTERVAL_SET')
    active=[]
    B,q,h,D=map(Q,(PARAMS['B'],PARAMS['q'],PARAMS['h'],PARAMS['D']))
    for x in summary['classification']:
        r=x['r']
        d=D/(1+r*(r+1)*D*D)
        beta=(d-h)/(1+d*h)
        c,s=(1-beta*beta)/(1+beta*beta),2*beta/(1+beta*beta)
        lossy=beta>0 and B*(c+s)>q
        require(x['active']==lossy and Q(x['beta_half_tangent'])==beta,'CLASSIFICATION')
        if lossy:
            active.append(r)
    require(sorted(x['r'] for x in rows)==active==summary['completed'],'CAP_ROW_SET')
    charges=[Q(10001,10000)]
    for row in rows:
        require(row['candidate_sha256']==PIN and row['implementation_sha256']==summary['implementation_sha256'],'FINITE_IDENTITY')
        require(len(row['triangles'])==16 and row['support_count_with_multiplicity']==3840*16,'CAP_MULTIPLICITY')
        a=Q(row['subtriangle_area'])
        require(a>0,'AREA')
        for triangle in row['triangles']:
            require(len(triangle)==3,'TRIANGLE')
            p=[tuple(map(Q,v)) for v in triangle]
            require(abs(sum(u[0]*v[1]-u[1]*v[0] for u,v in zip(p,p[1:]+p[:1])))/2==a,'TRIANGLE_AREA')
        G=Q(row['G'])
        require(G==Q(row['maximum_integer'],row['density_scale']) and G>=0,'ENVELOPE_ARITHMETIC')
        require(Q(row['loss'])==a*G and Q(row['required_tau'])==tau(row['r']),'LOSS_ARITHMETIC')
        charge=tau(row['r'])-a*G
        require(Q(row['conditional_charge'])==charge,'CHARGE_ARITHMETIC')
        charges.append(charge)
    chi=min(charges)
    require(chi==Q(summary['conditional_min_charge']) and chi>=Q(99981,100000),'FINAL_CHARGE')
    require(40*Q(99981,100000)-Q(PARAMS['M'])==Q(3,1250)>0,'COUNTING_GAP')
    return {'status':'FULL_REPLAY_PASSED','claim':'s(40) > 33509/5000','chi':str(chi),'simple_charge':'99981/100000','gap':'3/1250','nodes':201,'intervals':200,'active':len(active),'independence_grade':'CODE_DISTINCT_FULL'}

if __name__=='__main__':
    if not __debug__:
        raise SystemExit('ASSERTIONS_DISABLED')
    raise SystemExit('使用完整入口 / Use verifier/run.py')
