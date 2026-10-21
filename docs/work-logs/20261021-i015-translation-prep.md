# 작업 로그: 번역 준비 — 용어집, XBE 기능 문구 초벌 번역, 번역 도구와 지침 (issue #15, P6-0)

설계: [20261021-i015](../design/20261021-i015-translation-prep.md), 작업 지시: [20261021-i015](../work-orders/20261021-i015-translation-prep.md), 브랜치 `i015-translation-prep`.

## 1. 결과

* `patch/text/`에 뼈대 네 개를 넣고, `xbe.tsv`의 기능 문구 **544줄**을 초벌 번역했다(651줄 중). 기본 패치 출력에 들어간다.
* 번역 검사 도구 `tools/check_text.py`: 출력 없이 모든 오류·경고·진행률·한글 음절 수를 보이고, `--review`로 번역자용 검토 표를 만든다. 검토 표에는 **번역이 아닌 도움 정보**(그 줄의 용어와 용어집 표기, 지켜야 할 코드, 줄 한도)를 넣었다.
* 용어집 `docs/kb/glossary.md`(용어 119개), 번역자 가이드 `docs/guides/translation.md`, PLAN P6 갱신(P6-0 준비 + P6-1~ 사람 번역).
* 사용자 요청과 결정(2026-10-21): 사용자는 번역을 AI가 하길 원했다. 게임 대사 전체의 번역(초벌 포함)은 AI 작업 원칙(저작물 원문 재현 금지) 때문에 하지 않기로 했고, 사용자가 대안(용어집·기능 문구 초벌·도구·지침)을 골랐다. 대사 칸에 초벌을 넣는 것도 같은 이유로 하지 않고, 위의 도움 정보로 대신했다.

## 2. 한 일

1. `tools/jsrfkr/pipeline.py`: `patch.py`의 글꼴·인코딩 단계를 나눴다(`patch.py`와 `check_text.py`가 함께 씀). P4 시험 문장 출력 MD5가 그대로다(`default.xbe` `cbb44a11…`, `TE014.bin` `ef4ad91e…` 등).
2. `tools/check_text.py`: 파일별 적용, 실패한 파일은 줄마다 다시 적용해 모든 오류를 모은다. 진행률(번역 줄·바이트·옮김·오류·경고), 음절 수, `--review`.
3. `tools/jsrfkr/glossary.py`: 용어집 표 읽기와 줄별 용어 힌트(긴 용어 먼저, 겹치지 않게).
4. **인코더 수정**: 전각 공백 `0x8140`(U+3000)을 쓸 수 있게 했다. 렌더러가 그리지 않고 한 칸만큼 나아가는 특수 코드라 글리프 표에 없는데, 인코더가 표에서 찾고 있었다(text-renderer §4.1). 원문의 자리 맞춤 공백을 옮기려면 필요하다.
5. XBE 초벌: 실황 대사(`va:0x1d0934`~`va:0x1d1b10`) 67줄, 숫자·크기 글자·`Ｘ`·`ＮＴ－３０００`·`ＤＪＫ` 같은 바꿀 필요가 없는 줄 40줄은 비웠다. 스크래치 스크립트로 넣고 다음을 확인했다.
   * 모든 줄의 `$`·`%` 코드가 원문과 같은 순서(544/544).
   * 자리 표시: `va:0x1de0b8`의 전각 공백 두 칸 앞이 원문과 같은 20바이트, `va:0x1de1b4`의 `GRAFFITI     `는 그대로 맨 앞.
   * 끝을 전각 공백으로 채운 그래피티 편집기 안내 15줄은 원문 길이까지 채웠고, 가운데 맞춤 3줄은 양쪽을 채웠다.
   * 원문보다 긴 줄을 44줄에서 **7줄**로 줄였다(뜻을 해치지 않게 띄어쓰기·낱말 조정). 7줄은 새 섹션 `KRTEXT`로 옮겨진다.
   * 쓸 수 없던 기호 `＜＞` `－`는 `<>` `ー`로 바꿨다. 새 글리프 표에 남은 2바이트 기호는 `、。，．・：？！々ー／＼～…“”（）「」『』￥％＆※♪`다(용어집 §7).
6. 시험 `tests/test_check_text.py`(용어집 읽기·힌트, 메시지 출처, 코드, 진행률, 한도), `test_textpatch.py`에 전각 공백 인코딩.
7. 문서: 용어집, 번역 가이드, `text-pipeline.md`·`docs/README.md`·`kb/README.md`·`tools/README.md`·`patch/text/README.md`·PLAN.

