import json

from flask import Flask, jsonify
from flask_cors import CORS
# 导入蓝图
from Apps.lesson_plan import lesson_plan_bp
from Apps.question_handle import ques_handle_bp
from Apps.DatabaseTables import db, User, Question
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


@app.route('/add/ques', methods=['GET','POST'])
def add_questions():
    questions = [
        {
            "content": '{"content": "1. 选择题：数字素养的定义是？", "option_a": "信息获取能力", "option_b": "数据分析能力", "option_c": "编程能力", "option_d": "以上都是"}',
            "question_type": 0,
            "crt_ans": json.dumps({"ans": "d", "des": "数字素养包括信息获取、数据分析和编程能力等多方面的能力。"})
        },
        {
            "content": '{"content": "2. 填空题：提升数字素养需要不断{ }和实践。"}',
            "question_type": 1,
            "crt_ans": json.dumps({"ans": "学习", "des": "学习和实践是提升数字素养的关键。"})
        },
        {
            "content": '{"content": "3. 判断题：数字素养只与技术有关。"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "错误", "des": "数字素养不仅与技术有关，还包括信息的获取、评估和使用能力。"})
        },
        {
            "content": '{"content": "4. 选择题：以下哪项不是数字素养的组成部分？", "option_a": "信息获取", "option_b": "信息评估", "option_c": "信息传播", "option_d": "信息存储"}',
            "question_type": 0,
            "crt_ans": json.dumps({"ans": "d", "des": "信息存储不是数字素养的直接组成部分。"})
        },
        {
            "content": '{"content": "5. 填空题：在数字环境中，{ }是获取信息的第一步。"}',
            "question_type": 1,
            "crt_ans": json.dumps({"ans": "搜索", "des": "搜索是获取信息的第一步。"})
        },
        {
            "content": '{"content": "6. 判断题：所有的信息都是可靠的。"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "错误", "des": "并非所有信息都是可靠的，需进行评估。"})
        },
        {
            "content": '{"content": "7. 选择题：数字素养的提升需要哪些技能？", "option_a": "编程", "option_b": "数据分析", "option_c": "信息筛选", "option_d": "以上都是"}',
            "question_type": 0,
            "crt_ans": json.dumps({"ans": "d", "des": "数字素养的提升需要多种技能。"})
        },
        {
            "content": '{"content": "8. 填空题：在网络环境中，保护个人隐私的措施包括使用{ }和定期更新软件。"}',
            "question_type": 1,
            "crt_ans": json.dumps({"ans": "强密码", "des": "使用强密码是保护个人隐私的重要措施。"})
        },
        {
            "content": '{"content": "9. 判断题：数字素养只在工作中有用。"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "错误", "des": "数字素养在生活的各个方面都很重要。"})
        },
        {
            "content": '{"content": "10. 选择题：以下哪项是提升数字素养的有效方法？", "option_a": "参加培训", "option_b": "自学", "option_c": "实践", "option_d": "以上都是"}',
            "question_type": 0,
            "crt_ans": json.dumps({"ans": "d", "des": "参加培训、自学和实践都是提升数字素养的有效方法。"})
        },
        {
            "content": '{"content": "11. 填空题：数字素养的核心是{ }能力。"}',
            "question_type": 1,
            "crt_ans": json.dumps({"ans": "信息处理", "des": "信息处理能力是数字素养的核心。"})
        },
        {
            "content": '{"content": "12. 判断题：数字素养与传统素养无关。"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "错误", "des": "数字素养与传统素养是相辅相成的。"})
        },
        {
            "content": '{"content": "13. 选择题：数字素养的提升需要哪些方面的努力？", "option_a": "技术能力", "option_b": "批判性思维", "option_c": "信息素养", "option_d": "以上都是"}',
            "question_type": 0,
            "crt_ans": json.dumps({"ans": "d", "des": "数字素养的提升需要多方面的努力。"})
        },
        {
            "content": '{"content": "14. 填空题：在数字时代，{ }是获取信息的重要途径。"}',
            "question_type": 1,
            "crt_ans": json.dumps({"ans": "互联网", "des": "互联网是获取信息的重要途径。"})
        },
        {
            "content": '{"content": "15. 判断题：数字素养只与年轻人有关。"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "错误", "des": "数字素养与所有年龄段的人都有关。"})
        },
        {
            "content": '{"content": "16. 选择题：以下哪项是提升数字素养的有效方法？", "option_a": "参加培训", "option_b": "自学", "option_c": "实践", "option_d": "以上都是"}',
            "question_type": 0,
            "crt_ans": json.dumps({"ans": "d", "des": "参加培训、自学和实践都是提升数字素养的有效方法。"})
        },
        {
            "content": '{"content": "17. 填空题：提升数字素养需要不断{ }和实践。"}',
            "question_type": 1,
            "crt_ans": json.dumps({"ans": "学习", "des": "学习和实践是提升数字素养的关键。"})
        },
        {
            "content": '{"content": "18. 判断题：数字素养只在工作中有用。"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "错误", "des": "数字素养在生活的各个方面都很重要。"})
        },
        {
            "content": '{"content": "19. 选择题：以下哪项是提升数字素养的有效方法？", "option_a": "参加培训", "option_b": "自学", "option_c": "实践", "option_d": "以上都是"}',
            "question_type": 0,
            "crt_ans": json.dumps({"ans": "d", "des": "参加培训、自学和实践都是提升数字素养的有效方法。"})
        },
        {
            "content": '{"content": "20. 填空题：数字素养的核心是{ }能力。"}',
            "question_type": 1,
            "crt_ans": json.dumps({"ans": "信息处理", "des": "信息处理能力是数字素养的核心。"})
        },
        {
            "content": '{"content": "21. 简答题：请简述数字素养的重要性。"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "数字素养使个人能够有效地获取和使用信息，提升工作和生活的效率。",
                                   "des": "评分标准：回答完整且逻辑清晰得5分，回答部分正确得3分，回答不清晰或错误得0分。"})
        },
        {
            "content": '{"content": "22. 简答题：如何提升个人的数字素养？"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "通过参加培训、阅读相关书籍和实践应用等方式提升数字素养。",
                                   "des": "评分标准：回答完整且逻辑清晰得5分，回答部分正确得3分，回答不清晰或错误得0分。"})
        },
        {
            "content": '{"content": "23. 简答题：数字素养在现代社会中的作用是什么？"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "数字素养帮助人们在信息爆炸的时代中筛选和利用信息。",
                                   "des": "评分标准：回答完整且逻辑清晰得5分，回答部分正确得3分，回答不清晰或错误得0分。"})
        },
        {
            "content": '{"content": "24. 简答题：请举例说明如何在日常生活中应用数字素养。"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "通过使用搜索引擎查找信息、使用社交媒体与他人沟通等方式。",
                                   "des": "评分标准：回答完整且逻辑清晰得5分，回答部分正确得3分，回答不清晰或错误得0分。"})
        },
        {
            "content": '{"content": "25. 简答题：如何评估信息的可靠性？"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "检查信息来源、对比多个来源的信息、查看作者的背景等。",
                                   "des": "评分标准：回答完整且逻辑清晰得5分，回答部分正确得3分，回答不清晰或错误得0分。"})
        },
        {
            "content": '{"content": "26. 简答题：数字素养与传统素养的关系是什么？"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "数字素养与传统素养是相辅相成的，传统素养为数字素养提供基础。",
                                   "des": "评分标准：回答完整且逻辑清晰得5分，回答部分正确得3分，回答不清晰或错误得0分。"})
        },
        {
            "content": '{"content": "27. 简答题：在数字时代，如何保护个人隐私？"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "使用强密码、定期更新隐私设置、谨慎分享个人信息等。",
                                   "des": "评分标准：回答完整且逻辑清晰得5分，回答部分正确得3分，回答不清晰或错误得0分。"})
        },
        {
            "content": '{"content": "28. 简答题：请谈谈数字素养在教育中的重要性。"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "数字素养在教育中帮助学生有效获取和利用信息，提升学习效率。",
                                   "des": "评分标准：回答完整且逻辑清晰得5分，回答部分正确得3分，回答不清晰或错误得0分。"})
        },
        {
            "content": '{"content": "29. 简答题：如何在工作中应用数字素养？"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "通过使用数据分析工具、在线协作平台等提升工作效率。",
                                   "des": "评分标准：回答完整且逻辑清晰得5分，回答部分正确得3分，回答不清晰或错误得0分。"})
        },
        {
            "content": '{"content": "30. 简答题：请描述数字素养对未来职业发展的影响。"}',
            "question_type": 2,
            "crt_ans": json.dumps({"ans": "数字素养是未来职业发展的重要基础，能够帮助个人适应快速变化的工作环境。",
                                   "des": "评分标准：回答完整且逻辑清晰得5分，回答部分正确得3分，回答不清晰或错误得0分。"})
        }
    ]

    for question in questions:
        new_question = Question(
            content=question["content"],
            question_type=question["question_type"],
            crt_ans=question["crt_ans"],  # 存储 JSON 字符串
        )
        db.session.add(new_question)

    db.session.commit()
    # 返回成功响应
    return jsonify({"message": "问题添加成功", "status": "success"}), 201


if __name__ == '__main__':
    with app.app_context():  # 进入应用上下文
        db.create_all()  # 创建表格
    app.run(host='0.0.0.0',port=5001, debug=True)