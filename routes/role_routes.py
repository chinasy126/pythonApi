import uuid

from flask import Blueprint
from models.roleMenus import *
from models.systemManagement import *
from utils.utils import *

# 创建一个 Blueprint 对象
role_blueprint = Blueprint('role', __name__)


@role_blueprint.route('/role/list', methods=['POST'])
def role_list():
    data = request.get_json()

    page = request.args.get('currentPage', default=1, type=int)  # 获取页码，默认为第一页
    page_size = request.args.get('pageSize', default=10, type=int)  # 获取每页显示的数量，默认为10
    # 计算偏移量，用于指定从哪一条记录开始
    offset = (page - 1) * page_size

    query = db.session.query(Role)

    # 查询数据库，获取用户列表，并进行分页
    if 'roleName' in data:
        roles = query.filter(Role.roleName.like(f"%{data['roleName']}%")).order_by(Role.id.desc()).offset(
            offset).limit(page_size).all()
        total = query.filter(Role.roleName.like(f"%{data['roleName']}%")).count()
    else:
        roles = Role.query.order_by(Role.id.desc()).offset(offset).limit(page_size).all()
        total = Role.query.count()
    role_ids = [item.id for item in roles]
    role_menu_list = RoleMenus.query.filter(RoleMenus.roleId.in_(role_ids)).all()
    # 查询

    # 查询菜单
    menu_id_array = [item.menuId for item in role_menu_list]
    menu_array = Menu.query.filter(Menu.id.in_(menu_id_array)).all()

    for role_menu_index, role_menu_item in enumerate(role_menu_list):
        for menu_item in menu_array:
            if menu_item.id == role_menu_item.menuId:
                role_menu_list[role_menu_index].menuFid = menu_item.fid

    # 角色菜单的ID列表
    role_menu_ids = [item.id for item in role_menu_list]

    # 查询按钮列表
    role_btn_list = RoleButtons.query.filter(RoleButtons.roleMenuId.in_(role_menu_ids)).all()

    for role_index, role_menu in enumerate(role_menu_list):
        role_menu_list[role_index].rolebuttonsList = []
        for role_btn in role_btn_list:
            if role_menu_list[role_index].id == role_btn.roleMenuId:
                button_info = {
                    "buttonName": role_btn.buttonName,
                    "buttonType": role_btn.buttonType,
                    "id": role_btn.id,
                    "roleMenuId": role_btn.roleMenuId
                }
                role_menu_list[role_index].rolebuttonsList.append(button_info)

    for role_index, role_item in enumerate(roles):
        roles[role_index].roleMenus = []
        for role_menu_item in role_menu_list:
            if roles[role_index].id == role_menu_item.roleId:
                roles[role_index].roleMenus.append(role_menu_item.to_dict())

    return response({"data": {
        "records": [item.to_dict() for item in roles],
        "current": page,
        "pages": (total + page_size - 1) // page_size,
        "size": page_size,
        "total": total
    }})


@role_blueprint.route('/role/delete', methods=['DELETE'])
def role_delete():
    data = request.get_json()
    role_id = data["id"]

    try:
        # 1、删除角色
        Role.query.filter(Role.id == role_id).delete()
        # 2、删除角色菜单
        RoleMenus.query.filter(RoleMenus.roleId == role_id).delete()
        # 3、删除角色按钮
        RoleButtons.query.filter(RoleButtons.roleId == role_id).delete()
        return response('ok')
    except:
        return response({'message': 'id is invalid!'}), 401


@role_blueprint.route('/role/insert', methods=['POST'])
def role_insert():
    data = request.get_json()

    # 新增角色
    role_menus = data['roleMenus']
    data['roleMenus'] = ''
    if data['id'] == '':
        del data['id']
    role_item = Role.create_from_dict(data)
    db.session.add(role_item)
    db.session.commit()

    print(role_menus)
    # 通过角色新增菜单
    for role_Item in role_menus:
        print(role_Item)
        role_Item["roleId"] = role_item.id

        role_buttons_list = role_Item['rolebuttonsList']
        role_Item['rolebuttonsList'] = ''

        role_menu_item = RoleMenus.create_from_dict(role_Item)
        db.session.add(role_menu_item)
        db.session.commit()

        # 是否存在按钮
        if len(role_buttons_list) != 0:
            # 通过菜单新增按钮
            for role_btn_item in role_buttons_list:
                role_btn_item['roleMenuId'] = role_menu_item.id
                role_btn_item['roleId'] = role_item.id
                role_btn_item['menuId'] = role_Item["menuId"]
                role_btn = RoleButtons.create_from_dict(role_btn_item)
                db.session.add(role_btn)
                db.session.commit()
    return response("ok")


