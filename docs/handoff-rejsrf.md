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

## P3 한국어 글꼴 (issue #6)

근거: [design/20261020-i006-korean-font.md](design/20261020-i006-korean-font.md)

* 방식 A′: 렌더러 코드는 그대로 두고 XBE `.data`의 글리프 표 `0x1F7088`(1,390 × 4바이트)과 부류 시작 순번 `0x1F8B80`~`0x1F8B8F`만 바꾼다. US판도 같은 주소, 같은 원래 바이트다.
* 한글 코드: KS X 1001 2,350자의 k번째 → `0x8890`부터 둘째 바이트 `0x40`~`0x7E`·`0x80`~`0xFC`만 세어 k번째 코드(`tools/font/hangul.py`). reJSRF는 같은 규칙으로 계산하거나 이 저장소가 만든 표를 그대로 쓴다.
* 표 배치: 한글(코드 순) → 빈 칸 → 히라가나·가타카나(칸이 남을 때) → 숫자·영대문자 → 기호(`tools/font/glyph_table.py`).
* `jetfont.dat`: tex0~3만 새 표 순서로 다시 만든다. 남기는 칸은 원래 칸을 옮기고, 한글은 Do Hyeon(OFL)을 26×26 칸의 잉크 상자 (2,3)–(23,22)에 2,350자 공통 배율로 그린다. 같은 입력이면 같은 바이트가 나온다.
* reJSRF에서: 런타임에 US판 `0x1F7088`·`0x1F8B80`에 같은 표를 쓰고, 이 저장소 도구가 만든 `jetfont.dat`를 `rexbox` 파일 계층에서 대신 내주면 된다(**추정**, P4에서 확인).

## P4 개념 증명 (issue #8)

근거: [analysis/text-files.md](analysis/text-files.md), [작업 로그 i008](work-logs/20261020-i008-poc.md), [guides/emulator-check.md](guides/emulator-check.md)

* **reJSRF 일본판 빌드에서 확인됨**(reJSRF `4e2c0f2`, `build\win32_x86_jp` Release): 패치한 일본판 XBE(`out/poc/rejsrf/default_jpn.xbe`, `--xbe default_jpn.xbe`)와 패치한 `Media`로 차고의 로보이 대사 "뭐야、무슨 볼일？"이 한글로 나온다. 16:9 Hor+에서도 대사 칸과 글자는 가운데 제자리에 나온다. reJSRF는 인증서로 XBE를 알아보므로 서명을 고치지 않은 패치 XBE를 받는다.
* 같은 출력이 Cxbx-Reloaded와 xemu에서도 같게 나온다. 그러므로 P3의 방식(글리프 표 `0x1F7088`·부류 순번 `0x1F8B80` 데이터 패치 + 새 `jetfont.dat`)은 reJSRF가 원본 렌더러를 그대로 돌려도 동작한다.
* US XBE + `REJSRF_LANGUAGE=Japanese` 경로(`out/poc/rejsrf/default.xbe`, 같은 표를 넣은 US판)는 실행하지 않았다(**미확정**). US XBE의 메뉴 문자열은 주소가 달라 바꾸지 않았다.
* **HDD 캐시**: 게임은 `Media` 파일을 처음 읽을 때 `Z:\Media\…`에 복사하고 그 뒤로는 캐시를 읽는다. reJSRF에서 패치를 시험할 때는 `hdd\`(또는 `REJSRF_HDD_ROOT`)에 원본이 캐시되어 있지 않아야 한다. 런타임 패치를 넣을 때도 캐시 경로(`Z:`)로 읽히는 파일까지 같은 내용을 내줘야 한다. `jetfont.dat`는 캐시되지 않는다.
* 문장 자리(일본판, 제자리 교체로 확인):

| 자리 | 내용 | US판 |
|---|---|---|
| `Media/Mission/mssn0110.bin` `0x2228C` | 첫 미션 목표(일본어 NUL 영어 NUL 짝) | 같은 `Media` |
| `Media/Event/TalkEvent/TE014.bin` `0x88` | 로보이 첫 대사(한 문자열 안 메시지) | 같은 `Media` |
| XBE `.rdata` `0x1D29E0` | "セーブ" | 미대응 |
| XBE `.data` `0x221948` | 일시정지 메뉴 포인터 표(언어별) | 미대응 |
| XBE `.data` `0x2216DC`, `0x2221D8` | 리트라이 메뉴, B 버튼 안내 표 | 미대응 |

* 일본판은 언어 전역 `0x251F58`에 쓰지 않는다. 일본판 빌드의 언어 설정이 Japanese 고정인 것과 맞는다.

## P5-2 길이가 바뀌는 문장 재삽입 (issue #13)

근거: [설계 i013](design/20261021-i013-text-reinsert.md), [작업 로그 i013](work-logs/20261021-i013-text-reinsert.md)

* 이 저장소의 패치 출력에서 길이가 바뀐 파일: 이벤트 `e###.dat`(항목 `2/0`의 페이지와 컨테이너 연결), 대화 `TE###.bin`(파일 크기), 미션 `mssn####.bin`(파일 끝에 붙인 문자열과 칸 0 포인터), `default.xbe`(새 섹션 `KRTEXT` VA `0x289000`, 섹션 머리 표를 `0x988`로 옮김, 옮긴 문자열의 `.data` 칸과 `push` 즉치). 페이지 수는 바꾸지 않는다.
* reJSRF는 US XBE를 실행하므로 XBE 쪽은 그대로 쓸 수 없다. 런타임에 같은 문자열 참조를 새 문자열로 바꾸는 방식이 필요하다(옮긴 문자열의 참조 목록은 `tools/jsrfkr/xbetext.py`가 일본판에서 만든다. US판 대응은 P8). `Media` 파일은 US판에서도 같은 코드가 읽으므로 그대로 쓸 수 있을 것이다(**추정**, 화면 확인 전).

