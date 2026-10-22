# 전체 게임 텍스트 번역 작업 지시서 (issue #17)

작성: 2026-10-22, issue #17.
설계: [docs/design/20261022-i017-text-translation.md](../design/20261022-i017-text-translation.md)

## 1. 개요

`work/text/`의 일본어/영어 원문을 번역하여 `patch/text/` 내 대상 TSV 파일의 `korean` 열을 채운다. 번역은 스트리트 감성의 캐주얼하고 젊은 어조로 작성하며, `check_text.py` 검증을 통과해야 한다.

## 2. 작업 순서 및 검증

| 단계 | 대상 | 분량 | 작업 내용 | 검증 |
|---|---|---|---|---|
| 1 | `patch/text/xbe.tsv` | 107줄 | 잔여 실황/결과 대사 번역 | `python -I tools/check_text.py "roms/Jet Set Radio Future"` |
| 2 | `patch/text/event.tsv` | 397줄 | 컷신 스토리 대사 번역 | `check_text.py` 오류 0 확인 |
| 3 | `patch/text/mission.tsv` | 495줄 | 미션 목표/무전 대사 번역 | `check_text.py` 오류 0 확인 |
| 4 | `patch/text/talk.tsv` | 733줄 | NPC/크루 대화 번역 | `check_text.py` 오류 0 확인 |
| 5 | 전체 검증 및 커밋 | 2,276줄 | 100% 완료 확인 및 검증 | `check_text.py`, `patch.py` 빌드 확인 |

각 단계 완료 시마다 번역 진행률과 주요 샘플을 사용자에게 리포트한다.

---

# Work Order for Complete Game Text Translation (issue #17)

Written: 2026-10-22, issue #17.
Design: [docs/design/20261022-i017-text-translation.md](../design/20261022-i017-text-translation.md)

## 1. Overview

Translate the Japanese/English original text in `work/text/` to fill the `korean` column of TSV files under `patch/text/`. Use a casual, youthful street tone and pass `check_text.py` verification.

## 2. Work Sequence and Verification

| Step | Target | Count | Task | Verification |
|---|---|---|---|---|
| 1 | `patch/text/xbe.tsv` | 107 lines | Residual DJ commentary/results | `python -I tools/check_text.py "roms/Jet Set Radio Future"` |
| 2 | `patch/text/event.tsv` | 397 lines | Cutscene story dialogue | 0 errors in `check_text.py` |
| 3 | `patch/text/mission.tsv` | 495 lines | Mission objectives/radio | 0 errors in `check_text.py` |
| 4 | `patch/text/talk.tsv` | 733 lines | NPC/crew dialogue | 0 errors in `check_text.py` |
| 5 | Full check & commit | 2,276 lines | 100% completion & validation | `check_text.py`, `patch.py` build verification |

Report translation progress and sample lines to the user at the completion of each step.
