import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from pathlib import Path
import os
import logging
import csv

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ParticleData:
    def __init__(self):
        self.times = []
        self.particles = {}
        self.static_params = {}
        self.frames_data = []
        self.doors = []

    def load_doors(self, filename):
        """Carga las coordenadas de las puertas desde un archivo CSV"""
        logging.debug(f"Leyendo archivo de puertas: {filename}")
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                self.doors = []
                for row in reader:
                    door = {
                        'x1': float(row['initial_x'].strip()),
                        'y1': float(row['initial_y'].strip()),
                        'x2': float(row['end_x'].strip()),
                        'y2': float(row['end_y'].strip())
                    }
                    self.doors.append(door)
                logging.debug(f"Puertas cargadas: {len(self.doors)}")
        except Exception as e:
            logging.error(f"Error al cargar archivo de puertas: {e}")
            raise

    def load_static(self, filename):
        logging.debug(f"Leyendo archivo estático: {filename}")
        try:
            with open(filename, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                params = {}

                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        try:
                            if '.' in value:
                                params[key] = float(value)
                            else:
                                params[key] = int(value)
                        except ValueError:
                            logging.warning(f"No se pudo convertir el valor '{value}' para la clave '{key}'")
                            continue

                logging.debug(f"Parámetros encontrados: {params}")

                required_params = ['maxVelocity', 'tau', 'rMin', 'rMax', 'width', 'height']
                missing_params = [param for param in required_params if param not in params]

                if missing_params:
                    logging.error(f"Faltan parámetros requeridos: {missing_params}")
                    logging.debug(f"Contenido del archivo:\n{lines}")
                    raise ValueError(f"Faltan parámetros requeridos: {missing_params}")

                self.static_params = params

        except Exception as e:
            logging.error(f"Error al cargar archivo estático: {e}")
            raise

    def load_dynamic(self, filename):
        logging.debug(f"Iniciando carga de archivo dinámico: {filename}")
        current_frame = {"time": None, "particles": []}

        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        time = float(line)
                        if current_frame["time"] is not None:
                            self.frames_data.append(current_frame)
                        current_frame = {"time": time, "particles": []}
                        self.times.append(time)
                        continue
                    except ValueError:
                        pass

                    parts = line.split(',')
                    if len(parts) == 6:
                        try:
                            particle_data = {
                                'id': int(parts[0]),
                                'x': float(parts[1]),
                                'y': float(parts[2]),
                                'vx': float(parts[3]),
                                'vy': float(parts[4]),
                                'radius': float(parts[5])
                            }
                            current_frame["particles"].append(particle_data)
                        except ValueError as e:
                            logging.warning(f"Error al procesar línea de partícula: {line}, Error: {e}")
                            continue

                if current_frame["time"] is not None:
                    self.frames_data.append(current_frame)

            logging.debug(f"Carga completada. Frames totales: {len(self.frames_data)}")

        except Exception as e:
            logging.error(f"Error al cargar archivo dinámico: {e}")
            raise

def animate_particles(data, output_dir):
    logging.debug(f"Iniciando animación. Total frames: {len(data.frames_data)}")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8))

    scale_factor = 0.1

    def update(frame_idx):
        logging.debug(f"Procesando frame {frame_idx}")
        if frame_idx >= len(data.frames_data):
            logging.error(f"Índice de frame ({frame_idx}) fuera de rango")
            return []

        frame_data = data.frames_data[frame_idx]

        ax.clear()
        ax.set_xlim(0, data.static_params['width'])
        ax.set_ylim(0, data.static_params['height'])

        artists = []

        # Dibujar las puertas usando las coordenadas cargadas
        for door in data.doors:
            door_line = plt.Line2D([door['x1'], door['x2']],
                                   [door['y1'], door['y2']],
                                   color='green',
                                   linewidth=5)
            ax.add_artist(door_line)
            artists.append(door_line)

        # Dibujar cada partícula en el frame actual
        for particle in frame_data["particles"]:
            circle = plt.Circle((particle['x'], particle['y']),
                                particle['radius'],
                                color='blue',
                                alpha=0.5)
            ax.add_artist(circle)
            artists.append(circle)

            quiver = ax.quiver(particle['x'],
                               particle['y'],
                               particle['vx'] * scale_factor,
                               particle['vy'] * scale_factor,
                               angles='xy', scale_units='xy', scale=1,
                               color='black')
            artists.append(quiver)

        # Añadir contador de partículas
        ax.text(0.02, 0.98,
                f'Partículas: {len(frame_data["particles"])}',
                transform=ax.transAxes, verticalalignment='top')
        ax.set_title(f'Tiempo: {frame_data["time"]:.2f}s')

        plt.savefig(output_dir / f'frame_{frame_idx:04d}.png')

        return artists

    frames = len(data.frames_data)
    logging.debug(f"Creando animación con {frames} frames")

    ani = animation.FuncAnimation(fig, update, frames=frames,
                                  interval=50, blit=True)

    try:
        ani.save(output_dir / 'animation.gif', writer='pillow')
        logging.debug("Animación guardada exitosamente")
    except Exception as e:
        logging.error(f"Error al guardar la animación: {e}")

    plt.close()

def main():
    base_paths = [
        Path('outputs/heuristic_analysis'),
        Path('outputs/players_analysis')
    ]

    for base_dir in base_paths:
        if not base_dir.exists():
            logging.warning(f"Directorio {base_dir} no encontrado")
            continue

        logging.info(f"Procesando directorio base: {base_dir}")

        pattern = 'ap_*_bp_*' if 'heuristic_analysis' in str(base_dir) else 'N_*'

        for analysis_dir in base_dir.glob(pattern):
            if not analysis_dir.is_dir():
                continue

            logging.info(f"Procesando directorio: {analysis_dir}")

            for sim_dir in analysis_dir.glob('sim_*'):
                if not sim_dir.is_dir():
                    continue

                logging.info(f"Procesando simulación: {sim_dir}")

                static_file = sim_dir / 'static.txt'
                dynamic_file = sim_dir / 'dynamic.txt'
                doors_file = sim_dir / 'doors.csv'

                if not (static_file.exists() and dynamic_file.exists() and doors_file.exists()):
                    logging.warning(f"Archivos necesarios no encontrados en {sim_dir}")
                    continue

                try:
                    data = ParticleData()
                    data.load_doors(doors_file)
                    data.load_static(static_file)
                    data.load_dynamic(dynamic_file)

                    frames_dir = sim_dir / 'frames'
                    animate_particles(data, frames_dir)

                    logging.info(f"Procesamiento completado para {sim_dir}")

                except Exception as e:
                    logging.error(f"Error procesando {sim_dir}: {str(e)}")
                    import traceback
                    logging.error(traceback.format_exc())
                    continue

if __name__ == '__main__':
    main()