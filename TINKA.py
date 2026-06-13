import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from datetime import timedelta
from sklearn.ensemble import RandomForestClassifier
import os
import re
import numpy as np

# Función para obtener resultados desde la web
def obtener_resultados(force_refresh=False):
    # Primero, verificar si el archivo local existe y es reciente
    proyecto_dir = os.path.abspath(os.path.dirname(__file__))
    ruta_dir = os.path.join(proyecto_dir, "Historial")
    ruta = os.path.join(ruta_dir, "tinka_dataset.xlsx")

    columnas_base = [
        "Fecha_sorteo",
        "Numero_1", "Numero_2", "Numero_3", "Numero_4", "Numero_5", "Numero_6",
        "Numero_extra_1", "Numero_extra_2", "Numero_extra_3", "Numero_extra_4", "Numero_extra_5", "Numero_extra_6",
        "Boliyapa",
        "Ganador_seis_numeros", "Premio_seis_numeros",
        "Ganador_numeros_extra", "Premio_si_o_si",
        "Ganador_cinco_numeros_boliyapa", "Premio_cinco_boliyapa",
        "Ganador_cinco_numeros", "Premio_cinco",
        "Ganador_cuatro_numeros_boliyapa", "Premio_cuatro_boliyapa",
        "Ganador_cuatro_numeros", "Premio_cuatro",
        "Ganador_tres_numeros_boliyapa", "Premio_tres_boliyapa",
        "Ganador_tres_numeros", "Premio_tres",
        "Ganador_dos_numeros_boliyapa", "Premio_dos_boliyapa",
        "Ganadores", "Premio", "Ganadores_6", "Premio_6", "Total_ganadores", "Total_premio"
    ]

    def normalizar_dataset(df):
        df = df.copy()
        for col in columnas_base:
            if col not in df.columns:
                df[col] = 0 if col != "Fecha_sorteo" else pd.NaT
        df = df[columnas_base]
        df["Fecha_sorteo"] = pd.to_datetime(df["Fecha_sorteo"], errors="coerce", dayfirst=True)
        return df

    def exportar_dataset(df):
        df_export = df.copy()
        df_export["Fecha_sorteo"] = pd.to_datetime(df_export["Fecha_sorteo"], errors="coerce").dt.strftime("%d/%m/%Y")
        df_export.to_excel(ruta, index=False)
    
    # Si el archivo existe y fue actualizado hoy, devolver sin rescrapear
    if os.path.exists(ruta) and not force_refresh:
        import time
        hoy = datetime.datetime.now().date()
        ultima_modificacion = datetime.datetime.fromtimestamp(os.path.getmtime(ruta)).date()
        if hoy == ultima_modificacion:
            print(f"Dataset ya actualizado hoy, usando caché local")
            df = pd.read_excel(ruta)
            if not df.empty:
                df = normalizar_dataset(df)
                exportar_dataset(df)
                ultima_fecha = df["Fecha_sorteo"].max().strftime("%d-%m-%Y")
            else:
                ultima_fecha = "N/A"
            return df, ultima_fecha
    
    # Si no existe caché reciente, rescrapear
    fecha_inicio = datetime.datetime(2025, 1, 1)  # Últimos meses solamente
    sorteo_num = 1200  # Aproximación
    dias_sorteo = [2, 6]  # miércoles=2, domingo=6
    hoy = datetime.datetime.now()

    # Ajuste: si hoy es día de sorteo, solo tomar hasta el anterior
    if hoy.weekday() in dias_sorteo:
        fecha_fin = hoy - timedelta(days=1)
    else:
        fecha_fin = hoy

    resultados = []
    fecha_actual = fecha_inicio

    while fecha_actual <= fecha_fin:
        if fecha_actual.weekday() in dias_sorteo:
            fecha_str = fecha_actual.strftime("%d-%m-%Y")
            url = f"https://www.tinkaresultados.com/sorteos-historicos/jugada-{sorteo_num}-del-{fecha_str}"
            try:
                r = requests.get(url, timeout=5)
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")

                # Jugada ganadora
                jugada = [int(x.text) for x in soup.select("span.badge.text-bg-success.fs-4")[:6]]

                # Boliyapa y Sí o Sí
                boliyapa_tag = soup.select_one("span.badge.text-bg-danger.fs-4")
                boliyapa = boliyapa_tag.get_text(strip=True) if boliyapa_tag else ""
                badges_success = soup.select("span.badge.text-bg-success.fs-4")
                si_o_si = badges_success[6].get_text(strip=True) if len(badges_success) > 6 else ""

                # Intentar extraer información adicional: ganadores y premio
                def parse_number(s):
                    if s is None:
                        return 0
                    # Extraer grupo numérico y eliminar separadores de miles
                    m = re.search(r"([0-9][0-9\'\.,]*)", s)
                    if not m:
                        return 0
                    num = m.group(1)
                    # eliminar apostrofes, puntos y comas usados como separador de miles
                    num_digits = re.sub(r"[^0-9]", "", num)
                    try:
                        return int(num_digits)
                    except:
                        try:
                            return float(num_digits)
                        except:
                            return 0

                ganadores = 0
                premio = 0
                ganadores_6 = 0
                premio_6 = 0
                total_ganadores = 0
                total_premio = 0

                registro = {
                    "Fecha_sorteo": fecha_actual.strftime("%d/%m/%Y"),
                    "Numero_1": jugada[0], "Numero_2": jugada[1], "Numero_3": jugada[2],
                    "Numero_4": jugada[3], "Numero_5": jugada[4], "Numero_6": jugada[5],
                    "Numero_extra_1": si_o_si, "Numero_extra_2": 0, "Numero_extra_3": 0,
                    "Numero_extra_4": 0, "Numero_extra_5": 0, "Numero_extra_6": 0,
                    "Boliyapa": boliyapa,
                    "Ganador_seis_numeros": 0, "Premio_seis_numeros": "",
                    "Ganador_numeros_extra": 0, "Premio_si_o_si": "",
                    "Ganador_cinco_numeros_boliyapa": 0, "Premio_cinco_boliyapa": "",
                    "Ganador_cinco_numeros": 0, "Premio_cinco": "",
                    "Ganador_cuatro_numeros_boliyapa": 0, "Premio_cuatro_boliyapa": "",
                    "Ganador_cuatro_numeros": 0, "Premio_cuatro": "",
                    "Ganador_tres_numeros_boliyapa": 0, "Premio_tres_boliyapa": "",
                    "Ganador_tres_numeros": 0, "Premio_tres": "",
                    "Ganador_dos_numeros_boliyapa": 0, "Premio_dos_boliyapa": "",
                    "Ganadores": 0,
                    "Premio": 0,
                    "Ganadores_6": 0,
                    "Premio_6": 0,
                    "Total_ganadores": 0,
                    "Total_premio": 0,
                }

                # Intentar extraer sección/tabla de ganadores usando el HTML exacto de la web
                total_ganadores = 0
                total_premio = 0
                ganadores_6 = 0
                premio_6 = 0

                # Buscar tabla específica por clases comunes o por caption/header
                table = soup.select_one('table.table.table-striped.table-sm') or soup.select_one('table.table.table-striped') or soup.find('table', class_='table-striped')
                if not table:
                    for t in soup.find_all('table'):
                        caption = t.find('caption')
                        thead = t.find('thead')
                        head_text = ''
                        if caption:
                            head_text += caption.get_text(' ', strip=True).lower()
                        if thead:
                            head_text += ' ' + thead.get_text(' ', strip=True).lower()
                        if 'ganador' in head_text or 'gandores' in head_text or 'categoria' in head_text:
                            table = t
                            break

                if table:
                    tbody = table.find('tbody') or table
                    for tr in tbody.find_all('tr'):
                        cols = tr.find_all(['td', 'th'])
                        if len(cols) < 3:
                            continue

                        categoria = cols[0].get_text(strip=True).lower()
                        gan_text = cols[1].get_text(strip=True)
                        premiotext = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                        dinero_text = cols[3].get_text(strip=True) if len(cols) > 3 else premiotext

                        try:
                            g_val = int(re.sub(r"[^0-9]", "", gan_text)) if gan_text else 0
                        except:
                            g_val = 0
                        p_val = parse_number(premiotext) if premiotext else 0
                        d_val = parse_number(dinero_text) if dinero_text else 0

                        total_ganadores += g_val
                        total_premio += d_val

                        if '6 acierto' in categoria or '6 aciertos' in categoria or categoria.strip() == '6 aciertos':
                            ganadores_6 = g_val
                            premio_6 = p_val
                            registro["Ganador_seis_numeros"] = 1 if g_val > 0 else 0
                            registro["Premio_seis_numeros"] = premiotext
                        elif 'sí o sí' in categoria or 'si o si' in categoria:
                            registro["Ganador_numeros_extra"] = g_val
                            registro["Premio_si_o_si"] = premiotext
                        elif '5 aciertos + boliyapa' in categoria:
                            registro["Ganador_cinco_numeros_boliyapa"] = g_val
                            registro["Premio_cinco_boliyapa"] = premiotext
                        elif categoria.strip() == '5 aciertos':
                            registro["Ganador_cinco_numeros"] = g_val
                            registro["Premio_cinco"] = premiotext
                        elif '4 aciertos + boliyapa' in categoria:
                            registro["Ganador_cuatro_numeros_boliyapa"] = g_val
                            registro["Premio_cuatro_boliyapa"] = premiotext
                        elif categoria.strip() == '4 aciertos':
                            registro["Ganador_cuatro_numeros"] = g_val
                            registro["Premio_cuatro"] = premiotext
                        elif '3 aciertos + boliyapa' in categoria:
                            registro["Ganador_tres_numeros_boliyapa"] = g_val
                            registro["Premio_tres_boliyapa"] = premiotext
                        elif categoria.strip() == '3 aciertos':
                            registro["Ganador_tres_numeros"] = g_val
                            registro["Premio_tres"] = premiotext
                        elif '2 aciertos + boliyapa' in categoria:
                            registro["Ganador_dos_numeros_boliyapa"] = g_val
                            registro["Premio_dos_boliyapa"] = premiotext

                # Fallback directo para el HTML que a veces no usa thead/tbody como esperábamos
                if registro["Ganador_seis_numeros"] == 0 or registro["Premio_seis_numeros"] == "":
                    for tr in soup.select('table.table.table-striped.table-sm tbody tr, table.table.table-striped tbody tr'):
                        tds = tr.find_all('td')
                        if len(tds) != 4:
                            continue
                        categoria = tds[0].get_text(strip=True).lower()
                        g_val = int(re.sub(r"[^0-9]", "", tds[1].get_text(strip=True)) or 0)
                        premio_texto = tds[2].get_text(strip=True)
                        dinero_texto = tds[3].get_text(strip=True)
                        if '6 aciertos' in categoria:
                            registro["Ganador_seis_numeros"] = 1 if g_val > 0 else 0
                            registro["Premio_seis_numeros"] = premio_texto
                        elif 'sí o sí' in categoria or 'si o si' in categoria:
                            registro["Ganador_numeros_extra"] = g_val
                            registro["Premio_si_o_si"] = premio_texto
                        elif '5 aciertos + boliyapa' in categoria:
                            registro["Ganador_cinco_numeros_boliyapa"] = g_val
                            registro["Premio_cinco_boliyapa"] = premio_texto
                        elif categoria == '5 aciertos':
                            registro["Ganador_cinco_numeros"] = g_val
                            registro["Premio_cinco"] = premio_texto
                        elif '4 aciertos + boliyapa' in categoria:
                            registro["Ganador_cuatro_numeros_boliyapa"] = g_val
                            registro["Premio_cuatro_boliyapa"] = premio_texto
                        elif categoria == '4 aciertos':
                            registro["Ganador_cuatro_numeros"] = g_val
                            registro["Premio_cuatro"] = premio_texto
                        elif '3 aciertos + boliyapa' in categoria:
                            registro["Ganador_tres_numeros_boliyapa"] = g_val
                            registro["Premio_tres_boliyapa"] = premio_texto
                        elif categoria == '3 aciertos':
                            registro["Ganador_tres_numeros"] = g_val
                            registro["Premio_tres"] = premio_texto
                        elif '2 aciertos + boliyapa' in categoria:
                            registro["Ganador_dos_numeros_boliyapa"] = g_val
                            registro["Premio_dos_boliyapa"] = premio_texto

                # Si no se encontró tabla, intentar selectores puntuales como fallback
                if total_ganadores == 0 and total_premio == 0:
                    sel_gan = soup.select_one('.ganadores, .winners, .result-winners, .ganador')
                    sel_prem = soup.select_one('.premio, .prize, .premios, .award')
                    if sel_gan:
                        m = re.search(r"(\d[\d\.,']*)", sel_gan.get_text())
                        if m:
                            ganadores = int(re.sub(r"[^0-9]", "", m.group(1)))
                    if sel_prem:
                        m = re.search(r"(\d[\d\.,']*)", sel_prem.get_text())
                        if m:
                            premio = parse_number(m.group(1))

                # Asignar totales si se detectaron
                if total_ganadores > 0:
                    ganadores = total_ganadores
                if total_premio > 0:
                    premio = total_premio
                if ganadores_6 > 0:
                    registro["Ganador_seis_numeros"] = 1
                registro["Fecha_sorteo"] = fecha_actual
                registro["Ganadores"] = ganadores
                registro["Premio"] = premio
                registro["Ganadores_6"] = ganadores_6
                registro["Premio_6"] = premio_6
                registro["Total_ganadores"] = total_ganadores
                registro["Total_premio"] = total_premio
                resultados.append(registro)
            except Exception as e:
                print(f"Error descargando {url}: {e}")
            sorteo_num += 1
        fecha_actual += timedelta(days=1)

    if not resultados:
        print("No se obtuvieron resultados nuevos")
        # Si no hay resultados nuevos pero existe archivo previo, devolverlo
        if os.path.exists(ruta):
            df = pd.read_excel(ruta)
            if not df.empty:
                df["Fecha_sorteo"] = pd.to_datetime(df["Fecha_sorteo"], dayfirst=True, errors="coerce")
                ultima_fecha = df["Fecha_sorteo"].max().strftime("%d-%m-%Y")
            else:
                ultima_fecha = "N/A"
            return df, ultima_fecha
        raise Exception("No data found and no local cache")
    
    df = pd.DataFrame(resultados)
    df = normalizar_dataset(df)
    ultima_fecha = pd.to_datetime(df["Fecha_sorteo"], errors="coerce").max().strftime("%d-%m-%Y")

    # Guardar dataset en la carpeta local 'Historial'
    os.makedirs(ruta_dir, exist_ok=True)
    exportar_dataset(df)
    print(f"Dataset actualizado guardado en: {ruta}")

    return df, ultima_fecha

