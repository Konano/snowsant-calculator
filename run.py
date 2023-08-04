# customer_drink = 450
# customer_snack = 180
# customer_token = 30

# buy_drink = [20, 28, 38]
# buy_snack = [10, 20, 32]
# buy_token = [50, 100, 200]

# sell_base_drink = 50
# sell_base_snack = 40
# sell_base_token = 1000

customer_drink = 450
customer_snack = 450
customer_token = 60

buy_drink = [30, 42, 57]
buy_snack = [15, 30, 48]
buy_token = [50, 100, 200]

sell_base_drink = 100
sell_base_snack = 80
sell_base_token = 1000

customer = [customer_drink, customer_snack, customer_token]

stock_drink = customer_drink
stock_snack = customer_snack
stock_token = customer_token

import numpy as np

# aaa = (30, 30, 30)
# aab = (36, 36, 18)
# abb = (36, 27, 27)
# abc = (40, 30, 20)
# aa = (5, 5)
# ab = (6, 4)

sell_drink = np.arange(-5, 6) * 1 + sell_base_drink
sell_snack = np.arange(-5, 6) * 1 + sell_base_snack
sell_token = np.arange(-5, 6) * 10 + sell_base_token
sell = [sell_drink, sell_snack, sell_token]

# ============================================================


from itertools import product
from typing import Tuple


def average_with_weight(pairs):
    return sum([x[0] * x[-1] for x in pairs]) / sum([x[-1] for x in pairs])


# ============================================================


sell_result_cache = {}


def sell_result(bid: Tuple, me: int):
    if (bid, me) in sell_result_cache:
        return sell_result_cache[(bid, me)]
    ranks = [
        sum([1 for i in range(len(bid)) if bid[i] < bid[x]]) for x in range(len(bid))
    ]
    sorted_ranks = np.sort(ranks)
    if len(ranks) == 3:
        if np.all(sorted_ranks == [0, 0, 0]):
            ret = 30
        elif np.all(sorted_ranks == [0, 0, 2]):
            ret = [36, None, 18][ranks[bid.index(me)]]
        elif np.all(sorted_ranks == [0, 1, 1]):
            ret = [36, 27][ranks[bid.index(me)]]
        elif np.all(sorted_ranks == [0, 1, 2]):
            ret = [40, 30, 20][ranks[bid.index(me)]]
        else:
            print(bid, me, ranks, sorted_ranks)
            raise NotImplementedError
    elif len(ranks) == 2:
        if np.all(sorted_ranks == [0, 0]):
            ret = 5
        elif np.all(sorted_ranks == [0, 1]):
            ret = [6, 4][ranks[bid.index(me)]]
        else:
            print(bid, me, ranks, sorted_ranks)
            raise NotImplementedError
    else:
        print(bid, me, ranks, sorted_ranks)
        raise NotImplementedError
    sell_result_cache[(bid, me)] = ret
    return ret


def sell_conflict_checker(statement, info):
    if len(info) == 0:
        return True
    if len(info) == 1:
        return info == statement
    if len(info) == 2:
        return (info[0] is None or info[0] == statement[0]) and (
            info[1] is None or info[1] == statement[1]
        )
    return False


def sell_determine_stage(num, rival_num, info, kind) -> Tuple[float, int]:
    # print(num, rival_num, info, kind)
    statements = [
        statement
        for statement in product(range(11), repeat=[2, 2, 1][kind])
        if sell_conflict_checker(statement, info)
    ]

    best_income, best_choice = -1e9, None
    for c in range(11):
        incomes = []
        for statement in statements:
            customer_base = customer[kind] // [90, 90, 10][kind]
            customer_num = customer_base * sell_result(statement + (c,), c)
            income = min(customer_num, num) * sell[kind][c]
            income_rank = 0
            for _c, _n in zip(statement, rival_num):
                rival_customer_num = customer_base * sell_result(statement + (c,), _c)
                rival_income = min(rival_customer_num, _n) * sell[kind][_c]
                if rival_income > income:
                    income_rank += 1
            # print(c, statement + (c,), sell_result(statement + (c,), c), sell[kind][c], income, income_rank)
            if income_rank == 0:
                income += 5000
            elif income_rank == 1:
                income += 2000
            else:
                income += 1000
            incomes.append(income)
        exp_income = sum(incomes) / len(incomes)
        if exp_income > best_income:
            best_income, best_choice = exp_income, (c,)

    # print(kind, info, best_income, best_choice)
    return best_income, best_choice


sell_stage_cache = {}


