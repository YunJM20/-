"""Ali et al. 2025 / Gao et al. 2024 방식: PAR·기온 = 양적(선형) 고정 공변량, 측정일 = 임의효과, 처리 = 고정효과(BLUE=보정 평균).
y = μ + 처리 + β1·PAR + β2·T + (측정일 임의절편) + ε"""
import warnings; warnings.filterwarnings('ignore')
import itertools, numpy as np, pandas as pd
from scipy import stats
from scipy.stats import studentized_range
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from config import ORDER, PHASE_END, load_li600, common_days
from stats2x2 import _letters
pts=pd.read_csv('intermediate/li600_fluor_points.csv')
base=load_li600()
x=base.merge(pts[pts.단계=='처리 후'][['작물','날짜','Time','NPQ','PhiNO','PhiNPQ']],on=['작물','날짜','Time'],how='left')
IND={'phi':'PhiPS2','fs':'Fs','etr':'ETR','npq':'NPQ','phino':'PhiNO','phinpq':'PhiNPQ'}
x=x[x.Qamb>0].dropna(subset=['Tair']).copy()
def fit(d,col):
    d=d[['처리','날짜','Qamb','Tair',col]].dropna().rename(columns={col:'y'}).copy()
    trts=[t for t in ORDER if (d.처리==t).any()]
    d['trt']=pd.Categorical(d.처리,categories=trts)
    d['q']=d.Qamb/100.0
    if d.날짜.nunique()>1: m=smf.mixedlm('y ~ C(trt) + q + Tair',d,groups=d['날짜']).fit(reml=True)
    else: m=smf.ols('y ~ C(trt) + q + Tair',d).fit()
    return d,trts,m
def emmeans(d,trts,m):
    names=list(m.params.index) if not hasattr(m,'fe_params') else list(m.fe_params.index)
    b=(m.fe_params if hasattr(m,'fe_params') else m.params); V=(m.cov_params().loc[b.index,b.index]).values; b=b.values; names=list(m.fe_params.index) if hasattr(m,'fe_params') else names
    qb,tb=d.q.mean(),d.Tair.mean(); X={}
    for t in trts:
        v=np.zeros(len(b)); v[names.index('Intercept')]=1
        k=f'C(trt)[T.{t}]'
        if k in names: v[names.index(k)]=1
        v[names.index('q')]=qb; v[names.index('Tair')]=tb; X[t]=v
    return X,b,V,names
def analyse(d,col):
    d,trts,m=fit(d,col); X,b,V,names=emmeans(d,trts,m)
    em={t:X[t]@b for t in trts}; se={t:np.sqrt(X[t]@V@X[t]) for t in trts}
    dfres=max(len(d)-len(trts)-2-d.날짜.nunique()*0,10); sig={}
    for a,c in itertools.combinations(trts,2):
        w=X[a]-X[c]; z=abs(w@b)/np.sqrt(w@V@w)
        sig[(a,c)]=(studentized_range.sf(z*np.sqrt(2),len(trts),dfres) if len(trts)>2 else 2*stats.norm.sf(z))<0.05
    # omnibus Wald chi2 on treatment coefs
    ks=[i for i,n in enumerate(names) if n.startswith('C(trt)')]
    if ks:
        bb=b[ks]; VV=V[np.ix_(ks,ks)]; W=float(bb@np.linalg.solve(VV,bb)); P=float(stats.chi2.sf(W,len(ks)))
    else: P=np.nan
    L=_letters(trts,em,sig) if P<0.05 else {t:'a' for t in trts}
    pb=b[names.index('q')]/100.0; tb=b[names.index('Tair')]
    return [dict(처리=t,보정평균=em[t],보정SE=se[t],n=int((d.처리==t).sum()),원평균=d.loc[d.처리==t,'y'].mean(),문자=L[t],처리P=P) for t in trts],dict(b_PAR=pb,b_T=tb)
out=[];slopes=[]
for crop in ['bean','lettuce']:
    xc=x[(x.작물==crop)&(x.DAT>=1)]
    for per,s in [('P1',xc[xc.DAT<=PHASE_END[crop]]),('P2',xc[xc.DAT>PHASE_END[crop]])]:
        s=common_days(s)
        for ind,col in IND.items():
            r,sl=analyse(s,col)
            for row in r: out.append(dict(지표=ind,작물=crop,구간=per,**row))
            slopes.append(dict(지표=ind,작물=crop,구간=per,**sl))
pd.DataFrame(out).to_csv('intermediate/mm_phase.csv',index=False); pd.DataFrame(slopes).to_csv('intermediate/mm_slopes_phase.csv',index=False)
# ---- daily adjusted series (slopes from the whole post-treatment data of each crop, date random)
rows=[]; gs=[]
for crop in ['bean','lettuce']:
    xc=x[x.작물==crop]
    for ind,col in IND.items():
        d,trts,m=fit(xc,col); b=m.fe_params; pq=b['q']/100.0; pt=b['Tair']
        dd=xc.dropna(subset=[col]).copy(); dd['adj']=dd[col]+(-pq)*(dd.Qamb-dd.Qamb.mean())*1+(-pt)*(dd.Tair-dd.Tair.mean())
        gs.append(dict(지표=ind,작물=crop,b_PAR_per100=pq*100,b_T=pt))
        for (dat,date),g in dd.groupby(['DAT','날짜']):
            tr=[t for t in ORDER if (g.처리==t).any()]; grs=[g.loc[g.처리==t,'adj'] for t in tr]
            p=stats.f_oneway(*grs).pvalue if len(grs)>1 else np.nan
            for t,a in zip(tr,grs): rows.append(dict(지표=ind,작물=crop,DAT=dat,날짜=date,CI=g.CI.iloc[0],흐림=g.흐림.iloc[0],처리=t,평균=a.mean(),SE=a.sem(),n=len(a),p_raw=p))
D=pd.DataFrame(rows)
for (ind,crop),g in D.groupby(['지표','작물']):
    u=g.drop_duplicates('DAT').dropna(subset=['p_raw']); adj=dict(zip(u.DAT,multipletests(u.p_raw,method='holm')[1])); D.loc[g.index,'당일_ANOVA_P_Holm']=g.DAT.map(adj)
D.to_csv('intermediate/daily_mm.csv',index=False); pd.DataFrame(gs).to_csv('intermediate/mm_slopes_all.csv',index=False)
print(pd.DataFrame(gs).round(4).to_string())
