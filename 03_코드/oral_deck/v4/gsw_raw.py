"""gsw 보정 이전(PAR·기온 보정 없음, 측정 데이터의 보정gsw) 통계: 일별·구간별·회복비."""
import warnings; warnings.filterwarnings('ignore')
import itertools, numpy as np, pandas as pd
from scipy import stats
from scipy.stats import studentized_range
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from patsy import build_design_matrices
from config import INTER, ORDER, PHASE_END, load_li600, common_days
from stats2x2 import _letters
COL='gsw_해석용(0 이하 제외)'
x=load_li600(); x=x[x.Qamb>0].dropna(subset=[COL]).copy()
# ---- daily
dl=pd.read_csv('intermediate/daily_stats.csv'); dl=dl[dl.지표=='gsw'].copy()
new=[]
for (crop,dat),g in x.groupby(['작물','DAT']):
    trts=[t for t in ORDER if (g.처리==t).any()]; grs=[g.loc[g.처리==t,COL] for t in trts]
    p=stats.f_oneway(*grs).pvalue if len(grs)>1 else np.nan
    new.append((crop,dat,p))
P=pd.DataFrame(new,columns=['작물','DAT','p_raw'])
for crop,gg in P.groupby('작물'):
    u=gg.dropna(subset=['p_raw']); adj=dict(zip(u.DAT,multipletests(u.p_raw,method='holm')[1])); P.loc[gg.index,'ph']=gg.DAT.map(adj)
dl=dl.merge(P,on=['작물','DAT'],how='left')
dl['평균']=dl['원평균']; dl['SE']=dl['원SE']; dl['당일_ANOVA_P_Holm']=dl['ph']
dl.to_csv('intermediate/daily_gsw_raw.csv',index=False)
# ---- recovery ratio (raw)
for crop in ['bean','lettuce']:
    r=[]; s=x[x.작물==crop]
    for dat,g in s.groupby('DAT'):
        ctl=g[g.처리=='ETc'][COL]
        for t in ['침수ETc','ETc50','침수ETc50']:
            a=g[g.처리==t][COL]
            if len(a)>1 and len(ctl)>1: r.append(dict(DAT=dat,처리=t,ratio=a.mean()/ctl.mean()*100,p=stats.ttest_ind(ctl,a,equal_var=False).pvalue))
    r=pd.DataFrame(r)
    for t,gg in r.groupby('처리'): r.loc[gg.index,'pH']=multipletests(gg.p,method='holm')[1]
    r.to_csv(f'intermediate/recovery_raw_{crop}.csv',index=False)
    print(crop); print(r.pivot(index='DAT',columns='처리',values='ratio').round(0).T.to_string())
# ---- phase (no PAR/Tair covariates; 측정일 블록)
out=[]
for crop in ['bean','lettuce']:
    base=x[(x.작물==crop)&(x.DAT>=1)]
    for per,s in [('P1',base[base.DAT<=PHASE_END[crop]]),('P2',base[base.DAT>PHASE_END[crop]])]:
        s=common_days(s); d=s[['처리','날짜',COL]].dropna().rename(columns={COL:'y'})
        trts=[t for t in ORDER if (d.처리==t).any()]; multi=d.날짜.nunique()>1
        m=smf.ols('y ~ C(처리, levels=trts)'+(' + C(날짜)' if multi else ''),d).fit()
        dates=sorted(d.날짜.unique())
        X={t:np.asarray(build_design_matrices([m.model.data.orig_exog.design_info],pd.DataFrame({'처리':t,'날짜':dates}))[0]).mean(0) for t in trts}
        b,V=m.params.values,m.cov_params().values; em={t:X[t]@b for t in trts}; se={t:np.sqrt(X[t]@V@X[t]) for t in trts}
        names=[n for n in m.params.index if n.startswith('C(처리')]; R=np.zeros((len(names),len(b)))
        for i,n in enumerate(names): R[i,list(m.params.index).index(n)]=1
        Pt=float(m.f_test(R).pvalue); sig={}
        for a_,b_ in itertools.combinations(trts,2):
            c=X[a_]-X[b_]; t_=abs(c@b)/np.sqrt(c@V@c)
            sig[(a_,b_)]=(studentized_range.sf(t_*np.sqrt(2),len(trts),m.df_resid) if len(trts)>2 else 2*stats.t.sf(t_,m.df_resid))<0.05
        L=_letters(trts,em,sig) if Pt<0.05 else {t:'a' for t in trts}
        for t in trts: out.append(dict(작물=crop,구간=per,처리=t,평균=em[t],SE=se[t],원평균=d.loc[d.처리==t,'y'].mean(),n=int((d.처리==t).sum()),문자=L[t],P=Pt))
o=pd.DataFrame(out); o.to_csv('intermediate/gsw_phase_raw.csv',index=False); print(o.round(3).to_string())
