# 图片上传
import os
import uuid
from models.news import News
from flask import Blueprint
from utils.utils import *
from config.exts import db
from datetime import datetime
import os
import hashlib

# 创建一个 Blueprint 对象
upload_blueprint = Blueprint('upload', __name__)

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 生成文件路径
def get_current_file_path(file_name=''):
    if file_name != '':
        file_name = f'{file_name}/'
    # 获取当前日期和时间
    current_datetime = datetime.now()
    # 获取当前年份
    current_year = current_datetime.year
    # 获取当前月份
    current_month = current_datetime.month

    # 获取当前脚本所在目录
    current_directory = os.path.dirname(os.path.realpath(__file__))
    # 项目根目录为当前目录的上一级
    project_root = os.path.abspath(os.path.join(current_directory, os.pardir))
    # 拼接上传文件夹路径
    upload_path = f'public/{file_name}{current_year}{current_month}/'
    upload_folder = os.path.join(project_root, upload_path)
    os.makedirs(upload_folder, exist_ok=True)
    return [upload_folder, upload_path]


# 图片上传
@upload_blueprint.route("/upload/pictures", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return response('error')
    # 获取上传文件
    file = request.files['file']
    # 获取当前文件夹上传路径
    upload_folder = get_current_file_path()[0]
    upload_path = get_current_file_path()[1]
    # 是否允许文件上传类型
    if file and allowed_file(file.filename):
        # 使用 uuid 生成唯一的文件名
        unique_filename = str(uuid.uuid4())
        # 获取文件扩展名
        _, file_extension = os.path.splitext(file.filename)
        # 拼接完整的文件名
        filename = os.path.join(upload_folder, f'{unique_filename}{file_extension}')
        # filename = os.path.join(upload_folder, file.filename)
        file.save(filename)
        return response({
            "file": f'/{upload_path}{unique_filename}{file_extension}'
        })
    else:
        return response('error')
