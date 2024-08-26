import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib import cm

# Definimos las variables N, L y M a nivel del script
N = 0  # Número de partículas (será leído del archivo static.txt)
L = 0  # Tamaño del gráfico (será leído del archivo static.txt)
M = 0  # Valor adicional si es necesario (por ejemplo, para dimensiones adicionales)

min_radius = 1
default_color = 'black'


# Función para leer el archivo static.txt
def read_static_file(filename):
    global N, L
    with open(filename, 'r') as file:
        L = float(file.readline().strip())
        N = int(file.readline().strip())
        particles_info = []
        for idx in range(N):
            radius, color = file.readline().strip().split()
            radius = float(radius)
            particles_info.append((idx, radius, color))
    return (N, L, particles_info)


# Función para leer el archivo dynamic.txt
def read_dynamic_file(filename, N):
    timesteps = []
    with open(filename, 'r') as file:
        while True:
            time_line = file.readline().strip()
            if not time_line:
                break
            t = float(time_line)
            particle_states = []
            for i in range(N):
                values = file.readline().strip().split('\t')
                idx = int(values[0])
                x = float(values[1])
                y = float(values[2])
                v = float(values[3])
                theta = float(values[4])
                particle_states.append((idx, x, y, v, theta))
            timesteps.append((t, particle_states))
    return timesteps


# Función para convertir ángulo en color usando colormap 'hsv'
def angle_to_color(theta):
    # Normaliza el ángulo theta al rango [0, 1]
    normalized_value = (theta % (2 * np.pi)) / (2 * np.pi)
    # Convierte el valor normalizado a un color usando la colormap hsv
    color = cm.hsv(normalized_value)
    return color

def angle_to_gray(theta):
    # Normaliza el ángulo theta al rango [0, 1]
    normalized_value = (theta % (2 * np.pi)) / (2 * np.pi)
    # Mapea el valor normalizado a una escala de grises
    gray_value = str(normalized_value)  # Matplotlib acepta cadenas para colores de grises, e.g., '0.5'
    return gray_value


# Función para actualizar la animación
def update(frame, arrows, timesteps):
    _, particle_states = timesteps[frame]
    for i, arrow in enumerate(arrows):
        idx, x, y, v, theta = particle_states[i]

        # Calculamos las componentes x e y de la velocidad
        u = v * np.cos(theta)
        w = v * np.sin(theta)

        # Escalar las posiciones para hacer la flecha visible
        start_x = x - u * 0.05 * L  # Ajusta el factor de escala 0.1 según sea necesario
        start_y = y - w * 0.05 * L
        end_x = x + u * 0.05 * L
        end_y = y + w * 0.05 * L

        # Asigna el color en escala de grises según el ángulo
        gray_color = angle_to_color(theta)
        arrow.set_color(gray_color)

        # Actualizamos la posición y dirección de la flecha con cola
        arrow.set_positions((start_x, start_y), (end_x, end_y))

    return arrows


# Función principal para generar la animación
def animate_particles(static_file, dynamic_file):
    N, L, particles_info = read_static_file(static_file)
    timesteps = read_dynamic_file(dynamic_file, N)

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    arrows = []
    for idx, radius, _ in particles_info:
        # Escalar la flecha según L
        arrow = patches.FancyArrowPatch((0, 0), (0, 0), color='red', arrowstyle='-|>', mutation_scale=0.25 * L)
        ax.add_patch(arrow)
        arrows.append(arrow)

    ani = FuncAnimation(fig, update, frames=len(timesteps), fargs=(arrows, timesteps), repeat=False, blit=False)
    plt.show()


# Función para mostrar un frame específico
def show_specific_frame(static_file, dynamic_file, frame_number):
    N, L, particles_info = read_static_file(static_file)
    timesteps = read_dynamic_file(dynamic_file, N)

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    scatters = []
    quivers = []
    for idx, radius, _ in particles_info:
        scatter = patches.Circle((0, 0), max(radius, min_radius), fc=default_color)  # Radio mínimo de 0.5
        ax.add_patch(scatter)
        scatters.append(scatter)

        # Añadimos la flecha de velocidad
        if idx == 10:
            quiver = ax.quiver(0, 0, 0, 0, angles='xy', scale_units='xy', scale=1, color='blue')
            quivers.append(quiver)
        else:
            quiver = ax.quiver(0, 0, 0, 0, angles='xy', scale_units='xy', scale=1, color='red')
            quivers.append(quiver)

    # Actualizar el frame específico
    update(frame_number, scatters, quivers, timesteps)

    plt.show()


# Llamada a la función principal con los archivos correspondientes
animate_particles('static', 'dynamic')

# show_specific_frame('static.txt', 'dynamic.txt', 0)