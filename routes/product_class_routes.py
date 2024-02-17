import uuid
from models.news import News
from flask import Blueprint
from utils.utils import *
from config.exts import db
from datetime import datetime
import os
import hashlib
import pandas as pd
from io import BytesIO
from flask import Response
from sqlalchemy import func, case
from models.product import ProductClass, Product
from sqlalchemy import text

product_class_blueprint = Blueprint("productclass", __name__)

POWER = '0000'


# 新增分类
@product_class_blueprint.route("/productclass/insert", methods=['POST'])
def product_class_insert():
    data = request.get_json()
    # 如果为空则一级分类，否则二级分类

    power_depth_rootid = get_power_depth_rootid(data)

    # if data['rootid'] == '':
    #     classpwoer = POWER + 1
    #     depth = len(classpwoer)
    #     rootid = 0
    print(power_depth_rootid)
    item_add = ProductClass(
        rootid=power_depth_rootid['rootid'],
        classpower=power_depth_rootid['classpower'],
        depth=power_depth_rootid['depth'],
        classname=data["classname"],
        classcontents=data["classcontents"],
        classpic=data["classpic"]
    )
    db.session.add(item_add)
    item_result = db.session.commit()
    return response(item_result)


def get_power_depth_rootid(data):
    root_id = 0
    depth = len(POWER)
    # 如果是一级分类
    if data['rootid'] == "":
        # 先查询最大位数
        max_class_power = ProductClass.query.filter(ProductClass.depth == 4).order_by(
            ProductClass.classpower.desc()).first()
        if max_class_power:
            # 获取当前classpower的值
            current_classpower = max_class_power.classpower
            new_classpower = int(current_classpower) + 1
            new_classpower_str = f"{new_classpower:04d}"
        else:
            current_classpower = POWER
            new_classpower = int(current_classpower) + 1
            new_classpower_str = f"{new_classpower:04d}"
        root_id = 0
        depth = len(new_classpower_str)
    else:
        # 不是一级分类
        class_item = ProductClass.query.filter(ProductClass.classid == data["rootid"]).first()
        # 查询最大的 power
        max_class_power = ProductClass.query.filter(ProductClass.depth == len(class_item.classpower) + len(POWER),
                                                    ProductClass.rootid == class_item.classid).order_by(
            ProductClass.classpower.desc()).first()

        # 如果已经存在了分类
        if max_class_power:
            # 获取当前classpower的值
            current_classpower = max_class_power.classpower
            new_classpower_str = increment_classpower(current_classpower)

        else:
            new_classpower_str = class_item.classpower + increment_classpower(POWER)
        root_id = class_item.classid
        depth = len(new_classpower_str)
    return {
        "rootid": root_id,
        "classpower": new_classpower_str,
        "depth": depth
    }


# 删除分类
@product_class_blueprint.route("/productclass/delete", methods=['DELETE'])
def product_class_delete():
    data = request.get_json()
    delete_id = data["classid"]
    class_item = ProductClass.query.filter(ProductClass.classid == delete_id).first()
    class_result = 0
    if class_item:
        class_result = ProductClass.query.filter(ProductClass.classpower.like(f"{class_item.classpower}%")).delete()
    return response(class_result)

# 分类修改
@product_class_blueprint.route("/productclass/modify", methods=['POST'])
def product_class_modify():
    data = request.get_json()
    # {"classid": 2, "rootid": 1, "classname": "第一个人类小分类", "classcontents": "aaasdfadsfadsf", "classpic": ""}

    class_item = ProductClass.query.filter(ProductClass.classid == data["classid"]).first()
    if class_item.rootid == data["rootid"] or (class_item.rootid == 0 and data["rootid"] == ""):
        # 没修改分类
        class_item.classname = data["classname"]
        class_item.classcontents = data["classcontents"]
        class_item.classpic = data["classpic"]
        db.session.commit()
    else:
        power_item = get_power_depth_rootid(data)
        subclass_list = ProductClass.query.filter(ProductClass.classpower.like(f"{class_item.classpower}%"),
                                                  ProductClass.depth != len(class_item.classpower)).all()

        root_class_power = power_item["classpower"]
        for subclass_item in subclass_list:
            num = class_item.depth - subclass_item.depth
            subclass_item.classpower = root_class_power + subclass_item.classpower[num:]
            subclass_item.depth = len(subclass_item.classpower)
            print(subclass_item)
            db.session.commit()

        class_item.classpower = power_item["classpower"]
        class_item.classname = data["classname"]
        class_item.depth = power_item["depth"]
        class_item.rootid = power_item["rootid"]
        class_item.classcontents = data["classcontents"]
        class_item.classpic = data["classpic"]
        db.session.commit()

    return response("修改成功!")


