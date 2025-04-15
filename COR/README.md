# Causal Representation Learning for OOD Recommendation

논문  "Causal Representation Learning for Out-of-Distribution Recommendation" 을 바탕으로 인과 표현 학습 기반 추천 시스템을 구현하고, 이를 LLM 기반 추천 에이전트로 확장하는 것을 목표로 합니다.

## 주간 일정 (2025.04.08 ~ 2025.05.20)

| 주차       | 일정                                 | 세부 내용 |
|------------|--------------------------------------|-----------|
| 4/08 (1주차) | 논문 구조 분석 및 1차 구현 | 모델 구성 요소 파악, 구현 범위 설정 |
| 4/15 (2주차) | 데이터셋 구성 + OOD 시나리오 설계      |  |
| 4/22 (3주차) | 모델 구현 완료 (Causal 구조 포함)       |  |
| 4/29 (4주차) | LLM 에이전트 1차 개발         | 추천 시스템 초기 구현 |
| 5/06 (5주차) | LLM 에이전트 및 추천 시스템 고도화      | |
| 5/13 (6주차) | LLM 에이전트 2차 개발 | 시연 스크립트(질의 시나리오) 구성 |
| 5/20 (7주차) | 회고  | 전체 구조 리뷰, 코드 리팩토링, 문서화 및 기능 정리 |


## 진행 상황 (2025.04.15 기준)

### Preprocessing

- user feature / item feature가 all-zero vector인 경우 제거
- 이외의 추가적인 interaction 수 기준 필터링은 논문에는 명시되어 있지 않음
- 우리는 논문 기준 전처리만 우선 적용

**전처리 적용 결과:**
- Interaction 수는 약 14,000건 유지
- zero vector 제거로 noise 감소

### Experiment Results

#### Step 1: COR Pretrain (논문 전처리 기준)

- dropout=0.5, 100 epochs 기준 학습
- Precision@10: 0.0008 / Recall@10: 0.0079
- OOD 성능도 낮음 (Precision@10: 0.0005)

| 항목 | 값 |
| --- | --- |
| 학습 사용자 수 | 7096명 |
| 학습 아이템 수 | 5260개 |
| 학습 인터랙션 수 | 14192건 |
| Sparsity | 0.9996 |

#### Step 2: OOD Fine-tuning

- `-ood_finetune` 옵션 적용
- 대부분 초반(2~8 epoch)에 Best epoch 발생
- Recall, NDCG 큰 변화 없음

#### Step 3: Dropout Variation

| Dropout | Precision@10 | Recall@10 | NDCG@10 |
| --- | --- | --- | --- |
| 0.2 | 0.0011 | 0.0112 | 0.0063 |
| 0.5 | 0.0009 | 0.0172 | 0.0078 |
| 0.7 | 0.0008 | 0.0159 | 0.0071 |

→ Recall 기준으로는 0.5가 가장 안정적

#### Step 4: Additional Filtering

- 유저 5회 이상 클릭, 아이템 10회 이상 선택 조건
- interaction 수 급감 (iid 40, ood 2건)
- 모델 학습 불가능 → 실험 불가

---

### Key Factors of Performance Drop

#### (1) 데이터 희소성

- Sparsity 0.9996 → 유저당 평균 interaction 수 매우 적음
- OOD 유저 feature는 대부분 unseen → 학습 어려움

#### (2) Z1 / Z2 분리 성능 미흡

- 데이터가 적어 Z2가 의도를 충분히 포착하지 못함

#### (3) 논문 구현과의 구조 차이

- 일부 layer 정의 및 forward 구조에서 차이 존재


### Next Step

#### 1: Meituan 데이터 정제

- [user, item] 쌍 리스트 → `user → items` binary vector 구조로 변환
- MultiVAE, RecVAE와의 비교 실험에 활용

#### 2: Baseline 모델과 비교

- MultiVAE, CDAE, RecVAE 등 구현은 되어 있음
- COR와 동일 조건에서 성능 비교 실험 필요
