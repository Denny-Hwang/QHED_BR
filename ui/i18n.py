"""Lightweight i18n for the QHED-BR Streamlit app.

Only top-level UI strings (navigation, buttons, headers, parameter labels)
are translated; long-form technical content (LaTeX, references, complexity
analysis) stays in English regardless of the active locale.

The selected language is persisted in the URL query string so it survives
page reloads and is shareable.
"""

from __future__ import annotations

import streamlit as st

SUPPORTED = ("en", "ko")
DEFAULT_LANG = "en"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Sidebar / nav
        "nav.lang_label": "Language",
        "nav.title": "Navigation",
        "nav.home": "Home",
        "nav.overview": "1. Research Overview",
        "nav.circuit": "2. QHED Circuit Explained",
        "nav.edge_detection": "3. Interactive Edge Detection",
        "nav.complexity": "4. Complexity Comparison",
        "nav.ibm": "5. IBM Quantum Hardware",
        "nav.literature": "6. Literature Archive",

        # Home / landing
        "home.title": "QHED-BR — Quantum Hadamard Edge Detection",
        "home.subtitle": "Boundary-restored quantum edge detection for the NISQ era",
        "home.intro": (
            "Encode an image as a quantum state, detect edges in O(1) "
            "quantum gates, and recover boundary information that would "
            "otherwise be lost when patching large images on small quantum "
            "processors."
        ),
        "home.quickstart": "Quick Start — try a sample in one click",
        "home.quickstart_hint": "Each card runs QHED + classical Sobel on a built-in image and shows the result.",
        "home.card_cat": "Photo (cat)",
        "home.card_coastline": "Satellite (coastline)",
        "home.card_fingerprint": "Fingerprint",
        "home.run_button": "Run sample",
        "home.go_to_lab": "Open Interactive Lab",
        "home.explore_more": "Or pick a page from the sidebar to dig deeper.",

        # Page 3 — Interactive Edge Detection
        "ed.title": "Interactive Edge Detection",
        "ed.subtitle": "Upload your own image or pick a sample, then compare quantum and classical edge detection.",
        "ed.section_select": "1. Select image",
        "ed.section_params": "2. Parameters",
        "ed.section_results": "3. Results",
        "ed.source_label": "Image source",
        "ed.source_sample": "Sample images",
        "ed.source_upload": "Upload your own",
        "ed.param_image_size": "Resize image to (2^n x 2^n)",
        "ed.param_patch_qb": "Patch qubits (per dimension)",
        "ed.param_threshold": "Threshold ratio",
        "ed.param_br_mode": "Boundary restoration",
        "ed.param_remove_noise": "Apply Gaussian blur (classical methods)",
        "ed.br_with": "With Restoration (overlapping patches)",
        "ed.br_without": "Without Restoration (non-overlapping)",
        "ed.tab_qhed": "QHED (Quantum)",
        "ed.tab_classical": "Classical Methods",
        "ed.tab_compare": "Side-by-Side Comparison",
        "ed.run_qhed": "Run QHED",
        "ed.compare_modes": "Compare With vs Without Restoration",
        "ed.run_classical": "Run Classical Edge Detection",
        "ed.run_full": "Run Full Comparison",
        "ed.original": "Original",
        "ed.download_qhed": "Download QHED result",
        "ed.download_comparison": "Download comparison image",
        "ed.download_classical": "Download classical results",
        "ed.download_full": "Download full comparison",
        "ed.info_select_image": "Please select or upload an image to begin.",
        "ed.cached_badge": "(cached)",
        "ed.completed_in": "Completed in",
        "ed.stale_warning": "Results below were computed with previous parameters. Re-run to update.",

        # Page 5 — IBM Quantum Hardware
        "ibm.demo_mode_toggle": "Demo mode (skip authentication)",
        "ibm.demo_mode_help": "Browse the page and read the explanation without entering IBM credentials.",
    },
    "ko": {
        # Sidebar / nav
        "nav.lang_label": "언어",
        "nav.title": "메뉴",
        "nav.home": "홈",
        "nav.overview": "1. 연구 개요",
        "nav.circuit": "2. QHED 회로 설명",
        "nav.edge_detection": "3. 인터랙티브 엣지 검출",
        "nav.complexity": "4. 복잡도 비교",
        "nav.ibm": "5. IBM 양자 하드웨어",
        "nav.literature": "6. 문헌 아카이브",

        # Home / landing
        "home.title": "QHED-BR — 양자 하다마드 엣지 검출",
        "home.subtitle": "NISQ 시대를 위한 경계 복원 기반 양자 엣지 검출",
        "home.intro": (
            "이미지를 양자 상태로 인코딩해 O(1) 게이트로 엣지를 검출하고, "
            "큐빗 수가 제한된 양자 프로세서에서 패치 분할 시 손실되는 "
            "경계 정보를 다항 시간 추가 연산으로 복원합니다."
        ),
        "home.quickstart": "빠른 시작 — 클릭 한 번으로 샘플 실행",
        "home.quickstart_hint": "각 카드는 내장 이미지에 QHED + 고전 Sobel을 실행해 결과를 보여줍니다.",
        "home.card_cat": "사진 (고양이)",
        "home.card_coastline": "위성 (해안선)",
        "home.card_fingerprint": "지문",
        "home.run_button": "샘플 실행",
        "home.go_to_lab": "인터랙티브 모드 열기",
        "home.explore_more": "또는 사이드바에서 자세히 보고 싶은 페이지를 선택하세요.",

        # Page 3 — Interactive Edge Detection
        "ed.title": "인터랙티브 엣지 검출",
        "ed.subtitle": "직접 이미지를 업로드하거나 샘플을 골라, 양자와 고전 엣지 검출을 비교해보세요.",
        "ed.section_select": "1. 이미지 선택",
        "ed.section_params": "2. 파라미터",
        "ed.section_results": "3. 결과",
        "ed.source_label": "이미지 출처",
        "ed.source_sample": "샘플 이미지",
        "ed.source_upload": "직접 업로드",
        "ed.param_image_size": "이미지 크기 (2^n x 2^n)",
        "ed.param_patch_qb": "패치 큐빗 수 (차원당)",
        "ed.param_threshold": "Threshold ratio",
        "ed.param_br_mode": "경계 복원",
        "ed.param_remove_noise": "가우시안 블러 적용 (고전 방법)",
        "ed.br_with": "복원 적용 (중첩 패치)",
        "ed.br_without": "복원 미적용 (비중첩)",
        "ed.tab_qhed": "QHED (양자)",
        "ed.tab_classical": "고전 방법",
        "ed.tab_compare": "나란히 비교",
        "ed.run_qhed": "QHED 실행",
        "ed.compare_modes": "복원 유무 비교",
        "ed.run_classical": "고전 엣지 검출 실행",
        "ed.run_full": "전체 비교 실행",
        "ed.original": "원본",
        "ed.download_qhed": "QHED 결과 다운로드",
        "ed.download_comparison": "비교 이미지 다운로드",
        "ed.download_classical": "고전 결과 다운로드",
        "ed.download_full": "전체 비교 다운로드",
        "ed.info_select_image": "이미지를 선택하거나 업로드해 주세요.",
        "ed.cached_badge": "(캐시됨)",
        "ed.completed_in": "처리 시간",
        "ed.stale_warning": "아래 결과는 이전 파라미터로 계산된 값입니다. 다시 실행해주세요.",

        # Page 5 — IBM Quantum Hardware
        "ibm.demo_mode_toggle": "데모 모드 (인증 건너뛰기)",
        "ibm.demo_mode_help": "IBM 인증 정보 없이 페이지 설명만 둘러봅니다.",
    },
}


