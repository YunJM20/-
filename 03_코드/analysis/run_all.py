"""00 → 05 → 04 순서로 전부 실행."""
import runpy
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
for name in ['00_li600_daily_phase.py', '01_lsp_nrh_fit.py', '02_li6800_fluor_FoFm.py', '03_li600_fluor_params.py', '05_growth_param_stats.py', '04_make_figures.py', '06_yield.py', '07_v13_review.py']:
    print('==>', name)
    runpy.run_path(str(here / name), run_name='__main__')
