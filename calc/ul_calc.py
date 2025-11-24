def calc_UL(lord_positions, house_lords):

    # 1) 12H 로드
    lord = house_lords[12]
    lord_house = lord_positions[lord]

    # 2) 거리 계산
    dist = house_distance(12, lord_house)

    # 0 → 1 처리
    if dist == 0:
        dist = 1

    # 3) 기본 UL
    ul = lord_house + dist
    if ul > 12:
        ul -= 12

    # 4) UL 전용 예외: 결과가 12H면 1H
    if ul == 12:
        ul = 1

    # 5) UL 전용 예외: 1H → 7H 이동
    if ul == 1:
        ul = 7

    return ul
