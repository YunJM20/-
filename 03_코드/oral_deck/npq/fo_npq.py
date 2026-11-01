import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
import statsmodels.formula.api as smf
import fo_common as fc
from config import load_li600, ORDER
pts=pd.read_csv('intermediate/li600_fluor_points.csv')
x=load_li600()[['작물','날짜','Time','Qamb','Tair','DAT','처리','CI','흐림']].merge(pts[pts.단계=='처리 후'][['작물','날짜','Time','NPQ','PhiNO','PhiNPQ']],on=['작물','날짜','Time'],how='inner')
x=x[(x.Qamb>0)].dropna(subset=['Tair']).copy(); x['cell']=x['날짜'].astype(str)+'_'+x['처리']
IND={'npq':'NPQ','phino':'PhiNO','phinpq':'PhiNPQ'}
rows=[]
for crop in ['bean','lettuce']:
    xc=x[x.작물==crop]
    for ind,c in IND.items():
        d=xc.dropna(subset=[c]); m=smf.ols(f'Q("{c}") ~ C(cell) + Qamb + Tair',d).fit(); b1,b2=m.params['Qamb'],m.params['Tair']; qb,tb=d.Qamb.mean(),d.Tair.mean()
        adj=d[c]+b1*(qb-d.Qamb)+b2*(tb-d.Tair); dd=d.assign(adj=adj)
        for (dat,date),g in dd.groupby(['DAT','날짜']):
            trts=[t for t in ORDER if (g.처리==t).any()]; grs=[g.loc[g.처리==t,'adj'] for t in trts]
            p=stats.f_oneway(*grs).pvalue if len(grs)>1 else np.nan
            for t,a in zip(trts,grs): rows.append(dict(지표=ind,작물=crop,DAT=dat,날짜=date,CI=g.CI.iloc[0],흐림=g.흐림.iloc[0],처리=t,평균=a.mean(),SE=a.sem(),n=len(a),p_raw=p))
D=pd.DataFrame(rows)
for (ind,crop),g in D.groupby(['지표','작물']):
    u=g.drop_duplicates('DAT').dropna(subset=['p_raw']); adj=dict(zip(u.DAT,multipletests(u.p_raw,method='holm')[1])); D.loc[g.index,'당일_ANOVA_P_Holm']=g.DAT.map(adj)
D.to_csv('intermediate/daily_npq.csv',index=False)
fc.A04=pd.concat([fc.A04,D],ignore_index=True)
pre=pts[pts.단계=='처리 전'].copy(); fc.PRE=pre; fc.PRECOL.update({'npq':'NPQ','phino':'PhiNO','phinpq':'PhiNPQ'})
fc.ts_fig2('npq','NPQ','ts_npq.png'); fc.ts_fig2('phino','Φ$_{NO}$','ts_phino.png'); fc.ts_fig2('phinpq','Φ$_{NPQ}$','ts_phinpq.png'); print('ok')
