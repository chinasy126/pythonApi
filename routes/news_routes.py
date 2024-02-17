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

# 创建一个 Blueprint 对象
news_blueprint = Blueprint('news', __name__)


# 新闻列表
@news_blueprint.route("/news/list", methods=['POST'])
def news_list_s():
    current_page = request.args.get('currentPage', default=1, type=int)
    page_size = request.args.get('pageSize', default=10, type=int)

    data = request.get_json()
    query = db.session.query(News)
    offset = (current_page - 1) * page_size
    for key, value in data.items():
        if value is not None:
            if key == 'title':
                query = query.filter(getattr(News, key).ilike(f"%{value}%"))
            else:
                query = query.filter(getattr(News, key) == value)
    news_list = query.offset(offset).limit(page_size).all()
    total = query.count()
    return response({
        "data": {
            "current": current_page,
            "pages": (total + page_size - 1) // page_size,
            "records": [item.to_dict() for item in news_list],
            "size": page_size,
            "total": total,
        }
    })


# 插入修改
@news_blueprint.route("/news/saveOrUpdate", methods=['POST'])
def news_save_update():
    data = request.get_json()

    if 'id' in data:
        if data['id'] == '':
            del data['id']
            news_result = news_save(data)
        else:
            news_result = news_update(data)
    else:
        news_result = news_save(data)
    return response(news_result)


# 新增新闻
def news_save(data):
    news_item = News.create_from_dict(data)
    db.session.add(news_item)
    db.session.commit()
    return news_item


# 修改新闻
def news_update(data):
    news_item = News.query.filter(News.id == data['id']).first()
    news_item.title = data['title']
    news_item.fTitle = data['fTitle']
    news_item.update = data['update']
    news_item.top = data['top']
    news_item.num = data['num']
    news_item.pic = data['pic']
    news_item.contents = data['contents']
    db.session.commit()
    return 'ok'


# 删除新闻
@news_blueprint.route("/news/delete", methods=['DELETE'])
def news_delete():
    data = request.get_json()
    delete_id = data['id']
    news_del = News.query.filter(News.id == delete_id).delete()
    return response(news_del)


# 批量删除
@news_blueprint.route("/news/batchDelete", methods=['DELETE'])
def news_batch_delete():
    data = request.get_json()
    print(data)
    delete_item = News.query.filter(News.id.in_(data['id'])).delete()
    return response(delete_item)


@news_blueprint.route("/news/import", methods=['POST'])
def news_import():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.files['file']

        # Check if the file exists and is an Excel file
        if uploaded_file and uploaded_file.filename.endswith('.xlsx'):
            # Read the uploaded file using pandas
            df = pd.read_excel(uploaded_file)
            for index, row in df.iterrows():
                news_item = News(
                    title=row.values[0],
                    fTitle=row.values[4],
                    pic=str(row.values[1]).replace('nan', ''),
                    top=row.values[2],
                    update=row.values[3],
                    num=0,
                    author='a',
                    webtitle='adfs',
                    webkey='adsf',
                    webdes='adsf'
                )
                db.session.add(news_item)
                db.session.commit()
            # Process the data
    return response("数据导入成功!")


# 导出Excel
@news_blueprint.route("/news/export", methods=['POST'])
def news_export():
    param = request.get_json()
    # 创建一个示例数据框
    query = db.session.query(News)
    if len(param['id']) != 0:
        query = query.filter(News.id.in_(param['id']))
    else:
        query = query

    news_list = query.all()
    print(news_list)
    data = {"标题": [], '副标题': [], '图片': [], '日期': [], '点击量': [], '推荐值': []}
    for news_item in news_list:
        data['标题'].append(news_item.title)
        data['副标题'].append(news_item.fTitle)
        data['图片'].append(news_item.pic)
        data['日期'].append(news_item.update)
        data['点击量'].append(news_item.num)
        data['推荐值'].append(news_item.top)

    # data = {'Name': ['Alice', 'Bob', 'Charlie'],
    #         'Age': [25, 30, 35],
    #         'City': ['New York', 'San Francisco', 'Los Angeles']}

    df = pd.DataFrame(data)

    # 将数据框写入 BytesIO 对象
    excel_data = BytesIO()
    # df.to_csv(excel_data, index=False)
    df.to_excel(excel_data, index=False)
    # 获取二进制数据
    binary_data = excel_data.getvalue()

    # 关闭 BytesIO 对象
    excel_data.close()
    # 创建 Flask Response 对象，将二进制数据作为响应内容
    result = Response(binary_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    result.headers["Content-Disposition"] = "attachment; filename=news.xlsx"
    return result

    # # 将数据框写入 Excel 文件
    # excel_file_path = 'example.xlsx'
    # df.to_excel(excel_file_path, index=False)
    # return response("")
