from config.exts import db
from datetime import datetime

# 角色表
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    roleName = db.Column(db.String(255), nullable=False)
    roleDesc = db.Column(db.String(255), nullable=False)
    roleMenus = db.Column(db.Text, nullable=False)

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

# 用户表

# 菜单表