# 产品分类列表
@product_class_blueprint.route("/productclass/list", methods=['POST'])
def product_class_list():
    data = request.get_json()
    current_page = request.args.get('currentPage', default=1, type=int)
    page_size = request.args.get("pageSize", default=10, type=int)
    # 计算当前页数
    offset = (current_page - 1) * page_size

    query = db.session.query(ProductClass)
    for key, value in data.items():
        if value is not None:
            if key == "classname" or key == "classcontents":
                query = query.filter(getattr(ProductClass, key).like(f"%{value}%"))
    # 计算总数
    total = query.count()
    # 计算列表数量
    query = query.order_by(ProductClass.classpower.asc()).offset(offset).limit(page_size)
    data_list = query.all()

    return response({"data": {
        "current": current_page,
        "pages": (total + current_page - 1) // page_size,
        "records": [item.to_dict() for item in data_list],
        "size": page_size,
        "total": total
    }})


# 获取分类列表
@product_class_blueprint.route("/productclass/category", methods=['POST'])
def product_class_category():
    data_list = ProductClass.query.order_by(
        ProductClass.classpower.asc()).all()
    return response({
        "data": [item.to_dict() for item in data_list]
    })


# 产品管理
@product_class_blueprint.route("/product/list", methods=['POST'])
def product_list():
    current_page = request.args.get("currentPage", default=1, type=int)
    page_size = request.args.get("pageSize", default=10, type=int)
    data = request.get_json()

    # get_product_list(current_page, page_size, data)

    # query = db.session.query(Product, ProductClass).join(ProductClass, Product.pid == ProductClass.classid)
    if 'name' in data:
        query = db.session.query(Product, ProductClass).outerjoin(ProductClass, Product.pid == ProductClass.classid)
        records_list = (query.filter(Product.name.like(f"%{data['name']}%")).all())
        total = query.filter(Product.name.like(f"%{data['name']}%")).count()
    else:
        query = db.session.query(Product, ProductClass).outerjoin(ProductClass, Product.pid == ProductClass.classid)
        records_list = (query.all())
        total = query.count()

    result_list = []
    for product, product_class in records_list:
        print(product)
        print(product_class)
        result_list.append({
            "id": product.id,
            "classname": product_class.classname if product_class is not None else "",
            "name": product.name,
            "pic": product.pic
        })

    return response({
        "data": {
            "size": page_size,
            "current": current_page,
            "pages": (total + page_size - 1) // page_size,
            "records": result_list,
            "total": total
        }
    })


def get_product_list(current_page, page_size, data):
    # 使用 text 函数明确声明 SQL 表达式
    sql_query = text('SELECT * FROM news')
    # 执行 SQL 查询，并将结果转为字典列表
    result = db.session.execute(sql_query)
    records_list = result.fetchall()
    print(records_list)
    return []


# 删除产品
@product_class_blueprint.route("/product/delete", methods=['DELETE'])
def product_delete():
    data = request.get_json()
    delete_result = ''
    if 'id' in data:
        delete_result = Product.query.filter(Product.id == data["id"]).delete()
    return response(delete_result)


# 产品维护
@product_class_blueprint.route("/product/saveOrUpdate", methods=['POST'])
def product_save_update():
    data = request.get_json()
    result = ''
    if data["id"] == '':
        result = product_save(data)
    else:
        result = product_update(data)
    return response(result)


# 新增产品
def product_save(data):
    del data['id']
    data_item = Product.create_from_dict(data)
    db.session.add(data_item)
    db.session.commit()
    return data_item


# 更新产品
def product_update(data):
    item = Product.query.filter(Product.id == data['id']).first()
    item.name = data['name']
    item.contents = data['contents']
    item.num = data['num']
    item.pic = data['pic']
    item.pid = data['pid']
    item.top = data['top']
    db.session.commit()
    return item
