import streamlit as st

# Calculation functions
from calc.arudha_calc import calc_all_arudhas
from calc.ul_calc import calc_UL
from data.houses import generate_house_lords

# Arudha dictionaries
from dict import AL, A7, A10, UL


# ============================================================
# 초기 상태
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
# 유틸
# ============================================================
def slot_to_label(i:int):
    if i == 24:
        return "23:59"
    return f"{i:02d}:00"


def normalize_text(s:str):
    s = s.replace("<br> \n", "<br>")
    s = s.replace("<br>\n", "<br>")
    s = s.replace("\n", "")
    return s


# ============================================================
# Streamlit 스타일
# ============================================================
def style_radio_buttons():
    st.markdown("""
    <style>
    div[data-baseweb="radio"] > div {
        display: flex;
        gap: 20px;
        margin-top: 10px;
        margin-bottom: 14px;
    }
    div[data-baseweb="radio"] label {
        padding: 8px 16px;
        border-radius: 6px;
        background-color: #eeeeee;
        border: 1px solid #555;
        font-weight: 600;
        cursor: pointer;
    }
    div[data-baseweb="radio"] input[value="yes"]:checked + label {
        background-color:#C6F6D5; border-color:#38A169;
    }
    div[data-baseweb="radio"] input[value="no"]:checked + label {
        background-color:#FEB2B2; border-color:#E53E3E;
    }
    div[data-baseweb="radio"] input[value="maybe"]:checked + label {
        background-color:#FAF089; border-color:#D69E2E;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 1) 시간 입력 페이지
# ============================================================
def page_input_times():

    slot = st.session_state.current_slot
    label = slot_to_label(slot)

    st.title("🕰 Arudha Ascendant Finder")
    st.subheader(f"Transit Input — {label}")
    st.write("해당 시간의 Ascendant 및 Sun~Saturn House 정보를 입력하세요.")

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
# 2) 후보 asc 전체 생성
# ============================================================
def generate_candidates():

    cands = []

    for slot, data in st.session_state.transit_data.items():

        asc = data["asc"]
        hpos = data["houses"]

        hl = generate_house_lords(asc)
        aru = calc_all_arudhas(hpos, hl)
        ul  = calc_UL(hpos, hl)

        reduced = {
            "AL": aru["AL"],
            "A7": aru["A7"],
            "A10": aru["A10"],
            "UL": ul
        }

        cands.append({
            "asc": asc,
            "arudha": reduced,
            "slot": slot
        })

    st.session_state.candidates = cands


# ============================================================
# 내부 문항 생성 (ASC 단위)
# ============================================================
def build_internal_questions(candidates, key):
    internal = []
    qid = 0

    for c in candidates:
        hnum = c["arudha"][key]
        raw_text = DICT_MAP[key]["house"][hnum]
        text = normalize_text(raw_text)

        internal.append({
            "qid": qid,
            "text": raw_text,
            "asc": c["asc"],
            "slot": c["slot"],
            "hnum": hnum
        })
        qid += 1

    return internal


# ============================================================
# UI 문항 묶음 생성 (텍스트 기준)
# ============================================================
def group_questions_for_ui(internal_questions):
    groups = {}

    for q in internal_questions:
        t = q["text"]
        if t not in groups:
            groups[t] = []
        groups[t].append(q["qid"])

    ui_list = []
    for text, qids in groups.items():
        ui_list.append({
            "text": text,
            "qid_list": qids
        })

    return ui_list


# ============================================================
# 3) 질문 페이지
# ============================================================
def page_question():

    style_radio_buttons()

    candidates = st.session_state.candidates
    step = st.session_state.question_step
    key = ARUDHA_FLOW[step]

    # 내부 문항 생성
    internal = build_internal_questions(candidates, key)

    # UI 묶음 생성
    ui_groups = group_questions_for_ui(internal)

    if key != "UL":
        st.title("👁 Image Pattern Question")
        st.write("전혀 아니다 싶은 항목만 No를 선택하세요.")
    else:
        st.title("💞 Relationship Pattern Question")
        st.write("당신의 관계/배우자 패턴과 전혀 다르면 No를 선택하세요.")

    st.divider()

    remove_asc = set()

    # UI 문항 출력
    for gi, g in enumerate(ui_groups):

        t = g["text"].replace("<br>", "<br><br>")
        st.markdown(t, unsafe_allow_html=True)

        answer = st.radio(
            "",
            ["yes", "no", "maybe"],
            key=f"step_{step}_group_{gi}",
            horizontal=True
        )

        if answer == "no":
            for qid in g["qid_list"]:
                asc = internal[qid]["asc"]
                remove_asc.add(asc)

        st.markdown("---")

    # ASC 생존자 계산
    survivors = [c for c in candidates if c["asc"] not in remove_asc]

    # 페이지 이동
    if step == len(ARUDHA_FLOW) - 1:
        if st.button("Finish", use_container_width=True):
            st.session_state.candidates = survivors
            st.session_state.page = "result"
            st.rerun()
    else:
        if st.button("Next", use_container_width=True):
            st.session_state.candidates = survivors
            st.session_state.question_step += 1
            st.rerun()


# ============================================================
# 5) 결과 페이지
# ============================================================
def page_result():

    st.title("🎯 Likely Ascendant(s)")

    cands = st.session_state.candidates

    if not cands:
        st.error("모든 Asc가 제거되었습니다. 입력값을 다시 확인하세요.")
        return

    asc_list = sorted({c["asc"] for c in cands})

    st.write("가능성이 높은 Ascendant:")

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
