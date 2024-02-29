import requests
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


# Crear la base de datos SQL
conn = sqlite3.connect('stocks.db')
c = conn.cursor()

#convertir fechas
def convertir_fecha(fecha):
    return fecha[:4] + '-' + fecha[4:6] + '-' + fecha[6:]

# Crear la tabla si no existe
c.execute('''
    CREATE TABLE IF NOT EXISTS stocks
    (name text, date text, close real)
''')

while True:
    # Preguntar al usuario si quiere hacer una consulta o ingresar datos
    accion = input("¿Quiere hacer una consulta, ingresar datos o salir? (consulta/datos/resumen/salir): ")
    if accion.lower() == 'salir':
        break
    elif accion.lower() == 'consulta':
        tipo_consulta = input("¿Quiere consultar el último valor de una acción o revisar el historial de una acción? (ultimo/historial): ")
        if tipo_consulta.lower() == 'ultimo':
            # Solicitar al usuario el valor del ticker
            ticker = input("Por favor, ingresa el valor del ticker: ")
            ticker = ticker.upper()  # Convertir el ticker a mayúsculas
            
            # Obtener la fecha de hoy
            hoy = datetime.now().strftime('%Y-%m-%d')

            # Hacer la solicitud a la API
            url = f"https://financialmodelingprep.com/api/v3/historical-chart/1min/{ticker}?from={hoy}&to={hoy}&apikey=DdNI6qCLlZsXjjmgCDR6qEohCeAzqmiW"
            response = requests.get(url)
            data = response.json()

            # Imprimir el último valor
            print("El último valor de la acción es: ", data[0]['close'])
        elif tipo_consulta.lower() == 'historial':
            # Solicitar al usuario el valor del ticker, una fecha de inicio y una fecha de fin
            ticker = input("Por favor, ingresa el valor del ticker: ")
            ticker = ticker.upper()  # Convertir el ticker a mayúsculas
            fecha_inicio = convertir_fecha(input("Por favor, ingresa la fecha de inicio (formato YYYYMMDD): "))
            fecha_fin = convertir_fecha(input("Por favor, ingresa la fecha de fin (formato YYYYMMDD): "))

            # Hacer la consulta SQL
            c.execute(f"""
                SELECT * FROM stocks
                WHERE name = '{ticker}' AND date BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
            """)

            # Imprimir los resultados
            df = pd.DataFrame(c.fetchall(), columns=['name', 'date', 'close'])
            print(df)
            grafico = input("¿Quiere visualizar el gráfico? (s/n): ")
            if grafico.lower() == 's':
                    # Convertir la columna 'date' a formato de fecha
                    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
                    # Crear el gráfico
                    plt.figure(figsize=(10, 6))
                    plt.plot(df['date'], df['close'])
                    plt.title('Historial de precios de cierre')
                    plt.xlabel('Fecha')
                    plt.ylabel('Precio de cierre')
                    plt.grid(True)
                    plt.show()
                    # Preguntar al usuario si quiere comparar los datos con otro ticker
                    comparar = input("¿Quieres comparar los datos con otro ticker? (si/no): ")
                    if comparar.lower() == 'si':
                        # Solicitar al usuario el valor del segundo ticker
                        ticker2 = input("Por favor, ingresa el valor del segundo ticker: ")
                        ticker2 = ticker2.upper()  # Convertir el ticker a mayúsculas
                        # Hacer la solicitud a la API para el segundo ticker
                        url2 = f"https://financialmodelingprep.com/api/v3/historical-chart/4hour/{ticker2}?from={fecha_inicio}&to={fecha_fin}&apikey=DdNI6qCLlZsXjjmgCDR6qEohCeAzqmiW"
                        response2 = requests.get(url2)
                        data2 = response2.json()
                        # Insertar los nuevos datos en la base de datos
                        for stock in data2:
                            if fecha_inicio <= stock['date'] <= fecha_fin:
                                c.execute("INSERT INTO stocks VALUES (?, ?, ?)",
                                          (ticker2, stock['date'], stock['close']))
                        print(f"Se guardaron los datos de la acción {ticker2} desde {fecha_inicio} hasta {fecha_fin}.")
                        # Hacer la consulta SQL para el segundo ticker
                        c.execute(f"""
                            SELECT * FROM stocks
                            WHERE name = '{ticker2}' AND date BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
                        """)
                        # Crear el DataFrame para el segundo ticker
                        df2 = pd.DataFrame(c.fetchall(), columns=['name', 'date', 'close'])
                        # Convertir la columna 'date' a formato de fecha
                        df2['date'] = pd.to_datetime(df2['date'])
                        # Crear el gráfico comparativo
                        plt.figure(figsize=(10, 6))
                        plt.plot(df['date'], df['close'], label=ticker)
                        plt.plot(df2['date'], df2['close'], label=ticker2)
                        plt.title('Comparación de precios de cierre')
                        plt.xlabel('Fecha')
                        plt.ylabel('Precio de cierre')
                        plt.legend()
                        plt.grid(True)
                        plt.show()
        else:
            print("Opción inválida. Por favor, ingresa 'ultimo' o 'historial'.")
    elif accion.lower() == 'resumen':
        # Hacer la consulta SQL para obtener el resumen
        c.execute("""
            SELECT name, MIN(date), MAX(date)
            FROM stocks
            GROUP BY name
        """)
        # Imprimir el resumen
        resumen = pd.DataFrame(c.fetchall(), columns=['Ticker', 'Fecha inicial', 'Fecha final'])
        print(resumen)
    
    elif accion.lower() == 'datos':
        # Solicitar al usuario el valor del ticker, una fecha de inicio y una fecha de fin
        ticker = input("Por favor, ingresa el valor del ticker: ")
        ticker = ticker.upper()  # Convertir el ticker a mayúsculas
        fecha_inicio = convertir_fecha(input("Por favor, ingresa la fecha de inicio (formato YYYYMMDD): "))
        fecha_fin = convertir_fecha(input("Por favor, ingresa la fecha de fin (formato YYYYMMDD): "))

        # Validar las fechas
        try:
            datetime.strptime(fecha_inicio, '%Y-%m-%d')
            datetime.strptime(fecha_fin, '%Y-%m-%d')
        except ValueError:
            print("Fecha inválida. Por favor, ingresa la fecha en formato YYYY-MM-DD.")
            continue

        # Hacer la solicitud a la API
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/4hour/{ticker}?from={fecha_inicio}&to={fecha_fin}&apikey=DdNI6qCLlZsXjjmgCDR6qEohCeAzqmiW"
        response = requests.get(url)
        data = response.json()

        # Insertar los nuevos datos en la base de datos
        for stock in data:
            if fecha_inicio <= stock['date'] <= fecha_fin:
                c.execute("INSERT INTO stocks VALUES (?, ?, ?)",
                          (ticker, stock['date'], stock['close']))
        print(f"Se guardaron los datos de la acción {ticker} desde {fecha_inicio} hasta {fecha_fin}.")
        # Leer todos los datos de la base de datos
        c.execute("SELECT * FROM stocks")
        data = c.fetchall()
        df = pd.DataFrame(data, columns=['name', 'date', 'close'])
        df['date'] = pd.to_datetime(df['date'].str.split(" ").str[0])
        # Convertir la columna 'date' a formato de fecha
        df['date'] = pd.to_datetime(df['date'])

        # Eliminar los datos duplicados
        df.drop_duplicates(subset=['name', 'date', 'close'], keep='first', inplace=True)

        # Ordenar los datos por ticker y fecha
        df.sort_values(by=['name', 'date'], inplace=True)

        # Actualizar la base de datos
        c.execute("DELETE FROM stocks")  # Eliminar todos los datos existentes
        for row in df.itertuples():
            c.execute("INSERT INTO stocks VALUES (?, ?, ?)",
                      (row.name, row.date.strftime('%Y-%m-%d'), row.close))

        # Guardar los cambios
        conn.commit()

        print("La base de datos se ha actualizado correctamente.")

        # Guardar los cambios
        conn.commit()
    else:
        print("Opción inválida. Por favor, ingresa 'consulta', 'datos' o 'salir'.")

# Preguntar al usuario si desea volver al menú de inicio
    volver_inicio = input("¿Desea volver al menú de inicio? (si/no): ")
    if volver_inicio.lower() != 'si':
        break  #

# Cerrar la conexión
conn.close()
