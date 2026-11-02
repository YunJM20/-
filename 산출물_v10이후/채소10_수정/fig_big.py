# 축 이름·눈금·P1/P2 등 그래프 글자를 키워 figs7/ 에 다시 저장 (범례는 유지)
import warnings, os, sys, runpy; warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
from matplotlib.figure import Figure
K=1.2; os.makedirs('figs7',exist_ok=True)
_orig=Figure.savefig
def big(fig,fname,*a,**k):
    for ax in fig.axes:
        if ax.get_legend() is not None and not ax.get_xlabel() and not ax.get_ylabel() and not ax.lines and not ax.patches: continue
        for t in [ax.xaxis.label,ax.yaxis.label]+ax.get_xticklabels()+ax.get_yticklabels()+list(ax.texts):
            if not getattr(t,'_big',False): t.set_fontsize(t.get_fontsize()*K); t._big=True
    return _orig(fig,'figs7/'+os.path.basename(str(fname)),*a,**k)
Figure.savefig=big
which=sys.argv[1]
if which=='v22': runpy.run_path('fig_v22.py',run_name='__main__')
if which=='v13': runpy.run_path('fig_v13.py',run_name='__main__')
elif which=='v17': runpy.run_path('fig_v17.py',run_name='__main__')
elif which=='v15': runpy.run_path('fig_v15.py',run_name='__main__')
elif which=='v21': runpy.run_path('fig_v21.py',run_name='__main__')
elif which=='cum':
    import fo_figs as ff; ff.cum()
elif which=='v9':
    import fig_v9 as g; g.phi3(); g.recap3('bean'); g.recap3('lettuce')
