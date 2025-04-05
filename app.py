from flask import Flask
from flask_cors import CORS  # 添加跨域支持
from blueprints.auth import auth_bp  # 导入蓝图


# Flask 应用实例
app = Flask(__name__)

# 配置更详细的CORS设置
CORS(
    app,
    resources={
        r"/*": {
            "origins": ["http://localhost:8080"],  # 明确指定允许的前端源
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许的HTTP方法
            "allow_headers": [
                "Content-Type",
                "Authorization",
                "X-Requested-With",
            ],  # 允许的请求头
            "supports_credentials": True,  # 如果需要带Cookie的请求，设为True
        }
    },
)

app.register_blueprint(auth_bp)  # 注册蓝图

if __name__ == "__main__":
    app.run(debug=True)
