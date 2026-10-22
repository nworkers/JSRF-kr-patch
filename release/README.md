# JSRF 한국어 패치 v{version}

Xbox 게임 **Jet Set Radio Future**의 비공식 한국어 패치입니다. 게임을 영어 모드로 실행하고 화면 문장(메뉴, 미션, 대화, 이벤트 자막)을 한국어로 바꿉니다. 음성과 그림 자산은 영어 모드의 원래 것 그대로입니다.

이 묶음에는 **게임 데이터가 들어 있지 않습니다.** 직접 가진 디스크의 덤프에 패치 도구를 돌려 패치된 게임 폴더(`default.xbe` 포함)와 ISO를 만듭니다.

## 필요한 것

| 항목 | 조건 |
|---|---|
| 덤프 폴더 | `default.xbe`(US판, MD5 `f4e366bfdceee551a09f42219c90d84e`)와 `Media/` 폴더 전체 |
| xiso (선택) | 같은 디스크의 xiso. 주면 패치한 ISO도 만든다 |
| 디스크 여유 | 출력 폴더 약 2.4GB, ISO를 만들면 약 2.5GB 더 |
| Python판만 | Python 3.10 이상(외부 패키지 필요 없음) |

도구는 입력 파일의 MD5를 검사하고, 하나라도 다르면 아무것도 쓰지 않고 멈춥니다.

## 사용법

묶음을 푼 폴더에서 실행합니다. 출력은 **현재 폴더의 `out/` 아래**에 생깁니다. 출력 폴더는 없거나 비어 있어야 합니다.

**Windows** (`jsrf-kr-patch-v{version}-windows-x64.zip`)

```bat
jsrf-kr-patch.exe "D:\dump\Jet Set Radio Future" out\jsrf-kr --iso "D:\dump\Jet Set Radio Future.iso"
```

**Linux** (`jsrf-kr-patch-v{version}-linux-x64.tar.gz`)

```sh
./jsrf-kr-patch "/path/to/Jet Set Radio Future" out/jsrf-kr --iso "/path/to/Jet Set Radio Future.iso"
```

**Python판** (`jsrf-kr-patch-v{version}-python.zip`)

```sh
python -I tools/patch.py "/path/to/Jet Set Radio Future" out/jsrf-kr --iso "/path/to/Jet Set Radio Future.iso"
```

* `--iso`를 빼면 게임 폴더만 만듭니다.
* `--link`: 바뀌지 않은 파일을 복사 대신 하드링크로 둡니다(같은 드라이브, 디스크 절약). 이때 출력 폴더의 그 파일을 고치면 덤프도 바뀝니다.
* 인자 없이 실행하면 모든 옵션이 나옵니다.

## 출력

* `out/jsrf-kr/`: 패치된 게임 폴더. 바뀐 파일은 `default.xbe`, `Media/Font/jetfont.dat`, 이벤트·대화·미션 파일입니다. 바뀐 파일의 MD5는 `out/jsrf-kr/md5.txt`에 있습니다. 같은 덤프와 같은 판이면 늘 같은 값입니다.
* `out/jsrf-kr.iso`: 사용자 xiso의 사본에 바뀐 파일을 써 넣은 것입니다.
* 에뮬레이터: xemu는 ISO를 DVD로, Cxbx-Reloaded는 `out/jsrf-kr/default.xbe`를 엽니다. 에뮬레이터의 HDD 캐시에 원본 `Media`가 남아 있으면 바뀐 문장이 보이지 않습니다. 이 게임을 아직 실행하지 않은 HDD로 시험하거나, 캐시(`Z:\Media\…`)에서 바뀐 파일을 빼 주세요.

## 문제 해결

| 메시지 | 뜻 |
|---|---|
| `input check failed: … MD5 … is not …` | 덤프 파일이 기대한 원본과 다릅니다(다른 판이거나 고친 파일) |
| `exists and is not an empty folder` | 출력 폴더를 지우고 다시 실행하세요 |
| `the output must be a folder under …out` | 출력은 현재 폴더의 `out/` 아래여야 합니다 |

## 출처와 권리 고지

