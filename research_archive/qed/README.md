# QED Research Archive

Quantum Edge Detection(QED) 선행연구 아카이브.

## 구조

```
research_archive/qed/
├── README.md                 # 이 파일
├── TEMPLATE.md               # 통일 분석 템플릿 (새 엔트리 작성 시 복사)
├── index.yaml                # 메타데이터 인덱스 (Streamlit 검색/필터용)
├── generate_figures.py       # SVG 다이어그램 생성 스크립트
├── entries/                  # 개별 논문 엔트리
│   ├── yao2017_qhed/
│   │   └── entry.md
│   ├── zhang2015_neqr_edge/
│   │   └── entry.md
│   └── fan2019_quantum_laplacian/
│       └── entry.md
└── figures/                  # SVG 다이어그램
    ├── qed_pipeline_overview.svg
    ├── qhed_circuit_blocks.svg
    ├── qed_comparison_table.svg
    └── *.mmd                 # Mermaid 소스 파일
```

## 새 논문 추가 방법

1. `entries/` 아래에 `{author}{year}_{topic}/` 폴더 생성
2. `TEMPLATE.md`를 복사하여 `entry.md`로 저장 후 내용 작성
3. `index.yaml`에 새 엔트리 메타데이터 추가
4. (선택) `figures/`에 관련 다이어그램 추가

## 다이어그램 재생성

```bash
python research_archive/qed/generate_figures.py
```

## Streamlit에서 열람

```bash
streamlit run app.py
# → 사이드바에서 "6. Literature Archive" 선택
```
