import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Función para leer el archivo y extraer la información de las partículas
def read_dynamic_file(filename):
    data = {}
    current_time = None
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                # Si la línea es un tiempo, la convertimos a float y la usamos como clave
                if line.replace('.', '', 1).isdigit():
                    current_time = float(line)
                    data[current_time] = []
                else:
                    # Si no es un tiempo, es información de una partícula
                    particle_data = line.split(',')
                    particle = {
                        'id': int(particle_data[0]),
                        'x': float(particle_data[1]),
                        'y': float(particle_data[2]),
                        'vx': float(particle_data[3]),
                        'vy': float(particle_data[4]),
                        'r': float(particle_data[5]),
                        'puerta': int(particle_data[6])
                    }
                    data[current_time].append(particle)
    return data

# Leer los datos del archivo 'dynamic.txt'
filename = 'outputs/probabilistic_analysis/t_10_&_p_0.10/sim_000/dynamic.txt'
data = read_dynamic_file(filename)

# Calcular el número de partículas N(t) y el caudal Q(t)
# Supongamos que los tiempos son las claves del diccionario 'data'

times = sorted(data.keys())  # Ordenar los tiempos
particles_per_time = []  # Lista para almacenar el número de partículas por tiempo
Q_t = []  # Lista para almacenar el caudal por tiempo
dt = 3.75  # Intervalo de tiempo en segundos

# Inicializar la lista de partículas anteriores (en el tiempo t-1)
previous_particles = None

for time in times:
    current_particles = data[time]  # Las partículas en el tiempo actual
    particles_per_time.append(len(current_particles))  # Número de partículas en t
    if previous_particles is not None:
        # Calcular el caudal Q(t) en función de las partículas que salieron
        Q_t.append(particles_per_time[-2] - particles_per_time[-1])  # Q(t) = N(t) - N(t+1)
    else:
        Q_t.append(0)  # Al principio, no hay caudal, ya que no tenemos partículas anteriores

    # Actualizar las partículas anteriores para el siguiente paso de tiempo
    previous_particles = current_particles

# Interpolación de Q(t)
interpolator = interp1d(times, Q_t, kind='linear', fill_value="extrapolate")

# Generar puntos intermedios
interpolated_times = np.linspace(min(times), max(times),
                                 num=500)  # Generamos 500 puntos entre el mínimo y máximo tiempo
interpolated_Q_t = interpolator(interpolated_times)

# Mostrar los resultados
for i, time in enumerate(times):
    print(f"Tiempo: {time}, Q(t): {Q_t[i]}")

# Ahora puedes graficar los resultados en el mismo gráfico
plt.figure(figsize=(12, 6))

# Gráfico combinado de Q(t) (caudal total por tiempo) y Q(t) interpolado
plt.plot(times, Q_t, 'o-', label="Caudal Total Q(t)", color="blue")
plt.plot(interpolated_times, interpolated_Q_t, 'o-', label="Caudal Interpolado Q(t)", color="red")

# Títulos y etiquetas
plt.title("Caudal Total y Caudal Interpolado en función del Tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Q(t)")
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
