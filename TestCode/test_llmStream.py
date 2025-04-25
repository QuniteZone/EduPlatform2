from flask import Flask

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return "你好"

#http://127.0.0.1:5002/llmStream
@app.route('/llmStream', methods=['POST'])
def llmStream():



    return "llmStream"

if __name__ == '__main__':
    app.run(port=5002,debug=True)
