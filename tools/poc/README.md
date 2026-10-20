# 개념 증명 도구 (issue #8)

한국어 시험 문장 몇 줄을 제자리에 바꿔 넣어 화면에서 확인하는 도구다. 설계는 [docs/design/20261020-i008-poc.md](../../docs/design/20261020-i008-poc.md)에 있다. 표준 라이브러리만 쓰고, 글꼴은 [tools/font](../font/README.md)(P3)의 모듈로 만든다. 사용자 덤프를 읽기만 하고 출력은 `out/` 아래에 쓴다. 출력에는 게임 자료가 들어 있으므로 커밋하지 않는다. 정식 패치 도구는 P1(issue #2)에서 만들고, 이 모듈들을 그쪽으로 옮긴다.

| 파일 | 하는 일 |
|---|---|
| `encode.py` | 한국어(UTF-8) → 게임 바이트열. 한글은 P3 고정 대응, 나머지는 cp932. 새 글리프 표에 없는 2바이트 코드와 1바이트 표에 없는 글자는 거부한다 |
| `xiso.py` | XDVDFS(xiso) 읽기, 경로로 파일 찾기, 같은 크기 덮어쓰기. 단독 실행: 파일 목록과 MD5 |
| `build_poc.py` | 명령줄: 입력 MD5 검증 → 글꼴 → 제자리 교체 → 섹션 요약값 → 출력 세 가지 |

패치 데이터는 [patch/poc/lines.tsv](../../patch/poc/lines.tsv)다. 열은 `file`(덤프 기준 경로), `where`(`off:0x…` 파일 위치 또는 `va:0x…` XBE 가상 주소), `orig_len`(원문 바이트 수), `orig_sha1`(원문 바이트의 SHA-1), `korean`, `pad`다. 원문은 넣지 않는다. 도구는 그 자리의 바이트가 해시와 같을 때만 바꾼다. `pad`는 남는 바이트를 무엇으로 채울지 정한다.

* `nul`(기본): 문자열 하나 전체를 바꾼다. 원문 바로 뒤가 NUL이어야 한다.
* `space`: 긴 문자열 안의 메시지 하나(대화 이벤트의 한 쪽 등)를 바꾸고 남는 자리를 `0x20`으로 채운다.

## 사용법

```bash
python -I tools/poc/build_poc.py "roms/Jet Set Radio Future" "roms/Jet Set Radio Future.iso" out/poc
```

* 출력:
  * `out/poc/files/`: 바뀐 파일(`default.xbe`, `Media/Font/jetfont.dat`, 미션·대화 이벤트 파일)
  * `out/poc/jsrf-kr-poc.iso`: 사용자 xiso의 사본에 바뀐 파일을 같은 크기로 덮어쓴 것(xemu용)
  * `out/poc/rejsrf/`: reJSRF용 게임 폴더. `default.xbe`는 같은 글리프 표를 넣은 US판, `default_jpn.xbe`는 패치한 일본판이고, `Media`의 바뀌지 않은 파일은 하드링크다
* 약 1분(xiso 2.5GB 복사). xemu가 그 ISO를 쓰고 있으면 끄고 실행하거나 `--skip-iso`를 쓴다. `--skip-rejsrf`는 reJSRF 폴더를 만들지 않는다.
* US판 XBE는 기본으로 `<덤프>/default_eng.xbe`(MD5 `f4e366bf…`)를 쓴다. `--us-xbe`로 바꾼다. `--lines`로 다른 문장 파일을 준다.
* 출력 끝에 파일마다 MD5가 나온다. 같은 입력이면 늘 같은 값이다.

## 검증

* 왕복 시험: `--identity`는 원래 글리프 표로 문장 없이 만든다. 모든 출력(`default.xbe` 두 개, `jetfont.dat`, xiso 사본)이 원본과 MD5가 같아야 한다. 출력 폴더는 따로 준다(예: `out/poc-identity`). 끝나면 지운다(2.5GB).
* 화면 확인: [docs/guides/emulator-check.md](../../docs/guides/emulator-check.md). 에뮬레이터의 HDD 캐시를 먼저 지워야 한다.

---

# Proof-of-concept tools (issue #8)

Tools that put a few Korean test lines in place and check them on screen. The design is in [docs/design/20261020-i008-poc.md](../../docs/design/20261020-i008-poc.md). Standard library only; the font is built with the modules of [tools/font](../font/README.md) (P3). They only read the user's dump and write under `out/`; the output holds game data and is never committed. The proper patcher is P1 (issue #2), and these modules move there.

| File | What it does |
|---|---|
| `encode.py` | Korean (UTF-8) → game bytes; Hangul by the fixed P3 mapping, everything else as cp932; refuses double-byte codes missing from the new glyph table and characters missing from the single-byte table |
| `xiso.py` | XDVDFS (xiso) reading, file lookup by path, same-size overwrite; run alone it lists files and MD5s |
| `build_poc.py` | command line: input MD5 checks → font → in-place replacement → section digests → three outputs |

The patch data is [patch/poc/lines.tsv](../../patch/poc/lines.tsv), with the columns `file` (path in the dump), `where` (`off:0x…` file offset or `va:0x…` XBE virtual address), `orig_len` (original byte count), `orig_sha1` (SHA-1 of the original bytes), `korean` and `pad`. No original text is stored; the tool replaces a place only when its bytes match the hash. `pad` sets what fills the leftover bytes:

* `nul` (the default): replaces a whole string; a NUL must follow the original.
* `space`: replaces one message inside a longer string (such as one page of a talk event) and fills the rest with `0x20`.

## Usage

The command is above.

* Outputs:
  * `out/poc/files/`: the changed files (`default.xbe`, `Media/Font/jetfont.dat`, mission and talk-event files)
  * `out/poc/jsrf-kr-poc.iso`: a copy of the user's xiso with the changed files overwritten at the same size (for xemu)
  * `out/poc/rejsrf/`: a game folder for reJSRF; `default.xbe` is the US build with the same glyph table, `default_jpn.xbe` the patched Japanese build, and unchanged `Media` files are hard links
* About a minute (copies the 2.5 GB xiso). If xemu is using that ISO, close it first or pass `--skip-iso`; `--skip-rejsrf` skips the reJSRF folder.
* The US XBE defaults to `<dump>/default_eng.xbe` (MD5 `f4e366bf…`); `--us-xbe` changes it, and `--lines` gives another line file.
* The output ends with an MD5 per file; the same input always gives the same values.

## Verification

* Round trip: `--identity` builds with the original glyph table and no lines; every output (both `default.xbe`s, `jetfont.dat`, the xiso copy) must have its original's MD5. Give a separate output folder (for example `out/poc-identity`) and delete it afterwards (2.5 GB).
* On screen: [docs/guides/emulator-check.md](../../docs/guides/emulator-check.md); clear the emulator's HDD cache first.
