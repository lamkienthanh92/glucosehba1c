import numpy as np, pandas as pd, json
rng=np.random.default_rng(8)
O=json.load(open('p8.json')); D=O['dev']
raw=pd.read_excel('../data_private/sadec_deid.xlsx').sort_values('NGÀY XN'); sd=raw[~raw['MÃ BN'].duplicated()].reset_index(drop=True)
G=sd.Glucose.values*18.016; A=sd.Hba1c.values.astype(float); dur=sd['THỜI GIAN MẮC BỆNH ĐTĐ'].values
lvt=pd.read_excel('../data_private/thinh_deid.xlsx'); lvt.columns=[c.strip() for c in lvt.columns]
lg,la=np.log(lvt['Định lượng Glucose [Máu]'].values.astype(float)),np.log(lvt['Định lượng HbA1c [Máu]'].values.astype(float)); res=la-(D['areg']+D['breg']*lg)
a_law=np.log(np.median(A))-D['b']*np.log(np.median(G))
pr=np.exp((D['areg']+D['breg']*np.log(G))[:,None]+res[None,:]).ravel(); a_reg=D['areg']+np.log(np.median(A))-np.log(np.median(pr))
cats=[('< 5 năm','< 5 years'),('5 - 10 năm','5–10 years'),('10 - 15 năm','10–15 years'),('> 15 năm','> 15 years')]; rows=[]
for c,lab in cats:
    m=dur==c; g,a=G[m],A[m]; law=np.exp(a_law+D['b']*np.log(g)); rg=np.exp((a_reg+D['breg']*np.log(g))[:,None]+res[None,:]).ravel()
    rows.append(dict(group=lab,n=int(m.sum()),medG=float(np.median(g)),dG=float((np.median(g)/np.median(G)-1)*100),medA=float(np.median(a)),law_med=float(np.median(law)-np.median(a)),reg_med=float(np.median(rg)-np.median(a)),law_p7=float(np.mean(law>=7)*100-np.mean(a>=7)*100),reg_p7=float(np.mean(rg>=7)*100-np.mean(a>=7)*100)))
def slope(idx):
    x=[np.log(np.median(G[idx][dur[idx]==c])) for c,_ in cats]; y=[np.log(np.median(A[idx][dur[idx]==c])) for c,_ in cats]; return np.polyfit(x,y,1)[0]
s0=float(slope(np.arange(len(G)))); bs=[slope(rng.integers(0,len(G),len(G))) for _ in range(2000)]
json.dump(dict(rows=rows,slope=s0,slope_ci=np.percentile(bs,[2.5,97.5]).tolist(),beta=D['b'],breg=D['breg']),open('duration.json','w')); print('ok',round(s0,3))
