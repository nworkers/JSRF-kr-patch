# 작업 로그: 텍스트 렌더러 분석 (issue #3, P2)

설계: [PLAN.md §5 P2](../PLAN.md) · 작업 지시: [20261020-i003](../work-orders/20261020-i003-text-renderer.md) · 결과: [analysis/text-renderer.md](../analysis/text-renderer.md)

## 한 일

1. 경로 문자열 `D:\Media\Font\jetfont.dat`(`0x1C5B50`)와 `TNRoman.bin`(`0x1CAF74`)의 참조를 찾았다. `jetfont.dat`는 파일 표 `0x1EDE3C`를 거쳐 로더 `0x2C040`이 읽고, `TNRoman.bin`은 그래픽 초기화 `0x5F350`이 읽는다.
2. `$`(`0x24`) 비교와 2바이트 첫 바이트 비교(`0x80`/`0xA0`)가 함께 있는 함수를 찾아 문자열 너비 `0x3D680`과 문자열 그리기 `0x3CF20`에 닿았다. 여기서 2바이트 글리프 함수 `0x3CA20` → 부류 판정 `0x3C730` → 검색 `0x3C790`/`0x3C830` → 표 `0x1F7088`을 따라갔다.
3. 표 `0x1F7088`이 글리프 순서표임을 확인했다. 항목은 `u16` 코드(리틀엔디언) + `u16` 순번, 4바이트 간격이다. reJSRF가 Shift-JIS 바이트열로 찾을 때 걸리지 않은 이유다.
4. `jetfont.dat`를 512×2304 하나로 해독하니 페이지 3이 밀려 보였다. 로더가 노드 6개를 따라가는 것을 보고 파일 구조(노드 + 서술자 + 픽셀, 텍스처 6장)를 알아냈다. 다시 해독한 페이지 0과 3의 칸이 표 순서(19칸씩, 페이지 3의 빈 칸 41개 포함)와 정확히 맞았다. 1바이트 페이지(tex4)도 1바이트 표의 글리프 번호와 맞았다.
5. 메시지 쪽에서 토큰 분류기 `0xF81B0`, 타자기 `0xF8360`, 페이지 분석기 `0xF9090`을 찾아 `$` 코드마다 세 곳의 처리를 표로 만들었다.
6. `TNRoman.bin`으로 만든 객체 `[0x251D48]`의 사용처가 `Fps=%d`, `Object=%d`, 키 설정 화면뿐임을 확인했다(디버그 글꼴).
7. US판과 같은 주소의 바이트를 비교했다. 다른 바이트는 모두 재배치된 `.data` 주소 피연산자였고, 글꼴 표는 바이트 단위로 같았다.
8. 문장 레코드를 세어 실제로 쓰이는 `$` 코드, 표에 없는 글자, 가장 넓은 줄과 가장 긴 페이지를 구했다.
9. 스크립트 5개와 문서(분석, kb 2개, 인계 문서, PLAN §3, 색인)를 썼다.

## 검증

| 검증 | 결과 |
|---|---|
| 입력 MD5 | JP `d8490cdb75bd47b36c62effdf1461ae0`, US `f4e366bfdceee551a09f42219c90d84e`, `jetfont.dat` `bc566ef593dbf603e5332a7af346e2c8`, `TNRoman.bin` `8f2593685f21573197580b07b0350f0e` |
| `font_tables.py` | 서술자 4페이지 × 19×19(26픽셀), 2페이지 × 12×7(21×34). 표 1,390개, 빈 칸 41개, 부류 5개 모두 코드 범위 안(한자 구역의 `ヶ` `ー` 2개 제외) |
| `jetfont.py --png work/jetfont --grid` | 텍스처 6장, 데이터 끝 = 파일 크기 `0x120130`. 페이지 0·3과 tex4의 칸이 표와 일치(눈으로 확인, 그림은 `work/`) |
| `renderer_compare.py` | 로더·글꼴 객체·`TNRoman` 초기화·메시지 범위의 다른 바이트 57개가 모두 재배치 피연산자(+`0x20`, +`0x18`, 언어 전역 −`0x55834`). 표·경로·파일 표는 같음. "same renderer" |
| `text_codes.py` | 레코드 2,933개. 코드 `$r` 7,208, `$e` 3,098, `$n` 2,022, `$c` 1,188, `$a` 494, `$g` 10, `$p` 5, `$bc` 5. 표에 없는 2바이트는 `0x8140`(전각 공백, 따로 처리) 487개뿐. 가장 넓은 줄 581픽셀(`mssn3405.bin`), 가장 긴 페이지 135바이트(`mssn0515.bin`) |
| 화면 확인 | 하지 않았다. xemu 실행은 P4(개념 증명)에서 한다. 화면에 관한 결론은 추정으로 적었다 |
| `git status` | `roms/`, `work/`, `out/` 없음 |

## 쓴 도구와 출처

* 조사 중 디스어셈블리는 capstone 5.0.7(BSD-3)로 임시 스크립트에서 읽었다. 저장소의 스크립트는 표준 라이브러리만 쓴다. reJSRF 스크립트는 복사하지 않았다(`text_codes.py`의 레코드 정규식은 reJSRF `scripts/analysis/text/text_records.py`(커밋 `18aa27f`)와 같은 규칙을 다시 쓴 것이다).
* `THIRD_PARTY_NOTICES.md`는 바뀌지 않는다(서드파티 코드를 넣지 않았다).

## 남은 것

