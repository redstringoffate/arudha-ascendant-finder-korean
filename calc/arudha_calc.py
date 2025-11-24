def house_distance(start, end):
    """start → end 거리계산 (1~12 cycle)"""
    if end >= start:
        return end - start
    return (12 - start) + end


def calc_arudha(n, lord_positions, house_lords):
    lord = house_lords[n]
    lord_house = lord_positions[lord]

    # 기본 거리
    dist = house_distance(n, lord_house)

    # Arudha 기본 계산
    arudha = lord_house + dist
    if arudha > 12:
        arudha -= 12

    # 예외 1 — 같은 하우스
    if arudha == n:
        arudha += 10
        if arudha > 12:
            arudha -= 12

    # 예외 2 — 7번째 (180도)
    seventh = ((n + 6 - 1) % 12) + 1
    if arudha == seventh:
        arudha += 10
        if arudha > 12:
            arudha -= 12

    return arudha


def calc_all_arudhas(lord_positions, house_lords):
    result = {}
    result["AL"] = calc_arudha(1, lord_positions, house_lords)
    for n in range(2, 13):
        result[f"A{n}"] = calc_arudha(n, lord_positions, house_lords)
    return result
