import os
import traceback
import urllib.error
from urllib import request

import threading
import platform
import re

# https://github.com/ms7m/notify-py
from notifypy import Notify
from bs4 import BeautifulSoup

Count = 0
schoolUrlDictionary = {
    "软件学院": "https://sse.hust.edu.cn/bksjy1/tzgg.htm",
    "法医学系": "http://fayixi.tjmu.edu.cn/rcpy1/bksjy/jxdt.htm",
    "口腔医学院公示": "https://stomatology.hust.edu.cn/xwzx/gsl.htm",
    "口腔医学院通知": "https://stomatology.hust.edu.cn/jyjx/bksjy.htm",
    "网络安全学院": "https://cse.hust.edu.cn/bksjy/tzgg.htm",
    "计算机学院": "http://www.cs.hust.edu.cn/sylm/tzgg/bk.htm",
    "机械学院": "https://mse.hust.edu.cn/rcpy/bksjy/zxdt.htm",
    "光电学院": "https://oei.hust.edu.cn/bkjx/zxtz.htm",
    "第二临床学院": "https://www.tjh.com.cn/channels/290.html",
    "经济学院": "https://eco.hust.edu.cn/rcpy/bksjy/bksjwxx.htm",
    "电气学院": "https://seee.hust.edu.cn/xwzx/tzgg.htm",
    "电信学院": "https://ei.hust.edu.cn/bkjy/tzgg.htm",
    "外国语学院": "https://sfl.hust.edu.cn/bksjy/tzgg.htm",
    "数学学院": "https://maths.hust.edu.cn/bksjy/tzgg1.htm",
    "自动化学院": "https://aia.hust.edu.cn/tzgg/bks.htm",
    "新闻与传播学院": "https://sjic.hust.edu.cn/xwzx/tzgg.htm",
    "物理学院": "https://phys.hust.edu.cn/list_4.jsp?urltype=tree.TreeTempUrl&wbtreeid=1069",
    "管理学院": "https://cm.hust.edu.cn/old/bk/jwgg.htm",
    "社会学院": "https://soci.hust.edu.cn/bksjy/tzgg.htm",
    "土木学院": "https://civil.hust.edu.cn/rcpy1/bkspy/tzgg.htm",
    "公共管理学院": "https://cpa.hust.edu.cn/zsjx/bks/jwxx.htm",
    "生命学院": "https://life.hust.edu.cn/tzgg/bksjy.htm",
    "建规学院": "https://aup.hust.edu.cn/index/jwxx.htm",
    "航空航天学院": "https://ae.hust.edu.cn/index/xygg.htm",
    "材料学院": "https://mat.hust.edu.cn/rcpy/bkspy/tzgg.htm",
    "化学学院": "https://chem.hust.edu.cn/bksjy/tzgg.htm",
    "能动学院": "https://energy.hust.edu.cn/bksjy1/zxtz.htm",
    "哲学学院": "https://phil.hust.edu.cn/tzgg/tzgg.htm",
    "药学院": "http://pharm.tjmu.edu.cn/index/tzgg.htm",
    "法学院": "https://law.hust.edu.cn/index.htm",
    "公共卫生学院": "http://gwxy.tjmu.edu.cn/xydong_t/tzgg1/jx.htm",
    "第一临床学院": "https://jxpt.whuh.com/pc/PortalView/moreNotice",
    "集成电路学院": "https://ic.hust.edu.cn/bksjy/zxtz.htm",
    # "教务处": "https://jwc.hust.edu.cn/index.htm",
    # "人文学院": "https://humanity.hust.edu.cn/tzgg.htm",
}

text_list = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'}


def check_info():
    for school in schoolUrlDictionary.keys():
        myURL = schoolUrlDictionary[school]
        try:
            req = urllib.request.Request(url=myURL, headers=headers)
            response = urllib.request.urlopen(req).read()
        except:
            print("打开{}网页失败，请手动进行检查".format(school))
            print(traceback.format_exc())
            break
        data = response.decode('utf-8')
        soup = BeautifulSoup(data, "html.parser")
        for tag in soup.find_all(text=re.compile("转专业|转入|选拔|实验班")):
            if tag.text not in text_list:
                text_list.append(tag.text)
                file = open(file="records.txt", encoding="utf8", mode="a")
                file.write(tag.text)
                file.write("\n")
                file.close()
                print(tag.text)
                print(school + " 有新结果")
                make_notification(school, tag.text)
    global Count
    Count += 1
    print("check for " + Count.__str__() + " times")
    timer = threading.Timer(300, check_info)
    timer.start()


