# 용어집: 이름과 용어의 한국어 표기

issue #15(P6-0)에서 만든 번역 표기 기준이다. 번역자는 이 표를 따르고, 바꾸려면 이 문서를 먼저 고친 뒤 `patch/text/`의 같은 낱말을 함께 고친다. `tools/check_text.py --review`가 이 문서의 표(머리가 `| 일본어 | 영어 | 한국어 |`인 표)를 읽어, 줄마다 들어 있는 용어의 한국어 표기를 검토 표의 `terms` 열에 보여 준다. 절차는 [guides/translation.md](../guides/translation.md).

* 일본어 칸에는 고유명사·용어 **낱말만** 적는다. 대사 문장은 적지 않는다(AGENTS: 원문 문장은 커밋하지 않는다). 같은 이름의 다른 표기는 ` / `로 나란히 적는다.
* 영어 칸은 영어판에서 쓰인 이름이다. 확실하지 않으면 비운다.

## 1. 표기 원칙

| 경우 | 원칙 | 예 |
|---|---|---|
| 가타카나 외래어 이름 | 영어판 이름을 기준으로 [외래어 표기법](https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0003)에 가깝게 | ビート Beat → 비트 |
| 일본 고유명(지명·인명) | [일본어 표기법](https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0003): 장음 표기 안 함, 어두 거센소리 안 씀, ツ = 쓰 | ドーゲン坂 → 도겐자카, ツヅラ → 쓰즈라 |
| 지명의 일반명사 부분 | 번역한다. 고유명의 일부면 그대로 붙여 쓴다 | ～通り → ～ 거리, ロッカク台 → 롯카쿠다이 |
| 기술(트릭) 이름 | 영어 스케이트 용어를 외래어 표기법대로, 낱말 사이는 띄운다. 가운뎃점(・)은 쓰지 않는다 | バックサイド・ロック → 백사이드 록 |
| 숫자 | 원문이 전각이면 전각(`１８０`), 반각이면 반각 | ミュート５４０ → 뮤트 ５４０ |
| 그래피티 이름 | 영어 낱말은 외래어 표기, 일본어 말장난은 뜻을 살려 붙여 쓴다 | イタクテモガマン → 아파도참아 |
| 게임이 채우는 자리 | `%d` `%s`, 자리 표시 공백은 원문과 같은 바이트 위치 | [translation.md](../guides/translation.md) §3 |

## 2. 캐릭터

| 일본어 | 영어 | 한국어 | 메모 |
|---|---|---|---|
| ビート | Beat | 비트 | GG |
| ガム | Gum | 검 | GG. "껌"으로 읽히지 않게 늘 "검" |
| コーン | Corn | 콘 | GG |
| ヨーヨー | Yoyo | 요요 | GG |
| リズ | Rhyth | 리즈 | GG |
| ガラム | Garam | 가람 | GG |
| ブギィ | Boogie | 부기 | GG |
| コンボ | Combo | 콤보 | GG |
| キューブ | Cube | 큐브 | GG |
| ソーダ | Soda | 소다 | GG |
| ジャズ | Jazz | 재즈 | GG |
| クラッチ | Clutch | 클러치 | |
| ロボィ | Roboy | 로보이 | 차고의 로봇 |
| ポッツ | Pots | 포츠 | 개 |
| ＤＪプロフェッサーＫ / DJ Professor K | Professor K | DJ 프로페서 K | 풀네임 (이벤트·대화) |
| DJ-K | DJ-K | DJ-K | 대화 약칭 (TE213 등 원문 표기) |
| ＤＪＫ / DJK | Professor K | DJ K | 시스템 이름/라디오 DJ |
| アクム | | 아쿠무 | 확인 필요 |
| 警部 | | 경부 | 경찰 계급 |
| 警官 / ケーカン | | 경관 | |
| ケーサツロボ | | 경찰 로봇 | |
| ケーサツ | | 경찰 | |

## 3. 팀과 조직

