# 작업 로그: 텍스트 번역 (xbe, event, mission, talk 100% 번역 및 검증 완료) (issue #17)
# Work Log: Text Translation (xbe, event, mission, talk 100% translated and validated) (issue #17)

설계: [20261022-i017](../design/20261022-i017-text-translation.md), 작업 지시: [20261022-i017](../work-orders/20261022-i017-text-translation.md), 브랜치 `i017-translate-text`.

Design: [20261022-i017](../design/20261022-i017-text-translation.md), Work Order: [20261022-i017](../work-orders/20261022-i017-text-translation.md), Branch `i017-translate-text`.

## 1. 진행 결과 (Progress Summary)

* `patch/text/xbe.tsv`: 651/651행 전수 번역 완료 (0 오류, 0 경고)
* `patch/text/event.tsv`: 397/397행 전수 번역 완료 (0 오류, 0 경고)
* `patch/text/mission.tsv`: 495/495행 전수 번역 완료 (0 오류, 0 경고)
* `patch/text/talk.tsv`: 733/733행 전수 번역 완료 (0 오류, 0 경고)
* **전체 번역 대상 2,276행 100% 번역 및 전수 검증 통과**

* `patch/text/xbe.tsv`: 651/651 rows 100% translated (0 errors, 0 warnings).
* `patch/text/event.tsv`: 397/397 rows 100% translated (0 errors, 0 warnings).
* `patch/text/mission.tsv`: 495/495 rows 100% translated (0 errors, 0 warnings).
* `patch/text/talk.tsv`: 733/733 rows 100% translated (0 errors, 0 warnings).
* **Total 2,276 rows 100% translated and fully validated.**

## 2. 한 일 (Work Completed)

1. **번역 톤앤매너 구현**:
   - 딱딱한 번역투를 배제하고 JSRF 특유의 힙합/인라인 스트리트 컬처에 어울리는 젊고 캐주얼한 구어체 전면 적용.
   - DJ K(에너지 넘치는 해적방송 진행자), GG 크루(비트, 검, 콤보, 요요 등 10대 스케이터), 경찰 및 롯카쿠 보안대, 포이즌 잼/이모털즈/래피드 99/둠 라이더즈 등 각 조직과 인물의 개성을 살린 대사화.
2. **`xbe.tsv` 전수 번역 및 보완**:
   - 잔여 미번역 107개 항목(실황 중계 멘트 등) 전수 번역 완료.
   - `$s`, `$a`, `$c` 제어 코드 정확히 유지.
3. **`event.tsv` 전수 번역**:
   - 397개 이벤트 자막 전체 번역 적용.
   - 줄 너비 및 줄 수 한도에 맞추어 개행 `$n` 위치 최적화로 경고 0건 달성.
4. **`mission.tsv` 전수 번역**:
   - 495개 미션 텍스트(267개 고유 문장) 전수 번역.
   - `$r $e $p $a` 등 복잡한 페이지 분기 코드 1:1 보존.
   - 미션 목표 및 힌트의 픽셀 너비 한도(528px, 624px, 720px)를 정확히 준수하도록 문장 다듬기 수행.
5. **`talk.tsv` 전수 번역**:
   - 733개 대화 텍스트(596개 고유 문장) 전수 번역.
   - GG 멤버들 및 거리 라이벌들과의 대화 맥락을 살려 번역체 없는 한국어 길거리 구어체 적용.
   - 적용 결과 0 오류, 0 경고 단번에 달성.
6. **패치 빌드 검증 (`patch.py`)**:
   - `patch/manifest.json` 갱신 후 실제 게임 덤프에 전체 패치 적용 빌드(`out/test_patch`) 성공 확인.
7. **후속 정정: DJ 프로페서 K / DJ-K 표기 정위**:
   - `talk.tsv` 내 TE007(28행)과 TE159(418행)을 원문대로 `DJ 프로페서 K` 풀네임으로 반영.
   - TE213(599행)은 원문 약칭에 맞춰 `DJ-K`로 반영.
   - `docs/kb/glossary.md` 캐릭터 테이블에 풀네임(`DJ 프로페서 K`)과 약칭(`DJ-K`) 구분 명시.


1. **Translation Tone & Style Implementation**:
   - Replaced stiff translationese with lively, youthful street slang fitting JSRF's inline and graffiti culture.
   - Reflected distinct personalities for DJ Professor K, GG crew, police, and rival crews.
2. **Complete Translation of `xbe.tsv`**:
   - Translated the remaining 107 lines (play-by-play announcements, etc.).
   - Maintained all `$s`, `$a`, `$c` control codes.
