import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from models import Particle

# Función para leer el archivo static.txt
def read_static_file(filename):
    with open(filename, 'r') as file:
        L = float(file.readline().strip())
        N = int(file.readline().strip())
        particles_info = []
        for idx in range(N):
            radius, mass, color = file.readline().strip().split('\t')
            radius = float(radius)
            particles_info.append((idx, radius, mass, color))
    return (N, L, particles_info)

# Función para leer el archivo dynamic.txt
def read_dynamic_file(filename, N, particles_info):
    states = []
    with open(filename, 'r') as file:
        while True:
            # Leer la línea del tiempo
            time_line = file.readline().strip()
            if not time_line:
                break  # Fin del archivo

            # Intentar convertir la línea en tiempo
            try:
                t = float(time_line)  # Aquí es donde debería estar el tiempo
            except ValueError:
                print(f"Advertencia: Se encontró una línea inesperada al intentar leer el tiempo: {time_line}")
                continue  # Saltar a la siguiente línea

            particles = []
            # Leer las siguientes N líneas, que corresponden a los datos de las partículas
            for _ in range(N):
                particle_line = file.readline().strip()
                if not particle_line:
                    break  # Si no hay más datos, salir del bucle

                values = particle_line.split('\t')
                if len(values) != 5:
                    print(f"Advertencia: Línea de datos inválida: {particle_line}")
                    continue  # Saltar a la siguiente línea

                try:
                    idx = int(values[0])
                    x = float(values[1])
                    y = float(values[2])
                    vx = float(values[3])
                    vy = float(values[4])
                except ValueError:
                    print(f"Advertencia: Valores de datos inválidos: {particle_line}")
                    continue  # Saltar a la siguiente línea

                radius = particles_info[idx][1]  # Obtener el radio desde static.txt
                mass = particles_info[idx][2]  # Obtener la masa desde static.txt

                # Crear instancia de Particle con los argumentos completos
                particle = Particle(idx, radius, mass, x, y, vx, vy)
                particles.append(particle)

            # Agregar el estado con el tiempo y la lista de partículas
            states.append((t, particles))

            # Leer la siguiente línea para verificar si es parte del próximo tiempo
            next_line = file.readline().strip()
            if next_line:
                # Si la siguiente línea no está vacía y puede ser convertida a float, se asume que es el siguiente tiempo
                try:
                    float(next_line)  # Verificar si la siguiente línea es un nuevo tiempo
                    file.seek(file.tell() - len(next_line) - 1)  # Revertir la lectura para la siguiente iteración
                except ValueError:
                    # Si no puede ser convertida a float, continuar con el siguiente bloque
                    file.seek(file.tell() - len(next_line) - 1)  # Revertir la lectura para la próxima iteración

    return states







# Función para graficar las trayectorias de todas las partículas
def plot_all_trajectories(static_file, dynamic_file):
    N, L, particles_info = read_static_file(static_file)
    states = read_dynamic_file(dynamic_file, N, particles_info)

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    # Diccionario para almacenar las posiciones de las partículas
    trajectories = {i: ([], []) for i in range(N)}

    # Recorrer todos los estados y agregar las posiciones de las partículas
    for _, particle_states in states:
        for particle in particle_states:
            trajectories[particle.id][0].append(particle.x)  # X positions
            trajectories[particle.id][1].append(particle.y)  # Y positions

    # Dibujar las trayectorias de todas las partículas
    for i, (x_traj, y_traj) in trajectories.items():
        color = 'orange' if i == 0 else 'black'
        ax.plot(x_traj, y_traj, label=f'Particle {i}', color=color)

    plt.title('Trayectorias de todas las partículas')
    plt.legend()
    plt.show()

# Llamada a la función para graficar todas las trayectorias
plot_all_trajectories('output/static.txt', 'output/dynamic.txt')
