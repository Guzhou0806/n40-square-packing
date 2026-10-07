import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import random
import time

ROOT=Path(__file__).resolve().parents[1]
CANDIDATE=ROOT/'certificate/certified_candidate.json'
PIN='71011d0356dd179c6e7e6e02c9a064ff30f6f13844016ce3b97463bf7ef53dc0'
L=Q(67,10)
B=Q(9977,10000)
TARGET=Q(33509,5000)
SIDE=L/TARGET
STEP=Q(83,40000)
H=Q(1019088832887,10**15)
PRECISION=10**9

def sha(data):
    return hashlib.sha256(data).hexdigest()

def turn(t):
    return (1-t*t)/(1+t*t),2*t/(1+t*t)

def density():
    raw=CANDIDATE.read_bytes()
    assert sha(raw)==PIN
    data=json.loads(raw,parse_float=Q)
    assert Q(data['L'])==L and Q(data['B'])==B
    assert len(data['weights'])==len(data['rectangles'])==2526
    rows=[]
    positive=0
    for rectangle,weight in zip(data['rectangles'],data['weights']):
        weight=Q(weight)
        assert weight>=0
        if weight==0:
            continue
        positive+=1
        left,bottom,right,top=map(Q,rectangle)
        assert 0<=left<right<=L and 0<=bottom<top<=L
        rho=weight/(8*(right-left)*(top-bottom))
        for swap in (False,True):
            for sx in (-1,1):
                for sy in (-1,1):
                    vertices=[]
                    for x in (left,right):
                        for y in (bottom,top):
                            u,v=x-L/2,y-L/2
                            if swap:
                                u,v=v,u
                            vertices.append((sx*u+L/2,sy*v+L/2))
                    rows.append((min(p[0] for p in vertices),min(p[1] for p in vertices),max(p[0] for p in vertices),max(p[1] for p in vertices),rho))
    assert positive==480 and len(rows)==3840
    assert sum((r[4]*(r[2]-r[0])*(r[3]-r[1]) for r in rows),Q(0))==Q(3999,100)
    multiset=Counter(rows)
    assert multiset==Counter((L-r[3],r[0],L-r[1],r[2],r[4]) for r in rows)
    assert multiset==Counter((L-r[2],r[1],L-r[0],r[3],r[4]) for r in rows)
    return rows

def clip(poly,nx,ny,offset):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        fa=nx*a[0]+ny*a[1]-offset
        fb=nx*b[0]+ny*b[1]-offset
        if fa>=0:
            result.append(a)
        if (fa>0 and fb<0) or (fa<0 and fb>0):
            t=fa/(fa-fb)
            result.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
    return list(dict.fromkeys(result))

def area(poly):
    return abs(sum((a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])),Q(0)))/2

def midpoint(a,b):
    return ((a[0]+b[0])/2,(a[1]+b[1])/2)

def parameters(r):
    assert 0<=r<200
    gap=STEP/(1+r*(r+1)*STEP**2)
    beta=(gap-H)/(1+gap*H)
    if beta<=0:
        return beta,False
    cb,sb=turn(beta)
    return beta,B*(cb+sb)>SIDE

def shapes(r):
    beta,active=parameters(r)
    assert active
    cb,sb=turn(beta)
    assert cb>=sb>0 and SIDE*cb>=B and B>=SIDE*sb
    square=[(-B/2,-B/2),(B/2,-B/2),(B/2,B/2),(-B/2,B/2)]
    caps=[clip(square,nx,ny,SIDE/2) for nx,ny in ((cb,sb),(-sb,cb),(-cb,-sb),(sb,-cb))]
    assert all(len(p)==3 and area(p)>0 for p in caps)
    cap_area=area(caps[0])
    assert all(area(p)==cap_area for p in caps)
    cr,sr=turn(r*STEP)
    triangles=[]
    for a,b,c in caps:
        ab,bc,ca=midpoint(a,b),midpoint(b,c),midpoint(c,a)
        pieces=[[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]]
        assert all(area(p)==cap_area/4 for p in pieces)
        assert sum(map(area,pieces))==cap_area
        for p in pieces:
            rotated=[(cr*x-sr*y,sr*x+cr*y) for x,y in p]
            assert area(rotated)==cap_area/4
            triangles.append(rotated)
    assert len(triangles)==16
    boxes=[(min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p)) for p in triangles]
    return cap_area/4,triangles,boxes

