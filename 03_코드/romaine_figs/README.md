# 로메인 그림 재생성 (콩 + 로메인 합본)
- `build_data.py` : `data/`(콩)와 `로메인data/`(로메인)를 합쳐 분석 입력 CSV 생성. 로메인은 코드의 `'lettuce'` 자리에 넣음.
- `run_figs.py` : 04_make_figures.py의 시계열(gsw·ΦPSII·Fs·ETR)·회복 비율 그림. `run_figs2.py` : 07_v13_review.py의 ΦPSII 3패널·Fv/Fm+신호크기. `run_figs3.py` : 생육·환경 비교. `run_aq.py` : 로메인 A-Q 곡선(10/18·19 light 파일이 값 없음 → 미사용).
- 실행 전 `00_li600_daily_phase.py`로 `intermediate/daily_stats.csv`를 만들고 `ROM_DATA=<합친 data 폴더>` 환경변수를 지정한다.
- 10/18·10/19 LI-6800 light 파일은 계산 결과가 저장되지 않은 상태라 LibreOffice로 강제 재계산(OOXMLRecalcMode=0)한 뒤 `run_aq.py`로 A-Q 곡선을 그렸다.
