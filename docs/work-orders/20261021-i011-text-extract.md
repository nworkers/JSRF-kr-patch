# 작업 지시: 문장 형식 분석과 추출 (issue #11, P5-1)

설계: [20261021-i011](../design/20261021-i011-text-extract.md)

1. 분석 문서: `docs/analysis/message-script.md`(이벤트 `2/0`·대화 이벤트 형식, 분기 인자), `docs/analysis/mission-files.md`(머리 구역 표, 명령 레코드, 문장 명령, 재배치 함수 `0x4DB30`, 로더), `docs/analysis/xbe-strings.md`(문자열 규칙, 참조, 포인터 표 모양, 여백). `text-files.md`·`containers.md`의 미확정 항목을 갱신하고 링크한다. 분석 색인(`docs/analysis/README.md`)을 고친다. 주소마다 US판 대응과 확인 방법을 적는다.
2. `tools/jsrfkr/msgscript.py`: 읽기, 토큰, 언어·메시지·페이지 나누기(바이트 위치), `build()` 왕복.
3. `tools/jsrfkr/mission.py`: 구역 표, 명령 레코드, 문장 명령 포인터 7칸.
4. `tools/jsrfkr/xbetext.py`: `.rdata` 일본어 문자열 규칙과 참조(`.data` 포인터 칸, `push` 즉치).
5. `tools/jsrfkr/extract.py`: 문장 단위 목록(설계 §3.2), `textpatch` 자리 해석으로 SHA-1 자체 검사.
6. `tools/jsrfkr/textpatch.py`: `korean`이 빈 줄 건너뛰기. `patch/text/README.md`와 설계 i002 §3.1에 적는다.
7. `tools/extract_text.py`: `work/text/<group>.tsv`, `work/text/skeleton/<group>.tsv`, `work/text/summary.txt`, 표준 출력에 묶음별 개수와 2,933개 비교 수.
8. `tests/`: `test_msgscript.py`, `test_mission.py`, `test_xbetext.py`, `test_textpatch.py`에 빈 `korean` 시험(모두 게임 자료 없이).
9. 검증: 설계 §6의 1~7. `msgscript` 왕복(117 + 251), 미션 포인터, 자체 검사, 빈 뼈대로 `patch.py`, 두 번 실행 비교.
10. 가이드 `docs/guides/text-pipeline.md`: 추출 → 번역 → 재조합을 AI 없이 따라 할 수 있는 단계별 절차(명령, 입출력, 확인법, 오류의 뜻, TSV 채우기 규칙, 아직 안 되는 단계). `docs/guides/apply-patch.md`에서 링크한다. `AGENTS.md` 문서 작성 규칙에 "도구나 사용자 단계를 바꾸면 같은 작업에서 가이드를 갱신한다"를 더한다.
11. 문서: `tools/README.md`(도구 표, 사용법), PLAN §5 P5 줄(issue #11, 앞 절반), `handoff-rejsrf.md` P5 절(형식과 주소), 작업 로그 `docs/work-logs/20261021-i011-text-extract.md`.
12. 커밋: 작업 브랜치 `i011-text-extract`, 제목 끝 `(#11)`. 커밋 전 `git status`로 `work/`, `out/`, `roms/`가 빠졌는지 본다.

---

# Work order: text-format analysis and extraction (issue #11, P5-1)

Design: [20261021-i011](../design/20261021-i011-text-extract.md)

1. Analysis documents: `docs/analysis/message-script.md` (the event `2/0` and talk-event format, branch arguments), `docs/analysis/mission-files.md` (header section table, command records, text commands, the fixup function `0x4DB30`, the loader), `docs/analysis/xbe-strings.md` (string rule, references, pointer-table shapes, slack). Update and link the unresolved items of `text-files.md` and `containers.md`; update the analysis index (`docs/analysis/README.md`). Give each address its US counterpart and how it was matched.
2. `tools/jsrfkr/msgscript.py`: parsing, tokens, language/message/page split (byte offsets), `build()` round trip.
3. `tools/jsrfkr/mission.py`: section table, command records, the 7 pointer slots of text commands.
4. `tools/jsrfkr/xbetext.py`: the `.rdata` Japanese string rule and references (`.data` pointer slots, `push` immediates).
5. `tools/jsrfkr/extract.py`: the list of text units (design §3.2) and the SHA-1 self-check through `textpatch`'s place resolution.
6. `tools/jsrfkr/textpatch.py`: skip rows with an empty `korean`; recorded in `patch/text/README.md` and design i002 §3.1.
7. `tools/extract_text.py`: `work/text/<group>.tsv`, `work/text/skeleton/<group>.tsv`, `work/text/summary.txt`; counts per group and the 2,933 comparison on standard output.
8. `tests/`: `test_msgscript.py`, `test_mission.py`, `test_xbetext.py`, and an empty-`korean` test in `test_textpatch.py` (all without game data).
9. Verification: items 1–7 of design §6: `msgscript` round trip (117 + 251), mission pointers, the self-check, `patch.py` with the empty skeleton, two runs compared.
10. Guide `docs/guides/text-pipeline.md`: a step-by-step procedure for extract → translate → reassemble that can be followed without AI (commands, inputs and outputs, checks, what errors mean, rules for filling the TSV, steps not available yet), linked from `docs/guides/apply-patch.md`. Add to the documentation rules of `AGENTS.md`: "a task that changes a tool or a user step updates the guide in the same task".
11. Documents: `tools/README.md` (tool table, usage), the PLAN §5 P5 row (issue #11, first half), the P5 section of `handoff-rejsrf.md` (formats and addresses), the work log `docs/work-logs/20261021-i011-text-extract.md`.
12. Commits on the task branch `i011-text-extract`, titles ending `(#11)`; before committing, check with `git status` that `work/`, `out/` and `roms/` are left out.