## P5-1 문장 형식과 추출 (issue #11)

근거: [analysis/message-script.md](analysis/message-script.md), [analysis/mission-files.md](analysis/mission-files.md), [analysis/xbe-strings.md](analysis/xbe-strings.md), [설계 i011](design/20261021-i011-text-extract.md)

* **메시지 스크립트(확인됨, 368개 왕복)**: 이벤트 항목 `2/0`과 대화 이벤트 `TE###.bin`은 같은 형식이다. `u32` 머리 9개(`[1]` 언어 수, `[4]` 메시지 수), (언어 × 메시지)마다 필드 5개(필드 0 = 페이지 수), 페이지별 `u32` 값, 그 뒤 페이지마다 "바이트 + `$r`"이 데이터 끝까지. 게임은 머리의 페이지 수로 문장을 나눈다(P1의 "길이로 끝을 안다" 추정을 대신한다). reJSRF가 런타임에 페이지를 바꿀 때 페이지 수가 같으면 머리를 그대로 두면 된다.
* **대화 이벤트 분기**: `$bc`/`$bj`/`$bo` 다음 1바이트와 `$s` 다음 2바이트는 2진 인자이고, `$bj` `$bo` `$s`의 인자는 같은 언어 구간 안의 페이지 번호로 보인다(**추정**). 문자열을 NUL이나 바이트열 검색으로 다루면 안 된다.
* **미션 파일(확인됨, 정적)**: 로더 `0x25DD0`(파일 크기만큼 할당), 재배치 `0x4DB30`, 문장 명령 opcode `0xBE 0xBF 0xC0 0xE8 0xE9 0xEA 0xEF`의 언어별 포인터 7칸(칸 0 = 일본어). **US판도 같은 주소, 같은 바이트**(같은 주소 바이트 비교). reJSRF가 미션 문장을 바꿀 때는 `0x4DB30` 뒤 칸 0 포인터를 새 문자열로 돌리거나, 파일 끝에 붙인 파일을 내줘도 된다.
* **XBE 문자열(확인됨, 일본판)**: `.rdata` 651개, `.data` 포인터 칸 1,083개 + `push` 23곳. US판 대응은 아직 없다(P8).
* 추출 단위와 자리(`norm:2/0+…`, `off:…`, `va:…`)는 `tools/extract_text.py`가 만들고 `patch/text/*.tsv`에 그대로 쓴다.

## P1 결과물 형식과 컨테이너 (issue #2)

근거: [analysis/containers.md](analysis/containers.md), [design/20261021-i002-patcher.md](design/20261021-i002-patcher.md)

