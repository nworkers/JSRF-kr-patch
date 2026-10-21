# 문장 패치

`tools/patch.py`가 읽는 한국어 문장이다. 이 폴더의 `*.tsv`를 파일 이름 순서로 모두 읽는다. 지금은 번역이 없어 비어 있다(P6에서 채운다). 개념 증명 시험 문장은 [../poc/lines.tsv](../poc/lines.tsv)에 따로 있다. 형식의 근거는 [설계 i002 §3.1](../../docs/design/20261021-i002-patcher.md)이다.

UTF-8, 탭으로 나눈다. `#`로 시작하는 줄은 설명이다. 첫 줄(설명 제외)은 열 이름이다.

| 열 | 뜻 |
|---|---|
| `file` | 덤프 기준 경로(`default.xbe`, `Media/...`) |
| `where` | `off:0x…` 파일 위치, `va:0x…` XBE 가상 주소, `norm:<항목 경로>+0x…` `MULT`/`NORM` 항목 안 위치(예: `norm:2/0+0x60`) |
| `orig_len` | 원문 바이트 수(NUL 제외) |
| `orig_sha1` | 원문 바이트의 SHA-1. **원문은 적지 않는다** |
| `korean` | 한국어. **비우면 번역하지 않은 줄**(원문 그대로) |
| `pad` | `nul`(기본, 남는 바이트를 NUL로) 또는 `space`(긴 문자열 안의 메시지, 남는 바이트를 공백으로) |

* 번역할 자리와 원문 해시는 추출 도구가 만든다(`tools/extract_text.py`의 뼈대). 단계별 절차는 [docs/guides/text-pipeline.md](../../docs/guides/text-pipeline.md).
* 한국어는 원문보다 길어도 된다(issue #13, [설계 i013](../../docs/design/20261021-i013-text-reinsert.md)): 이벤트·대화는 페이지를 바꿔 파일을 다시 만들고(`pad`는 쓰지 않음), 미션은 파일 끝에 붙이고, XBE는 새 섹션으로 옮긴다. 그 밖의 자리는 제자리 교체만 된다. 페이지(`$r`)·메시지(`$e`)·분기 코드의 수와 순서는 원문과 같아야 한다.
* 같은 파일에 `norm:`과 `off:`·`va:`를 섞어 쓰지 않는다.
* 문장이 건드리는 파일은 [../manifest.json](../manifest.json)에 MD5가 있어야 한다. `python -I tools/patch.py <덤프> --update-manifest`가 채운다.
* 한글은 KS X 1001 2,350자만, 그 밖의 글자는 새 글리프 표에 남은 기호·숫자·영대문자·가나만 쓸 수 있다. 쓸 수 없는 글자가 있으면 도구가 그 글자를 알리고 멈춘다.

---

# Text patches

The Korean text `tools/patch.py` reads: every `*.tsv` in this folder, in file-name order. Empty for now, as there is no translation yet (filled in P6). The proof-of-concept test lines are kept apart in [../poc/lines.tsv](../poc/lines.tsv). The format rests on [design i002 §3.1](../../docs/design/20261021-i002-patcher.md).

UTF-8, tab-separated; lines starting with `#` are comments; the first other line names the columns.

| Column | Meaning |
|---|---|
| `file` | path in the dump (`default.xbe`, `Media/...`) |
| `where` | `off:0x…` file offset, `va:0x…` XBE virtual address, `norm:<item path>+0x…` offset inside a `MULT`/`NORM` item (for example `norm:2/0+0x60`) |
| `orig_len` | original byte count (NUL excluded) |
| `orig_sha1` | SHA-1 of the original bytes; **the original text is never written** |
| `korean` | Korean; **empty = an untranslated row** (the original stays) |
| `pad` | `nul` (the default; leftover bytes become NUL) or `space` (a message inside a longer string; leftover bytes become spaces) |

* The places and original hashes come from the extraction tool (the skeleton of `tools/extract_text.py`); the step-by-step procedure is [docs/guides/text-pipeline.md](../../docs/guides/text-pipeline.md).
* Korean may be longer than the original (issue #13, [design i013](../../docs/design/20261021-i013-text-reinsert.md)): event and talk pages are replaced and the file rebuilt (`pad` unused), mission strings are appended at the end of the file, XBE strings move to a new section; other places only allow in-place replacement. The number and order of page (`$r`), message (`$e`) and branch codes must match the original.
* Do not mix `norm:` with `off:`/`va:` in the same file.
* Every file the text touches needs its MD5 in [../manifest.json](../manifest.json); `python -I tools/patch.py <dump> --update-manifest` fills it in.
* Hangul is limited to the 2,350 KS X 1001 syllables, and other characters to the symbols, digits, capitals and kana kept in the new glyph table; the tool names any character it cannot use and stops.
