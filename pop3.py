import email
import socket
import configparser
from email import message_from_string
import base64
from email.header import decode_header
import glob
import os
import quopri
from email.parser import BytesParser
from email.policy import default
from email import policy
import json
from EmailMethod import *
from Function_3_4 import *



def save_email_eml(email_data, save_path, uidl):
    # Phân giải email từ dạng bytes
    email_message = BytesParser(policy=policy.default).parsebytes(email_data)

    # Tạo tên file dựa trên UIDL của email
    email_filename = f"{uidl.split('.')[0]}.eml"
    email_path = os.path.join(save_path, email_filename)

    # Lưu email vào file .msg
    with open(email_path, "wb") as email_file:
        email_file.write(email_data)
 

file_path = "D:/SMTPPOP3/mailclient/mailclient/uidl_status_download.json"

try:
    with open(file_path, 'r') as file:
        downloaded_uidls = json.load(file)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    # Nếu tệp không tồn tại hoặc nội dung không hợp lệ JSON, tạo danh sách mới rỗng
    downloaded_uidls = []

# Hàm để đánh dấu email đã tải
def mark_as_downloaded(uidl):
    downloaded_uidls.append(uidl)
    save_status()

# Hàm để kiểm tra xem email đã được tải hay chưa
def is_downloaded(uidl):
    return uidl in downloaded_uidls

# Hàm để lưu trạng thái vào tệp
def save_status():
    # Kiểm tra và tạo thư mục nếu cần
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(downloaded_uidls, file, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Lỗi khi lưu trạng thái: {e}")

def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path, encoding="utf-8")
    return config

def move_email(email_message, save_path, uidl, target_folder):
    email_filename = f"{uidl.split('.')[0]}.eml"
    target_folder_path = os.path.join(save_path, target_folder)
    # Tạo thư mục nếu nó không tồn tại
    os.makedirs(target_folder_path, exist_ok=True)

    email_path = os.path.join(target_folder_path, email_filename)

    with open(email_path, "wb") as email_file:
        email_file.write(email_message.as_bytes())
        
def get_email_content(email_message):
    content = ""
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            content += part.get_payload(decode=True).decode("utf-8", errors="ignore")

    return content
    
def filter_and_move_email(email_message, save_path, uidl):
    config = load_config("D:/SMTPPOP3/mailclient/mailclient/Config.ini")
    from_address = email_message.get('from', '').lower()
    subject = email_message.get('subject', '').lower()
    content = get_email_content(email_message).lower() 

    folder = None
    if config.has_section('USER') and 'to_folder' in config['USER']:
        folder = config['USER']['to_folder']

    if 'ahihi@testing.com' in from_address or 'ahuu@testing.com' in from_address:
        move_email(email_message, save_path, uidl, "Project")
    elif 'urgent' in subject or 'asap' in subject:
        move_email(email_message, save_path, uidl, "Important")
    elif 'report' in content or 'meeting' in content:
        move_email(email_message, save_path, uidl, "Work")
    elif any(keyword in subject or keyword in content for keyword in ["virus", "hack", "crack"]):
        move_email(email_message, save_path, uidl, "Spam")
    elif folder:
        move_email(email_message, save_path, uidl, folder)
    else:
        move_email(email_message, save_path, uidl, "Inbox")

        
def download_msg(user_name, user_pass, pop3_server, pop3_port, save_msg_path):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client_socket:
        client_socket.connect((pop3_server,pop3_port))
        response = client_socket.recv(1024).decode("utf-8")
        print(response)
        
        # GỬI LỆNH USER
        client_socket.send(f"USER {user_name}\r\n".encode("utf-8"))
        response = client_socket.recv(1024).decode("utf-8")
        print(response)

        # Gửi lệnh PASS
        client_socket.send(f"PASS {user_pass}\r\n".encode("utf-8"))
        response = client_socket.recv(1024).decode("utf-8")
        print(response)
        
        # Gửi lệnh STAT để lấy thông tin về số lượng email
        client_socket.send("STAT\r\n".encode("utf-8"))
        response = client_socket.recv(1024).decode("utf-8")
        print(response)
        # Lấy thông tin về số lượng email và kích thước của chúng
        num_messages = int(response.split()[1])
        print(response)
        print(f"Total emails: {num_messages}")
        print("LIST")
        # Gửi lệnh LIST để lấy danh sách email
        client_socket.send("LIST\r\n".encode("utf-8"))
        response = client_socket.recv(4096).decode("utf-8")
        print(response)
        
     
    
        print("UIDL")
        # Lấy danh sách UIDL (Unique IDs) của tất cả email
        uidl_command = "UIDL\r\n"
        client_socket.sendall(uidl_command.encode())
        response = client_socket.recv(1024).decode()
        print(response)
        uidl_list = response.split("\r\n")[1:-2]
        uidl_list = [uidl.split()[1] for uidl in uidl_list ]
        
         # Lấy thông tin của từng email và tải nội dung có attachment
        for i in range(1,num_messages +1):
            uidl = uidl_list[i - 1]
            # Kiểm tra xem email đã tải hay chưa
            if not is_downloaded(uidl):
                # Gửi lệnh RETR để lấy nội dung email
                retr_command = f"RETR {i}\r\n"

                client_socket.sendall(retr_command.encode("utf-8"))
                email_data = b''
                while True:
                    data = client_socket.recv(4096)
                    email_data += data
                    if data.decode().endswith("\r\n.\r\n"):
                        break

                email_data = '\n'.join(email_data.decode().splitlines()[1:-1]).encode('utf-8')
                # Hiển thị thông tin về email
                email_data = email_data.decode("utf-8")
                # Xử lý nội dung email
                email_message = BytesParser(policy=default).parsebytes(email_data.encode("utf-8"))

                #save_email_eml(email_data.encode("utf-8"), save_msg_path, uidl)
                filter_and_move_email(email_message, save_msg_path, uidl)
                # Đánh dấu email đã tải
                mark_as_downloaded(uidl)
       # Gửi lệnh QUIT để đóng kết nối
        client_socket.send("QUIT\r\n".encode("utf-8"))
        response = client_socket.recv(1024).decode("utf-8")
        print(response)