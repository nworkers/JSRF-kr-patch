# 작업 지시: 영어 모드 이벤트 자막 타이밍 (issue #26)

설계: [20261023-i026](../design/20261023-i026-subtitle-timing.md)(안 2를 계산으로, 사용자 결정)

1. `tools/jsrfkr/resplit.py`: 낱말과 틈의 세기, 영어 글자 비율 목표, 동적 계획법으로 나눌 곳 고르기, 창 한도 안의 줄 맞추기, 안 1용 시간 나누기(`spread`).
2. `tools/jsrfkr/english.py`: 이벤트는 `english_timing()`(영어 필드 1~4·페이지별 값 + 한국어 페이지, 필요하면 다시 나눔), 대화는 그대로 `copy_language0()`. `Result`에 메시지 수.
3. `tools/patch.py`: 1바이트 글자 폭을 넘기고 메시지 수를 출력한다.
4. `tools/check_timing.py`(덤프 전체 계산 검증, `--review`), `tools/check_english.py`를 새 규칙으로.
5. 시험: `tests/test_resplit.py`, `tests/test_english.py` 갱신. 덤프 전체: `check_timing.py`, `check_english.py`, `check_reinsert.py`, `check_roundtrip.py`, 재현성.
6. 문서: 분석 [message-script §5](../analysis/message-script.md), 가이드(`text-pipeline.md` §3.2, `translation.md`), `tools/README.md`, 작업 로그.

---

# Work order: English-mode cutscene subtitle timing (issue #26)

Design: [20261023-i026](../design/20261023-i026-subtitle-timing.md) (option 2 by calculation, the user's decision)

1. `tools/jsrfkr/resplit.py`: words and gap strengths, targets from English letter shares, dynamic programming for the breaks, wrapping within the window limits, time spreading for option 1 (`spread`).
2. `tools/jsrfkr/english.py`: events through `english_timing()` (English fields 1–4 and per-page values + Korean pages, re-split when needed); talk stays on `copy_language0()`; message counts in `Result`.
3. `tools/patch.py`: pass the single-byte glyph widths; print the message counts.
4. `tools/check_timing.py` (computed whole-dump check, `--review`); `tools/check_english.py` on the new rule.
5. Tests: `tests/test_resplit.py`, `tests/test_english.py` updated. Whole dump: `check_timing.py`, `check_english.py`, `check_reinsert.py`, `check_roundtrip.py`, reproducibility.
6. Documents: analysis [message-script §5](../analysis/message-script.md), guides (`text-pipeline.md` §3.2, `translation.md`), `tools/README.md`, work log.
