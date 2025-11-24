import streamlit as st
from calc.arudha_calc import calc_all_arudhas
from calc.ul_calc import calc_UL
from data.houses import generate_house_lords
from dict import AL, A7, A10, UL


# ============================================================
# 최초 초기화
# ============================================================
if "initialized" not in st.session_state:
    st.session_state.page = "input_times"
    st.session_state.transit_data = {}
    st.session_state.current_slot = 0
    st.session_state.candidates = None
    st.session_state.question_step = 0
    st.session_state.initialized = True


# ============================================================
# 상수
# ============================================================
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

ASC_SIGNS = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

ARUDHA_FLOW = ["AL", "A7", "A10", "UL"]

DICT_MAP = {
    "AL": AL.Arudha_dict,
    "A7": A7.Arudha_dict,
    "A10": A10.Arudha_dict,
    "UL": UL.Arudha_dict
}


# ============================================================
# Slot → 시간 라벨
# ============================================================
def slot_to_label(i: int):
    if i == 24:
        return "23:59"
    return f"{i:02d}:00"


# ============================================================
# UI용 텍스트 정규화
# ============================================================
def normalize_text(s: str):
    s = s.replace("<br> \n", "<br>")
    s = s.replace("<br>\n", "<br>")
    s = s.replace("<br>  \n", "<br>")
    return s


# ============================================================
# 라디오 스타일 적용
# ============================================================
def style_radio_buttons():
    st.markdown("""
    <style>

    div[data-baseweb="radio"] > div {
        display: flex;
        gap: 16px;
        margin-top: 8px;
        margin-bottom: 12px;
    }

    div[data-baseweb="radio"] label {
        padding: 8px 16px;
        border-radius: 8px;
        background-color: #eee;
        border: 1px solid #777;
        cursor: pointer;
        font-weight: 600;
    }

    div[data-baseweb="radio"] input[value="yes"]:checked + label {
        background-color: #C6F6D5;
        border-color: #38A169;
    }

    div[data-baseweb="radio"] input[value="no"]:checked + label {
        background-color: #FEB2B2;
        border-color: #E53E3E;
    }

    div[data-baseweb="radio"] input[value="maybe"]:checked + label {
        background-color: #FAF089;
        border-color: #D69E2E;
    }

    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 1) 시간대 입력 페이지
# ============================================================
def page_input_times():

    slot = st.session_state.current_slot
    label = slot_to_label(slot)

    st.title("🕰 Arudha Ascendant Finder")
    st.subheader(f"Transit Input — {label}")
    st.write("해당 시간의 Transit 정보를 입력해주세요.")

    lord_positions = {}

    # 이전 slot 반영
    if slot > 0 and (slot - 1) in st.session_state.transit_data:
        prev = st.session_state.transit_data[slot - 1]

        asc = st.selectbox(
            "Ascendant", ASC_SIGNS,
            index=ASC_SIGNS.index(prev["asc"])
        )

        for p in PLANETS:
            lord_positions[p] = st.selectbox(
                f"{p} House",
                range(1, 13),
                index=prev["houses"][p] - 1
            )

    else:
        asc = st.selectbox("Ascendant", ASC_SIGNS)
        for p in PLANETS:
            lord_positions[p] = st.selectbox(f"{p} House", range(1, 13))

    st.markdown(f"### Slot: {slot}")

    if st.button("Save & Next", use_container_width=True):

        st.session_state.transit_data[slot] = {
            "asc": asc,
            "houses": lord_positions
        }

        if slot < 24:
            st.session_state.current_slot += 1
            st.session_state.page = "input_times"
        else:
            generate_candidates()
            st.session_state.page = "question"

        st.rerun()


# ============================================================
# 2) 후보 Asc/Arudha 생성 (중복 제거 없음)
# ============================================================
def generate_candidates():

    raw = []

    for slot, data in st.session_state.transit_data.items():

        asc = data["asc"]
        houses = data["houses"]

        hl = generate_house_lords(asc)
        arudhas = calc_all_arudhas(houses, hl)
        ul = calc_UL(houses, hl)

        reduced = {
            "AL": arudhas["AL"],
            "A7": arudhas["A7"],
            "A10": arudhas["A10"],
            "UL": ul
        }

        raw.append({
            "asc": asc,
            "arudha": reduced
        })

    st.session_state.candidates = raw


# ============================================================
# 3) 한 단계에 표시할 항목 (Asc + house 기반 중복 제거)
# ============================================================
def candidates_for_display(cands, key):

    seen = set()
    result = []

    for item in cands:
        asc = item["asc"]
        house_num = item["arudha"][key]

        group_key = (asc, house_num)

        if group_key not in seen:
            seen.add(group_key)
            result.append(item)

    return result


# ============================================================
# 4) 질문 페이지
# ============================================================
def page_question():

    style_radio_buttons()

    all_cands = st.session_state.candidates
    step = st.session_state.question_step
    key = ARUDHA_FLOW[step]

    # UI용 후보
    display_list = candidates_for_display(all_cands, key)

    # 안내문
    if key != "UL":
        st.title("👁 Image Pattern Question")
        st.write("전혀 아니다 라고 느껴지는 항목만 **No**로 선택해주세요.")
    else:
        st.title("💞 Relationship Pattern Question")
        st.write("전혀 아니다 라고 느껴지는 설명만 **No**로 선택해주세요.")

    st.divider()

    # 이번 단계에서 제거해야 할 실제 후보 index
    removal_indices = []

    for ui_idx, item in enumerate(display_list):

        asc = item["asc"]
        house_num = item["arudha"][key]

        text = normalize_text(DICT_MAP[key]["house"][house_num])
        text_html = text.replace("<br>", "<br><br>")

        st.markdown(text_html, unsafe_allow_html=True)

        sel = st.radio(
            "",
            options=["yes", "no", "maybe"],
            key=f"q_{step}_{ui_idx}",
            horizontal=True
        )

        if sel == "no":
            # 실제 후보 중 동일 asc + 동일 house_num 제거
            for real_i, c in enumerate(all_cands):
                if c["asc"] == asc and c["arudha"][key] == house_num:
                    removal_indices.append(real_i)

        st.markdown("---")

    # Next / Finish
    if step == len(ARUDHA_FLOW) - 1:
        if st.button("Finish", use_container_width=True):

            st.session_state.candidates = [
                x for i, x in enumerate(all_cands) if i not in removal_indices
            ]

            st.session_state.page = "result"
            st.rerun()

    else:
        if st.button("Next", use_container_width=True):

            st.session_state.candidates = [
                x for i, x in enumerate(all_cands) if i not in removal_indices
            ]

            st.session_state.question_step += 1
            st.rerun()


# ============================================================
# 5) 결과 페이지
# ============================================================
def page_result():

    st.title("🎯 Likely Ascendant(s)")

    cands = st.session_state.candidates

    if not cands:
        st.error("모든 후보가 제거되었습니다. 입력을 다시 확인해주세요.")
        return

    asc_list = sorted(list({c["asc"] for c in cands}))

    st.write("가능성이 높은 Ascendant 후보:")

    for asc in asc_list:
        st.markdown(f"**{asc}**")

    st.success("최종 Ascendant 후보를 도출했습니다.")


# ============================================================
# 라우팅
# ============================================================
if st.session_state.page == "input_times":
    page_input_times()
elif st.session_state.page == "question":
    page_question()
elif st.session_state.page == "result":
    page_result()