* **`MULT`/`NORM` 컨테이너 형식(확인됨, 1,056개 파일 왕복)**: 머리 16바이트(마법값, 개수, 0, 0) 뒤에 16바이트 연결 `(start, end, size, flag)`이 사슬로 이어진다. 값은 그 컨테이너 머리 기준 상대값이고, 다음 연결은 앞 항목의 `end`에 있다. `MULT` 항목은 블록, `NORM` 항목은 데이터(16바이트 경계까지 0 패딩, 길이 0이면 `flag` 1). reJSRF `text-and-font.md`의 "레코드 머리에 시작·끝 오프셋과 크기"는 이 연결이다.
* **이벤트 문장 자리(확인됨)**: `Media/Event/Event/e###.dat`의 항목 경로 `2/0`(맨 위 `MULT`의 항목 2 안의 `NORM` 항목 0), 117개 파일. 항목 앞쪽은 `u32` 값들이고 문장 한 줄이 항목 끝까지 간다. NUL 종료는 항목 길이에 들어가지 않고, 5개 항목은 패딩도 없다. reJSRF가 런타임에 문장을 바꿀 때는 항목 길이(연결의 `size`)를 기준으로 해야 한다(**추정**: 게임이 길이로 끝을 안다). `e###.bin`에는 문장이 없다.
* 패치 데이터 형식(`patch/text/*.tsv`의 `off:`·`va:`·`norm:` 자리, `manifest.json`, `xbe/*.json`)은 reJSRF가 같은 문장을 런타임에 적용할 때 그대로 읽을 수 있게 정했다. 원문 대신 SHA-1이 있으므로, reJSRF는 그 자리의 원래 바이트를 해시로 확인한 뒤 바꾸면 된다.

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

## P3 Korean font (issue #6)

Basis: [design/20261020-i006-korean-font.md](design/20261020-i006-korean-font.md)

* Option A′: the renderer code stays; only the XBE `.data` glyph table `0x1F7088` (1,390 × 4 bytes) and the class first indexes `0x1F8B80`–`0x1F8B8F` change. The US build has the same addresses and original bytes.
* Hangul codes: the k-th of the 2,350 KS X 1001 syllables → the k-th code counting from `0x8890` with second bytes `0x40`–`0x7E` and `0x80`–`0xFC` only (`tools/font/hangul.py`). reJSRF can compute the same rule or take the table this repository builds.
* Table layout: Hangul (code order) → padding → hiragana and katakana (when there is room) → digits and capitals → symbols (`tools/font/glyph_table.py`).
* `jetfont.dat`: only tex0–3 are rebuilt in the new table order. Kept cells are moved; Hangul is drawn from Do Hyeon (OFL) into the ink box (2,3)–(23,22) of the 26×26 cell with one scale for all 2,350 syllables. The same input gives the same bytes.
* In reJSRF: write the same table to the US `0x1F7088` and `0x1F8B80` at run time, and serve the `jetfont.dat` built by this repository's tool through the `rexbox` file layer (**inferred**, checked in P4).

## P4 proof of concept (issue #8)

Basis: [analysis/text-files.md](analysis/text-files.md), [work log i008](work-logs/20261020-i008-poc.md), [guides/emulator-check.md](guides/emulator-check.md)

* **Confirmed in reJSRF's Japanese build** (reJSRF `4e2c0f2`, `build\win32_x86_jp` Release): with the patched Japanese XBE (`out/poc/rejsrf/default_jpn.xbe`, `--xbe default_jpn.xbe`) and the patched `Media`, Roboy's line in the garage shows "뭐야、무슨 볼일？" in Hangul. At 16:9 Hor+ the speech box and letters stay centered in place. reJSRF identifies the XBE by its certificate, so it accepts the patched XBE with its signature left unfixed.
* The same output looks the same in Cxbx-Reloaded and xemu. So the P3 approach (a data patch of the glyph table `0x1F7088` and the class first indexes `0x1F8B80`, plus a new `jetfont.dat`) works with reJSRF running the original renderer as it is.
* The US XBE + `REJSRF_LANGUAGE=Japanese` path (`out/poc/rejsrf/default.xbe`, the US build with the same table) was not run (**unresolved**). The US XBE's menu strings sit at other addresses and were not changed.
* **HDD cache**: the game copies a `Media` file to `Z:\Media\…` the first time it reads it and reads the cache afterwards. When testing the patch in reJSRF, `hdd\` (or `REJSRF_HDD_ROOT`) must not hold cached originals. A run-time patch must serve the same content for files read through the cache path (`Z:`) as well. `jetfont.dat` is never cached.
* Text places (Japanese build, confirmed by in-place replacement):

| Place | Content | US |
|---|---|---|
| `Media/Mission/mssn0110.bin` `0x2228C` | the first mission's objective (a Japanese NUL English NUL pair) | same `Media` |
| `Media/Event/TalkEvent/TE014.bin` `0x88` | Roboy's first line (a message inside one string) | same `Media` |
| XBE `.rdata` `0x1D29E0` | "セーブ" | not matched |
| XBE `.data` `0x221948` | the pause menu pointer table (per language) | not matched |
| XBE `.data` `0x2216DC`, `0x2221D8` | the retry menu and B-button hint tables | not matched |

* The Japanese build never writes the language global `0x251F58`, which agrees with the Japanese build's language being fixed to Japanese.

## P5-2 reinserting text whose length changes (issue #13)

Basis: [design i013](design/20261021-i013-text-reinsert.md), [work log i013](work-logs/20261021-i013-text-reinsert.md)

* Files whose length changes in this repository's patch output: events `e###.dat` (the pages of item `2/0` and the container links), talk `TE###.bin` (file size), missions `mssn####.bin` (strings appended at the end with slot-0 pointers), `default.xbe` (new section `KRTEXT` at VA `0x289000`, the section header table moved to `0x988`, the `.data` slots and `push` immediates of moved strings). Page counts never change.
* reJSRF runs the US XBE, so the XBE side cannot be used as is; it needs the same string references swapped for new strings at run time (the reference lists of moved strings come from `tools/jsrfkr/xbetext.py` on the Japanese build; the US counterparts are P8). The `Media` files are read by the same code in the US build, so they should work as they are (**inferred**, before the screen check).

