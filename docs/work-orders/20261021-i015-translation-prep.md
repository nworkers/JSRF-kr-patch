# 작업 지시: 번역 준비 (issue #15, P6-0)

설계: [20261021-i015](../design/20261021-i015-translation-prep.md)

1. `tools/patch.py`의 글꼴·인코딩 부분을 함수로 나눈다(공용, 출력 MD5가 그대로인지 확인).
2. `tools/check_text.py`: 메모리에서 검사, 파일별 오류 모으기, 진행률·음절 수·옮김 수, `--review` 검토 표, 끝 코드.
3. `tests/test_check_text.py`(게임 자료 없이).
4. `patch/text/`에 뼈대 네 개 복사.
5. `docs/kb/glossary.md`(+ `docs/kb/README.md` 색인).
6. `patch/text/xbe.tsv`: XBE 기능 문구 초벌 번역(실황 대사·숫자·크기 글자 제외). 코드·자리 표시 공백 검사 스크립트로 확인.
7. `--update-manifest`, `check_text.py`, `patch.py`, `check_reinsert.py`.
8. `docs/guides/translation.md`, `text-pipeline.md`·`apply-patch.md` 링크, `docs/README.md`, `tools/README.md`, `patch/text/README.md`, PLAN P6 줄, 작업 로그 `docs/work-logs/20261021-i015-translation-prep.md`.
9. 커밋: 작업 브랜치 `i015-translation-prep`, 제목 끝 `(#15)`. 커밋 전 `git status`.

---

# Work order: translation preparation (issue #15, P6-0)

Design: [20261021-i015](../design/20261021-i015-translation-prep.md)

1. Split the font and encoding part of `tools/patch.py` into a function (shared; check the output MD5s stay the same).
2. `tools/check_text.py`: in-memory checks, per-file error collection, progress, syllable count and moves, the `--review` table, the exit code.
3. `tests/test_check_text.py` (no game data).
4. Copy the four skeletons into `patch/text/`.
5. `docs/kb/glossary.md` (+ the `docs/kb/README.md` index).
6. `patch/text/xbe.tsv`: the first-pass translation of XBE functional strings (commentary, digits and size letters left out), checked by a code and placeholder script.
7. `--update-manifest`, `check_text.py`, `patch.py`, `check_reinsert.py`.
8. `docs/guides/translation.md`; links from `text-pipeline.md` and `apply-patch.md`; `docs/README.md`, `tools/README.md`, `patch/text/README.md`, the PLAN P6 row, the work log `docs/work-logs/20261021-i015-translation-prep.md`.
9. Commits on the task branch `i015-translation-prep`, titles ending `(#15)`; `git status` before committing.
