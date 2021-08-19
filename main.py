import json
import os
import re

p = {}  # players玩家字典数据

# if not os.path.isfile("playersINFO.json"):
path = os.getcwd() + "\\logs\\"  # 程序下的绝对路径
logs = os.listdir(path)  # 文件名列表
print("正在分析日志记录，这可能需要一点时间。")
for log in logs:  # 遍历每一个日志文件
    print(f"正在分析{log}...")
    with open(path + log) as f:
        for line in f:  # 遍历每一行内容

            if "was kicked" in line and ">>" not in line:  # 加快计算速度
                continue
            if "Villager" in line and ">>" not in line:  # 勿删除该行 Villager死亡可能会被误判为玩家死亡
                continue
            if "[Server thread/WARN]" in line and ">>" not in line:  # 加快计算速度
                continue
            if "[Server thread/ERROR]" in line and ">>" not in line:  # 加快计算速度
                continue
            # 以上内容跳过分析

            matchIn = re.search(r"\[(.+)\] \[Server.+\]: (.+)\[.+\] logged in", line)  # 正则匹配登入信息
            if matchIn:  # 匹配登入记录
                time, name = matchIn.groups()  # 将匹配到的信息分组
                dIn = log[:-6] + " " + time  # 登入时的日期，示例格式：2021-07-15-1 16:51
                if name not in p:  # 如果字典中不存在该玩家，即初次匹配到登入
                    p[name] = {}  # 初始化该玩家数据
                    p[name]["registration_time"] = dIn  # 写入注册时间
                    p[name]["last_logIn"] = dIn  # 写入最后一次登入时间
                    p[name]["online_time"] = 0  # 写入累计在线时长
                    p[name]["deaths"] = 0  # 写入累计死亡数
                    p[name]["chat_messages"] = 0  # 写入累计聊天条数
                else:
                    p[name]["last_logIn"] = dIn  # 覆写最后一次登入时间

            matchOut = re.search(r"\[(.+)\] \[Server.+\]: ([^/]+) lost connection", line)  # 正则匹配登出信息
            if matchOut:
                time, name = matchOut.groups()  # 将匹配到的信息分组
                dOut = log[:-6] + " " + time  # 登出时的日期，示例格式：2021-07-15 16:51:22
                p[name]["last_logOut"] = dOut  # 写入最后一次登出时间
                dIn = p[name]["last_logIn"]
                if dIn[:10] == dOut[:10]:  # 登入登出在同一天时
                    t = (int(dOut[-8:-6]) - int(dIn[-8:-6])) * 60 + int(dOut[-5:-3]) - int(dIn[-5:-3])
                else:  # 登入登出不在同一天时 (跨多天按一天算，我不管w)
                    t = 1440 - (abs(int(dIn[-8:-6]) - int(dOut[-8:-6]))) * 60 - abs(int(dOut[-8:-6]) - int(dIn[-5:-3]))
                p[name]["online_time"] += t  # 累加在线时长

            for i in ["was", "tried", "fell", "burnt", "drowned", "walked", "blew", "hit ", "caught", "suffocated"]:
                if i in line and "[Server thread/INFO]" in line and ">>" not in line:  # 统计玩家死亡次数
                    for player in p.keys():
                        if player in line:
                            p[player]["deaths"] += 1
                            break

            for player in p.keys():  # 统计玩家聊天消息数量
                if f"{player} >>" in line:
                    p[player]["chat_messages"] += 1
                    break

with open("playersINFO.json", "w") as pf:  # 导出.json信息
    json.dump(p, pf, sort_keys=True, indent=4)
with open("玩家数据分析结果.txt", "w") as pf_final:  # 导出格式化信息
    str_bg = "玩家名称\t在线时长(分)\t聊天消息数\t死亡次数\t注册时间\t最后一次上线时间"
    print(str_bg)
    pf_final.write(str_bg + "\n")
    for player, i in p.items():
        str_data = player + "\t" + str(i["online_time"]) + "\t" + str(i["chat_messages"]) + "\t"
        str_data += str(i["deaths"]) + "\t" + i["registration_time"] + "\t" + i["last_logIn"]
        print(str_data)
        pf_final.write(str_data + "\n")
print("\n程序作者：b站小泠君")
os.system("pause")
