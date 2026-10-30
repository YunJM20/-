import pandas as pd, numpy as np, os
R='/home/user/-/'; D=R+'data/'; M=R+'로메인data/'; O=os.path.dirname(os.path.abspath(__file__))+'/data/'
rd=lambda p: pd.read_csv(p,encoding='utf-8-sig')
# 02 main LI-600
b=rd(D+'40_LI600_개별측정_Tair포함.csv'); b=b[b.작물=='bean'].rename(columns={'Tair(Tref, °C)':'Tair'})
r=rd(M+'40_LI600_개별측정_Tair포함.csv'); r=r.rename(columns={'Tair(Tref, °C)':'Tair'})
rm=r[r.DAT>=1].copy(); rm['작물']='lettuce'; rm['제외(흐림)']=False
main=pd.concat([b,rm.drop(columns=['흐림'])],ignore_index=True); main.to_csv(O+'02_LI600_개별측정.csv',index=False)
# 02b pre
bp=rd(D+'02b_LI600_처리전_개별측정.csv'); bp=bp[bp.작물=='bean']
rp=r[r.DAT<1].copy(); rp['작물']='lettuce'
rp=rp.rename(columns={'gsw_보정(mol m-2 s-1)':'gsw_보정','gsw_해석용(0 이하 제외)':'gsw_해석용'})
pre=pd.concat([bp,rp.reindex(columns=bp.columns)],ignore_index=True); pre.to_csv(O+'02b_LI600_처리전_개별측정.csv',index=False)
print('pre rows romaine',len(rp),rp['처리'].unique(),rp['날짜'].unique())
# 01 CI
c=rd(D+'01_흐린날_판정_CI.csv'); cb=c[c['작물(bean/let)']=='bean']
cr=rd(M+'01_흐린날_판정_CI.csv'); print(cr.columns.tolist())
cr2=pd.DataFrame({'작물(bean/let)':'let','날짜':cr['날짜'],'측정시작':cr['측정시작'],'측정끝':cr['측정끝'],'측정구간 평균SW(W m-2)':cr['측정구간 평균SW(W m-2)'],'기준SW(±10일 90분위수)':cr['기준SW(±10일 90분위수)'],'SW 자료수':cr['SW 자료수'],'맑음지수CI':cr['맑음지수CI']})
pd.concat([cb,cr2],ignore_index=True).to_csv(O+'01_흐린날_판정_CI.csv',index=False,encoding='utf-8-sig')
# 03 FvFm
f=rd(D+'03_암적응_FvFm_개별측정.csv'); fb=f[f.작물=='bean']
fr=rd(M+'03_암적응_FvFm_개별측정.csv'); fr['작물']='lettuce'
pd.concat([fb,fr.reindex(columns=fb.columns)],ignore_index=True).to_csv(O+'03_암적응_FvFm_개별측정.csv',index=False)
print(main.groupby('작물').날짜.agg(['min','max','nunique']))
print(main.날짜.dtype, rm.날짜.head(2).tolist(), b.날짜.head(2).tolist())
