# ======================================================
#   Arudha Pada Calculator (A1 ~ A12)
#   Jaimini 방식 기반 — 예외 규칙 완전 포함
# ======================================================

def house_distance(start, end):
    """start → end까지의 거리 (1~12 순환)"""
    if end >= start:
        return end - start
    return (12 - start) + end


def calc_arudha(n, lord_positions, house_lords):
    """
    A(n) 계산 함수
    n: 기준 하우스 번호 (1~12)
    lord_positions: {"Moon": 11, ...}
    house_lords: {1: "Moon", ...}
    """

    # 1) 기준 하우스 로드 찾기
    lord = house_lords[n]
    lord_house = lord_positions[lord]

    # ------------------------------------------------------
    # 🔥 예외 규칙 1: lord가 같은 하우스에 있을 때
    # ------------------------------------------------------
    if lord_house == n:
        arudha = n + 10
        if arudha > 12:
            arudha -= 12
        return arudha

    # ------------------------------------------------------
    # 🔥 예외 규칙 2: lord가 7번째 하우스에 있을 때
    #     즉, 정반대 (distance = 7)
    # ------------------------------------------------------
    if house_distance(n, lord_house) == 7:
        arudha = n + 4
        if arudha > 12:
            arudha -= 12
        return arudha

    # ------------------------------------------------------
    # 2) 기본 거리 계산
    # ------------------------------------------------------
    dist = house_distance(n, lord_house)

    # 3) Arudha = lord_house + dist
    arudha = lord_house + dist
    if arudha > 12:
        arudha -= 12

    # ------------------------------------------------------
    # 🔥 doubling rule — 결과가 원래 하우스와 같을 때
    # ------------------------------------------------------
    if arudha == n:
        arudha = arudha + dist
        if arudha > 12:
            arudha -= 12

    return arudha


def calc_all_arudhas(lord_positions, house_lords):
    result = {}
    result["AL"] = calc_arudha(1, lord_positions, house_lords)

    for n in range(2, 13):
        result[f"A{n}"] = calc_arudha(n, lord_positions, house_lords)

    return result
