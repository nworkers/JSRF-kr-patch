# 작업 로그: 문장 형식 분석과 추출 (issue #11, P5-1)

설계: [20261021-i011](../design/20261021-i011-text-extract.md), 작업 지시: [20261021-i011](../work-orders/20261021-i011-text-extract.md), 브랜치 `i011-text-extract`.

입력: 일본판 덤프 `roms/Jet Set Radio Future`(`default.xbe` MD5 `d8490cdb75bd47b36c62effdf1461ae0`), US판 `default_eng.xbe`(MD5 `f4e366bfdceee551a09f42219c90d84e`, 코드 대응 확인용).

## 1. 결과

* 화면 문장이 있는 네 곳의 형식을 확인했고, 문장 길이가 바뀔 때 다시 계산할 것을 정리했다([설계 §2](../design/20261021-i011-text-extract.md), 분석 [message-script](../analysis/message-script.md), [mission-files](../analysis/mission-files.md), [xbe-strings](../analysis/xbe-strings.md)).
* `tools/extract_text.py`가 덤프에서 **문장 단위 2,276개**를 자리·SHA-1과 함께 `work/text/`에 쓰고, 원문 없는 번역 뼈대를 만든다. 모든 자리를 패치 도구의 자리 해석으로 다시 읽어 확인한다.
* 사용자 요구(2026-10-21): 패치를 AI 없이 가이드와 도구만으로 끝까지 만들 수 있어야 한다. 단계별 가이드 [guides/text-pipeline.md](../guides/text-pipeline.md)를 쓰고 `AGENTS.md` 문서 규칙에 더했다.

| 묶음 | 파일 | 레코드 | 단위 | 바이트 | 뺀 것 |
|---|---|---|---|---|---|
| `event` | 117 | 117 메시지 스크립트 | 397 페이지 | 18,867 | 139(`$e` 페이지 등) |
| `talk` | 251 | 251 메시지 스크립트 | 733 페이지 | 32,038 | 429(분기·선택지·`$e` 페이지) |
| `mission` | 196 | 674 문장 명령 | 495 문자열 | 34,234 | 179(빈 문자열, `$r$e$r`만 있는 것) |
| `xbe` | 1 | 651 문자열 | 651 문자열 | 14,189 | 0 |

## 2. 한 일

1. 조사(임시 스크립트, 스크래치 폴더): `e###.dat` 항목 `2/0`의 머리, `TE###.bin`, 미션 파일 머리와 레코드, XBE `.rdata`·`.data`·`.text` 참조, 그 밖의 `Media` 전체에서 가나 연속 검색. 디스어셈블리는 capstone 5.0.7(BSD-3)로 임시 스크립트에서만 읽었다(저장소 코드는 표준 라이브러리만).
2. 미션 파일을 읽는 코드: 경로 형식 문자열 `0x1C753C`의 참조 `0x3055A` → 로더 `0x25DD0`, 재배치 `0x4DB30`과 점프 표 다섯 개. US판과 같은 주소 바이트 비교(`renderer_compare.compare_code`)로 대응 확인.
3. 모듈: `tools/jsrfkr/msgscript.py`, `mission.py`, `xbetext.py`, `extract.py`. 명령줄 `tools/extract_text.py`.
4. `textpatch.py`: 빈 `korean` 건너뛰기(`translated`), 자리 해석 `locate`, 원문 검사 `check_original`(제자리 교체와 같은 검사 `_check`를 함께 씀). `patch.py`가 미번역 줄 수를 알린다.
5. 단위 시험 `tests/test_msgscript.py`, `test_mission.py`, `test_xbetext.py`, `test_textpatch.py`(빈 `korean`, `check_original`).
6. 문서: 분석 세 개 새로, `text-files.md`·`containers.md`의 미확정 해소, 분석 색인, 가이드 `text-pipeline.md`(+ `apply-patch.md`, `docs/README.md` 링크), `AGENTS.md`, `patch/text/README.md`, 설계 i002 §3.1, `tools/README.md`, PLAN P5 줄, `handoff-rejsrf.md` P5-1 절.

## 3. 검증