@role_blueprint.route("/role/modify", methods=['POST'])
def role_modify():
    data = request.get_json()

    # 修改角色
    role_item = Role.query.get(data["id"])

    role_menus = data["roleMenus"]
    del data["roleMenus"]

    # 修改角色个人信息
    if role_item:
        for key, value in data.items():
            if hasattr(role_item, key):
                setattr(role_item, key, value)
        db.session.commit()

    # 修改菜单信息
    # 第一步先查询
    role_menu_list = RoleMenus.query.filter(RoleMenus.roleId == data["id"]).all()
    # 第二步循环比较，如果存在不变化，没有则删除
    # 循环数据库查询的菜单
    for role_menu_item in role_menu_list:
        role_menu_exist = False
        # 循环接口的菜单
        for menu in role_menus:
            if role_menu_item.menuId == int(menu['menuId']):
                role_menu_exist = True
                # 接下来操作按钮
                role_btn_list = RoleButtons.query.filter(RoleButtons.roleId == data['id'],
                                                         RoleButtons.roleMenuId == role_menu_item.id).all()
                # 数据库查询的按钮
                for btn_item in role_btn_list:
                    role_btn_exist = False
                    # 循环接口的按钮
                    for role_btn_item in menu['rolebuttonsList']:
                        if btn_item.buttonType == role_btn_item['buttonType']:
                            role_btn_exist = True
                    if not role_btn_exist:
                        # 删除按钮
                        RoleButtons.query.filter(RoleButtons.id == btn_item.id).delete()

        if not role_menu_exist:
            RoleMenus.query.filter(RoleMenus.id == role_menu_item.id).delete()
            RoleButtons.query.filter(RoleButtons.roleMenuId == role_menu_item.id,
                                     RoleButtons.roleMenuId == role_menu_item.id).delete()

    role_menu_list = RoleMenus.query.filter(RoleMenus.roleId == data["id"]).all()
    # 没有的菜单进行新增
    # 没有按钮进行增加
    # 循环接口的菜单
    for menu in role_menus:
        menu_exist = False
        for role_menu_item in role_menu_list:
            if int(menu['menuId']) == role_menu_item.menuId:
                menu_exist = True
                if len(menu['rolebuttonsList']) != 0:
                    role_btn_list = RoleButtons.query.filter(RoleButtons.roleId == 4).all()
                    for btn_item in menu['rolebuttonsList']:
                        btn_exist = False
                        for role_btn_item in role_btn_list:
                            if btn_item['buttonType'] == role_btn_item.buttonType:
                                btn_exist = True
                        if not btn_exist:
                            # 添加按钮
                            btn_item['id'] = int(str(uuid.uuid4().int)[:16])
                            btn_item['roleMenuId'] = role_menu_item.id
                            btn_item['roleId'] = data['id']
                            btn_item['menuId'] = menu['menuId']
                            btn_item_add = RoleButtons.create_from_dict(btn_item)
                            db.session.add(btn_item_add)
                            db.session.commit()

        if not menu_exist:
            # 添加菜单
            menu['roleId'] = data["id"]
            menu_item_add = RoleMenus.create_from_dict(menu)
            db.session.add(menu_item_add)
            db.session.commit()

            if len(menu['rolebuttonsList']) != 0:
                for btn_item in menu['rolebuttonsList']:
                    btn_item['roleMenuId'] = menu_item_add.id
                    btn_item['roleId'] = data['id']
                    btn_item['menuId'] = menu['menuId']
                    btn_item_add = RoleButtons.create_from_dict(btn_item)
                    db.session.add(btn_item_add)
                    db.session.commit()

    print(role_menu_list)
    print(role_menus)

    return {}


@role_blueprint.route("/role/rolelist", methods=['POST'])
def role_role_list():
    roles = Role.query.order_by(Role.id.asc()).all()
    return response({
        "data": [item.to_dict() for item in roles]
    })
