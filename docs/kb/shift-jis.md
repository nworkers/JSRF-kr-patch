# Shift-JIS와 JSRF 렌더러의 2바이트 판정

* Shift-JIS(Windows에서는 CP932)는 1바이트 ASCII·반각 가타카나와 2바이트 JIS X 0208 글자를 섞어 쓰는 인코딩이다. 첫 바이트(lead)는 `0x81`~`0x9F`, `0xE0`~`0xFC`(CP932는 `0xE0`~`0xFC` 중 일부 사용자 정의), 둘째 바이트(trail)는 `0x40`~`0x7E`, `0x80`~`0xFC`다. 출처: [WHATWG Encoding Standard, Shift_JIS](https://encoding.spec.whatwg.org/#shift_jis), [Microsoft, Code Page 932](https://learn.microsoft.com/en-us/windows/win32/intl/code-page-932).
* 구획: `0x8140`~`0x81FC` 기호(전각 공백 `0x8140`), `0x824F`~ 전각 숫자, `0x8260`~ 전각 영대문자, `0x829F`~`0x82F1` 히라가나, `0x8340`~`0x8396` 가타카나, `0x889F`~`0x9872` JIS 제1수준 한자, `0x989F`~`0xEAA4` 제2수준 한자.
* 한글은 JIS X 0208에 없다. Shift-JIS로 한글을 쓰려면 기존 코드에 한글 그림을 배정해야 한다.
* **JSRF 렌더러의 차이**: 2바이트로 읽는 첫 바이트가 `0x80`~`0x9F`뿐이다. `0xA0`~`0xFF`는 Latin-1 1바이트 글자로 그린다(유럽 언어용). 그래서 제2수준 한자의 뒤쪽(`0xE0`~`0xEA`로 시작)은 이 게임에서 쓸 수 없다. 자세한 것은 [analysis/text-renderer.md §4](../analysis/text-renderer.md)에 있다.

---

# Shift-JIS and the JSRF renderer's double-byte test

* Shift-JIS (CP932 on Windows) mixes single-byte ASCII and half-width katakana with double-byte JIS X 0208 characters. Lead bytes are `0x81`–`0x9F` and `0xE0`–`0xFC` (CP932 uses part of `0xE0`–`0xFC` for user-defined and vendor characters); trail bytes are `0x40`–`0x7E` and `0x80`–`0xFC`. Sources: [WHATWG Encoding Standard, Shift_JIS](https://encoding.spec.whatwg.org/#shift_jis), [Microsoft, Code Page 932](https://learn.microsoft.com/en-us/windows/win32/intl/code-page-932).
* Blocks: `0x8140`–`0x81FC` symbols (full-width space `0x8140`), `0x824F`– full-width digits, `0x8260`– full-width capitals, `0x829F`–`0x82F1` hiragana, `0x8340`–`0x8396` katakana, `0x889F`–`0x9872` JIS level-1 kanji, `0x989F`–`0xEAA4` level-2 kanji.
* JIS X 0208 has no Hangul. Writing Hangul in Shift-JIS means assigning Hangul pictures to existing codes.
* **Where the JSRF renderer differs**: only lead bytes `0x80`–`0x9F` start a double-byte character; `0xA0`–`0xFF` are drawn as Latin-1 single-byte characters (for the European languages). The upper level-2 kanji (lead `0xE0`–`0xEA`) are therefore unusable in this game. Details in [analysis/text-renderer.md §4](../analysis/text-renderer.md).