| 항목 | 결과 |
|---|---|
| 단위 시험 `python -I -m unittest discover -s tests` | 27개 통과(게임 자료 없음) |
| 메시지 스크립트 왕복 | 이벤트 117 + 대화 251 = 368개 모두 `build(parse(x)) == x`(추출 도구가 매번 검사) |
| 미션 포인터 | 248개 파일, 문장 명령 674개, 포인터 4,718개 모두 NUL 바로 뒤의 문자열 시작. 0인 포인터 없음, 공유 없음 |
| 자체 검사 | 단위 2,276개 모두 `textpatch.check_original` 통과 |
| 빈 뼈대로 `patch.py --text work/text/skeleton --link` | `2276 untranslated rows`, `md5.txt`가 기본 출력(`patch/text` 빈 상태)과 같다: `default.xbe` `a60c6cf0a6508d54148a9d32f78f3375`, `jetfont.dat` `524ad3a1144e68056e4d221074cb4efc` |
| 뼈대에 P4 시험 문장 7줄을 채워 `patch.py` | 7곳 모두 뼈대의 자리·길이·해시와 `patch/poc/lines.tsv`가 같다. 출력이 [작업 로그 i008](20261020-i008-poc.md) §3과 같다: `default.xbe` `cbb44a1188af507cc37b4234e5d9b09e`, `jetfont.dat` `fd1400c59e888b241901b8a5c97d10b4`, `mssn0110.bin` `8062445d8f0eba37515b4a1f42056b12`, `TE014.bin` `20a502fe1ec2071a5edacecf757e9ce4` |
| 2,933개와 비교 | 정규식 규칙 재계산: 이벤트 134, 대화 5, 미션 `.bin` 2,776, `.dat` 18 = 2,933(같음). 비교할 수: 이벤트 스크립트 117 = 진짜 레코드 117, 미션 칸 0 `$e` 문자열 406 = 정규식의 칸 0 레코드 406 |
| 재현성 | 두 번 실행한 `work/text/` 파일 9개의 MD5가 같다 |
| 가이드 명령 그대로 | `cp -n` 뼈대 → `--update-manifest`(`0 added`) → `patch.py out/jsrf-kr-guide --link` → §3.1 확인. 모두 가이드에 적힌 결과. 시험 뒤 `patch/text/`의 복사본과 `out/`을 지웠다 |
| `check_roundtrip.py` | `MULT`/`NORM` 1,056/1,056, XBE 요약값 왕복 같음(바뀐 코드가 영향 없음) |
| `git status` | `roms/`, `out/`, `work/` 없음 |

## 4. 계획과 달라진 것

* 사용자 요구로 가이드(`text-pipeline.md`)와 `AGENTS.md` 규칙을 범위에 더했다(설계 §3.6, 작업 지시 10).
* `textpatch`에 빈 `korean` 건너뛰기만이 아니라 자리 해석 함수(`locate`, `check_original`)를 더했다. 추출 도구가 같은 해석으로 자기 출력을 검사하게 하려는 것이다.
* 미션 포인터 검사에 "NUL 바로 뒤" 조건을 더했다(조사에서 4,718개 모두 성립).
* `--update-manifest`는 내용이 같아도 `manifest.json`을 LF로 다시 쓴다. Git `autocrlf` 작업 사본에서는 `git status`에 바뀐 것으로 보이지만 `git diff`는 비어 있다(가이드 시험 뒤 되돌렸다). 고치지 않았다.

## 5. 새로 안 사실

* 이벤트 항목 `2/0`과 대화 이벤트는 같은 메시지 스크립트 형식이다. 게임은 머리의 페이지 수로 문장을 나누므로 NUL이 필요 없다(P1 추정을 대신함).
* 대화 이벤트의 `0x01`·`0x00` 바이트는 `$bc` `$bj` `$bo`의 2진 인자다. 분기 인자는 페이지 번호로 보인다(추정).
* 미션 파일의 오프셋은 모두 파일 위치이고 `0x4DB30`이 읽은 뒤 주소로 바꾼다. 로더가 파일 크기만큼 할당하므로 긴 문장은 파일 끝에 붙일 수 있다. 미션 문장의 "일본어 NUL 영어 NUL 짝"은 칸 0·칸 1 문자열이 이어서 놓인 것이다.
* XBE의 화면 문장은 `.rdata`에만 있다(`.data`의 후보는 글리프 표 항목과 float 자료). `push` 즉치 23곳이 문자열을 직접 가리킨다.
* 네 곳 밖의 `Media`에 화면 문장이 없다(`Effect/ptcl*.dat`의 가나는 개발자 경로).

