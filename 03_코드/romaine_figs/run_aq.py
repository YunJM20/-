import openpyxl, glob, re, pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
R='/home/user/-/'
rows=[]
for f in sorted(glob.glob(R+'광합성/*light.xlsx')):
    wb=openpyxl.load_workbook(f,data_only=True,read_only=True); ws=wb['Measurements']; Rr=list(ws.iter_rows(values_only=True))
    hdr=[str(x) for x in Rr[14]]; iA=hdr.index('A'); iQ=hdr.index('Qin')
    base=f.split('/')[-1]; date,tm,lab=re.search(r'(\d{4}-\d{2}-\d{2})-(\d{4})_logdata (\S+(?: \d)?) light',base).groups()
    for r in Rr[16:]:
        if r[iA] is None: continue
        rows.append(dict(날짜=date,라벨=lab,Q=round(float(r[iQ]),-1),A=float(r[iA])))
d=pd.DataFrame(rows); d=d[d.Q>=40]
def trt(l,dt):
    if dt=='2026-10-04': return 'pre'
    return {'C':'ETc','D':'ETc50','W':'침수ETc'}[l[0]] if not l.startswith('WD') else '침수ETc50'
d['처리']=[trt(l,dt) for l,dt in zip(d.라벨,d.날짜)]
d['곡선']=d.날짜+d.라벨
Q=sorted(d.Q.unique()); print(Q, d.groupby('처리').곡선.nunique().to_dict())
S=d.groupby(['처리','Q']).A.agg(['mean','sem','count']).reset_index(); S.to_csv('intermediate/romaine_aq_summary.csv',index=False)
minp=[]
for q in Q:
    g=[d[(d.처리==t)&(d.Q==q)].A.values for t in ['ETc','ETc50','침수ETc','침수ETc50']]
    minp.append((q,stats.f_oneway(*g).pvalue))
print('minP',min(minp,key=lambda x:x[1]), [(q,round(p,3)) for q,p in minp])
print(S[S.Q==1500].round(2).to_string())
# figure
GC={'ETc':'#1F3D2B','ETc50':'#8FAA91','침수ETc':'#2E7D4F','침수ETc50':'#9FD3A8'}
MK={'ETc':'o','ETc50':'o','침수ETc':'s','침수ETc50':'s'}; FIL={'ETc':True,'ETc50':False,'침수ETc':True,'침수ETc50':False}
LS={'ETc':'-','ETc50':'-','침수ETc':(0,(4,1.6)),'침수ETc50':(0,(4,1.6))}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.8})
fig,ax=plt.subplots(figsize=(4.3,2.86),dpi=300)
for t in ['pre','ETc','ETc50','침수ETc','침수ETc50']:
    s=S[S.처리==t].sort_values('Q')
    if t=='pre': ax.errorbar(s.Q,s['mean'],s['sem'],color='#9A9A9A',ls='--',marker='x',ms=4,lw=1,capsize=2); continue
    c=GC[t]; ax.fill_between(s.Q,s['mean']-s['sem'],s['mean']+s['sem'],color=c,alpha=0.16,lw=0)
    ax.plot(s.Q,s['mean'],color=c,ls=LS[t],lw=1.5,marker=MK[t],ms=4.2,mfc=c if FIL[t] else 'white',mec=c,mew=1.1)
ax.set_title('Romaine',loc='left',fontsize=11,fontweight='bold',color='#2E6B3F'); ax.set_xlabel('PPFD (µmol·m$^{-2}$·s$^{-1}$)'); ax.set_ylabel('A (µmol·m$^{-2}$·s$^{-1}$)')
ax.set_ylim(bottom=-3); fig.tight_layout(); fig.savefig('figures/aq_romaine.png'); plt.close(fig)
print(d.groupby(['날짜','라벨','처리']).size().to_string())
