from flask import Flask, render_template, request, jsonify

import os
import openai
import flask

from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_version = os.getenv("AZURE_OPENAI_VERSION")
deployment_id = os.getenv("AZURE_DEPLOYMENT_ID")
messages = [{"role": "system", "content": "You are a helpful assistant."}]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    prompt = request.args.get("prompt")
    messages.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        deployment_id=deployment_id,
        messages=messages,
        stream=True
    )
    def stream():
        assistant_content = ''
        for chunk in response:
            finish_reason = chunk.choices[0].finish_reason
            if finish_reason == 'stop':
                messages.append({"role": "assistant", "content": assistant_content})
                yield 'data: %s\n\n' % '[DONE]'
            else:
                delta = chunk.choices[0].delta.get('content') or ""
                assistant_content += delta
                yield 'data: %s\n\n' % delta.replace('\n', '[NEWLINE]')
    return flask.Response(stream(), mimetype='text/event-stream')


if __name__ == "__main__":
    app.run()
