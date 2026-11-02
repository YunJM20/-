import warnings; warnings.filterwarnings('ignore')
src=open('05_growth_param_stats.py',encoding='utf-8').read()
a=src.index('import warnings'); b=src.index('# ---------------- 생육'); c=src.index('# ---------------- A-Ci·A-Q 파라미터')
exec(compile(src[a:b]+src[c:],'05p','exec'))
s4=open('04_make_figures.py',encoding='utf-8').read()
head=s4.split('# ------------------------------------------------------------------ time series')[0]
mid=s4[s4.index('# ------------------------------------------------------------------ A-Ci / A-Q parameters'):s4.index('# ------------------------------------------------------------------ growth lollipop')]
head=head.replace("CROPN = {'lettuce': 'Lettuce'","CROPN = {'lettuce': 'Romaine'")
exec(compile(head+mid,'04p','exec'))
print('params ok')
