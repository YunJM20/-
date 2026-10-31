import pandas as pd
R='/home/user/-/'
L=open('07_v13_review.py',encoding='utf-8').read().split('\n')
seg='\n'.join(L[:113])+'\n'+'\n'.join(L[113:126])+'\n'+'\n'.join(L[232:293])
g=pd.read_csv(R+'로메인data/11_생육_로메인상추.csv',encoding='utf-8-sig'); g['날짜']=g['날짜'].astype(str)
g['처리']=g['처리'].map({'ETc':'대조구','ETc50':'건조','침수ETc':'침수','침수ETc50':'복합'}); g.to_csv('intermediate/romaine_growth_kr.csv',index=False)
seg=seg.replace("l = pd.read_csv(DATA / '11_生育_잎상추.csv')".replace('生育','생육'),"l = pd.read_csv('intermediate/romaine_growth_kr.csv')")
seg=seg.replace("cp = pd.read_csv(DATA / '37_잎상추_캐노피_SAM.csv')","cp = pd.read_csv('/home/user/-/로메인data/37_로메인상추_캐노피_SAM.csv')")
seg=seg.replace("'Lettuce'","'Romaine'")
assert 'romaine_growth_kr' in seg and '로메인data/37' in seg
exec(compile(seg,'07_canopy','exec'))
