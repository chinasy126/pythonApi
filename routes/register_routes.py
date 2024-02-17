# routes/register_routes.py
from .role_routes import role_blueprint
from .user_routes import user_blueprint
from .admin_routes import admin_blueprint
from routes.menu_routes import menu_blueprint
from routes.news_routes import news_blueprint
from routes.upload_routes import upload_blueprint
from routes.product_class_routes import product_class_blueprint


def register_routes(app):
    # 注册角色路由
    app.register_blueprint(role_blueprint, url_prefix='')
    # 注册用户路由
    app.register_blueprint(user_blueprint, url_prefix='')
    # 用户管理
    app.register_blueprint(admin_blueprint)
    # 菜单管理
    app.register_blueprint(menu_blueprint)
    # 新闻管理
    app.register_blueprint(news_blueprint)
    # 图片上传
    app.register_blueprint(upload_blueprint)
    # 产分分类
    app.register_blueprint(product_class_blueprint)
