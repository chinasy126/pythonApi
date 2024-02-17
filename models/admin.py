from config.exts import db
from datetime import datetime

from utils.utils import md5_hash


class Admin(db.Model):
    __tablename__ = 't_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    birthday = db.Column(db.DateTime, nullable=True)
    roleId = db.Column(db.Integer)
    createTime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updateTime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    avatar = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        if model_dict['updateTime']:
            model_dict['updateTime'] = model_dict['updateTime'].strftime("%Y-%m-%d")

        if model_dict['createTime']:
            model_dict['createTime'] = model_dict['createTime'].strftime("%Y-%m-%d")

        if model_dict['birthday']:
            model_dict['birthday'] = model_dict['birthday'].strftime("%Y-%m-%d")

        return model_dict

    # def to_dict(self):
    #     # 获取模型的所有列，并将它们包括在字典中
    #     columns_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns}
    #     return columns_dict

    def set_password(self, password):
        self.password = md5_hash(password)

    def check_password(self, password):
        return self.password == md5_hash(password)

    @classmethod
    def create_from_dict(cls, data):
        item = cls()
        for key, value in data.items():
            setattr(item, key, value)
        return item
