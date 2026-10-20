# XBE 패치

`tools/patch.py`가 일본판 `default.xbe`에 쓰는 바이트 패치(코드·자료)다. 이 폴더의 `*.json`을 파일 이름 순서로 읽는다. 지금은 없다. 글리프 표는 도구가 문장에서 계산하므로 여기 넣지 않는다. 형식의 근거는 [설계 i002 §3.3](../../docs/design/20261021-i002-patcher.md)이다.

```json
{
  "reason": "왜 바꾸는지",
  "patches": [
    {"va": "0x001F7088", "orig_sha1": "<원래 바이트의 SHA-1>", "bytes": "<새 바이트, 16진수>"}
  ]
}
```

* 우리가 쓴 바이트만 넣는다. 원래 바이트는 넣지 않고 SHA-1로만 확인한다.
* 주소는 일본판 가상 주소다. 한 패치는 한 섹션의 파일 자료 안에 있어야 한다. 두 패치가 겹치면 멈춘다.
* 바꾼 섹션의 요약값은 도구가 다시 계산한다.

---

# XBE patches

Byte patches (code and data) that `tools/patch.py` writes into the Japanese `default.xbe`: every `*.json` in this folder, in file-name order. None yet. The glyph table is computed by the tool from the text and does not go here. The format rests on [design i002 §3.3](../../docs/design/20261021-i002-patcher.md).

(Example above; `reason` says why the change is needed.)

* Only bytes we wrote go in; the original bytes are never stored, only checked by SHA-1.
* Addresses are Japanese virtual addresses; a patch must lie within one section's file data; overlapping patches stop the tool.
* The tool recomputes the changed sections' digests.