* **Jet Set Radio Future**와 그 대본, 그림, 음성의 권리는 **SEGA**에 있습니다. 이 패치는 SEGA와 관계가 없는 비공식 팬 번역이며, 번역문은 원작의 2차적 저작물입니다.
* 패치 도구와 패치 데이터 형식: JSRF-kr-patch 프로젝트, [MIT License](LICENSE). 저장소: <https://github.com/nworkers/JSRF-kr-patch>
* 한글 글꼴 **Do Hyeon(도현)**: Copyright 2018 The Do Hyeon Project Authors, SIL Open Font License 1.1(라이선스 원문: Python판 `patch/font/OFL.txt`, 실행 파일판 `licenses/DoHyeon-OFL.txt`). 출처: google/fonts `ofl/dohyeon`.
* 실행 파일판에는 **Nuitka**(Apache-2.0)로 컴파일한 **CPython**(PSF License)과 그 표준 모듈(OpenSSL, bzip2, xz, zlib 등), zstd(BSD)가 들어 있습니다. 라이선스 원문은 `licenses/`에 있습니다.
* 게임 구조 분석의 일부는 [reJSRF](https://github.com/nworkers/reJSRF)(JSRF 정적 재컴파일 프로젝트)의 분석을 참고했습니다. 자세한 서드파티 고지는 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 있습니다.
* 이 판의 변경 사항과 해결된 issue는 [RELEASE_NOTES.md](RELEASE_NOTES.md)에 있습니다.

---

# JSRF Korean Patch v{version}

An unofficial Korean patch for the Xbox game **Jet Set Radio Future**. The game runs in English mode and its on-screen text (menus, missions, talk, event subtitles) becomes Korean; voice and picture assets stay English mode's originals.

This package contains **no game data**. Run the patcher on a dump of a disc you own to make a patched game folder (with `default.xbe`) and an ISO.

## Requirements

| Item | Requirement |
|---|---|
| Dump folder | `default.xbe` (US build, MD5 `f4e366bfdceee551a09f42219c90d84e`) and the whole `Media/` folder |
| xiso (optional) | the same disc's xiso; given, a patched ISO is made too |
| Free disk | about 2.4 GB for the output folder, about 2.5 GB more with the ISO |
| Python edition only | Python 3.10 or later (no external packages) |

The tool checks the input files' MD5s and writes nothing if any differs.

## Usage

Run it from the unpacked folder; the output goes **under `out/` in the current folder**, and the output folder must be absent or empty. The commands for Windows, Linux and the Python edition are above.

* Without `--iso` only the game folder is made.
* `--link` hard-links unchanged files instead of copying them (same drive, saves disk); editing such a file in the output then edits the dump too.
* Run it without arguments to see every option.

## Output

* `out/jsrf-kr/`: the patched game folder. The changed files are `default.xbe`, `Media/Font/jetfont.dat` and the event, talk and mission files; their MD5s are in `out/jsrf-kr/md5.txt`, always the same for the same dump and release.
* `out/jsrf-kr.iso`: a copy of your xiso with the changed files written in.
* Emulators: open the ISO as the DVD in xemu, or `out/jsrf-kr/default.xbe` in Cxbx-Reloaded. If an emulator's HDD cache still holds the original `Media`, the changed text does not show; test with an HDD on which the game has not run yet, or take the changed files out of the cache (`Z:\Media\…`).

## Troubleshooting

| Message | Meaning |
|---|---|
| `input check failed: … MD5 … is not …` | a dump file is not the expected original (another release or a modified file) |
| `exists and is not an empty folder` | delete the output folder and run again |
| `the output must be a folder under …out` | the output must be under `out/` in the current folder |

## Sources and rights notice

* **Jet Set Radio Future** and its script, art and voice belong to **SEGA**. This patch is an unofficial fan translation not affiliated with SEGA; the translation is a derivative of the original work.
* The patcher and patch data format: the JSRF-kr-patch project, [MIT License](LICENSE). Repository: <https://github.com/nworkers/JSRF-kr-patch>
* The Hangul font **Do Hyeon**: Copyright 2018 The Do Hyeon Project Authors, SIL Open Font License 1.1 (license text: `patch/font/OFL.txt` in the Python edition, `licenses/DoHyeon-OFL.txt` in the executable editions). Source: google/fonts `ofl/dohyeon`.
* The executable editions contain **CPython** (PSF License) and its standard modules (OpenSSL, bzip2, xz, zlib …) compiled with **Nuitka** (Apache-2.0), and zstd (BSD); the license texts are in `licenses/`.
* Part of the game-structure analysis draws on [reJSRF](https://github.com/nworkers/reJSRF) (a static-recompilation project of JSRF). The detailed third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
* This release's changes and resolved issues are in [RELEASE_NOTES.md](RELEASE_NOTES.md).
