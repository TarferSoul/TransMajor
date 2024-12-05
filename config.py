# config.py

# 项目配置文件
MODEL_NAME = "gpt-4o"
API_KEY = "your_api_key"
BASE_URL = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o"
TEMPERATURE = 0.7

# 文件路径
DOCUMENT_FILE = "./data/document.json" # 知识库
QA_RECORDS_FILE = "./data/qa_records.json" #QA数据
LOG_FILE = "./trans_major_errors.log" # log
PERSIST_DIRECTORY = './vecstore' # 向量库
FEEDBACK_FILE = "./data/qa_feedback.json" #带反馈的QA数据

# 文件类型参数
ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx']
MAX_FILE_SIZE_MB = 10  # 最大上传size显示，单位MB

# Gradio参数
SERVER_NAME = "0.0.0.0"
SERVER_PORT = 7860
SHARE = False

# 界面描述
TITLE = "TransMajor：面向 Huster 的大语言模型驱动智能转专业助手"
DESCRIPTION = (
    "### 项目说明\n"
    "- 本项目为 Python 课程大作业，仅供学习交流使用。\n"
    "- 本助手基于大语言模型，旨在帮助用户解决与转专业相关的常见问题。\n"
    "- **注意：** 大语言模型回答具有局限性，可能会出现不准确或幻觉信息。请谨慎参考，最终请以学校官方文件为准。\n"
)