## 3. 검증

| 항목 | 결과 |
|---|---|
| 단위 시험 | 54개 통과 |
| `check_text.py` | `xbe.tsv` 544/651줄, 한국어 9,441바이트, 옮김 7, **오류 0, 경고 0**. 한글 음절 474자(가나 유지 한도 1,158) |
| 오류 모으기 | 틀린 줄 넷(글자, `$r` 추가, 해시)을 섞은 파일에서 오류 3개를 한 번에 보고, 끝 코드 1 |
| 검토 표 | 대화 733줄 중 326줄에 용어 힌트. 모든 줄에 코드·한도 열 |
| `patch.py`(기본 `patch/text`) | 544곳, 7곳 옮김, 경고 0. `default.xbe` `cbeb2c7aaa47fa6ce40c048e6d5c6f5f`, `jetfont.dat` `11ef97403a0843ffb387aba2a1287d63` |
| `check_reinsert.py` | `all round trips hold` |
| 화면 | 확인하지 않음(issue #13의 화면 확인과 함께 사용자에게 부탁) |
| `git status` | `roms/`, `out/`, `work/` 없음 |

## 4. 사람 검토가 필요한 줄 (기능 문구와 대사의 경계)

* 차고 메뉴 설명(`va:0x1d857c` 등 6줄): 말투가 있는 메뉴 설명이라 기능 문구로 보고 반말로 옮겼다.
* 확인·선택 질문(`va:0x1cca10` `va:0x1d0894` `va:0x1dd6c0` `va:0x1dd79c` 등): 짧은 반말로 옮겼다.
* 그래피티 이름 124줄(`va:0x1d9938`~`va:0x1da2a8`): 짧은 이름이라 옮겼고, 일본어 말장난은 뜻을 살렸다(예: 天高く馬肥ゆる秋 → 천고마비의가을). 영어판 이름과 맞출지 검토가 필요하다.
* 기술 이름 중 확실하지 않은 낱말(`スティルジュード` → 스틸 주드, `バドミックミュート` → 바드믹 뮤트, `ロックマック` → 록맥, `リューカン` → 류칸): 영어판 표기를 확인해 고친다.
* `アクム` → 아쿠무: 무엇인지 확인하지 않았다.

## 5. 계획과 달라진 것

* 인코더의 전각 공백 처리(§2의 4)는 계획에 없던 수정이다.
* 사용자가 작업 중 "번역자를 돕는 초벌 문구를 `korean` 칸에 넣을 수 있는지" 물었다. 대사 초벌은 같은 원칙으로 하지 않고, `korean` 칸은 비어 있어야 미번역으로 남는다는 기술적 이유도 설명했다. 대신 검토 표에 용어·코드·한도 열을 넣었다(설계 §4를 넓힘).

## 6. 다음

* P6-1~ 사람 번역 issue(미션, 대화, 이벤트, XBE 실황): 번역자가 정해지면 만든다.
* 화면 확인: issue #13의 긴 문장과 함께 XBE 메뉴·안내 초벌이 화면에 맞게 나오는지.

---

# Work log: translation preparation — glossary, first pass of XBE functional strings, translation tools and guidelines (issue #15, P6-0)

Design: [20261021-i015](../design/20261021-i015-translation-prep.md); work order: [20261021-i015](../work-orders/20261021-i015-translation-prep.md); branch `i015-translation-prep`.

## 1. Result

* The four skeletons went into `patch/text/`, and **544 functional rows** of `xbe.tsv` (of 651) got a first-pass translation, now in the default patch output.
* The check tool `tools/check_text.py` shows every error and warning, progress and the Hangul syllable count without output, and `--review` writes review tables for translators carrying **help that is not translation** (the line's terms with their glossary forms, the codes to keep, the line limits).
* The glossary `docs/kb/glossary.md` (119 terms), the translator guide `docs/guides/translation.md`, and the PLAN P6 update (P6-0 preparation + P6-1 on, human translation).
* The user's request and decision (2026-10-21): the user wanted AI to translate. Translating the whole game dialogue (drafts included) was declined under the AI working principle (no reproduction of copyrighted originals), and the user chose the alternatives (glossary, first pass of functional strings, tools, guidelines). Dialogue drafts in the `korean` column were declined for the same reason and replaced by the help columns above.

## 2. Done

1. `tools/jsrfkr/pipeline.py`: the font and encoding steps split out of `patch.py` (shared by `patch.py` and `check_text.py`); the P4 test lines' output MD5s are unchanged (`default.xbe` `cbb44a11…`, `TE014.bin` `ef4ad91e…` and so on).
2. `tools/check_text.py`: applies per file and re-applies a failing file row by row to collect every error; progress (rows, bytes, moves, errors, warnings), the syllable count, `--review`.
3. `tools/jsrfkr/glossary.py`: reading the glossary tables and per-line term hints (longest terms first, no overlaps).
4. **Encoder fix**: the full-width space `0x8140` (U+3000) can now be used. It is a special code the renderer advances over without drawing, so it is not in the glyph table, but the encoder looked it up there (text-renderer §4.1); carrying the original's alignment spaces needs it.
5. XBE first pass: the 67 commentary lines (`va:0x1d0934`–`va:0x1d1b10`) and 40 rows needing no change (digits, size letters, `Ｘ`, `ＮＴ－３０００`, `ＤＪＫ` and the like) were left empty. Merged with a scratch script, checking:
   * the `$` and `%` codes of every row in the original's order (544/544);
   * placeholders: the part before the two full-width spaces of `va:0x1de0b8` is 20 bytes as in the original, and the `GRAFFITI     ` of `va:0x1de1b4` stays at the start;
   * the 15 graffiti editor hints padded with full-width spaces up to the original length, and the 3 centred rows padded on both sides;
   * rows longer than the original cut from 44 to **7** (spacing and word choice, keeping the sense); the 7 move to the new section `KRTEXT`;
   * the unusable symbols `＜＞` `－` became `<>` `ー`; the double-byte symbols kept in the new glyph table are `、。，．・：？！々ー／＼～…“”（）「」『』￥％＆※♪` (glossary §7).
6. Tests `tests/test_check_text.py` (glossary parsing and hints, message sources, codes, progress, limits) and full-width space encoding in `test_textpatch.py`.
7. Documents: the glossary, the translation guide, `text-pipeline.md`, `docs/README.md`, `kb/README.md`, `tools/README.md`, `patch/text/README.md`, PLAN.

## 3. Verified

| Item | Result |
|---|---|
| unit tests | 54 pass |
| `check_text.py` | `xbe.tsv` 544/651 rows, 9,441 Korean bytes, 7 moved, **0 errors, 0 warnings**; 474 Hangul syllables (kana kept up to 1,158) |
| error collection | a file mixing four bad rows (character, added `$r`, hash) reports 3 errors at once, exit code 1 |
| review tables | term hints on 326 of the 733 talk rows; code and limit columns on every row |
| `patch.py` (default `patch/text`) | 544 places, 7 moved, 0 warnings; `default.xbe` `cbeb2c7aaa47fa6ce40c048e6d5c6f5f`, `jetfont.dat` `11ef97403a0843ffb387aba2a1287d63` |
| `check_reinsert.py` | `all round trips hold` |
| screen | not checked (requested from the user together with issue #13's screen check) |
| `git status` | no `roms/`, `out/`, `work/` |

## 4. Rows needing human review (the line between functional strings and dialogue)

* Garage menu descriptions (`va:0x1d857c` and 5 more): menu descriptions with a speaking tone, treated as functional and rendered casually.
* Confirmation and choice prompts (`va:0x1cca10`, `va:0x1d0894`, `va:0x1dd6c0`, `va:0x1dd79c` and others): short, casual.
* The 124 graffiti names (`va:0x1d9938`–`va:0x1da2a8`): short names, translated, Japanese puns rendered by sense (for example the proverb about autumn skies becomes its Korean idiom); whether to match the English edition's names needs review.
* Uncertain trick-name words (`スティルジュード` → 스틸 주드, `バドミックミュート` → 바드믹 뮤트, `ロックマック` → 록맥, `リューカン` → 류칸): to be fixed against the English edition.
* `アクム` → 아쿠무: not identified.

## 5. Deviations from the plan

* The encoder's full-width space handling (§2 item 4) was not planned.
* Mid-task the user asked whether draft phrases could go into the `korean` column to help translators. Dialogue drafts were declined on the same principle, with the technical reason that an empty `korean` is what keeps a row untranslated; the review table's term, code and limit columns were added instead (widening design §4).

## 6. Next

* P6-1 on, human-translation issues (missions, talk, events, XBE commentary), opened when translators are chosen.
* Screen check: together with issue #13's long lines, whether the XBE menu and notice first pass shows properly.
