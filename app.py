from flask import Flask
from flask_cors import CORS  # 添加跨域支持
from blueprints.auth import auth_bp  # 导入蓝图
from blueprints.article import article_bp  # 导入蓝图
from blueprints.media import media_bp  # 导入蓝图
from blueprints.activity import activity_bp  # 导入动态蓝图
from blueprints.friend_link import friend_link_bp  # 导入友链蓝图
from blueprints.message import message_bp  # 导入留言蓝图
from apscheduler.schedulers.background import BackgroundScheduler
from mail import send_activity_reminder_email
import os

# Flask 应用实例
app = Flask(__name__)

# 配置CORS设置
CORS(app)

app.register_blueprint(auth_bp)  # 注册蓝图
app.register_blueprint(article_bp)  # 注册蓝图
app.register_blueprint(media_bp)  # 注册蓝图
app.register_blueprint(activity_bp)  # 注册动态蓝图
app.register_blueprint(friend_link_bp)  # 注册友链蓝图
app.register_blueprint(message_bp)  # 注册留言蓝图


# 定时任务配置
def scheduled_email_task():
    # 默认发送给配置的邮箱发送者（即博主自己）
    admin_email = os.getenv("MAIL_USER")
    if admin_email:
        # print(f"正在向 {admin_email} 发送每日动态提醒...")
        send_activity_reminder_email(admin_email)


# 防止Debug模式下重载导致启动两次scheduler
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    scheduler = BackgroundScheduler()
    # 每天 19:30 执行
    scheduler.add_job(func=scheduled_email_task, trigger="cron", hour=19, minute=41)
    scheduler.start()
    # print("定时任务调度器已启动")


if __name__ == "__main__":
    app.run(debug=True)
