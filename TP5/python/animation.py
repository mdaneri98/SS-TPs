import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


class ParticleData:
    def __init__(self):
        self.times = []
        self.particles = {}  # Dictionary para guardar datos por ID
        self.static_params = {}

    def load_static(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            self.static_params = {
                'blueVelocityMax': float(lines[0].split(': ')[1]),
                'redVelocityMax': float(lines[1].split(': ')[1]),
                'blueTau': float(lines[2].split(': ')[1]),
                'redTau': float(lines[3].split(': ')[1]),
                'rMin': float(lines[4].split(': ')[1]),
                'rMax': float(lines[5].split(': ')[1]),
                'width': int(lines[6].split(': ')[1]),
                'height': int(lines[7].split(': ')[1])
            }

    def load_dynamic(self, filename):
        current_time = None
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Si es una línea de tiempo
                try:
                    time = float(line)
                    current_time = time
                    self.times.append(time)
                    continue
                except ValueError:
                    pass

                # Si es una línea de partícula
                parts = line.split(',')
                if len(parts) == 6:
                    pid = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    vx = float(parts[3])
                    vy = float(parts[4])
                    radius = float(parts[5])

                    if pid not in self.particles:
                        self.particles[pid] = {
                            'times': [],
                            'x': [],
                            'y': [],
                            'vx': [],
                            'vy': [],
                            'radius': []
                        }

                    self.particles[pid]['times'].append(current_time)
                    self.particles[pid]['x'].append(x)
                    self.particles[pid]['y'].append(y)
                    self.particles[pid]['vx'].append(vx)
                    self.particles[pid]['vy'].append(vy)
                    self.particles[pid]['radius'].append(radius)


def create_particle_plot(data, frame_index=0):
    """
    Crea un gráfico estático para un frame específico
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Configurar los límites del campo
    ax.set_xlim(0, data.static_params['width'])
    ax.set_ylim(0, data.static_params['height'])

    # Factor de escala para las flechas de velocidad
    scale_factor = 0.01 * min(data.static_params['width'], data.static_params['height'])

    # Dibujar cada partícula
    for pid in data.particles.keys():
        # Color según tipo de partícula
        color = 'blue' if pid == 0 else 'red'

        # Crear y añadir el círculo
        circle = plt.Circle((data.particles[pid]['x'][frame_index],
                             data.particles[pid]['y'][frame_index]),
                            data.particles[pid]['radius'][frame_index],
                            color=color,
                            alpha=0.5)
        ax.add_artist(circle)

        # Añadir vector de velocidad
        ax.quiver(data.particles[pid]['x'][frame_index],
                  data.particles[pid]['y'][frame_index],
                  data.particles[pid]['vx'][frame_index] * scale_factor,
                  data.particles[pid]['vy'][frame_index] * scale_factor,
                  angles='xy', scale_units='xy', scale=1, color='black')

    # Añadir título con el tiempo
    ax.set_title(f'Tiempo: {data.times[frame_index]:.2f}s')

    return fig, ax


def animate_particles(data):
    fig, ax = plt.subplots(figsize=(10, 8))

    # Configurar los límites del campo
    ax.set_xlim(0, data.static_params['width'])
    ax.set_ylim(0, data.static_params['height'])

    # Diccionario para guardar los círculos y vectores de velocidad de cada partícula
    circles = {}
    quiver_data = {'x': [], 'y': [], 'vx': [], 'vy': []}

    # Obtener los límites del gráfico para ajustar el tamaño de las flechas (1%)
    scale_factor = 0.01 * min(data.static_params['width'], data.static_params['height'])

    def init():
        for pid in data.particles.keys():
            # La partícula 0 es azul (jugador), el resto rojas
            color = 'blue' if pid == 0 else 'red'
            circle = plt.Circle((data.particles[pid]['x'][0],
                                 data.particles[pid]['y'][0]),
                                data.particles[pid]['radius'][0],
                                color=color,
                                alpha=0.5)
            circles[pid] = circle
            ax.add_artist(circle)

            # Inicializar datos de flechas
            quiver_data['x'].append(data.particles[pid]['x'][0])
            quiver_data['y'].append(data.particles[pid]['y'][0])
            quiver_data['vx'].append(data.particles[pid]['vx'][0] * scale_factor)
            quiver_data['vy'].append(data.particles[pid]['vy'][0] * scale_factor)

        # Crear el quiver inicial
        quiver = ax.quiver(quiver_data['x'], quiver_data['y'],
                           quiver_data['vx'], quiver_data['vy'],
                           angles='xy', scale_units='xy', scale=1, color='black')

        # Añadir título con el tiempo
        ax.set_title(f'Tiempo: {data.times[0]:.2f}s')

        return list(circles.values()) + [quiver]

    def update(frame):
        for i, (pid, circle) in enumerate(circles.items()):
            # Actualizar la posición del círculo (partícula)
            circle.center = (data.particles[pid]['x'][frame],
                             data.particles[pid]['y'][frame])

            # Actualizar los datos de quiver para velocidad, escalando
            quiver_data['x'][i] = data.particles[pid]['x'][frame]
            quiver_data['y'][i] = data.particles[pid]['y'][frame]
            quiver_data['vx'][i] = data.particles[pid]['vx'][frame] * scale_factor
            quiver_data['vy'][i] = data.particles[pid]['vy'][frame] * scale_factor

        # Redibujar el quiver con nuevos datos
        ax.collections[-1].set_offsets(np.c_[quiver_data['x'], quiver_data['y']])
        ax.collections[-1].set_UVC(quiver_data['vx'], quiver_data['vy'])

        # Actualizar título con el tiempo actual
        ax.set_title(f'Tiempo: {data.times[frame]:.2f}s')

        return list(circles.values()) + [ax.collections[-1]]

    frames = len(data.times)
    ani = animation.FuncAnimation(fig, update, frames=frames,
                                  init_func=init, blit=True,
                                  interval=50)  # 50ms entre frames

    plt.show()


def main():
    data = ParticleData()
    data.load_static('outputs/try_maradoniano/static.txt')
    data.load_dynamic('outputs/try_maradoniano/dynamic.txt')

    # Ejemplo de uso:
    # 1. Mostrar la animación completa
    animate_particles(data)

    # 2. Mostrar frames específicos
    # Frame inicial
    fig, ax = create_particle_plot(data, frame_index=0)
    plt.show()

    # Frame intermedio (frame 50)
    # fig, ax = create_particle_plot(data, frame_index=50)
    # plt.show()

    # Frame final
    fig, ax = create_particle_plot(data, frame_index=-1)
    plt.show()


if __name__ == '__main__':
    main()