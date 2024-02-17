from flask import jsonify, request, session
from sqlalchemy.orm import DeclarativeMeta
# 创建一个 Blueprint 对象

from datetime import datetime, timedelta
from functools import wraps
import jwt
import hashlib

SECRET_KEY = 'thisissecret'

# 白名单路由列表
no_login_required_routes = [
    '/user/login',
    '/user/verificationcode',
    "/user/resetToken",
    "/apidocs/",
    "/aaa"
]


# 返回数据
def response(data=None, code=20000, message='', success=True):
    """
    自定义返回结果的封装函数
    :param code: 状态码，默认为 200
    :param message: 提示信息，默认为空字符串
    :param data: 返回数据，默认为 None
    :return: Response 对象
    """
    response_data = {
        'code': code,
        'message': message,
        'data': None,
        'success': success
    }
    try:
        response_data['data'] = serialize(data)
        return jsonify(response_data)
    except SerializationError as e:
        response_data['code'] = e.code
        response_data['message'] = e.message
        return jsonify(response_data)


def serialize(obj):
    """
    将对象转换为可以序列化为JSON的数据类型
    :param obj: 待转换的对象
    :return: 转换后的数据类型
    """
    if obj is None:
        return None
    try:
        # 如果对象本身就是可以序列化为JSON的类型，则直接返回
        if isinstance(obj, (str, int, float, bool, list, tuple, dict)):
            return obj
        # 如果对象是ORM对象，则将其转换为字典并返回
        elif isinstance(obj.__class__, DeclarativeMeta):
            # return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            serialized_obj = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            # 动态获取对象的属性字典
            additional_attributes = obj.__dict__
            # 过滤掉不需要的属性，比如系统生成的属性
            additional_attributes = {k: v for k, v in additional_attributes.items() if not k.startswith('_')}
            serialized_obj.update(additional_attributes)
            return serialized_obj
        # 如果对象实现了__dict__方法，则将其转换为字典并返回
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        # 如果对象是其他类型，则抛出异常
        else:
            raise SerializationError(code=500, message='Cannot serialize object')
    except Exception as e:
        raise SerializationError(code=500, message=str(e))


class SerializationError(Exception):
    """
    自定义的异常类，用于处理序列化错误
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message


def before_reset_token_request(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # 添加你需要的逻辑，比如验证 token、刷新 token 等
        # ...

        return f(*args, **kwargs)

    return wrapper


# 检验token是否合法
# @app.before_request
def login_required(f):
    """
    登陆保护，验证用户是否登陆
    :param f:
    :return:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        # 50008：非法令牌； 50012：其他客户端已登录；50014：令牌已过期。
        if request.path and "public" not in request.path and request.path not in no_login_required_routes:
            token = request.headers.get("X-Token", default=None)
            if not token:
                return response("非法令牌", 50008)
            userId = identify(token)
            if not userId:
                return response("其他客户端已登录", 50012)
            else:
                session["user_id"] = userId
            # 获取到用户并写入到session中,方便后续使用
            return f(*args, **kwargs)

    return wrapper


# 识别token 解析token 返回
def identify(auth_header: str):
    # 用户鉴权

    if auth_header:
        payload = decode_auth_token(auth_header)
        if not payload:
            return False
        if "id" in payload:
            return payload['id']
        else:
            return False
    else:
        return False


# 解析token
def decode_auth_token(token: str):
    try:
        # 取消过期时间验证
        # payload = jwt.decode(token, key, options={'verify_exp': False})
        payload = jwt.decode(token, 'thisissecret', algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.InvalidSignatureError):
        return ""
    else:
        return payload


def getUserInfoByToken():
    auth_header = request.headers.get("X-Token", default=None)
    if auth_header:
        payload = decode_auth_token(auth_header)
        if not payload:
            return False
        if "id" in payload:
            return payload
        else:
            return False
    else:
        return False


# 密码MD5加密
def md5_hash(password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    return md5.hexdigest()


def conversion_date(data_time):
    date_time = ''
    if not is_empty(data_time):
        year = data_time.year
        month = data_time.month
        day = data_time.day
        date_time = f"{year}-{month}-{day}"
    return date_time


def is_empty(value):
    if value is None:
        return True
    elif isinstance(value, str) and value == '':
        return True
    elif isinstance(value, (list, dict, set, tuple)) and not value:
        return True
    elif hasattr(value, 'is_empty') and callable(getattr(value, 'is_empty')):
        return value.is_empty()
    else:
        return False


def get_current_year_mounth_day():
    # 获取当前日期和时间
    current_datetime = datetime.now()

    # 获取年、月、日
    current_year = current_datetime.year
    current_month = current_datetime.month
    current_day = current_datetime.day
    return f"{current_year}{current_month}{current_day}"


# power加1
def increment_classpower(classpower_str):
    # 将字符串形式的classpower转换为整数，进行加一操作
    classpower_int = int(classpower_str) + 1
    # 将新的classpower转换为字符串，并左侧填充零，保持固定长度
    new_classpower_str = str(classpower_int).zfill(len(classpower_str))
    return new_classpower_str
