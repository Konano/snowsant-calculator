class Colors:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


good_stage = int(input("[*] 今日的经营商品是哪个阶段的商品？(1-4) "))

if good_stage == 1:
    buy_drink = [20, 28, 38]
    buy_snack = [10, 20, 32]
    buy_token = [50, 100, 200]
    sell_base_drink = 50
    sell_base_snack = 40
    sell_base_token = 1000

elif good_stage == 2:
    buy_drink = [30, 42, 57]
    buy_snack = [15, 30, 48]
    buy_token = [50, 100, 200]
    sell_base_drink = 100
    sell_base_snack = 80
    sell_base_token = 1000

elif good_stage == 3:
    print(Colors.RED + "[!] 该商品种类的基础数据还未添加。" + Colors.RESET)
    exit()

elif good_stage == 4:
    print(Colors.RED + "[!] 该商品种类的基础数据还未添加。" + Colors.RESET)
    exit()

customer_drink = int(input("[*] 今日的饮品爱好者有多少？"))
customer_snack = int(input("[*] 今日的餐点爱好者有多少？"))
customer_token = int(input("[*] 今日的纪念品爱好者有多少？"))
customer = [customer_drink, customer_snack, customer_token]
buy_prices = [buy_drink, buy_snack, buy_token]
stock_drink = customer_drink
stock_snack = customer_snack
stock_token = customer_token

# aaa = (30, 30, 30)
# aab = (36, 36, 18)
# abb = (36, 27, 27)
# abc = (40, 30, 20)
# aa = (5, 5)
# ab = (6, 4)

sell_drink = list(range(sell_base_drink - 5, sell_base_drink + 6, 1))
sell_snack = list(range(sell_base_snack - 5, sell_base_snack + 6, 1))
sell_token = list(range(sell_base_token - 50, sell_base_token + 51, 10))
sell = [sell_drink, sell_snack, sell_token]

# ============================================================


from itertools import product


def average_with_weight(pairs):
    return sum([x[0] * x[-1] for x in pairs]) / sum([x[-1] for x in pairs])


# ============================================================


sell_result_cache = {}


def sell_result(bid, me) -> int:
    if (bid, me) in sell_result_cache:
        return sell_result_cache[(bid, me)]
    ranks = [sum([1 for y in bid if y < x]) for x in bid]
    sorted_ranks = sorted(ranks)
    if sorted_ranks == [0, 0, 0]:
        ret = 30
    elif sorted_ranks == [0, 0, 2]:
        ret = [36, None, 18][ranks[bid.index(me)]]
    elif sorted_ranks == [0, 1, 1]:
        ret = [36, 27][ranks[bid.index(me)]]
    elif sorted_ranks == [0, 1, 2]:
        ret = [40, 30, 20][ranks[bid.index(me)]]
    elif sorted_ranks == [0, 0]:
        ret = 5
    elif sorted_ranks == [0, 1]:
        ret = [6, 4][ranks[bid.index(me)]]
    else:
        raise NotImplementedError
    sell_result_cache[(bid, me)] = ret
    return ret


def sell_conflict_checker(statement, info) -> bool:
    if len(info) == 0:
        return True
    if len(info) == 1:
        return info == statement
    if len(info) == 2:
        if info == (None, None):
            return True
        elif None not in info:
            return info == statement
        elif info[0] == None:
            return info[1] == statement[1] and info[1] >= statement[0]
        elif info[1] == None:
            return info[0] == statement[0] and info[0] >= statement[1]
        else:
            raise NotImplementedError
    return False


sell_action_cache = {}


def sell_action(gid, num, rival_num, info):
    if (gid, num, rival_num, info) in sell_action_cache:
        return sell_action_cache[(gid, num, rival_num, info)]

    # print(num, rival_num, info, gid)
    statements = [
        statement
        for statement in product(range(11), repeat=[2, 2, 1][gid])
        if sell_conflict_checker(statement, info)
    ]

    best_income, best_choice = -1e9, None
    for c in range(11):
        incomes = []
        sameprice = None
        for statement in statements:
            customer_base = customer[gid] // [90, 90, 10][gid]
            customer_num = customer_base * sell_result(statement + (c,), c)
            income = min(customer_num, num) * sell[gid][c]
            income_rank = 0
            for _c, _n in zip(statement, rival_num):
                rival_customer_num = customer_base * sell_result(statement + (c,), _c)
                rival_income = min(rival_customer_num, _n) * sell[gid][_c]
                if rival_income > income:
                    income_rank += 1
            # print(c, statement + (c,), sell_result(statement + (c,), c), sell[gid][c], income, income_rank)
            if income_rank == 0:
                income += 5000
            elif income_rank == 1:
                income += 2000
            else:
                income += 1000
            incomes.append(income)
            if len(info) == 2 and None in info and statement[0] == statement[1]:
                sameprice = income
        # print(c, incomes, sameprice)
        if sameprice is not None:
            exp_income = (sum(incomes) - 0.5 * sameprice) / (len(incomes) - 0.5)
        else:
            exp_income = sum(incomes) / len(incomes)
        if exp_income > best_income:
            best_income, best_choice = exp_income, (c,)

    # print(gid, info, best_income, best_choice, statements)
    sell_action_cache[(gid, num, rival_num, info)] = (best_income, best_choice)
    return best_income, best_choice