def sell_stage(clues, nums, rival_nums, info, kind):
    if kind == 3:
        return 0, -1, None
    if (clues, nums[kind:], rival_nums[kind:], info, kind) in sell_stage_cache:
        return sell_stage_cache[(clues, nums[kind:], rival_nums[kind:], info, kind)]

    best_income, best_choice = sell_determine_stage(
        nums[kind], rival_nums[kind], info, kind
    )
    best_income += sell_stage(clues, nums, rival_nums, (), kind + 1)[0]

    if clues:
        if info == ():
            if kind != 2:
                pry_income = average_with_weight(
                    [
                        sell_stage(
                            clues - 1,
                            nums,
                            rival_nums,
                            (i, None),
                            kind,
                        )
                        for i in range(11)
                    ]
                    + [
                        sell_stage(
                            clues - 1,
                            nums,
                            rival_nums,
                            (None, i),
                            kind,
                        )
                        for i in range(11)
                    ]
                )
                if pry_income > best_income:
                    best_income, best_choice = pry_income, -1
            else:
                pry_income = average_with_weight(
                    [
                        sell_stage(
                            clues - 1,
                            nums,
                            rival_nums,
                            (i,),
                            kind,
                        )
                        for i in range(11)
                    ]
                )
                if pry_income > best_income:
                    best_income, best_choice = pry_income, -1
        elif None in info:
            __idx = 1 - info.index(None)
            pry_income = average_with_weight(
                [
                    sell_stage(
                        clues - 1,
                        nums,
                        rival_nums,
                        (i, info[1]) if __idx == 1 else (info[0], i),
                        kind,
                    )
                    for i in range(info[__idx] + 1)
                ]
            )
            if pry_income > best_income:
                best_income, best_choice = pry_income, -1

    statements = [
        statement
        for statement in product(range(11), repeat=[2, 2, 1][kind])
        if sell_conflict_checker(statement, info)
    ]

    sell_stage_cache[(clues, nums[kind:], rival_nums[kind:], info, kind)] = (
        best_income,
        best_choice,
        len(statements),
    )
    return best_income, best_choice, len(statements)


# ============================================================


buy_result_cache = {}


def buy_result(bid: Tuple, me: int):
    if (bid, me) in buy_result_cache:
        return buy_result_cache[(bid, me)]
    ranks = [
        sum([1 for i in range(len(bid)) if bid[i] > bid[x]]) for x in range(len(bid))
    ]
    sorted_ranks = np.sort(ranks)
    if len(ranks) == 3:
        if np.all(sorted_ranks == [0, 0, 0]):
            ret = 30
        elif np.all(sorted_ranks == [0, 0, 2]):
            ret = [36, None, 18][ranks[bid.index(me)]]
        elif np.all(sorted_ranks == [0, 1, 1]):
            ret = [36, 27][ranks[bid.index(me)]]
        elif np.all(sorted_ranks == [0, 1, 2]):
            ret = [40, 30, 20][ranks[bid.index(me)]]
        else:
            print(bid, me, ranks, sorted_ranks)
            raise NotImplementedError
    elif len(ranks) == 2:
        if np.all(sorted_ranks == [0, 0]):
            ret = 5
        elif np.all(sorted_ranks == [0, 1]):
            ret = [6, 4][ranks[bid.index(me)]]
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError
    buy_result_cache[(bid, me)] = ret
    return ret


def buy_conflict_checker(statement, info):
    if len(info) == 0 or statement == info:
        return True
    if len(info) == 1:
        return info[0] == statement[0]
    return False


def buy_determine_stage(clues, infos) -> Tuple[float, int]:
    statements = [
        statement
        for statement in product(range(3), repeat=5)
        if buy_conflict_checker(statement[0:2], infos[0])
        and buy_conflict_checker(statement[2:4], infos[1])
        and buy_conflict_checker(statement[4:5], infos[2])
    ]

    if len(statements) == 0:
        print(clues, infos)

    best_income, best_choice = -1e9, None
    for c in product(range(3), repeat=3):
        incomes = []
        for statement in statements:
            drink_nums = stock_drink // 90 * buy_result(statement[0:2] + (c[0],), c[0])
            snack_nums = stock_snack // 90 * buy_result(statement[2:4] + (c[1],), c[1])
            token_nums = stock_token // 10 * buy_result(statement[4:5] + (c[2],), c[2])
            costs = (
                drink_nums * buy_drink[c[0]]
                + snack_nums * buy_snack[c[1]]
                + token_nums * buy_token[c[2]]
            )
            nums = (drink_nums, snack_nums, token_nums)
            __sd = stock_drink // 90
            __ss = stock_snack // 90
            __st = stock_token // 10
            rival_nums = (
                (
                    __sd * buy_result(statement[0:2] + (c[0],), statement[0]),
                    __sd * buy_result(statement[0:2] + (c[0],), statement[1]),
                ),
                (
                    __ss * buy_result(statement[2:4] + (c[1],), statement[2]),
                    __ss * buy_result(statement[2:4] + (c[1],), statement[3]),
                ),
                (__st * buy_result(statement[4:5] + (c[2],), statement[4]),),
            )
            # if c == (2, 2, 2):
            #     print(c, statement, nums, rival_nums, costs)
            sell_income = sell_stage(clues, nums, rival_nums, (), 0)[0]
            incomes.append(sell_income - costs)
        exp_income = sum(incomes) / len(incomes)
        if exp_income > best_income:
            best_income, best_choice = exp_income, c
    return best_income, best_choice


