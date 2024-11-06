import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os

class ParticleData:
    # [La clase ParticleData permanece igual...]
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

def create_frame(data, frame_index, output_dir=None):
    """
    Crea un gráfico para un frame específico y opcionalmente lo guarda
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Configurar los límites del campo
    ax.set_xlim(0, data.static_params['width'])
    ax.set_ylim(0, data.static_params['height'])

    # Factor de escala para las flechas de velocidad
    scale_factor = 0.0001 * min(data.static_params['width'], data.static_params['height'])

    # Limpiar el gráfico anterior
    ax.clear()
    ax.set_xlim(0, data.static_params['width'])
    ax.set_ylim(0, data.static_params['height'])

    # Dibujar cada partícula
    for pid in data.particles.keys():
        color = 'blue' if pid == 0 else 'red'
        
        circle = plt.Circle((data.particles[pid]['x'][frame_index],
                           data.particles[pid]['y'][frame_index]),
                          data.particles[pid]['radius'][frame_index],
                          color=color,
                          alpha=0.5)
        ax.add_artist(circle)

        ax.quiver(data.particles[pid]['x'][frame_index],
                 data.particles[pid]['y'][frame_index],
                 data.particles[pid]['vx'][frame_index] * scale_factor,
                 data.particles[pid]['vy'][frame_index] * scale_factor,
                 angles='xy', scale_units='xy', scale=1, color='black')

    ax.set_title(f'Tiempo: {data.times[frame_index]:.2f}s')

    # Si se especifica un directorio de salida, guardar el frame
    if output_dir is not None:
        plt.savefig(os.path.join(output_dir, f'frame_{frame_index:04d}.png'))
        plt.close()
    
    return fig, ax

def animate_particles(data, output_dir):
    """
    Crea y guarda la animación y los frames individuales
    """
    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, data.static_params['width'])
    ax.set_ylim(0, data.static_params['height'])

    scale_factor = 0.0001 * min(data.static_params['width'], data.static_params['height'])
    
    def update(frame):
        # Limpiar el gráfico anterior
        ax.clear()
        ax.set_xlim(0, data.static_params['width'])
        ax.set_ylim(0, data.static_params['height'])
        
        # Dibujar las partículas para este frame
        artists = []
        for pid in data.particles.keys():
            color = 'blue' if pid == 0 else 'red'
            
            circle = plt.Circle((data.particles[pid]['x'][frame],
                               data.particles[pid]['y'][frame]),
                              data.particles[pid]['radius'][frame],
                              color=color,
                              alpha=0.5)
            ax.add_artist(circle)
            artists.append(circle)

            quiver = ax.quiver(data.particles[pid]['x'][frame],
                             data.particles[pid]['y'][frame],
                             data.particles[pid]['vx'][frame] * scale_factor,
                             data.particles[pid]['vy'][frame] * scale_factor,
                             angles='xy', scale_units='xy', scale=1, color='black')
            artists.append(quiver)

        ax.set_title(f'Tiempo: {data.times[frame]:.2f}s')
        
        # Guardar el frame actual
        plt.savefig(os.path.join(output_dir, f'frame_{frame:04d}.png'))
        
        return artists

    frames = len(data.times)
    ani = animation.FuncAnimation(fig, update, frames=frames,
                                interval=50, blit=True)
    
    # Guardar la animación como GIF
    ani.save(os.path.join(output_dir, 'animation.gif'), writer='pillow')
    plt.close()

def main():
    # Directorio base donde están las simulaciones
    base_dir = 'outputs/heuristic_analysis'
    
    # Recorrer todas las carpetas de ap_bp
    for ap_bp_dir in os.listdir(base_dir):
        if ap_bp_dir.startswith('ap_'):
            # Construir la ruta a la simulación 0
            sim_path = os.path.join(base_dir, ap_bp_dir, 'sim_000')
            
            # Verificar que exista la simulación 0
            if not os.path.exists(sim_path):
                continue
                
            # Cargar los datos de la simulación
            data = ParticleData()
            static_file = os.path.join(sim_path, 'static.txt')
            dynamic_file = os.path.join(sim_path, 'dynamic.txt')
            
            # Verificar que existan los archivos necesarios
            if not (os.path.exists(static_file) and os.path.exists(dynamic_file)):
                continue
                
            data.load_static(static_file)
            data.load_dynamic(dynamic_file)
            
            # Crear directorio para los frames dentro de sim_000
            frames_dir = os.path.join(sim_path, 'frames')
            
            # Generar la animación
            animate_particles(data, frames_dir)
            
            print(f"Procesado {ap_bp_dir} - simulación 000")

if __name__ == '__main__':
    main()