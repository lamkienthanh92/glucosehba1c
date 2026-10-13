"""External validation in NHANES August 2021-August 2023 (fasting subsample, United States).
Only the 2021-2023 cycle is used (contemporaneous with the hospital data)."""
import numpy as np, pandas as pd, json
rng=np.random.default_rng(2123)
u=np.linspace(.02,.98,49); uu=np.linspace(.05,.95,19)
def wq(x,q,w=None):
    if w is None: return np.quantile(x,q)
    o=np.argsort(x); x,w=x[o],w[o]; c=(np.cumsum(w)-.5*w)/w.sum(); return np.interp(q,c,x)
def law(G,A,w=None): b,a=np.polyfit(np.log(wq(G,u,w)),np.log(wq(A,u,w)),1); return a,b
G7=lambda a,b: float(np.exp((np.log(7)-a)/b))
O=json.load(open('p8.json')); D=O['dev']
lvt=pd.read_excel('../data_private/thinh_deid.xlsx'); lvt.columns=[c.strip() for c in lvt.columns]
lg0=np.log(lvt['Định lượng Glucose [Máu]'].values.astype(float)); la0=np.log(lvt['Định lượng HbA1c [Máu]'].values.astype(float))
res=la0-(D['areg']+D['breg']*lg0)

d=pd.read_csv('../data/nhanes_2021_2023_fasting.csv')
d['t1']=(d.DID040<30)&(d.DIQ050==1)                     # probable type 1 diabetes
T=d[(d.DIQ010==1)&~d.t1&(d.RIDEXPRG!=1)].reset_index(drop=True)
N=d[(d.DIQ010==2)&(d.RIDEXPRG!=1)].reset_index(drop=True)
grp={'Adults without diabetes':N,
     'T2D, no glucose-lowering drug':T[(T.DIQ050!=1)&(T.DIQ070!=1)],
     'T2D, oral drugs only':T[(T.DIQ050!=1)&(T.DIQ070==1)],
     'T2D, insulin':T[T.DIQ050==1]}
GA=lambda x:(x.LBXGLU.values.astype(float),x.LBXGH.values.astype(float))

def fitall(G,A,w=None,B=2000):
    a,b=law(G,A,w); bs=[]
    for _ in range(B):
        i=rng.integers(0,len(G),len(G)); aa,bb=law(G[i],A[i],None if w is None else w[i]); bs.append((bb,G7(aa,bb)))
    bs=np.array(bs); lg,la=np.log(G),np.log(A)
    return dict(n=int(len(G)),a=float(a),b=float(b),b_ci=np.percentile(bs[:,0],[2.5,97.5]).tolist(),G7=G7(a,b),G7_ci=np.percentile(bs[:,1],[2.5,97.5]).tolist(),
                breg=float(np.polyfit(lg,la,1)[0]),sdratio=float(la.std()/lg.std()),r=float(np.corrcoef(lg,la)[0,1]),
                medG=float(np.median(G)),medA=float(np.median(A)),p7=float(np.mean(A>=7)*100))
G,A=GA(T)
fit=dict(t2d=fitall(G,A),t2d_w=fitall(G,A,T.WTSAF2YR.values),t2d_egfr60=fitall(*GA(T[T.eGFR>=60])),
         t2d_asian=fitall(*GA(T[T.RIDRETH3==6]),B=1000))
# transfer of the Vietnamese development law to NHANES T2D
def preds(a_law,b_law,a_reg,b_reg,g):
    return np.exp(a_law+b_law*np.log(g)), np.exp((a_reg+b_reg*np.log(g))[:,None]+res[None,:]).ravel()
def errs(p,a): return dict(p7=float(np.mean(p>=7)*100-np.mean(a>=7)*100),p65=float(np.mean(p>=6.5)*100-np.mean(a>=6.5)*100),med=float(np.median(p)-np.median(a)),qf=float(np.mean(np.abs(np.quantile(p,uu)-np.quantile(a,uu)))))
pu,pr=preds(D['a'],D['b'],D['areg'],D['breg'],G); pa=np.exp(np.log(np.median(A))-D['b']*np.log(np.median(G))+D['b']*np.log(G))
transfer={'Law, unchanged':errs(pu,A),'Law, anchored to local median':errs(pa,A),'Individual regression':errs(pr,A),'obs_p7':float(np.mean(A>=7)*100)}
# glycaemic-level test: anchor once to NHANES T2D, then predict groups not defined by glucose or HbA1c
def anchors(G,A,bl,ar,br):
    a_law=np.log(np.median(A))-bl*np.log(np.median(G))
    pr=np.exp((ar+br*np.log(G))[:,None]+res[None,:]).ravel(); a_reg=ar+np.log(np.median(A))-np.log(np.median(pr)); return a_law,a_reg
def group_test(G,A,groups,bl,ar,br):
    al,arg=anchors(G,A,bl,ar,br); out={}
    for k,x in groups.items():
        g,a=GA(x); pl,prg=preds(al,bl,arg,br,g); out[k]=dict(n=int(len(g)),medG=float(np.median(g)),medA=float(np.median(a)),p7=float(np.mean(a>=7)*100),p65=float(np.mean(a>=6.5)*100),law=errs(pl,a),reg=errs(prg,a))
    return out
