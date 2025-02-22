from flask import Flask
from flask_cors import CORS  # 添加跨域支持
from blueprints.auth import auth_bp  # 导入蓝图


# Flask 应用实例
app = Flask(__name__)
CORS(app)  # 启用跨域支持，默认允许所有域名访问

app.register_blueprint(auth_bp)  # 注册蓝图

if __name__ == "__main__":
    app.run(debug=True)