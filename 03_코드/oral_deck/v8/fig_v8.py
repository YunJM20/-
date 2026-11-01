import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import fo_common as fc, fo_figs as ff
pts=pd.read_csv('intermediate/li600_fluor_points.csv')
fc.PRE=pts[pts.단계=='처리 전'].copy(); fc.PRECOL.update({'npq':'NPQ','phino':'PhiNO','phinpq':'PhiNPQ'})
fc.ts_fig2('gsw','g$_{sw}$ (mol·m$^{-2}$·s$^{-1}$)','ts_gsw_w.png',size=(7.5,2.75))
fc.ts_fig2('phinpq','Φ$_{NPQ}$','ts_phinpq_w.png',size=(7.5,2.75)); fc.ts_fig2('phino','Φ$_{NO}$','ts_phino_w.png',size=(7.5,2.75))
ff.rec(size=(7.7,3.0),fname='recovery_w.png'); ff.recap('bean'); ff.recap('lettuce'); print('ok')
