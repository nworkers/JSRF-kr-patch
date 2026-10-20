# reJSRF 인계 문서

이 저장소의 결과 중 reJSRF가 런타임 방식으로 다시 구현하거나 참고할 것을 단계마다 적는다([PLAN §8](PLAN.md)). 주소는 일본판 주소, US판 주소, 대응을 확인한 방법을 함께 적는다.

## P2 텍스트 렌더러 (issue #3)

근거: [analysis/text-renderer.md](analysis/text-renderer.md)

| 항목 | 일본판 | US판 | 대응 방법 |
|---|---|---|---|
| 문자열 그리기 | `0x3CF20` | `0x3CF20` | 같은 주소 바이트 비교(`tools/analysis/renderer_compare.py`) |
| 2바이트 글리프 / 1바이트 글리프 | `0x3CA20` / `0x3CBC0` | 같음 | 같음 |
| 코드 부류 / 부류 검색 / 한자 검색 | `0x3C730` / `0x3C790` / `0x3C830` | 같음 | 같음 |
| `DrawText` 포장 함수 | `0x3D5D0`, `0x3D610` | 같음 | 같음 |
| 문자열 너비 | `0x3D680`(`0x3D750`) | 같음 | 같음 |
| 메시지 토큰 분류기 / 타자기 / 페이지 분석기 | `0xF81B0` / `0xF8360` / `0xF9090` | 같음 | 같음 |
| `jetfont.dat` 로더 | `0x2C040` | 같음 | 같음 |
| 2바이트 글리프 표 | `.data` `0x1F7088`(1,390 × 4바이트) | `0x1F7088` | 바이트 단위로 같음 |
| 1바이트 글리프 표 | `0x1F8640`(156 × 8바이트) | 같음 | 같음 |
| 글꼴 서술자·부류 경계·시작 순번 | `0x1F8B20`~`0x1F8B9F` | 같음 | 같음 |
| 글꼴 작업 조회 | `[0x22FCC0]`, ID `0x1166` | `[0x22FCE0]` | 피연산자 대응(+`0x20`) |
| 언어 전역 | `0x251F58` | `0x1FC724` | 피연산자 대응(reJSRF language §4와 같음) |

* reJSRF `docs/analysis/text-and-font.md`에서 고칠 것:
  * "글리프 순서표가 XBE와 `Media` 어디에도 없다" → `0x1F7088`에 있다(리틀엔디언 `u16` 코드, 4바이트 간격이라 바이트열 검색에 걸리지 않았다).
  * "`jetfont.dat` = DXT3 512×2304, 약 88줄, 약 1,500자" → 텍스처 6장(512×512 네 장, 256×256 두 장), 2바이트 1,390칸(찾을 수 있는 코드 1,343개), 1바이트 156자.
  * "`TNRoman.bin`은 영문 비례 글꼴" → 개발용 디버그 글꼴. 영어 문장은 `jetfont`의 1바이트 페이지로 그린다.
  * `$` 코드 뜻은 text-renderer §6.
* 렌더러가 두 빌드에서 같으므로, 이 저장소의 `jetfont.dat`·문장 파일 패치는 reJSRF(US XBE, 언어 0)에서 그대로 시험할 수 있다(**추정**, P4에서 확인). XBE 글리프 표 패치를 택하면(P3) reJSRF는 US판 같은 주소 `0x1F7088`의 표를 런타임에 바꾸면 된다.

---

# Handoff to reJSRF

What reJSRF should reimplement at run time or take as reference, recorded per phase ([PLAN §8](PLAN.md)). Addresses give the Japanese address, the US address and how the match was established.

## P2 text renderer (issue #3)

Basis: [analysis/text-renderer.md](analysis/text-renderer.md)

| Item | Japanese | US | Match |
|---|---|---|---|
| draw string | `0x3CF20` | `0x3CF20` | byte comparison at the same address (`tools/analysis/renderer_compare.py`) |
| double-byte glyph / single-byte glyph | `0x3CA20` / `0x3CBC0` | same | same |
| code class / class search / kanji search | `0x3C730` / `0x3C790` / `0x3C830` | same | same |
| `DrawText` wrappers | `0x3D5D0`, `0x3D610` | same | same |
| string width | `0x3D680` (`0x3D750`) | same | same |
| message tokenizer / typewriter / page parser | `0xF81B0` / `0xF8360` / `0xF9090` | same | same |
| `jetfont.dat` loader | `0x2C040` | same | same |
| double-byte glyph table | `.data` `0x1F7088` (1,390 × 4 bytes) | `0x1F7088` | byte-identical |
| single-byte glyph table | `0x1F8640` (156 × 8 bytes) | same | same |
| font descriptors, class bounds, first indexes | `0x1F8B20`–`0x1F8B9F` | same | same |
| font task lookup | `[0x22FCC0]`, ID `0x1166` | `[0x22FCE0]` | operand pairing (+`0x20`) |
| language global | `0x251F58` | `0x1FC724` | operand pairing (as in reJSRF language §4) |

* To correct in reJSRF `docs/analysis/text-and-font.md`:
  * "no glyph order table anywhere in the XBE or `Media`" → it is at `0x1F7088` (little-endian `u16` codes at a 4-byte stride, which a byte-string search misses).
  * "`jetfont.dat` = DXT3 512×2304, about 88 rows, about 1,500 glyphs" → six textures (four 512×512, two 256×256), 1,390 double-byte cells (1,343 findable codes), 156 single-byte glyphs.
  * "`TNRoman.bin` is a proportional Latin font" → a developer debug font; English text is drawn from `jetfont`'s single-byte pages.
  * The `$` codes' meaning: text-renderer §6.
* Since the renderer is the same in both builds, this repository's `jetfont.dat` and text-file patches can be tested as they are in reJSRF (US XBE, language 0) (**inferred**, to be checked in P4). If P3 chooses the XBE glyph-table patch, reJSRF replaces the table at the same US address `0x1F7088` at run time.
