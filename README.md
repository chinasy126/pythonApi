执行
1、python3 -m venv venv
2、source venv/bin/activate
安装依赖
3、pip install -r requirements.txt

导出依赖
4、pip freeze > requirements.txt


windows 环境
虚拟环境 >python -m venv venv

导出依赖
pip freeze > requirements.txt

安装依赖
pip install -r requirements.txt

pip install sqlacodegen
sqlacodegen mysql+pymysql://root:root@127.0.0.1:3306/mybook --tables news --outfile news.py

.\activate 