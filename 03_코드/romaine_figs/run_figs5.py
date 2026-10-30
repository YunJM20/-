import pandas as pd, numpy as np
R='/home/user/-/'
a=pd.read_csv(R+'로드셀 CL 데이터.csv',encoding='utf-8-sig'); b=pd.read_csv(R+'로드셀 DL_WL_WDL 데이터.csv',encoding='utf-8-sig')
for d in (a,b): d['t']=pd.to_datetime(d['timestamp'].str.replace(' Asia/Seoul','',regex=False)).dt.floor('h')
HR=pd.concat([a.groupby('t').mean(numeric_only=True),b.groupby('t').mean(numeric_only=True)],axis=1)
HR.index.name='t'; HR.reset_index().assign(시각=lambda z:z.t.dt.strftime('%Y-%m-%d %H')).drop(columns='t').to_csv('intermediate/romaine_loadcell_hourly.csv',index=False)
L=open('07_v13_review.py',encoding='utf-8').read().split('\n')
seg='\n'.join(L[:51])+'\n'+'\n'.join(L[126:157])
seg=seg.replace("h = pd.read_csv(DATA / '36_잎상추_로드셀_시간별무게.csv'); h['t'] = pd.to_datetime(h['시각'])\nh = h[h.t.dt.hour == 5].set_index('t')","h = HR.copy(); h = h[h.index.hour == 5]")
seg=seg.replace("'lettuce': [60, 93, 44]","'lettuce': [43, 56, 37]").replace("['Lettuce', 'Soybean']","['Romaine', 'Soybean']").replace("ax.set_title('Lettuce pot weight')","ax.set_title('Romaine pot weight')")
assert "HR.copy()" in seg and '[43, 56, 37]' in seg
exec(compile(seg,'07_5a','exec'))
print('ok', h.shape, h.index.min(), h.index.max())
print(((h-h.loc['2026-10-07 05:00'])).round(2).loc['2026-10-08 05:00':'2026-10-23 05:00':3])
