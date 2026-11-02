import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, os
from fo_common import *
from config import PHASE_END, load_li600, common_days
os.makedirs('figs5',exist_ok=True)
MM=pd.read_csv('intermediate/mm_phase.csv'); GR=pd.read_csv('intermediate/gsw_phase_raw.csv')
COL='gsw_해석용(0 이하 제외)'
x=load_li600(); x=x[x.Qamb>0].dropna(subset=[COL])
SHORT={'ETc':'Ctrl','ETc50':'Dr.','침수ETc':'Wl.','침수ETc50':'Comb.'}
LAB={'gsw':'g$_{sw}$ (mol m$^{-2}$ s$^{-1}$)','phi':'Φ$_{PSII}$','phinpq':'Φ$_{NPQ}$','phino':'Φ$_{NO}$'}
def gsw_stats(crop,per):
    b=x[(x.작물==crop)&(x.DAT>=1)]; b=b[b.DAT<=PHASE_END[crop]] if per=='P1' else b[b.DAT>PHASE_END[crop]]
    b=common_days(b); return {t:(b[b.처리==t][COL].mean(),b[b.처리==t][COL].sem()) for t in ORDER if (b.처리==t).any()}
def stats(ind,crop,per):
    if ind=='gsw':
        s=gsw_stats(crop,per); q=GR[(GR.작물==crop)&(GR.구간==per)]; P=q.P.iloc[0]; let={r.처리:r.문자 for r in q.itertuples()}
        return {t:(m,se,let.get(t,'')) for t,(m,se) in s.items()},P
    q=MM[(MM.지표==ind)&(MM.작물==crop)&(MM.구간==per)]; P=q.처리P.iloc[0]
    return {r.처리:(r.보정평균,r.보정SE,r.문자) for r in q.itertuples()},P
def nbars(crop): return sum(1 for t in ORDER if not MM[(MM.지표=='phi')&(MM.작물==crop)&(MM.구간=='P1')&(MM.처리==t)].empty)+4
def panel(ax,ind,crop,xlab=True,ylab=True):
    xpos=0; ticks=[]; labs=[]; groups=[]; top=0; bounds=[]
    for per in ['P1','P2']:
        st,P=stats(ind,crop,per); start=xpos
        for t in ORDER:
            if t not in st: continue
            m,se,l=st[t]; c=CROPC[crop][t]
            if FILLED[t]: ax.bar(xpos,m,0.78,color=c)
            else: ax.bar(xpos,m,0.78,facecolor='white',edgecolor=c,linewidth=1.5,hatch='////' if t=='침수ETc50' else None)
            ax.errorbar(xpos,m,se,color='#333',capsize=2.5,lw=1)
            top=max(top,m+se); ticks.append(xpos); labs.append(SHORT[t]); xpos+=1
            if P<0.05: ax.text(xpos-1,m+se,l,ha='center',va='bottom',fontsize=7.5)
        groups.append((per,(start+xpos-1)/2)); bounds.append((start,xpos-1)); xpos+=0.9
    mid=(bounds[0][1]+bounds[1][0])/2; ax.axvline(mid,color='0.55',ls=':',lw=1.1,zorder=0)
    ax.set_ylim(0,top*1.22); ax.set_xlim(-0.7,bounds[1][1]+0.7); ax.set_xticks(ticks); ax.set_xticklabels(labs if xlab else [],fontsize=6.5); ax.tick_params(axis='y',labelsize=7)
    if ylab: ax.set_ylabel(LAB[ind],fontsize=9)
    if xlab:
        for per,xc in groups: ax.text(xc,-0.2,per,ha='center',va='top',fontsize=8.5,fontweight='bold',color='0.35',transform=ax.get_xaxis_transform())
def legend_bar(fig,ncol=5,fs=7.2,cs=1.1,hl=2.0):
    hs=[(tuple(Patch(color=CROPC[c][t]) if FILLED[t] else Patch(facecolor='white',edgecolor=CROPC[c][t],lw=1.4,hatch='////' if t=='침수ETc50' else None) for c in ('bean','lettuce')),NAME[t]) for t in ORDER]
    legend2(fig,E_crops()+hs,ncol,fontsize=fs,hl=hl,cs=cs)
def make(inds,size,fname,adjust,lg=dict()):
    r=len(inds); wr=[nbars('bean')-1+0.9,nbars('lettuce')-1+0.9]
    fig,axs=plt.subplots(r,2,figsize=size,dpi=300,gridspec_kw={'width_ratios':wr}); axs=np.atleast_2d(axs)
    for i,ind in enumerate(inds):
        for j,crop in enumerate(['bean','lettuce']): panel(axs[i,j],ind,crop,xlab=(i==r-1),ylab=(j==0))
    legend_bar(fig,**lg); fig.subplots_adjust(**adjust); fig.savefig('figs5/'+fname); plt.close(fig)
if __name__=='__main__':
    make(['gsw'],(7.5,2.55),'bars_gsw.png',dict(left=0.09,right=0.99,top=0.86,bottom=0.25,wspace=0.22),lg=dict(ncol=6,fs=6.6,cs=0.9,hl=1.6))
    make(['phi','phinpq','phino'],(7.2,5.3),'bars_phi3.png',dict(left=0.095,right=0.99,top=0.89,bottom=0.085,hspace=0.2,wspace=0.22))
    print('ok')
