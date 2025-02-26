## Cách khởi động chương trình
Phần Mail Server sử dụng: https://github.com/eugenehr/test-mail-server/releases/download/1.0/test-mail-server-1.0.jar
#### LƯU Ý: Cần thay đổi các đường dẫn tới folder/file để có thể thực thi, biên dịch chương trình vì
mỗi máy có 1 link đường dẫn khác nhau
- Hàm pop3.py Line 32, Đường dẫn tới folder chứa file json lưu trạng thái mail đã download hay
chưa
- Hàm pop3.py Line 86, đường dẫn tới file Config.ini
- Hàm mailclient.py Line 186, đường dẫn tới file Config.ini
- Hàm mailclient.py Line 194, đường dẫn tới folder mailbox để lưu mail

#### Với chương trình này có sử dụng thư viện "glob" nên cần cấp quyền admin để có thể chạy, ví dụ:
- Chọn file sau đó click chuột phải -> Properties, sau đó sẽ hiện lên 1 bảng
- Chọn Security -> System hoặc Adminstrator -> OK
  
- Mở Command Prompt với đường dẫn tới folder chứa file test-mail-server-1.0.jar 
- Nhập lệnh "java -jar test-mail-server-1.0.jar -s 2225 -p 3335 -m ./" để khởi động chương trình
Test Mail Server với port SMTP = 2225, port POP3 = 3335
