from flask import Flask, send_from_directory

from models.roleMenus import RoleMenus, Menu, RoleButtons
from models.systemManagement import *
from utils.utils import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 防止显示警告
app.config['SECRET_KEY'] = SECRET_KEY
# db = SQLAlchemy(app)
db.init_app(app)

# 引用角色路由
# from routes.roleRoutes import role_blueprint
# app.register_blueprint(role_blueprint, url_prefix='')
# 引用角色路由

from routes import register_routes

register_routes(app)

import jwt


# MD5 加密

@app.before_request
@login_required
def check_login():
    pass


# MD5 加密

# 添加下面这行代码，创建应用上下文
# app.app_context().push()

# 数据模型


# 初始化数据库
# with app.app_context():
#     db.create_all()
# db.create_all()

# **********************

# *********操作 admin 表


@app.route('/public/<path:filename>')
def serve_image(filename):
    return send_from_directory('public', filename)


from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from models.news import News


@app.route('/aaa')
def aa():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 如果需要无界面模式，可以添加这一行
    driver = webdriver.Chrome(options=options)
    driver.get("https://so.gushiwen.cn/gushi/tangshi.aspx")
    driver.implicitly_wait(30)
    data1 = driver.find_elements(By.CSS_SELECTOR, '.left .sons div:nth-child(1) span')
    for item in data1:
        news_item = News(title=item.text)
        db.session.add(news_item)
        db.session.commit()
        print(item.text)
    return "ok"

def proxy_ip():
    url = 'https://httpbin.org/ip'
    proxy = '58.58.213.55:8888'
    driver_path = '/path/to/chromedriver'

    # 使用 ChromeOptions 设置代理
    opt = webdriver.ChromeOptions()
    opt.add_argument('--proxy-server=' + proxy)

    # 移除 executable_path 参数
    browser = webdriver.Chrome(options=opt)
    browser.get(url)
    print(browser.page_source)
    browser.quit()  # 使用 quit() 方法关闭浏览器



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(debug=True)
