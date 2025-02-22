from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS  # 添加跨域支持
from blueprints.auth import auth_bp  # 导入蓝图

# 加载环境变量
load_dotenv()

# Flask 应用实例
app = Flask(__name__)
CORS(app)  # 启用跨域支持，默认允许所有域名访问

app.register_blueprint(auth_bp)  # 注册蓝图

if __name__ == "__main__":
    app.run(debug=True)