gt=group_test(G,A,grp,D['b'],D['areg'],D['breg'])
# bootstrap CIs for the difference in absolute error (law - regression), resampling NHANES participants
bs={k:{'med':[],'qf':[],'p7':[]} for k in grp}
for _ in range(500):
    Tb=T.sample(len(T),replace=True,random_state=int(rng.integers(1e9))); Gb,Ab=GA(Tb)
    gb={k:x.sample(len(x),replace=True,random_state=int(rng.integers(1e9))) for k,x in grp.items()}
    r=group_test(Gb,Ab,gb,D['b'],D['areg'],D['breg'])
    for k in grp:
        for m in ['med','qf','p7']: bs[k][m].append(abs(r[k]['law'][m])-abs(r[k]['reg'][m]))
for k in grp:
    for m in ['med','qf','p7']: gt[k]['diff_'+m]=[float(np.mean(bs[k][m])),*np.percentile(bs[k][m],[2.5,97.5]).tolist()]
# sensitivity: both methods fitted within NHANES T2D (own parameters) instead of the Vietnamese development parameters
lg,la=np.log(G),np.log(A); brN,arN=np.polyfit(lg,la,1); aN,bN=law(G,A)
resN=la-(arN+brN*lg); res_bak=res; res=resN
gt_own=group_test(G,A,grp,bN,arN,brN); res=res_bak
desc={k:dict(n=int(len(x)),age=np.percentile(x.RIDAGEYR,[50,25,75]).tolist(),female=float((x.RIAGENDR==2).mean()*100),glu=np.percentile(x.LBXGLU,[50,25,75]).tolist(),a1c=np.percentile(x.LBXGH,[50,25,75]).tolist(),p7=float(np.mean(x.LBXGH>=7)*100),
         egfr_lt60=float((x.eGFR<60).sum()/x.eGFR.notna().sum()*100),egfr=np.nanpercentile(x.eGFR,[50,25,75]).tolist(),egfr_n=int(x.eGFR.notna().sum()),insulin=float((x.DIQ050==1).mean()*100),asian=float((x.RIDRETH3==6).mean()*100)) for k,x in {'t2d':T,'nodm':N}.items()}
dd=(T.RIDAGEYR-T.DID040.where(T.DID040<100)).dropna(); desc['t2d']['dur']=[float((dd<5).mean()*100),float(((dd>=5)&(dd<=10)).mean()*100),float((dd>10).mean()*100)]
desc['n_excl_t1']=int(((d.DIQ010==1)&d.t1).sum())
q=dict(gq=np.quantile(G,u).tolist(),aq=np.quantile(A,u).tolist())
json.dump(dict(fit={k:v for k,v in fit.items() if v},transfer=transfer,groups=gt,groups_own=gt_own,desc=desc,q=q),open('nhanes.json','w'),default=float)
f=fit['t2d']; print('NHANES T2D',f['n'],round(f['b'],3),[round(x,3) for x in f['b_ci']],round(f['G7'],1),[round(x,1) for x in f['G7_ci']],'breg',round(f['breg'],2),'sdr',round(f['sdratio'],2))
for k in ['t2d_w','t2d_egfr60','t2d_asian']: f=fit[k]; print(k,f['n'],round(f['b'],3),[round(x,3) for x in f['b_ci']],round(f['G7'],1))
print({k:(round(v['p7'],1) if isinstance(v,dict) else round(v,1)) for k,v in transfer.items()})
for k,v in gt.items(): print(k,v['n'],round(v['medA'],2),'law',{m:round(v['law'][m],2) for m in ['med','p7','p65','qf']},'reg',{m:round(v['reg'][m],2) for m in ['med','p7','p65','qf']},'dq',[round(x,3) for x in v['diff_qf']],'dmed',[round(x,2) for x in v['diff_med']])
for k,v in gt_own.items(): print('own',k,'law',round(v['law']['med'],2),round(v['law']['qf'],2),'reg',round(v['reg']['med'],2),round(v['reg']['qf'],2))
# exponent in T2D not using insulin, and differences from the Vietnamese sites (bootstrap)
def bsb(G,A,B=2000):
    out=[]
    for _ in range(B):
        i=rng.integers(0,len(G),len(G)); a,b=law(G[i],A[i]); out.append((b,G7(a,b)))
    return np.array(out)
lvtG=np.exp(lg0); lvtA=np.exp(la0)
raw=pd.read_excel('../data_private/sadec_deid.xlsx').sort_values('NGÀY XN'); sd=raw[~raw['MÃ BN'].duplicated()]
sdG=sd.Glucose.values*18.016; sdA=sd.Hba1c.values.astype(float)
bN=bsb(G,A); bL=bsb(lvtG,lvtA); bS=bsb(sdG,sdA)
noins=fitall(*GA(T[T.DIQ050!=1]))
ins=fitall(*GA(T[T.DIQ050==1]),B=1000)
J=json.load(open('nhanes.json')); J['fit']['t2d_noins']=noins; J['fit']['t2d_ins']=ins
J['diff']={'vs_lvt':dict(beta=np.percentile(bN[:,0]-bL[:,0],[50,2.5,97.5]).tolist(),G7=np.percentile(bN[:,1]-bL[:,1],[50,2.5,97.5]).tolist()),
           'vs_sd':dict(beta=np.percentile(bN[:,0]-bS[:,0],[50,2.5,97.5]).tolist(),G7=np.percentile(bN[:,1]-bS[:,1],[50,2.5,97.5]).tolist())}
json.dump(J,open('nhanes.json','w'),default=float)
print('noins',noins['n'],round(noins['b'],3),noins['b_ci'],round(noins['G7'],1)); print(J['diff'])
