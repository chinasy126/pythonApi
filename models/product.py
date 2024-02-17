from config.exts import db
from datetime import datetime
from utils.utils import conversion_date


class ProductClass(db.Model):
    __tablename__ = 'productclass'
    classid = db.Column(db.Integer, primary_key=True)
    classname = db.Column(db.String(50), comment='分类名称')
    classpower = db.Column(db.String(100), comment='分类编码')
    depth = db.Column(db.Integer, comment='分类深度')
    rootid = db.Column(db.Integer, comment='分类根')
    classcontents = db.Column(db.String(500), comment='内容')
    classpic = db.Column(db.String(255), comment='分类图片')

    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    @classmethod
    def create_from_dict(cls, data):
        item = cls()
        for key, value in data.items():
            setattr(item, key, value)
        return item


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(50), comment='分类ID')
    name = db.Column(db.String(100), comment='产品名称')
    title = db.Column(db.String(100), comment='产品副标题')
    pic = db.Column(db.String(255), comment='产品图图片')
    contents = db.Column(db.Text, comment='产品内容')
    num = db.Column(db.Integer, comment='产品点击数')
    top = db.Column(db.Integer, comment='产品推荐值')
    update = db.Column(db.Integer, comment='产品更新时间')
    author = db.Column(db.String(30), comment='文章作者')
    webtitle = db.Column(db.String(80))
    webkey = db.Column(db.String(160))
    webdes = db.Column(db.String(200))

    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    @classmethod
    def create_from_dict(cls, data):
        item = cls()
        for key, value in data.items():
            setattr(item, key, value)
        return item
