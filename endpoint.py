from flask import Flask, jsonify, request, render_template, send_from_directory
import openai
import prompt 

app = Flask(__name__)

@app.route('/answer', methods=['GET'])
def answer():
    question = request.args.get('question', '')
    user_id = request.args.get('userid', '')
    print(question)
    answer = prompt.answer_question(question=question, user_id=user_id, debug=True, model="gpt-3.5-turbo")
    return jsonify({"answer": answer})


@app.route('/public/<path:path>')
def public(path):
    return send_from_directory('public', path)


@app.route('/chatbox')
@app.route('/')
def chatbox():
    return render_template('chatbox.html')

if __name__ == '__main__':
    app.run(debug=True)
