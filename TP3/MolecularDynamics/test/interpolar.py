import numpy as np


def leer_datos(archivo):
    """
    Lee los datos del archivo, separando los tiempos y las partículas.
    """
    datos = []
    tiempos = []
    with open(archivo, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            try:
                # Si la línea solo tiene un número, es un tiempo
                tiempo = float(lines[i].strip())
                tiempos.append(tiempo)
                i += 1
                particulas_tiempo = []

                # Leer las partículas hasta que llegue una línea que es tiempo o el final del archivo
                while i < len(lines) and len(lines[i].strip().split()) > 1:
                    particula = list(map(float, lines[i].strip().split()))
                    particulas_tiempo.append(particula)
                    i += 1

                datos.append((tiempo, particulas_tiempo))
            except ValueError:
                i += 1
    return datos, tiempos


def interpolar_posiciones(datos, tiempos, intervalo):
    """
    Rellena los huecos en las posiciones de las partículas mediante interpolación lineal.

    datos: lista con (tiempo, lista de partículas con [id, x, y, vx, vy])
    tiempos: lista de tiempos en los que se tienen datos
    intervalo: intervalo de tiempo para rellenar los huecos.

    Retorna: un diccionario con posiciones interpoladas para cada partícula.
    """
    tiempo_total = max(tiempos)
    tiempos_interpolados = np.arange(0, tiempo_total + intervalo, intervalo)
    interpolaciones = {}

    # Obtener el número de partículas
    num_particulas = 10#max(max([p[0] for _, ps in datos for p in ps]), key=int) + 1

    for i in range(int(num_particulas)):
        tiempos_particula = []
        posiciones_x = []
        posiciones_y = []
        velocidades_x = []
        velocidades_y = []

        # Recopilar datos de la partícula i en cada tiempo disponible
        for tiempo, particulas in datos:
            for particula in particulas:
                if int(particula[0]) == i:
                    tiempos_particula.append(tiempo)
                    posiciones_x.append(particula[1])
                    posiciones_y.append(particula[2])
                    velocidades_x.append(particula[3])
                    velocidades_y.append(particula[4])
                    break

        # Si tenemos al menos dos puntos, realizamos la interpolación
        if len(tiempos_particula) >= 2:
            pos_x_interpolada = np.interp(tiempos_interpolados, tiempos_particula, posiciones_x)
            pos_y_interpolada = np.interp(tiempos_interpolados, tiempos_particula, posiciones_y)

            # Para cada partícula interpolada, asumimos que la velocidad es constante
            interpolaciones[i] = []
            for t in range(len(tiempos_interpolados)):
                # Buscar la velocidad más cercana en los datos originales
                velocidad_x = np.interp(tiempos_interpolados[t], tiempos_particula, velocidades_x)
                velocidad_y = np.interp(tiempos_interpolados[t], tiempos_particula, velocidades_y)
                interpolaciones[i].append(
                    (tiempos_interpolados[t], pos_x_interpolada[t], pos_y_interpolada[t], velocidad_x, velocidad_y))

    return interpolaciones


def guardar_interpolaciones_formato(interpolaciones, tiempos_interpolados, archivo_salida):
    """
    Guarda las posiciones interpoladas en un archivo de salida con el formato solicitado.

    interpolaciones: diccionario con las posiciones interpoladas y velocidades.
    tiempos_interpolados: lista de tiempos en los que se han interpolado los datos.
    archivo_salida: nombre del archivo donde se guardarán los resultados.
    """
    with open(archivo_salida, 'w') as f:
        for tiempo in tiempos_interpolados:
            f.write(f"{tiempo:.6f}\n")
            for particula, posiciones in interpolaciones.items():
                for t, x, y, vx, vy in posiciones:
                    if np.isclose(t, tiempo):
                        f.write(f"{particula}\t{x:.6f}\t{y:.6f}\t{vx:.6f}\t{vy:.6f}\n")


# Ejecución principal
if __name__ == "__main__":
    # Nombre del archivo de entrada
    archivo_entrada = "output/dynamic.txt"

    # Leer los datos del archivo
    datos, tiempos = leer_datos(archivo_entrada)

    # Parámetros de la interpolación
    intervalo = 0.25  # Define el intervalo de tiempo para la interpolación

    # Realizar la interpolación
    posiciones_interpoladas = interpolar_posiciones(datos, tiempos, intervalo)

    # Obtener la lista de tiempos interpolados
    tiempo_total = max(tiempos)
    tiempos_interpolados = np.arange(0, tiempo_total + intervalo, intervalo)

    # Guardar los resultados en un archivo de salida
    archivo_salida = "output/interpolated_dynamic.txt"
    guardar_interpolaciones_formato(posiciones_interpoladas, tiempos_interpolados, archivo_salida)

    print(f"Interpolación completada. Datos guardados en {archivo_salida}")
