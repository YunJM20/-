import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerTuple
from stats2x2 import tukey_letters
R='/home/user/-/'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.8,'legend.frameon':False,'axes.titlesize':7,'axes.titleweight':'bold'})
ORDER=['ETc','ETc50','침수ETc','침수ETc50']; NAME={'ETc':'Control','ETc50':'Drought','침수ETc':'Waterlogging','침수ETc50':'Combined'}
CROPC={'lettuce':{'ETc':'#1F3D2B','ETc50':'#8FAA91','침수ETc':'#2E7D4F','침수ETc50':'#9FD3A8'},'bean':{'ETc':'#3B2618','ETc50':'#B9A28C','침수ETc':'#8B5A2B','침수ETc50':'#E0B98A'}}
ACC={'lettuce':'#2E6B3F','bean':'#6B4226'}
MK={'ETc':'o','ETc50':'o','침수ETc':'s','침수ETc50':'s'}; FILLED={'ETc':True,'ETc50':False,'침수ETc':True,'침수ETc50':False}
def handle(c,t): return Line2D([],[],color=CROPC[c][t],lw=0,marker=MK[t],ms=5.5,mfc=CROPC[c][t] if FILLED[t] else 'white',mec=CROPC[c][t],mew=1.3)
def legend(fig,y=1.0):
    fig.legend([tuple(handle(c,t) for c in ('lettuce','bean')) for t in ORDER],[NAME[t] for t in ORDER],loc='upper center',bbox_to_anchor=(0.5,y),ncol=4,fontsize=8,handler_map={tuple:HandlerTuple(ndivide=None,pad=0.3)},handlelength=3.2,columnspacing=1.6)
# ---------------- growth
b=pd.read_csv(R+'data/10_생육_밭콩_파괴조사.csv',encoding='utf-8-sig'); b=b.rename(columns={'Treatment':'처리'})
b['지상부FW']=b['지상부FW(잎+줄기)']; b['지상부DW']=b['지상부DW(잎+줄기)']
r=pd.read_csv(R+'로메인data/11_생육_로메인상추.csv',encoding='utf-8-sig'); r=r[r.날짜=='2026-10-23']
VARS=[('SPAD','SPAD','SPAD','SPAD'),('Leaf area (cm$^{2}$·plant$^{-1}$)','엽면적','엽면적','엽면적'),('Leaf number','잎 수','엽수','엽수'),
      ('Shoot fresh wt. (g·plant$^{-1}$)','지상부FW','지상부생체중_전체','지상부생체중_전체'),('Shoot dry wt.* (g·plant$^{-1}$)','지상부DW','지상부건조중_전체','지상부건조중_전체'),
      ('Root dry wt.** (g·plant$^{-1}$)','뿌리 D.W','지하부건조중','지하부건조중')]
groups=[('bean','Bean\n9/1',b[b.날짜=='2026-09-01']),('bean','Bean\n10/6',b[b.날짜=='2026-10-06']),('lettuce','Romaine\n10/23',r)]
fig,axs=plt.subplots(1,6,figsize=(12,3.08),dpi=300)
out=[]
for ax,(title,cb,_,cr) in zip(axs,VARS):
    ymax=0
    for gi,(crop,lab,df) in enumerate(groups):
        col=cb if crop=='bean' else cr
        grp={t:df.loc[df.처리==t,col].dropna() for t in ORDER}
        let,P=tukey_letters(grp)
        for k,t in enumerate(ORDER):
            v=grp[t]; x=gi+(k-1.5)*0.2; m=v.mean(); se=v.sem()
            ax.bar(x,m,0.19,color=CROPC[crop][t]); ax.errorbar(x,m,se,color='0.25',lw=0.7,capsize=1)
            ax.text(x,m+se,let[t],ha='center',va='bottom',fontsize=5.5); ymax=max(ymax,m+se)
            out.append((title,lab.replace('\n',' '),t,round(m,2),let[t],round(P,4)))
    ax.set_ylim(0,ymax*1.18); ax.set_xticks(range(3)); ax.set_xticklabels([g[1] for g in groups],fontsize=5.5)
    ax.tick_params(axis='y',labelsize=7); ax.set_title(title,fontsize=6.5,loc='left')
legend(fig); fig.tight_layout(rect=(0,0,1,0.92),w_pad=0.6); fig.savefig('figures/growth_cmp.png'); plt.close(fig)
pd.DataFrame(out,columns=['var','group','trt','mean','letter','P']).to_csv('intermediate/growth_cmp_values.csv',index=False)
# ---------------- environment
e1=pd.read_csv(R+'data/19_환경_밭콩_일별.csv'); e2=pd.read_csv(R+'로메인data/25_환경_일별.csv')
e1['날짜']=pd.to_datetime(e1['날짜']); e2['날']=pd.to_datetime(e2['날']); print(e2.columns.tolist()); 
miss=[c for c in e2.columns if '결측' in c][0]; e2=e2[~e2[miss].astype(str).str.contains('True|결측|1',na=False)] if e2[miss].dtype==object else e2[e2[miss]==False]
fig,axs=plt.subplots(1,2,figsize=(7.7,2.9),dpi=300)
for ax,(c1,c2,yl) in zip(axs,[('평균기온','평균기온','Mean air temp. (°C)'),('DLI_mol','DLI_추정(mol m-2 d-1)','DLI (mol·m$^{-2}$·day$^{-1}$)')]):
    s=e1[e1.날짜>='2026-08-12']; ax.plot(s.날짜,s[c1],color=ACC['bean'],lw=1.4,label='Soybean')
    t=e2[e2.날>='2026-10-07']; ax.plot(t.날,t[c2],color=ACC['lettuce'],lw=1.4,marker='o',ms=3,label='Romaine')
    ax.axvline(pd.Timestamp('2026-08-12'),color=ACC['bean'],ls=':',lw=0.9); ax.axvline(pd.Timestamp('2026-10-07'),color=ACC['lettuce'],ls=':',lw=0.9)
    import matplotlib.dates as md
    ax.xaxis.set_major_locator(md.MonthLocator()); ax.xaxis.set_major_formatter(md.DateFormatter('%b %d')); ax.set_ylabel(yl); ax.set_xlabel('Date (2026)')
axs[0].legend(loc='lower left',fontsize=8); axs[1].text(0.10,0.98,'dotted: flooding start',transform=axs[1].transAxes,fontsize=7,va='top',color='0.35')
fig.tight_layout(); fig.savefig('figures/env_cmp.png'); plt.close(fig)
print('ok')