def get_info():
    global text_list
    if os.path.exists("records.txt"):
        file = open(file="records.txt", encoding="utf8", mode="r")
        text_list = file.read().splitlines()
        for text in text_list:
            print(text)
        file.close()
        return
    file = open(file="records.txt", encoding="utf8", mode="w")
    for school in schoolUrlDictionary.keys():
        myURL = schoolUrlDictionary[school]
        try:
            req = urllib.request.Request(url=myURL, headers=headers)
            response = urllib.request.urlopen(req).read()
        except:
            print("打开{}网页失败，请手动进行检查".format(school))
            print(traceback.format_exc())
            break
        data = response.decode('utf-8')
        soup = BeautifulSoup(data, "html.parser")
        for tag in soup.find_all(text=re.compile("转专业|转入|选拔|实验班")):
            text_list.append(tag.text)
    for text in text_list:
        file.write(text)
        file.write("\n")
        print(text)
    print("total: " + len(text_list).__str__() + " records")
    file.close()


def make_notification(school_name, tag_name):
    notification_title = school_name + "转专业消息有新结果"
    notification = Notify()
    notification.title = notification_title
    notification.message = tag_name
    notification.send()


if __name__ == '__main__':
    get_info()
    check_info()



import os
import traceback
import urllib.error
from urllib import request
import re
from notifypy import Notify
from bs4 import BeautifulSoup
from enum import Enum
from langchain.agents import tool
from pydantic import BaseModel, Field
# 定义学院枚举
class College(Enum):
    # 教务处 = "教务处"
    软件学院 = "软件学院"
    法医学系 = "法医学系"
    口腔医学院公示 = "口腔医学院公示"
    口腔医学院通知 = "口腔医学院通知"
    网络安全学院 = "网络安全学院"
    计算机学院 = "计算机学院"
    机械学院 = "机械学院"
    光电学院 = "光电学院"
    第二临床学院 = "第二临床学院"
    # 人文学院 = "人文学院"
    经济学院 = "经济学院"
    电气学院 = "电气学院"
    电信学院 = "电信学院"
    外国语学院 = "外国语学院"
    数学学院 = "数学学院"
    自动化学院 = "自动化学院"
    新闻与传播学院 = "新闻与传播学院"
    物理学院 = "物理学院"
    管理学院 = "管理学院"
    社会学院 = "社会学院"
    土木学院 = "土木学院"
    公共管理学院 = "公共管理学院"
    生命学院 = "生命学院"
    建规学院 = "建规学院"
    航空航天学院 = "航空航天学院"
    材料学院 = "材料学院"
    化学学院 = "化学学院"
    能动学院 = "能动学院"
    哲学学院 = "哲学学院"
    药学院 = "药学院"
    法学院 = "法学院"
    公共卫生学院 = "公共卫生学院"
    第一临床学院 = "第一临床学院"
    集成电路学院 = "集成电路学院"