sell_stage_cache = {}


def sell_stage(clues, gid, nums, rival_nums, info):
    if gid == 3:
        return 0, -1, None
    if (clues, gid, nums[gid:], rival_nums[gid:], info) in sell_stage_cache:
        return sell_stage_cache[(clues, gid, nums[gid:], rival_nums[gid:], info)]

    best_income, best_choice = sell_action(gid, nums[gid], rival_nums[gid], info)
    best_income += sell_stage(clues, gid + 1, nums, rival_nums, ())[0]

    if clues:
        if info == ():
            if gid != 2:
                pry_income = average_with_weight(
                    [
                        sell_stage(clues - 1, gid, nums, rival_nums, (i, None))
                        for i in range(11)
                    ]
                    + [
                        sell_stage(clues - 1, gid, nums, rival_nums, (None, i))
                        for i in range(11)
                    ]
                )
                if pry_income >= best_income:
                    best_income, best_choice = pry_income, -1
            else:
                pry_income = average_with_weight(
                    [
                        sell_stage(clues - 1, gid, nums, rival_nums, (i,))
                        for i in range(11)
                    ]
                )
                if pry_income >= best_income:
                    best_income, best_choice = pry_income, -1
        elif None in info:
            __idx = 1 - info.index(None)
            pry_income = average_with_weight(
                [
                    sell_stage(
                        clues - 1,
                        gid,
                        nums,
                        rival_nums,
                        (i, info[1]) if __idx == 1 else (info[0], i),
                    )
                    for i in range(info[__idx] + 1)
                ]
            )
            if pry_income > best_income:
                best_income, best_choice = pry_income, -1

    statements = [
        statement
        for statement in product(range(11), repeat=[2, 2, 1][gid])
        if sell_conflict_checker(statement, info)
    ]

    sell_stage_cache[(clues, gid, nums[gid:], rival_nums[gid:], info)] = (
        best_income,
        best_choice,
        len(statements),
    )
    return best_income, best_choice, len(statements)


# ============================================================


buy_result_cache = {}


def buy_result(bid, me):
    if (bid, me) in buy_result_cache:
        return buy_result_cache[(bid, me)]
    ranks = [sum([1 for y in bid if y > x]) for x in bid]
    sorted_ranks = sorted(ranks)
    if sorted_ranks == [0, 0, 0]:
        ret = 30
    elif sorted_ranks == [0, 0, 2]:
        ret = [36, None, 18][ranks[bid.index(me)]]
    elif sorted_ranks == [0, 1, 1]:
        ret = [36, 27][ranks[bid.index(me)]]
    elif sorted_ranks == [0, 1, 2]:
        ret = [40, 30, 20][ranks[bid.index(me)]]
    elif sorted_ranks == [0, 0]:
        ret = 5
    elif sorted_ranks == [0, 1]:
        ret = [6, 4][ranks[bid.index(me)]]
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


def buy_action(clues, infos):
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
            sell_income = sell_stage(clues, 0, nums, rival_nums, ())[0]
            incomes.append(sell_income - costs)
        exp_income = sum(incomes) / len(incomes)
        if exp_income > best_income:
            best_income, best_choice = exp_income, c
    return best_income, best_choice


buy_stage_cache = {}


def buy_stage(clues, infos):
    if (clues, infos) in buy_stage_cache:
        return buy_stage_cache[(clues, infos)]

    best_income, best_choice = buy_action(clues, infos)

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

import sys


def action_confirm():
    input("行动结束后按下回车键……")
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")


clues = int(input("[*] 请输入可打探的次数："))
infos = ((), (), ())
print("请稍等，正在计算……")
while True:
    ret = buy_stage(clues, infos)
    print(Colors.GREEN + f"[+] 当前期望收益为：{ret[0]}" + Colors.RESET)
    if isinstance(ret[1], int):
        print("[A] 请选择打探 %s 的信息（选择从上往下第一个未被打探过的商店）" % (["饮品", "餐点", "纪念品"][ret[1]]))
        action_confirm()
        choice = int(input("[*] 请问打探到的消息中，该商店的策略是？(1-3) "))
        infos = list(infos)
        infos[ret[1]] = infos[ret[1]] + (choice - 1,)
        infos = tuple(infos)
        clues -= 1
    else:
        strategy = [["保守", "稳健", "激进"][ret[1][i]] for i in range(3)]
        print("[A] 进货策略已确定：" + "，".join(strategy))
        action_confirm()
        break

