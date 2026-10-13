import numpy as np, pandas as pd, json
rng=np.random.default_rng(2025)
u=np.linspace(.02,.98,49); uu=np.linspace(.05,.95,19)
def law(G,A): b,a=np.polyfit(np.log(np.quantile(G,u)),np.log(np.quantile(A,u)),1); return a,b
G7=lambda a,b: float(np.exp((np.log(7)-a)/b))
lvt=pd.read_excel('../data_private/thinh_deid.xlsx'); lvt.columns=[c.strip() for c in lvt.columns]
# Dates: text cells are dd/mm/yyyy. In the first batch (Sep-Nov 2025; the 127 records with a sample ID and E11 code),
# Excel date cells were stored with day and month swapped (checked against the ddmmyy prefix of the sample ID).
def _date(x,batch1):
    if isinstance(x,str): return pd.to_datetime(x.strip(),format='%d/%m/%Y')
    x=pd.Timestamp(x); return pd.Timestamp(year=x.year,month=x.day,day=x.month) if (batch1 and x.day<=12) else x
dt=pd.Series([_date(x,b) for x,b in zip(lvt['Ngày XN'],lvt['Chẩn đoán'].notna())])
L=dict(G=lvt['Định lượng Glucose [Máu]'].values.astype(float),A=lvt['Định lượng HbA1c [Máu]'].values.astype(float),egfr=lvt['eGFR (CKD-EPI)'].values.astype(float),
       age=(dt.dt.year-lvt['Năm sinh']).values.astype(float),female=lvt['Giới tính'].str.strip().str.lower().eq('nữ').values,e11=lvt['Chẩn đoán'].notna().values,period=[str(dt.min().date()),str(dt.max().date())])
raw=pd.read_excel('../data_private/sadec_deid.xlsx'); raw['NGÀY XN']=pd.to_datetime(raw['NGÀY XN']); sd=raw.sort_values('NGÀY XN'); sd=sd[~sd['MÃ BN'].duplicated()].reset_index(drop=True)
S=dict(G=sd.Glucose.values*18.016,A=sd.Hba1c.values.astype(float),egfr=sd.eGFR.values.astype(float),age=(sd['NGÀY XN'].dt.year-sd['NĂM SINH']).values.astype(float),
       female=sd['GIỚI TÍNH'].eq('NỮ').values,dur=sd['THỜI GIAN MẮC BỆNH ĐTĐ'].values,occ=sd['NGHỀ NGHIỆP'].values,period=[str(sd['NGÀY XN'].min().date()),str(sd['NGÀY XN'].max().date())])
def fitall(G,A,B=2000):
    a,b=law(G,A); bs=[]
    for _ in range(B):
        i=rng.integers(0,len(G),len(G)); aa,bb=law(G[i],A[i]); bs.append((aa,bb,G7(aa,bb)))
    bs=np.array(bs); X=np.log(np.quantile(G,u)); Y=np.log(np.quantile(A,u)); lg,la=np.log(G),np.log(A); breg,areg=np.polyfit(lg,la,1)
    return dict(n=len(G),a=float(a),b=float(b),k=float(np.exp(a)),b_ci=np.percentile(bs[:,1],[2.5,97.5]).tolist(),G7=G7(a,b),G7_ci=np.percentile(bs[:,2],[2.5,97.5]).tolist(),
                r2qq=float(np.corrcoef(X,Y)[0,1]**2),r=float(np.corrcoef(lg,la)[0,1]),breg=float(breg),areg=float(areg),sdratio=float(la.std()/lg.std())),bs
dev,bsd=fitall(L['G'],L['A']); ext,bse=fitall(S['G'],S['A'])
diff=dict(beta=ext['b']-dev['b'],beta_ci=np.percentile(bse[:,1]-bsd[:,1],[2.5,97.5]).tolist(),G7=ext['G7']-dev['G7'],G7_ci=np.percentile(bse[:,2]-bsd[:,2],[2.5,97.5]).tolist())
def predict(a,b,breg,areg,res,Gt,At):
    oq=np.quantile(At,uu); o7=np.mean(At>=7)*100; om=np.median(At)
    P={'Law, unchanged':np.exp(a+b*np.log(Gt)),'Law, anchored to local median':np.exp(np.log(om)-b*np.log(np.median(Gt))+b*np.log(Gt))}
    lp=areg+breg*np.log(Gt); P['Individual regression']=np.exp(lp[:,None]+rng.choice(res,(len(Gt),100))).ravel()
    return {k:dict(p7=float(np.mean(p>=7)*100-o7),med=float(np.median(p)-om),qf=float(np.mean(np.abs(np.quantile(p,uu)-oq))),q=np.quantile(p,uu).tolist()) for k,p in P.items()},dict(obs_q=oq.tolist(),obs_p7=float(o7),obs_med=float(om),gq=np.quantile(Gt,uu).tolist())
