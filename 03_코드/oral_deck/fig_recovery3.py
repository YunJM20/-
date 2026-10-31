import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats
from statsmodels.stats.multitest import multipletests
import statsmodels.formula.api as smf
from config import load_li600, ORDER
CROPC={'lettuce':{'ETc':'#1F3D2B','ETc50':'#8FAA91','침수ETc':'#2E7D4F','침수ETc50':'#9FD3A8'},'bean':{'ETc':'#3B2618','ETc50':'#B9A28C','침수ETc':'#8B5A2B','침수ETc50':'#E0B98A'}}
ACC={'lettuce':'#2E6B3F','bean':'#6B4226'}; CN={'lettuce':'Romaine','bean':'Soybean'}
MK={'침수ETc':'s','ETc50':'o','침수ETc50':'s'}; FIL={'침수ETc':True,'ETc50':False,'침수ETc50':False}; LS={'침수ETc':(0,(4,1.6)),'ETc50':'-','침수ETc50':(0,(4,1.6))}
NAME={'침수ETc':'Waterlogging','ETc50':'Drought','침수ETc50':'Combined'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.8,'legend.frameon':False})
x=load_li600(); x=x[(x.Qamb>0)].dropna(subset=['Tair']).copy(); c='gsw_해석용(0 이하 제외)'
x['cell']=x['날짜'].astype(str)+'_'+x['처리']
for crop in ['bean','lettuce']:
    k=x.작물==crop; d=x[k].dropna(subset=[c]); m=smf.ols(f'Q("{c}") ~ C(cell) + Qamb + Tair',d).fit()
    x.loc[k,'adj']=x.loc[k,c]+m.params['Qamb']*(d.Qamb.mean()-x.loc[k,'Qamb'])+m.params['Tair']*(d.Tair.mean()-x.loc[k,'Tair'])
res={}
for crop in ['bean','lettuce']:
    r=[]; s=x[x.작물==crop]
    for dat,g in s.groupby('DAT'):
        ctl=g[g.처리=='ETc'].adj.dropna()
        for t in ['침수ETc','ETc50','침수ETc50']:
            a=g[g.처리==t].adj.dropna()
            if len(a)>1 and len(ctl)>1:
                r.append(dict(DAT=dat,처리=t,ratio=a.mean()/ctl.mean()*100,p=stats.ttest_ind(ctl,a,equal_var=False).pvalue))
    r=pd.DataFrame(r)
    for t,gg in r.groupby('처리'):
        r.loc[gg.index,'pH']=multipletests(gg.p,method='holm')[1]
    res[crop]=r; r.to_csv(f'intermediate/recovery3_{crop}.csv',index=False)
fig,axs=plt.subplots(1,2,figsize=(7.7,3.5),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
for ax,crop in zip(axs,['bean','lettuce']):
    r=res[crop]; ax.axvspan(0,3,color='#E6E6E6',lw=0); ax.axhline(100,color='0.45',lw=0.8,ls='--')
    for t in ['침수ETc','ETc50','침수ETc50']:
        g=r[r.처리==t].sort_values('DAT'); col=CROPC[crop][t]
        if crop=='bean' and t=='침수ETc':
            e=g.DAT<=9
            ax.plot(g.DAT[e],g.ratio[e],color=col,ls=LS[t],lw=1.5,marker='s',ms=4.2,mfc=col,mec=col)
            ax.plot([9,17],[g[g.DAT==9].ratio.iloc[0],g[g.DAT==17].ratio.iloc[0]],':',color=col,lw=1.2)
            ax.plot(g.DAT[~e],g.ratio[~e],color=col,ls=LS[t],lw=1.5,marker='s',ms=4.2,mfc=col,mec=col)
        else:
            ax.plot(g.DAT,g.ratio,color=col,ls=LS[t],lw=1.5,marker=MK[t],ms=4.2,mfc=col if FIL[t] else 'white',mec=col,mew=1.1)
        for _,rw in g[g.pH<0.05].iterrows(): ax.text(rw.DAT,rw.ratio-12,'*',ha='center',color=col,fontsize=10,fontweight='bold')
    ax.set_title(CN[crop],loc='left',fontsize=10,fontweight='bold',color=ACC[crop]); ax.set_xlabel('Days after waterlogging start (DAT)')
    ax.set_ylim(0,200 if crop=='bean' else 190)
axs[0].set_ylabel('g$_{sw}$ (% of control)')
axs[0].text(1.5,196,'Water-\nlogging',ha='center',va='top',fontsize=6.5,color='0.35')
b=res['bean']; b9=b[(b.처리=='침수ETc')&(b.DAT==9)].ratio.iloc[0]
axs[0].annotate(f'DAT 9: {b9:.0f}%\n(not recovered)',xy=(9,b9),xytext=(11,8),fontsize=7.5,color=ACC['bean'],arrowprops=dict(arrowstyle='->',color=ACC['bean'],lw=1))
l=res['lettuce']; l6=l[(l.처리=='침수ETc')&(l.DAT==6)].ratio.iloc[0]
axs[1].annotate('Recovered by\nDAT 5–6',xy=(6,l6),xytext=(7.2,150),fontsize=7.5,color=ACC['lettuce'],arrowprops=dict(arrowstyle='->',color=ACC['lettuce'],lw=1))
hs=[tuple(Line2D([],[],color=CROPC[cc][t],lw=1.5,ls=LS[t],marker=MK[t],ms=5,mfc=CROPC[cc][t] if FIL[t] else 'white',mec=CROPC[cc][t]) for cc in ('lettuce','bean')) for t in ['침수ETc','ETc50','침수ETc50']]
from matplotlib.legend_handler import HandlerTuple
fig.legend(hs,[NAME[t] for t in ['침수ETc','ETc50','침수ETc50']],loc='upper center',ncol=3,fontsize=8,handler_map={tuple:HandlerTuple(ndivide=None,pad=0.3)},handlelength=3.2,columnspacing=2)
fig.tight_layout(rect=(0,0,1,0.92)); fig.savefig('figs2/recovery3.png'); plt.close(fig)
for crop in res: print(crop); print(res[crop].pivot(index='DAT',columns='처리',values='ratio').round(0).T.to_string())
