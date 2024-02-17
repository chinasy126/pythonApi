import uuid
import json
from flask import Blueprint
from models.roleMenus import *
from models.systemManagement import *
from models.admin import Admin
from utils.utils import *
from datetime import datetime

menu_blueprint = Blueprint("menu", __name__)


# 菜单列表
@menu_blueprint.route("/menu/menulist", methods=['POST'])
def menu_list_fn():
    current_page = request.args.get('currentPage', default=1, type=int)  # 获取页码，默认为第一页
    page_size = request.args.get('pageSize', default=10, type=int)  # 获取每页显示的数量，默认为10

    menus = Menu.query.order_by(Menu.menuOrder.desc(), Menu.id.asc()).all()
    buttons = MenuButton.query.all()
    menu_array = []
    # 主菜单
    for menu_item in menus:
        if menu_item.fid == 0:
            menu_button_list = []
            for btn_item in buttons:
                if menu_item.id == btn_item.menuId:
                    menu_button_list.append(btn_item)
            menu_item.menubuttonList = menu_button_list
            menu_array.append(menu_item.to_dict())

    # 子菜单
    menu_children_list = []
    for item in menus:
        if item.fid != 0:
            # S 子菜单按钮
            menubuttonList = []
            for btn_item in buttons:
                if item.id == btn_item.menuId:
                    menubuttonList.append(btn_item.to_dict())
            # 父级菜单按钮
            item.menubuttonList = menubuttonList
            menu_children_list.append(item.to_dict())

    for i, item in enumerate(menu_array):
        menu_child_list = []
        for iten_child in menu_children_list:
            if item['id'] == iten_child['fid']:
                menu_child_list.append(iten_child)
        menu_array[i]['children'] = menu_child_list
    total = Menu.query.count()

    return response({
        "data": {
            "current": current_page,
            "pages": (len(menu_array) + page_size - 1) // page_size,
            "records": menu_array,
            "size": page_size,
            "total": total
        }
    })


# 菜单一级分类
@menu_blueprint.route("/menu/category", methods=['POST'])
def menu_category():
    menu_list = Menu.query.order_by(Menu.menuOrder.desc(), Menu.id.asc()).filter(Menu.fid == 0).all()
    return response({
        "data": [menu_item.to_dict() for menu_item in menu_list]
    })


# 插入或者修改
@menu_blueprint.route("/menu/saveOrUpdate", methods=['POST'])
def menu_save_update():
    data = request.get_json()
    if 'id' in data:
        if data["id"] == "":
            menu_save(data)
        else:
            menu_update(data)
    else:
        menu_save(data)
    print(data)
    return response("success")


def parent_menu(data):
    menu_id = 0
    if data != "":
        param_arr = data.split(',')
        menu_item = Menu.query.filter(Menu.title == param_arr[0], Menu.name == param_arr[1]).first()
        menu_id = menu_item.id
    return menu_id


# 新增
def menu_save(data):
    menu_data = Menu(
        title=data['title'],
        name=data['name'],
        fid=parent_menu(data['parentMenu']) if data['parentMenu'] != "" else 0,
        button="",
        menuOrder=data['menuOrder'],
        icon=data['icon'] if 'icon' in data else ""
    )
    db.session.add(menu_data)
    db.session.commit()
    return data


# 修改菜单数据
def menu_update(data):
    menu_item = Menu.query.get(data["id"])
    menu_item.title = data['title']
    menu_item.name = data['name']
    menu_item.fid = parent_menu(data['parentMenu']) if data['parentMenu'] != "" else 0
    menu_item.menuOrder = data['menuOrder']
    menu_item.icon = data['icon'] if 'icon' in data else ""
    db.session.commit()
    return menu_item


@menu_blueprint.route("/menu/delete", methods=['DELETE'])
def menu_delete():
    data = request.get_json()
    Menu.query.filter(Menu.id == data["id"]).delete()
    Menu.query.filter(Menu.fid == data["id"]).delete()
    return response("success")


@menu_blueprint.route("/menu/batchdelete", methods=['DELETE'])
def menu_batch_delete():
    data = request.get_json()
    ids = data["ids"]
    for item_id in ids:
        Menu.query.filter(Menu.id == item_id).delete()
        Menu.query.filter(Menu.fid == item_id).delete()
    return response("success")


@menu_blueprint.route("/menubutton/indertBtn", methods=['POST'])
def menu_button_insert_btn():
    data = request.get_json()
    menu_item = MenuButton(
        id=int(str(uuid.uuid4().int)[:16]), menuId=data['menuId'], createTime='2023-01-02', updateTime='2023-01-02',
        type=data['type'], name=data['name']
    )
    db.session.add(menu_item)
    db.session.commit()
    return response(menu_item)


@menu_blueprint.route("/menubutton/delete", methods=['POST'])
def menu_button_delete():
    data = request.get_json()
    delete_id = data["id"]
    MenuButton.query.filter(MenuButton.id == delete_id).delete()
    return response("success")


# 菜单子菜单按钮
@menu_blueprint.route("/menu/multiclassclassification", methods=['POST'])
def menu_multiclass_classification():
    menu_list = Menu.query.order_by(Menu.id.asc()).all()
    menu_id_list = [item.id for item in menu_list]

    menu_btn_list = MenuButton.query.filter(MenuButton.menuId.in_(menu_id_list)).all()

    for index, item in enumerate(menu_list):
        menu_button_list = []
        for button in menu_btn_list:
            if item.id == button.menuId:
                menu_button_list.append(button.to_dict())
        if len(menu_button_list) != 0:
            menu_list[index].menubuttonList = menu_button_list

    first_level_menu = []
    secondary_menu = []
    for item in menu_list:
        if item.fid == 0 or item.fid == '':
            first_level_menu.append(item.to_dict())
        else:
            secondary_menu.append(item.to_dict())

    print(first_level_menu)
    print(secondary_menu)

    for index, item in enumerate(first_level_menu):
        children = []
        for menu_item in secondary_menu:
            if item['id'] == menu_item['fid']:
                children.append(menu_item)
        first_level_menu[index]['children'] = children

    return response({
        "data": first_level_menu
    })
