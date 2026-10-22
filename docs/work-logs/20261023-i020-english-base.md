# 작업 로그: 영문 모드 기반 한국어 패치 (issue #20, P6-2)

설계: [20261023-i020](../design/20261023-i020-english-base.md) · 작업 지시: [20261023-i020](../work-orders/20261023-i020-english-base.md) · 이슈: [#20](https://github.com/nworkers/JSRF-kr-patch/issues/20)

기간: 2026-10-23. 브랜치 `i020-english-base`(`main` `9b95ef3`, v0.0.11에서).

## 1. 결과

* 게임이 **영어 모드**로 동작하고, 메뉴·대화·미션·이벤트 문장이 한국어로 나온다. 바탕 XBE는 같은 디스크의 US판(`default_eng.xbe`, 언어 값 1)이다. Cxbx-Reloaded와 xemu에서 사용자가 확인했다("다 괜찮아 보인다", xemu 정상). reJSRF US 빌드는 출력을 그대로 부팅한다.
* 기존 번역 2,276줄은 고치지 않았다. 지금까지의 한국어 패치(일본어 자리)를 적용한 **위에** 영어 자리를 한국어로 맞춘다.
* 사용자 결정: XBE는 US판 바탕(안 B), 영어 음성을 받아들인다(2-a). 작업 중 사용자가 덤프의 `default.xbe`를 US판으로 바꾸고 그것을 쓰라고 했다.

## 2. 한 일

1. issue #20, 브랜치, 설계·작업 지시(사용자 결정 반영).
2. 분석(임시 스크립트, 결과는 [analysis/english-mode.md](../analysis/english-mode.md)):
   * US판 언어 값 `0x1FC724` = 1, 일본판 `0x251F58`은 bss. 두 빌드의 `.rdata`는 같은 주소에서 7바이트만 다르다.
   * 미디어 영어 자리: 메시지 스크립트 368개 모두 언어 2개(영어 구간 페이지 구조는 절반쯤 다르다), 미션 문장 명령 674개 모두 칸 1이 있다.
   * XBE: 언어 값을 읽는 191곳에서 표 모양 넷(직접 17, 배열 37, 2차원·레코드, 분기)을 찾고, 일본어 문자열의 언어 0 칸 695개를 영어 칸과 1:1로 짝지었다(일본어 문자열 579개). 처음 표 모양만 본 계산(118개)과 "한 칸짜리 레코드 266개"는 언어별 배열 안의 칸을 잘못 센 것이었다.
   * 그래피티 이름은 영어 모드에서 배율이 다르다(0.8 → 0.9).
   * 분석 결과로 설계를 고쳤다(§9): 일본어 자리를 원문으로 되돌리지 않는다(언어와 무관하게 쓰이는 문자열 51개 때문).
3. `tools/analysis/en_slots.py` → `patch/xbe-en.tsv`(695쌍, 주소와 원래 포인터 값만). 특수 3곳은 코드 바이트를 확인한 뒤에만 쓴다.
4. `tools/jsrfkr/english.py`: 메시지 스크립트 언어 1 = 언어 0 복사, 미션 칸 1 = 칸 0(칸 0이 한국어인 명령만), XBE 영어 칸 = 짝인 일본어 칸 값(번역된 문자열만, 대응표 값이 XBE와 맞는지 먼저 확인).
5. `tools/patch.py`: 영어 단계(기본), `--japanese-places`, xiso의 `default.xbe`(디스크의 일본판)를 패치한 US판으로 바꿔 넣기. `patch/manifest.json` 대상 US판. `extract_text.py`·`check_text.py`·`check_reinsert.py`·`check_roundtrip.py`의 XBE 확인을 US판으로.
6. `tools/check_english.py`(정적 검사), `tests/test_english.py`(7개).
7. 문서: `AGENTS.md`(프로젝트 개요의 입력 전제와 음성 범위, 주소 규칙), README, 가이드 세 개(`apply-patch`, `emulator-check` §6, `text-pipeline`), `tools/README.md`, `tools/analysis/README.md`, PLAN P6-2, `handoff-rejsrf.md` P6-2 절, 분석 색인.

## 3. 검증

| 항목 | 결과 |
|---|---|
| 단위 시험 | 60개 통과(새로 7개) |
| `check_english.py`(영어 모드 출력 ↔ `--japanese-places` 출력) | 메시지 스크립트 368개: 언어 0 같음, 언어 1 = 언어 0. 미션 196개 파일: 바뀐 바이트는 칸 1 포인터 495개뿐, 모두 칸 0과 같음. XBE: 바뀐 u32는 모두 대응표의 영어 칸(673개, 나머지 22개는 원래 같은 문자열을 가리킴), 섹션 요약값 모두 맞음. `jetfont.dat` 같음 |
| 기존 검사(US판 바탕) | 컨테이너 1,056개 왕복, XBE 요약값 왕복, 재삽입 왕복 2,276단위·565개 파일, `check_text.py` 오류 0·경고 0 |
| 출력 `out/jsrf-kr-en` | 2,276곳(201곳 붙임·옮김), 경고 0, 한글 907자, 영어 자리: 스크립트 368, 미션 명령 495, XBE 칸 695. `default.xbe` `98c624a9d72f47aafdb3d956bb6ca53d`, `jetfont.dat` `bf1d90ffe6a53881c6d359977a0ba2fa`, xiso `841c9f67e136b12e1a2a663d84a219ed` |
| reJSRF US 빌드(`build\win32_x86`, v0.0.47) | `xbe: USA`, `language: English`, 섹션 12개 배치, 30초 동안 경고 화면(영어 그림)까지 |
| **화면** | Cxbx-Reloaded·xemu: 사용자 확인, 문제 보고 없음 |
| `git status` | `roms/`, `out/`, `work/` 없음 |

## 4. 계획과 달라진 것

* 설계 §1의 "일본어 자리는 원문 그대로"를 분석 뒤 바꿨다(설계 §9).
* 미션은 영어 문자열 자리에 쓰지 않고 칸 1 포인터를 한국어 문자열로 돌렸다(붙이는 문자열이 늘지 않는다). 메시지 스크립트는 영어 구간 자체를 한국어로 다시 썼다.
* `push`로만 참조되는 21개는 화면 확인에서 문제가 보고되지 않아 따로 고치지 않았다(analysis english-mode §6에 미확정으로 남김).
* 덤프의 `default.xbe`를 US판으로 두는 것은 사용자가 한 일이다. 일본판 디스크 덤프를 그대로 쓰는 사용자는 `default_eng.xbe`를 `default.xbe`로 복사해야 한다(README, 가이드에 적음).

## 5. 다음

* 머지 요청 시: `VERSION` 0.0.12, 릴리스 노트, PR(`Closes #20`).
* 글자 그림(P7): 영어 모드의 경고문·로고·타이틀·메뉴 글자 그림은 영어판 그림이다.

---

# Work log: English-mode-based Korean patch (issue #20, P6-2)

Design: [20261023-i020](../design/20261023-i020-english-base.md) · Work order: [20261023-i020](../work-orders/20261023-i020-english-base.md) · Issue: [#20](https://github.com/nworkers/JSRF-kr-patch/issues/20)

Period: 2026-10-23. Branch `i020-english-base` (from `main` `9b95ef3`, v0.0.11).

## 1. Result

* The game runs in **English mode** and its menus, talk, missions and event text show in Korean. The base XBE is the same disc's US build (`default_eng.xbe`, language value 1). The user checked it in Cxbx-Reloaded and xemu ("all look fine", xemu works); reJSRF's US build boots the output as it is.
* The 2,276 existing translations were not touched; the English places are made Korean **on top of** the patch so far (the Japanese places).
* User decisions: the US XBE as the base (option B), English voices accepted (2-a). During the work the user replaced the dump's `default.xbe` with the US build and asked for it to be used.

## 2. Done

1. Issue #20, the branch, design and work order (with the user's decisions).
2. Analysis (temporary scripts; results in [analysis/english-mode.md](../analysis/english-mode.md)):
   * US language value `0x1FC724` = 1, Japanese `0x251F58` in bss; the two builds' `.rdata` differ in only 7 bytes at the same addresses.
   * English places in Media: all 368 message scripts have two languages (the English blocks' page structure differs in about half); all 674 mission text commands have slot 1.
   * XBE: from the 191 language reads, four table shapes (17 direct, 37 array, 2D/record, branch); the 695 language-0 slots of Japanese strings pair 1:1 with English slots (579 Japanese strings). The first shape-only count (118) and the "266 single-slot records" came from miscounting slots inside per-language arrays.
   * Graffiti names are drawn at another scale in English mode (0.8 → 0.9).
   * The design was changed after the analysis (§9): the Japanese places are not restored to the original (because of 51 strings used regardless of language).
3. `tools/analysis/en_slots.py` → `patch/xbe-en.tsv` (695 pairs, addresses and original pointer values only); the three special places are written only after their code bytes are checked.
4. `tools/jsrfkr/english.py`: message-script language 1 = a copy of language 0, mission slot 1 = slot 0 (only commands whose slot 0 is Korean), XBE English slot = its Japanese slot's value (only translated strings, after checking the map against the XBE).
5. `tools/patch.py`: the English step (default), `--japanese-places`, writing the patched US build over the xiso's `default.xbe` (the disc's Japanese build); `patch/manifest.json` targets the US build; the XBE checks of `extract_text.py`, `check_text.py`, `check_reinsert.py` and `check_roundtrip.py` now expect the US build.
6. `tools/check_english.py` (static check), `tests/test_english.py` (7).
7. Documents: `AGENTS.md` (the input premise and voice scope in the overview, the address rule), README, three guides (`apply-patch`, `emulator-check` §6, `text-pipeline`), `tools/README.md`, `tools/analysis/README.md`, PLAN P6-2, the P6-2 section of `handoff-rejsrf.md`, the analysis index.

## 3. Verified

| Item | Result |
|---|---|
| Unit tests | 60 pass (7 new) |
| `check_english.py` (English-mode output ↔ `--japanese-places` output) | 368 message scripts: language 0 equal, language 1 = language 0; 196 mission files: only the 495 slot-1 pointers differ, each equal to slot 0; XBE: every differing u32 is an English slot of the map (673; the other 22 already pointed at the same string), all section digests right; `jetfont.dat` equal |
| Existing checks (US base) | 1,056 container round trips, XBE digest round trip, reinsertion round trip of 2,276 units in 565 files, `check_text.py` 0 errors and 0 warnings |
| Output `out/jsrf-kr-en` | 2,276 places (201 appended or moved), 0 warnings, 907 Hangul; English places: 368 scripts, 495 mission commands, 695 XBE slots; `default.xbe` `98c624a9d72f47aafdb3d956bb6ca53d`, `jetfont.dat` `bf1d90ffe6a53881c6d359977a0ba2fa`, xiso `841c9f67e136b12e1a2a663d84a219ed` |
| reJSRF US build (`build\win32_x86`, v0.0.47) | `xbe: USA`, `language: English`, 12 sections placed, up to the warning screen (English picture) in 30 s |
| **Screen** | Cxbx-Reloaded and xemu: checked by the user, no problem reported |
| `git status` | no `roms/`, `out/`, `work/` |

## 4. Deviations from the plan

* Design §1's "the Japanese places keep the original" was changed after the analysis (design §9).
* Missions do not write into the English strings; slot-1 pointers are turned to the Korean strings (no extra appended strings). Message scripts have their English block itself rewritten in Korean.
* The 21 `push`-only strings were left as they are since the screen check reported no problem (kept unresolved in analysis english-mode §6).
* Putting the US build in the dump's `default.xbe` was done by the user; users with a plain Japanese disc dump copy `default_eng.xbe` to `default.xbe` (in the README and guides).

## 5. Next

* On a merge request: `VERSION` 0.0.12, release notes, a PR (`Closes #20`).
* Lettering pictures (P7): English mode's warning, logo, title and menu lettering are English pictures.
