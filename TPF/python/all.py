import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class SimulationAnalyzer:
    def __init__(self, base_path="outputs/probabilistic_analysis"):
        self.base_path = Path(base_path)
        self.initialize_parameters()

    def initialize_parameters(self):
        """Inicializa los parámetros basados en static.txt"""
        self.room_width = 30
        self.room_height = 30
        self.door_width = 1.5

    def read_static_file(self, sim_path):
        """Lee el archivo static.txt con los parámetros de la simulación"""
        static_path = sim_path / "static.txt"
        static_data = {}

        try:
            with open(static_path, 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':')
                        static_data[key.strip()] = float(value.strip())
            return static_data
        except Exception as e:
            print(f"Error reading static file: {e}")
            return {}

    def read_particles_file(self, sim_path):
        """Lee el archivo dynamic.txt con la información de las partículas"""
        particles_path = sim_path / "dynamic.txt"
        particles_data = []
        current_time = None

        try:
            with open(particles_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue

                    # Try to parse as timestamp first
                    try:
                        current_time = float(line)
                        continue
                    except ValueError:
                        # If it's not a timestamp, it must be particle data
                        if current_time is not None:
                            try:
                                # Parse particle data
                                values = line.split(',')
                                if len(values) == 7:  # Ensure we have all expected values
                                    particles_data.append({
                                        'time': current_time,
                                        'id': int(float(values[0])),
                                        'x': float(values[1]),
                                        'y': float(values[2]),
                                        'vel_x': float(values[3]),
                                        'vel_y': float(values[4]),
                                        'radius': float(values[5]),
                                        'exit_door': int(float(values[6]))
                                    })
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing line: {line}")
                                continue

            # Convert to DataFrame
            df = pd.DataFrame(particles_data)

            if len(df) > 0:
                # Calculate exit times for each particle
                max_time = df['time'].max()
                particle_times = df.groupby('id')['time'].max()
                exit_times = particle_times[particle_times < max_time]

                # Add exit_time column
                df['exit_time'] = df['id'].map(exit_times)

            return df

        except Exception as e:
            print(f"Error reading particles file: {e}")
            return pd.DataFrame()

    def read_doors_file(self, sim_path):
        """Lee el archivo doors.csv con la información de las puertas"""
        doors_path = sim_path / "doors.csv"
        try:
            # Read CSV without headers first
            df = pd.read_csv(doors_path, header=None)

            # Check if we have the expected number of columns
            if df.shape[1] == 4:
                # Assign proper column names
                df.columns = ['initial_x', 'initial_y', 'end_x', 'end_y']

                # Ensure all columns are numeric
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                # Add door number as index for identification
                df['door_number'] = range(len(df))

                # Drop any rows with NaN values
                df = df.dropna()

                return df
            else:
                print(f"Unexpected number of columns in doors file: {df.shape[1]}")
                return pd.DataFrame()

        except Exception as e:
            print(f"Error reading doors file: {e}")
            return pd.DataFrame()

    def load_simulation_data(self, t_value, p_value):
        """Carga los datos de todas las simulaciones para un par de valores (t,p)"""
        path = self.base_path / f"t_{t_value}_&_p_{p_value:.2f}"
        all_data = []

        for sim_dir in path.glob("sim_*"):
            try:
                # Cargar datos estáticos de la simulación
                static_data = self.read_static_file(sim_dir)
                if not static_data:
                    continue

                # Cargar datos de las partículas
                particles_data = self.read_particles_file(sim_dir)
                if len(particles_data) == 0:
                    continue

                # Cargar datos de las puertas
                doors_data = self.read_doors_file(sim_dir)
                if len(doors_data) == 0:
                    continue

                # Agregar información de la simulación
                sim_data = {
                    'static': static_data,
                    'particles': particles_data,
                    'doors': doors_data,
                    'simulation': sim_dir.name,
                    't_value': t_value,
                    'p_value': p_value
                }

                all_data.append(sim_data)

            except Exception as e:
                print(f"Error loading data from {sim_dir}: {e}")
                continue

        return all_data if all_data else None

    def calculate_evacuation_time(self, data):
        """Calcula el tiempo de evacuación para cada simulación"""
        particles_data = data['particles']
        if 'exit_time' in particles_data.columns:
            evacuation_times = particles_data.groupby('id')['exit_time'].max()
            return {
                'mean_evacuation_time': evacuation_times.mean(),
                'max_evacuation_time': evacuation_times.max(),
                'evacuation_percentage': (len(evacuation_times) / len(particles_data['id'].unique())) * 100
            }
        return None

    def calculate_flow_rate(self, data, dt=1.0):
        """
        Calcula ambos tipos de caudal:
        1. Q_global = N_total / T_total
        2. Q(t) = (N(t) - N(t + Δt)) / Δt
        """
        particles_data = data['particles']
        doors_data = data['doors']

        if len(particles_data) == 0 or len(doors_data) == 0:
            return None

        # Caudal global
        total_time = particles_data['exit_time'].max()
        total_particles = len(particles_data['id'].unique())
        q_global = total_particles / total_time if total_time > 0 else 0

        # Caudal por puerta
        q_by_door = {}
        for door_num in doors_data['door_number'].unique():
            door_particles = particles_data[particles_data['exit_door'] == door_num]
            if len(door_particles) > 0:
                door_time = door_particles['exit_time'].max()
                q_by_door[f'door_{door_num}'] = len(door_particles) / door_time if door_time > 0 else 0
            else:
                q_by_door[f'door_{door_num}'] = 0

        # Caudal instantáneo
        time_range = np.arange(0, total_time + dt, dt)
        particles_out = []
        for t in time_range[:-1]:
            n_t = len(particles_data[particles_data['exit_time'] <= t])
            n_t_dt = len(particles_data[particles_data['exit_time'] <= t + dt])
            particles_out.append((n_t_dt - n_t) / dt)

        return {
            'q_global': q_global,
            'q_by_door': q_by_door,
            'q_instantaneous': np.array(particles_out),
            'time_points': time_range[:-1]
        }

    def calculate_density(self, data, r_k=5):
        """
        Calcula la densidad media según la fórmula:
        ρ(t) = (1/N) * Σ (n_i(t) / A_c)
        """
        particles_data = data['particles']
        doors_data = data['doors']

        if len(particles_data) == 0 or len(doors_data) == 0:
            return None

        # Calcular centroide de las puertas
        centroid_x = doors_data['initial_x'].mean()
        centroid_y = doors_data['initial_y'].mean()

        # Agregar el centroide a los puntos de medición
        measure_points = pd.concat([
            doors_data[['initial_x', 'initial_y']],
            pd.DataFrame({'initial_x': [centroid_x], 'initial_y': [centroid_y]})
        ])

        densities = []
        times = particles_data['time'].unique()

        for t in times:
            particles_t = particles_data[particles_data['time'] == t]
            density_t = []

            for _, point in measure_points.iterrows():
                # Calcular distancias a este punto
                distances = np.sqrt(
                    (particles_t['x'] - point['initial_x'])**2 +
                    (particles_t['y'] - point['initial_y'])**2
                )

                # Obtener el radio r_k (distancia a la k-ésima partícula más cercana)
                if len(distances) >= r_k:
                    r = np.sort(distances)[r_k-1]
                    # Contar partículas dentro del radio
                    n = len(distances[distances <= r])
                    # Calcular densidad en este punto
                    area = np.pi * r**2 / 2  # Área de semicircunferencia
                    density_t.append(n / area)
                else:
                    density_t.append(0)

            densities.append(np.mean(density_t))

        return {
            'times': times,
            'densities': np.array(densities)
        }

    def calculate_uniformity(self, data):
        """
        Calcula el coeficiente de uniformidad:
        U = 1 - (σ / μ)
        """
        doors_data = data['doors']
        particles_data = data['particles']

        if len(particles_data) == 0 or len(doors_data) == 0:
            return None

        uniformity_over_time = []
        times = particles_data['time'].unique()

        for t in times:
            particles_t = particles_data[particles_data['time'] == t]
            door_densities = []

            for _, door in doors_data.iterrows():
                # Calcular densidad en cada puerta
                distances = np.sqrt(
                    (particles_t['x'] - door['initial_x'])**2 +
                    (particles_t['y'] - door['initial_y'])**2
                )

                if len(distances) >= 5:  # k=5 como en la definición
                    r = np.sort(distances)[4]  # 5ta partícula más cercana
                    n = len(distances[distances <= r])
                    density = n / (np.pi * r**2 / 2)
                    door_densities.append(density)
                else:
                    door_densities.append(0)

            # Calcular coeficiente de uniformidad
            if door_densities:
                mean_density = np.mean(door_densities)
                if mean_density > 0:
                    std_density = np.std(door_densities)
                    uniformity = 1 - (std_density / mean_density)
                    uniformity_over_time.append(uniformity)
                else:
                    uniformity_over_time.append(1)  # Cuando no hay partículas, consideramos uniformidad perfecta
            else:
                uniformity_over_time.append(1)

        return {
            'times': times,
            'uniformity': np.array(uniformity_over_time)
        }

    def analyze_simulation(self, t_value, p_value):
        """Realiza el análisis completo para un par de valores (t,p)"""
        simulations_data = self.load_simulation_data(t_value, p_value)
        if not simulations_data:
            return None

        results = {
            't_value': t_value,
            'p_value': p_value,
            'evacuation_times': [],
            'flow_rates': [],
            'densities': [],
            'uniformity': []
        }

        for sim_data in simulations_data:
            # Calcular todos los observables
            evac_time = self.calculate_evacuation_time(sim_data)
            flow_rate = self.calculate_flow_rate(sim_data)
            density = self.calculate_density(sim_data)
            unif = self.calculate_uniformity(sim_data)

            # Almacenar resultados
            if evac_time:
                results['evacuation_times'].append(evac_time)
            if flow_rate:
                results['flow_rates'].append(flow_rate)
            if density:
                results['densities'].append(density)
            if unif:
                results['uniformity'].append(unif)

        return results if any(results.values()) else None

    def plot_results(self, results, output_dir="plots"):
        """Genera gráficos para visualizar los resultados"""
        os.makedirs(output_dir, exist_ok=True)

        if not results or not any(results.values()):
            print("No hay resultados para graficar")
            return

        # Gráfico de tiempos de evacuación
        if results['evacuation_times']:
            plt.figure(figsize=(10, 6))
            mean_times = [r['mean_evacuation_time'] for r in results['evacuation_times']]
            plt.boxplot(mean_times)
            plt.title(f"Tiempos de evacuación (t={results['t_value']}, p={results['p_value']})")
            plt.savefig(f"{output_dir}/evacuation_times_t{results['t_value']}_p{results['p_value']}.png")
            plt.close()

        # Gráfico de caudales
        if results['flow_rates']:
            plt.figure(figsize=(10, 6))
            for flow_data in results['flow_rates']:
                plt.plot(flow_data['time_points'], flow_data['q_instantaneous'], alpha=0.3)
            plt.title(f"Caudal instantáneo (t={results['t_value']}, p={results['p_value']})")
            plt.xlabel("Tiempo (s)")
            plt.ylabel("Caudal (partículas/s)")
            plt.savefig(f"{output_dir}/flow_rates_t{results['t_value']}_p{results['p_value']}.png")
            plt.close()

        # Gráfico de densidades medias
        if results['densities']:
            plt.figure(figsize=(10, 6))
            for density_data in results['densities']:
                plt.plot(density_data['times'], density_data['densities'], alpha=0.3)
            plt.title(f"Densidad media (t={results['t_value']}, p={results['p_value']})")
            plt.xlabel("Tiempo (s)")
            plt.ylabel("Densidad (partículas)")

            plt.ylabel("Densidad (partículas/m²)")
            plt.savefig(f"{output_dir}/densities_t{results['t_value']}_p{results['p_value']}.png")
            plt.close()

        # Gráfico de uniformidad
        if results['uniformity']:
            plt.figure(figsize=(10, 6))
            for unif_data in results['uniformity']:
                plt.plot(unif_data['times'], unif_data['uniformity'], alpha=0.3)
            plt.title(f"Coeficiente de uniformidad (t={results['t_value']}, p={results['p_value']})")
            plt.xlabel("Tiempo (s)")
            plt.ylabel("Uniformidad")
            plt.savefig(f"{output_dir}/uniformity_t{results['t_value']}_p{results['p_value']}.png")
            plt.close()

    def create_heatmap_data(self, t_values, p_values):
        """
        Crea matrices de datos para los heatmaps de cada observable
        """
        # Inicializar matrices para cada observable
        evac_times_matrix = np.zeros((len(t_values), len(p_values)))
        flow_rates_matrix = np.zeros((len(t_values), len(p_values)))
        density_matrix = np.zeros((len(t_values), len(p_values)))
        uniformity_matrix = np.zeros((len(t_values), len(p_values)))

        for i, t in enumerate(t_values):
            for j, p in enumerate(p_values):
                results = self.analyze_simulation(t, p)

                if results:
                    # Tiempo de evacuación promedio
                    if results['evacuation_times']:
                        evac_times = [r['mean_evacuation_time'] for r in results['evacuation_times']]
                        evac_times_matrix[i, j] = np.mean(evac_times)

                    # Caudal global promedio
                    if results['flow_rates']:
                        flow_rates = [r['q_global'] for r in results['flow_rates']]
                        flow_rates_matrix[i, j] = np.mean(flow_rates)

                    # Densidad media promedio
                    if results['densities']:
                        densities = [np.mean(r['densities']) for r in results['densities']]
                        density_matrix[i, j] = np.mean(densities)

                    # Uniformidad promedio
                    if results['uniformity']:
                        uniformities = [np.mean(r['uniformity']) for r in results['uniformity']]
                        uniformity_matrix[i, j] = np.mean(uniformities)

        return {
            'evacuation_times': evac_times_matrix,
            'flow_rates': flow_rates_matrix,
            'densities': density_matrix,
            'uniformity': uniformity_matrix
        }

    def plot_heatmaps(self, t_values, p_values, data_matrices, output_dir="plots"):
        """
        Genera heatmaps para cada observable
        """
        os.makedirs(output_dir, exist_ok=True)

        # Configurar el estilo de las gráficas
        plt.style.use('default')

        # Definir títulos y etiquetas para cada observable
        observables = {
            'evacuation_times': {
                'title': 'Tiempo medio de evacuación',
                'cmap': 'viridis_r',  # Invertido porque menor tiempo es mejor
                'fmt': '.1f',
                'units': 's'
            },
            'flow_rates': {
                'title': 'Caudal global promedio',
                'cmap': 'viridis',
                'fmt': '.2f',
                'units': 'part/s'
            },
            'densities': {
                'title': 'Densidad media',
                'cmap': 'viridis',
                'fmt': '.2f',
                'units': 'part/m²'
            },
            'uniformity': {
                'title': 'Coeficiente de uniformidad promedio',
                'cmap': 'viridis',
                'fmt': '.2f',
                'units': ''
            }
        }

        for observable, matrix in data_matrices.items():
            plt.figure(figsize=(12, 8))

            # Crear el heatmap
            sns.heatmap(matrix[::-1],  # Esto invierte el orden de las filas
                        xticklabels=[f'{p:.1f}' for p in p_values],
                        yticklabels=t_values[::-1],  # Esto invierte el orden de las etiquetas del eje y
                        cmap=observables[observable]['cmap'],
                        annot=True,
                        fmt=observables[observable]['fmt'],
                        annot_kws={'rotation': 0},  # Esto hace que los números dentro del heatmap sean legibles
                        cbar_kws={'label': observables[observable]['units']} if observables[observable]['units'] else {})

            plt.title(observables[observable]['title'])
            plt.xlabel('Probabilidad de redecisión (p)')
            plt.ylabel('Tiempo de redecisión (ct)')

            # Ajustar layout y guardar
            plt.tight_layout()
            plt.savefig(f"{output_dir}/heatmap_{observable}.png", dpi=300, bbox_inches='tight')
            plt.close()

def main():
    # Crear el analizador
    analyzer = SimulationAnalyzer()

    # Definir rangos de parámetros
    t_values = list(range(5, 251, 5))  # [20, 30, ..., 100]
    p_values = list(np.arange(0, 1.1, 0.1))  # [0.0, 0.1, ..., 1.0]

    # Crear directorio para los plots si no existe
    os.makedirs("plots", exist_ok=True)

    # Obtener datos para los heatmaps
    print("Recopilando datos para los heatmaps...")
    heatmap_data = analyzer.create_heatmap_data(t_values, p_values)

    # Generar heatmaps
    print("Generando heatmaps...")
    analyzer.plot_heatmaps(t_values, p_values, heatmap_data)
    print("¡Análisis completado!")

if __name__ == "__main__":
    main()