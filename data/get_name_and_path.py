import os
import csv
import pdfplumber
import docx
import pandas as pd
import xlrd  # For reading .xls files
import win32com.client as win32  # For reading .doc files

# Define the directory to scan
directory = 'download'
output_dir = 'converted_txt'  # Directory to store the converted .txt files

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# List to hold file information
file_list = []

# Function to convert PDF to text
def convert_pdf_to_txt(pdf_path, txt_path):
    with pdfplumber.open(pdf_path) as pdf:
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            for page in pdf.pages:
                txt_file.write(page.extract_text())

# Function to convert Word to text
def convert_docx_to_txt(docx_path, txt_path):
    doc = docx.Document(docx_path)
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        for para in doc.paragraphs:
            txt_file.write(para.text + '\n')

# Function to convert Word (.doc) to text
def convert_doc_to_txt(doc_path, txt_path):
    try:
        word = win32.Dispatch("Word.Application")
        abs_doc_path = os.path.abspath(doc_path)  # 确保路径为绝对路径
        doc = word.Documents.Open(abs_doc_path)
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(doc.Content.Text)
        doc.Close()
        word.Quit()
        print(f"Successfully converted {doc_path} to {txt_path}")
    except Exception as e:
        print(f"Error converting {doc_path}: {e}")

# Function to convert Excel to text
def convert_excel_to_txt(excel_path, txt_path):
    df = pd.read_excel(excel_path)
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(df.to_string())

# Function to convert Excel (.xls) to text
def convert_xls_to_txt(xls_path, txt_path):
    workbook = xlrd.open_workbook(xls_path)
    sheet = workbook.sheet_by_index(0)
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        for row_num in range(sheet.nrows):
            row_values = sheet.row_values(row_num)
            txt_file.write('\t'.join(map(str, row_values)) + '\n')

# Walk through the directory
for root, dirs, files in os.walk(directory):
    for file in files:
        # Get the relative path including the directory
        relative_path = os.path.relpath(os.path.join(root, file), os.getcwd())
        # Generate the .txt file path
        txt_filename = os.path.splitext(file)[0] + '.txt'
        txt_relative_path = os.path.join(output_dir, txt_filename)

        # Convert files based on their extension
        file_extension = os.path.splitext(file)[1].lower()
        full_file_path = os.path.join(root, file)

        if file_extension == '.pdf':
            convert_pdf_to_txt(full_file_path, txt_relative_path)
        elif file_extension == '.docx':
            convert_docx_to_txt(full_file_path, txt_relative_path)
        elif file_extension == '.xlsx':
            convert_excel_to_txt(full_file_path, txt_relative_path)
        elif file_extension == '.txt':
            # If the file is already a .txt file, just copy the path
            txt_relative_path = relative_path
        elif file_extension == '.xls':
            convert_xls_to_txt(full_file_path, txt_relative_path)
        elif file_extension == '.doc':
            convert_doc_to_txt(full_file_path, txt_relative_path)
        else:
            # For unsupported files, skip conversion
            txt_relative_path = ''  # Leave empty if no conversion is performed

        # Append file information to the list
        file_list.append([file, relative_path, txt_relative_path])

# Write to CSV file
with open('file_list.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header
    csvwriter.writerow(['name', 'path', 'txt_path'])
    # Write the file information
    csvwriter.writerows(file_list)