| 일본어 | 영어 | 한국어 | 메모 |
|---|---|---|---|
| ＧＧ | GG | ＧＧ | 원문의 전각 표기 그대로 |
| ポイズンジャム | Poison Jam | 포이즌 잼 | |
| ノイズタンク | Noise Tanks | 노이즈 탱크 | |
| ラブショッカーズ / ラヴショッカーズ | Love Shockers | 러브 쇼커즈 | |
| イモータルズ | Immortals | 이모털즈 | |
| ドゥームライダーズ | Doom Riders | 둠 라이더즈 | |
| ラピッド９９ | Rapid 99 | 래피드 ９９ | |
| 金のサイ | Golden Rhinos | 황금 코뿔소 | |
| サイ | | 코뿔소 | 황금 코뿔소의 줄임 |

## 4. 장소

| 일본어 | 영어 | 한국어 | 메모 |
|---|---|---|---|
| ガレージ | Garage | 차고 | ＧＧ의 아지트 |
| シブヤターミナル | Shibuya Terminal | 시부야 터미널 | |
| ドーゲン坂 | Dogenzaka Hill | 도겐자카 | |
| チュウオウ街 | Chuo Street | 주오 거리 | |
| ロッカク台 | Rokkaku-dai Heights | 롯카쿠다이 | |
| ヒカゲ通り | Hikage Street | 히카게 거리 | |
| トーキョー地下下水施設 | Tokyo Underground Sewage Facility | 도쿄 지하 하수 시설 | 最深部 최심부, 調整区 조정구역 |
| キボウヶ丘 | Kibogaoka Hill | 기보가오카 | |
| 要塞居住区 | Fortified Residential Zone | 요새거주구 | XBE에서는 붙여 씀(길이) |
| ９９番街 | 99th Street | ９９번가 | |
| 高層ビル群 | Skyscraper District | 고층 빌딩가 | |
| ファラオパーク | Pharaoh Park | 파라오 파크 | |
| 国道ゼロ号 | Highway Zero | 국도０호 | |
| 上空キョウリュウ街 | | 상공 공룡 거리 | |
| 万博スタジアム予定地 | | 엑스포 경기장 예정지 | |
| 第２スタジアム | | 제２ 스타디움 | 대전 스테이지 |
| ツヅラパーク | | 쓰즈라 파크 | 대전 스테이지 |
| ラデンパーク | | 라덴 파크 | 대전 스테이지 |
| ショウワパーク | | 쇼와 파크 | 대전 스테이지 |
| だるま商店街 / ダルマ | | 다루마 상점가 / 다루마 | |

## 5. 게임 용어

| 일본어 | 영어 | 한국어 | 메모 |
|---|---|---|---|
| グラフィティ | graffiti | 그래피티 | |
| グラフィティソウル | Graffiti Soul | 그래피티 소울 | |
| スプレー / スプレーカン / スプレー缶 | spray can | 스프레이 / 스프레이 캔 | |
| ＧＧ手帳 | | ＧＧ 수첩 | |
| トリック / ＴＲＩＣＫＳ | trick | 트릭 | |
| グラインド | grind | 그라인드 | |
| ウォールライド | wall ride | 월 라이드 | |
| エアー | air | 에어 | |
| コンビネーション | combination | 콤비네이션 | |
| トリックコンボ | trick combo | 트릭 콤보 | |
| ジェット | Jet | 제트 | 랭크·기술 이름 |
| スタミナ | stamina | 스태미나 | |
| タイリョク | | 체력 | |
| スコア | score | 점수 | |
| トライアル / トライアルミッション | trial | 트라이얼 / 트라이얼 미션 | |
| プラクティス | practice | 연습 | |
| ミッション | mission | 미션 | |
| チャプター | chapter | 챕터 | |
| セーブ | save | 저장 | |
| ロード | load | 불러오기 | |
| ゲームデータ | game data | 게임 데이터 | |
| メモリユニット | memory unit | 메모리 유닛 | |
| ハードディスク | hard disk | 하드 디스크 | |
| ブロック | block | 블록 | 저장 공간 단위 |
| コントローラ / コントローラー | controller | 컨트롤러 | |
| 方向パッド | directional pad | 방향 패드 | |
| 左サムスティック | left thumbstick | 왼쪽 스틱 | |
| 左トリガ / 右トリガ | trigger | 왼쪽 트리거 / 오른쪽 트리거 | |
| Ａボタン / Ｂボタン | A / B button | Ａ 버튼 / Ｂ 버튼 | 전각 글자 그대로 |
| マップ | map | 지도 | |
| テイルトゥノーズ | | 테일 투 노즈 | 대전 모드 |
| バトルグラフィティ | | 배틀 그래피티 | 대전 모드 |
| デスボウル | | 데스 볼 | 대전 모드 |

