from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS
import traceback
import os
from io import BytesIO
from openpyxl.utils import get_column_letter
import TINKA

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/update', methods=['POST'])
def update():
    try:
        df, ultima_fecha = TINKA.obtener_resultados(force_refresh=True)
        if df.empty:
            return jsonify({'status':'empty','message':'No se obtuvieron resultados'}), 200
        return jsonify({'status':'ok','rows':len(df),'ultima_fecha':ultima_fecha}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/predict', methods=['GET'])
def predict():
    try:
        # cargar dataset desde Historial si existe
        proyecto_dir = os.path.abspath(os.path.dirname(__file__))
        ruta = os.path.join(proyecto_dir, 'Historial', 'tinka_dataset.xlsx')
        if not os.path.exists(ruta):
            return jsonify({'status':'error','message':'Dataset no encontrado'}), 404
        df = TINKA.pd.read_excel(ruta, parse_dates=['Fecha_sorteo'])
        dataset = TINKA.preparar_dataset(df)
        modelo = TINKA.entrenar_modelo(dataset)
        # obtener predicción usando la función centralizada
        numeros_recomendados, boliyapa = TINKA.predecir(modelo, df)
        return jsonify({'status':'ok','numeros_recomendados':numeros_recomendados,'boliyapa':boliyapa}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/download', methods=['GET'])
def download():
    try:
        df, _ = TINKA.obtener_resultados(force_refresh=True)
        buffer = BytesIO()
        df_export = df.copy()
        if 'Fecha_sorteo' in df_export.columns:
            df_export['Fecha_sorteo'] = TINKA.pd.to_datetime(df_export['Fecha_sorteo'], errors='coerce').dt.strftime('%d/%m/%Y')
        with TINKA.pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Dataset')
            columnas = TINKA.pd.DataFrame({'Columna': list(df_export.columns)})
            columnas.to_excel(writer, index=False, sheet_name='Columnas')

            ws = writer.sheets['Dataset']
            ws.freeze_panes = 'A2'
            for idx, col in enumerate(df_export.columns, start=1):
                max_len = max(
                    len(str(col)),
                    *(len(str(v)) for v in df_export[col].head(50).fillna('').astype(str).tolist())
                )
                ws.column_dimensions[get_column_letter(idx)].width = min(max_len + 2, 28)
        buffer.seek(0)
        response = send_file(
            buffer,
            as_attachment=True,
            download_name='tinka_dataset_actualizado.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status':'error','message':str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
