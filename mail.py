import smtplib
from email.mime.text import MIMEText
from email.header import Header
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()
# 从环境变量获取配置
mail_host = os.getenv("MAIL_HOST")
mail_port = int(os.getenv("MAIL_PORT"))
mail_user = os.getenv("MAIL_USER")
mail_pass = os.getenv("MAIL_PASS")


def send_email(to_addr, code):

    # HTML 邮件模板
    html_content = f"""
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-bottom: 20px; text-align: center;">邮箱验证码</h2>
            <p style="color: #666; font-size: 16px;">亲爱的用户：</p>
            <p style="color: #666; font-size: 14px; line-height: 1.6;">
                欢迎注册何东的个人博客！您的验证码为：
            </p>
            <div style="background-color: #fff; padding: 15px; margin: 20px 0; text-align: center; border-radius: 5px;">
                <span style="color: #007bff; font-size: 24px; font-weight: bold; letter-spacing: 5px;">
                    {code}
                </span>
            </div>
            <p style="color: #666; font-size: 14px;">
                验证码有效期为5分钟，请勿泄露给他人。<br>
                如非本人操作，请忽略此邮件。
            </p>
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 12px;">
                <p>这是一封自动发送的邮件，请勿直接回复</p>
                <p>© 2025 何东的个人博客 版权所有</p>
            </div>
        </div>
    </div>
    """

    # 创建邮件对象
    message = MIMEText(html_content, "html", "utf-8")
    message["From"] = Header(mail_user)  # 发件人
    message["To"] = Header(to_addr)  # 收件人
    message["Subject"] = Header("注册验证码 - 何东的个人博客", "utf-8")

    try:
        # 创建SSL加密连接
        smtpObj = smtplib.SMTP_SSL(mail_host, mail_port)
        # 登录邮箱（使用授权码而非密码）
        smtpObj.login(mail_user, mail_pass)
        # 发送邮件
        smtpObj.sendmail(mail_user, [to_addr], message.as_string())
        # print("邮件发送成功")
        return True
    except smtplib.SMTPException as e:
        # print(f"发送失败: {str(e)}")
        return False
    finally:
        smtpObj.quit()


# 使用示例
if __name__ == "__main__":
    result = send_email("dongshangwl@gmail.com", "123456")  # 收件地址
    print(result)
