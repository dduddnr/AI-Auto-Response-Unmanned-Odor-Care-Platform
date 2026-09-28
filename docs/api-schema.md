# API 응답 스키마

AI 자동응답 무인악취종합병원 플랫폼 (파일럿)

Backend가 프론트엔드·멀티모달 파트로 내보내는 응답 형식입니다.
RAG 결과든 공공데이터 API 결과든 Backend에서 이 형식으로 조립해 전달하므로,
수신 측은 근거의 출처 종류와 무관하게 항상 동일한 구조를 받습니다.

| | |
|---|---|
| 상태 | 초안 확정 |

---

## 타입 정의

```typescript
type MultimodalInput = {
  schema_version: "0.1";
  request_id: string;              // 로그 추적용 고유 ID

  // 질의 분석 결과
  intent: "status" | "cause" | "regulation" | "mitigation" | "unknown";
  status: "ok" | "partial" | "clarify" | "no_evidence" | "error";

  // 답변 본문 — 문장 블록 단위로 분리하고 각 블록에 근거를 연결
  // 본문에 [E1] 같은 표기를 넣지 않으므로 음성 낭독 시 text만 이어 붙이면 됨
  answer_blocks: {
    id: string;
    text: string;
    evidence_ids: string[];        // 이 문장을 뒷받침하는 evidence.id 목록
  }[];

  confidence: number;              // 근거 충족 점수 0~100
                                   // 정답 확률이나 안전 확률이 아님
                                   // 임계 미만이면 status를 partial로 처리

  evidence: Evidence[];            // 근거 카드에 표시할 출처 목록
  datasets: Dataset[];             // 표·차트로 그릴 데이터

  // status가 clarify일 때만 값이 있음
  follow_up: {
    missing_fields: string[];      // 누락된 슬롯 (region, substance, time_range 등)
    question: string;              // 사용자에게 되물을 문장
  } | null;

  warnings: {
    code: string;
    message: string;
    related_ids: string[];         // 관련된 evidence.id 또는 dataset.id
  }[];
};
```

```typescript
// 모든 근거가 공통으로 갖는 출처 정보
type EvidenceBase = {
  id: string;                      // answer_blocks.evidence_ids와 연결되는 키
  title: string;                   // 문서명 또는 자료명
  publisher: string | null;        // 기관명 (법제처, 한국환경공단 등)
  url: string | null;              // 원문 링크
  reference_date: string | null;   // 자료 기준일 (YYYY-MM-DD)
                                   // 법령이면 개정일, 측정자료면 측정 기준일
  retrieved_at: string;            // 조회 시각 (ISO 8601, 시간대 포함)
                                   // reference_date와 벌어져 있으면 공표 지연 신호
  is_mock: boolean;                // 목업 데이터 여부
                                   // 실데이터 연동 실적 집계에서 제외하기 위함

  evidence_tier: 1 | 2 | 3 | 4 | 5;
  // 근거 계층 — 낮을수록 상위 근거
  // 1 법·표준    악취방지법, 시행규칙, 환경부 고시
  // 2 공공데이터  에어코리아, 국민권익위 민원통계
  // 3 실측·센서   태성 자체 측정·관제 데이터
  // 4 학술       KCI, RISS 등 논문
  // 5 내부지식   태성 설계·저감 노하우
};
```

```typescript
// 근거는 문서(RAG 검색 결과)와 API(공공데이터 조회 결과) 두 종류
// 한 응답에 두 종류가 함께 담길 수 있음
// 예) "기준 초과야?" → 기준값(법령 문서) + 실측값(공공데이터 API)
type Evidence =
  | (EvidenceBase & {
      kind: "document";
      document_type: "law" | "paper" | "other";
      locator: string | null;      // 조항·페이지 (예: "별표3", "제8조")
      excerpt: string;             // 원문 발췌 — 근거 카드에 그대로 노출
    })
  | (EvidenceBase & {
      kind: "api";
      query: Record<string, string | number | boolean | null>;
                                   // 호출 파라미터 — 재현성 확보용
      delivery: "live" | "cache";  // 실시간 조회인지 캐시된 값인지
    });
```

