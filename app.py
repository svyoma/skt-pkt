"""
Sanskrit → Prakrit Translator — Flask web application.
"""

from flask import Flask, render_template, request, jsonify
from translator.engine import SanskritPrakritTranslator

app = Flask(__name__)
_translator = SanskritPrakritTranslator()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json(silent=True) or {}
    word = (data.get('word') or '').strip()
    if not word:
        return jsonify({'error': 'No word provided'}), 400

    soften_k = bool(data.get('soften_k', False))
    result = _translator.translate(word, soften_k=soften_k)
    return jsonify(result.as_dict())


@app.route('/translate_form', methods=['POST'])
def translate_form():
    """Form-based (non-AJAX) endpoint for progressive enhancement."""
    word = request.form.get('word', '').strip()
    result = None
    if word:
        result = _translator.translate(word).as_dict()
    return render_template('index.html', result=result, query=word)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
