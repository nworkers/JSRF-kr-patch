# AGENTS.md

이 문서의 작업 규칙은 [nworkers/reJSRF](https://github.com/nworkers/reJSRF)의 `AGENTS.md`를 바탕으로 하고, 이 프로젝트의 성격(일본판 Jet Set Radio Future의 한국어 패치 도구)에 맞게 고쳤다. 고친 곳은 [docs/PLAN.md §2](docs/PLAN.md)에 있다.

The working rules here are based on the `AGENTS.md` of [nworkers/reJSRF](https://github.com/nworkers/reJSRF), adapted to this project's nature (a Korean patch tool for the Japanese Jet Set Radio Future). The changes are listed in [docs/PLAN.md §2](docs/PLAN.md).

## 프로젝트 개요

이 프로젝트는 Xbox 게임 Jet Set Radio Future(JSRF) **일본판** `default.xbe`(MD5 `d8490cdb75bd47b36c62effdf1461ae0`)와 그 `Media`에 적용하는 **한국어 패치**를 만든다.

* 결과물은 **패치 도구와 패치 데이터**다. 사용자가 자기 덤프에 도구를 돌려 패치된 게임 폴더를 만든다. 원본 바이트는 저장소와 배포물에 넣지 않는다.
* 이 저장소의 결과(바꾼 주소, 데이터 형식, 글꼴 방식)는 reJSRF가 참고해 런타임 방식으로 다시 구현한다. 두 저장소는 코드를 공유하지 않고 문서(`docs/handoff-rejsrf.md`)로 넘긴다.
* 범위 밖: 한국어 음성. 음성은 일본어 그대로 두고 화면 문장(자막)만 번역한다.

## Project Overview

This project makes a **Korean patch** for the **Japanese** Jet Set Radio Future (JSRF) `default.xbe` (MD5 `d8490cdb75bd47b36c62effdf1461ae0`) and its `Media`.

* The deliverable is **a patcher and patch data**: users run the tool on their own dump to make a patched game folder. No original bytes go into the repository or a release.
* reJSRF takes this repository's results (changed addresses, data formats, the font approach) as reference and reimplements them at run time. The two repositories share no code; results pass through documents (`docs/handoff-rejsrf.md`).
* Out of scope: Korean voice. Voice stays Japanese; only on-screen text (subtitles) is translated.

---

## 핵심 설계 목표

우선순위:

1. 원본 게임 동작은 바꾸지 않는다. 문장, 글꼴, 글자 그림만 바꾼다.
2. 코드 패치는 최소로 한다. 데이터만으로 되면 코드를 고치지 않는다.
3. 결과물은 사용자 덤프와 우리 패치 데이터만으로 **재생성**한다. 차분(xdelta 등)처럼 원본 바이트를 담을 수 있는 형식은 쓰지 않는다.
4. 입력을 MD5로 검증하고, 같은 입력에서 항상 같은 출력을 만든다(재현성).
5. 에뮬레이터 소스(xemu, Cxbx-Reloaded)를 가져오지 않는다.
6. 게임 데이터(XBE, 자산, ISO), 덤프에서 추출한 원문, 패치된 결과물은 저장소에 넣지 않는다.

## Primary Design Goals

Priority order:

1. Game behaviour stays as it is. Only text, the font and lettering pictures change.
2. Keep code patches minimal. When data alone works, no code is changed.
3. The output is **regenerated** from the user's dump and our patch data alone. Formats that can carry original bytes (xdelta diffs and the like) are not used.
4. Inputs are checked by MD5, and the same input always gives the same output (reproducibility).
5. Do not take emulator source code (xemu, Cxbx-Reloaded).
6. Never put game data (XBE, assets, ISO), original text extracted from a dump, or patched output in the repository.

---

## 참조 문서

작업 전에는 관련 문서를 먼저 읽고 갱신한다.

* `docs/PLAN.md`
* `docs/analysis/`
* `docs/design/`
* `docs/work-orders/`
* `docs/work-logs/`
* `docs/kb/`
* `docs/guides/`
* `THIRD_PARTY_NOTICES.md`
* reJSRF 분석: [text-and-font](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/text-and-font.md), [language](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/language.md)(로컬 `C:\workspace\git\reJSRF\docs\`)

## Reference Documents

Read and update the relevant documents before starting work.

* `docs/PLAN.md`
* `docs/analysis/`
* `docs/design/`
* `docs/work-orders/`
* `docs/work-logs/`
* `docs/kb/`
* `docs/guides/`
* `THIRD_PARTY_NOTICES.md`
* reJSRF analyses: [text-and-font](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/text-and-font.md), [language](https://github.com/nworkers/reJSRF/blob/main/docs/analysis/language.md) (locally under `C:\workspace\git\reJSRF\docs\`)

---

## 핵심 원칙

1. 사용자 요구사항을 받으면 바로 구현하지 말고 먼저 설계를 작성하거나 기존 설계를 갱신한다.
2. 설계가 정리되면 구현 계획서를 작성하거나 갱신한 뒤 구현을 시작한다.
3. 코드나 패치 데이터 변경이 있는 모든 작업은 작업 지시 문서와 작업 로그 문서를 남긴다.
4. 문서는 기본적으로 한국어를 먼저 쓰고 바로 아래에 영어 번역을 추가한다. 이 규칙은 `docs/` 아래 문서와 `README.md` 같은 저장소 문서에만 적용되며, 소스 코드 주석과 번역 데이터에는 적용하지 않는다.
5. 기존 코드, 데이터, 문서의 의도를 확인한 뒤 수정하며, 큰 구조 변경은 근거를 문서에 남긴다.

## Core Principles

1. When a user requirement is received, do not implement immediately. First write a design or update the existing design.
2. After the design is clear, write or update the implementation work order before starting implementation.
3. Every task that changes code or patch data must leave a work-order document and a work-log document.
4. Documents should be written in Korean first, followed immediately by an English translation. This applies to documents under `docs/` and repository documents such as `README.md`; it does not apply to source-code comments or translation data.
5. Confirm the intent of existing code, data, and documents before modifying them. Document the rationale for large structural changes.

---

## 응답 태도 규칙

* 모든 질문에 대한 답변은 존대말을 사용하고 예의 있는 태도를 유지한다.

## Response Tone Rules

* Use polite Korean speech and maintain a respectful attitude for all answers.

---

## 요구사항 처리 절차

1. 요구사항 접수
2. 관련 코드, 문서, 데이터 맥락 확인
3. 설계 문서 작성 또는 갱신
4. 구현 계획서 작성 또는 갱신
5. 사용자 승인 또는 현재 진행 맥락 확인
6. 구현
7. 범위에 맞는 검증(왕복 시험, 해시, xemu·reJSRF 실행)
8. 작업 로그 작성

단, 요구사항이 단순 질문이거나 확인 요청이라면 해당 내용에 바로 응답하고 문서화 및 코드 구현은 하지 않는다.

## Requirement Handling Procedure

1. Receive the requirement.
2. Inspect the relevant code, documentation, and data context.
3. Write or update the design document.
4. Write or update the implementation work order.
5. Confirm user approval or the current active context.
6. Implement.
7. Run verification appropriate to the scope (round trips, hashes, runs in xemu or reJSRF).
8. Write the work log.

If the requirement is a simple question or confirmation request, answer it directly without documentation or code implementation.

---

## 문서 작성 규칙

* 설계 문서는 `docs/design/` 아래에 둔다.
* 계획 문서는 `docs/work-orders/` 아래에 둔다.
* 작업 결과와 회고는 `docs/work-logs/` 아래에 둔다.
* 사용자가 직접 수행하는 검증·패치 적용·운영 절차는 `docs/guides/` 아래에 둔다. 반복 수행 가능한 절차만 두고, 근거가 되는 작업 로그와 설계를 링크한다.
* 원본 XBE·`Media` 분석으로 확인한 사실, 가설, 미해결 질문은 `docs/analysis/` 아래에 주제별로 둔다.
* 일반 기술 정의, 배경 지식, 용어집(`docs/kb/glossary.md`)은 `docs/kb/` 아래에 주제별로 두고, 외부 자료에서 왔으면 원문 링크를 단다.
* 프로젝트의 큰 방향성과 단계는 `docs/PLAN.md`에 반영한다.
* reJSRF로 넘길 결과(주소, 형식, 글꼴 방식)는 `docs/handoff-rejsrf.md`에 단계마다 갱신한다.
* 규칙이 바뀌면 `AGENTS.md`와 관련 문서를 함께 갱신한다.
* 작업 단위 문서 파일명은 `YYYYMMDD-i###-slug.md` 형식을 사용한다. `###`은 task의 GitHub issue 번호를 세 자리로 맞춘 값이다(예: issue #6 → `20261020-i006-slug.md`).
* Markdown 문서에서 구조, 관계, 흐름, 호출 순서, 상태 전이, 주소 변환을 도식화할 수 있으면 Mermaid를 적극적으로 사용한다.
* 세 개 이상의 구성요소·단계·분기·계층이 있으면 Mermaid 적용 가능성을 검토하고, 내용에 맞는 형식(flowchart, sequenceDiagram, stateDiagram, classDiagram 등)을 고른다.
* 단순 사실 하나나 한 단계 설명에는 도식을 강제하지 않는다.
* Mermaid 도식은 본문과 같은 사실 및 확인 상태를 표현해야 하며, 본문 설명을 완전히 대체하지 않는다.

## Documentation Rules

* Put design documents under `docs/design/`.
* Put work-order documents under `docs/work-orders/`.
* Put work results and retrospectives under `docs/work-logs/`.
* Put procedures the user runs themselves (verification, applying the patch, operations) under `docs/guides/`. Keep only repeatable procedures there, and link the design and work log they rest on.
* Put findings from the original XBE and `Media` (confirmed behavior, hypotheses, unresolved questions) under `docs/analysis/`, organized by topic.
* Put generally applicable technical definitions, background and the glossary (`docs/kb/glossary.md`) under `docs/kb/`, organized by topic and linked to external sources when derived from them.
* Reflect the project's broad direction and phases in `docs/PLAN.md`.
* Update the results handed to reJSRF (addresses, formats, the font approach) in `docs/handoff-rejsrf.md` at each phase.
* When rules change, update `AGENTS.md` and the related documents together.
* Use the `YYYYMMDD-i###-slug.md` filename format for task documents, where `###` is the task's GitHub issue number padded to three digits (for example issue #6 → `20261020-i006-slug.md`).
* Use Mermaid whenever structure, relationships, flows, call sequences, state transitions, or address translation can be visualized.
* Evaluate Mermaid whenever content has three or more components, steps, branches, or layers, and choose a fitting form (flowchart, sequenceDiagram, stateDiagram, classDiagram, ...).
* Do not force diagrams into single-fact or one-step explanations.
* Mermaid diagrams must express the same facts and confirmation status as the prose and must not replace the written explanation.

## 분석 및 지식 기반 유지 규칙

* 바이너리 분석이나 패치 검증으로 새로운 사실이 확인되거나 기존 결론이 바뀌면 같은 작업에서 관련 `docs/analysis/` 문서를 갱신한다.
* 작업 중 프로젝트 이해에 중요한 새로운 용어, 형식(문자 인코딩, 텍스처 압축 등), 표준이 등장하면 관련 `docs/kb/` 문서를 작성하거나 갱신한다.
* 외부 자료에서 얻은 기술 지식에는 가능한 한 권위 있는 출처 링크를 가까운 위치에 남긴다.
* `docs/analysis/`는 **확인됨**, **추정**, **미확정**을 구분한다.
* analysis 또는 kb 파일을 추가하거나 이름을 바꾸면 해당 디렉터리의 `README.md` 색인을 같은 작업에서 갱신한다.
* `docs/work-logs/`는 시간순 작업 증거로, `docs/analysis/`와 `docs/kb/`는 주제별 누적 문서로 유지한다.
* reJSRF에서 확인된 사실은 출처를 달아 가져온다. US판에서만 확인된 사실은 일본판에서 다시 확인하기 전까지 **추정**으로 적는다. 다른 프로젝트에서 얻은 주장도 우리 바이너리에서 다시 확인하기 전까지 **추정**으로 적고 출처를 단다.

## Analysis and Knowledge Base Maintenance Rules

* When binary analysis or patch verification confirms a new fact or changes an earlier conclusion, update the relevant `docs/analysis/` topic in the same task.
* When important new terminology, formats (character encodings, texture compression, ...) or standards arise, create or update the relevant `docs/kb/` topic.
* Place authoritative external links near derived technical knowledge.
* Distinguish **confirmed**, **inferred**, and **unresolved** statements in `docs/analysis/`.
* When adding or renaming an analysis or knowledge file, update that directory's `README.md` index in the same task.
* Keep `docs/work-logs/` as chronological evidence and `docs/analysis/` and `docs/kb/` as cumulative topic references.
* Facts confirmed in reJSRF are carried over with their source. Facts confirmed only on the US build are recorded as **inferred** until re-checked on the Japanese build. Claims from other projects are likewise **inferred**, with their source, until re-checked on our binary.

---

## 도구 구조

* `tools/`: 패치 도구와 분석 도구(Python). 표준 라이브러리를 우선 쓰고, 외부 패키지가 필요하면 설계 문서에 이유를 적고 허용적 라이선스만 쓴다.
* `patch/`: 패치 데이터(커밋함). `text/`(번역문), `glyphs`(글리프 배치), `xbe/`(XBE 패치), `font/`(재배포 가능한 글꼴과 라이선스). 형식은 issue #2 설계에서 확정한다.
* 도구는 입력(덤프)을 읽기만 하고, `out/`(패치 결과물) 또는 `work/`(추출한 원문과 중간 결과)에만 쓴다. 입력 폴더를 고치지 않는다.
* 패치 도구는 입력의 MD5를 검증하고, 다르면 아무것도 쓰지 않고 멈춘다.

## Tool Structure

* `tools/`: the patcher and analysis tools (Python). Prefer the standard library; when an external package is needed, give the reason in a design document and use only permissively licensed ones.
* `patch/`: patch data (committed): `text/` (translations), `glyphs` (glyph layout), `xbe/` (XBE patches), `font/` (a redistributable font and its license). The formats are settled in the issue #2 design.
* Tools only read their input (the dump) and write only to `out/` (patched output) or `work/` (extracted original text and intermediates). They never modify the input folder.
* The patcher checks the input's MD5s and stops without writing anything on a mismatch.

---

## 구현 규칙

* 주소는 일본판 XBE의 가상 주소로 적고, US판 대응 주소와 대응을 확인한 방법(코드 비교, 바이트 패턴)을 함께 적는다.
* 새 기능을 추가할 때는 테스트 전략 또는 최소 검증 절차(특히 왕복 시험)를 문서에 함께 남긴다.
* 코드 수정이 있는 작업은 영향 범위에 맞는 검증을 수행하고, 불가능하면 이유를 작업 로그에 남긴다.
* 소스 코드 주석은 영어로만 작성한다.
* 큰 기능은 하나의 거대 파일에 누적하지 않는다. 독립적으로 이름 붙일 수 있는 부분(XBE 읽기, `NORM` 레코드, 글꼴 아틀라스 등)은 전용 모듈로 분리한다.

## Implementation Rules

* Addresses are written as virtual addresses of the Japanese XBE, with the US counterpart beside them and how the match was established (code comparison, byte pattern).
* When adding a feature, document the test strategy or minimum verification procedure (round trips in particular).
* For tasks that modify code, run verification appropriate to the impact. If verification is impossible, record the reason in the work log.
* Write source-code comments in English only.
* Do not accumulate major features in one monolithic file. Give independently named parts (XBE reading, `NORM` records, the font atlas, ...) their own modules.

---

## 게임 데이터와 생성물 규칙

* `roms/`, XBE, ISO, 게임 자산은 절대 커밋하지 않는다. 사용자가 자기 덤프를 제공한다.
* 덤프에서 **추출한 원문 문장**(일본어·영어)은 커밋하지 않는다. `work/`에 두고 로컬에서 다시 만든다. 패치 데이터에는 원문 대신 위치와 원문 해시만 적는다.
* **패치된 결과물**(`out/`)은 커밋하지 않는다.
* 코드 패치에 원본 명령 바이트를 넣지 않는다. 원래 바이트의 검증은 해시로 한다. 패치 데이터에는 우리가 쓴 코드·자료만 넣는다.
* 커밋 전에 `git status`로 `roms/`, `out/`, `work/`와 게임 데이터가 staging되지 않았는지 확인한다.

## Game Data and Generated Output Rules

* Never commit `roms/`, XBEs, ISOs or game assets. Users supply their own dump.
* **Original text extracted** from the dump (Japanese and English) is never committed. It lives in `work/` and is rebuilt locally. Patch data records only the place and a hash of the original instead of the text.
* **Patched output** (`out/`) is never committed.
* Code patches carry no original instruction bytes; the original bytes are checked by hash. Patch data holds only code and data we wrote.
* Before committing, check with `git status` that `roms/`, `out/`, `work/` and no game data are staged.

---

## 라이선스 규칙

* 프로젝트 라이선스는 `MIT License`다.
* 서드파티 오픈소스는 MIT, BSD, zlib, ISC, Apache-2.0, Boost 같은 허용적 라이선스만 포함한다. 글꼴은 SIL OFL 1.1처럼 재배포가 허용된 것만 쓴다.
* GPL, LGPL, AGPL 같은 전염성 라이선스의 코드는 실행 경로에 넣지 않고 저장소에 복사하지도 않는다.
* 에뮬레이터(xemu 등)는 검증용 외부 도구로만 쓰고 코드는 가져오지 않는다. 전염성 라이선스 프로젝트는 동작을 이해하는 지식 출처로만 참고한다.
* 라이선스가 명시되지 않았거나 LLM 기여를 금지한 프로젝트(예: Codeberg `KeybadeBlox/JSRF-Decompilation`)의 코드는 가져오지 않는다. 공개 문서의 사실은 출처를 달아 참고할 수 있다.
* reJSRF(MIT)의 분석 스크립트는 복사해 쓸 수 있다. 복사할 때 출처(reJSRF 경로와 커밋)를 파일 머리와 작업 로그에 적는다.
* 서드파티 코드나 글꼴을 가져오면 같은 작업에서 `THIRD_PARTY_NOTICES.md`를 갱신한다. 예외가 필요하면 먼저 문서화하고 사용자 확인을 받는다.
* 가져온 서드파티 코드에서 문제(버그, 이식성)를 찾으면 우리 사본만 고치지 않고 업스트림에 기여한다.

## License Rules

* The project license is the `MIT License`.
* Only permissively licensed third-party code (MIT, BSD, zlib, ISC, Apache-2.0, Boost, ...) is included. Fonts are used only when redistribution is allowed, such as SIL OFL 1.1.
* Copyleft code (GPL, LGPL, AGPL) is neither put on the execution path nor copied into the repository.
* Emulators (xemu and the like) are used only as external verification tools; none of their code is taken. Copyleft projects are consulted only as sources of knowledge about behavior.
* Do not take code from projects with no stated license or that forbid LLM contributions (for example Codeberg `KeybadeBlox/JSRF-Decompilation`). Facts from their public documents may be used with attribution.
* reJSRF's (MIT) analysis scripts may be copied. When copying, record the source (the reJSRF path and commit) in the file header and the work log.
* When bringing in third-party code or a font, update `THIRD_PARTY_NOTICES.md` in the same task. If an exception is needed, document it and confirm with the user first.
* When a problem (a bug, a portability issue) is found in third-party code we took, contribute the fix upstream instead of fixing only our copy.

---

## 작업 단위 규칙

* task는 GitHub issue로 만든다. task 번호는 GitHub issue 번호를 쓴다.
* 기존 task의 후속 작업(남은 검증, 후속 수정)은 새 issue를 만들지 않고 그 task의 issue에 붙인다.
* 커밋 제목 끝에 관련 issue 번호를 `(#6)`처럼 붙인다.
* 의미 있는 작업마다 하나의 작업 지시 문서를 만든다.
* 작업이 끝나면 대응되는 작업 로그를 남긴다.
* 설계 없이 바로 코드만 추가하지 않는다.
* 초기 구조 작업이라도 디렉터리 목적과 향후 확장 방향을 문서로 남긴다.

## Task Unit Rules

* A task is created as a GitHub issue, and the task number is the GitHub issue number.
* Follow-up work on an existing task (verification left open, a follow-up fix) goes to that task's issue rather than a new one.
* End commit titles with the related issue number, as in `(#6)`.
* Create one work-order document for each meaningful task.
* When the task is complete, leave the corresponding work log.
* Do not add code directly without a design.
* Even for initial structure work, document the directory purpose and future extension direction.

---

## Git 작업 규칙

* 사용자가 작업을 요청하면 먼저 현재 Git 브랜치명을 확인한다.
* 현재 브랜치가 `main`이면 사용자가 요청한 작업 내용을 바탕으로 작업용 브랜치를 새로 만든 뒤 작업한다.
* 현재 브랜치가 `main`이 아니면 새 브랜치를 만들지 않고 그 브랜치에서 이어서 작업한다. 다른 issue의 작업이어도 같다. 커밋마다 제목 끝에 해당 issue 번호를 붙여 구분한다.
* 작업 단위가 하나 끝날 때마다 관련 변경을 Git 커밋으로 남긴다.
* 프로젝트 버전은 저장소 루트의 `VERSION` 파일에서 `major.minor.patch` 형식으로 관리한다.
* 사용자가 머지를 요청하면 `main`에 머지하기 전에 patch 버전을 1 증가시킨다.
* 사용자가 minor 버전 증가를 요청하면 minor 버전을 1 증가시키고 patch 버전은 0으로 리셋한다.
* 사용자가 major 버전 증가를 요청하면 major 버전을 1 증가시키고 minor와 patch 버전은 0으로 리셋한다.
* 사용자가 머지를 요청하면 작업 브랜치를 원격에 push하고 GitHub pull request를 만든 뒤(머지 요청이 이 push와 PR 생성의 승인이다), 그 PR을 squash merge해 `main`에 넣는다. 머지한 뒤 `git pull`로 로컬 `main`을 원격과 같게 갱신한다.
* PR 본문에는 해결하는 issue를 `Closes #6`처럼 적는다. 여러 issue를 해결하면 issue마다 적는다.
* squash merge의 커밋 제목은 작업 브랜치 안의 커밋 제목들을 확인하고, 전체 변경 내용을 잘 표현하는 제목으로 만든다.
* `main`에 머지한 뒤에는 그 머지 커밋에 `VERSION`과 같은 값의 annotated tag를 `vmajor.minor.patch` 형식으로 붙인다.
* tag 메시지에는 해당 버전의 핵심 변경을 한 줄로 남긴다.
* tag는 로컬까지만 만들고 원격 push는 사용자가 직접 수행한다.
* 머지가 완료되면 현재 작업 브랜치를 삭제한다.
* 릴리스 노트(`docs/release-notes/v<version>.md`)에는 해결된 issue 번호와 그 커밋 ID를 함께 적는다.

## Git Workflow Rules

* When the user requests work, first check the current Git branch name.
* If the current branch is `main`, create a task branch based on the requested work before making changes.
* If the current branch is not `main`, keep working on it without creating a new branch, even for a different issue. Each commit title ends with its own issue number.
* Leave a Git commit for the related changes whenever one task unit is complete.
* Manage the project version in the repository-root `VERSION` file using `major.minor.patch`.
* When the user requests a merge, increment the patch version by 1 before merging into `main`.
* When the user requests a minor version bump, increment the minor version by 1 and reset the patch version to 0.
* When the user requests a major version bump, increment the major version by 1 and reset the minor and patch versions to 0.
* When the user requests a merge, push the task branch, open a GitHub pull request from it (the merge request approves this push and the pull request), and squash-merge it into `main`. Afterwards update local `main` with `git pull`.
* Name the issues the pull request resolves in its description, as in `Closes #6`, one per issue.
* For the squash merge's commit title, inspect the branch's commit titles and write one that describes the complete change.
* After merging into `main`, tag that merge commit with an annotated tag matching `VERSION`, in the form `vmajor.minor.patch`.
* Put a one-line summary of the version's key change in the tag message.
* Create tags locally only; the user pushes them to the remote.
* Delete the task branch after the merge is complete.
* Release notes (`docs/release-notes/v<version>.md`) record the resolved issue numbers together with their commit IDs.

---

## 개발 철학

여러 구현이 가능할 때는 원본 게임 동작을 보존하면서 코드 패치와 리버스 엔지니어링 부담을 최소화하는 방법을 선택한다. 화면 결과는 문서나 코드를 읽어서 추론하지 말고 xemu나 reJSRF에서 실행해서 확인한다.

최적화보다 정확성을 우선한다.

## Development Philosophy

When multiple implementations are possible, choose the one that preserves the original game behavior while minimizing code patches and reverse engineering effort. Check what appears on screen by running it in xemu or reJSRF rather than inferring it from documents or code.

Accuracy is preferred over optimization.
