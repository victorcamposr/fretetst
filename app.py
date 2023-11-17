from models import Validator
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import io
from celery import Celery

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "https://jetcalcship.web.app"}})

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '' or not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Invalid file'}), 400

    task = process_file.delay(file.read())
    return jsonify({'task_id': task.id}), 202

@celery.task(bind=True)
def process_file(self, file_data):
    try:
        excel_data = pd.read_excel(io.BytesIO(file_data))
        validator = Validator(dataframe=excel_data)
        validator.style_dataframe()
        excel_data = validator.get_dataframe()

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        excel_data.to_excel(writer, index=False)
        writer.close()
        output.seek(0)

        # You might need to save the file somewhere and return a link or ID to download it
        return send_file(output, download_name='planilha_atualizada.xlsx', as_attachment=True)
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    app.run(debug=True)



            
