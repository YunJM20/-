# analysis (밭콩·잎상추 v6 분석 코드 사본)

- `config.py` : 경로 독립형으로 수정함. 입력 CSV는 `..\data\` 에 둔다(없으면 환경변수 `ROM_DATA`).
- `stats2x2.py` : **핵심 통계** — `ancova(df, v)`(측정일 + 선형 PAR + 기온 보정 평균·Tukey 문자·처리 P·침수×관수 P), `tukey_letters`, `twoway`. 작물과 무관하게 재사용 가능.
- `00_li600_daily_phase.py` : 측정일별 보정 일평균(`daily_stats.csv`)과 P1/P2 구간 통계(`phase_stats.csv`). 입력 열: 작물, 날짜, DAT, 처리, Time, Qamb, Tair, gsw_해석용(0 이하 제외), PhiPS2, Fs, Fm', ETR, CI(맑음지수), 흐림.
- `03_li600_fluor_params.py` : NPQ·ΦNO 등(선택, 콩은 제외했음).
- `04_make_figures.py` : 그래프 양식(팔레트·마커·범례·시계열·회복 비율·상자그림). **그림 양식의 기준 코드.**
- `07_v13_review.py` : 구간 강건성(블록 검정), ΦPSII 광도 의존 예측, 형광 신호 크기, 상추 생장 손실 환산 등.
- `01·02·05·06_*.py`, `run_all.py` : 밭콩/레드립용 보조 분석(LSP, LI-6800 형광, 생육, 수확량). 필요한 것만 참고.
- 작물 코드는 `'bean'`/`'lettuce'` 문자열로 되어 있다. 로메인을 `'romaine'` 같은 새 코드로 쓰거나, 로메인 단독 분석이면 `'lettuce'` 자리에 넣고 `CROPC`/`ACC`/`CROPN`(04) 색 딕셔너리만 맞춘다.
- `PHASE_END = {'bean': 9, 'lettuce': 10}` : P1 경계(DAT). 로메인은 10.
