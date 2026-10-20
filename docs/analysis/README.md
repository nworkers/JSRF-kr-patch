# JSRF-kr-patch 분석 색인

이 디렉터리는 일본판 JSRF `default.xbe`(MD5 `d8490cdb75bd47b36c62effdf1461ae0`)와 `Media`에서 직접 확인한 사실을 주제별로 누적한다. 시간순 작업 증거는 `docs/work-logs/`에 남기고, 여기에는 현재 유효한 결론을 통합한다.

표기 기준:

* **확인됨**: 정적 분석, 바이트 덤프, 왕복 시험, xemu·reJSRF 실행으로 직접 검증
* **추정**: 관측·정황·reJSRF(US판)나 외부 프로젝트의 보고와 일치하지만 일본판에서 더 확인해야 함
* **미확정**: 다음 분석에서 검증해야 할 가설 또는 blocker

주소는 일본판 가상 주소를 먼저 적고 US판 대응 주소와 대응 확인 방법을 함께 적는다.

reJSRF에서 이어받은 사실은 [PLAN.md §3](../PLAN.md)과 reJSRF의 [text-and-font](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/text-and-font.md), [language](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/language.md)에 있다.

## 문서

아직 없다. 첫 문서는 `text-renderer.md`(issue #3)다.

---

# JSRF-kr-patch analysis index

This directory accumulates, by topic, facts confirmed directly on the Japanese JSRF `default.xbe` (MD5 `d8490cdb75bd47b36c62effdf1461ae0`) and its `Media`. Chronological evidence stays in `docs/work-logs/`; current conclusions are merged here.

Labels:

* **Confirmed**: verified by static analysis, byte dumps, round trips, or runs in xemu or reJSRF
* **Inferred**: consistent with observations, context, or reports from reJSRF (US build) or other projects, but still to be checked on the Japanese build
* **Unresolved**: a hypothesis or blocker for a later analysis

Addresses give the Japanese virtual address first, with the US counterpart and how the match was established.

Facts carried over from reJSRF are in [PLAN.md §3](../PLAN.md) and reJSRF's [text-and-font](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/text-and-font.md) and [language](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/language.md).

## Documents

None yet. The first is `text-renderer.md` (issue #3).