# 学院对应的URL字典
schoolUrlDictionary = {
    # "教务处": "https://jwc.hust.edu.cn/index.htm",
    "软件学院": "https://sse.hust.edu.cn/bksjy1/tzgg.htm",
    "法医学系": "http://fayixi.tjmu.edu.cn/rcpy1/bksjy/jxdt.htm",
    "口腔医学院公示": "https://stomatology.hust.edu.cn/xwzx/gsl.htm",
    "口腔医学院通知": "https://stomatology.hust.edu.cn/jyjx/bksjy.htm",
    "网络安全学院": "https://cse.hust.edu.cn/bksjy/tzgg.htm",
    "计算机学院": "http://www.cs.hust.edu.cn/sylm/tzgg/bk.htm",
    "机械学院": "https://mse.hust.edu.cn/rcpy/bksjy/zxdt.htm",
    "光电学院": "https://oei.hust.edu.cn/bkjx/zxtz.htm",
    "第二临床学院": "https://www.tjh.com.cn/channels/290.html",
    # "人文学院": "https://humanity.hust.edu.cn/tzgg.htm",
    "经济学院": "https://eco.hust.edu.cn/rcpy/bksjy/bksjwxx.htm",
    "电气学院": "https://seee.hust.edu.cn/xwzx/tzgg.htm",
    "电信学院": "https://ei.hust.edu.cn/bkjy/tzgg.htm",
    "外国语学院": "https://sfl.hust.edu.cn/bksjy/tzgg.htm",
    "数学学院": "https://maths.hust.edu.cn/bksjy/tzgg1.htm",
    "自动化学院": "https://aia.hust.edu.cn/tzgg/bks.htm",
    "新闻与传播学院": "https://sjic.hust.edu.cn/xwzx/tzgg.htm",
    "物理学院": "https://phys.hust.edu.cn/list_4.jsp?urltype=tree.TreeTempUrl&wbtreeid=1069",
    "管理学院": "https://cm.hust.edu.cn/old/bk/jwgg.htm",
    "社会学院": "https://soci.hust.edu.cn/bksjy/tzgg.htm",
    "土木学院": "https://civil.hust.edu.cn/rcpy1/bkspy/tzgg.htm",
    "公共管理学院": "https://cpa.hust.edu.cn/zsjx/bks/jwxx.htm",
    "生命学院": "https://life.hust.edu.cn/tzgg/bksjy.htm",
    "建规学院": "https://aup.hust.edu.cn/index/jwxx.htm",
    "航空航天学院": "https://ae.hust.edu.cn/index/xygg.htm",
    "材料学院": "https://mat.hust.edu.cn/rcpy/bkspy/tzgg.htm",
    "化学学院": "https://chem.hust.edu.cn/bksjy/tzgg.htm",
    "能动学院": "https://energy.hust.edu.cn/bksjy1/zxtz.htm",
    "哲学学院": "https://phil.hust.edu.cn/tzgg/tzgg.htm",
    "药学院": "http://pharm.tjmu.edu.cn/index/tzgg.htm",
    "法学院": "https://law.hust.edu.cn/index.htm",
    "公共卫生学院": "http://gwxy.tjmu.edu.cn/xydong_t/tzgg1/jx.htm",
    "第一临床学院": "https://jxpt.whuh.com/pc/PortalView/moreNotice",
    "集成电路学院": "https://ic.hust.edu.cn/bksjy/zxtz.htm",
    # ...（继续添加其他学院及其URL）
}

# 全局变量
text_list = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
}

# 初始化函数，获取已有的记录
def get_info():
    global text_list
    if os.path.exists("records.txt"):
        with open("records.txt", "r", encoding="utf8") as file:
            text_list = file.read().splitlines()
        return

    for school in schoolUrlDictionary.keys():
        myURL = schoolUrlDictionary[school]
        try:
            req = urllib.request.Request(url=myURL, headers=headers)
            response = urllib.request.urlopen(req).read()
        except:
            print(f"打开 {school} 网页失败，请手动进行检查。")
            print(traceback.format_exc())
            continue
        data = response.decode('utf-8')
        soup = BeautifulSoup(data, "html.parser")
        for tag in soup.find_all(text=re.compile("转专业|转入|选拔|实验班")):
            text_list.append(tag)

    with open("records.txt", "w", encoding="utf8") as file:
        for text in text_list:
            file.write(text + "\n")

# 可选的通知功能
def make_notification(school_name, tag_name):
    notification_title = f"{school_name} 转专业消息有新结果"
    notification = Notify()
    notification.title = notification_title
    notification.message = tag_name
    notification.send()

class CheckCollegeUpdateInput(BaseModel):
    college_name: College = Field(..., title="学院名称", description="需要查询的学院名称")
# 使用 @tool 装饰器定义工具

@tool("check_college_update",args_schema=CheckCollegeUpdateInput, return_direct=True)
def check_college_update(college_name: College) -> str:
    """
    根据学院名称查询是否有新的转专业相关更新。
    """
    print(college_name)
    # global text_list
    # print(type(text_list))
    if text_list == []:
        get_info()
    # print(text_list)
    print(f"Checking for {college_name}...")
    if college_name.value not in schoolUrlDictionary:
        return f"学院 {college_name.value} 不存在，请输入有效的学院名称。"

    myURL = schoolUrlDictionary[college_name.value]
    try:
        req = urllib.request.Request(url=myURL, headers=headers)
        response = urllib.request.urlopen(req).read()
    except Exception as e:
        return f"打开 {college_name.value} 网页失败，请手动进行检查。\n错误信息: {e}"

    data = response.decode('utf-8')
    soup = BeautifulSoup(data, "html.parser")
    new_results = []

    for tag in soup.find_all(text=re.compile("转专业|转入|选拔|实验班")):
        text_content = tag.strip()
        if text_content not in text_list:
            text_list.append(text_content)
            with open("records.txt", "a", encoding="utf8") as file:
                file.write(text_content + "\n")
            new_results.append(text_content)
            # 可选：发送通知
            # make_notification(college_name.value, text_content)

    if new_results:
        result = f"{college_name.value} 有新的转专业相关更新：\n" + "\n".join(new_results)
    else:
        result = f"{college_name.value} 没有新的转专业相关更新。"

    return result