buy_stage_cache = {}


def buy_stage(clues: int, infos: Tuple[Tuple, Tuple, Tuple]) -> Tuple[float, int]:
    if (clues, infos) in buy_stage_cache:
        return buy_stage_cache[(clues, infos)]

    best_income, best_choice = buy_determine_stage(clues, infos)

    if clues:
        if len(infos[0]) < 2:
            pry_income = average_with_weight(
                [
                    buy_stage(clues - 1, (infos[0] + (i,), infos[1], infos[2]))
                    for i in range(3)
                ]
            )
            if pry_income > best_income:
                best_income, best_choice = pry_income, 0

        if len(infos[1]) < 2:
            pry_income = average_with_weight(
                [
                    buy_stage(clues - 1, (infos[0], infos[1] + (i,), infos[2]))
                    for i in range(3)
                ]
            )
            if pry_income > best_income:
                best_income, best_choice = pry_income, 1

        if len(infos[2]) < 1:
            pry_income = average_with_weight(
                [
                    buy_stage(clues - 1, (infos[0], infos[1], infos[2] + (i,)))
                    for i in range(3)
                ]
            )
            if pry_income > best_income:
                best_income, best_choice = pry_income, 2

    statements = [
        statement
        for statement in product(range(3), repeat=5)
        if buy_conflict_checker(statement[0:2], infos[0])
        and buy_conflict_checker(statement[2:4], infos[1])
        and buy_conflict_checker(statement[4:5], infos[2])
    ]

    buy_stage_cache[(clues, infos)] = (best_income, best_choice, len(statements))
    return (best_income, best_choice, len(statements))


# ============================================================


def cal_profit(result, cost=0, income=0):
    return (result[0] - cost + income,) + result[1:]


# print(buy_stage(6, ((), (), ())))
# print(buy_stage(5, ((0,), (), ())))
# print(buy_stage(4, ((0, 1), (), ())))
# print(cal_profit(sell_stage(4, (180, 36, 12), ((90, 180), (72, 72), (18,)), (), 0), 6000))
# print(cal_profit(sell_stage(3, (180, 36, 12), ((90, 180), (72, 72), (18,)), (None, 7), 0), 6000))
# print(cal_profit(sell_stage(3, (180, 36, 12), ((90, 180), (72, 72), (18,)), (), 1), 6000, 12650))
# print(cal_profit(sell_stage(3, (180, 36, 12), ((90, 180), (72, 72), (18,)), (), 2), 6000, 12650+2620))
# print(sell_determine_stage(180, (90, 180), (None, 7), 0))

# ============================================================

# print(buy_stage(4, ((), (), ())))
# print(buy_stage(3, ((), (), (2,))))
# print(buy_determine_stage(3, ((), (), (2,))))
# print(sell_stage(3, (216, 180, 35), ((216, 108), (135, 135), (35,)), (), 0))
# print(sell_stage(2, (216, 180, 35), ((216, 108), (135, 135), (35,)), (6,), 0))
# print(sell_stage(1, (216, 180, 35), ((216, 108), (135, 135), (35,)), (6,6), 0))
# print(sell_stage(1, (216, 180, 35), ((216, 108), (135, 135), (35,)), (), 1))
# print(sell_stage(1, (216, 180, 35), ((216, 108), (135, 135), (35,)), (), 2))
# print(sell_stage(1, (216, 180, 35), ((216, 108), (135, 135), (35,)), (5,), 2))

# ============================================================

# print(buy_stage(4, ((), (), ())))

# print(buy_stage(3, ((0,), (), ())))
# print(buy_stage(3, ((1,), (), ())))
# print(buy_stage(3, ((2,), (), ())))
# print(buy_stage(3, ((), (0,), ())))
# print(buy_stage(3, ((), (1,), ())))
# print(buy_stage(3, ((), (2,), ())))
# print(buy_stage(3, ((), (), (0,))))
# print(buy_stage(3, ((), (), (1,))))
# print(buy_stage(3, ((), (), (2,))))

