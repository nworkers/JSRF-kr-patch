# 작업 로그: 길이가 바뀌는 문장 재삽입 (issue #13, P5-2)

설계: [20261021-i013](../design/20261021-i013-text-reinsert.md), 작업 지시: [20261021-i013](../work-orders/20261021-i013-text-reinsert.md), 브랜치 `i013-text-reinsert`.

입력: 일본판 덤프 `roms/Jet Set Radio Future`(`default.xbe` MD5 `d8490cdb75bd47b36c62effdf1461ae0`), xiso `roms/Jet Set Radio Future.iso`(일반 xiso, 파티션 0).

## 1. 결과

* `patch/text/*.tsv`의 한국어가 원문보다 길어도 들어간다. 이벤트·대화는 페이지를 바꿔 메시지 스크립트를 다시 만들고, 미션은 파일 끝에 붙이고 칸 0 포인터를 고치고, XBE는 새 섹션 `KRTEXT`로 옮기고 참조를 모두 고친다. 페이지 수는 바꾸지 않는다(사용자 승인, 설계 §3.1).
* 정적·왕복 검증은 모두 통과했다. **에뮬레이터 화면 확인은 하지 않았다**(사용자 사정, 2026-10-21). 사용자 결정으로 화면 확인 없이 머지하고, 화면 확인은 issue #13의 후속으로 남긴다.

## 2. 한 일

1. 조사: XBE 머리(머리 크기 `0x988`, 첫 섹션 원시 위치 `0x1000`, 섹션 머리 표 `0x348`, 공유 페이지 참조 수 `0x5B0`~), xiso 형식(사용자 xiso는 파티션 0), 이벤트·대화의 원문 줄 수·폭 최댓값(이벤트 3줄·528픽셀, 대화 3줄·456픽셀), 미션 명령 레코드에 페이지 수 값이 있는지(상관이 뚜렷하지 않음 → 페이지 수를 바꾸지 않기로).
2. 모듈: `tools/jsrfkr/reinsert.py`(파일별 적용), `xbeedit.py`(섹션 더하기, 표에서 요약값), `screen.py`(구조·페이지 버퍼·줄 폭·줄 수). `textpatch.py`에 `encode_row`·`put`을 나눴다. `xiso.py`는 커진 파일을 받는다(섹터 안이면 크기만, 넘으면 이미지 끝). `xbe.py`는 파일을 닫는다(시험 경고).
3. `tools/patch.py`: 인코딩 오류를 한꺼번에 알리고, `reinsert`로 넣고, 경고와 붙임·옮김을 출력한다. 요약값은 이미지 자신의 섹션 표로 계산한다(`xbeedit.fix_digests`).
4. `tools/check_reinsert.py`: 원문 왕복과 옮기기 왕복.
5. 시험 `tests/test_reinsert.py`, `test_xbeedit.py`, `test_screen.py`, `test_xiso.py`, 합성 XBE `tests/fakexbe.py`.
6. 시험 문장 `patch/poc/long.tsv`(묶음마다 원문보다 긴 한 줄, 이 저장소가 쓴 문장). `patch/manifest.json`에 `e000.dat`를 더했다.
7. 문서: 가이드 `text-pipeline.md`(머리말, §2.2 길이·코드 규칙, §3 출력, §4, §5 오류), `emulator-check.md` §5, `apply-patch.md` §3, `patch/text/README.md`, `tools/README.md`, 분석 세 개의 구현 절, `handoff-rejsrf.md` P5-2 절, PLAN P5 줄.

## 3. 검증

