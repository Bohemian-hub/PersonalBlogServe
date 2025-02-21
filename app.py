from flask import Flask
from dotenv import load_dotenv
from blueprints.auth import auth_bp  # 导入蓝图

# 加载环境变量
load_dotenv()

# Flask 应用实例
app = Flask(__name__)
app.register_blueprint(auth_bp)  # 注册蓝图

if __name__ == "__main__":
    app.run(debug=True)
