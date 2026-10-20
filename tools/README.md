# 도구

모두 Python 표준 라이브러리만 쓴다(Python 3.10 이상, 확인은 3.12). 저장소 루트에서 `python -I`로 실행한다. 사용자 덤프는 읽기만 하고, 쓰는 곳은 `out/`(패치 결과물)과 `work/`(중간 결과)뿐이다. 둘 다 게임 자료에서 나온 것이라 커밋하지 않는다.

| 경로 | 하는 일 | issue |
|---|---|---|
| `patch.py` | **패치 도구**: 덤프 → 패치된 게임 폴더(`out/` 아래), 선택으로 xiso | #2 |
| `check_roundtrip.py` | 덤프의 `MULT`/`NORM` 파일 전체와 XBE 요약값 왕복, 패치 결과 폴더와 덤프 비교 | #2 |
| `jsrfkr/` | 공용 모듈: `xbe`, `container`(`MULT`/`NORM`), `encode`, `textpatch`, `xbepatch`, `digest`, `xiso` | #2 |
| `font/` | 한국어 글꼴(A′): 글리프 표와 `jetfont.dat` 만들기([README](font/README.md)) | #6 |
| `analysis/` | 분석 스크립트([README](analysis/README.md)) | #3 |
| `poc/` | 개념 증명 도구: reJSRF용 US XBE 폴더 포함([README](poc/README.md)) | #8 |

## 패치 도구

```bash
python -I tools/patch.py "roms/Jet Set Radio Future" out/jsrf-kr
python -I tools/patch.py "roms/Jet Set Radio Future" out/jsrf-kr --iso "roms/Jet Set Radio Future.iso"
```

* 입력 검사: [patch/manifest.json](../patch/manifest.json)의 MD5가 덤프와 다르면 아무것도 쓰지 않고 멈춘다.
* 출력 폴더는 `out/` 아래의 없거나 빈 폴더여야 한다. 덤프 폴더 전체를 복사하고 바뀐 파일만 새로 쓴다. 바뀐 파일의 MD5는 `<출력>/md5.txt`에 있다.
* `--iso <xiso>`: 출력 폴더 옆에 `<출력>.iso`를 만든다(사용자 xiso 사본에 바뀐 파일을 같은 크기로 덮어씀).
* `--link`: 바뀌지 않은 파일을 복사 대신 하드링크로 둔다(같은 드라이브, 디스크 절약). **이때 출력 폴더의 그 파일을 고치면 덤프도 바뀐다.**
* `--text <파일 또는 폴더>`: 문장 패치를 바꾼다(기본 `patch/text`). 예: `--text patch/poc/lines.tsv`(P4 시험 문장).
* `--identity`: 원래 글리프 표, 문장·XBE 패치 없이 만든다(왕복 시험).
* `--update-manifest`: 문장 패치가 건드리는 파일의 MD5를 덤프에서 읽어 `manifest.json`에 더한다.

사용자용 절차는 [docs/guides/apply-patch.md](../docs/guides/apply-patch.md)에 있다.

## 시험

```bash
python -I -m unittest discover -s tests
python -I tools/check_roundtrip.py "roms/Jet Set Radio Future"
python -I tools/patch.py "roms/Jet Set Radio Future" out/identity --identity
python -I tools/check_roundtrip.py "roms/Jet Set Radio Future" --output out/identity
```

* 단위 시험(`tests/`)은 게임 자료 없이 돈다.
* `check_roundtrip.py`는 원문을 출력하지 않는다. `--identity` 출력 폴더는 덤프와 모든 파일이 같아야 한다. 확인한 뒤 지운다(2.4GB).

---

# Tools

Standard library only (Python 3.10 or later; checked with 3.12). Run from the repository root with `python -I`. The user's dump is only read; the tools write only to `out/` (patched output) and `work/` (intermediates), both derived from game data and never committed.

| Path | What it does | Issue |
|---|---|---|
| `patch.py` | **the patcher**: dump → patched game folder (under `out/`), optionally an xiso | #2 |
| `check_roundtrip.py` | round trips of every `MULT`/`NORM` file in the dump and the XBE digests; compares a patched folder with the dump | #2 |
| `jsrfkr/` | shared modules: `xbe`, `container` (`MULT`/`NORM`), `encode`, `textpatch`, `xbepatch`, `digest`, `xiso` | #2 |
| `font/` | the Korean font (A′): building the glyph table and `jetfont.dat` ([README](font/README.md)) | #6 |
| `analysis/` | analysis scripts ([README](analysis/README.md)) | #3 |
| `poc/` | the proof-of-concept tool, including the US XBE folder for reJSRF ([README](poc/README.md)) | #8 |

## The patcher

(Commands above.)

* Input checks: if an MD5 in [patch/manifest.json](../patch/manifest.json) differs from the dump, nothing is written.
* The output must be an absent or empty folder under `out/`. The whole dump folder is copied and only the changed files are written anew; their MD5s are in `<output>/md5.txt`.
* `--iso <xiso>`: also writes `<output>.iso` (a copy of the user's xiso with the changed files overwritten at the same size).
* `--link`: hard-links unchanged files instead of copying them (same drive, saves disk). **Editing such a file in the output then edits the dump too.**
* `--text <file or folder>`: another text patch (default `patch/text`), for example `--text patch/poc/lines.tsv` (the P4 test lines).
* `--identity`: builds with the original glyph table and no text or XBE patches (round trip).
* `--update-manifest`: adds the dump's MD5 for every file the text patches touch to `manifest.json`.

The user procedure is in [docs/guides/apply-patch.md](../docs/guides/apply-patch.md).

## Tests

(Commands above.)

* The unit tests (`tests/`) need no game data.
* `check_roundtrip.py` prints no original text. A `--identity` output folder must equal the dump file for file; delete it after checking (2.4 GB).
