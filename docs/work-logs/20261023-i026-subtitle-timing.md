# 작업 로그: 영어 모드 이벤트 자막 타이밍 (issue #26)

설계: [20261023-i026](../design/20261023-i026-subtitle-timing.md) · 작업 지시: [20261023-i026](../work-orders/20261023-i026-subtitle-timing.md)

## 1. 결과

이벤트 자막이 영어판의 시간에 맞는다. 메시지 139개 모두 영어 구간이 영어의 페이지 수·필드 1~4·페이지별 값을 갖는다. 페이지 수가 같은 77개는 한국어 페이지를 그대로 쓰고, 다른 62개는 한국어를 영어 페이지 수로 자동으로 다시 나눴다. 나눌 수 없어 안 1(시간만 나누기)로 간 메시지는 없다. 번역 파일은 바뀌지 않았다.

## 2. 한 일

1. 원인 조사(정적): `english.copy_language0()`가 영어 구간의 시간 값까지 일본어에서 복사했다. 원본은 언어마다 페이지 수(62개)·시간 합(비율 0.12~2.49)·필드 4(21개)가 다르다([message-script §5](../analysis/message-script.md)).
2. 설계를 쓰고 사용자가 안 2(계산)를 골랐다.
3. `resplit.py`를 만들고 틈 비용을 조정했다. 처음 값(문장 0.01, 절 0.03, 띄어쓰기 0.06)은 영어 글자 비율에 가깝게 맞추느라 구절 한가운데 나눈 곳이 82개였다(예: "난 먼저 차고로 / 가 있을게"). 한국어 연결 어미·조사를 틈의 세기에 넣고 비용을 올리자(문장 0, 절 0.1, 조사 0.2, 그 밖 0.35) 10개로 줄었고, 목표와의 차이 중앙값은 0.013에서 0.021로 조금 늘었다.

| 비용(문장, 절, 조사, 그 밖) | 문장 | 절 | 조사 | 그 밖 | 차이 중앙값 |
|---|---|---|---|---|---|
| 처음(0.01, 0.03, -, 0.06) | 106 | 60 | - | 82 | 0.013 |
| 채택(0, 0.1, 0.2, 0.35) | 142 | 74 | 22 | 10 | 0.021 |

4. `english.py`, `patch.py`, `check_english.py`를 고치고 `check_timing.py`를 더했다. 시험과 문서를 갱신했다.

## 3. 검증

| 검증 | 결과 |
|---|---|
| 단위 시험 | 88개 통과(새 15개) |
| `check_timing.py` | 메시지 139개, 문제 0. 다시 나눈 곳 248개(문장 142, 절 74, 조사 22, 그 밖 10), 목표와의 차이 중앙값 0.032, 최대 0.21 |
| 읽어 보기(`--review`) | 다시 나눈 62개를 영어와 나란히 읽었다. 예: `e024` "음? 또 경찰 단속인가. / 요즘 부쩍 많아졌네. / 난 먼저 차고로 가 있을게. / 한판 붙을 생각이라면, 정신 나간 경부를 조심해! / 그럼 이만.", `e210`은 "제트 셋 라디오！！"가 "Jet Set Radio!" 페이지에 온다. 차이가 큰 메시지(`e210` 0.21 등)도 뜻은 영어 페이지와 맞는다(언어마다 줄 길이가 달라서 생기는 차이) |
| `check_english.py` | 대화 368개 스크립트, 미션 196개, XBE 칸 673개: 통과 |
| `check_reinsert.py`, `check_roundtrip.py` | 통과 |
| 재현성 | 두 번 빌드한 `md5.txt`가 같다. `default.xbe`는 v0.0.13과 같다(`98c624a9…`) |
| 화면 | 하지 않았다(사용자 결정: 계산으로 검증). 출력은 `out/i026-check`(하드링크) |

* 로컬 덤프 폴더(`roms/Jet Set Radio Future`)의 `default.xbe`가 일본판이라, US판을 `default.xbe`로 둔 보기 폴더 `work/game-us`(하드링크·정션)로 실행했다.

## 4. 남은 것

* 값의 뜻(표시 시간, 시작 지연)을 코드로 확인하지 않았다. 플레이 중 어긋나는 장면이 있으면 그 메시지와 함께 알린다.
* 대화 이벤트와 미션 무전 시간은 범위 밖이다.

---

# Work log: English-mode cutscene subtitle timing (issue #26)

Design: [20261023-i026](../design/20261023-i026-subtitle-timing.md) · Work order: [20261023-i026](../work-orders/20261023-i026-subtitle-timing.md)

## 1. Result

Cutscene subtitles follow the English version's timing. In all 139 messages the English block has the English page count, fields 1–4 and per-page values; the 77 with the same page count use the Korean pages as they are, and the other 62 have the Korean re-split automatically into the English page count. No message fell back to option 1 (time spreading only). The translation files did not change.

## 2. Done

1. Cause (static): `english.copy_language0()` copied the English block's timing from the Japanese too; the originals differ by language in page count (62), time sums (ratio 0.12–2.49) and field 4 (21) ([message-script §5](../analysis/message-script.md)).
2. Wrote the design; the user chose option 2 (by calculation).
3. Wrote `resplit.py` and tuned the gap costs. The first values (sentence 0.01, clause 0.03, space 0.06) followed the English letter shares closely but broke inside a phrase 82 times ("난 먼저 차고로 / 가 있을게"). With Korean connective endings and particles in the gap strengths and higher costs (sentence 0, clause 0.1, particle 0.2, other 0.35) that fell to 10, while the median distance from the targets rose a little, from 0.013 to 0.021 (table above).
4. Changed `english.py`, `patch.py` and `check_english.py`; added `check_timing.py`; updated tests and documents.

## 3. Verified

| Check | Result |
|---|---|
| Unit tests | 88 pass (15 new) |
| `check_timing.py` | 139 messages, 0 problems; 248 re-split breaks (sentence 142, clause 74, particle 22, other 10); distance from the targets median 0.032, max 0.21 |
| Reading (`--review`) | read the 62 re-split messages beside the English; for example `e024` breaks at each sentence, and in `e210` "제트 셋 라디오！！" lands on the "Jet Set Radio!" page; even the largest distances (`e210` 0.21) match the English pages in meaning (line lengths differ by language) |
| `check_english.py` | 368 scripts, 196 missions, 673 XBE slots: pass |
| `check_reinsert.py`, `check_roundtrip.py` | pass |
| Reproducibility | two builds give the same `md5.txt`; `default.xbe` equals v0.0.13 (`98c624a9…`) |
| Screen | not done (the user's decision: verify by calculation); the output is `out/i026-check` (hard links) |

* The local dump folder (`roms/Jet Set Radio Future`) has the Japanese build as `default.xbe`, so the runs used a view folder `work/game-us` (hard link and junction) with the US build as `default.xbe`.

## 4. Open

* The values' meaning (display time, start delay) is not code-confirmed; if a scene still drifts in play, report it with the message.
* Talk-event and mission-radio timing are out of scope.
