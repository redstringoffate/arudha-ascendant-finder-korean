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
#  후보 생성 시 1차 그룹핑
#   (AL/A7/A10/UL 전체 텍스트 기준 → 완전히 동일한 조합만 묶음)
# ============================================================
def group_candidates_initial(raw_dict):

    grouped = {}

    for slot, data in raw_dict.items():

        asc = data["asc"]
        aro = data["arudha"]

        combined_key = (
            DICT_MAP["AL"]["house"][aro["AL"]],
            DICT_MAP["A7"]["house"][aro["A7"]],
            DICT_MAP["A10"]["house"][aro["A10"]],
            DICT_MAP["UL"]["house"][aro["UL"]],
        )

        if combined_key not in grouped:
            grouped[combined_key] = {
                "asc": asc,
                "arudha": aro,
                "slots": [slot]
            }
        else:
            grouped[combined_key]["slots"].append(slot)

    # 딕셔너리 → 리스트
    return list(grouped.values())



# ============================================================
#  질문 단계별 2차 그룹핑 (핵심!!)
#   AL 단계 → AL 텍스트만 기준으로 그룹핑
#   A7 단계 → A7 텍스트만 기준으로 그룹핑
#   A10 단계 → A10 텍스트만 기준으로 그룹핑
#   UL 단계 → UL 텍스트만 기준으로 그룹핑
# ============================================================
def group_candidates_for_step(cands_list, key):
    grouped = {}

    for item in cands_list:
        aro = item["arudha"]

        # 지금 질문 중인 Arudha key만 기준
        text = DICT_MAP[key]["house"][aro[key]]

        if text not in grouped:
            grouped[text] = item  # 대표 1개만 유지

    return list(grouped.values())



# ============================================================
#  라디오 버튼 스타일
# ============================================================
def style_radio_buttons():
    st.markdown("""
    <style>

    div[data-baseweb="radio"] > div {
        display: flex;
        gap: 20px;
        margin-top: 8px;
        margin-bottom: 10px;
    }

    div[data-baseweb="radio"] label {
        padding: 8px 16px;
        border-radius: 6px;
        background-color: #eee;
        border: 1px solid #555;
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
# 2) 후보 Asc/Arudha 생성
# ============================================================
def generate_candidates():

    raw = {}

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

        raw[slot] = {
            "asc": asc,
            "arudha": reduced
        }

    # 1차 그룹핑 (전체 텍스트 기준)
    st.session_state.candidates = group_candidates_initial(raw)

# ============================================================
#  텍스트 정규화 (줄바꿈 문제 해결)
# ============================================================
def normalize_text(s: str):
    """HTML <br> 변형들을 전부 통일"""
    s = s.replace("<br> \n", "<br>")
    s = s.replace("<br>\n", "<br>")
    s = s.replace("<br>  \n", "<br>")
    s = s.replace("<br>   \n", "<br>")
    return s


# ============================================================
#  단계별 텍스트 기반 그룹핑
# ============================================================
def group_candidates_for_step(cands_list, key):
    grouped = {}

    for item in cands_list:
        aro = item["arudha"]
        txt = normalize_text(DICT_MAP[key]["house"][aro[key]])

        if txt not in grouped:
            grouped[txt] = item

    return list(grouped.values())


# ============================================================
# 3) 질문 페이지
# ============================================================
def page_question():

    style_radio_buttons()

    all_cands = st.session_state.candidates   # 내부 후보
    step = st.session_state.question_step
    key = ARUDHA_FLOW[step]

    # UI용 후보 정리 (표시용)
    display_cands = group_candidates_for_step(all_cands, key)

    # 안내문
    if key != "UL":
        st.title("👁 Image Pattern Question")
        st.write("전혀 아니다라고 느껴지는 항목만 **No**로 표시해주세요.")
    else:
        st.title("💞 Relationship Pattern Question")
        st.write("전혀 아니다라고 느껴지는 설명만 **No**로 표시해주세요.")

    st.divider()

    # 이번 스텝에서 제거할 index 목록
    removal = []

    for shown_idx, record in enumerate(display_cands):

        aro = record["arudha"]
        house_num = aro[key]

        text = normalize_text(DICT_MAP[key]["house"][house_num])
        text = text.replace("<br>", "<br><br>")

        st.markdown(text, unsafe_allow_html=True)

        selected = st.radio(
            "",
            options=["yes", "no", "maybe"],
            key=f"q_{step}_{shown_idx}",
            horizontal=True
        )

        if selected == "no":
            # 실제 내부 후보들 중 해당 텍스트 가진 것 모두 제거 대상으로 표시
            for real_idx, real_item in enumerate(all_cands):
                if normalize_text(DICT_MAP[key]["house"][real_item["arudha"][key]]) \
                        == normalize_text(DICT_MAP[key]["house"][house_num]):
                    removal.append(real_idx)

        st.markdown("---")

    # Next / Finish 버튼
    if step == len(ARUDHA_FLOW) - 1:
        if st.button("Finish", use_container_width=True):

            # 실제 후보 제거
            st.session_state.candidates = [
                x for i, x in enumerate(all_cands) if i not in removal
            ]

            st.session_state.page = "result"
            st.rerun()
    else:
        if st.button("Next", use_container_width=True):

            # 실제 후보 제거
            st.session_state.candidates = [
                x for i, x in enumerate(all_cands) if i not in removal
            ]

            st.session_state.question_step += 1
            st.rerun()



# ============================================================
# 4) 결과 페이지
# ============================================================
def page_result():

    st.title("🎯 Likely Ascendant(s)")

    cands = st.session_state.candidates

    if not cands:
        st.error("모든 후보가 제거되었습니다. 입력을 다시 확인하세요.")
        return

    asc_list = sorted(list({data["asc"] for data in cands}))
    st.write("가능성이 높은 Ascendant 후보:")

    for asc in asc_list:
        st.markdown(f"**{asc}**")

    st.success("최종 Ascendant 후보가 도출되었습니다.")



# ============================================================
# 라우팅
# ============================================================
if st.session_state.page == "input_times":
    page_input_times()
elif st.session_state.page == "question":
    page_question()
elif st.session_state.page == "result":
    page_result()

