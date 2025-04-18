from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config


db = SQLAlchemy()


class User(db.Model):
    # 数据表明、字段
    __tablename__ = 'qgz_user'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    head = db.Column(db.String(100))
    nickName = db.Column(db.String(100))
    status = db.Column(db.Date)

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)




# # 获取表结构并打印
# def get_tables_info(app, db):
#     with app.app_context():  # 进入 app 上下文
#         inspector = inspect(db.engine)
#         tables = inspector.get_table_names()
#
#         result = []
#         for table in tables:
#             columns = inspector.get_columns(table)
#             col_info = [f"{col['name']} ({col['type']})" for col in columns]
#             result.append(f"{table}: {', '.join(col_info)}")
#
#         for line in result:
#             print(line)


if __name__ == '__main__':
    with app.app_context():  # 进入应用上下文
        db.create_all()  # 创建表格
    app.run(host='0.0.0.0',port=5001, debug=True)
