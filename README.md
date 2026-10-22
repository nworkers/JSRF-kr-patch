# JSRF-kr-patch

Xbox 게임 **Jet Set Radio Future**의 **한국어 패치**를 만드는 프로젝트입니다. 게임을 영어 모드로 실행하고 화면 문장(메뉴, 미션, 대사 자막)을 한국어로 바꿉니다. 음성과 그림 자산은 영어 모드의 원래 것(영어판) 그대로입니다.

> 소개 페이지: <https://nworkers.github.io/JSRF-kr-patch/> · 내려받기: [GitHub 릴리스](https://github.com/nworkers/JSRF-kr-patch/releases) · 진행 계획: [docs/PLAN.md](docs/PLAN.md)

## 게임 데이터는 포함되지 않습니다

이 저장소와 배포물에는 게임의 실행 파일, 자산, 원문 문장이 들어 있지 않으며 앞으로도 넣지 않습니다. 결과물은 **패치 도구와 패치 데이터**이고, 직접 소유한 디스크의 덤프에 도구를 돌려 패치된 게임 폴더를 만듭니다.

## 필요한 덤프

| 파일 | 조건 |
|---|---|
| `default.xbe` | US판, MD5 `f4e366bfdceee551a09f42219c90d84e` |
| `Media/` | 같은 디스크의 `Media` 폴더 전체 |

덤프는 `roms/` 아래에 두면 Git이 무시합니다. 다른 디스크(US판 디스크, PAL)의 `Media`는 확인하지 않았습니다. 도구는 입력의 MD5를 검사하고 다르면 멈춥니다.

## 사용법

Python 3.10 이상만 있으면 됩니다(외부 패키지 없음).

```
python -I tools/patch.py <덤프 폴더> out/<이름> [--iso <같은 디스크의 xiso>]
```

입력 MD5를 검사한 뒤 `out/<이름>/`에 패치된 게임 폴더를, `--iso`를 주면 `out/<이름>.iso`도 만듭니다. 자세한 절차는 [docs/guides/apply-patch.md](docs/guides/apply-patch.md), 도구 안내는 [tools/README.md](tools/README.md)에 있습니다. 번역이 생기기 전까지 출력은 시험용입니다.

```mermaid
flowchart LR
    DUMP["your dump<br/>US default.xbe + Media"] --> TOOL["tools/patch.py"]
    DATA["patch/<br/>manifest, Korean text,<br/>XBE patches, OFL font"] --> TOOL
    TOOL --> OUT["patched game folder"]
```

## 관련 프로젝트

[reJSRF](https://github.com/nworkers/reJSRF)(JSRF의 정적 재컴파일 포팅)가 이 저장소의 결과를 참고해 같은 한국어 문장을 실행 중에 적용하는 방식으로 다시 구현합니다. 두 저장소는 코드를 공유하지 않습니다.

## 권리 고지

Jet Set Radio Future와 그 대본, 그림, 음성의 권리는 SEGA에 있습니다. 이 프로젝트는 SEGA와 관계가 없는 비공식 팬 번역입니다. 번역문은 원작의 2차적 저작물입니다. 패치 도구의 코드는 [MIT License](LICENSE)이고, 서드파티 글꼴과 코드는 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 적습니다.

---

# JSRF-kr-patch

A **Korean patch** for the Xbox game **Jet Set Radio Future**. The game runs in English mode and its on-screen text (menus, missions, dialogue subtitles) becomes Korean; voice and picture assets stay English mode's originals (English).

> Site: <https://nworkers.github.io/JSRF-kr-patch/> · Download: [GitHub releases](https://github.com/nworkers/JSRF-kr-patch/releases) · Plan: [docs/PLAN.md](docs/PLAN.md)

## No game data included

This repository and its releases contain no game executable, assets or original text, and never will. The deliverable is **a patcher and patch data**: run the tool on a dump of a disc you own to make a patched game folder.

## Dump needed

| File | Requirement |
|---|---|
| `default.xbe` | US build, MD5 `f4e366bfdceee551a09f42219c90d84e` |
| `Media/` | the whole `Media` folder from the same disc |

Git ignores a dump kept under `roms/`. Other discs' `Media` (the US disc, PAL) have not been checked; the tool checks the input's MD5s and stops on a mismatch.

## Usage

Only Python 3.10 or later is needed (no external packages).

```
python -I tools/patch.py <dump folder> out/<name> [--iso <the same disc's xiso>]
```

After checking the input MD5s it writes the patched game folder to `out/<name>/`, and with `--iso` also `out/<name>.iso`. The procedure is in [docs/guides/apply-patch.md](docs/guides/apply-patch.md) and the tools are described in [tools/README.md](tools/README.md). Until there is a translation, the output is for testing.

## Related project

[reJSRF](https://github.com/nworkers/reJSRF) (a static-recompilation port of JSRF) takes this repository's results as reference and reimplements the same Korean text as a run-time replacement. The two repositories share no code.

## Rights notice

Jet Set Radio Future and its script, art and voice belong to SEGA. This is an unofficial fan translation, not affiliated with SEGA. The translation is a derivative of the original work. The patcher's code is under the [MIT License](LICENSE); third-party fonts and code are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