print("[+] 请告知每种商品的进货情况，店与店之间用空格隔开。")
print("[+] 注意，商店的次序需要是特定的顺序（雪雉商店，其他商店，时钟商店）而不是进货数量排行榜的顺序。")

drink = tuple(map(int, input("[*] 饮品进货数量（三个数，中间用空格隔开）：").strip().split(" ")))
while sum(drink) != customer_drink:
    print(Colors.RED + "[!] 饮品进货总数量与顾客数量不符，请重新输入。" + Colors.RESET)
    drink = tuple(map(int, input("[*] 饮品进货数量（三个数，中间用空格隔开）：").strip().split(" ")))

snack = tuple(map(int, input("[*] 餐点进货数量（三个数，中间用空格隔开）：").strip().split(" ")))
while sum(snack) != customer_snack:
    print(Colors.RED + "[!] 餐点进货总数量与顾客数量不符，请重新输入。" + Colors.RESET)
    snack = tuple(map(int, input("[*] 餐点进货数量（三个数，中间用空格隔开）：").strip().split(" ")))

token = tuple(map(int, input("[*] 纪念品进货数量（两个数，中间用空格隔开）：").strip().split(" ")))
while sum(token) != customer_token:
    print(Colors.RED + "[!] 纪念品进货总数量与顾客数量不符，请重新输入。" + Colors.RESET)
    token = tuple(map(int, input("[*] 纪念品进货数量（两个数，中间用空格隔开）：").strip().split(" ")))

nums = (drink[0], snack[0], token[0])
rival_nums = (drink[1:], snack[1:], token[1:])

cost = sum([nums[i] * buy_prices[i][ret[1][i]] for i in range(3)])
income = 0

print("饮品售卖阶段。")
info = ()
while True:
    ret = sell_stage(clues, 0, nums, rival_nums, info)
    print(Colors.GREEN + f"[+] 当前期望收益为：{ret[0] - cost + income}" + Colors.RESET)
    if isinstance(ret[1], int):
        print("[A] 请进行一次消息打探。")
        action_confirm()
        rival = int(input("[*] 请问打探到了哪个商店的信息？(1-2) "))
        price = int(input("[*] 请问他们给出的售价是？"))
        price_idx = list(sell_drink).index(price)
        if info == ():
            info = (None, None)
        info = list(info)
        info[rival - 1] = price_idx
        info = tuple(info)
        clues -= 1
    else:
        print("[A] 饮品售卖策略已确定。请设定价格为：", sell_drink[ret[1][0]])
        action_confirm()
        break
income += int(input("[*] 请输入饮品售卖收益（包括激励奖励）："))


print("餐品售卖阶段。")
info = ()
while True:
    ret = sell_stage(clues, 1, nums, rival_nums, info)
    print(Colors.GREEN + f"[+] 当前期望收益为：{ret[0] - cost + income}" + Colors.RESET)
    if isinstance(ret[1], int):
        print("[A] 请进行一次消息打探。")
        action_confirm()
        rival = int(input("[*] 请问打探到了哪个商店的信息？(1-2) "))
        price = int(input("[*] 请问他们给出的售价是？"))
        price_idx = list(sell_snack).index(price)
        if info == ():
            info = (None, None)
        info = list(info)
        info[rival - 1] = price_idx
        info = tuple(info)
        clues -= 1
    else:
        print("[A] 餐品售卖策略已确定。请设定价格为：", sell_snack[ret[1][0]])
        action_confirm()
        break
income += int(input("[*] 请输入餐点售卖收益（包括激励奖励）："))


print("纪念品售卖阶段。不考虑库存的问题。")
info = ()
while True:
    ret = sell_stage(clues, 2, nums, rival_nums, info)
    print(Colors.GREEN + f"[+] 当前期望收益为：{ret[0] - cost + income}" + Colors.RESET)
    if isinstance(ret[1], int):
        print("[A] 请进行一次消息打探。")
        action_confirm()
        price = int(input("[*] 请问他们给出的售价是？"))
        price_idx = list(sell_token).index(price)
        info = (price_idx,)
        clues -= 1
    else:
        print("[A] 纪念品售卖策略已确定。请设定价格为：", sell_token[ret[1][0]])
        action_confirm()
        break
income += int(input("[*] 请输入纪念品售卖收益（包括激励奖励）："))

print(Colors.GREEN + f"[+] 实际收益为：{income - cost}" + Colors.RESET)
print("结束了！")
action_confirm()
