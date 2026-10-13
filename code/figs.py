import json,numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, seaborn as sns
from matplotlib.ticker import NullFormatter
sns.set_theme(style='ticks',context='paper',font='Liberation Sans',font_scale=1.05); pal=sns.color_palette('colorblind')
O=json.load(open('p8.json')); D,X=O['dev'],O['ext']
lvt=pd.read_excel('../data_private/thinh_deid.xlsx')
G=lvt['glucose_mg_dl'].values.astype(float); A=lvt['hba1c_pct'].values.astype(float)
def tag(a,t): a.set_title(t,loc='left',fontweight='bold',fontsize=13)
# ---- Figure 1: development at LVT
fig,ax=plt.subplots(1,3,figsize=(12,4.2)); a,b,c=ax; x=np.linspace(70,450,100)
a.scatter(G,A,s=10,alpha=.5,color='0.5',lw=0,label=f'Patients (n = {D["n"]})'); a.plot(x,np.exp(D['areg'])*x**D['breg'],'--',color=pal[1],lw=2,label=f"Individual regression (slope {D['breg']:.2f})"); a.plot(x,D['k']*x**D['b'],color=pal[3],lw=2.3,label=f"Distribution law (exponent {D['b']:.2f})")
a.set_xscale('log'); a.set_yscale('log'); a.set_xticks([80,100,200,400]); a.set_xticklabels(['80','100','200','400']); a.set_yticks([5,6,8,10,14]); a.set_yticklabels(['5','6','8','10','14']); a.xaxis.set_minor_formatter(NullFormatter()); a.yaxis.set_minor_formatter(NullFormatter())
a.set_xlabel('Glucose (mg/dL, log scale)'); a.set_ylabel('HbA1c (%, log scale)'); a.legend(frameon=False,fontsize=7.5,loc='upper left'); tag(a,'a')
q=O['lvt_q']; b.plot(q['gq'],q['aq'],'o',ms=3.5,color=pal[3],label='Quantiles 2%–98%'); b.plot(x,D['k']*x**D['b'],color=pal[3],lw=2,label=f"HbA1c = {D['k']:.3f} × G^{D['b']:.3f}")
b.set_xscale('log'); b.set_yscale('log'); b.set_xticks([80,100,150,200,300]); b.set_xticklabels(['80','100','150','200','300']); b.set_yticks([5,6,7,8,10,12]); b.set_yticklabels(['5','6','7','8','10','12']); b.xaxis.set_minor_formatter(NullFormatter()); b.yaxis.set_minor_formatter(NullFormatter())
b.set_xlim(85,400); b.set_ylim(5,14); b.text(.97,.05,f"Quantile R² = {D['r2qq']:.3f}",transform=b.transAxes,ha='right',fontsize=8.5); b.set_xlabel('Glucose quantile (mg/dL)'); b.set_ylabel('HbA1c quantile (%)'); b.legend(frameon=False,fontsize=7.5,loc='upper left'); tag(b,'b')
I=O['internal']; ks=list(I); xx=np.arange(3)
c.bar(xx-.2,[I[k]['p7'] for k in ks],.4,color=pal[0],label='Share with HbA1c ≥ 7% (points)'); c2=c.twinx(); c2.bar(xx+.2,[I[k]['qf'] for k in ks],.4,color=pal[7],hatch='//',edgecolor='white',label='Quantile error (HbA1c points)')
c.set_xticks(xx); c.set_xticklabels(['Law,\nunchanged','Law,\nanchored','Individual\nregression'],fontsize=8.5); c.set_ylabel('Mean absolute error, share ≥ 7% (points)'); c2.set_ylabel('Mean quantile error (HbA1c points)'); c.set_ylim(0,6); c2.set_ylim(0,.35)
h1,l1=c.get_legend_handles_labels(); h2,l2=c2.get_legend_handles_labels(); c.legend(h1+h2,l1+l2,frameon=False,fontsize=7.5,loc='upper right'); c.set_title('c',loc='left',fontweight='bold',fontsize=13)
sns.despine(fig,right=False); fig.tight_layout(); fig.savefig('fig1.png',dpi=240); fig.savefig('../figures/Fig1.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'}); plt.close()
# ---- Figure 2: external validation at Sa Dec
fig,ax=plt.subplots(2,2,figsize=(11,8.5)); a,b,c,d=ax.ravel(); P=O['ext_pred']; ob=O['ext_obs']; a.plot([5,13],[5,13],color='0.6',lw=.8)
for k,col,mk in [('Law, unchanged',pal[3],'o'),('Law, anchored to local median',pal[0],'s'),('Individual regression',pal[1],'D')]:
    a.plot(ob['obs_q'],P[k]['q'],marker=mk,ms=3.5,color=col,label=f"{k} (Δ ≥ 7%: {P[k]['p7']:+.1f})")
