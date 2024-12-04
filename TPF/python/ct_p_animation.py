import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from pathlib import Path
import os
import logging
import csv
import argparse

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
        self.door_colors = [
            '#FF0000', '#00FF00', '#0000FF', '#FFA500', '#800080',
            '#FFD700', '#00FFFF', '#FF00FF', '#008000', '#000080'
        ]
        self.door_color_map = {}

    def get_door_color(self, door_number):
        if door_number < 0:
            return '#808080'
        if door_number not in self.door_color_map:
            self.door_color_map[door_number] = self.door_colors[len(self.door_color_map) % len(self.door_colors)]
        return self.door_color_map[door_number]

    def load_doors(self, filename):
        logging.debug(f"Reading doors file: {filename}")
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                self.doors = []
                for i, row in enumerate(reader):
                    door = {
                        'x1': float(row['initial_x'].strip()),
                        'y1': float(row['initial_y'].strip()),
                        'x2': float(row['end_x'].strip()),
                        'y2': float(row['end_y'].strip()),
                        'id': i
                    }
                    self.doors.append(door)
                    self.get_door_color(i)
                logging.debug(f"Doors loaded: {len(self.doors)}")
        except Exception as e:
            logging.error(f"Error loading doors file: {e}")
            raise

    def load_static(self, filename):
        logging.debug(f"Reading static file: {filename}")
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
                            logging.warning(f"Could not convert value '{value}' for key '{key}'")
                            continue

                required_params = ['maxVelocity', 'tau', 'rMin', 'rMax', 'width', 'height']
                missing_params = [param for param in required_params if param not in params]

                if missing_params:
                    raise ValueError(f"Missing required parameters: {missing_params}")

                self.static_params = params

        except Exception as e:
            logging.error(f"Error loading static file: {e}")
            raise

    def load_dynamic(self, filename):
        logging.debug(f"Loading dynamic file: {filename}")
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
                    if len(parts) == 7:
                        try:
                            particle_data = {
                                'id': int(parts[0]),
                                'x': float(parts[1]),
                                'y': float(parts[2]),
                                'vx': float(parts[3]),
                                'vy': float(parts[4]),
                                'radius': float(parts[5]),
                                'doorNumber': int(parts[6])
                            }
                            current_frame["particles"].append(particle_data)
                        except ValueError as e:
                            logging.warning(f"Error processing particle line: {line}, Error: {e}")
                            continue

                if current_frame["time"] is not None:
                    self.frames_data.append(current_frame)

            logging.debug(f"Loading completed. Total frames: {len(self.frames_data)}")

        except Exception as e:
            logging.error(f"Error loading dynamic file: {e}")
            raise

def animate_particles(data, output_dir, save_frames=True):
    logging.info(f"Starting animation. Total frames: {len(data.frames_data)}")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    scale_factor = 0.1

    def update(frame_idx):
        if frame_idx >= len(data.frames_data):
            return []

        frame_data = data.frames_data[frame_idx]
        ax.clear()
        ax.set_xlim(0, data.static_params['width'])
        ax.set_ylim(0, data.static_params['height'])

        artists = []

        for door in data.doors:
            door_color = data.get_door_color(door['id'])
            door_line = plt.Line2D([door['x1'], door['x2']],
                                   [door['y1'], door['y2']],
                                   color=door_color,
                                   linewidth=5,
                                   label=f'Door {door["id"]}')
            ax.add_artist(door_line)
            artists.append(door_line)

        for particle in frame_data["particles"]:
            particle_color = data.get_door_color(particle['doorNumber'])
            circle = plt.Circle((particle['x'], particle['y']),
                                particle['radius'],
                                color=particle_color,
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

        handles = [plt.Line2D([0], [0], color=color, linewidth=5)
                   for color in data.door_color_map.values()]
        labels = [f'Door {door_id}' for door_id in data.door_color_map.keys()]
        ax.legend(handles, labels, loc='upper right', bbox_to_anchor=(1.15, 1))

        ax.text(0.02, 0.98,
                f'Particles: {len(frame_data["particles"])}',
                transform=ax.transAxes, verticalalignment='top')
        ax.set_title(f'Time: {frame_data["time"]:.2f}s')

        plt.tight_layout()

        if save_frames:
            plt.savefig(output_dir / f'frame_{frame_idx:04d}.png', bbox_inches='tight')

        return artists

    frames = len(data.frames_data)
    ani = animation.FuncAnimation(fig, update, frames=frames, interval=10, blit=True)

    try:
        writer = animation.PillowWriter(fps=30)
        ani.save(output_dir / 'animation.gif', writer=writer)
        logging.info("Animation saved successfully")
    except Exception as e:
        logging.error(f"Error saving animation: {e}")

    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Particle Visualization for Specific ct and p')
    parser.add_argument('--ct', type=int, required=True, help='Critical time value')
    parser.add_argument('--p', type=float, required=True, help='Probability value')
    parser.add_argument('--save-frames', action='store_true',
                        help='Save each frame as PNG in addition to GIF')
    args = parser.parse_args()

    # Construct the specific directory path
    base_dir = Path('outputs/probabilistic_analysis')
    target_dir = base_dir / f't_{args.ct}_&_p_{args.p:.2f}'

    if not target_dir.exists():
        logging.error(f"Directory not found: {target_dir}")
        return

    logging.info(f"Processing directory: {target_dir}")

    # Process each simulation in the target directory
    for sim_dir in target_dir.glob('sim_*'):
        if not sim_dir.is_dir():
            continue

        logging.info(f"Processing simulation: {sim_dir}")

        static_file = sim_dir / 'static.txt'
        dynamic_file = sim_dir / 'dynamic.txt'
        doors_file = sim_dir / 'doors.csv'

        if not all(f.exists() for f in [static_file, dynamic_file, doors_file]):
            logging.warning(f"Required files not found in {sim_dir}")
            continue

        try:
            data = ParticleData()
            data.load_doors(doors_file)
            data.load_static(static_file)
            data.load_dynamic(dynamic_file)

            frames_dir = sim_dir / 'frames'
            animate_particles(data, frames_dir, save_frames=args.save_frames)

            logging.info(f"Processing completed for {sim_dir}")

        except Exception as e:
            logging.error(f"Error processing {sim_dir}: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            continue

if __name__ == '__main__':
    main()