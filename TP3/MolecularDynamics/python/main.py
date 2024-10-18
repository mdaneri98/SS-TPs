import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

from models import Particle, State



N = 0  # Número de partículas (será leído del archivo static.txt)
L = 0  # Tamaño del gráfico (será leído del archivo static.txt)



# Función para leer el archivo static.txt
def read_static_file(filename):
    global N, L
    with open(filename, 'r') as file:
        L = float(file.readline().strip())
        N = int(file.readline().strip())
        particles_info = []
        for idx in range(N):
            line = file.readline().strip().split()
            radius = float(line[0])
            mass = float(line[1])
            color = int(line[2])
            particles_info.append((radius, mass, color))

    return (N, L, particles_info)


def read_dynamic_file(filename, particles_info, N):
    states = []
    with open(filename, 'r') as file:
        while True:
            time_line = file.readline().strip()
            if not time_line:
                break
            time = float(time_line)
            particles_list = []
            for i in range(N):
                line = file.readline().strip().split()
                idx = int(line[0])
                x = float(line[1])
                y = float(line[2])
                vx = float(line[3])
                vy = float(line[4])
                particles_list.append(Particle(idx, particles_info[i][0], particles_info[i][1], x, y, vx, vy))
            states.append(State(time, particles_list))
    return states


# Función para interpolar posiciones
def interpolate_position(start_pos, velocity, delta_time):
    return start_pos + velocity * delta_time


def update(frame, states, arrows, L):
    state_start = states[frame]
    state_end = states[min(frame + 1, len(states) - 1)]  # Asegurarse de no salir del índice

    delta_time = state_end.time - state_start.time if state_end.time != state_start.time else 1

    for i, arrow in enumerate(arrows):
        start_particle = state_start.particles[i]
        end_particle = state_end.particles[i]

        # Interpolación de las posiciones
        interpolated_x = interpolate_position(start_particle.x, start_particle.vx, delta_time)
        interpolated_y = interpolate_position(start_particle.y, start_particle.vy, delta_time)

        # Componentes de la velocidad
        u = start_particle.vx
        w = start_particle.vy

        # Actualizamos la posición y dirección de la flecha
        start_x = interpolated_x - u * 0.05 * L
        start_y = interpolated_y - w * 0.05 * L
        end_x = interpolated_x + u * 0.05 * L
        end_y = interpolated_y + w * 0.05 * L

        # Actualizamos la flecha
        arrow.set_positions((start_x, start_y), (end_x, end_y))

    return arrows  # Devuelve solo los objetos que se redibujan

# Función principal para animar las partículas
def animate_particles(static_file, dynamic_file):
    N, L, particles_info = read_static_file(static_file)
    states = read_dynamic_file(dynamic_file, particles_info, N)

    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    # Creamos las flechas para las partículas
    arrows = []
    for _ in range(N):
        arrow = patches.FancyArrowPatch((0, 0), (0, 0), color='red', arrowstyle='-|>', mutation_scale=10)
        ax.add_patch(arrow)
        arrows.append(arrow)

    # Número de frames basado en el número de estados
    num_frames = len(states)

    # FuncAnimation para la animación
    ani = FuncAnimation(fig, update, frames=num_frames, fargs=(states, arrows, L), interval=1000, repeat=False, blit=True)
    plt.show()


# Cargar los datos
# L, N, particles_info = read_static('output/static.txt')
# states = read_dynamic('output/dynamic.txt', particles_info)

# Graficar el movimiento de las partículas
animate_particles('output/static.txt', 'output/posiciones_interpoladas_formato.txt')
