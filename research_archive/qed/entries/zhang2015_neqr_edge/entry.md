# NEQR: A Novel Enhanced Quantum Representation of Digital Images and Edge Detection

> **Entry ID**: `zhang2015_neqr_edge`
> **Last Updated**: 2026-03-13

---

## (A) TL;DR (간단 요약)

- NEQR(Novel Enhanced Quantum Representation) 기반 양자 이미지 표현을 사용한 엣지 검출 알고리즘 제안
- 픽셀 강도를 큐빗 비트열(basis state)로 인코딩하여 FRQI 대비 이미지 복원 정확도 향상
- 양자 비교 연산(quantum comparator)으로 인접 픽셀 차이를 계산하여 엣지 검출 수행
- Basis encoding 방식의 장단점을 잘 보여주는 초기 QED 연구

---

## (B) 상세 요약

### 문제 정의

기존 FRQI(Flexible Representation of Quantum Images)는 픽셀 강도를 회전각으로 인코딩하는데, 이는 측정 시 확률적 복원만 가능하여 정확도가 낮다. 더 정확한 양자 이미지 표현과 이를 활용한 엣지 검출이 가능한가?

### 핵심 아이디어

NEQR은 각 픽셀의 그레이스케일 값(0~255)을 8개 큐빗의 basis state로 직접 인코딩한다. 이를 통해 측정 시 정확한 픽셀 값 복원이 가능하며, 양자 비교 연산으로 인접 픽셀 간 차이를 판별한다.

### 방법

1. **NEQR 인코딩**: 2^n × 2^n 이미지의 각 픽셀을 위치 큐빗(2n개) + 강도 큐빗(q개, 보통 8)으로 인코딩
2. **양자 비교기**: 인접 픽셀 쌍의 강도 큐빗을 양자 비교 회로로 비교
3. **엣지 판별**: 비교 결과가 임계값 초과 시 해당 위치를 엣지로 표시
4. **측정 및 재구성**: 전체 이미지를 측정하여 엣지맵 재구성

### 결과

- FRQI 대비 이미지 복원 정확도 크게 향상 (결정론적 복원)
- 시뮬레이션에서 클래식 엣지 검출과 유사한 엣지맵 생성
- 그러나 큐빗 수가 2n + q로 amplitude encoding 대비 많이 필요

---

## (C) 원리 / 메커니즘

### 양자 회로 / 연산 흐름

```
|0⟩^{⊗(2n+q)} ─── [NEQR Encoding] ─── [Quantum Comparator] ─── [Measure]
                     ↓                        ↓
               위치(2n) + 강도(q)      인접 픽셀 차이 > 임계값?
```

### 핵심 수식

**NEQR 표현**:

$$|I\rangle_{NEQR} = \frac{1}{2^n} \sum_{y=0}^{2^n-1} \sum_{x=0}^{2^n-1} |f(y,x)\rangle |y\rangle |x\rangle$$

여기서 $|f(y,x)\rangle = |c_{q-1} c_{q-2} \ldots c_0\rangle$는 픽셀 (y,x)의 그레이스케일 값의 이진 표현.

---

## (D) 장점 / 기여

- 측정 시 결정론적 픽셀 값 복원 가능 (FRQI의 확률적 복원 문제 해결)
- 양자 비교 연산을 통한 직관적인 엣지 검출 프레임워크
- Basis encoding의 장점과 한계를 체계적으로 분석

---

## (E) 문제점 / 한계

| 한계 항목 | 설명 |
|-----------|------|
| 데이터 인코딩 비용 | 큐빗 수 2n+q로 amplitude encoding(2k+1) 대비 훨씬 많음 |
| 노이즈 민감도 | 많은 큐빗 사용으로 NISQ 디바이스에서 실행 어려움 |
| 확장성 | 256×256 이미지: 16+8=24 큐빗 필요 (현재 하드웨어 한계 근접) |
| 재현성 | 시뮬레이션만 제공, 실제 하드웨어 실험 없음 |

---

## (F) 비교 / 베이스라인

| 방법 | 큐빗 수 | 인코딩 정확도 | 엣지 검출 | 실용성 |
|------|---------|-------------|----------|--------|
| NEQR (본 논문) | 2n + q | 결정론적 | 양자 비교기 | 큐빗 수 제한 |
| FRQI | 2n + 1 | 확률적 | 제한적 | 적은 큐빗 |
| QHED (Yao2017) | 2k + 1 | 확률적 | Hadamard 기반 | 적은 큐빗 |
| Classical Sobel | N/A | 정확 | 컨볼루션 | 성숙한 기술 |

---

## (G) 재현 / 구현 노트

| 항목 | 내용 |
|------|------|
| 필요 라이브러리 | Qiskit, NumPy |
| 데이터셋 | 소규모 그레이스케일 이미지 |
| 큐빗 수 | 2n + q (4×4 이미지: 4+8=12 큐빗) |
| 회로 깊이 | O(2^{2n} × q) |
| 실행 환경 | 시뮬레이터 전용 |
| 실행 비용/시간 | 시뮬레이션: 큐빗 수에 따라 기하급수적 증가 |
| 코드 공개 여부 | 미공개 |

---

## (H) 키워드 / 태그

- **데이터 인코딩**: basis
- **엣지 정의**: gradient
- **회로 타입**: comparator
- **노이즈 고려**: no
- **평가 방식**: visual, complexity

---

## (I) 인용 정보

```bibtex
@article{zhang2015neqr,
  title   = {NEQR: a novel enhanced quantum representation of digital images},
  author  = {Zhang, Yi and Lu, Kai and Gao, Yinghui and Wang, Mo},
  journal = {Quantum Information Processing},
  volume  = {12},
  number  = {8},
  pages   = {2833--2860},
  year    = {2013},
  doi     = {10.1007/s11128-013-0567-z},
}
```

**링크**: [https://doi.org/10.1007/s11128-013-0567-z](https://doi.org/10.1007/s11128-013-0567-z)

---

## (J) 그림 / 다이어그램

![QED Pipeline](../../figures/qed_pipeline_overview.svg)

---

## (K) 오픈 퀘스천 / 후속 연구 아이디어

- NEQR과 amplitude encoding의 하이브리드 접근은 가능한가?
- Basis encoding에서 양자 비교기의 회로 깊이를 줄일 수 있는 최적화 기법은?
- QRAM이 실용화되면 NEQR의 인코딩 비용 문제가 해결되는가?
