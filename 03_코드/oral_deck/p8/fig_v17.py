import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
import fig_v13 as F
from fo_common import *
f=pd.read_csv('data/03_암적응_FvFm_개별측정.csv'); f=f[~((f.작물=='bean')&(f.날짜=='2026-09-28'))]; f=f[f.DAT>=1].dropna(subset=['Fv/Fm'])
PH=pd.read_csv('intermediate/fvfm_phase.csv')
old=F.stats
def stats(ind,crop,per):
    if ind!='fvfm': return old(ind,crop,per)
    q=PH[(PH.작물==crop)&(PH.구간==per)]; days=[int(x) for x in str(q.포함DAT.iloc[0]).split(',')]
    b=f[(f.작물==crop)&(f.DAT.isin(days))]; P=q.P.iloc[0]
    return {r.처리:(r.원평균,b[b.처리==r.처리]['Fv/Fm'].sem(),r.문자) for r in q.itertuples()},P
F.stats=stats; F.LAB['fvfm']='F$_v$/F$_m$'
import fig_v14 as G  # reuses F.stats (patched) ; its own makes run on import
YL={'abs':{'bean':(0.80,0.85),'lettuce':(0.80,0.85)}}
def build(kind,fname):
    fig,axs=plt.subplots(1,2,figsize=(7.5,2.55),dpi=300,gridspec_kw={'width_ratios':[4.9,6.9]})
    for j,crop in enumerate(['bean','lettuce']):
        (F.panel if kind=='abs' else G.pct_panel)('fvfm',crop,'x') if False else (F.panel(axs[j],'fvfm',crop,True,j==0) if kind=='abs' else G.pct_panel(axs[j],'fvfm',crop,True,j==0))
        ax=axs[j]
        if kind=='abs': ax.set_ylim(0.80,0.85)
        else: ax.set_ylim(95,102)
    if kind=='abs': F.legend_bar(fig,ncol=6,fs=6.6,cs=0.9,hl=1.6)
    else:
        TR=['ETc50','침수ETc','침수ETc50']
        hs=[(tuple(Patch(color=CROPC[c][t]) if FILLED[t] else Patch(facecolor='white',edgecolor=CROPC[c][t],lw=1.4,hatch='////' if t=='침수ETc50' else None) for c in ('bean','lettuce')),NAME[t]) for t in TR]
        legend2(fig,E_crops()+hs+[(Line2D([],[],color='0.4',ls='--',lw=1),'Control = 100%')],6,fontsize=6.6,hl=1.6,cs=0.9)
    fig.subplots_adjust(left=0.09,right=0.99,top=0.86,bottom=0.25,wspace=0.22); fig.savefig('figs6/'+fname); plt.close(fig)
build('abs','bars_fvfm.png'); build('pct','pct_fvfm.png')
