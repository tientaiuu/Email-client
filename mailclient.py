import socket
import base64
import os
import email.utils
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from Function_3_4 import ViewEmail, MoveEmail
from email.parser import BytesParser
from email import policy
from email import encoders
from pop3 import *

def menu():
    print("Vui lòng chọn menu: ")
    print("1. Để gửi email ")
    print("2. Để xem danh sách các email đã nhận ")
    print("3. Di Chuyển email")
    print("4. Tải nội dung mail")
    print("5. Thoát ")
     
def send_email(sender_email,  smtp_server, smtp_port, to_list , cc_list, bcc_list, subject, body, attachment_paths):
    # Tạo đối tượng MIMEMultipart
    message = MIMEMultipart()
    
    # Thêm ngày giờ và Message ID
    message['Message-ID'] = email.utils.make_msgid()
    message['Date'] = email.utils.formatdate(localtime=True)
    # Thêm danh sách TO vào email nếu có
    if to_list != ['']:
        to = ', '.join(to_list)
        message['TO'] = to
        
    # Thêm danh sách CC vào email nếu có
    if cc_list != ['']:
        cc = ', '.join(cc_list)
        message['CC'] = cc
        
    # Thêm nội dung email
    message['From'] = sender_email
    message['Subject'] = subject
    
    message.attach(MIMEText(body, 'plain'))
  

    # Thêm các file đính kèm
    if attachment_paths:
        for attachment_path in attachment_paths:
                with open(attachment_path, 'rb') as attachment_file:
                    mime_type, _ = mimetypes.guess_type(attachment_path)
                    text_mime_type = mime_type.split('/')
                    subtype = text_mime_type[1]
                    attachment = MIMEApplication(attachment_file.read(), f'{subtype}; name ="{os.path.basename(attachment_path)}"')
                    attachment.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
                    message.attach(attachment)

    # Xây dựng nội dung MIME
    mime_content = message.as_string()

    # Kết nối đến server SMTP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((smtp_server, smtp_port))

        # Nhận và in lời chào từ server
        response = client_socket.recv(1024)
        print(response.decode())

        # Gửi lệnh EHLO để bắt đầu phiên làm việc
        client_socket.sendall('EHLO [127.0.0.1]\r\n'.encode())
        response = client_socket.recv(1024)
        print(response.decode())

        # # Bắt đầu quá trình xác thực
        # client_socket.sendall('AUTH LOGIN\r\n'.encode())
        # response = client_socket.recv(1024)
        # print(response.decode())

        # # Gửi tên người dùng đã mã hóa base64
        # client_socket.sendall(base64.b64encode(username.encode()) + b'\r\n')
        # response = client_socket.recv(1024)
        # print(response.decode())

        # # Gửi mật khẩu đã mã hóa base64
        # client_socket.sendall(base64.b64encode(password.encode()) + b'\r\n')
        # response = client_socket.recv(1024)
        # print(response.decode())

        # Gửi lệnh MAIL FROM
        client_socket.sendall(f'MAIL FROM: <{sender_email}>\r\n'.encode())
        response = client_socket.recv(1024)
        print(response.decode())

        # Gửi lệnh RCPT TO:
        if to_list != ['']:
            for tos in to_list:
                client_socket.sendall(f'RCPT TO: <{tos}>\r\n'.encode())
                response = client_socket.recv(1024)
                print(response.decode())
        
        if cc_list != ['']:
            for ccs in cc_list:
                client_socket.sendall(f'RCPT TO: <{ccs}>\r\n'.encode())
                response = client_socket.recv(1024)
                print(response.decode())
        
        if bcc_list != ['']:
            for bccs in bcc_list:
                 client_socket.sendall(f'RCPT TO: <{bccs}>\r\n'.encode())
                 response = client_socket.recv(1024)
                 print(response.decode())

        # Gửi lệnh DATA để bắt đầu truyền nội dung email
        client_socket.sendall('DATA\r\n'.encode())
        response = client_socket.recv(1024)
        print(response.decode())

        # Gửi nội dung email
        client_socket.sendall(mime_content.encode())
        client_socket.sendall('\r\n.\r\n'.encode())
        response = client_socket.recv(1024)
        print(response.decode())

        # Đóng kết nối
        client_socket.sendall('QUIT\r\n'.encode())
        response = client_socket.recv(1024)
        print(response.decode())

    print(f'Gửi email thành công!\r\n')
    
def main():
   while True:
        menu()
        choice = int(input("Nhập lựa chọn: "))
        # Gửi mail với attachment
        if choice == 1: 
            print("Đây là thông tin soạn email: (nếu không điền vui lòng nhấn enter để bỏ qua)")
            
            # Thông tin tài khoản email
            sender_email = input("Nhập địa chỉ email của bạn: ")

            # Thông tin SMTP server 
            smtp_server = "127.0.0.1"
            smtp_port = 2225
            
            # Nhập thông tin người nhận
            to_list = input("TO: ").split(',')
            cc_list = input("CC: ").split(',')
            bcc_list = input("BCC: ").split(',')

            subject = input("Subject: ")
            
            print("Content: ")
            content_lines = []
            while True:
                line = input()
                if not line: 
                    break
                content_lines.append(line)
            body = "\r\n".join(content_lines) + "\r\n"
            
            choice1 = int(input("Có gửi kèm file (1. có, 2. không): "))
            attachment_paths = []
            if choice1 == 1:
                temp = int(input("Số lượng file muốn gửi: "))
                for i in range(temp):
                    path = input("Cho biết đường dẫn file thứ {}: ".format(i + 1))
                    if os.path.exists(path) == False:
                        print(f"File không tồn tại")
                        continue
                    else:
                        attachment_size = os.path.getsize(path) / (1024 * 1024)  # Kích thước file đính kèm tính bằng MB
                        if attachment_size > 3:
                            print(f"{os.path.basename(path)} vượt quá giới hạn dung lượng.")
                            continue
                    attachment_paths.append(path)
            send_email(sender_email, smtp_server, smtp_port, to_list , cc_list, bcc_list, subject, body, attachment_paths)
        elif choice == 2:
            ViewEmail()
        elif choice == 3:
            MoveEmail()
        # tải mail 
        elif choice == 4: 
            config_obj = configparser.ConfigParser()
            config_file = "D:/SMTPPOP3/mailclient/mailclient/Config.ini"
            config_obj.read(config_file, encoding = "utf-8")

            user_config = config_obj['USER']
            user_name = user_config['Email'].strip('"\'')
            user_pass = user_config['Password'].strip('"\'')
            pop3_server = user_config['Mailserver'].strip('"\'')
            pop3_port = int(user_config['POP3'].strip('"\''))
            save_msg_path = f"D:/SMTPPOP3/mailclient/mailclient/mailbox"
            os.makedirs(save_msg_path, exist_ok=True)
            download_msg(user_name, user_pass, pop3_server, pop3_port, save_msg_path)
        elif choice == 5:   
              print("Hẹn gặp lại!\r\n")
              exit()
            

if __name__ == '__main__':
    main()