def supports(rows,boxes):
    scale=1
    for row in rows:
        for coordinate in row[:4]:
            scale=math.lcm(scale,coordinate.denominator)
    for box in boxes:
        for coordinate in box:
            scale=math.lcm(scale,coordinate.denominator)
    def integer(q):
        assert scale%q.denominator==0
        return q.numerator*(scale//q.denominator)
    rr=[(*map(integer,r[:4]),-((-r[4]*PRECISION).numerator//(-r[4]*PRECISION).denominator)) for r in rows]
    bb=[tuple(map(integer,b)) for b in boxes]
    rectangles=Counter()
    for a,b,d,e,w in rr:
        assert w>0
        for x0,y0,x1,y1 in bb:
            rectangles[(a-x1,b-y1,d-x0,e-y0)]+=w
    return [(*key,w) for key,w in sorted(rectangles.items())],scale

def maximum(rectangles):
    assert rectangles and all(a<d and b<e and w>0 for a,b,d,e,w in rectangles)
    ys=sorted({v for a,b,d,e,w in rectangles for v in (b,e)})
    lookup={v:i for i,v in enumerate(ys)}
    events=defaultdict(list)
    for a,b,d,e,w in rectangles:
        events[a].append((lookup[b],lookup[e]-1,w))
        events[d].append((lookup[b],lookup[e]-1,-w))
    xs=sorted(events)
    n=len(ys)-1
    value=[0]*(4*n+8)
    lazy=[0]*(4*n+8)
    def add(v,lo,hi,ql,qh,w):
        if ql<=lo and hi<=qh:
            value[v]+=w
            lazy[v]+=w
            return
        middle=(lo+hi)//2
        if ql<=middle:
            add(2*v,lo,middle,ql,qh,w)
        if qh>middle:
            add(2*v+1,middle+1,hi,ql,qh,w)
        value[v]=lazy[v]+max(value[2*v],value[2*v+1])
    def argmax(v,lo,hi):
        if lo==hi:
            return lo
        middle=(lo+hi)//2
        if value[2*v]>=value[2*v+1]:
            return argmax(2*v,lo,middle)
        return argmax(2*v+1,middle+1,hi)
    best=-1
    witness=None
    for i,x in enumerate(xs):
        for low,high,w in events[x]:
            add(1,0,n-1,low,high,w)
        if i+1<len(xs) and value[1]>best:
            best=value[1]
            k=argmax(1,0,n-1)
            witness=(x+xs[i+1],ys[k]+ys[k+1])
    assert value[1]==0
    wx,wy=witness
    direct=sum(w for a,b,d,e,w in rectangles if 2*a<wx<2*d and 2*b<wy<2*e)
    assert direct==best
    return best,witness,len(xs),len(ys)

def brute(rectangles):
    xs=sorted({v for a,b,d,e,w in rectangles for v in (a,d)})
    ys=sorted({v for a,b,d,e,w in rectangles for v in (b,e)})
    return max(sum(w for a,b,d,e,w in rectangles if 2*a<x0+x1<2*d and 2*b<y0+y1<2*e) for x0,x1 in zip(xs,xs[1:]) for y0,y1 in zip(ys,ys[1:]))

def selftests():
    cases=[[(0,0,1,1,2),(1,0,2,1,3)],[(0,0,2,2,2),(0,0,2,2,3)],[(0,0,4,4,1),(1,1,2,2,2),(2,1,3,2,4)]]
    rng=random.Random(400020261008)
    for _ in range(80):
        row=[]
        for j in range(12):
            a,b=rng.randrange(-5,6),rng.randrange(-5,6)
            row.append((a,b,a+rng.randrange(1,5),b+rng.randrange(1,5),rng.randrange(1,9)))
        cases.append(row)
    for row in cases:
        assert maximum(row)[0]==brute(row)
        rng.shuffle(row)
        assert maximum(row)[0]==brute(row)
    assert maximum(cases[0])[0]==3
    return {'event_cases':len(cases),'permutation_replays':len(cases),'boundary_contact_allowed':True}

def run_interval(r):
    start=time.monotonic()
    rows=density()
    a,triangles,boxes=shapes(r)
    rr,scale=supports(rows,boxes)
    g,witness,nx,ny=maximum(rr)
    tau=Q(2503,2500) if r==0 else Q(10009,10000) if r<=3 else Q(1251,1250) if r<=33 else Q(2001,2000) if r<=42 else Q(10001,10000)
    loss=a*Q(g,PRECISION)
    canonical=lambda x:json.dumps(x,default=str,separators=(',',':')).encode()
    return {'r':r,'status':'FRESH_FINITE_ENVELOPE_ONLY','subtriangle_area':str(a),'triangles':[[[str(x),str(y)] for x,y in p] for p in triangles],
            'triangle_sha256':sha(canonical(triangles)),'support_sha256':sha(canonical(rr)),
            'support_count_with_multiplicity':len(rows)*len(boxes),'aggregated_support_count':len(rr),'coordinate_scale':str(scale),
            'density_scale':PRECISION,'maximum_integer':g,'G':str(Q(g,PRECISION)),'witness_twice_scaled':list(map(str,witness)),
            'x_events':nx,'y_events':ny,'loss':str(loss),'required_tau':str(tau),'conditional_charge':str(tau-loss),
            'candidate_sha256':PIN,'implementation_sha256':sha(Path(__file__).read_bytes()),'wall_seconds':time.monotonic()-start,
            'nodes_independently_verified':False,'publication_allowed':False}

def main():
    if not __debug__:
        raise SystemExit('ASSERTIONS_DISABLED')
    ap=argparse.ArgumentParser(description="精确削角上界 / Exact cap bounds")
    ap.add_argument('--workers',type=int,default=4,help='并行进程数 / Worker count')
    ap.add_argument('--rows',default='all',help='区间选择 / Interval selection')
    ap.add_argument('--out',type=Path,required=True,help='输出目录 / Output directory')
    args=ap.parse_args()
    assert 1<=args.workers<=16
    args.out.mkdir(parents=True,exist_ok=False)
    assert SIDE>=B and 0<H<STEP
    ch,sh=turn(H)
    assert B*(ch+sh)<=SIDE and 2*H<=1-H*H and (1+200*STEP)**2>=2
    classification=[{'r':r,'beta_half_tangent':str(parameters(r)[0]),'active':parameters(r)[1]} for r in range(200)]
    active=[z['r'] for z in classification if z['active']]
    requested=active if args.rows=='all' else list(map(int,args.rows.split(',')))
    assert requested and len(set(requested))==len(requested) and set(requested)<=set(active)
    rows=density()
    geometry=[]
    for r in active:
        a,tr,boxes=shapes(r)
        beta=parameters(r)[0]
        c,s=turn(beta)
        assert 16*a==(B*(c+s)-SIDE)**2/(2*c*s)
        geometry.append({'r':r,'subtriangle_area':str(a),'triangle_count':len(tr)})
    controls=selftests()
    initial={'status':'RUNNING','classification':classification,'geometry':geometry,'controls':controls,'requested':requested,'imports_producer_code':False,'global_independence':'INCOMPLETE','publication_allowed':False}
    (args.out/'progress.json').write_text(json.dumps(initial,indent=2),encoding='utf-8')
    results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(run_interval,r):r for r in requested}
        for future in as_completed(futures):
            result=future.result()
            (args.out/('r%03d.json'%result['r'])).write_text(json.dumps(result,indent=2),encoding='utf-8')
            results.append(result)
            print(json.dumps({'r':result['r'],'completed':len(results),'requested':len(requested),'seconds':result['wall_seconds']}),flush=True)
    charges=[Q(z['conditional_charge']) for z in results]+[Q(10001,10000)]
    chi=min(charges)
    initial.update(status='FULL_FINITE_ONLY' if set(requested)==set(active) else 'PARTIAL_FINITE_ONLY',completed=sorted(z['r'] for z in results),conditional_min_charge=str(chi),conditional_gap=str(40*chi-Q(3999,100)),meets_simple_charge=chi>=Q(99981,100000),candidate_sha256=PIN,implementation_sha256=sha(Path(__file__).read_bytes()))
    (args.out/'summary.json').write_text(json.dumps(initial,indent=2),encoding='utf-8')
    print(json.dumps({'status':initial['status'],'meets_simple_charge':initial['meets_simple_charge'],'publication_allowed':False}),flush=True)

if __name__=='__main__':
    main()
