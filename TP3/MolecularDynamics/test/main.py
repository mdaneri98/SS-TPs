import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from models import Particle, State


# Función para leer el archivo static.txt
def read_static(file_path):
    with open(file_path, 'r') as f:
        L = float(f.readline().strip())  # Largo del cuadrado
        N = int(f.readline().strip())  # Número de partículas
        particles = []
        for _ in range(N):
            line = f.readline().strip().split()
            radius = float(line[0])
            mass = float(line[1])
            color = int(line[2])
            particles.append((radius, mass, color))
    return L, N, particles


# Función para leer el archivo dynamic.txt
def read_dynamic(file_path):
    states = []
    with open(file_path, 'r') as f:
        while True:
            try:
                particles_list = []
                time = float(f.readline().strip())  # Lee el tiempo
                for _ in range(N):
                    line = f.readline().strip().split()
                    particle_id = int(line[0])
                    x = float(line[1])
                    y = float(line[2])
                    vx = float(line[3])
                    vy = float(line[4])
                    particles_list.append(Particle(particle_id, x, y, vx, vy))
                states.append(State(time, particles_list))
            except:
                print("Termino abruptamente con {} states!".format(len(states)))
                break
    return states


def interpolate_position(p0, v, t):
    """Interpolar la posición de la partícula en función del tiempo y velocidad."""
    return p0 + v * t

def plot_particles(L, states, frame_rate=30):
    fig, ax = plt.subplots()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    colors = ['red', 'blue', 'green', 'purple', 'orange', 'yellow', 'brown', 'pink', 'gray', 'cyan']

    # Para cada par de estados
    for state_id in range(len(states) - 1):
        state_start = states[state_id]
        state_end = states[state_id + 1]
        delta_time = state_end.time - state_start.time

        # Crear interpolaciones en función del frame_rate
        num_frames = int(delta_time * frame_rate)
        time_step = delta_time / num_frames

        for frame in range(num_frames):
            current_time = state_start.time + frame * time_step
            ax.clear()
            ax.set_title(f'Time: {current_time:.3f}')
            ax.set_xlim(0, L)
            ax.set_ylim(0, L)

            # Dibujar cada partícula
            for i, (radius, _, color) in enumerate(particles):
                start_particle = state_start.particles[i]
                end_particle = state_end.particles[i]

                # Interpolar posición
                interpolated_x = interpolate_position(start_particle.x, start_particle.vx, frame * time_step)
                interpolated_y = interpolate_position(start_particle.y, start_particle.vy, frame * time_step)

                # Crear un círculo para la partícula
                circle = patches.Circle((interpolated_x, interpolated_y), radius, color=colors[color], fill=True)
                ax.add_patch(circle)

                # Si no es la partícula fija, dibujar la flecha de velocidad
                if start_particle.id != 0:
                    ax.arrow(interpolated_x, interpolated_y, start_particle.vx * 0.01, start_particle.vy * 0.01,
                             head_width=0.005, head_length=0.01, fc='black', ec='black')

            plt.pause(0.1)  # Pausa para la animación

    plt.show()


# Cargar los datos
L, N, particles = read_static('output/static.txt')
states = read_dynamic('output/dynamic.txt')

# Graficar el movimiento de las partículas
plot_particles(L, states)
