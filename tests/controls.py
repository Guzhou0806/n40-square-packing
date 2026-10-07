import copy
from fractions import Fraction as Q
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'verifier'))
import caps
from validate import validate, require

def run(nodes,summary,rows,parameters,run_id):
    controls=[]
    def reject(name,change):
        n,s,c,p=copy.deepcopy((nodes,summary,rows,parameters))
        change(n,s,c,p)
        try:
            validate(n,s,c,p,run_id)
        except (ValueError,KeyError) as error:
            controls.append({'case':name,'refused':True,'reason':str(error)})
        else:
            raise RuntimeError('CONTROL_NOT_REFUSED:'+name)
    reject('missing_direction',lambda n,s,c,p:n['rows'].pop())
    reject('duplicate_direction',lambda n,s,c,p:n['rows'].append(n['rows'][1]))
    reject('missing_enhanced_node',lambda n,s,c,p:n['rows'][1].update(threshold='10001/10000'))
    reject('wrong_multiplicity',lambda n,s,c,p:c[0].update(support_count_with_multiplicity=3839*16))
    reject('floatified_exact_constant',lambda n,s,c,p:p.update(q=str(float(Q(p['q'])))))
    reject('missing_triangle',lambda n,s,c,p:c[0]['triangles'].pop())
    reject('reduced_G',lambda n,s,c,p:c[1].update(G='0'))
    reject('changed_target_stale_parameters',lambda n,s,c,p:p.update(X='33510/5000'))
    reject('stale_receipt',lambda n,s,c,p:n.update(run_id='stale'))
    reject('incomplete_domain',lambda n,s,c,p:n['rows'][200].update(complete_continuous_domain=False))
    for name in ('run.py','caps.py','validate.py'):
        process=subprocess.run([sys.executable,'-O',str(Path(caps.__file__).with_name(name))],capture_output=True,text=True)
        require(process.returncode!=0 and 'ASSERTIONS_DISABLED' in process.stderr,'OPTIMIZED_NOT_REFUSED')
        controls.append({'case':'disabled_assertions_'+name,'refused':True,'exit_code':process.returncode})
    cases=caps.selftests()
    big=2**200
    require(caps.maximum([(0,0,2,2,big),(1,1,3,3,big+1)])[0]==2*big+1,'UNBOUNDED_INTEGER_FAILURE')
    controls.append({'case':'integer_overflow_avoided','passed':True,'weight_bits':201})
    return {'status':'CONTROLS_PASSED','controls':controls,'event_controls':cases}
