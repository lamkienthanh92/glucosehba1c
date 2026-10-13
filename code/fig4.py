import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, seaborn as sns
sns.set_theme(style='ticks',context='paper',font='Liberation Sans',font_scale=1.05); pal=sns.color_palette('colorblind')
O=json.load(open('p8.json')); N=json.load(open('nhanes.json')); D,X,F=O['dev'],O['ext'],N['fit']['t2d']
fig,(a,b)=plt.subplots(1,2,figsize=(10,4.2),gridspec_kw={'width_ratios':[1,1.25]})
x=np.linspace(70,330,100)
a.plot(x,np.exp(D['a'])*x**D['b'],color=pal[3],lw=2,label=f"Le Van Thinh: β {D['b']:.2f}, G7 {D['G7']:.0f}")
a.plot(x,np.exp(X['a'])*x**X['b'],color=pal[0],lw=2,ls='--',label=f"Sa Dec: β {X['b']:.2f}, G7 {X['G7']:.0f}")
a.plot(x,np.exp(F['a'])*x**F['b'],color=pal[2],lw=2,ls='-.',label=f"NHANES 2021–2023: β {F['b']:.2f}, G7 {F['G7']:.0f}")
a.scatter(N['q']['gq'],N['q']['aq'],s=14,marker='^',color=pal[2],zorder=3,label='NHANES quantiles (2%–98%)')
a.axhline(7,ls=':',color='0.4',lw=.8); a.set_xlim(70,330); a.set_ylim(5,13); a.set_xlabel('Glucose quantile (mg/dL)'); a.set_ylabel('HbA1c quantile (%)'); a.legend(frameon=False,fontsize=7.5,loc='upper left'); a.set_title('a',loc='left',fontweight='bold',fontsize=13)
G=N['groups']; ks=list(G.keys()); lab=['Adults without\ndiabetes','Diabetes,\nno drug','Diabetes,\noral drugs','Diabetes,\ninsulin']
xx=np.arange(len(ks)); b.bar(xx-.2,[G[k]['law']['med'] for k in ks],.4,color=pal[3],label='Distribution law (anchored)')
b.bar(xx+.2,[G[k]['reg']['med'] for k in ks],.4,color=pal[7],hatch='//',edgecolor='white',label='Individual regression (anchored)')
for i,k in enumerate(ks): b.text(i,-0.68,f"n = {G[k]['n']:,}\nmedian {G[k]['medA']:.1f}%",ha='center',fontsize=7.2)
b.axhline(0,color='0.3',lw=.8); b.set_xticks(xx); b.set_xticklabels(lab,fontsize=8.5); b.set_ylim(-0.75,0.55); b.set_ylabel('Error in median HbA1c, predicted − observed (%)'); b.legend(frameon=False,fontsize=7.5,loc='upper right'); b.set_title('b',loc='left',fontweight='bold',fontsize=13)
sns.despine(fig); fig.tight_layout(); fig.savefig('fig4.png',dpi=240); fig.savefig('../figures/Fig3.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'}); print('ok')