* P3(issue #4): §9의 권장(A′ 표 데이터 패치, 1,390~1,444칸)으로 설계한다. 번역문의 서로 다른 음절 수가 결정 기준이다.
* P4(issue #5): xemu와 reJSRF에서 한글 칸과 줄 폭을 화면으로 확인한다. 표에 없는 코드가 어떻게 보이는지도 본다.
* reJSRF: `docs/analysis/text-and-font.md`의 세 가지 사실(순서표, `jetfont.dat` 구조, `TNRoman.bin`)을 고칠 것([handoff-rejsrf.md](../handoff-rejsrf.md)).
* 미확정 `$` 코드(`$a $p $s $j $v $b? $f $m $h $o`)의 표시 쪽 동작.

---

# Work log: text renderer analysis (issue #3, P2)

Design: [PLAN.md §5 P2](../PLAN.md) · Work order: [20261020-i003](../work-orders/20261020-i003-text-renderer.md) · Result: [analysis/text-renderer.md](../analysis/text-renderer.md)

## Done

1. Found the references to the path strings `D:\Media\Font\jetfont.dat` (`0x1C5B50`) and `TNRoman.bin` (`0x1CAF74`): the loader `0x2C040` reads `jetfont.dat` through the file table `0x1EDE3C`; the graphics init `0x5F350` reads `TNRoman.bin`.
2. Looked for functions comparing both with `$` (`0x24`) and with double-byte lead bytes (`0x80`/`0xA0`), which led to the string width `0x3D680` and the draw-string function `0x3CF20`; from there followed the double-byte glyph function `0x3CA20` → class test `0x3C730` → searches `0x3C790`/`0x3C830` → table `0x1F7088`.
3. Confirmed that the table `0x1F7088` is the glyph order table: entries are a little-endian `u16` code plus a `u16` serial at a 4-byte stride, which is why reJSRF's Shift-JIS byte-string search missed it.
4. Decoding `jetfont.dat` as one 512×2304 image showed page 3 shifted. The loader walking six nodes revealed the file structure (node + descriptor + pixels, six textures). The re-decoded pages 0 and 3 matched the table order exactly (19 cells per row, including page 3's 41 empty cells); the single-byte page (tex4) matched the single-byte table's glyph numbers too.
5. On the message side, found the tokenizer `0xF81B0`, the typewriter `0xF8360` and the page parser `0xF9090`, and tabulated how each handles every `$` code.
6. Confirmed that the object `[0x251D48]` made from `TNRoman.bin` is used only by `Fps=%d`, `Object=%d` and a key-configuration screen (a debug font).
7. Compared the bytes at the same addresses in the US build: every differing byte was a relocated `.data` address operand, and the font tables were byte-identical.
8. Counted the text records for the `$` codes in use, characters missing from the table, the widest line and the longest page.
9. Wrote five scripts and the documents (analysis, two kb topics, the handoff, PLAN §3, indexes).

## Verification

| Check | Result |
|---|---|
| Input MD5s | JP `d8490cdb75bd47b36c62effdf1461ae0`, US `f4e366bfdceee551a09f42219c90d84e`, `jetfont.dat` `bc566ef593dbf603e5332a7af346e2c8`, `TNRoman.bin` `8f2593685f21573197580b07b0350f0e` |
| `font_tables.py` | descriptors 4 pages × 19×19 (26 px) and 2 pages × 12×7 (21×34); 1,390 table entries, 41 empty, all five classes inside their code ranges (except `ヶ` and `ー` in the kanji range) |
| `jetfont.py --png work/jetfont --grid` | six textures; data ends at the file size `0x120130`; the cells of pages 0 and 3 and of tex4 match the tables (checked by eye; pictures in `work/`) |
| `renderer_compare.py` | all 57 differing bytes in the loader, font object, `TNRoman` init and message ranges are relocated operands (+`0x20`, +`0x18`, the language global −`0x55834`); tables, paths and the file table are identical; "same renderer" |
| `text_codes.py` | 2,933 records; codes `$r` 7,208, `$e` 3,098, `$n` 2,022, `$c` 1,188, `$a` 494, `$g` 10, `$p` 5, `$bc` 5; the only double-byte code missing from the table is `0x8140` (full-width space, handled separately), 487 times; widest line 581 px (`mssn3405.bin`), longest page 135 bytes (`mssn0515.bin`) |
| Screen check | not done; xemu runs come in P4 (proof of concept). Conclusions about the screen are recorded as inferred |
| `git status` | no `roms/`, `work/` or `out/` |

## Tools and sources

* During the investigation, disassembly was read with capstone 5.0.7 (BSD-3) in temporary scripts. The repository's scripts use the standard library only. No reJSRF script was copied (`text_codes.py`'s record regex restates the rule of reJSRF `scripts/analysis/text/text_records.py`, commit `18aa27f`).
* `THIRD_PARTY_NOTICES.md` is unchanged (no third-party code added).

## Remaining

* P3 (issue #4): design along §9's recommendation (A′, a table data patch, 1,390–1,444 cells); the distinct syllable count of the translation decides.
* P4 (issue #5): check Hangul cells and line widths on screen in xemu and reJSRF, including how a code missing from the table looks.
* reJSRF: correct three facts in `docs/analysis/text-and-font.md` (the order table, the `jetfont.dat` structure, `TNRoman.bin`) ([handoff-rejsrf.md](../handoff-rejsrf.md)).
* The display-side behaviour of the unresolved `$` codes (`$a $p $s $j $v $b? $f $m $h $o`).
