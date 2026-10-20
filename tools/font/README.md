# 글꼴 도구 (issue #6)

한국어 글꼴(A′ 방식)을 만드는 도구다. 설계는 [docs/design/20261020-i006-korean-font.md](../../docs/design/20261020-i006-korean-font.md)에 있다. 표준 라이브러리만 쓴다. 사용자 덤프를 읽기만 하고, 출력은 `work/` 아래에 쓴다(게임 자료에서 나온 결과라 커밋하지 않는다).

| 파일 | 하는 일 |
|---|---|
| `ttf.py` | TrueType(`glyf`) 읽기와 래스터라이저. 같은 글꼴에서 항상 같은 비트맵 |
| `hangul.py` | KS X 1001 한글 2,350자와 2바이트 코드의 고정 대응(`가` = `0x8890` … `힝` = `0x94ED`) |
| `dxt3.py` | DXT3 alpha 풀기·압축(흰색 색 블록, 손실 없음) |
| `glyph_table.py` | 새 글리프 표와 부류 시작 순번(한글 → 빈 칸 → 가나 → 숫자·영대문자 → 기호) |
| `build_font.py` | 명령줄: 새 `jetfont.dat`, 새 표를 넣은 `default.xbe`, `layout.tsv`, 미리보기 PNG |
| `sample.txt` | 시험용 한국어 문장(이 저장소에서 쓴 것) |

```bash
python -I tools/font/build_font.py "roms/Jet Set Radio Future" tools/font/sample.txt work/font-sample
```

```bash
python -I tools/font/build_font.py "roms/Jet Set Radio Future" NUL work/font-identity --identity
```

`--identity`는 원래 표로 다시 만드는 왕복 시험이다. 출력 `jetfont.dat`와 `default.xbe`가 원본과 같아야 한다.

---

# Font tools (issue #6)

Tools that build the Korean font (option A′). The design is in [docs/design/20261020-i006-korean-font.md](../../docs/design/20261020-i006-korean-font.md). Standard library only. They only read the user's dump and write under `work/` (the output derives from game data and is never committed).

| File | What it does |
|---|---|
| `ttf.py` | TrueType (`glyf`) reader and rasterizer; the same font always gives the same bitmaps |
| `hangul.py` | the fixed map between the 2,350 KS X 1001 syllables and double-byte codes (`가` = `0x8890` … `힝` = `0x94ED`) |
| `dxt3.py` | DXT3 alpha decode and encode (white colour blocks, lossless) |
| `glyph_table.py` | the new glyph table and class first indexes (Hangul, padding, kana, digits/capitals, symbols) |
| `build_font.py` | command line: new `jetfont.dat`, `default.xbe` with the new table, `layout.tsv`, preview PNGs |
| `sample.txt` | Korean test sentences (written for this repository) |

`--identity` (commands above) is the round-trip test that rebuilds with the original table; the output `jetfont.dat` and `default.xbe` must equal the originals.
