from flask import Flask, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

@app.route('/')
def index():
    return '''
    <form method="post" enctype="multipart/form-data" action="/upload">
        <input type="file" name="file">
        <input type="text" name="text" placeholder="Type something">
        <button type="submit">Submit</button>
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    print(f"Request method: {request.method}")
    print(f"Content type: {request.content_type}")
    print(f"Files: {dict(request.files)}")
    print(f"Form: {dict(request.form)}")
    
    file = request.files.get('file')
    text = request.form.get('text')
    
    return f"File: {file.filename if file else 'None'}, Text: {text}"

if __name__ == '__main__':
    app.run(debug=True, port=5001)