import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from fo_common import *
from stats2x2 import tukey_letters
from scipy import stats
b=pd.read_csv(R+'data/54_생육_밭콩_파괴조사_이상값제거.csv',encoding='utf-8-sig').rename(columns={'Treatment':'처리'}); b=b[b.날짜=='2026-10-06']
l=pd.read_csv(R+'로메인data/11_생육_로메인상추.csv',encoding='utf-8-sig'); l=l[l.날짜=='2026-10-23']
SHORT={'ETc':'Ctrl','ETc50':'Dr.','침수ETc':'Wl.','침수ETc50':'Comb.'}
BEAN1=[('초장','Plant height (cm)'),('경장','Stem length (cm)'),('SPAD','SPAD'),('잎 수','Leaf no.'),('분지 수','Branch no.'),('엽면적','Leaf area (cm$^2$)'),
       ('꼬투리 수','Pod no.'),('알 수','Seed no.'),('알 F.W','Seed FW (g)'),('알 D.W','Seed DW (g)'),('꼬투리 F.W','Pod FW (g)'),('꼬투리 D.W','Pod DW (g)')]
BEAN2=[('잎 F.W','Leaf FW (g)'),('잎 D.W','Leaf DW (g)'),('줄기 F.W','Stem FW (g)'),('줄기 D.W','Stem DW (g)'),('지상부FW(잎+줄기)','Shoot FW (g)'),('지상부DW(잎+줄기)','Shoot DW (g)'),('뿌리 D.W','Root DW (g)')]
LET=[('SPAD','SPAD'),('엽장','Leaf length (cm)'),('엽폭','Leaf width (cm)'),('엽수','Leaf no.'),('엽면적','Leaf area (cm$^2$)'),('지상부생체중_전체','Shoot FW (g)'),('지상부건조중_전체','Shoot DW (g)'),('지하부건조중','Root DW (g)'),('LSI','LSI'),('SLA','SLA'),('SR','Shoot/root ratio')]
rows=[]
def panel(ax,df,col,lab,crop):
    vals={t:df.loc[df.처리==t,col].dropna() for t in ORDER}; tops=[]; ms=[]
    for k,t in enumerate(ORDER):
        v=vals[t]; 
        if len(v)==0: continue
        m=v.mean(); se=v.sem() if len(v)>1 else 0; c=CROPC[crop][t]
        if FILLED[t]: ax.bar(k,m,0.78,color=c)
        else: ax.bar(k,m,0.78,facecolor='white',edgecolor=c,linewidth=1.4,hatch='////' if t=='침수ETc50' else None)
        ax.errorbar(k,m,se,color='#333',capsize=2,lw=0.9); tops.append(m+se); ms.append(m)
    ok={t:v for t,v in vals.items() if len(v)>1}
    let,P=tukey_letters(ok) if len(ok)>1 else ({},np.nan)
    sig=P<0.05
    if sig:
        for k,t in enumerate(ORDER):
            if t in let and len(vals[t]): ax.text(k,tops[[x for x in range(4) if len(vals[x and ORDER[x]] if False else vals[ORDER[x]])>0].index(k)]*1.02,let[t],ha='center',va='bottom',fontsize=7.5)
    ax.set_ylim(0,max(tops)*1.22); ax.set_xticks(range(4)); ax.set_xticklabels([SHORT[t] for t in ORDER],fontsize=6.3); ax.set_ylabel(lab,fontsize=7.3); ax.tick_params(axis='y',labelsize=6.5)
    rows.append((crop,col,round(P,4) if P==P else None,'/'.join(str(len(vals[t])) for t in ORDER),'; '.join(f'{SHORT[t]}={vals[t].mean():.3g}' for t in ORDER if len(vals[t]))))
def sheet(df,items,crop,cols,rowsn,fname,size):
    fig,axs=plt.subplots(rowsn,cols,figsize=size,dpi=300); axs=np.atleast_1d(axs).ravel()
    for ax,(c,lab) in zip(axs,items): panel(ax,df,c,lab,crop)
    for ax in axs[len(items):]: ax.axis('off')
    fig.subplots_adjust(left=0.06,right=0.995,top=0.97,bottom=0.07,wspace=0.42,hspace=0.55); fig.savefig('figs4/'+fname); plt.close(fig)
sheet(b,BEAN1,'bean',4,3,'growth_bean1.png',(12.2,4.9)); sheet(b,BEAN2,'bean',4,2,'growth_bean2.png',(12.2,3.6)); sheet(l,LET,'lettuce',4,3,'growth_lettuce.png',(12.2,4.9))
pd.DataFrame(rows,columns=['crop','var','P','n(C/D/W/Cb)','means']).to_csv('intermediate/growth_final_panels.csv',index=False)
print(pd.DataFrame(rows,columns=['crop','var','P','n','means']).to_string())
