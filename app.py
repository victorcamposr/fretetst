from models import Validator
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import io

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "https://jetcalcship.web.app"}})

@app.route('/upload', methods=['POST'])
async def upload_file():
    try:
        # Check if the POST request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        # Check if the file has a valid name and extension
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Ensure the file is an Excel file
        if file and file.filename.endswith('.xlsx'):
            # Read the Excel file into a DataFrame
            excel_data = pd.read_excel(file)

            # Validator to check the excel data
            validator = Validator(dataframe=excel_data)
            validator.style_dataframe()

            # Check data
            excel_data = validator.get_dataframe()

            # Save the updated DataFrame to a new Excel file
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')

            excel_data.to_excel(writer, index=False)
            writer.close()
            output.seek(0)

            # Return the updated Excel file to the user asynchronously
            response = await send_file_async(output, 'planilha_atualizada.xlsx', True)

            # Adicione os cabeçalhos CORS à resposta
            response.headers.add("Access-Control-Allow-Origin", "https://jetcalcship.web.app")
            response.headers.add("Access-Control-Allow-Methods", "POST")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type")

            return response

        else:
            return jsonify({'error': 'Invalid file format, must be .xlsx'}), 400

    except Exception as e:
        print(f"Erro: {str(e)}")  # Imprime o erro no console
        return jsonify({'error': 'Internal Server Error'}), 500

async def send_file_async(output, download_name, as_attachment):
    return await send_file(output, download_name=download_name, as_attachment=as_attachment)

if __name__ == '__main__':
    app.run(debug=True)
