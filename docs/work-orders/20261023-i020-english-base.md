# 작업 지시: 영문 모드 기반 한국어 패치 (issue #20, P6-2)

설계: [20261023-i020](../design/20261023-i020-english-base.md)

1. 분석(코드 없음, 임시 스크립트): 언어 값과 두 빌드 차이 재확인, XBE 영어 짝 대응표(언어를 읽는 191곳), 미션 칸 1 사용, 영어 모드 문장 배치, 음성 파일. 분석 문서 갱신.
2. 사용자 결정 반영: XBE 바탕(안 A/B), 음성(2-a/2-b).
3. 구현: `msgscript`·`reinsert`(언어 1 구간 = 일본어 구조 + 한국어), `mission`(칸 1), XBE 영어 짝 돌리기(대응표 패치 데이터), 안에 따라 `.data` 늘리기 또는 US판 바탕, `patch.py`·`manifest.json`.
4. 시험: 단위 시험, 영어 원문 왕복, 정적 검사.
5. 화면 확인(Cxbx-Reloaded, xemu, reJSRF US 빌드).
6. 문서: 분석, 가이드(`apply-patch`, `emulator-check`, `text-pipeline`), README, PLAN, `AGENTS.md`(안 B면 입력 전제), `handoff-rejsrf.md`, 작업 로그.

---

# Work order: English-mode-based Korean patch (issue #20, P6-2)

Design: [20261023-i020](../design/20261023-i020-english-base.md)

1. Analysis (no code; temporary scripts): re-check the language value and build differences, the XBE English-partner map (the 191 language reads), mission slot-1 use, English-mode text layout, voice files; update the analysis documents.
2. Apply the user's decisions: the XBE base (option A/B), voices (2-a/2-b).
3. Implementation: `msgscript` and `reinsert` (language 1 = Japanese structure + Korean), `mission` (slot 1), repointing XBE English partners (the map as patch data), extending `.data` or basing on the US XBE depending on the option, `patch.py` and `manifest.json`.
4. Tests: unit tests, the English-original round trip, static checks.
5. Screen checks (Cxbx-Reloaded, xemu, reJSRF US build).
6. Documents: analyses, guides (`apply-patch`, `emulator-check`, `text-pipeline`), README, PLAN, `AGENTS.md` (the input premise under option B), `handoff-rejsrf.md`, the work log.
