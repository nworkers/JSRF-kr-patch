# JSRF-kr-patch 분석 색인

이 디렉터리는 일본판 JSRF `default.xbe`(MD5 `d8490cdb75bd47b36c62effdf1461ae0`)와 `Media`에서 직접 확인한 사실을 주제별로 누적한다. 시간순 작업 증거는 `docs/work-logs/`에 남기고, 여기에는 현재 유효한 결론을 통합한다.

표기 기준:

* **확인됨**: 정적 분석, 바이트 덤프, 왕복 시험, xemu·reJSRF 실행으로 직접 검증
* **추정**: 관측·정황·reJSRF(US판)나 외부 프로젝트의 보고와 일치하지만 일본판에서 더 확인해야 함
* **미확정**: 다음 분석에서 검증해야 할 가설 또는 blocker

주소는 일본판 가상 주소를 먼저 적고 US판 대응 주소와 대응 확인 방법을 함께 적는다.

reJSRF에서 이어받은 사실은 [PLAN.md §3](../PLAN.md)과 reJSRF의 [text-and-font](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/text-and-font.md), [language](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/language.md)에 있다.

## 문서

| 문서 | 내용 | issue |
|---|---|---|
| [text-renderer.md](text-renderer.md) | 텍스트 렌더러: 그리는 함수(일본판·US판 주소), 글리프 순서표 `0x1F7088`과 칸 계산, `jetfont.dat`의 텍스처 6장, `$` 코드, 줄 폭·페이지 크기 제한, `TNRoman.bin`(디버그 글꼴), 한국어 글꼴 방식에 주는 뜻 | #3 |
| [text-files.md](text-files.md) | 문장이 들어 있는 곳: 미션 파일(`mssn####.bin`)의 목표 짝, 대화 이벤트(`TE###.bin`) 문자열, XBE 메뉴 문자열과 `.data` 포인터 표, 일본판의 언어, HDD 캐시, 화면 결과 | #8 |
| [containers.md](containers.md) | `MULT`/`NORM` 컨테이너: 머리, 연결(시작·끝·크기·깃발), 패딩 규칙, 1,056개 파일 왕복, 이벤트 문장 항목의 자리 | #2 |
| [message-script.md](message-script.md) | 메시지 스크립트(이벤트 항목 `2/0`, 대화 이벤트 `TE###.bin`): 머리, 페이지 수, 페이지별 값, 분기 코드의 페이지 번호 인자, 길이가 바뀔 때 다시 계산할 것 | #11 |
| [mission-files.md](mission-files.md) | 미션 파일: 로더와 재배치 함수 `0x4DB30`, 머리 구역 표, 명령 레코드, 문장 명령의 언어별 포인터 7칸, 긴 문장은 파일 끝에 붙이기 | #11 |
| [xbe-strings.md](xbe-strings.md) | XBE `.rdata` 일본어 문자열 651개, `.data` 포인터 칸과 `push` 즉치 참조, 정렬 여백 | #11 |
| [english-mode.md](english-mode.md) | 영어 모드: 언어 값(US판 `0x1FC724`), 미디어의 영어 자리, XBE 언어 표 55개와 특수 3곳(언어 0 칸 695 ↔ 영어 칸), 일본어 문자열의 참조 맥락, 그리기 차이 | #20 |

---

# JSRF-kr-patch analysis index

This directory accumulates, by topic, facts confirmed directly on the Japanese JSRF `default.xbe` (MD5 `d8490cdb75bd47b36c62effdf1461ae0`) and its `Media`. Chronological evidence stays in `docs/work-logs/`; current conclusions are merged here.

Labels:

* **Confirmed**: verified by static analysis, byte dumps, round trips, or runs in xemu or reJSRF
* **Inferred**: consistent with observations, context, or reports from reJSRF (US build) or other projects, but still to be checked on the Japanese build
* **Unresolved**: a hypothesis or blocker for a later analysis

Addresses give the Japanese virtual address first, with the US counterpart and how the match was established.

Facts carried over from reJSRF are in [PLAN.md §3](../PLAN.md) and reJSRF's [text-and-font](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/text-and-font.md) and [language](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/language.md).

## Documents

| Document | Content | Issue |
|---|---|---|
| [text-renderer.md](text-renderer.md) | the text renderer: drawing functions (Japanese and US addresses), the glyph order table `0x1F7088` and cell computation, the six textures in `jetfont.dat`, `$` codes, line-width and page-size limits, `TNRoman.bin` (a debug font), what it means for the Korean font approach | #3 |
| [text-files.md](text-files.md) | where the text lives: objective pairs in mission files (`mssn####.bin`), talk-event (`TE###.bin`) strings, XBE menu strings and their `.data` pointer tables, the Japanese build's language, the HDD cache, screen results | #8 |
| [containers.md](containers.md) | the `MULT`/`NORM` containers: header, links (start, end, size, flag), padding rule, a round trip of 1,056 files, where event text items sit | #2 |
| [message-script.md](message-script.md) | message scripts (event item `2/0`, talk events `TE###.bin`): header, page counts, per-page values, the page-number arguments of branch codes, what to recompute when a length changes | #11 |
| [mission-files.md](mission-files.md) | mission files: loader and the relocation function `0x4DB30`, header section table, command records, the 7 per-language pointer slots of text commands, appending longer strings at the end | #11 |
| [xbe-strings.md](xbe-strings.md) | the 651 Japanese `.rdata` strings of the XBE, their `.data` pointer-slot and `push` references, alignment slack | #11 |
| [english-mode.md](english-mode.md) | English mode: the language value (US `0x1FC724`), English places in Media, 55 XBE language tables and 3 special places (695 language-0 slots ↔ English slots), the reference context of Japanese strings, drawing differences | #20 |
