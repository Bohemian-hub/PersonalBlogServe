### 一、安装
1. 克隆或下载本项目代码。
2. 创建并激活虚拟环境（Windows 下示例）(条件允许，建议使用anaconda)：
```bash
python -m venv venv
.\venv\Scripts\activate
```
3. 安装依赖：
```bash
pip install -r requirement.txt
```
4. 根据需要在系统中设置数据库相关环境变量：
* DB_HOST
* DB_USER
* DB_PASSWORD
* DB_NAME

### 二、本地运行
1. 启动应用：
```bash
python app.py
```
### 三、使用 Gunicorn 部署运行
1. 安装 Gunicorn：
```bash
pip install gunicorn
```
2. 在服务器环境中，使用如下命令：
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```
3. 通过浏览器或其他客户端访问对应 IP 地址与端口进行测试。