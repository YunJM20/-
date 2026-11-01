import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import fo_common as fc
pts=pd.read_csv('intermediate/li600_fluor_points.csv')
fc.PRE=pts[pts.단계=='처리 전'].copy(); fc.PRECOL.update({'npq':'NPQ','phino':'PhiNO','phinpq':'PhiNPQ'})
fc.ts_fig2('npq','NPQ','ts_npq.png'); fc.ts_fig2('phino','Φ$_{NO}$','ts_phino.png'); fc.ts_fig2('phinpq','Φ$_{NPQ}$','ts_phinpq.png'); print('ok')
