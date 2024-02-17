from datetime import datetime, timedelta

# 创建一个 Blueprint 对象
from flask import Blueprint, session

from models.admin import *
from models.roleMenus import *
from models.systemManagement import *
from utils.utils import *
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
import os

user_blueprint = Blueprint('user', __name__)


# 用户登录
@user_blueprint.route('/user/login', methods=['POST'])
def user_login():
    data = request.get_json()
    print(data)
    if data["code"].lower() != session['captcha'].lower():
        return response("", 20001, "验证码输入错误", False)
    existing_user = Admin.query.filter_by(username=data['username'], password=md5_hash(data['password'])).first()
    if existing_user:
        token = jwt.encode({
            'id': existing_user.id,
            'username': existing_user.username,
            'exp': datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY)
        return response({"token": token, "name": data['username']}, 20000, '成功'), 201
    else:
        return response({"message": "用户名密码错误"}), 401


@before_reset_token_request
@user_blueprint.route('/user/resetToken', methods=['POST'])
def refresh_token():
    # 获取旧 token
    old_token = request.headers.get("X-Token", default=None)
    if not old_token:
        return response("", 40001, "未提供 token", False)

    try:
        # 解码旧 token
        old_token_data = jwt.decode(old_token, SECRET_KEY, algorithms=['HS256'])
        print(old_token_data)
    except jwt.ExpiredSignatureError:
        # return response("", 40002, "token 已过期", False)
        if 'user_id' in session:
            admin_item = Admin.query.filter(Admin.id == session['user_id']).first()
            # 生成新的 token
            new_token = jwt.encode({
                'id': admin_item.id,
                'username': admin_item.username,
                'exp': datetime.utcnow() + timedelta(minutes=30 * 6)}, SECRET_KEY)
            return response({"token": new_token}, 20000, '成功'), 201
        else:
            return response("", 40001, "没有登录", False)
    except jwt.InvalidTokenError:
        return response("无效的 token", 50008)


# token 黑名单
blacklisted_tokens = []


# 退出登录
@user_blueprint.route("/user/logout", methods=['POST'])
def user_logout():
    token = request.headers.get("X-Token")

    # 将Token添加到黑名单
    # blacklisted_tokens.add(token)
    session['captcha'] = ''
    return response({}, 20000, '退出成功'), 200


@user_blueprint.route('/protected/resource', methods=['GET'])
def protected_resource():
    token = request.headers.get("X-Token")

    if token in blacklisted_tokens:
        return response({}, 20001, 'Token已失效，请重新登录', False), 401

    # 处理受保护的资源
    # ...

    return response({'data': '受保护的资源'}, 20004, '成功'), 200


# 通过token获取用户信息
@user_blueprint.route('/user/info', methods=['GET'])
@login_required
def userInfo():
    token = request.args.get('token')
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = Admin.query.filter_by(id=data['id']).first()
        return response({
            "name": user.username,
            "avatar": user.avatar
        })
    except:
        return response({'message': 'Token is invalid!'}), 401


@user_blueprint.route('/user/nav', methods=['POST'])
def user_nav():
    user_id = 1
    userInfo = Admin.query.filter_by(id=user_id).first()

    # 通过关联查询出来觉得都有哪些菜单
    role_menus = db.session \
        .query(Menu.id, Menu.title, Menu.name, Menu.menuOrder, Menu.icon, Menu.fid) \
        .join(RoleMenus, (RoleMenus.menuId == Menu.id) & (RoleMenus.roleId == user_id)) \
        .all()

    # 转换数据成对象形式
    for i, menu in enumerate(role_menus):
        # 添加新属性，例如 'new_property'
        role_menus[i] = dict(zip(('id', 'title', 'name', 'menuOrder', 'icon', 'fid'), menu))

    # 获取 菜单的 id 列表
    menuIdList = [menu_dict['id'] for menu_dict in role_menus]

    # 通过角色ID 以及菜单ID 获取按钮的列表
    roleBtnList = RoleButtons.query \
        .filter(RoleButtons.roleId == 1, RoleButtons.menuId.in_(menuIdList)) \
        .all()

    for roleMenuIndex, roleMenuItem in enumerate(role_menus):
        role_menus[roleMenuIndex]['menubuttonList'] = []
        for roleBtnItem in roleBtnList:
            if role_menus[roleMenuIndex]['id'] == roleBtnItem.menuId:
                button_info = {"name": roleBtnItem.buttonName, "type": roleBtnItem.buttonType}
                role_menus[roleMenuIndex]['menubuttonList'].append(button_info)
    userInfo.menusList = role_menus
    return response({"data": userInfo.to_dict()})


# 登录验证码
@user_blueprint.route('/user/verificationcode', methods=['POST'])
def user_verify_cation_code():
    # 使用上述函数生成验证码图片
    image, captcha_text = generate_captcha_image()

    # 将验证码文本存储到session，以便之后进行验证
    session['captcha'] = captcha_text

    buf = io.BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue(), 200, {
        'Content-Type': 'image/png',
        'Content-Length': str(len(buf.getvalue()))
    }


def generate_captcha_image():
    # 将图片背景设置为白色
    image = Image.new('RGB', (95, 25), color=(255, 255, 255))

    # 生成5位数的验证码文本
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    # 设置文本颜色为黑色
    text_color = (0, 0, 0)

    # 调整文本位置
    text_position = (10, 5)

    # 获取当前脚本所在目录
    current_directory = os.path.dirname(os.path.realpath(__file__))
    # 拼接字体文件的路径
    font_path = os.path.join(current_directory, "arial.ttf")
    # 在这里指定字号
    text_font_size = 20
    # 使用Pillow的truetype方法加载字体
    font = ImageFont.truetype(font_path, text_font_size)
    # font_path = "./arial.ttf"

    # 使用Pillow的truetype方法加载字体
    # font = ImageFont.truetype(font_path, text_font_size)

    # 使用加载的字体绘制文本
    d = ImageDraw.Draw(image)
    d.text(text_position, captcha_text, font=font, fill=text_color)

    # 添加干扰线条和噪点
    for _ in range(random.randint(3, 5)):
        start = (random.randint(0, image.width), random.randint(0, image.height))
        end = (random.randint(0, image.width), random.randint(0, image.height))
        d.line([start, end], fill=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

    for _ in range(100):
        xy = (random.randrange(0, image.width), random.randrange(0, image.height))
        d.point(xy, fill=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

    return image, captcha_text
