import json
import os

from flask import Flask, jsonify
from flask_cors import CORS
# 导入蓝图
from Apps.lesson_plan import lesson_plan_bp
from Apps.question_handle import ques_handle_bp
from Apps.DatabaseTables import db, User, Question, KnowledgePoint, Offline_Resource
import Apps.config

app = Flask(__name__)
# 注册蓝图
app.register_blueprint(lesson_plan_bp, url_prefix='/plan')  # 可以设置 URL 前缀
app.register_blueprint(ques_handle_bp, url_prefix='/ques')  # 可以设置 URL 前缀
CORS(app)

app.config.from_object(Apps.config)
db.init_app(app)


@app.route('/')
def home():
    return "你好呀，这里是EduPlatform系统！"


@app.route('/knowledge/add', methods=['GET'])
def add_knowledge_points_from_file():
    try:
        file_path = os.path.join(app.static_folder, 'knowledges.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            knowledge_points = json.load(file)

        for k in knowledge_points:
            new_knowledge_point = KnowledgePoint(
                content=k['content'],
                weight=k['weight']
            )
            db.session.add(new_knowledge_point)

        db.session.commit()
        return jsonify({'message': 'Knowledge Points added successfully!'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/resources/add', methods=['GET'])
def add_offline_resources_from_file():
    try:
        file_path = os.path.join(app.static_folder, 'offline_resources.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            resources = json.load(file)

        for r in resources:
            new_resource = Offline_Resource(
                title=r['title'],
                link=r['link'],
                duration=r['duration'],
                views=r.get('views', 0),
                likes=r.get('likes', 0),
                favorites=r.get('favorites', 0),
                shares=r.get('shares', 0),
                tags=r.get('tags', None)
            )
            db.session.add(new_resource)

        db.session.commit()
        return jsonify({'message': 'Offline Resources added successfully!'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500



# 增加用户
@app.route('/users/add', methods=['POST',"GET"])
def add_user():
    new_user = User(
        token='sample_token',
        mobile='1234567890',
        head='http://example.com/image.jpg',
        nickName='Test User',
        status=None  # 假设状态为 None
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully!'}), 201

# 查询用户
@app.route('/users/get/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'token': user.token,
            'mobile': user.mobile,
            'head': user.head,
            'nickName': user.nickName,
            'status': user.status
        }), 200
    return jsonify({'message': 'User not found!'}), 404

# 更新用户
@app.route('/users/update/<int:user_id>', methods=['GET','POST'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user:
        # 使用假设的新数据进行更新
        user.token = 'updated_token'
        user.mobile = '0987654321'
        user.head = 'http://example.com/new_image.jpg'
        user.nickName = 'Updated User'
        user.status = None  # 假设状态为 None
        db.session.commit()
        return jsonify({'message': 'User updated successfully!'}), 200
    return jsonify({'message': 'User not found!'}), 404

# 删除用户
@app.route('/users/delete/<int:user_id>', methods=['GET','POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully!'}), 200
    return jsonify({'message': 'User not found!'}), 404


if __name__ == '__main__':
    with app.app_context():  # 进入应用上下文
        db.create_all()  # 创建表格
    # app.run(host='0.0.0.0', port=5001)
    app.run(host='0.0.0.0', port=5001, debug=True)
    # app.run(host='127.0.0.1',port=5001, debug=True)
    # app.run(port=5001, debug=True)