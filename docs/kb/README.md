# JSRF-kr-patch 기술 지식 기반 색인

이 디렉터리는 프로젝트를 이해하는 데 필요한 일반 기술 지식(문자 인코딩, 텍스처 압축, XBE 형식, 글꼴 라이선스 등)과 번역 용어집을 정리한다. 일본판 바이너리에서 직접 확인한 사실은 `docs/analysis/`에 기록한다. 외부 자료에서 얻은 정의와 규약에는 원문 링크를 함께 둔다.

## 문서

| 문서 | 내용 |
|---|---|
| [shift-jis.md](shift-jis.md) | Shift-JIS(CP932) 바이트 구조와 구획, JSRF 렌더러의 2바이트 판정(`0x80`~`0x9F`) |
| [dxt3.md](dxt3.md) | DXT3(BC2) 블록 압축, `jetfont.dat`의 흰색 + 4비트 alpha |
| [glossary.md](glossary.md) | 용어집: 캐릭터·팀·장소·게임 용어·기술 이름의 한국어 표기, 쓸 수 있는 기호(#15) |

번역 단계(P6)에서 `glossary.md`(캐릭터·장소·기술 이름 표기)를 만든다.

---

# JSRF-kr-patch knowledge base index

This directory collects general technical knowledge the project needs (character encodings, texture compression, the XBE format, font licensing, ...) and the translation glossary. Facts confirmed on the Japanese binary go in `docs/analysis/`. Definitions and conventions from external sources carry links to them.

## Documents

| Document | Content |
|---|---|
| [shift-jis.md](shift-jis.md) | Shift-JIS (CP932) byte structure and blocks; the JSRF renderer's double-byte test (`0x80`–`0x9F`) |
| [dxt3.md](dxt3.md) | DXT3 (BC2) block compression; white plus 4-bit alpha in `jetfont.dat` |
| [glossary.md](glossary.md) | the glossary: Korean forms of characters, teams, places, game terms and trick names; usable symbols (#15) |

The translation phase (P6) adds `glossary.md` (how character, place and trick names are written).
