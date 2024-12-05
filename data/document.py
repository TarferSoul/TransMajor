import os
import json

# 文件夹列表
folders = [
    "/home/tarfersoul/TransMajor/data/download/★★入群必看！！",
    "/home/tarfersoul/TransMajor/data/download/2020各学院考核方案",
    "/home/tarfersoul/TransMajor/data/download/2020级启明选拔",
    "/home/tarfersoul/TransMajor/data/download/2020转专业通知",
    "/home/tarfersoul/TransMajor/data/download/2021各学院复试方案及复试名单",
    "/home/tarfersoul/TransMajor/data/download/2021启明选拔",
    "/home/tarfersoul/TransMajor/data/download/2021转专业通知",
    "/home/tarfersoul/TransMajor/data/download/2023启明选拔",
    "/home/tarfersoul/TransMajor/data/download/2024启明选拔",
    "/home/tarfersoul/TransMajor/data/download/2022级各专业培养计划",
    "/home/tarfersoul/TransMajor/data/download/2022转专业通知",
    "/home/tarfersoul/TransMajor/data/download/2022转专业考核方案及复试名单",
    "/home/tarfersoul/TransMajor/data/download/毕业生就业质量报告",
    "/home/tarfersoul/TransMajor/data/download/部分学院内部资料",
    "/home/tarfersoul/TransMajor/data/download/部分院系毕业生去向",
    "/home/tarfersoul/TransMajor/data/download/大类内转专业",
    "/home/tarfersoul/TransMajor/data/download/各学院推免保研相关资料",
    "/home/tarfersoul/TransMajor/data/download/各学院专业分流文件",
    "/home/tarfersoul/TransMajor/data/download/各学院专业分流相关文件+专业介绍",
    "/home/tarfersoul/TransMajor/data/download/入群必看补充包（历史文件）",
    "/home/tarfersoul/TransMajor/data/download/网安、软件机考",
    "/home/tarfersoul/TransMajor/data/download/转专业面试问卷",
    "/home/tarfersoul/TransMajor/data/download/转专业统一英语考试真题",
]

# 额外文件
extra_files = [
    "/home/tarfersoul/TransMajor/data/download/转专业-数学（时间匆忙 先写一点）.txt",
    "/home/tarfersoul/TransMajor/data/download/有关中德（2019版）必看.txt",
    "/home/tarfersoul/TransMajor/data/download/平时学习资料/MOOC大学英语词汇检测答案与解析（2023.6修订版）.txt",
    "/home/tarfersoul/TransMajor/data/download/体测项目和评分标准(1).txt"
]

result = []

# 检查文件夹和文件
def process_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content
    except UnicodeDecodeError:
        print(f"文件编码错误，无法读取：{file_path}")
        return None

# 处理文件夹中的所有 .txt 文件
for folder in folders:
    if os.path.exists(folder):
        for file in os.listdir(folder):
            # 跳过包含“名单”或“结果公示”的文件
            if file.endswith(".txt") and "名单" not in file and "公示" not in file:
                file_path = os.path.join(folder, file)
                content = process_file(file_path)
                if content:
                    result.append(f"{file}: {content}")
    else:
        print(f"文件夹不存在：{folder}")

# 处理额外文件
for file_path in extra_files:
    file_name = os.path.basename(file_path)
    if os.path.exists(file_path) and "名单" not in file_name and "公示" not in file_name:
        content = process_file(file_path)
        if content:
            result.append(f"{file_name}: {content}")
    else:
        print(f"额外文件不存在或被过滤：{file_path}")

# 保存
output_file = "/home/tarfersoul/TransMajor/data/document.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)  
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(result, json_file, ensure_ascii=False, indent=4)

print("Finished!")