# internal validation at LVT: repeated split-half
iv={'Law, unchanged':[],'Law, anchored to local median':[],'Individual regression':[]}
for _ in range(500):
    p=rng.permutation(len(L['G'])); tr,te=p[:len(p)//2],p[len(p)//2:]
    a,b=law(L['G'][tr],L['A'][tr]); lg,la=np.log(L['G'][tr]),np.log(L['A'][tr]); br,ar=np.polyfit(lg,la,1); res=la-(ar+br*lg)
    pr,_=predict(a,b,br,ar,res,L['G'][te],L['A'][te])
    for k in iv: iv[k].append((abs(pr[k]['p7']),pr[k]['qf']))
internal={k:dict(p7=float(np.mean([x[0] for x in v])),qf=float(np.mean([x[1] for x in v]))) for k,v in iv.items()}
# external
lg,la=np.log(L['G']),np.log(L['A']); res=la-(dev['areg']+dev['breg']*lg)
ext_pred,ext_obs=predict(dev['a'],dev['b'],dev['breg'],dev['areg'],res,S['G'],S['A'])
# subgroups at Sa Dec
sub={}
for lab,m in [('Duration < 5 years',S['dur']=='< 5 năm'),('Duration 5–10 years',S['dur']=='5 - 10 năm'),('Duration > 10 years',np.isin(S['dur'],['10 - 15 năm','> 15 năm'])),
              ('Women',S['female']),('Men',~S['female']),('Age < 65 years',S['age']<65),('Age ≥ 65 years',S['age']>=65),('Farmers',S['occ']=='Nông dân'),('Other occupations',S['occ']!='Nông dân'),('eGFR ≥ 60',S['egfr']>=60),('eGFR < 60',S['egfr']<60)]:
    r,_=fitall(S['G'][m],S['A'][m],B=1000); pr,ob=predict(dev['a'],dev['b'],dev['breg'],dev['areg'],res,S['G'][m],S['A'][m])
    sub[lab]=dict(n=r['n'],b=r['b'],b_ci=r['b_ci'],G7=r['G7'],G7_ci=r['G7_ci'],anch=pr['Law, anchored to local median']['p7'],unch=pr['Law, unchanged']['p7'],obs_p7=ob['obs_p7'])
# sensitivity
sens={}
r,_=fitall(raw.Glucose.values*18.016,raw.Hba1c.values.astype(float),B=500); sens['Sa Dec, all 288 records']=dict(b=r['b'],b_ci=r['b_ci'],G7=r['G7'],G7_ci=r['G7_ci'])
m=L['e11']; r,_=fitall(L['G'][m],L['A'][m],B=500); sens['Le Van Thinh, E11 coded only']=dict(n=r['n'],b=r['b'],b_ci=r['b_ci'],G7=r['G7'],G7_ci=r['G7_ci'])
m=~(L['egfr']<60); r,_=fitall(L['G'][m],L['A'][m],B=500); sens['Le Van Thinh, eGFR ≥ 60 or missing']=dict(n=r['n'],b=r['b'],b_ci=r['b_ci'],G7=r['G7'],G7_ci=r['G7_ci'])
# anchoring sample size at Sa Dec
anc=[]
for k in [10,20,30,50,100]:
    e=[]; e2=[]
    for _ in range(1000):
        j=rng.choice(len(S['A']),k,replace=False); aa=np.log(np.median(S['A'][j]))-dev['b']*np.log(np.median(S['G'])); e.append(abs(np.mean(np.exp(aa+dev['b']*np.log(S['G']))>=7)-np.mean(S['A']>=7))*100)
        e2.append(abs(np.mean(S['A'][j]>=7)-np.mean(S['A']>=7))*100)   # direct estimate from the same k HbA1c values
    anc.append(dict(k=k,med=float(np.median(e)),p90=float(np.percentile(e,90)),dir_med=float(np.median(e2)),dir_p90=float(np.percentile(e2,90))))
q=lambda x:np.nanpercentile(x,[50,25,75]).tolist()
desc=dict(lvt=dict(n=len(L['G']),age=q(L['age']),female=float(L['female'].mean()*100),glu=q(L['G']),a1c=q(L['A']),p7=float(np.mean(L['A']>=7)*100),egfr=q(L['egfr']),egfr_n=int(np.sum(~np.isnan(L['egfr']))),egfr_lt60=float(np.sum(L['egfr']<60)/np.sum(~np.isnan(L['egfr']))*100),e11=int(L['e11'].sum()),period=L['period']),
          sd=dict(n=len(S['G']),n_raw=len(raw),age=q(S['age']),female=float(S['female'].mean()*100),glu=q(S['G']),a1c=q(S['A']),p7=float(np.mean(S['A']>=7)*100),egfr=q(S['egfr']),egfr_n=len(S['egfr']),egfr_lt60=float(np.mean(S['egfr']<60)*100),
                  dur=pd.Series(S['dur']).value_counts().to_dict(),occ=pd.Series(S['occ']).value_counts().to_dict(),period=S['period']))
out=dict(dev=dev,ext=ext,diff=diff,internal=internal,ext_pred=ext_pred,ext_obs=ext_obs,sub=sub,sens=sens,anchor=anc,desc=desc,lvt_q=dict(gq=np.quantile(L['G'],u).tolist(),aq=np.quantile(L['A'],u).tolist()),sd_q=dict(gq=np.quantile(S['G'],u).tolist(),aq=np.quantile(S['A'],u).tolist()))
json.dump(out,open('p8.json','w'),default=float)
print('dev',{k:(round(v,3) if isinstance(v,float) else v) for k,v in dev.items()}); print('ext',{k:(round(v,3) if isinstance(v,float) else v) for k,v in ext.items()}); print('diff',diff); print('internal',internal)
for k,v in ext_pred.items(): print(k,round(v['p7'],1),round(v['med'],2),round(v['qf'],2))
print(sens)
