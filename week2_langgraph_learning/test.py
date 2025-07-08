import os, pathlib
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 设置凭据文件路径
credentials_path = pathlib.Path(__file__).with_name("credentials.json")
os.environ["GOOGLE_CLIENT_SECRETS_FILE"] = str(credentials_path)

# 验证凭据文件路径是否正确
print("GOOGLE_CLIENT_SECRETS_FILE:", os.environ["GOOGLE_CLIENT_SECRETS_FILE"])
print("文件是否存在:", credentials_path.exists())

# 使用 Google OAuth 流程进行授权
try:
    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        scopes=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send"
        ] #scopes是授权模式
    )
    credentials = flow.run_local_server(port=0)
    print("OAuth 授权成功")

    # 在此处可以添加 Gmail API 的调用逻辑
    # 例如：使用 credentials 发送邮件
    # 使用授权的凭据构建 Gmail 服务
    service = build('gmail', 'v1', credentials=credentials)

    # 读取最近一封邮件
    try:
        print("正在读取最近一封邮件...")
        # 获取用户的邮件列表
        # 限制 maxResults 为 5，减少 API 响应数据量
        results = service.users().messages().list(userId='me', maxResults=5).execute()
        print("正在获取邮件列表...")
        print("API 响应:", results)  # 打印 API 响应以调试
        messages = results.get('messages', [])
        print("找到邮件数量:", len(messages))
        if not messages:
            print("没有找到邮件。")
        else:
            for message_info in messages:
                # 获取每封邮件详情
                message_id = message_info['id']
                print("邮件 ID:", message_id)  # 打印邮件 ID
                message = service.users().messages().get(userId='me', id=message_id).execute()
                print("邮件详情 API 响应:", message)  # 打印邮件详情响应
                print("邮件主题:", message['payload']['headers'])
                print("邮件内容:", message['snippet'])
    except Exception as e:
        print("读取邮件失败:", str(e))
except Exception as e:
    print("OAuth 授权失败:", str(e))