```typescript
// 표·차트에 사용할 데이터
// 시각화 종류에 따라 필요한 구조가 달라 두 가지로 구분
type Dataset =
  // 시계열 — 라인·바 차트용
  | {
      id: string;
      kind: "measurements";
      title: string;
      substance: string;           // 물질명 (복합악취, 황화수소 등)
      location: string;            // 지역명
      unit: string;                // 단위 (희석배수, ppm, μg/m³)
      evidence_ids: string[];      // 이 데이터의 출처
      points: {
        time: string;              // 측정 시각 (ISO 8601, 시간대 포함)
        value: number | null;      // 결측 시 null
        quality: "valid" | "missing" | "invalid";
        // 공공데이터 API는 측정 이상 플래그를 함께 제공하므로
        // 값의 유효성을 함께 전달함
      }[];
    }

  // 비교표 — 테이블용
  // 예) 기준값 vs 실측값, 지역별·물질별 비교
  | {
      id: string;
      kind: "comparison";
      title: string;
      columns: {
        key: string;               // rows.cells의 키와 일치
        label: string;             // 화면에 표시할 컬럼명
        unit: string | null;
      }[];
      rows: {
        cells: Record<string, string | number | boolean | null>;
        evidence_ids: string[];    // 행 단위 출처 — 행마다 근거가 다를 수 있음
      }[];
    };
```

---

## 값 설명

### intent — 질의 유형

| 값 | 의미 | 예시 질문 |
|---|---|---|
| `status` | 현황조회 | "지금 여기 악취 어때?" |
| `cause` | 원인·성분 | "무슨 냄새야? 성분이 뭐야?" |
| `regulation` | 규제·법기준 | "우리 배출 기준 초과야?" |
| `mitigation` | 처방·저감 | "어떻게 줄여?" |
| `unknown` | 분류 실패 | |

### status — 응답 상태

| 값 | 의미 | 화면 처리 |
|---|---|---|
| `ok` | 정상 답변 | 전체 표시 |
| `partial` | 신뢰도 임계 미만 또는 근거 일부 부족 | 불확실 표시 |
| `clarify` | 조건 누락 | `follow_up`으로 재질문 |
| `no_evidence` | 확인된 근거 없음 | "확인되지 않음" 표시 |
| `error` | 시스템 오류 | 오류 안내 |

`ok` 외의 상태에서는 `datasets`가 빈 배열일 수 있습니다.

---

## 예시

```json
{
  "schema_version": "0.1",
  "request_id": "req-0001",
  "intent": "regulation",
  "status": "ok",

  "answer_blocks": [
    {
      "id": "B1",
      "text": "공업지역 배출구의 복합악취 배출허용기준은 희석배수 1000 이하입니다.",
      "evidence_ids": ["E1"]
    },
    {
      "id": "B2",
      "text": "울산 남구 측정소의 2026년 9월 28일 09시 측정값은 3.2입니다.",
      "evidence_ids": ["E2"]
    }
  ],
  "confidence": 87,

  "evidence": [
    {
      "id": "E1",
      "kind": "document",
      "title": "악취방지법 시행규칙 별표3",
      "publisher": "법제처",
      "url": "https://www.law.go.kr/...",
      "reference_date": "2024-01-01",
      "retrieved_at": "2026-09-28T10:00:00+09:00",
      "is_mock": false,
      "evidence_tier": 1,
      "document_type": "law",
      "locator": "별표3",
      "excerpt": "공업지역 배출구 희석배수 1000 이하 ..."
    },
    {
      "id": "E2",
      "kind": "api",
      "title": "에어코리아 실시간 측정소 자료",
      "publisher": "한국환경공단",
      "url": "https://www.airkorea.or.kr/...",
      "reference_date": "2026-09-28",
      "retrieved_at": "2026-09-28T10:00:00+09:00",
      "is_mock": false,
      "evidence_tier": 2,
      "query": { "stationName": "남구", "dataTerm": "DAILY" },
      "delivery": "live"
    }
  ],

  "datasets": [
    {
      "id": "D1",
      "kind": "measurements",
      "title": "울산 남구 복합악취 추이",
      "substance": "복합악취",
      "location": "울산광역시 남구",
      "unit": "희석배수",
      "evidence_ids": ["E2"],
      "points": [
        { "time": "2026-09-28T08:00:00+09:00", "value": 2.9, "quality": "valid" },
        { "time": "2026-09-28T09:00:00+09:00", "value": 3.2, "quality": "valid" }
      ]
    }
  ],

  "follow_up": null,
  "warnings": []
}
```