# print(cal_profit(sell_stage(3, (150, 180, 35), ((100, 200), (240, 120), (35,)), (), 0), 18700))
# print(cal_profit(sell_stage(2, (150, 180, 35), ((100, 200), (240, 120), (35,)), (None, 6), 0), 18700))
# print(cal_profit(sell_stage(1, (150, 180, 35), ((100, 200), (240, 120), (35,)), (3, 6), 0), 18700))
# print(cal_profit(sell_stage(1, (150, 180, 35), ((100, 200), (240, 120), (35,)), (), 1), 18700, 20000))
# print(cal_profit(sell_stage(1, (150, 180, 35), ((100, 200), (240, 120), (35,)), (), 2), 18700, 20000+18860))
# print(cal_profit(sell_stage(0, (150, 180, 35), ((100, 200), (240, 120), (35,)), (5,), 2), 18700, 20000+18860))

# print(sell_stage(3, (180, 150, 36), ((90, 180), (100, 200), (24,)), (), 0))

# exit()

# ============================================================

clues = int(input("请输入可打探的次数："))
infos = ((), (), ())
print("请稍等，正在计算……")
while True:
    ret = buy_stage(clues, infos)
    print("当前期望收益为：", ret[0])
    if isinstance(ret[1], int):
        print("***** 请选择打探第 %d 个物品的信息（默认选择第一个未被打探的商家）" % (ret[1] + 1))
        print("请问打探到的消息中，该商家的策略是：")
        choice = int(input("（1：保守，2：稳健，3：激进）"))
        infos = list(infos)
        infos[ret[1]] = infos[ret[1]] + (choice - 1,)
        infos = tuple(infos)
        clues -= 1
    else:
        print("进货策略已确定：")
        print("***** 饮品进货策略：", ["保守", "稳健", "激进"][ret[1][0]])
        print("***** 餐点进货策略：", ["保守", "稳健", "激进"][ret[1][1]])
        print("***** 纪念品进货策略：", ["保守", "稳健", "激进"][ret[1][2]])
        break

print("请告诉我每种东西的进货情况，需要按照商家的顺序给出，每家店的进货情况用空格隔开。")
print("举例子：30 40 50")
drink = tuple(map(int, input("饮品进货情况：").strip().split(" ")))
snack = tuple(map(int, input("餐点进货情况：").strip().split(" ")))
token = tuple(map(int, input("纪念品进货情况：").strip().split(" ")))
nums = (drink[0], snack[0], token[0])
rival_nums = (drink[1:], snack[1:], token[1:])

cost = int(input("请输入进货总成本："))
income = 0

print("现在开始售卖阶段。")

print("首先是饮品。")
info = ()
while True:
    print(clues, nums, rival_nums, info, 0)
    ret = sell_stage(clues, nums, rival_nums, info, 0)
    print("当前期望收益为：", ret[0] - cost + income)
    if isinstance(ret[1], int):
        print("***** 请进行一次消息打探。")
        print("请问打探到了哪个商家的信息？")
        rival = int(input("（1: 非时钟，2: 时钟）"))
        price = int(input("请问他们的售价是？"))
        price_idx = list(sell_drink).index(price)
        if info == ():
            info = (None, None)
        info = list(info)
        info[rival - 1] = price_idx
        info = tuple(info)
        clues -= 1
    else:
        print("饮品售卖策略已确定：")
        print("***** 请设定价格为：", sell_drink[ret[1][0]])
        break
income += int(input("请输入饮品售卖收益："))


print("其次是餐品。")
info = ()
while True:
    ret = sell_stage(clues, nums, rival_nums, info, 1)
    print("当前期望收益为：", ret[0] - cost + income)
    if isinstance(ret[1], int):
        print("***** 请进行一次消息打探。")
        print("请问打探到了哪个商家的信息？")
        rival = int(input("（1: 非时钟，2: 时钟）"))
        price = int(input("请问他们的售价是？"))
        price_idx = list(sell_snack).index(price)
        if info == ():
            info = (None, None)
        info = list(info)
        info[rival - 1] = price_idx
        info = tuple(info)
        clues -= 1
    else:
        print("餐点售卖策略已确定：")
        print("***** 请设定价格为：", sell_snack[ret[1][0]])
        break
income += int(input("请输入餐点售卖收益："))


print("最后是纪念品。")
info = ()
while True:
    ret = sell_stage(clues, nums, rival_nums, info, 2)
    print("当前期望收益为：", ret[0] - cost + income)
    if isinstance(ret[1], int):
        print("***** 请进行一次消息打探。")
        price = int(input("请问他们的售价是？"))
        price_idx = list(sell_token).index(price)
        info = (price_idx,)
        clues -= 1
    else:
        print("纪念品售卖策略已确定：")
        print("***** 请设定价格为：", sell_token[ret[1][0]])
        break
income += int(input("请输入纪念品售卖收益："))

print("结束了！")
print("最终收益为：", income - cost)
