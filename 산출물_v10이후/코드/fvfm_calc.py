import warnings; warnings.filterwarnings('ignore')
import itertools, numpy as np, pandas as pd
from scipy import stats
from scipy.stats import studentized_range
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from patsy import build_design_matrices
from stats2x2 import _letters
ORDER=['ETc','ETc50','침수ETc','침수ETc50']; PH={'bean':10,'lettuce':10}
f=pd.read_csv('data/03_암적응_FvFm_개별측정.csv'); f=f[~((f.작물=='bean')&(f.날짜=='2026-09-28'))]
f=f[f.DAT>=1].dropna(subset=['Fv/Fm']).rename(columns={'Fv/Fm':'y'})
print(f.groupby(['작물','DAT']).처리.nunique().unstack(0).T.to_string())
rows=[]
for crop,g in f.groupby('작물'):
    for dat,d in g.groupby('DAT'):
        trts=[t for t in ORDER if (d.처리==t).any()]; grs=[d[d.처리==t].y for t in trts]
        p=stats.f_oneway(*grs).pvalue if len(grs)>1 else np.nan
        for t,a in zip(trts,grs): rows.append(dict(지표='fvfm',작물=crop,DAT=dat,날짜=d.날짜.iloc[0],흐림=False,CI=1.0,처리=t,평균=a.mean(),SE=a.sem(),n=len(a),p_raw=p))
D=pd.DataFrame(rows)
for crop,g in D.groupby('작물'):
    u=g.drop_duplicates('DAT').dropna(subset=['p_raw']); adj=dict(zip(u.DAT,multipletests(u.p_raw,method='holm')[1])); D.loc[g.index,'당일_ANOVA_P_Holm']=g.DAT.map(adj)
D.to_csv('intermediate/daily_fvfm.csv',index=False)
# ratio to control
for crop,g in f.groupby('작물'):
    r=[]
    for dat,d in g.groupby('DAT'):
        c=d[d.처리=='ETc'].y
        for t in ['침수ETc','ETc50','침수ETc50']:
            a=d[d.처리==t].y
            if len(a)>1 and len(c)>1: r.append(dict(DAT=dat,처리=t,ratio=a.mean()/c.mean()*100,p=stats.ttest_ind(c,a,equal_var=False).pvalue))
    r=pd.DataFrame(r)
    for t,gg in r.groupby('처리'): r.loc[gg.index,'pH']=multipletests(gg.p,method='holm')[1]
    r.to_csv(f'intermediate/recovery_fvfm_{crop}.csv',index=False)
# phase tables (처리 + 측정일 모형, 모든 처리가 측정된 날만)
out=[]
for crop,g in f.groupby('작물'):
    for per in ['P1','P2']:
        s=g[g.DAT<=PH[crop]] if per=='P1' else g[g.DAT>PH[crop]]
        nt=s.groupby('DAT').처리.nunique(); full=nt.max(); days=nt[nt==full].index; s=s[s.DAT.isin(days)]
        trts=[t for t in ORDER if (s.처리==t).any()]; multi=s.날짜.nunique()>1
        m=smf.ols('y ~ C(처리, levels=trts)'+(' + C(날짜)' if multi else ''),s).fit(); dates=sorted(s.날짜.unique())
        X={t:np.asarray(build_design_matrices([m.model.data.orig_exog.design_info],pd.DataFrame({'처리':t,'날짜':dates}))[0]).mean(0) for t in trts}
        b,V=m.params.values,m.cov_params().values; em={t:X[t]@b for t in trts}
        names=[n for n in m.params.index if n.startswith('C(처리')]; Rm=np.zeros((len(names),len(b)))
        for i,n in enumerate(names): Rm[i,list(m.params.index).index(n)]=1
        Pt=float(m.f_test(Rm).pvalue); sig={}
        for a,c in itertools.combinations(trts,2):
            w=X[a]-X[c]; z=abs(w@b)/np.sqrt(w@V@w); sig[(a,c)]=(studentized_range.sf(z*np.sqrt(2),len(trts),m.df_resid) if len(trts)>2 else 2*stats.t.sf(z,m.df_resid))<0.05
        L=_letters(trts,em,sig) if Pt<0.05 else {t:'a' for t in trts}
        for t in trts: out.append(dict(작물=crop,구간=per,처리=t,원평균=s[s.처리==t].y.mean(),문자=L[t],P=Pt,일수=len(days),포함DAT=','.join(str(int(x)) for x in days)))
o=pd.DataFrame(out); o.to_csv('intermediate/fvfm_phase.csv',index=False); print(o.round(4).to_string())
