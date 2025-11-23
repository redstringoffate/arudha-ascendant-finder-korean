# ======================================================
#   Upapada Lagna (UL) Calculator
#   Jaimini 방식 기반 — 12H의 Pada
# ======================================================

# ------------------------------------------------------
#   하우스 거리 계산 (1~12 순환)
# ------------------------------------------------------
def house_distance(start, end):
    if end >= start:
        return end - start
    return (12 - start) + end


# ------------------------------------------------------
#   Upapada Lagna 계산
# ------------------------------------------------------
def calc_UL(lord_positions, house_lords):
    """
    UL 계산 공식:
    1) 12H의 로드 찾기
    2) 12H → 로드까지 거리 계산 (0 → 1 처리)
    3) 로드 위치 + 거리
    4) 결과가 12H면 1H로 이동 (UL 전용 예외)
    """

    # 1) 12H 로드
    lord = house_lords[12]
    lord_house = lord_positions[lord]

    # 2) 거리 계산
    dist = house_distance(12, lord_house)

    # 0칸이면 1칸 처리
    if dist == 0:
        dist = 1

    # 3) 기본 UL = lord_house + dist
    ul = lord_house + dist
    if ul > 12:
        ul -= 12

    # 4) UL 전용 예외: 결과가 12H면 1H로 이동
    if ul == 12:
        ul = 1

    return ul
