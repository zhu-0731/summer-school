import imaplib, email
from email.header import decode_header

def fetch_subjects(host, user, auth_code, keyword: str, limit: int = 10):
    """读取最近 limit 封邮件，按关键字过滤并返回标题列表"""
    with imaplib.IMAP4_SSL(host) as imap:
        imap.login(user, auth_code)
        imap.select("INBOX")

        # ALL + 逆序截取 limit 封
        status, msg_ids = imap.search(None, "ALL")
        ids = msg_ids[0].split()[-limit:]

        result = []
        for mid in ids[::-1]:
            _, data = imap.fetch(mid, "(RFC822)")
            if data and data[0] is not None:
                raw_email = data[0][1] if isinstance(data[0], tuple) and len(data[0]) > 1 else None
                if isinstance(raw_email, (bytes, bytearray)):
                    msg = email.message_from_bytes(raw_email)
                    subject, enc = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(enc or "utf-8", errors="ignore")
                    if keyword.lower() in subject.lower():
                        result.append(subject)
        return result