## 6. 다음

* P5 재삽입 issue: 길이가 바뀌는 문장(설계 §4). 메시지 스크립트 페이지 나누기 규칙, 미션 파일 끝 붙이기, XBE 새 섹션과 참조 수정, 줄 폭·페이지 길이 경고, 원문 그대로 넣은 왕복. 화면 확인(분기 인자, 커진 미션 파일, HDD 캐시). 가이드 §4 갱신.
* P6 시작 때 뼈대를 `patch/text/`에 넣는다.

---

# Work log: text-format analysis and extraction (issue #11, P5-1)

Design: [20261021-i011](../design/20261021-i011-text-extract.md); work order: [20261021-i011](../work-orders/20261021-i011-text-extract.md); branch `i011-text-extract`.

Inputs: the Japanese dump `roms/Jet Set Radio Future` (`default.xbe` MD5 `d8490cdb75bd47b36c62effdf1461ae0`) and the US `default_eng.xbe` (MD5 `f4e366bfdceee551a09f42219c90d84e`, for matching code).

## 1. Result

* The formats of the four places holding on-screen text are confirmed, with what to recompute when a length changes ([design §2](../design/20261021-i011-text-extract.md); analyses [message-script](../analysis/message-script.md), [mission-files](../analysis/mission-files.md), [xbe-strings](../analysis/xbe-strings.md)).
* `tools/extract_text.py` writes **2,276 text units** of the dump, with places and SHA-1s, to `work/text/` and builds a translation skeleton without original text; every place is read back through the patcher's place resolution.
* User requirement (2026-10-21): the patch must be completable without AI, with the guides and tools alone. The step-by-step guide [guides/text-pipeline.md](../guides/text-pipeline.md) was written and the rule added to the documentation rules of `AGENTS.md`.

| Group | Files | Records | Units | Bytes | Left out |
|---|---|---|---|---|---|
| `event` | 117 | 117 message scripts | 397 pages | 18,867 | 139 (`$e` pages and the like) |
| `talk` | 251 | 251 message scripts | 733 pages | 32,038 | 429 (branch, choice and `$e` pages) |
| `mission` | 196 | 674 text commands | 495 strings | 34,234 | 179 (empty, or only `$r$e$r`) |
| `xbe` | 1 | 651 strings | 651 strings | 14,189 | 0 |

## 2. Done

1. Investigation (temporary scripts in the scratch folder): the header of `e###.dat` item `2/0`, `TE###.bin`, mission headers and records, XBE `.rdata`/`.data`/`.text` references, and a search for kana runs in all other `Media`. Disassembly was read with capstone 5.0.7 (BSD-3) in temporary scripts only (repository code uses the standard library only).
2. The code reading mission files: the path format string `0x1C753C`, its reference `0x3055A` → loader `0x25DD0`, relocation `0x4DB30` and its five jump tables; matched to the US build by comparing bytes at the same address (`renderer_compare.compare_code`).
3. Modules `tools/jsrfkr/msgscript.py`, `mission.py`, `xbetext.py`, `extract.py`; the command line `tools/extract_text.py`.
4. `textpatch.py`: skipping empty `korean` (`translated`), place resolution `locate`, the original check `check_original` (sharing `_check` with in-place replacement); `patch.py` reports the untranslated row count.
5. Unit tests `tests/test_msgscript.py`, `test_mission.py`, `test_xbetext.py`, and in `test_textpatch.py` (empty `korean`, `check_original`).
6. Documents: three new analyses, the unresolved items of `text-files.md` and `containers.md` resolved, the analysis index, the guide `text-pipeline.md` (linked from `apply-patch.md` and `docs/README.md`), `AGENTS.md`, `patch/text/README.md`, design i002 §3.1, `tools/README.md`, the PLAN P5 row, the P5-1 section of `handoff-rejsrf.md`.

