# 작업 지시: 길이가 바뀌는 문장 재삽입 (issue #13, P5-2)

설계: [20261021-i013](../design/20261021-i013-text-reinsert.md)

1. `tools/jsrfkr/screen.py`: 줄 폭·줄 수·페이지 버퍼 검사, `$r`·`$e`·분기 코드 개수 검사.
2. `tools/jsrfkr/xbeedit.py`: 섹션 머리 표 옮기기와 섹션 더하기, 머리 값(섹션 수·주소, 머리 크기, 이미지 크기), 새 섹션을 포함한 요약값.
3. `tools/jsrfkr/reinsert.py`: 파일별 묶기, 이벤트·대화(페이지 바꾸기와 다시 만들기), 미션(제자리 또는 붙이기·포인터), XBE(제자리 또는 새 섹션·참조), 그 밖(제자리). "늘 옮기기" 시험 선택.
4. `tools/jsrfkr/xiso.py`: 커진 파일(섹터 안이면 크기만, 넘으면 이미지 끝에 붙이고 항목 고치기).
5. `tools/patch.py`: 문장 단계를 `reinsert`로, XBE 순서, 경고 출력.
6. `tools/check_reinsert.py`: 원문 왕복, 옮기기 왕복.
7. `tests/`: `test_reinsert.py`, `test_xbeedit.py`, `test_screen.py`, `test_xiso.py`(게임 자료 없이).
8. `patch/poc/long.tsv`: 묶음마다 원문보다 긴 시험 문장 한 줄(번역 아님).
9. 검증: 설계 §5의 1~7. 화면 확인은 사용자에게 요청한다.
10. 문서: 가이드 `text-pipeline.md` §2.2(길이 규칙)·§4, `apply-patch.md` §3 기대 MD5, `emulator-check.md` 볼 화면, 분석 문서(새 섹션을 받는지, 커진 파일 동작 — 화면 결과), `tools/README.md`, `patch/text/README.md`, `handoff-rejsrf.md` P5-2 절, PLAN P5 줄, 작업 로그 `docs/work-logs/20261021-i013-text-reinsert.md`.
11. 커밋: 작업 브랜치 `i013-text-reinsert`, 제목 끝 `(#13)`. 커밋 전 `git status`로 `work/`, `out/`, `roms/`가 빠졌는지 본다.

---

# Work order: reinserting text whose length changes (issue #13, P5-2)

Design: [20261021-i013](../design/20261021-i013-text-reinsert.md)

1. `tools/jsrfkr/screen.py`: line width, line count and page buffer checks; the `$r`/`$e`/branch-code count check.
2. `tools/jsrfkr/xbeedit.py`: moving the section header table and adding a section; header values (section count and address, header size, image size); digests including the new section.
3. `tools/jsrfkr/reinsert.py`: grouping per file; events and talk (page replacement and rebuild), missions (in place, or append and repoint), XBE (in place, or new section and references), others (in place); an "always move" test option.
4. `tools/jsrfkr/xiso.py`: grown files (size only within the allocated sectors; beyond them, append at the end of the image and fix the entry).
5. `tools/patch.py`: the text step through `reinsert`, the XBE order, warnings printed.
6. `tools/check_reinsert.py`: the original round trip and the move round trip.
7. `tests/`: `test_reinsert.py`, `test_xbeedit.py`, `test_screen.py`, `test_xiso.py` (no game data).
8. `patch/poc/long.tsv`: one longer-than-original test line per group (not a translation).
9. Verification: items 1–7 of design §5; the screen check is requested from the user.
10. Documents: guide `text-pipeline.md` §2.2 (length rules) and §4, `apply-patch.md` §3 expected MD5s, `emulator-check.md` screens to look at, analysis documents (whether the added section is accepted, how grown files behave — screen results), `tools/README.md`, `patch/text/README.md`, the P5-2 section of `handoff-rejsrf.md`, the PLAN P5 row, the work log `docs/work-logs/20261021-i013-text-reinsert.md`.
11. Commits on the task branch `i013-text-reinsert`, titles ending `(#13)`; before committing, check with `git status` that `work/`, `out/` and `roms/` are left out.
