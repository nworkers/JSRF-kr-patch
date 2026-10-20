# 작업 지시: 텍스트 렌더러 분석 (issue #3, P2)

설계: [PLAN.md §5 P2](../PLAN.md). 이 작업은 분석이라 패치 데이터를 바꾸지 않는다. 분석 스크립트(`tools/analysis/`)만 새로 만든다.

## 목표

일본판 `default.xbe`(MD5 `d8490cdb75bd47b36c62effdf1461ae0`)에서 다음을 찾아 `docs/analysis/text-renderer.md`에 확인됨·추정·미확정으로 적는다.

1. 화면 문장을 그리는 함수와 그 호출 구조.
2. Shift-JIS 코드 → `Media/Font/jetfont.dat` 칸의 대응(표 또는 계산).
3. `$` 제어 코드(`$n $r $e $p $b $c $a $g $s` 등)의 뜻.
4. 한 줄 최대 폭, 글리프 크기, 그 밖의 크기 제한.
5. `Media/Font/TNRoman.bin`의 역할(US판 `sub_0005F350`이 연다).
6. US판 대응 주소와 대응 방법, 렌더러가 두 빌드에서 같은지(PLAN §6의 전제).
7. P3(글꼴 방식 결정)에 넘길 권장 입력.

## 방법

1. 글꼴 파일 경로 문자열과 그 참조에서 시작해 로더와 글꼴 객체를 찾는다. `$`(`0x24`)와 2바이트 첫 바이트 비교가 함께 있는 함수에서 문자열 그리기 함수를 찾는다.
2. 디스어셈블리는 조사 중에 capstone(BSD-3, reJSRF `code_diff.py`와 같은 도구)으로 읽었다. 저장소에 넣는 스크립트는 표준 라이브러리만 쓴다.
3. 표·서술자를 해독하는 스크립트, `jetfont.dat` 텍스처를 해독해 칸을 표와 맞춰 보는 스크립트, US판과 바이트 비교하는 스크립트, 문장 레코드를 세는 스크립트를 `tools/analysis/`에 만든다.
4. 원문, 해독한 그림, 대응표 파일은 `work/`에만 둔다.

## 산출물

* `tools/analysis/`: `xbe.py`, `font_tables.py`, `jetfont.py`, `renderer_compare.py`, `text_codes.py`, `README.md`
* `docs/analysis/text-renderer.md`, `docs/analysis/README.md` 색인
* `docs/kb/shift-jis.md`, `docs/kb/dxt3.md`, `docs/kb/README.md` 색인(새로 나온 형식 지식)
* `docs/handoff-rejsrf.md`(P2 결과), `docs/PLAN.md` §3의 바뀐 사실, `docs/README.md`
* 작업 로그

## 검증

* `jetfont.py --png --grid`로 해독한 페이지의 칸이 `font_tables.py`의 표 순서와 맞는지 눈으로 본다(그림은 `work/`).
* `renderer_compare.py`가 "same renderer"를 내는지.
* 커밋 전 `git status`에 `roms/`, `work/`, `out/`가 없는지.

---

# Work order: text renderer analysis (issue #3, P2)

Design: [PLAN.md §5 P2](../PLAN.md). This is analysis and changes no patch data; only analysis scripts (`tools/analysis/`) are added.

## Goal

Find the following in the Japanese `default.xbe` (MD5 `d8490cdb75bd47b36c62effdf1461ae0`) and record them, labelled confirmed / inferred / unresolved, in `docs/analysis/text-renderer.md`:

1. The functions that draw on-screen text and how they are called.
2. The mapping from a Shift-JIS code to a cell of `Media/Font/jetfont.dat` (a table or a computation).
3. The meaning of the `$` control codes (`$n $r $e $p $b $c $a $g $s` ...).
4. The maximum line width, the glyph size and other size limits.
5. The role of `Media/Font/TNRoman.bin` (opened by the US build's `sub_0005F350`).
6. The US counterpart addresses and how they were matched, and whether the renderer is the same in both builds (PLAN §6's premise).
7. The recommended input for P3 (the font approach).

## Method

1. Start from the font file path strings and their references to find the loader and the font object; find the draw-string function among functions that compare with `$` (`0x24`) and with double-byte lead bytes.
2. Disassembly was read during the investigation with capstone (BSD-3, the same tool as reJSRF's `code_diff.py`). Scripts committed to the repository use the standard library only.
3. Add scripts under `tools/analysis/` that decode the tables and descriptors, decode the `jetfont.dat` textures to check cells against the table, compare bytes with the US build, and count the text records.
4. Original text, decoded pictures and map files stay in `work/`.

## Deliverables

* `tools/analysis/`: `xbe.py`, `font_tables.py`, `jetfont.py`, `renderer_compare.py`, `text_codes.py`, `README.md`
* `docs/analysis/text-renderer.md` and the `docs/analysis/README.md` index
* `docs/kb/shift-jis.md`, `docs/kb/dxt3.md` and the `docs/kb/README.md` index (new format knowledge)
* `docs/handoff-rejsrf.md` (P2 results), the changed facts in `docs/PLAN.md` §3, `docs/README.md`
* the work log

## Verification

* Check by eye that the cells of pages decoded with `jetfont.py --png --grid` follow the table order from `font_tables.py` (pictures in `work/`).
* `renderer_compare.py` reports "same renderer".
* Before committing, `git status` shows no `roms/`, `work/` or `out/`.
