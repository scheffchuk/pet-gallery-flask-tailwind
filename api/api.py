import os
from flask import Flask, request, jsonify
from functools import wraps

from tensorflow.keras.models import load_model
import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input

# Class names
cn = [
    "アビシニアン",
    "ベンガル",
    "バーマン",
    "ボンベイ",
    "ブリティッシュショートヘア",
    "エジプシャンマウ",
    "メインクーン",
    "ペルシャ",
    "ラグドール",
    "ロシアンブルー",
    "シャム",
    "スフィンクス",
    "アメリカンブルドッグ",
    "ピットブル", 
    "バセットハウンド",
    "ビーグル",
    "ボクサー",
    "チワワ",
    "イングリッシュコッカー", 
    "イングリッシュセッター",
    "ジャーマンショートヘアードポインター", 
    "グレートピレニーズ",
    "ハバニーズ",
    "狆",
    "キースホンド",
    "レオンベルガー",
    "ミニチュアピンシャー",
    "ニューファンドランド",
    "ポメラニアン",
    "パグ",
    "セントバーナード",
    "サモエド",
    "スコッチテリア",  
    "柴犬",
    "スタッフォードシャーブルテリア",
    "ウィートンテリア",
    "ヨークシャーテリア"
]

# Load model once at startup
MODEL_PATH = 'dog_cat_classification_fine_tuned_e30.keras'  
model = load_model(MODEL_PATH)

app = Flask(__name__)

# Get API key from environment
API_KEY = os.environ.get('API_KEY', 'dev-api-key-change-in-production')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def prepare_image(file_stream):
    # Read image from file stream
    file_bytes = np.frombuffer(file_stream.read(), np.uint8)
    im = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    im = cv2.resize(im, (160, 160))
    im = im.astype('float32')
    im = preprocess_input(im)
    im = np.expand_dims(im, axis=0)
    return im

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

@app.route('/predict', methods=['POST'])
@require_api_key
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        im = prepare_image(file)
        preds = model.predict(im, batch_size=1, verbose=0)[0]
        result = {
            'predicted_class': cn[int(np.argmax(preds))],
            'probabilities': {cn[i]: float(preds[i]) for i in range(len(cn))}
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)