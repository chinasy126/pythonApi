import uuid

from flask import Blueprint
from models.roleMenus import *
from models.systemManagement import *
from models.admin import Admin
from utils.utils import *

# 创建一个 Blueprint 对象
admin_blueprint = Blueprint('admin', __name__)


# 管理员数据插入
@admin_blueprint.route('/user/insert', methods=['POST'])
def admin_insert():
    data = request.get_json()
    admin = Admin.query.filter(Admin.username == data["username"]).first()
    msg = "用户名已存在!"
    code = 20000
    s = True
    if admin is None:
        admin_item = Admin.create_from_dict(data)
        admin_item.set_password(data['password'])
        db.session.add(admin_item)
        db.session.commit()
        msg = "success"
    elif admin is not None:
        code = 20001
        msg = "用户名已存在!"
        s = False
    return response([], code, msg, s)


# 数据列表
@admin_blueprint.route("/user/list", methods=["POST"])
def admin_list():
    current_page = request.args.get('currentPage', default=1, type=int)
    page_size = request.args.get('pageSize', default=10, type=int)
    offset = (current_page - 1) * page_size

    admin_list = Admin.query.order_by(Admin.id.desc()).offset(offset).limit(page_size).all()
    total = Admin.query.count()
    # 获取角色ID 过滤重复的
    admin_ids = list(set([admin_item.roleId for admin_item in admin_list]))
    role_list = Role.query.filter(Role.id.in_(admin_ids)).all()

    for admin_index, admin_item in enumerate(admin_list):
        for role_item in role_list:
            if admin_item.roleId == role_item.id:
                admin_list[admin_index].roleName = role_item.roleName

    return response({"data": {
        "current": current_page,
        "pages": (total + page_size - 1) // page_size,
        "records": [admin_item.to_dict() for admin_item in admin_list],
        "size": page_size,
        "total": total
    }})


# 角色管理-用户删除

# 删除用户
@admin_blueprint.route("/user/delete", methods=["delete"])
def admin_delete():
    data = request.get_json()
    delete_id = data['id']
    admin_del = Admin.query.filter(Admin.id == delete_id).delete()
    return response(admin_del)


# 用户修改信息
@admin_blueprint.route("/user/modify", methods=['POST'])
def user_modify():
    data = request.get_json()
    print(data)
    admin_item = Admin.query.get_or_404(data["id"])
    if "password" in data:
        admin_item.password = md5_hash(data["password"])
    else:
        for key, value in data.items():
            if hasattr(admin_item, key):
                setattr(admin_item, key, value)
    db.session.commit()
    return response(admin_item)


@admin_blueprint.route("/user/batchdelete", methods=['POST'])
def user_batchdelete():
    data = request.get_json()
    if len(data) != 0:
        try:
            Admin.query.filter(Admin.id.in_(data)).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
    return response("用户删除成功!")
