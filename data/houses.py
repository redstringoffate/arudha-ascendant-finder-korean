# ======================================================
#   Ascendant 기반 하우스/로드 자동 생성기
# ======================================================

# 12궁 로드 정보
rashi_lords = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter"
}

# 12궁 순서 리스트 (순환 가능)
rashi_order = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


# ------------------------------------------------------
# Ascendant를 받아서 1~12H 별자리 생성
# ------------------------------------------------------
def generate_house_signs(asc_sign):
    idx = rashi_order.index(asc_sign)
    return {h+1: rashi_order[(idx + h) % 12] for h in range(12)}


# ------------------------------------------------------
# 1~12H 별자리 → 1~12H 로드 생성
# ------------------------------------------------------
def generate_house_lords(asc_sign):
    house_signs = generate_house_signs(asc_sign)
    return {h: rashi_lords[house_signs[h]] for h in range(1, 13)}
