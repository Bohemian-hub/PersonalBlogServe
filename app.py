from flask import Flask
from flask_cors import CORS  # 添加跨域支持
from blueprints.auth import auth_bp  # 导入蓝图
from blueprints.article import article_bp  # 导入蓝图
from blueprints.media import media_bp  # 导入蓝图


# Flask 应用实例
app = Flask(__name__)

# 配置CORS设置
CORS(app)

app.register_blueprint(auth_bp)  # 注册蓝图
app.register_blueprint(article_bp)  # 注册蓝图
app.register_blueprint(media_bp)  # 注册蓝图

if __name__ == "__main__":
    app.run(debug=True)