| 항목 | 결과 |
|---|---|
| 단위 시험 | 48개 통과(게임 자료 없음) |
| 원문 왕복 `check_reinsert.py` | 단위 2,276개를 원문 바이트로 다시 넣으면 파일 565개 모두 원본과 같다 |
| 옮기기 왕복 | 미션 495개·XBE 651개 문자열을 일부러 모두 붙이거나 옮겨도 모든 칸 0 포인터·`.data` 칸·`push` 즉치가 원래 바이트로 이어지고, 그 밖의 바이트는 원본과 같다(문제 0) |
| P4 시험 문장 | `TE014.bin`만 바뀐다(`72ef06…` → `ef4ad91efec7a607a2b984d3b32aabc8`, 공백 채움 없이 다시 만들어 1바이트 짧다). `default.xbe` `cbb44a11…`, `jetfont.dat` `fd1400c5…`, `mssn0110.bin` `8062445d…`는 v0.0.7과 같다 |
| 긴 시험 문장 `long.tsv` | 4곳: 이벤트 34 → 61바이트, 대화 18 → 33, 미션 42 → 43(붙임), XBE 6 → 8(옮김), 경고 0. 출력: `default.xbe` `b0b95c85b71a70fd638054997a1e640e`(섹션 12개, `KRTEXT` VA `0x289000` 원시 `0x22D000` 크기 9, 머리 크기 `0xC34`, 이미지 크기 `0x279009`, 요약값 12개 모두 맞음), `e000.dat` `9b629a93…`, `TE014.bin` `757e044e…`, `mssn0110.bin` `665e7c6d…`, `jetfont.dat` `401a2efe…` |
| `--iso` | `out/jsrf-kr-long.iso` `80a4a3ee2ef50d5e23cf4b37f7fcdb8f`. 커진 `default.xbe`는 이미지 끝(섹터 1,223,008)에 쓰였다. xiso 안의 바뀐 파일 5개가 출력 폴더와 같다 |
| 화면 | 머지 때는 확인하지 않음. **후속 확인(2026-10-22, Cxbx-Reloaded 585c49a)**: §7 |
| `git status` | `roms/`, `out/`, `work/` 없음 |

## 4. 계획과 달라진 것

* 화면 확인(설계 §5의 5)을 하지 못했다. 사용자가 에뮬레이터 확인이 지금은 어렵다며, 문서를 마무리하고 머지하기로 했다.
* 설계 §5의 7(가이드 명령 그대로 실행)은 §4의 `check_reinsert.py`와 `long.tsv` 출력으로 대신했다(가이드의 나머지 명령은 v0.0.7과 같다).
* `xbe.py`의 파일 닫기는 계획에 없던 작은 수정이다.

## 5. 새로 안 사실

* 일본판 XBE 머리 뒤에 `0x678`바이트 여유가 있어 섹션 머리 표를 옮겨 늘릴 수 있다.
* 사용자 xiso는 일반 xiso(파티션 0)이고 볼륨 서술자에 전체 크기가 없어, 이미지 끝에 파일을 붙여도 된다(정적).

## 6. 다음

* ~~화면 확인(이 issue의 후속)~~: Cxbx-Reloaded에서 확인함(§7). 남은 것: 이벤트 자막(`e000.dat`), xemu.
* P6 번역.

## 7. 후속: 화면 확인 (2026-10-22)

