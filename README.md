<p>
  <a href="https://mixedcas-lab.github.io/"><img src="assets/mcaslab.png" alt="MCAS Lab" height="34"></a>
  &nbsp;&nbsp;
  <a href="https://www.uos.ac.kr"><img src="assets/uos.png" alt="University of Seoul" height="20"></a>
</p>

# Circuit Design Automation Census

아날로그·혼성신호(그리고 메모리) **회로 설계 자동화** 논문을 모아 보여주는 사이트입니다. MCAS Lab(서울시립대학교 첨단융합학부)에서 운영합니다.

- 사이트: https://mixedcas-lab.github.io/eda-census/
- 데이터 출처: IEEE Xplore API (서지 메타데이터와 링크만 공개, 초록·본문은 올리지 않음)

## 대상

- **설계자동화 학회·저널 (2012년부터):** DAC, ICCAD, DATE, ASP-DAC, TCAD (IEEE 수집 전까지는 accel-census가 Crossref·OpenAlex에서 받은 기록을 함께 읽음)
- **회로 학회·저널:** ISSCC, VLSI, JSSC, CICC, ESSCIRC/ESSERC, A-SSCC, SSC-L, TCAS-I/II, TVLSI (합성형 회로, 생성기, 자동 레이아웃을 쓴 칩 논문)

논리 합성, FPGA 매핑, 타이밍 분석, 클록 트리 같은 디지털 EDA는 범위 밖입니다.

## 분류

- **core**: 제목에 아날로그·혼성신호·메모리 회로(op-amp, ADC/DAC, PLL, LDO, 비교기, 기준전압, LNA, 필터, SRAM 등)와 설계 자동화 과제(사이징, 토폴로지 합성, 레이아웃 자동화·배치·배선, 합성형/표준셀 기반 회로, 생성기·컴파일러, 수율·변동 인지 설계, LLM 기반 설계 등)가 함께 있는 논문. 최적화·학습 기법(RL, BO, GNN, 진화 알고리즘, gm/ID 등)은 "설계·사이징·최적화" 맥락일 때만 인정합니다(보정·검출에 쓴 경우 제외).
- **related**: 회로 논문인데 초록에서 합성형·자동 생성·자동 레이아웃을 언급한 경우.
- **유형**: ML-based(RL, BO, GNN, LLM, 신경망, 대리 모델) / Conventional.
- **태그**: 과제(사이징/최적화, 토폴로지 합성, 레이아웃 자동화, 합성형/셀 기반, 생성기/컴파일러, 모델링/대리모델, 수율/변동, 검증/테스트), 기법, 대상 회로, 실리콘 검증 여부.
- **수치**: 논문이 주장한 속도 향상(×, 시뮬레이션 횟수 감소 포함), 공정, 면적. 초록에 값이 여럿이면 비워 둡니다. 속도 향상은 논문마다 기준이 달라 서로 비교할 수 없습니다.

## 그래프

연도별 논문 수(과제별, 기법별, ML/Conventional), 연도별 속도 향상, Custom.

## 검수 값 넣기

`data/annotations.csv` 열: `id, exclude, type, task, method, circuit, speedup, node, area, silicon, note, by`. 여러 값은 `;`로 구분하고, `-`는 값 삭제입니다.

## 랩 서버 설정 (1회)

```bash
ssh-keygen -t ed25519 -f ~/.ssh/eda_census -N "" -C "eda-census@lab-server"   # 공개키를 Deploy keys에 쓰기 권한으로 등록
git clone github-eda-census:mixedcas-lab/eda-census.git ~/eda-census
( crontab -l; echo "32 6 * * * PYTHON=$(command -v python3) $HOME/eda-census/scripts/update.sh >> $HOME/eda-census/logs/update.log 2>&1" ) | crontab -
```

GitHub Pages: Settings → Pages에서 Branch를 **main / (root)**로 지정합니다.
