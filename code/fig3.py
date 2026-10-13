import json,numpy as np,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, seaborn as sns
sns.set_theme(style='ticks',context='paper',font='Liberation Sans',font_scale=1.05); pal=sns.color_palette('colorblind')
S=json.load(open('samplesize.json')); O=json.load(open('p8.json'))
fig,ax=plt.subplots(1,3,figsize=(12,3.9)); a,b,c=ax
n=[r['n'] for r in S['calib']]
a.plot(n,[r['b_half'] for r in S['calib']],'o-',color=pal[3]); a.axhline(.10,ls=':',color='0.5'); a.axhline(.05,ls='--',color='0.5'); a.text(1000,.103,'±0.10',ha='right',fontsize=8); a.text(1000,.053,'±0.05',ha='right',fontsize=8)
a2=a.twinx(); a2.plot(n,[r['g_half'] for r in S['calib']],'s--',color=pal[0]); a2.set_ylabel('G7 95% CI half-width (mg/dL)',color=pal[0])
a.set_xscale('log'); a.set_xticks([50,100,200,400,1000]); a.set_xticklabels(['50','100','200','400','1000']); a.set_xlabel('Patients used to derive the law'); a.set_ylabel('β 95% CI half-width',color=pal[3]); a.set_title('a',loc='left',fontweight='bold',fontsize=13)
k=[r['k'] for r in O['anchor']]; b.plot(k,[r['med'] for r in O['anchor']],'o-',color=pal[0],label='Median'); b.plot(k,[r['p90'] for r in O['anchor']],'o--',color=pal[0],alpha=.6,label='90th percentile')
b.set_xscale('log'); b.set_xticks(k); b.set_xticklabels([str(v) for v in k]); b.set_xlabel('HbA1c values used to anchor at a new hospital'); b.set_ylabel('Error in share with HbA1c ≥ 7% (points)'); b.legend(frameon=False,fontsize=8); b.set_title('b',loc='left',fontweight='bold',fontsize=13)
n2=[r['n'] for r in S['slope']]; c.plot(n2,[r['power']*100 for r in S['slope']],'o-',color=pal[2]); c.axhline(80,ls=':',color='0.5')
c.set_xlabel('Patients in the comparison'); c.set_ylabel('Power to distinguish slope 0.47 from 0.68 (%)'); c.set_ylim(0,100); c.set_title('c',loc='left',fontweight='bold',fontsize=13)
sns.despine(fig,right=False); fig.tight_layout(); fig.savefig('fig3.png',dpi=240); fig.savefig('../figures/Fig4.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'}); print('ok')
