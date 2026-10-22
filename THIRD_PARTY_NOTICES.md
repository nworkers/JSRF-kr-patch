# 서드파티 고지 / Third-Party Notices

JSRF-kr-patch는 MIT 라이선스다. 저장소에 포함하거나 옮겨 온 서드파티 코드와 글꼴을 아래에 적는다.

JSRF-kr-patch is MIT licensed. Third-party code and fonts included in, or ported into, the repository are listed below.

| 이름 / Name | 출처 / Source | 라이선스 / License | 저장소 안 위치 / Location | 용도 / Use |
|---|---|---|---|---|
| Do Hyeon (도현) Regular | [google/fonts `ofl/dohyeon`](https://github.com/google/fonts/tree/main/ofl/dohyeon) 커밋/commit `47d54ca`, 원 저장소/upstream [baemin/Dohyeon](https://github.com/baemin/Dohyeon); Copyright 2018 The Do Hyeon Project Authors | SIL Open Font License 1.1 (`patch/font/OFL.txt`) | `patch/font/DoHyeon-Regular.ttf` | 한글 글리프 / Hangul glyphs (issue #6) |

## 실행 파일 배포물 / Executable distributions

릴리스의 Windows·Linux 실행 파일(`jsrf-kr-patch`, issue #22)은 Nuitka로 컴파일되어 아래를 함께 담는다. 저장소에는 들어 있지 않다. 라이선스 원문은 배포 묶음의 `licenses/`에 넣는다(`tools/release.py`).

The Windows and Linux executables of the releases (`jsrf-kr-patch`, issue #22) are compiled with Nuitka and carry the items below; none of them is in the repository. Their license texts go into the package's `licenses/` (`tools/release.py`).

| 이름 / Name | 출처 / Source | 라이선스 / License | 배포 묶음 안 / In the package | 용도 / Use |
|---|---|---|---|---|
| Nuitka 런타임 / runtime 2.8.10 | [Nuitka](https://nuitka.net/), PyPI `nuitka==2.8.10` | Apache-2.0 (4.0부터 AGPL-3.0이라 2.8.10에 고정 / pinned to 2.8.10 since 4.0+ is AGPL-3.0) | `licenses/Nuitka-LICENSE.txt` | 컴파일·실행 파일 / compiler runtime, onefile bootstrap |
| CPython 3.12과 표준 모듈 / and standard modules (OpenSSL `libcrypto`, bzip2, xz, zlib 등 / and others) | [python.org](https://www.python.org/) | PSF License 2.0, 각 모듈 라이선스는 Python `LICENSE.txt`에 / each module's license in Python's `LICENSE.txt` | `licenses/Python-LICENSE.txt` | 실행 환경 / runtime |
| zstd | Nuitka 안의 사본 / Nuitka's inline copy, [facebook/zstd](https://github.com/facebook/zstd) | BSD-3-Clause | `licenses/zstd-LICENSE.txt` | 실행 파일 압축 해제 / onefile decompression |
| Microsoft Visual C++ 런타임 / runtime (Windows) | Visual Studio 재배포 파일 / redistributable | Microsoft 재배포 허용 / redistributable under the Visual Studio license | 실행 파일 안 / inside the executable | Windows 실행 / runtime |
| Do Hyeon | 위와 같음 / as above | SIL OFL 1.1 | `licenses/DoHyeon-OFL.txt` | 한글 글리프 / Hangul glyphs |

빌드 도구 `zstandard==0.25.0`(BSD-3-Clause)은 빌드에만 쓴다. / The build tool `zstandard==0.25.0` (BSD-3-Clause) is used only at build time.
