import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from fo_common import *
from config import PHASE_END, load_li600, common_days
MM=pd.read_csv('intermediate/mm_phase.csv'); GR=pd.read_csv('intermediate/gsw_phase_raw.csv')
COL='gsw_해석용(0 이하 제외)'
x=load_li600(); x=x[x.Qamb>0].dropna(subset=[COL])
def gsw_stats(crop,per):
    b=x[(x.작물==crop)&(x.DAT>=1)]; b=b[b.DAT<=PHASE_END[crop]] if per=='P1' else b[b.DAT>PHASE_END[crop]]
    b=common_days(b); out={}
    for t in ORDER:
        v=b[b.처리==t][COL].dropna()
        if len(v): out[t]=(v.mean(),v.sem())
    return out
SHORT={'ETc':'Ctrl','ETc50':'Dr.','침수ETc':'Wl.','침수ETc50':'Comb.'}
IND=[('gsw','g$_{sw}$ (mol m$^{-2}$ s$^{-1}$)'),('phi','Φ$_{PSII}$'),('phinpq','Φ$_{NPQ}$'),('phino','Φ$_{NO}$')]
def stats(ind,crop,per):
    if ind=='gsw':
        s=gsw_stats(crop,per); q=GR[(GR.작물==crop)&(GR.구간==per)]; P=q.P.iloc[0]; let={r.처리:r.문자 for r in q.itertuples()}
        return {t:(m,se,let.get(t,'')) for t,(m,se) in s.items()},P
    q=MM[(MM.지표==ind)&(MM.작물==crop)&(MM.구간==per)]; P=q.처리P.iloc[0]
    return {r.처리:(r.보정평균,r.보정SE,r.문자) for r in q.itertuples()},P
fig,axs=plt.subplots(2,4,figsize=(12.2,5.0),dpi=300)
for i,crop in enumerate(['bean','lettuce']):
    for j,(ind,lab) in enumerate(IND):
        ax=axs[i,j]; xpos=0; ticks=[]; labs=[]; groups=[]; top=0
        for per in ['P1','P2']:
            st,P=stats(ind,crop,per); start=xpos
            for t in ORDER:
                if t not in st: continue
                m,se,l=st[t]; c=CROPC[crop][t]
                if FILLED[t]: ax.bar(xpos,m,0.78,color=c)
                else: ax.bar(xpos,m,0.78,facecolor='white',edgecolor=c,linewidth=1.5,hatch='////' if t=='침수ETc50' else None)
                ax.errorbar(xpos,m,se,color='#333',capsize=2.5,lw=1)
                if P<0.05: ax.text(xpos,m+se+0.01*1,l,ha='center',va='bottom',fontsize=7.5)
                top=max(top,m+se); ticks.append(xpos); labs.append(SHORT[t]); xpos+=1
            groups.append((per,(start+xpos-1)/2)); xpos+=0.8
        ax.set_ylim(0,top*1.2); ax.set_xticks(ticks); ax.set_xticklabels(labs,fontsize=6.3); ax.set_ylabel(lab,fontsize=8.5); ax.tick_params(axis='y',labelsize=7)
        for per,xc in groups: ax.text(xc,-0.17,per,ha='center',va='top',fontsize=8.5,fontweight='bold',color='0.35',transform=ax.get_xaxis_transform())
fig.legend([Patch(color=ACC['bean']),Patch(color=ACC['lettuce'])],['Soybean (top)','Lettuce (bottom)'],loc='upper center',ncol=2,fontsize=9,frameon=False,handlelength=1.6,columnspacing=2.5)
fig.subplots_adjust(left=0.06,right=0.995,top=0.93,bottom=0.12,wspace=0.32,hspace=0.45)
fig.savefig('figs4/bars_period.png'); print('ok')
