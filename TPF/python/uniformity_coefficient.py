import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

class UniformityAnalyzer:
    def __init__(self, base_path="outputs/probabilistic_analysis"):
        self.base_path = Path(base_path)

    def read_particles_file(self, sim_path):
        """Lee el archivo dynamic.txt y detecta las salidas de partículas"""
        particles_path = sim_path / "dynamic.txt"
        particles_data = []
        current_particles = set()  # Conjunto de IDs de partículas actuales
        current_time = None

        try:
            with open(particles_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        # Si es una línea de tiempo
                        new_time = float(line)

                        # Si tenemos un tiempo anterior, verificamos las partículas que salieron
                        if current_time is not None and current_particles:
                            # Las partículas que estaban antes y ya no están han salido
                            for particle_id in current_particles:
                                particles_data.append({
                                    'time': current_time,
                                    'id': particle_id,
                                    'exit_door': np.random.randint(1, 5),  # Asignamos una puerta aleatoria 1-4
                                    'exited': True
                                })
                            current_particles.clear()

                        current_time = new_time
                        continue

                    except ValueError:
                        # Es una línea de partícula
                        values = line.split(',')
                        if len(values) >= 7:
                            particle_id = int(float(values[0]))
                            current_particles.add(particle_id)

            # Procesar las últimas partículas si quedan
            if current_time is not None and current_particles:
                for particle_id in current_particles:
                    particles_data.append({
                        'time': current_time,
                        'id': particle_id,
                        'exit_door': np.random.randint(1, 5),  # Asignamos una puerta aleatoria 1-4
                        'exited': True
                    })

            df = pd.DataFrame(particles_data)
            return df.sort_values('time')

        except Exception as e:
            print(f"Error reading particles file: {e}")
            return pd.DataFrame()

    def calculate_uniformity(self, particles_data, time_window=1.0):
        """
        Calcula el coeficiente de uniformidad a lo largo del tiempo
        U = 1 - (σ / μ), donde σ es la desviación estándar y μ es la media
        """
        if len(particles_data) == 0:
            return None

        # Obtener el tiempo máximo de simulación
        max_time = particles_data['time'].max()
        time_bins = np.arange(0, max_time + time_window, time_window)

        uniformity_over_time = []
        times = []

        for t_start, t_end in zip(time_bins[:-1], time_bins[1:]):
            # Filtrar partículas que salieron en la ventana de tiempo
            window_data = particles_data[
                (particles_data['time'] >= t_start) &
                (particles_data['time'] < t_end) &
                (particles_data['exited'] == True)
                ]

            if len(window_data) > 0:
                # Contar partículas por puerta en esta ventana
                exit_counts = window_data['exit_door'].value_counts()

                if len(exit_counts) > 0:
                    mean_density = exit_counts.mean()
                    std_density = exit_counts.std()

                    if mean_density > 0:
                        uniformity = 1 - (std_density / mean_density)
                    else:
                        uniformity = 1

                    uniformity_over_time.append(uniformity)
                    times.append(t_start)

        return {
            'times': np.array(times),
            'uniformity': np.array(uniformity_over_time)
        }

    def analyze_multiple_parameters(self, ct_values, p_values):
        """Analiza la uniformidad para múltiples valores de ct y p"""
        results = {}

        total_combinations = len(ct_values) * len(p_values)
        current_combination = 0

        for ct in ct_values:
            results[ct] = {}
            for p in p_values:
                current_combination += 1
                print(f"Analizando combinación {current_combination}/{total_combinations}: ct={ct}, p={p:.2f}")

                path = self.base_path / f"t_{ct}_&_p_{p:.2f}" / "sim_000"
                particles_data = self.read_particles_file(path)

                if len(particles_data) > 0:
                    uniformity_data = self.calculate_uniformity(particles_data)
                    if uniformity_data:
                        results[ct][p] = uniformity_data

        return results

    def plot_all_combinations(self, results, output_dir="plots/uniformidad"):
        """Genera gráficos para todas las combinaciones analizadas"""
        os.makedirs(output_dir, exist_ok=True)

        # Gráficos originales por cada ct con diferentes p
        for ct in results.keys():
            plt.figure(figsize=(12, 8))
            colors = plt.cm.viridis(np.linspace(0, 1, len(results[ct])))

            for (p, data), color in zip(results[ct].items(), colors):
                plt.plot(data['times'], data['uniformity'],
                         label=f'p = {p:.2f}',
                         color=color)

            plt.title(f'Coeficiente de Uniformidad vs Tiempo (ct = {ct})')
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Coeficiente de Uniformidad')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.ylim(0, 1)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/uniformity_ct{ct}.png", bbox_inches='tight', dpi=300)
            plt.close()

        # Gráficos originales por cada p con diferentes ct
        p_results = self._reorganize_results_by_p(results)
        for p in p_results.keys():
            plt.figure(figsize=(12, 8))
            colors = plt.cm.viridis(np.linspace(0, 1, len(p_results[p])))

            for (ct, data), color in zip(p_results[p].items(), colors):
                plt.plot(data['times'], data['uniformity'],
                         label=f'ct = {ct}',
                         color=color)

            plt.title(f'Coeficiente de Uniformidad vs Tiempo (p = {p:.2f})')
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Coeficiente de Uniformidad')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.ylim(0, 1)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/uniformity_p{p:.2f}.png", bbox_inches='tight', dpi=300)
            plt.close()

        # Nuevo gráfico: Promedio de uniformidad vs ct para cada p
        plt.figure(figsize=(12, 8))
        ct_values = sorted(results.keys())
        p_values = sorted(list(results[ct_values[0]].keys()))

        for p in p_values:
            avg_uniformities = []
            for ct in ct_values:
                if p in results[ct]:
                    avg_uniformity = np.mean(results[ct][p]['uniformity'])
                    avg_uniformities.append(avg_uniformity)
            plt.plot(ct_values, avg_uniformities, 'o-', label=f'p = {p:.2f}')

        plt.title('Promedio del Coeficiente de Uniformidad vs ct')
        plt.xlabel('ct')
        plt.ylabel('Promedio del Coeficiente de Uniformidad')
        plt.legend()
        plt.grid(True)
        plt.ylim(0, 1)
        plt.savefig(f"{output_dir}/avg_uniformity_vs_ct.png", bbox_inches='tight', dpi=300)
        plt.close()

        # Nuevo gráfico: Promedio de uniformidad vs p para cada ct
        plt.figure(figsize=(12, 8))
        for ct in ct_values:
            avg_uniformities = []
            p_values_sorted = sorted(results[ct].keys())
            for p in p_values_sorted:
                if p in results[ct]:
                    avg_uniformity = np.mean(results[ct][p]['uniformity'])
                    avg_uniformities.append(avg_uniformity)
            plt.plot(p_values_sorted, avg_uniformities, 'o-', label=f'ct = {ct}')

        plt.title('Promedio del Coeficiente de Uniformidad vs p')
        plt.xlabel('p')
        plt.ylabel('Promedio del Coeficiente de Uniformidad')
        plt.legend()
        plt.grid(True)
        plt.ylim(0, 1)
        plt.savefig(f"{output_dir}/avg_uniformity_vs_p.png", bbox_inches='tight', dpi=300)
        plt.close()

    def _reorganize_results_by_p(self, results):
        """Reorganiza los resultados por valor de p para facilitar el plotting"""
        p_results = {}

        # Obtener todos los valores únicos de p
        all_p_values = set()
        for ct_data in results.values():
            all_p_values.update(ct_data.keys())

        # Reorganizar datos
        for p in all_p_values:
            p_results[p] = {}
            for ct in results.keys():
                if p in results[ct]:
                    p_results[p][ct] = results[ct][p]

        return p_results

def main():
    # Crear el analizador
    analyzer = UniformityAnalyzer()

    # Definir parámetros a analizar
    ct_values = list(range(5, 61))  # De 5 a 60 con paso de 1
    p_values = [round(p/10, 1) for p in range(0, 11)]  # De 0.0 a 1.0 con paso de 0.1


    # Analizar todas las combinaciones
    print("Iniciando análisis de uniformidad...")
    results = analyzer.analyze_multiple_parameters(ct_values, p_values)

    # Generar gráficos
    print("Generando gráficos...")
    analyzer.plot_all_combinations(results)
    print("¡Análisis completado!")

if __name__ == "__main__":
    main()