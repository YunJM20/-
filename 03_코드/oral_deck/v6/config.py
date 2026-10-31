"""경로 설정(경로 독립형). 입력 CSV는 이 폴더와 같은 위치의 data\ 폴더에 둡니다(또는 환경변수 ROM_DATA)."""
from pathlib import Path

import os
CODE = Path(__file__).resolve().parent
# 이 폴더(analysis)와 같은 위치에 data\ 폴더(분석 입력 CSV)를 둔다. 다른 위치면 환경변수 ROM_DATA 로 지정.
DATA = Path(os.environ.get("ROM_DATA", CODE.parent / "data"))
RAW_BEAN_DARK_1016 = None      # 밭콩 전용 (로메인 분석에서는 사용하지 않음)

INTER = CODE / 'intermediate'                    # 계산 중간 산출물 (CSV)
FIG = CODE / 'figures'                           # 그래프 PNG
INTER.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

ORDER = ['ETc', 'ETc50', '침수ETc', '침수ETc50']   # CSV 안의 처리 코드 (대조구, 건조, 침수, 복합)

# LI-600 흐린 날 처리: 모든 측정일을 포함하고, 통계에서 선형 PAR(Qamb)과 기온(Tair)을 공변량으로 보정한다.
# 맑음지수(CI, data/01)는 그림에 흐린 날(CI < 0.5)을 표시하는 데만 쓴다.
CI_CLOUDY = 0.5
PHASE_END = {'bean': 10, 'lettuce': 10}   # P1 = DAT 1 ~ 침수 종료 후 7일, P2 = 그 이후
# 국면 비교는 해당 국면에서 모든 처리가 측정된 날만 사용 (콩 P1은 대조·침수 2처리만 측정)


def load_li600():
    """02_LI600_개별측정.csv 전체(흐린 날 포함) + 맑음지수 CI 열."""
    import pandas as pd
    x = pd.read_csv(DATA / '02_LI600_개별측정.csv')
    ci = pd.read_csv(DATA / '01_흐린날_판정_CI.csv', encoding='utf-8-sig')
    ci['작물'] = ci['작물(bean/let)'].replace({'let': 'lettuce'})
    x = x.merge(ci[['작물', '날짜', '맑음지수CI']].rename(columns={'맑음지수CI': 'CI'}), on=['작물', '날짜'], how='left')
    x['흐림'] = x['CI'] < CI_CLOUDY
    if 'Tair' not in x.columns:    # 입력 CSV에 이미 Tair(=LI-600 Tref)가 있으면 그대로 사용 (로메인은 원출력 행에서 직접 읽어 넣는다)
        raise ValueError('입력 CSV에 Tair 열(LI-600 Tref)이 필요합니다. 40_LI600_개별측정_Tair포함.csv 형식 참고')
    return x


def common_days(s):
    """국면 자료 s에서 그 국면에 등장한 모든 처리가 측정된 날짜만 남김."""
    trts = set(s['처리'].unique())
    ok = [d for d, g in s.groupby('날짜') if set(g['처리'].unique()) == trts]
    return s[s['날짜'].isin(ok)]