## 6. 기술(트릭) 이름의 낱말

| 일본어 | 영어 | 한국어 | 메모 |
|---|---|---|---|
| フロントサイド | frontside | 프런트사이드 | |
| バックサイド | backside | 백사이드 | |
| ファーサイド | farside | 파사이드 | |
| アリウープ | alley-oop | 앨리웁 | |
| ソウル | soul | 솔 | |
| ミズ | | 미즈 | |
| ミストリアル | mistrial | 미스트리얼 | |
| ユニティー / ユニティ | unity | 유니티 | |
| ロイヤル | royale | 로열 | |
| ソイヤル | soyale | 소이얼 | |
| フィッシュ | fish | 피시 | |
| トーク | torque | 토크 | |
| ミュート | mute | 뮤트 | |
| セイフティ | safety | 세이프티 | |
| メソッド | method | 메서드 | |
| バックフリップ / フロントフリップ | backflip / frontflip | 백플립 / 프런트플립 | |
| コークスクリュー | corkscrew | 코크스크루 | |
| フラットスピン | flatspin | 플랫스핀 | |
| ロケット | rocket | 로켓 | |
| カラテ | karate | 가라테 | |
| リューカン | | 류칸 | |
| バイオ | bio | 바이오 | |

## 7. 문장 부호와 글자

* 쓸 수 있는 2바이트 기호(새 글리프 표에 남은 것): `、。，．・：？！々ー／＼～…“”（）「」『』￥％＆※♪`. 그 밖의 전각 기호(`＜＞－` 등)는 쓸 수 없다. 1바이트 ASCII 기호·영문·숫자와 공백은 쓸 수 있다.
* 문장 끝의 `！` `？`는 원문처럼 전각을 쓴다. 쉼표·마침표는 1바이트 `,` `.`를 기본으로 한다(화면 확인 뒤 바꿀 수 있다).
* 전각 공백(U+3000)은 그리지 않고 한 칸(24픽셀)만큼 띄운다. 자리 맞춤에 쓴다.

---

# Glossary: Korean forms of names and terms

The translation spelling standard made in issue #15 (P6-0). Translators follow these tables; to change an entry, change this document first and then the same word in `patch/text/`. `tools/check_text.py --review` reads the tables here (those whose header is `| 일본어 | 영어 | 한국어 |`) and shows, for every line, the Korean forms of the terms in it in the review table's `terms` column. The procedure is in [guides/translation.md](../guides/translation.md).

* The Japanese column holds **proper nouns and term words only**, never dialogue sentences (AGENTS: original sentences are never committed). Other spellings of the same name stand side by side, separated by ` / `.
* The English column holds the names used in the English edition; left empty when not certain.
* §1 gives the spelling rules: katakana loanword names follow the English edition's name under the Korean loanword rules; Japanese proper names follow the Korean rules for Japanese (no long vowels, no aspirated initials, ツ = 쓰); the common-noun part of a place name is translated unless it is part of the proper name; trick names are written word by word without the middle dot; digits keep the original's width; graffiti names render loanwords and keep the sense of Japanese puns, written without spaces; places the game fills keep their byte positions.
* §2–§6 list characters, teams, places, game terms and the words of trick names.
* §7: the usable double-byte symbols are those listed (kept in the new glyph table); other full-width symbols (`＜＞－` and the like) cannot be used, while single-byte ASCII symbols, letters, digits and space can. Sentence-final `！` `？` are full-width as in the original; commas and full stops default to single-byte `,` `.` (open to change after the screen check). The full-width space (U+3000) advances one cell (24 px) without drawing and serves for alignment.