## P5-1 text formats and extraction (issue #11)

Basis: [analysis/message-script.md](analysis/message-script.md), [analysis/mission-files.md](analysis/mission-files.md), [analysis/xbe-strings.md](analysis/xbe-strings.md), [design i011](design/20261021-i011-text-extract.md)

* **Message scripts (confirmed, round trip of 368)**: event item `2/0` and talk events `TE###.bin` share one format: 9 `u32` header values (`[1]` languages, `[4]` messages), 5 fields per (language × message) (field 0 = page count), one `u32` per page, then each page as "bytes + `$r`" to the end of the data. The game splits the text by the header's page counts (replacing P1's "finds the end by length" inference). When reJSRF changes pages at run time with the page count unchanged, the header stays as it is.
* **Talk-event branches**: the byte after `$bc`/`$bj`/`$bo` and the two bytes after `$s` are binary arguments; those of `$bj` `$bo` `$s` appear to be page numbers inside the same language block (**inferred**). Do not handle these strings by NUL or byte-pattern search.
* **Mission files (confirmed, static)**: loader `0x25DD0` (allocates the file's size), relocation `0x4DB30`, and the 7 per-language pointers (slot 0 = Japanese) of text commands with opcodes `0xBE 0xBF 0xC0 0xE8 0xE9 0xEA 0xEF`. **The US build has the same code at the same addresses, byte for byte** (compared at the same address). To change a mission string, reJSRF can point slot 0 at a new string after `0x4DB30`, or serve a file with the string appended.
* **XBE strings (confirmed, Japanese build)**: 651 in `.rdata`, referenced by 1,083 `.data` pointer slots and 23 `push`es; no US counterparts yet (P8).
* The extraction units and places (`norm:2/0+…`, `off:…`, `va:…`) are produced by `tools/extract_text.py` and used as they are in `patch/text/*.tsv`.

## P1 deliverable format and containers (issue #2)

Basis: [analysis/containers.md](analysis/containers.md), [design/20261021-i002-patcher.md](design/20261021-i002-patcher.md)

* **The `MULT`/`NORM` container format (confirmed, round trip of 1,056 files)**: a 16-byte header (magic, count, 0, 0) followed by a chain of 16-byte links `(start, end, size, flag)`, relative to the container's header, each next link at the previous item's `end`. `MULT` items are blocks, `NORM` items data (zero-padded to 16 bytes; `flag` 1 for length 0). The "record headers with start and end offsets and a size" of reJSRF's `text-and-font.md` are these links.
* **Where event text sits (confirmed)**: item path `2/0` of `Media/Event/Event/e###.dat` (`NORM` item 0 inside item 2 of the top-level `MULT`), 117 files. The item starts with `u32` values and one line of text runs to its end; the NUL terminator is not counted in the item length, and 5 items have no padding either. A run-time text replacement in reJSRF should go by the item length (the link's `size`) (**inferred**: the game finds the end by length). The `e###.bin` files hold no text.
* The patch data format (`off:`, `va:` and `norm:` places in `patch/text/*.tsv`, `manifest.json`, `xbe/*.json`) is meant for reJSRF to read as it is when applying the same text at run time; with SHA-1 in place of the original text, reJSRF checks the original bytes at a place by hash before replacing them.
