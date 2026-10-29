"""Read-only linear feasibility of fixed C33 QP rows before any geometry update."""
from pathlib import Path
import sys,json,numpy as np,scipy.sparse as sp,scipy.optimize as opt
inp=Path(sys.argv[1]);out=Path(sys.argv[2]);d=np.load(inp);n=int(d['n']);A=sp.csr_matrix((d['A_data'],(d['A_rows'],d['A_cols'])),shape=(len(d['lower']),n));lo=d['lower'];hi=d['upper'];eq=np.isfinite(lo)&np.isfinite(hi)&(lo==hi);up=np.isfinite(hi)&~eq;low=np.isfinite(lo)&~eq;Au=sp.vstack([A[up],-A[low]],format='csr');bu=np.r_[hi[up],-lo[low]];r=opt.linprog(np.zeros(n),A_ub=Au,b_ub=bu,A_eq=A[eq],b_eq=lo[eq],bounds=[(None,None)]*n,method='highs',options={'time_limit':30,'primal_feasibility_tolerance':1e-8,'dual_feasibility_tolerance':1e-8});result={'stage':'C33-before-geometry-readonly-linear-feasibility','status':int(r.status),'message':r.message,'success':bool(r.success),'fixed_targets_and_QP_rows_unchanged':True,'geometry_applied':False}
if r.x is not None:
 val=A@r.x;result['actual_max_upper_violation']=float(np.max(np.maximum(val-hi,0)));result['actual_max_lower_violation']=float(np.max(np.maximum(lo-val,0)));np.savez(out,x=r.x)
out.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