# Preparar dataset para ML
def preparar_dataset(df):
    # Asegurar columnas de ganadores/premio
    if 'Ganadores' not in df.columns:
        df['Ganadores'] = 0
    if 'Premio' not in df.columns:
        df['Premio'] = 0
    if 'Ganador_seis_numeros' not in df.columns:
        df['Ganador_seis_numeros'] = 0
    # ordenar por fecha ascendente para calcular recencia y counts acumuladas
    df = df.sort_values('Fecha_sorteo').reset_index(drop=True)
    df['dia_semana'] = df['Fecha_sorteo'].dt.dayofweek
    df['mes'] = df['Fecha_sorteo'].dt.month
    df['anio'] = df['Fecha_sorteo'].dt.year

    # contadores y ultimo visto por número
    last_seen = {i: None for i in range(1,49)}
    cum_counts = {i: 0 for i in range(1,49)}
    # global frequency (total occurrences in dataset)
    global_counts = {i: 0 for i in range(1,49)}
    for _, row in df.iterrows():
        for n in [row['Numero_1'], row['Numero_2'], row['Numero_3'], row['Numero_4'], row['Numero_5'], row['Numero_6']]:
            global_counts[int(n)] += 1

    numeros = []
    for _, row in df.iterrows():
        fecha = row['Fecha_sorteo']
        premio_val = row.get('Premio', 0)
        premio_log = np.log1p(premio_val)
        ganadores = row.get('Ganadores', 0)
        ganador_seis = row.get('Ganador_seis_numeros', 0)
        ganadores_6 = row.get('Ganadores_6', 0) if 'Ganadores_6' in row else 0
        premio_6 = row.get('Premio_6', 0) if 'Premio_6' in row else 0
        impacto_6 = np.log1p(ganadores_6) * np.log1p(premio_6)
        total_premio = row.get('Total_premio', row.get('Premio', 0))
        total_premio_log = np.log1p(total_premio)

        for n in [row['Numero_1'], row['Numero_2'], row['Numero_3'], row['Numero_4'], row['Numero_5'], row['Numero_6']]:
            n = int(n)
            # cumulative count before this occurrence
            cum = cum_counts.get(n, 0)
            # days since last seen
            last = last_seen.get(n)
            if last is None:
                days_since = 9999
            else:
                days_since = (fecha - last).days
            # recency weight (exponential decay)
            recency_w = np.exp(-days_since / 30.0) if days_since < 9999 else 0.0
            global_freq = global_counts.get(n, 0)

            numeros.append([
                row['dia_semana'], row['mes'], row['anio'],
                ganadores, premio_log, ganador_seis, ganadores_6, premio_6, impacto_6, total_premio_log,
                cum, recency_w, global_freq, n
            ])

        # actualizar last_seen y cum_counts después de procesar la fila
        for n in [row['Numero_1'], row['Numero_2'], row['Numero_3'], row['Numero_4'], row['Numero_5'], row['Numero_6']]:
            n = int(n)
            cum_counts[n] = cum_counts.get(n, 0) + 1
            last_seen[n] = fecha

    dataset = pd.DataFrame(numeros, columns=[
        'dia_semana','mes','anio','ganadores','premio_log','ganador_seis_numeros','ganadores_6','premio_6','impacto_6','total_premio_log',
        'cum_count','recency_w','global_freq','numero'])
    return dataset

