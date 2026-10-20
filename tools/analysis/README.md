# 분석 스크립트

일본판 XBE와 `Media`를 조사할 때 쓰는 스크립트다. 표준 라이브러리만 쓴다. 사용자 덤프를 읽기만 하고, 파일을 쓰는 옵션(`--tsv`, `--png`)은 `work/` 아래를 가리켜야 한다(게임 자료에서 나온 결과라 커밋하지 않는다). 결과는 [docs/analysis/](../../docs/analysis/README.md)에 정리한다. XBE 읽기 모듈(`xbe.py`)은 P1(issue #2)에서 [tools/jsrfkr/](../README.md)로 옮겼다.

| 스크립트 | 하는 일 | issue |
|---|---|---|
| `font_tables.py` | 렌더러가 쓰는 글꼴 서술자, 2바이트·1바이트 글리프 표, 부류 경계를 해독하고 요약한다. `--tsv`로 칸 대응표 전체를 쓴다 | #3 |
| `jetfont.py` | `jetfont.dat`의 텍스처 6장을 나열하고, `--png`로 alpha를 PNG로 쓴다(`--grid`는 칸 격자) | #3 |
| `renderer_compare.py` | 렌더러 코드 범위가 일본판과 US판에서 같은지(다른 바이트가 모두 재배치된 주소인지)와 글꼴 표가 같은지 확인한다 | #3 |
| `text_codes.py` | 문장 레코드의 `$` 코드 수, 표에 없는 글자, 가장 넓은 줄(픽셀), 가장 긴 페이지(바이트)를 센다. 원문은 출력하지 않는다. **1분 30초쯤 걸린다** | #3 |

실행(저장소 루트에서, 덤프가 `roms/`에 있을 때):

```bash
python -I tools/analysis/font_tables.py "roms/Jet Set Radio Future/default.xbe"
```

```bash
python -I tools/analysis/renderer_compare.py "roms/Jet Set Radio Future/default.xbe" "roms/Jet Set Radio Future/default_eng.xbe"
```

---

# Analysis scripts

Scripts for examining the Japanese XBE and `Media`. Standard library only. They only read the user's dump; the options that write files (`--tsv`, `--png`) must point under `work/` (the output derives from game data and is never committed). Findings go to [docs/analysis/](../../docs/analysis/README.md). The XBE reader (`xbe.py`) moved to [tools/jsrfkr/](../README.md) in P1 (issue #2).

| Script | What it does | Issue |
|---|---|---|
| `font_tables.py` | decodes and summarises the font descriptors, double- and single-byte glyph tables and class bounds the renderer uses; `--tsv` writes the whole cell map | #3 |
| `jetfont.py` | lists the six textures in `jetfont.dat`; `--png` writes their alpha as PNG (`--grid` draws the cell grid) | #3 |
| `renderer_compare.py` | checks that the renderer code ranges are the same in the JP and US builds (every differing byte a relocated address) and that the font tables are identical | #3 |
| `text_codes.py` | counts the `$` codes in the text records, characters missing from the table, the widest line (pixels) and the longest page (bytes); prints no original text. **Takes about 1.5 minutes** | #3 |

Run from the repository root with the dump under `roms/` (commands above).
