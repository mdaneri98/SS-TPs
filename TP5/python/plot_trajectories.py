import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

class ParticleData:
    def __init__(self):
        self.times = []
        self.particles = {}
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

                try:
                    time = float(line)
                    current_time = time
                    self.times.append(time)
                    continue
                except ValueError:
                    pass

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


def plot_particle_trajectories(data):
    """
    Grafica la trayectoria de cada partícula a lo largo del tiempo, con colores variados.
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Configurar los límites del campo
    ax.set_xlim(0, data.static_params['width'])
    ax.set_ylim(0, data.static_params['height'])
    ax.set_title("Trayectorias de las partículas")

    # Colormap para asignar colores a cada partícula
    colors = cm.jet(np.linspace(0, 1, len(data.particles)))

    # Dibujar la trayectoria de cada partícula
    for i, (pid, particle_data) in enumerate(data.particles.items()):
        ax.plot(particle_data['x'], particle_data['y'], color=colors[i], alpha=0.7)

    plt.show()


def main():
    data = ParticleData()
    data.load_static('outputs/try_maradoniano/static.txt')
    data.load_dynamic('outputs/try_maradoniano/dynamic.txt')

    # Graficar las trayectorias de las partículas
    plot_particle_trajectories(data)


if __name__ == '__main__':
    main()
