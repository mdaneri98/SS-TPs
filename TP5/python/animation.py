import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import numpy as np
import os


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


def animate_particles(data, folder_path):
    fig, ax = plt.subplots(figsize=(10, 8))

    # Configurar los límites del campo
    width = data.static_params['width']
    height = data.static_params['height']
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)

    # Diccionario para guardar los círculos y vectores de velocidad de cada partícula
    circles = {}
    quiver_data = {'x': [], 'y': [], 'vx': [], 'vy': []}
    
    # Variables para mantener referencias a elementos dinámicos
    quiver = None
    ortho_lines = []
    
    # Polígonos para las áreas coloreadas
    front_area = patches.Polygon([(0, 0)], color='orange', alpha=0.2)
    back_area = patches.Polygon([(0, 0)], color='green', alpha=0.2)
    ax.add_patch(front_area)
    ax.add_patch(back_area)

    # Obtener los límites del gráfico para ajustar el tamaño de las flechas (1%)
    scale_factor = 0.01 * min(width, height)

    def create_area_vertices(x0, y0, ortho_vx, ortho_vy):
        # Encuentra los puntos de intersección con los bordes del área de juego
        def find_intersection(px, py, vx, vy):
            # Parametric line equation: p + t*v
            # Find smallest positive t that intersects with boundary
            ts = []
            # Intersección con x = 0
            if vx != 0:
                t = -px/vx
                y_int = py + t*vy
                if 0 <= y_int <= height and t > 0:
                    ts.append((t, 0, y_int))
            # Intersección con x = width
            if vx != 0:
                t = (width-px)/vx
                y_int = py + t*vy
                if 0 <= y_int <= height and t > 0:
                    ts.append((t, width, y_int))
            # Intersección con y = 0
            if vy != 0:
                t = -py/vy
                x_int = px + t*vx
                if 0 <= x_int <= width and t > 0:
                    ts.append((t, x_int, 0))
            # Intersección con y = height
            if vy != 0:
                t = (height-py)/vy
                x_int = px + t*vx
                if 0 <= x_int <= width and t > 0:
                    ts.append((t, x_int, height))
            
            if ts:
                t, x, y = min(ts, key=lambda x: x[0])
                return (x, y)
            return None

        # Encuentra los puntos de intersección en ambas direcciones
        p1 = find_intersection(x0, y0, ortho_vx, ortho_vy)
        p2 = find_intersection(x0, y0, -ortho_vx, -ortho_vy)

        if p1 is None or p2 is None:
            return None, None

        # Crea los vértices para las dos áreas
        corners = [(0, 0), (width, 0), (width, height), (0, height)]
        
        # Encuentra qué esquinas están en cada área
        front_corners = []
        back_corners = []
        
        for corner in corners:
            # Vector desde el punto de la línea hasta la esquina
            to_corner = (corner[0] - x0, corner[1] - y0)
            # Producto cruz 2D para determinar de qué lado está
            cross_product = ortho_vx * to_corner[1] - ortho_vy * to_corner[0]
            if cross_product > 0:
                front_corners.append(corner)
            else:
                back_corners.append(corner)

        # Ordenar los puntos para formar polígonos válidos
        front_vertices = sorted(front_corners + [p1, p2], key=lambda p: np.arctan2(p[1]-y0, p[0]-x0))
        back_vertices = sorted(back_corners + [p1, p2], key=lambda p: np.arctan2(p[1]-y0, p[0]-x0))

        return front_vertices, back_vertices

    def init():
        for pid in data.particles.keys():
            # La partícula 0 es azul (jugador), el resto rojas
            color = 'red' if pid == 0 else 'blue'
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
        nonlocal quiver
        quiver = ax.quiver(quiver_data['x'], quiver_data['y'],
                          quiver_data['vx'], quiver_data['vy'],
                          angles='xy', scale_units='xy', scale=1, color='black')

        # Inicializar líneas ortogonales
        nonlocal ortho_lines
        ortho_lines = [ax.plot([], [], color='gray', linestyle='--')[0],
                      ax.plot([], [], color='gray', linestyle='--')[0]]

        # Añadir título con el tiempo
        ax.set_title(f'Tiempo: {data.times[0]:.2f}s')

        return list(circles.values()) + [quiver] + ortho_lines + [front_area, back_area]

    def update(frame):
        # Actualizar círculos y datos de quiver
        for i, (pid, circle) in enumerate(circles.items()):
            # Actualizar la posición y el radio del círculo
            circle.center = (data.particles[pid]['x'][frame],
                           data.particles[pid]['y'][frame])
            circle.radius = data.particles[pid]['radius'][frame]

            # Actualizar los datos de quiver para velocidad
            quiver_data['x'][i] = data.particles[pid]['x'][frame]
            quiver_data['y'][i] = data.particles[pid]['y'][frame]
            quiver_data['vx'][i] = data.particles[pid]['vx'][frame] * scale_factor
            quiver_data['vy'][i] = data.particles[pid]['vy'][frame] * scale_factor

        # Actualizar quiver
        quiver.set_offsets(np.c_[quiver_data['x'], quiver_data['y']])
        quiver.set_UVC(quiver_data['vx'], quiver_data['vy'])

        # Actualizar líneas ortogonales y áreas coloreadas para la partícula id=0
        if 0 in data.particles:
            x0, y0 = data.particles[0]['x'][frame], data.particles[0]['y'][frame]
            vx = data.particles[0]['vx'][frame]
            vy = data.particles[0]['vy'][frame]
            norm = np.sqrt(vx**2 + vy**2)
            if norm > 0:  # Evitar división por cero
                ortho_vx, ortho_vy = -vy / norm, vx / norm
                
                # Definir los extremos de la línea ortogonal
                length = max(width, height)
                x_back = x0 - ortho_vx * length
                y_back = y0 - ortho_vy * length
                x_front = x0 + ortho_vx * length
                y_front = y0 + ortho_vy * length

                # Actualizar las líneas ortogonales
                ortho_lines[0].set_data([x0, x_front], [y0, y_front])  # Línea naranja
                ortho_lines[1].set_data([x_back, x0], [y_back, y0])    # Línea verde

                # Actualizar áreas coloreadas
                front_vertices, back_vertices = create_area_vertices(x0, y0, ortho_vx, ortho_vy)
                if front_vertices and back_vertices:
                    front_area.set_xy(front_vertices)
                    back_area.set_xy(back_vertices)
            else:
                # Si la velocidad es cero, ocultar las líneas y áreas
                ortho_lines[0].set_data([], [])
                ortho_lines[1].set_data([], [])
                front_area.set_xy([(0, 0)])
                back_area.set_xy([(0, 0)])

        # Actualizar título con el tiempo actual
        ax.set_title(f'Tiempo: {data.times[frame]:.2f}s')

        return list(circles.values()) + [quiver] + ortho_lines + [front_area, back_area]

    frames = len(data.times)
    ani = animation.FuncAnimation(fig, update, frames=frames,
                                init_func=init, blit=True,
                                interval=50)  # 50ms entre frames

    # Guardar la animación como un GIF
    gif_path = os.path.join(folder_path, 'animation.gif')
    ani.save(gif_path, writer='pillow', fps=10)

    print(f'Guardado GIF en: {gif_path}')
    plt.close(fig)


def main():
    folder_path = 'outputs/try_maradoniano/'
    
    data = ParticleData()
    data.load_static(folder_path + 'static.txt')
    data.load_dynamic(folder_path + 'dynamic.txt')

    animate_particles(data, folder_path)


if __name__ == "__main__":
    main()