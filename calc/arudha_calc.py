# ======================================================
#   Upapada Lagna (UL) Calculator — 독립형 완성 버전
#   Jaimini 방식 기반 + 표준 예외 규칙 포함
# ======================================================

# ------------------------------------------------------
#   하우스 거리 계산 (1~12 순환)
# ------------------------------------------------------
def house_distance(start, end):
    """
    start → end까지 1~12 사이클 거리 계산
    e.g. (12 → 2) = 2 / (5 → 3) = 10
    """
    if end >= start:
        return end - start
    return (12 - start) + end


# ------------------------------------------------------
#   Upapada Lagna 계산
#   UL = 12H의 Pada
#   규칙 정리:
#     1) 12H의 로드를 찾는다
#     2) distance(12 → lord_house) 계산
#     3) distance = 0 이면 1로 처리 (UL 고유 규칙)
#     4) UL = lord_house + distance
#     5) UL이 12H면 1H로 이동
#     6) 추가 규칙: UL이 1H이면 7H로 이동 (일반적으로 쓰이는 전통)
# ------------------------------------------------------
def calc_UL(lord_positions, house_lords):
    """
    lord_positions: {"Sun":5, "Moon":11, ...}
    house_lords:    {1:"Mars", 2:"Venus", ..., 12:"Saturn"}
    """

    # 1) 12H 로드
    lord = house_lords[12]
    lord_house = lord_positions[lord]

    # 2) 거리 계산
    dist = house_distance(12, lord_house)

    # 3) 0칸이면 1칸 처리
    if dist == 0:
        dist = 1

    # 4) UL 기본 계산
    ul = lord_house + dist
    if ul > 12:
        ul -= 12

    # 5) UL 예외: 결과가 12H면 반드시 1H로 이동
    if ul == 12:
        ul = 1

    # 6) UL 전용 규칙: UL = 1H → 7H로 이동
    #    (가장 널리 쓰이는 Jaimini school 법칙)
    if ul == 1:
        ul = 7

    return ul
