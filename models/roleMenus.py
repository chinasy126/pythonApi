from config.exts import db
from datetime import datetime
from utils.utils import conversion_date

class RoleMenus(db.Model):
    __tablename__ = 'rolemenus'
    id = db.Column(db.Integer, primary_key=True)
    roleId = db.Column(db.Integer, nullable=True)
    menuId = db.Column(db.Integer, nullable=True)
    menuTitle = db.Column(db.String(255), nullable=False)
    menuButton = db.Column(db.String(255), nullable=False)

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


class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    fid = db.Column(db.Integer, nullable=True)
    button = db.Column(db.String(255), nullable=False)
    menuOrder = db.Column(db.Integer, nullable=True)
    icon = db.Column(db.String(255), nullable=False)

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


class MenuButton(db.Model):
    __tablename__ = 'menubutton'
    id = db.Column(db.Integer, primary_key=True)
    menuId = db.Column(db.Integer, nullable=False)
    createTime = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    updateTime = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    type = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        model_dict = dict(self.__dict__)
        model_dict["createTime"] = conversion_date(model_dict["createTime"])
        model_dict["updateTime"] = conversion_date(model_dict["updateTime"])
        del model_dict['_sa_instance_state']
        return model_dict

    @classmethod
    def create_from_dict(cls, data):
        item = cls()
        for key, value in data.items():
            setattr(item, key, value)
        return item


class RoleButtons(db.Model):
    __tablename__ = 'rolebuttons'
    id = db.Column(db.BigInteger, primary_key=True)
    roleMenuId = db.Column(db.BigInteger, nullable=True)
    buttonName = db.Column(db.String(255), nullable=True)
    buttonType = db.Column(db.String(255), nullable=True)
    roleId = db.Column(db.Integer, nullable=True)
    menuId = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @classmethod
    def create_from_dict(cls, data):
        item = cls()
        for key, value in data.items():
            setattr(item, key, value)
        return item
