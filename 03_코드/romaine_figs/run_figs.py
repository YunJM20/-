import re
src=open('04_make_figures.py',encoding='utf-8').read()
head=src.split('# ------------------------------------------------------------------ LI-600 NPQ / PhiNO box+strip')[0]
head=head.replace("CROPN = {'lettuce': 'Lettuce'","CROPN = {'lettuce': 'Romaine'")
head=head.replace("A04 = pd.read_csv(L + 'daily_stats.csv')","A04 = pd.read_csv(L + 'daily_stats.csv'); A04 = A04[~((A04.작물 == 'lettuce') & (A04.DAT < 1))]")
head=head.replace("        for d in (7, 8): ax.plot([d], [r[d]], 's', ms=5, mfc='white', mec=c, mew=1.3, zorder=4)\n","")
head=head.replace("ax.annotate('Recovered by\\nDAT 7–8', xy=(8, res['lettuce'][8]), xytext=(3.6, 145)","ax.annotate('Recovered by\\nDAT 5–6', xy=(6, res['lettuce'][6]), xytext=(3.6, 145)")
head=head.replace("['Lettuce', 'Soybean', 'Cloudy (CI<0.5)']","['Romaine', 'Soybean', 'Cloudy (CI<0.5)']")
exec(compile(head,'04_head','exec'))
print('figs ok')