## 3. Verified

| Item | Result |
|---|---|
| unit tests `python -I -m unittest discover -s tests` | 27 pass (no game data) |
| message-script round trip | all 368 (117 events + 251 talk) satisfy `build(parse(x)) == x` (checked on every extraction run) |
| mission pointers | 248 files, 674 text commands, 4,718 pointers, all at a string start right after a NUL; none 0, none shared |
| self-check | all 2,276 units pass `textpatch.check_original` |
| `patch.py --text work/text/skeleton --link` with the empty skeleton | `2276 untranslated rows`; `md5.txt` equals the default output (empty `patch/text`): `default.xbe` `a60c6cf0a6508d54148a9d32f78f3375`, `jetfont.dat` `524ad3a1144e68056e4d221074cb4efc` |
| the skeleton filled with the seven P4 test lines, through `patch.py` | all seven skeleton places, lengths and hashes equal `patch/poc/lines.tsv`; the output equals [work log i008](20261020-i008-poc.md) §3: `default.xbe` `cbb44a1188af507cc37b4234e5d9b09e`, `jetfont.dat` `fd1400c59e888b241901b8a5c97d10b4`, `mssn0110.bin` `8062445d8f0eba37515b4a1f42056b12`, `TE014.bin` `20a502fe1ec2071a5edacecf757e9ce4` |
| comparison with the 2,933 | the regex rule recounted: events 134, talk 5, mission `.bin` 2,776, `.dat` 18 = 2,933 (equal); comparable numbers: 117 event scripts = 117 real records, 406 slot-0 mission strings with `$e` = the regex's 406 slot-0 records |
| reproducibility | two runs give the same MD5 for all nine `work/text/` files |
| the guide's commands as written | `cp -n` skeletons → `--update-manifest` (`0 added`) → `patch.py out/jsrf-kr-guide --link` → the §3.1 check, all with the results the guide states; the copies in `patch/text/` and the `out/` folders were removed afterwards |
| `check_roundtrip.py` | `MULT`/`NORM` 1,056/1,056 and the XBE digest round trip equal (the changed code has no effect) |
| `git status` | no `roms/`, `out/`, `work/` |

## 4. Deviations from the plan

* At the user's request the guide (`text-pipeline.md`) and the `AGENTS.md` rule joined the scope (design §3.6, work order 10).
* Besides skipping empty `korean`, `textpatch` gained place-resolution functions (`locate`, `check_original`), so the extraction tool checks its own output with the same resolution.
* The mission pointer check gained the "right after a NUL" condition (true for all 4,718 in the survey).
* `--update-manifest` rewrites `manifest.json` with LF even when the content is the same; in a Git `autocrlf` working copy `git status` then lists it as changed while `git diff` is empty (reverted after the guide test); left as it is.

## 5. New findings

* Event item `2/0` and talk events share one message-script format; the game splits the text by the header's page counts, so no NUL is needed (replaces the P1 inference).
* The `0x01`/`0x00` bytes in talk events are binary arguments of `$bc` `$bj` `$bo`; branch arguments look like page numbers (inferred).
* Every offset in a mission file is a file position that `0x4DB30` turns into an address after loading; the loader allocates the file's size, so longer strings can be appended at the end. The "Japanese NUL English NUL pairs" are the slot-0 and slot-1 strings placed one after the other.
* The XBE's on-screen strings are only in `.rdata` (the `.data` candidates are glyph-table entries and float data); 23 `push` immediates point at strings directly.
* No `Media` outside the four places holds on-screen text (the kana in `Effect/ptcl*.dat` are developer paths).

## 6. Next

* The P5 reinsertion issue: text whose length changes (design §4): the message-script page-split rule, appending to mission files, a new XBE section with references fixed, line-width and page-length warnings, a round trip with the original text, screen checks (branch arguments, grown mission files, HDD cache), and §4 of the guide.
* When P6 starts, put the skeleton into `patch/text/`.