# Entrenar modelo
def entrenar_modelo(dataset):
    X = dataset[['dia_semana','mes','anio','ganadores','premio_log','ganador_seis_numeros','ganadores_6','premio_6','impacto_6','total_premio_log','cum_count','recency_w','global_freq']].astype(float)
    y = dataset['numero']
    modelo = RandomForestClassifier(n_estimators=200, random_state=42)
    modelo.fit(X, y)
    return modelo

# Predecir próxima jugada
def predecir(modelo, df):
    # Construir features usando la fila más reciente del dataset si existe
    fecha_actual = datetime.datetime.now()
    if df is not None and not df.empty:
        ultima = df.sort_values('Fecha_sorteo').iloc[-1]
        ganadores = ultima.get('Ganadores', 0)
        premio_log = np.log1p(ultima.get('Premio', 0))
        ganador_seis = ultima.get('Ganador_seis_numeros', 0)
        ganadores_6 = ultima.get('Ganadores_6', 0)
        premio_6 = ultima.get('Premio_6', 0)
        impacto_6 = np.log1p(ganadores_6) * np.log1p(premio_6)
        total_premio_log = np.log1p(ultima.get('Total_premio', ultima.get('Premio', 0)))
    else:
        ganadores = 0
        premio_log = 0
        ganador_seis = 0
        ganadores_6 = 0
        premio_6 = 0
        impacto_6 = 0
        total_premio_log = 0

    # Preparar stats históricos (counts y last seen) desde df
    counts = {i: 0 for i in range(1,49)}
    last_seen = {i: None for i in range(1,49)}
    # recorrer df ordenado y actualizar hasta la última fecha
    if df is not None and not df.empty:
        df_sorted = df.sort_values('Fecha_sorteo')
        for _, row in df_sorted.iterrows():
            fecha = row['Fecha_sorteo']
            for n in [row['Numero_1'], row['Numero_2'], row['Numero_3'], row['Numero_4'], row['Numero_5'], row['Numero_6']]:
                n = int(n)
                counts[n] = counts.get(n, 0) + 1
                last_seen[n] = fecha

    # construir una fila de features por cada candidato 1..48
    feature_rows = []
    for n in range(1,49):
        cum = counts.get(n, 0)
        last = last_seen.get(n)
        if last is None:
            days_since = 9999
        else:
            days_since = (fecha_actual - last).days
        recency_w = np.exp(-days_since / 30.0) if days_since < 9999 else 0.0
        global_freq = 0
        # attempt to fetch global freq from df
        if df is not None and not df.empty:
            # count occurrences in full df
            global_freq = int(((df['Numero_1'] == n) | (df['Numero_2'] == n) | (df['Numero_3'] == n) | (df['Numero_4'] == n) | (df['Numero_5'] == n) | (df['Numero_6'] == n)).sum())

        row_features = [fecha_actual.weekday(), fecha_actual.month, fecha_actual.year, ganadores, premio_log, ganador_seis, ganadores_6, premio_6, impacto_6, total_premio_log, cum, recency_w, global_freq]
        feature_rows.append(row_features)

    feature_cols = ['dia_semana','mes','anio','ganadores','premio_log','ganador_seis_numeros','ganadores_6','premio_6','impacto_6','total_premio_log','cum_count','recency_w','global_freq']
    X = pd.DataFrame(feature_rows, columns=feature_cols)

    probs_matrix = modelo.predict_proba(X)
    classes = list(modelo.classes_)

    prob_map = {}
    max_count = max(counts.values()) if counts else 1
    ajuste_6 = 1.0 + (np.tanh(np.log1p(premio_6) / 10.0) - np.tanh(np.log1p(ganadores_6 + 1) / 8.0))
    for i, n in enumerate(range(1,49)):
        if n in classes:
            idx = classes.index(n)
            base_prob = float(probs_matrix[i][idx])
            frecuencia_normalizada = counts.get(n, 0) / max_count if max_count else 0.0
            recencia_normalizada = float(np.clip(recency_w, 0.0, 1.0))
            factor_numero = 1.0 + (ajuste_6 * (0.7 * frecuencia_normalizada + 0.3 * recencia_normalizada))
            prob_map[n] = base_prob * factor_numero
        else:
            prob_map[n] = 0.0

    numeros_recomendados = sorted(prob_map.keys(), key=lambda k: prob_map[k], reverse=True)[:6]
    boliyapa = sorted(prob_map.keys(), key=lambda k: prob_map[k], reverse=True)[6]

    return numeros_recomendados, boliyapa

if __name__ == "__main__":
    # Ejecutar flujo automático
    df, ultima_fecha = obtener_resultados()
    dataset = preparar_dataset(df)
    modelo = entrenar_modelo(dataset)
    nums, bol = predecir(modelo, df)
    print('Predicción:', nums, bol)