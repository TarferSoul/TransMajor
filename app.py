import gradio as gr
import os
from agent import TransMajor
import json
from utils import check_college_update
import logging
import re
from datetime import datetime
import uuid
import config  # 导入配置文件

# 日志
logging.basicConfig(
    filename=config.LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 类实例化
trans_major = TransMajor(
    api_key=config.API_KEY,
    base_url=config.BASE_URL,
    model_name=config.MODEL_NAME,
    temperature=config.TEMPERATURE,
    tools=[check_college_update]
)

# 定义持久化目录
persist_directory = config.PERSIST_DIRECTORY

# 尝试从磁盘加载向量存储
try:
    trans_major.load_vectorstore(persist_directory)
    print("Successfully loaded vector store from disk.")
except FileNotFoundError:
    print("Vector store not found on disk. Indexing documents...")
    # 加载文档文件
    if os.path.exists(config.DOCUMENT_FILE):
        with open(config.DOCUMENT_FILE, "r", encoding="utf-8") as f:
            documents = json.load(f)
    else:
        logging.error(f"Document file not found: {config.DOCUMENT_FILE}")
        raise FileNotFoundError(f"Document file not found: {config.DOCUMENT_FILE}")

    # 索引文档并持久化向量存储
    trans_major.index_documents(documents, persist_directory=persist_directory)
    print("Documents indexed and vector store persisted.")


# 提取文件内容
def extract_text_from_file(file):
    if file is None:
        return ''

    try:
        if isinstance(file, str):  # 如果是路径字符串
            file_obj = open(file, 'rb')
        elif hasattr(file, 'read'):  # 如果是文件对象
            file_obj = file
        else:
            raise ValueError("文件类型错误，既不是路径字符串，也不是文件对象")

        # 扩展名检查
        filename, file_extension = os.path.splitext(file_obj.name)
        file_extension = file_extension.lower()
        if file_extension not in config.ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件类型：{file_extension}")

        # 文件大小限制
        if os.path.getsize(file_obj.name) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValueError("文件过大，请上传小于 10MB 的文件")

        # 提取内容
        if file_extension == '.txt':
            text = file_obj.read().decode('utf-8', errors='ignore')
        elif file_extension == '.pdf':
            from PyPDF2 import PdfReader
            reader = PdfReader(file_obj)
            text = ''.join(page.extract_text() for page in reader.pages)
        elif file_extension in ['.doc', '.docx']:
            from docx import Document
            doc = Document(file_obj)
            text = '\n'.join([para.text for para in doc.paragraphs])
        elif file_extension in ['.xls', '.xlsx']:
            import pandas as pd
            df = pd.read_excel(file_obj)
            text = df.to_string()
        else:
            raise ValueError(f"不支持的文件类型：{file_extension}")

        return text.strip()
    except Exception as e:
        logging.error(f"提取文件内容时发生错误: {e}")
        return ''
    finally:
        if isinstance(file, str) and 'file_obj' in locals():
            file_obj.close()


# 输入问题安全检查
def sanitize_input(input_text):
    # 限制输入长度
    max_length = 10000
    if len(input_text) > max_length:
        raise ValueError(f"输入过长，请限制在 {max_length} 个字符以内")

    # 移除HTML和脚本标签
    sanitized_text = re.sub(r'<.*?>', '', input_text)

    # 防止SQL注入等特殊字符
    sanitized_text = re.sub(r'[\'";]', '', sanitized_text)

    return sanitized_text


# 普通问答功能
def qa_function(question, use_rag):
    try:
        question = sanitize_input(question)
        print("Is using RAG:", use_rag)
        if not question.strip():
            return "请输入有效的问题。"
        if use_rag:
            response = trans_major.rag_query(question)
        else:
            response = trans_major.query(question)
        answer = response['output'] if isinstance(response, dict) and 'output' in response else "抱歉，我无法获取到有效的回答。"
        return answer
    except Exception as e:
        logging.error(f"qa_function 执行错误: {e}")
        return "请求过程中发生未知错误，请稍后再试。"


# 文件问答功能
def file_qa_function(question, file):
    if not question.strip():
        return "请输入有效的问题。"
    if file is None:
        return "请上传一个文件以进行文件问答。"

    try:
        text = extract_text_from_file(file)
        if not text.strip():
            return "无法从文件中提取内容，请检查文件格式和内容。"
        response = trans_major.document_qa(text, question)
        answer = response['output'] if isinstance(response, dict) and 'output' in response else "抱歉，我无法获取到有效的回答。"
        return answer
    except Exception as e:
        logging.error(f"file_qa_function 执行错误: {e}")
        return "请求过程中发生未知错误，请稍后再试。"


# 保存QA数据
def save_qa_record(id, question, answer, use_rag, file=None, feedback=None):
    record = {
        "id":id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "answer": answer,
        "use_rag": use_rag,
        "file": file.name if file else None,
        "feedback": feedback
    }
    try:
        if os.path.exists(config.QA_RECORDS_FILE):
            with open(config.QA_RECORDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
        data.append(record)
        with open(config.QA_RECORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"保存问答记录时发生错误: {e}")


# 更新用户反馈
def update_feedback(record_id, feedback):
    try:
        if os.path.exists(config.QA_RECORDS_FILE):
            with open(config.QA_RECORDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for record in data:
                if record["id"] == record_id:
                    record["feedback"] = feedback
                    break
            with open(config.QA_RECORDS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"更新用户反馈时发生错误: {e}")


# 根据是否上传文件选择问答模式
def combined_function(question, file, use_rag):
    """
    问答逻辑，返回回答和记录ID。
    """
    try:
        if file is not None:
            # 使用文件问答模式
            answer = file_qa_function(question, file)
        else:
            # 使用普通问答模式
            answer = qa_function(question, use_rag)
        
        # 为当前问答生成唯一记录ID
        record_id = str(datetime.now().timestamp()).replace('.', '')  # 使用时间戳作为唯一ID
        save_qa_record(record_id,question, answer, use_rag, file)  # 保存记录
        
        return answer, record_id  # 返回回答和记录ID
    except Exception as e:
        logging.error(f"combined_function 执行错误: {e}")
        return "请求过程中发生未知错误，请稍后再试。", ""


# 创建 Gradio 界面

def submit_feedback(record_id, feedback):
    """
    更新反馈记录并返回感谢信息。
    """
    update_feedback(record_id, feedback)
    return f"感谢您的反馈！已记录为“{feedback}”。"

def submit_question():
    """
    提交问题后，显示反馈按钮并清空反馈信息
    """
    section = gr.Row.update(visible=True)
    return section, f""
with gr.Blocks(title='TransMajor') as iface:
    # 项目标题和描述居中
    with gr.Row(elem_id="header", equal_height=True):
        gr.Markdown(f"<h1 style='text-align: center;'>{config.TITLE}</h1>")

    gr.Markdown(config.DESCRIPTION)

    # 左右布局
    with gr.Row():
        # 左侧输入区域
        with gr.Column(scale=1):
            question_input = gr.Textbox(label="你的问题", placeholder="请输入问题", lines=2)
            file_input = gr.File(label="上传文件（可选）", file_types=config.ALLOWED_EXTENSIONS)
            use_rag_checkbox = gr.Checkbox(label="使用 RAG（检索增强生成）", value=False, info="RAG（Retrieval-Augmented Generation）是一种结合文档检索和生成能力的问答方法，开启 RAG 功能可以使得模型通过检索我们搜集到的华中科技大学转专业相关数据进行回答。")
            submit_button = gr.Button("提交问题")

        # 右侧输出区域
        with gr.Column(scale=2):
            answer_output = gr.Markdown(label="回答")  # 使用 Markdown 渲染回答内容
            record_id_output = gr.Textbox(visible=False)  # 隐藏的记录 ID
            feedback_output = gr.Markdown(label="反馈")  # 使用 Markdown 渲染回答内容

    # 反馈区域
    feedback_section = gr.Row(visible=False)
    with feedback_section:
        gr.Markdown("您是否对当前回答满意？请点击右侧的按钮选择满意或不满意，您的选择会帮助我们更好的改善模型")
        feedback_buttons = [
            gr.Button("满意", variant="primary"),
            gr.Button("不满意", variant="secondary")
        ]

    # 提交问题逻辑
    submit_button.click(
        combined_function,
        inputs=[question_input, file_input, use_rag_checkbox],
        outputs=[answer_output, record_id_output]
    )

    # 显示反馈按钮
    submit_button.click(
        submit_question,
        inputs=[],
        outputs=[feedback_section, feedback_output]
    )

    # 处理满意反馈
    feedback_buttons[0].click(
        submit_feedback,
        inputs=[record_id_output, gr.Text(value="满意", visible=False)],
        outputs=feedback_output
    )

    # 处理不满意反馈
    feedback_buttons[1].click(
        submit_feedback,
        inputs=[record_id_output, gr.Text(value="不满意", visible=False)],
        outputs=feedback_output
    )

if __name__ == "__main__":
    iface.launch(
        server_name=config.SERVER_NAME,
        server_port=config.SERVER_PORT,
        share=config.SHARE
    )