3. **Complete Translation of `event.tsv`**:
   - Translated all 397 event subtitle lines.
   - Resolved all line width limits by tuning line breaks (`$n`), achieving 0 warnings.
4. **Complete Translation of `mission.tsv`**:
   - Translated all 495 mission lines (267 unique strings).
   - Preserved exact branching codes (`$r $e $p $a`).
   - Tuned pixel widths to fit objective display limits (528px, 624px, 720px).
5. **Complete Translation of `talk.tsv`**:
   - Translated all 733 dialog lines (596 unique strings).
   - Applied natural Korean street phrasing fitting the GG crew and rival dialogue contexts.
   - Achieved 0 errors and 0 warnings on validation.
6. **Patch Build Verification (`patch.py`)**:
   - Updated `patch/manifest.json` and successfully executed a test patch build (`out/test_patch`).
7. **Follow-up Refinement: DJ Professor K / DJ-K Notation Alignment**:
   - Updated TE007 (line 28) and TE159 (line 418) in `talk.tsv` to use the full name `DJ 프로페서 K`.
   - Updated TE213 (line 599) to match the original abbreviation `DJ-K`.
   - Updated character entry in `docs/kb/glossary.md` to distinguish full name (`DJ 프로페서 K`) and abbreviation (`DJ-K`).


## 3. 검증 결과 (Verification Results)

| 파일 (File) | 행수 (Rows) | 번역률 (Rate) | 결과 (Result) |
|---|---|---|---|
| `xbe.tsv` | 651 / 651 | 100% | 0 errors, 0 warnings 통과 |
| `event.tsv` | 397 / 397 | 100% | 0 errors, 0 warnings 통과 |
| `mission.tsv` | 495 / 495 | 100% | 0 errors, 0 warnings 통과 |
| `talk.tsv` | 733 / 733 | 100% | 0 errors, 0 warnings 통과 |
| **통합 검증 (Total)** | **2,276 / 2,276** | **100%** | **0 errors, 0 warnings 통과 (Hangul 907음절)** |

* All files checked with `tools/check_text.py "roms/Jet Set Radio Future"`.
* Test build executed with `python -I tools/patch.py "roms/Jet Set Radio Future" out/test_patch --link` (exit code 0).
* `git status` verifies no game data or copyright text from `roms/`, `out/`, `work/` is staged.

## 4. 화면 확인 (Screen Check, 2026-10-23)

* 산출물: 브랜치 `i017-fix-dj-k`(`d278e77`)로 만든 `out/jsrf-kr-i017-fix-dj-k`. xiso MD5 `bb08de8a4f9f4064f66530feb6b216df`, `default.xbe` `5122b0f5c8e05a42e828861f0c93e322`, `jetfont.dat` `bf1d90ffe6a53881c6d359977a0ba2fa`. 2,276곳, 경고 0, 한글 907자. v0.0.10 출력과 비교하면 `TE007.bin`, `TE159.bin`, `TE213.bin`만 다르다.
* Cxbx-Reloaded HDD 캐시에서 바뀌는 `Media` 파일 56개를 먼저 뺐다(백업 `EmuDisk\cache-bak-20261023\`).
* **xemu 0.8.139: 확인됨**(사용자 캡처): 섹션 `KRTEXT`를 더한 XBE가 부팅하고, 세이브 선택 화면("게임 데이터를 골라", "게임 데이터 1/2", "챕터", "플레이 시간", "새 게임 데이터")이 한글로 나온다. 칸 밖 번짐·잘림 없음.
* **DJ 프로페서 K / DJ-K 표기: 확인됨**(사용자 보고).
* 화면 캡처는 게임 그림이므로 커밋하지 않는다.

* Output: `out/jsrf-kr-i017-fix-dj-k`, built from branch `i017-fix-dj-k` (`d278e77`); xiso MD5 `bb08de8a4f9f4064f66530feb6b216df`, `default.xbe` `5122b0f5c8e05a42e828861f0c93e322`, `jetfont.dat` `bf1d90ffe6a53881c6d359977a0ba2fa`; 2,276 places, 0 warnings, 907 Hangul. Against the v0.0.10 output only `TE007.bin`, `TE159.bin` and `TE213.bin` differ.
* The 56 changed `Media` files were first taken out of the Cxbx-Reloaded HDD cache (backup `EmuDisk\cache-bak-20261023\`).
* **xemu 0.8.139: confirmed** (user's capture): the XBE with the added `KRTEXT` section boots, and the save selection screen ("게임 데이터를 골라", "게임 데이터 1/2", "챕터", "플레이 시간", "새 게임 데이터") shows in Hangul with no ink outside cells or clipping.
* **The DJ Professor K / DJ-K notation: confirmed** (user's report).
* Screen captures are game pictures and are not committed.
