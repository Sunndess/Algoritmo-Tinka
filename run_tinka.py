import traceback
import TINKA

try:
    df, ultima_fecha = TINKA.obtener_resultados()
    if df.empty:
        print('No se obtuvieron resultados (DataFrame vacío).')
    else:
        print('DataFrame obtenido con', len(df), 'filas.')
    dataset = TINKA.preparar_dataset(df)
    modelo = TINKA.entrenar_modelo(dataset)
    TINKA.predecir(modelo, ultima_fecha)
except Exception as e:
    print('Ocurrió una excepción al ejecutar el flujo:')
    traceback.print_exc()
    raise
