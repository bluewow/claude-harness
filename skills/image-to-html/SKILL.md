---
name: image-to-html
description: 사용자가 "/image-to-html" slash command를 입력했을 때만 활성화. 디자인 이미지를 영역별로 크롭하여 HTML/CSS로 구현한다. 이미지 붙여넣기, 디버깅 요청, UI 수정 요청 등 일반적인 이미지 관련 작업에서는 트리거하지 않는다.
---

# Image to HTML

전체 페이지 디자인 이미지를 영역별로 크롭 → 개별 분석 → HTML/CSS 구현.

## 사용법

```
/image-to-html <이미지_경로>
```

---

## 프로세스

### Phase 1: 이미지 분석 & 크롭

1. **전체 이미지 로드** - Read로 원본 이미지를 열어 전체 구조 파악
2. **자동 경계 감지** - 크롭 스크립트 실행:
   ```
   python .claude/skills/image-to-html/crop_sections.py <이미지경로> <출력폴더> [min_height]
   ```
3. **크롭 검증** - 모든 크롭 이미지를 Read로 한장씩 열어 아래 체크리스트로 판정:

   **[A] 크기 검증**
   - 높이 80px 미만 → WARN: 너무 작은 조각, 인접 섹션에 병합 필요 가능성
   - 높이가 원본의 30% 초과 → WARN: 2개 이상 영역이 합쳐졌을 가능성

   **[B] 경계 검증**
   - 상단/하단 가장자리에 콘텐츠(텍스트, 이미지, 카드)가 잘려 있는지 확인
   - 잘린 콘텐츠가 있으면 → FAIL: 경계 위치 보정 필요

   **[C] 인접 섹션 비교**
   - 연속된 2개 섹션의 배경색이 동일하고 콘텐츠가 연속되면 → 병합 후보
   - 반대로, 한 섹션 안에 배경색이 뚜렷하게 바뀌는 구간이 있으면 → 분할 후보

   **[D] 의미 단위 확인**
   - 각 크롭이 하나의 의미 있는 섹션(header, hero, cards, footer 등)에 대응하는지 확인
   - 검증 완료 후 파일명을 의미 있는 이름으로 변경 (예: `03_section_2.png` → `03_cards.png`)

   **판정 결과 예시:**
   ```
   01_header.png    (92px)   - PASS
   02_section_1.png (660px)  - PASS → 02_hero.png 으로 rename
   03_section_2.png (135px)  - WARN: 80px 근접, dot indicator만 포함 → hero에 병합
   04_section_3.png (110px)  - FAIL: 상단에 이전 섹션 텍스트 잘림 → 경계 보정
   ```

4. **경계 보정** - WARN/FAIL 항목에 대해 수동 경계로 재크롭:
   ```python
   from PIL import Image
   img = Image.open(img_path)
   boundaries = [0, 92, 752, ...]  # 보정된 경계
   for i, (s, e) in enumerate(zip(boundaries, boundaries[1:])):
       img.crop((0, s, img.width, e)).save(f"sections/{i+1:02d}_section.png")
   ```
5. **섹션 목록 출력** - 최종 결과(PASS 항목만)를 사용자에게 보여주고 확인

### Phase 2: 스타일 가이드 추출

크롭 이미지들에서 공통 스타일 요소 추출:
- 색상 팔레트, 타이포그래피, 간격 체계, 컴포넌트 패턴

`css/style.css` 상단에 주석으로 기록.

### Phase 3: 섹션별 구현

각 크롭 이미지에 대해 순차적으로:
1. **크롭 이미지 Read** - 아래 [이미지 분석 기준]에 따라 분석
2. **HTML 작성** - 시맨틱 태그, BEM 네이밍
3. **CSS 작성** - Phase 2 스타일 가이드 기반
4. **사용자 확인** - 브라우저 확인 요청 후 다음 섹션

---

## 이미지 분석 기준

크롭 이미지를 Read로 열었을 때, 반드시 다음 순서로 분석한다:

1. **레이아웃 구조** - flex/grid 방향, 정렬 방식, 열/행 수, 중첩 구조
2. **요소 목록** - 보이는 모든 요소를 빠짐없이 나열 (텍스트, 아이콘, 이미지, 버튼, 구분선, 뱃지 등)
3. **텍스트 내용** - 보이는 텍스트를 정확히 그대로 기록 (추측하지 않음, 잘려서 안 보이면 "잘림" 표기)
4. **색상** - 배경색, 텍스트색, 보더색, 아이콘색을 각각 hex로 추정
5. **크기/간격** - 요소 크기, 요소 간 gap, padding, margin을 px 단위로 추정
6. **폰트** - weight(400/500/600/700/800), size(px), letter-spacing 추정
7. **특수 스타일** - 그림자, border-radius, 그라데이션, opacity, 호버 효과 등

### 분석 출력 예시

```
[06_section_5 분석]
- 레이아웃: flex row, 3열 균등 배치, gap ~24px, 중앙 정렬
- 요소: 카드 3개 (아이콘 + 제목 + 설명)
  - 카드1: 비디오 아이콘(빨강), "이지캠", NEW 뱃지, 설명 2줄
  - 카드2: PDF 아이콘, "이지뷰어", Coming Soon 오버레이
  - 카드3: 캡처 아이콘(그라데이션), "이지캡쳐", 설명 2줄
- 색상: 카드 배경 #ffffff, 카드 보더 없음, 그림자 있음, 텍스트 #333
- 크기: 카드 width ~300px, 카드 간 gap ~24px, 패딩 ~32px
- 폰트: 제목 16px/700, 설명 14px/400 #666
- 특수: 카드 border-radius ~16px, box-shadow 0 2px 12px rgba(0,0,0,0.08)
```

이 분석을 완료한 뒤 HTML/CSS를 작성한다. 분석 없이 바로 코드를 쓰지 않는다.

---

## 모델 선택 가이드

| Phase | 작업 | 권장 모델 | 이유 |
|-------|------|-----------|------|
| Phase 1 | 이미지 분석 & 크롭 | **opus** | 이미지 해석 정확도 |
| Phase 2 | 스타일 가이드 추출 | **opus** | 디자인 언어 이해 |
| Phase 3 | HTML/CSS 구현 | **sonnet** | 코드 생성 속도 + 비용 효율 |

Agent 사용 시 `model` 파라미터로 전환:
```
Agent(model="sonnet", prompt="크롭 이미지 기반으로 hero 섹션 HTML/CSS 구현...")
```

---

## 출력 구조

출력 경로: `output/image-to-html/{이미지파일명(확장자제외)}/`

```
output/image-to-html/
└── {이미지파일명}/
    ├── index.html
    ├── css/
    │   └── style.css
    └── images/sections/    ← 크롭된 섹션 이미지
```

예시: 입력이 `landing-page.png`이면 → `output/image-to-html/landing-page/` 에 생성

---

## 핵심 원칙

1. **크롭 먼저, 구현은 나중** - 전체 이미지를 한번에 분석하지 않는다
2. **크롭 검증 필수** - 모든 크롭 결과를 Read로 열어 확인한다
3. **섹션 단위 진행** - 한 섹션 완료 → 사용자 확인 → 다음 섹션
4. **추측 금지** - 크롭 이미지에서 보이지 않는 요소는 만들지 않는다