a.set_xlim(5,13); a.set_ylim(5,13.5); a.set_xlabel('Observed HbA1c quantile, Sa Dec (%)'); a.set_ylabel('Predicted HbA1c quantile (%)'); a.legend(frameon=False,fontsize=7.5,loc='upper left'); tag(a,'a')
x=np.linspace(80,330,100); b.plot(x,D['k']*x**D['b'],color=pal[3],lw=2,label=f"Le Van Thinh (development): β {D['b']:.2f}, G7 {D['G7']:.0f}"); b.plot(x,X['k']*x**X['b'],color=pal[0],lw=2,label=f"Sa Dec (external): β {X['b']:.2f}, G7 {X['G7']:.0f}")
b.scatter(O['sd_q']['gq'],O['sd_q']['aq'],s=12,color=pal[0],zorder=3,alpha=.8); b.axhline(7,ls=':',color='0.4',lw=.8); b.set_xlim(80,330); b.set_ylim(5,14); b.set_xlabel('Glucose quantile (mg/dL)'); b.set_ylabel('HbA1c quantile (%)'); b.legend(frameon=False,fontsize=8,loc='upper left'); tag(b,'b')
rows=[('Le Van Thinh',D,pal[3]),('Sa Dec, all',X,pal[0])]+[(f'  {k}',v,'0.45') for k,v in O['sub'].items()]
y=np.arange(len(rows))[::-1]
for yy,(l,v,col) in zip(y,rows):
    c.errorbar(v['b'],yy,xerr=[[v['b']-v['b_ci'][0]],[v['b_ci'][1]-v['b']]],fmt='o',color=col,capsize=2,ms=4); d.errorbar(v['G7'],yy,xerr=[[v['G7']-v['G7_ci'][0]],[v['G7_ci'][1]-v['G7']]],fmt='o',color=col,capsize=2,ms=4)
c.set_yticks(y); c.set_yticklabels([r[0] for r in rows],fontsize=7.8); d.set_yticks(y); d.set_yticklabels([]); c.axvline(D['b'],ls=':',color=pal[3]); d.axvline(D['G7'],ls=':',color=pal[3])
c.set_xlabel('Exponent β (95% CI)'); d.set_xlabel('Glucose equivalent to HbA1c 7% (mg/dL)'); tag(c,'c'); tag(d,'d')
sns.despine(fig); fig.tight_layout(); fig.savefig('fig2.png',dpi=240); fig.savefig('../figures/Fig2.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'}); plt.close()
# ---- Figure S1: anchoring
fig,a=plt.subplots(figsize=(6,4)); A_=O['anchor']; k=[q['k'] for q in A_]
a.plot(k,[q['med'] for q in A_],'o-',color=pal[0],label='Median'); a.plot(k,[q['p90'] for q in A_],'o--',color=pal[0],alpha=.6,label='90th percentile')
a.set_xscale('log'); a.set_xticks(k); a.set_xticklabels([str(v) for v in k]); a.set_xlabel('HbA1c measurements used to anchor the law at Sa Dec'); a.set_ylabel('Absolute error in share with HbA1c ≥ 7%\n(percentage points)'); a.legend(frameon=False)
sns.despine(fig); fig.tight_layout(); fig.savefig('figS1.png',dpi=240); fig.savefig('../figures/ESM_Fig_S1.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'}); plt.close(); print('ok')
