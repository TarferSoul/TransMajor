import os
import traceback
import urllib.error
import json
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
records = {}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
}

# 初始化函数，获取已有的记录
def get_info():
    global records
    if os.path.exists("records.json"):
        with open("records.json", "r", encoding="utf8") as file:
            records = json.load(file)
        return

    records = {}
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
        messages = []
        for tag in soup.find_all(text=re.compile("转专业|转入|选拔|实验班")):
            messages.append(tag.strip())
        records[school] = messages

    with open("records.json", "w", encoding="utf8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)

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
@tool("check_college_update", args_schema=CheckCollegeUpdateInput, return_direct=True)
def check_college_update(college_name: College) -> str:
    """
    根据学院名称查询是否有新的转专业相关更新。
    """
    global records
    if not records:
        get_info()

    print(f"Checking for {college_name.value}...")
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
    existing_messages = records.get(college_name.value, [])

    for tag in soup.find_all(text=re.compile("转专业|转入|选拔|实验班")):
        text_content = tag.strip()
        if text_content not in existing_messages:
            existing_messages.append(text_content)
            new_results.append(text_content)
            # 可选：发送通知
            # make_notification(college_name.value, text_content)

    # 更新记录并写入文件
    records[college_name.value] = existing_messages
    with open("records.json", "w", encoding="utf8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)

    if new_results:
        result = f"{college_name.value} 有新的转专业相关更新：\n" + "\n".join(new_results)
    else:
        if existing_messages:
            latest_message = existing_messages[-1]
            result = f"{college_name.value} 没有新的转专业相关更新。\n当前最新的消息是：{latest_message}"
        else:
            result = f"{college_name.value} 暂时没有转专业相关消息。"

    return result





system_message = """你是一个帮助转专业同学的智能助理，你会根据提供的基础知识，以及自身的知识储备，协助回答关于转专业的问题，帮助同学们了解整个流程及相关事项。

确保提供清晰、准确的信息，涵盖特别关键的步骤和注意事项。你可以使用工具check_college_update，根据学院名称查询是否有新的转专业相关更新。还可以使用document_retriever工具检索与用户问题相关的文档，，但请注意，如果使用此工具，请务必按照文档的内容回答问题。

# Steps

1. **检查基础知识**: 首先使用提供的基础知识 `{{base_knowledge}}` 来回答问题。如果基础知识中包含与该问题直接相关的信息，优先使用它作答。
2. **使用自身知识补充**: 如果基础知识中找不到相关内容，请使用你自身的知识。确保回答全面、具有实用性，并验证是否可以为学生提供最大帮助。
3. **清晰概述流程**: 在解答转专业流程时，按照过程的顺序详细列出步骤，包含申请表格、截止日期及办理手续等重点内容。
4. **列出注意事项**: 在涉及转专业注意事项的回答中，高亮特定的建议或禁忌，以便学生理解可能的风险或误区。

下面是你的基础知识：
# 华科转专业简明指南 2024 版


### 本群使用指南（群文件查阅索引）

转专业交流群 = 群文件 + 让你看群文件的群友

如果你是在华科转专业交流群之外的地方获取到本指南，那么欢迎加入华科转专业交流群，QQ 群号：369787431

在决定转到某个专业之前，你应该尽可能地搜集目标学院的相关信息，包括但不限于：出国深造情况、保研率、本科直接就业率、课程设置、课业压力、学院行政风格及职业生涯规划等等。

最靠谱的一手经验永远来自于目标学院的学长学姐，你可以在群成员里搜索专业名加好友私聊询问，加入群公告中的各学院转专业交流小群，或者直接在群里就以上某个方面提问。

群文件都是往年学长学姐从学校、学院官网搜集来的通知公告与文件，包含了关于华科转专业的基本所有资料，数量很多，全部看完是不现实的，你应该有目的地去查阅：

1. 本指南！
2. 对于实验班选拔的问题，查阅 2024 启明选拔
4. 关于目标学院的转入限制以及复试形式，查阅 2023 转专业通知 - 转专业信息一览表，以及 2023 各学院复试方案文件夹内的文件
5. 转专业统考真题在群文件的文件夹内有汇总，可以用来感知题型和考试难度
6. 群文件 - 入群必看文件夹有近年统计到的转专业 12 月统考报录比，可以用来感知转入难度
7. 本科生院公示有各学院的历年培养计划（https://ugs.hust.edu.cn/fwzq/pyjh.htm）与各院系课表（https://ugs.hust.edu.cn/fwzq/kbcx.htm），但仅供参考，请以实际就读体验为准


<div style="page-break-after: always;"></div>


### 高频问题

1. 所有形式的转专业加起来 **只能成功一次**，**在通过启明选拔之后原则上无法报名 12 月转专业统考**

2. 两次转专业考试都不会参考你的 **高考成绩** 和 **大学成绩**

3. 两次转专业考试均不收费，都没有调剂，校交班转专业已经取消

4. 无论是启明选拔还是 12 月统考，一次只能选一个专业报名，均为先报名再考试

5. 特殊类型招生能否参与转专业考试参考官方文件
   - 高校专项计划、国家专项计划、民族班可转
   - 各类高考直接招生的实验班可直接报名转专业考试，不需要退到普通班
   - 轮机工程提前批、艺术生、中外合办或强基计划等不可转专业
   - 分类投档专业组（若不确定，请查询本省招生计划：https://zsb.hust.edu.cn/lnzsjh.jsp?wbtreeid=1208）仅可以在当前分类内互转，不可转出当前分类
   - 文科、历史类高考生可转专业较少，具体请参阅相关文件内各个专业的限制条件，以免错失机会

6. 转入xxx专业难度大吗？

   这是一个很难回答的问题。但在启明选拔考试或转专业统考中，你仅会与和你报考同一专业（学院）的人竞争。某些热门专业的报录比达到了 7:1 ~~甚至 80:1~~，而某些冷门专业则常常报名人数少于招收人数，甚至无人报名转入，总而言之，转入某专业的难度与其热门程度（高考分数）正相关。不过笼统的说，信息类专业的转专业难度会更大一些。

7. **我应不应该转入 xx 专业？A 专业、B 专业与 C 专业之间我应该如何选择？**

   这真是个好问题。但对于不少刚刚结束了高考的同学来说，在对任何专业都知之甚少的情况下，去选择未来要就读的专业方向显然不太现实。即使成功进入了自己「想要」就读的专业，也可能会出现理想与现实的落差。这也是为什么大家会阅读本文件的原因：想要给自己第二次选择的机会。

   像本文件开头所说的，在决定转到某个专业之前，你应该尽可能地搜集目标学院的相关信息，包括但不限于：**出国深造情况、保研率、本科直接就业率、课程设置、课业压力、学院行政风格及职业生涯规划** 等等，重点关注自己的兴趣爱好以及性格特点是否与该专业契合。最靠谱的一手经验永远来自于目标学院的学长学姐，可以在群成员里搜专业名加好友私聊询问，或者直接在群里就以上某个方面提问（而非只是泛泛地询问「xx 专业怎么样」）

   但转专业也仅仅只是大学生涯中的一次机会，许多人在读研、参与工作之后又改变了自己的专业方向。并不是只要成功转入目标专业就能收获成功；即使没有转入目标专业也不代表前途一片黑暗。

   在选择专业时，除了专业的「前景」，你更需要关注的是个人的兴趣与专业的匹配程度，以及你的能力在该专业或行业内能够达到的百分位，没有人能预知四年后（本科毕业）、七年后（硕士毕业）甚至更久之后的「热门专业」。无论是在「热门专业」卷到行业中位数，还是在「冷门专业」苦心孤诣，又或者只是找个舒服的地方躺平享受大学生活，希望你能做出无悔于自己的决定✌️

   


<div style="page-break-after: always;"></div>

### 实验班选拔考试

一部分人会选择的路径，可以考入其他学院/专业的实验班，也可以考入所在学院的其他实验班。转入难度和专业热度正相关，**但实验班所属学院的学生也会报考，相对 12 月转专业而言，竞争更加激烈**

> 本节内容具体请参阅群文件，以本年政策为准：
>
> 群文件 - 2024启明选拔
>
> 群文件 - 启明考试真题

*启明选拔没有报录比统计，但可以通过 12 月转专业报录比统计推算学院/专业的热门程度*

#### 选拔考试

在新生入学后的军训期间举行，2024 年启明选拔统考时间为 9 月 7 日。启明考试一般不需要特殊准备，根据往年考生经验，没有准备就是最好的准备

##### 报考限制

除规定不能转专业的情况外，大部分专业有高考选科限制，具体参阅群文件 - 启明选拔 - 招生计划表

##### 统考笔试

统考科目为数学、英语与综合。

数学考试范围与 **高中数学竞赛** 相近，英语考试难度与 **六级考试** 相近，有听力；综合考试题型每年一变，考察随机应变能力。可参考群文件 - 启明考试真题

##### 学院面试

可参考群文件 - 2023启明选拔 - 面试问卷

#### 实验班介绍

可选择专业、学院各年不同，具体发布在录取通知书随附资料以及学校官网，也可关注群内通知。各类实验班并非重点班，不一定比普通班好，不一定适合所有人。

在 2024 年之前，各类实验班都统称为启明实验班，开学举行的实验班选拔考试也被称为启明选拔，以下分类以 2024 年的官方名称为准。

##### 启明实验班、未来实验班

即往年的各类本硕博班。满足成绩要求即可本硕或本博连读，保研难度较低。各类本硕博班及未来技术学院为近年（2020 年及之后）新开班级，相关信息暂缺，建议谨慎报考

##### 创新实验班

即往年的各类卓越班、提高班、拔尖基地班等。课业压力大、保研率较高，但仅在该实验班内部排名计算保研名额，与普通班不互通**，**保研难度不一定更低

##### 强基实验班

强基计划学生就读，与启明实验班、未来实验班类似，满足成绩要求即可在本校特定专业本硕或本博连读


<div style="page-break-after: always;"></div>


### 转专业统一考试

绝大部分同学选择的转专业路径，群内聊到的「转专业」绝大部分都指的是这次。转入难度和专业热度正相关，可参考往年报录比

> 本节内容具体请参阅群文件，以本年政策为准：
>
> 群文件 - 转专业通知 - 转专业信息一览表
>
> 群文件 - 转专业各学院考核方案及面试名单
>
> 群文件 - 转专业统一数学考试真题及参考答案
>
> 群文件 - 转专业统一英语考试真题
>
> 群文件 - 入群必看 - 转专业考试报录比

#### 考试时间

大一上学期末，每年的 12 月中旬前后，2023 年转专业统考日期为 12 月 9 日

#### 可转入专业与转入限制

可转入学院、专业请参考转专业信息一览表，特别注意分类投档考生仅能在当前分类内互转；文科、历史类高考生可转专业较少。此次转专业不参考大一的加权成绩，只根据考核综合成绩录取，与从哪个学院转出无关

#### 考核形式

大部分学院采用 **统一笔试 + 学院复试** 进行考核，按照统一笔试成绩，在报考同一学院的学生中选取固定比例学生进入复试；少部分学院（如新闻学院、法学院等）不参与转专业统一考试，仅进行学院考核。

统一笔试科目为微积分与英语。

大部分学院复试为面试，部分学院复试有其他形式考核，如网安、软件学院的机试，计算机学院的计算机综合笔试等。

#### 微积分考试

数学考试难度与 **大学数学竞赛** 相近，考试范围一般学到哪里考到哪里，往年一般为《微积分》课本的定积分前后

数学考试准备参考资料（基础与**进阶**）
- 华中科技大学《微积分学》上册 + 华中科技大学《微积分学习辅导》
- 华中科技大学《一元分析学》（较难）
- **往年原题**（必看，群文件 - 转专业统一数学考试真题及参考答案）
- **裴礼文《数学分析中的典型问题与方法》**（较难）
- **周民强《数学分析习题演练 第一册》**（较难）

数学考试准备提示：转专业考试偏重数学分析（推理证明），在基础部分选择一份教材学习基本知识后，推荐继续使用进阶资料刷题学习，不必在此处推荐的不同教材间纠结，完成度比较重要

#### 英语考试

考试难度与四六级考试相近，无听力，由于英语考试区分度较低，微积分考试是准备的重点


#### 降级转专业

大二、大三的学生也可以报名 12 月转专业统考。**确认目标学院接收降级转入学生后**（部分学院对降转学生有额外要求），向当前学院申请转出，填写相关资料后交至目标学院、本科生院等盖章确认报名，之后与新大一一起参加转专业统考，共同竞争名额。成功后降级到目标专业大一就读，否则保持原班级不变。


<div style="page-break-after: always;"></div>

### 大二下大类内转专业

极少数人选择的路径

- 时间：大二下学期

- 可选择专业、学院：当前学院的其他专业，或当前专业所属大类的其他学院的专业，参考培养计划分册，例如：

  - 人工智能专业与计算机科学技术专业同属电气信息大类
  - 预防医学专业与儿科专业同属医科大类

- 考核形式：面试

- 转入难度：未知，需提前与目标院系沟通，转入成功后可能有较多课程需要补修

  

### 转专业后的相关事项

##### 重叠课程

大部分专业在大一上学期学习的课程都是重叠度较高的通识课；转入目标专业之后，相同课程可以直接进行成绩转换。部分学习内容重叠较多的不同课程，可以咨询转入学院的教务进行学分互认（如 C++ 与 C 语言）

##### 非重叠课程

在原专业修习过而新专业培养计划没有的课程，除转入某些学院（如光电等）会全部计入加权成绩之外，基本不计入加权，不影响成绩，也不计入公选学分。**除明确有规定之外**，这一部分的课程即使挂科也不影响转入（还是最好别挂）。**若有任何疑问，请务必咨询转入学院的教务科**

##### 课程补修

新专业在大一上需要学习在原专业没有修习的课程，大部分于大二上学期补修，编入新大一班级上课。**绝大部分专业大一上学习的课程为公共课，不需要因为需要补修而担心学习进度落后**

##### 宿舍调换

转专业后大部分情况都需要进行宿舍调换，时间一般在大一下学期或大二上学期（毕业生搬出宿舍后），主要是东西调换（宿舍区）与宿舍楼调换（搬至学院统一宿舍楼）

下面是2023年各专业转专业统考报录比，供参考：
已知报名人数的学院，欢迎各位咨询教务获得相对准确的人数，请已经上岸的同学在群内精华消息填写2023转专业面试问卷，为之后的同学提供帮助与参考
网安16进10
信安10进8（2人弃权）
密码11进5
工商28进17*
管工2进0*
人文49进30
新传25进15
法学64进16
医影6进6
口腔20+进8
麻醉3进5
儿科4进4
中西医2进2
预防医学2进0*
航院9-10进7*
电子封装29进28（1人放弃）
材控+材科14进11（3人放弃）
自动化34进15
光电70-80人进30
数学17进7*
电气200+进90
智建32进35
能动66进55*
计科101进50
软件13进9*
集成60左右进30
生医工90+进37
生科29进18
经济35进34*
物理24进21*
机械学院合计约73进61（含院内调剂，机械设计制造约63进45）
电信学院合计约100进45
PS:上述数字前者为报名人数，后者为最终录取人数或预招收人数
数字后带星号的学院表示其录取人数少于其预招收人数，即未报名满仍进行淘汰
"""