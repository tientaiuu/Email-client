import os
import shutil
import configparser
import string
import re
import glob
import email
from email import policy
from email.parser import BytesParser
import base64

def read_eml_file(eml_file_path):
    with open(eml_file_path, 'rb') as eml_file:
        msg = BytesParser(policy=policy.default).parse(eml_file)
    return msg

def get_email_info(msg):
    subject = "Subject: " + msg.get('Subject', '')
    sender = "From: " + msg.get('From', '')
    date_sent = "Date: " + msg.get('Date', '')
    return subject, sender, date_sent

def get_email_text(msg):
    text_content = ""
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            text_content += part.get_payload()
    return text_content

def get_attachments(msg):
    attachments = []
    for part in msg.walk():
        if part.get('Content-Disposition') and part.get('Content-Disposition').startswith("attachment"):
            filename = part.get_filename()
            if filename:
                attachments.append(filename)
    return attachments

def get_image_paths(msg):
    image_paths = []
    for part in msg.walk():
        if part.get_content_type().startswith("image"):
            image_paths.append(part.get_filename())
    return image_paths

def download_attachments(eml_file_path, save_folder):
    with open(eml_file_path, 'rb') as eml_file:
        msg = BytesParser(policy=policy.default).parse(eml_file)

        # Lặp qua tất cả các phần tử trong email
        for part in msg.walk():
            if part.get('Content-Disposition') and part.get('Content-Disposition').startswith("attachment"):
                # Lấy tên của tệp đính kèm
                filename = part.get_filename()

                # Kiểm tra xem tên tệp có tồn tại không
                if filename:
                    # Tạo đường dẫn đầy đủ để lưu tệp
                    file_path = os.path.join(save_folder, filename)

                    # Ghi nội dung của tệp đính kèm vào máy
                    with open(file_path, 'wb') as file:
                        file.write(part.get_payload(decode=True))

                    print(f"Tải về thành công: {filename} - Lưu tại: {file_path}")

# lay ra link file 
def find_file(file_name):
    # Tìm kiếm tất cả các tệp có tên file_name trên toàn bộ hệ thống
    files = glob.glob('**/' + file_name, recursive=True)

    if files:
        # Trả về đường dẫn của tệp đầu tiên tìm thấy
        return files[0]

    # Trả về None nếu không tìm thấy tệp
    return None
# lay ra link folder
def find_folder(folder_name):
    # Bắt đầu từ thư mục gốc ('/') và lặp qua toàn bộ hệ thống tệp tin
    for root, dirs, files in os.walk('/', topdown=True):
        if folder_name in dirs:
            # Nếu tìm thấy thư mục, trả về đường dẫn của nó
            return os.path.join(root, folder_name)

    # Trả về None nếu không tìm thấy thư mục
    return None


# lọc đoạn text
def FilterText(Text):
    config_obj = configparser.ConfigParser()
    Config_path = find_file("Config.ini")
    config_obj.read(Config_path)

    Work_config = config_obj["WORK"]
    Spam_config = config_obj["SPAM"]

    List_KeyWords_Spam = Spam_config["KeyWords"]
    List_KeyWords_Work = Work_config["From"] + Work_config["Subject"] + ", " + Work_config["Recruitment"] + ", " + Work_config["Job_Positions"] + ", " + Work_config["Job_Requirements"] + ", " + Work_config["Job_Benefits"]
    List_KeyWords_Spam = List_KeyWords_Spam.split(",")
    List_KeyWords_Work = List_KeyWords_Work.split(",")

    is_Spam = re.compile("|".join(List_KeyWords_Spam), flags=re.IGNORECASE)
    is_work = re.compile("|".join(List_KeyWords_Work), flags=re.IGNORECASE)

    if re.search(is_Spam, Text):
        return "Spam"
    if re.search(is_work, Text):
        return "Work"
    return "Inbox" 

# in ra danh sach cac lua chon
def PrintList(folder):
    folder_path = find_folder(folder)
    List_EmailFile = dict()
    i = 1
    
    #create list 
    for choice in os.listdir(folder_path):
        List_EmailFile[i] = choice
        i += 1    
    List_EmailFile[i] = "Thoát."
    
    # in menu
    for key, value in List_EmailFile.items():
        text = value.split(".")
        if "eml" in text:
            config_obj = configparser.ConfigParser()
            Config_path = find_file("Config.ini")
            config_obj.read(Config_path, encoding='utf-8')

            config_User = config_obj["USER"]
            config_readed = config_User['Readed']
            #kiem tra trang thai email
            status = "Chưa đọc"
            if value in config_readed:
                status = "Đã đọc"
            file_path = find_file(value)
            info = get_email_info(read_eml_file(file_path))
            print(f"{key}. {status}, {info[0]}, {info[1]}, {info[2]}\r\n")
        else:
            print(f"{key}. {value} \r\n")     

    # return dictionary
    return List_EmailFile


# di chuyen file email
def moveFile(file_name, folder_name):
    file_path = find_file(file_name)
    folder_path = find_folder(folder_name)
    try:
        if os.path.exists(file_path) and os.path.exists(folder_path):
            shutil.move(file_path, folder_path)
            print(f"File đã được chuyển thành công đến {folder_path}")
        else:
            print("File không tồn tại. ")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


## Lấy nội dung email
def get_content_from_eml(eml_file_path):
    with open(eml_file_path, 'r', encoding='utf-8') as eml_file:
        # Đọc nội dung của file EML
        eml_content = eml_file.read()

    # Parse nội dung của EML thành đối tượng EmailMessage
    msg = email.message_from_string(eml_content)

    # Lấy nội dung của email
    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))

        # Kiểm tra xem phần này có phải là text/plain hay không
        if content_type == "text/plain" and "attachment" not in content_disposition:
            # Lấy đoạn mã content
            content = part.get_payload()

            # Kiểm tra xem có mã hóa không
            if part.get('Content-Transfer-Encoding') == 'base64':
                # Giải mã nếu có mã hóa base64
                content = base64.b64decode(content).decode('utf-8')

            return content
        
#luu email file name vao Readed
def save_file_name(Email):
    config_obj = configparser.ConfigParser()
    config_path =find_file("Config.ini")
    config_obj.read(config_path, encoding='utf-8')
    config_User = config_obj['USER']
    config_readed = config_User['Readed']
    if not Email in config_readed:
        current_value = config_obj.get('USER', 'Readed')
        new_value = f"{current_value}, {Email}"
        config_obj.set('USER', 'Readed', new_value)
        with open(config_path, 'w', encoding='utf-8') as file:
            config_obj.write(file)