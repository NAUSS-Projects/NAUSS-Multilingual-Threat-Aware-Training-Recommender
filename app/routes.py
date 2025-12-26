from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from .models.excel import parse_training_excel
from .scrapers.news import process_news_inputs
from .models.similarity import SimilarityEngine
from .models.recommender import Recommender

bp = Blueprint('main', __name__)

# Initialize engines lazily to avoid startup issues
sim_engine = None
recommender = None

def get_engines():
    global sim_engine, recommender
    if sim_engine is None:
        sim_engine = SimilarityEngine()
    if recommender is None:
        recommender = Recommender()
    return sim_engine, recommender


def build_response_schema(recommendations, errors=None):
    return {
        "recommendations": recommendations,
        "errors": errors or []
    }


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@bp.route('/simple-test', methods=['GET'])
def simple_test():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Simple Test</title></head>
    <body>
        <h2>Simple File Upload Test</h2>
        <form action="/test-upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".xlsx,.xls">
            <br><br>
            <button type="submit">Upload</button>
        </form>
    </body>
    </html>
    '''


@bp.route('/test-upload', methods=['POST'])
def test_upload():
    print("=== TEST UPLOAD DEBUG ===")
    print(f"Request files: {request.files}")
    print(f"Request form: {request.form}")
    print(f"Request method: {request.method}")
    print(f"Request content type: {request.content_type}")
    
    file = request.files.get('file')
    if file:
        print(f"File found: {file.filename}")
        print(f"File content type: {file.content_type}")
        return f"File received: {file.filename}"
    else:
        print("No file received")
        return "No file received"
    print("=== END DEBUG ===")


@bp.route('/api/recommend', methods=['POST'])
def api_recommend():
    # Expect: excel file (form file), optional: urls (json list) or news_text (string)
    file = request.files.get('file')
    urls = request.form.get('urls')
    news_text = request.form.get('news_text')

    if not file or not file.filename:
        return jsonify(build_response_schema([], ["No Excel file uploaded."])), 400

    upload_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    try:
        user_data = parse_training_excel(filepath)
    except Exception as e:
        return jsonify(build_response_schema([], [f"Failed to parse Excel: {e}"])), 400

    try:
        news_docs = process_news_inputs(urls=urls, raw_text=news_text)
    except Exception as e:
        return jsonify(build_response_schema([], [f"Failed to process news: {e}"])), 400

    try:
        sim_eng, rec = get_engines()
        recs = rec.generate_recommendations(user_data, news_docs, sim_eng)
        return jsonify(build_response_schema(recs)), 200
    except Exception as e:
        return jsonify(build_response_schema([], [f"Failed to generate recommendations: {e}"])), 500


@bp.route('/recommendations', methods=['POST'])
def web_recommendations():
    # Web form posts to this route; we render HTML results
    file = request.files.get('file')
    urls = request.form.get('urls')
    news_text = request.form.get('news_text')
    
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: Request content type: {request.content_type}")
    print(f"DEBUG: Request files keys: {list(request.files.keys())}")
    print(f"DEBUG: Request form keys: {list(request.form.keys())}")
    print(f"DEBUG: File received: {file}")
    print(f"DEBUG: File filename: {file.filename if file else 'No file'}")
    print(f"DEBUG: File content length: {len(file.read()) if file else 0}")
    if file:
        file.seek(0)  # Reset file pointer after reading
    print(f"DEBUG: URLs: {urls}")
    print(f"DEBUG: News text: {news_text[:100] if news_text else 'No text'}")

    if not file or not file.filename:
        return render_template('index.html', error="Please upload an Excel file."), 400

    upload_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    try:
        user_data = parse_training_excel(filepath)
        news_docs = process_news_inputs(urls=urls, raw_text=news_text)
        sim_eng, rec = get_engines()
        recs = rec.generate_recommendations(user_data, news_docs, sim_eng)
        return render_template('results.html', results=recs)
    except Exception as e:
        return render_template('index.html', error=str(e)), 500
