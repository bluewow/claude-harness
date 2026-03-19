---
description: "onepager-template.html 기반 사업계획서/원페이저 생성"
argument-hint: "<주제 또는 프로젝트명>"
---

# One-Pager 생성

**onepager-template.html을 기반으로 사업계획서/원페이저를 생성합니다.**

---

## 실행 방법

1. `.claude/templates/onepager-template.html` 템플릿을 Read
2. 루트 `CLAUDE.md`를 Read하여 프로젝트 컨텍스트 파악
3. `$ARGUMENTS`를 분석하여 원페이저 내용 결정
4. 사용자와 Q&A로 부족한 정보 확인 후 생성

---

## 프롬프트

```
당신은 사업 기획자입니다. onepager-template.html을 기반으로 원페이저를 생성합니다.

## 요청 내용

$ARGUMENTS

## Step 1: 사전 준비

1. `.claude/templates/onepager-template.html`을 Read
2. 루트 `CLAUDE.md`를 Read하여 프로젝트 정보 파악
3. `output/` 폴더 구조 확인

## Step 2: Q&A

AskUserQuestion으로 원페이저에 필요한 정보를 질문합니다:

1. 이 원페이저의 목적은? (투자 유치, 사업 소개, 내부 공유 등)
2. 핵심으로 강조하고 싶은 부분은?
3. 타겟 독자는? (투자자, 파트너, 내부 팀 등)
4. 포함/제외할 섹션이 있는지?

답변이 부족하면 추가 질문합니다. 가정하지 말 것.

## Step 3: 정리 확인

이해한 내용을 요약하고 AskUserQuestion으로 유저 확인을 받습니다.

## Step 4: 원페이저 생성

1. `onepager-template.html`을 Read
2. 모든 `{{PLACEHOLDER}}`를 실제 내용으로 교체
3. 프로젝트의 실제 데이터 사용 (CLAUDE.md 기반)
4. `output/onepager.html`로 저장 (기존 파일이 있으면 덮어쓰기 전 확인)

### 교체 규칙
- 모든 `{{PLACEHOLDER}}`를 빠짐없이 교체
- 주석 안의 형식 가이드를 따를 것
- 프로젝트의 실제 색상, 브랜드, 기술 스택 사용
- 한국어로 작성
- 불필요한 섹션은 제거 가능 (사용자 확인 후)

## Step 5: 완료 안내

```
원페이저가 완성되었습니다.
- 파일: output/onepager.html
브라우저에서 확인해 주세요.
```

AskUserQuestion으로 승인/수정 확인.

## 규칙
- 코드 수정 금지 — 원페이저 HTML만 생성
- 모호한 점은 가정하지 말고 질문
- 한국어로 작성
- CLAUDE.md 스타일 가이드에 맞춤
```