`out/jsrf-kr-long`을 다시 만들었다. 출력 MD5는 §3과 같다(`default.xbe` `b0b95c85…`, `e000.dat` `9b629a93…`, `TE014.bin` `757e044e…`, `mssn0110.bin` `665e7c6d…`, `jetfont.dat` `401a2efe…`, xiso `80a4a3ee…`). Cxbx-Reloaded HDD 캐시에서 바뀌는 `Media` 파일 세 개를 먼저 뺐다. 그 가운데 `TE014.bin`·`mssn0110.bin`은 10/21에 P4 패치판으로 캐시된 것이었다. 백업은 `EmuDisk\cache-bak-20261022\`에 있다.

| 시험 문장 | 결과(Cxbx-Reloaded 585c49a, `out/jsrf-kr-long/default.xbe`) |
|---|---|
| 부팅(섹션 `KRTEXT`를 더한 XBE) | **확인됨**: 실행된다 |
| 저장하기(XBE, `KRTEXT`로 옮김) | **확인됨** |
| 로보이 첫 대사(대화 페이지 다시 만들기, 18 → 33바이트) | **확인됨** |
| 첫 미션 목표(미션 파일 끝에 붙임, 42 → 43바이트) | **확인됨** |
| `e000` 이벤트 자막(이벤트 페이지 다시 만들기, 34 → 61바이트) | **미확인**: 실행 뒤 캐시에 `e000.dat`이 없었다. 게임이 그 파일을 읽지 않았으므로 그 이벤트까지 가지 않았다 |

* 사용자 보고: "잘 된다". 캐시 시각으로 보면 대화(`TE014.bin` 00:30)와 미션(`mssn0110.bin` 00:29) 파일을 읽었다.
* 결론: 섹션을 더하는 XBE 방식, 대화 페이지 다시 만들기, 미션 붙이기는 Cxbx-Reloaded에서 동작한다. 설계를 바꿀 필요가 없다.
* 남은 것: 이벤트 자막 하나, xemu(HDD 이미지에 P4 캐시가 남아 있을 수 있어 깨끗한 HDD가 필요하다).
* **추가(2026-10-23)**: 전체 번역 출력(issue #17, `KRTEXT`로 201곳 옮김)이 **xemu 0.8.139에서 부팅**하고 XBE 문구가 나온다([작업 로그 i017](20261022-i017-text-translation.md) §4). 섹션을 더하는 방식은 xemu에서도 동작한다.

---

# Work log: reinserting text whose length changes (issue #13, P5-2)

Design: [20261021-i013](../design/20261021-i013-text-reinsert.md); work order: [20261021-i013](../work-orders/20261021-i013-text-reinsert.md); branch `i013-text-reinsert`.

Inputs: the Japanese dump `roms/Jet Set Radio Future` (`default.xbe` MD5 `d8490cdb75bd47b36c62effdf1461ae0`) and the xiso `roms/Jet Set Radio Future.iso` (a plain xiso, partition at 0).

## 1. Result

* Korean in `patch/text/*.tsv` may now be longer than the original: event and talk pages are replaced and the message script rebuilt; mission strings are appended at the end of the file with slot 0 repointed; XBE strings move into a new section `KRTEXT` with every reference fixed. Page counts never change (approved by the user, design §3.1).
* All static and round-trip checks pass. **No emulator screen check was made** (the user's circumstances, 2026-10-21); by the user's decision the work is merged without it, and the screen check stays as a follow-up of issue #13.

## 2. Done

1. Investigation: the XBE header (header size `0x988`, first section raw offset `0x1000`, section header table at `0x348`, shared page reference counts from `0x5B0`), the xiso format (the user's xiso has its partition at 0), the original maxima of lines and width in events and talk (3 lines and 528 px, 3 lines and 456 px), and whether mission command records hold page counts (no clear correlation → page counts stay).
2. Modules `tools/jsrfkr/reinsert.py` (per-file application), `xbeedit.py` (adding a section, digests from the image's own table), `screen.py` (structure, page buffer, line width, line count); `textpatch.py` gained `encode_row` and `put`; `xiso.py` accepts grown files (size only within the sectors, else at the end of the image); `xbe.py` closes its file (a test warning).
3. `tools/patch.py`: reports all encoding errors at once, applies through `reinsert`, prints warnings and appends/moves; digests are computed from the image's own section table (`xbeedit.fix_digests`).
4. `tools/check_reinsert.py`: the original and move round trips.
5. Tests `tests/test_reinsert.py`, `test_xbeedit.py`, `test_screen.py`, `test_xiso.py` and the synthetic XBE `tests/fakexbe.py`.
6. Test lines `patch/poc/long.tsv` (one line per group longer than its original, written for this repository); `e000.dat` added to `patch/manifest.json`.
7. Documents: guide `text-pipeline.md` (header note, §2.2 length and code rules, §3 output, §4, §5 errors), `emulator-check.md` §5, `apply-patch.md` §3, `patch/text/README.md`, `tools/README.md`, implementation notes in the three analyses, the P5-2 section of `handoff-rejsrf.md`, the PLAN P5 row.

## 3. Verified

| Item | Result |
|---|---|
| unit tests | 48 pass (no game data) |
| original round trip `check_reinsert.py` | putting the 2,276 units back as original bytes leaves all 565 files equal to the originals |
| move round trip | appending or moving all 495 mission and 651 XBE strings on purpose keeps every slot-0 pointer, `.data` slot and `push` immediate leading to the original bytes, with no other byte changed (0 problems) |
| P4 test lines | only `TE014.bin` changes (`72ef06…` → `ef4ad91efec7a607a2b984d3b32aabc8`, rebuilt without padding, one byte shorter); `default.xbe` `cbb44a11…`, `jetfont.dat` `fd1400c5…` and `mssn0110.bin` `8062445d…` equal v0.0.7 |
| long test lines `long.tsv` | 4 places: event 34 → 61 bytes, talk 18 → 33, mission 42 → 43 (appended), XBE 6 → 8 (moved), 0 warnings. Output: `default.xbe` `b0b95c85b71a70fd638054997a1e640e` (12 sections, `KRTEXT` VA `0x289000` raw `0x22D000` size 9, header size `0xC34`, image size `0x279009`, all 12 digests check), `e000.dat` `9b629a93…`, `TE014.bin` `757e044e…`, `mssn0110.bin` `665e7c6d…`, `jetfont.dat` `401a2efe…` |
| `--iso` | `out/jsrf-kr-long.iso` `80a4a3ee2ef50d5e23cf4b37f7fcdb8f`; the grown `default.xbe` was written at the end of the image (sector 1,223,008); the five changed files inside the xiso equal the output folder |
| screen | not checked at the merge; **follow-up check (2026-10-22, Cxbx-Reloaded 585c49a)**: §7 |
| `git status` | no `roms/`, `out/`, `work/` |

## 4. Deviations from the plan

* The screen check (design §5 item 5) was not made; the user said an emulator check is hard for now and chose to finish the documents and merge.
* Design §5 item 7 (running the guide's commands as written) was covered by §4's `check_reinsert.py` and the `long.tsv` output (the guide's other commands are as in v0.0.7).
* Closing the file in `xbe.py` is a small fix outside the plan.

## 5. New findings

* The Japanese XBE has `0x678` free bytes after its headers, enough to move and grow the section header table.
* The user's xiso is a plain xiso (partition at 0) and its volume descriptor holds no total size, so files can be appended at the end of the image (static).

## 6. Next

* ~~Screen check (a follow-up of this issue)~~: done in Cxbx-Reloaded (§7). Left: the event subtitle (`e000.dat`), xemu.
* P6 translation.

## 7. Follow-up: screen check (2026-10-22)

`out/jsrf-kr-long` was rebuilt with the MD5s of §3 (`default.xbe` `b0b95c85…`, `e000.dat` `9b629a93…`, `TE014.bin` `757e044e…`, `mssn0110.bin` `665e7c6d…`, `jetfont.dat` `401a2efe…`, xiso `80a4a3ee…`). The three changed `Media` files were first taken out of the Cxbx-Reloaded HDD cache; `TE014.bin` and `mssn0110.bin` there were the P4-patched copies cached on 10/21. They are backed up in `EmuDisk\cache-bak-20261022\`.

| Test line | Result (Cxbx-Reloaded 585c49a, `out/jsrf-kr-long/default.xbe`) |
|---|---|
| boot (the XBE with the added `KRTEXT` section) | **confirmed**: it runs |
| 저장하기 (XBE, moved to `KRTEXT`) | **confirmed** |
| Roboy's first line (talk page rebuilt, 18 → 33 bytes) | **confirmed** |
| first mission objective (appended to the mission file, 42 → 43 bytes) | **confirmed** |
| the `e000` event subtitle (event page rebuilt, 34 → 61 bytes) | **not checked**: `e000.dat` was not in the cache after the run, so the game never read it and that event was not reached |

* The user reported "it works". The cache times show the talk (`TE014.bin` 00:30) and mission (`mssn0110.bin` 00:29) files were read.
* Conclusion: adding an XBE section, rebuilding talk pages and appending mission strings work in Cxbx-Reloaded; the design needs no change.
* Left: the one event subtitle, and xemu (its HDD image may still hold P4 caches, so a clean HDD is needed).
* **Added (2026-10-23)**: the full translation output (issue #17, 201 places moved or appended) **boots in xemu 0.8.139** and shows the XBE text ([work log i017](20261022-i017-text-translation.md) §4); adding a section works in xemu too.
