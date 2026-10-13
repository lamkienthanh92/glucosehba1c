import numpy as np, pandas as pd, json
rng=np.random.default_rng(88)
u=np.linspace(.02,.98,49)
def law(G,A): b,a=np.polyfit(np.log(np.quantile(G,u)),np.log(np.quantile(A,u)),1); return a,b
G7=lambda a,b: np.exp((np.log(7)-a)/b)
lvt=pd.read_excel('../data_private/thinh_deid.xlsx')
Gl=lvt['glucose_mg_dl'].values.astype(float); Al=lvt['hba1c_pct'].values.astype(float)
raw=pd.read_excel('../data_private/sadec_deid.xlsx').sort_values('test_date'); sd=raw[~raw['patient_id'].duplicated()].reset_index(drop=True)
Gs=sd.glucose_mmol_l.values*18.016; As=sd.hba1c_pct.values.astype(float); dur=sd['diabetes_duration'].values
Gp=np.r_[Gl,Gs]; Ap=np.r_[Al,As]   # pooled non-tertiary data as the sampling frame
NS=[50,100,150,200,300,400,600,800,1000]; out={'calib':[],'transfer':[],'slope':[]}
# 1) precision of beta and G7 as a function of development sample size
for n in NS:
    est=np.array([law(Gp[i],Ap[i]) for i in [rng.integers(0,len(Gp),n) for _ in range(1000)]]); b=est[:,1]; g=G7(est[:,0],est[:,1])
    out['calib'].append(dict(n=n,b_half=float(1.96*b.std()),g_half=float(1.96*g.std()),b_p=np.percentile(b,[2.5,97.5]).tolist()))
# 2) transfer error: law developed on n LVT-like patients (resampled from LVT), anchored at Sa Dec with 100 HbA1c values, error in share >=7 at Sa Dec
o7=np.mean(As>=7)
for n in NS:
    e=[]
    for _ in range(500):
        i=rng.integers(0,len(Gl),n); a,b=law(Gl[i],Al[i]); j=rng.choice(len(As),100,replace=False)
        aa=np.log(np.median(As[j]))-b*np.log(np.median(Gs)); e.append(abs(np.mean(np.exp(aa+b*np.log(Gs))>=7)-o7)*100)
    out['transfer'].append(dict(n=n,med=float(np.median(e)),p90=float(np.percentile(e,90))))
# 3) power to distinguish between-group slope (duration groups): SE as function of n (scaled resampling of Sa Dec)
cats=['<5 y','5-10 y','10-15 y','>15 y']
def slope(G,A,dd):
    x=[np.log(np.median(G[dd==c])) for c in cats]; y=[np.log(np.median(A[dd==c])) for c in cats]; return np.polyfit(x,y,1)[0]
for n in [279,600,1000,1500,2000,3000]:
    s=[]
    for _ in range(600):
        i=rng.integers(0,len(Gs),n); s.append(slope(Gs[i],As[i],dur[i]))
    se=float(np.std(s)); out['slope'].append(dict(n=n,se=se,power=float(__import__('scipy.stats',fromlist=['norm']).norm.cdf(0.21/se-1.96))))
json.dump(out,open('samplesize.json','w'))
print(pd.DataFrame(out['calib'])[['n','b_half','g_half']].round(3).to_string(index=False)); print(pd.DataFrame(out['transfer']).round(2).to_string(index=False)); print(pd.DataFrame(out['slope']).round(3).to_string(index=False))
