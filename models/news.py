from config.exts import db
from datetime import datetime
from utils.utils import conversion_date


class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), comment='标题')
    fTitle = db.Column(db.String(400), comment='副标题')
    pic = db.Column(db.String(255), comment='图片')
    s_pic = db.Column(db.String(70), comment='缩略图')
    contents = db.Column(db.Text, comment='内容')
    update = db.Column(nullable=False, default=datetime.utcnow, comment='时间')
    num = db.Column(db.Integer, nullable=False, server_default=db.text("'0'"), comment='点击数')
    top = db.Column(db.Integer, nullable=False, server_default=db.text("'0'"), comment='推荐值')
    author = db.Column(db.String(30), comment='作者')
    webtitle = db.Column(db.String(80), comment='网页标题')
    webkey = db.Column(db.String(160), comment='网页关键词')
    webdes = db.Column(db.String(200), comment='网页描述')

    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        model_dict["update"] = conversion_date(model_dict["update"])
        return model_dict

    @classmethod
    def create_from_dict(cls, data):
        item = cls()
        for key, value in data.items():
            setattr(item, key, value)
        return item