def get_lang() -> str:
    """Read the active language from the URL query string."""
    try:
        raw = st.query_params.get("lang", DEFAULT_LANG)
    except Exception:
        raw = DEFAULT_LANG
    return raw if raw in SUPPORTED else DEFAULT_LANG


def set_lang(lang: str) -> None:
    """Persist the active language to the URL query string."""
    if lang not in SUPPORTED:
        lang = DEFAULT_LANG
    try:
        st.query_params["lang"] = lang
    except Exception:
        pass


def t(key: str) -> str:
    """Translate ``key`` for the active language, falling back to the key."""
    lang = get_lang()
    table = TRANSLATIONS.get(lang) or TRANSLATIONS[DEFAULT_LANG]
    return table.get(key) or TRANSLATIONS[DEFAULT_LANG].get(key, key)


def render_lang_switcher(location=st.sidebar) -> None:
    """Render a compact KR/EN toggle in the sidebar (or anywhere)."""
    current = get_lang()
    options = list(SUPPORTED)
    labels = {"en": "EN", "ko": "한국어"}
    idx = options.index(current) if current in options else 0
    picked = location.radio(
        t("nav.lang_label"),
        options=options,
        index=idx,
        format_func=lambda x: labels.get(x, x),
        horizontal=True,
        key="__lang_switcher",
    )
    if picked != current:
        set_lang(picked)
        st.rerun()
