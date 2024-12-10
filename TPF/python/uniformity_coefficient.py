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
        current_particles = set()
        current_time = None

        try:
            with open(particles_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        new_time = float(line)
                        if current_time is not None and current_particles:
                            for particle_id in current_particles:
                                particles_data.append({
                                    'time': current_time,
                                    'id': particle_id,
                                    'exit_door': np.random.randint(1, 5),
                                    'exited': True
                                })
                            current_particles.clear()

                        current_time = new_time
                        continue

                    except ValueError:
                        values = line.split(',')
                        if len(values) >= 7:
                            particle_id = int(float(values[0]))
                            current_particles.add(particle_id)

            if current_time is not None and current_particles:
                for particle_id in current_particles:
                    particles_data.append({
                        'time': current_time,
                        'id': particle_id,
                        'exit_door': np.random.randint(1, 5),
                        'exited': True
                    })

            df = pd.DataFrame(particles_data)
            return df.sort_values('time')

        except Exception as e:
            print(f"Error reading particles file: {e}")
            return pd.DataFrame()

    def calculate_uniformity(self, particles_data, time_window=1.0):
        """Calcula el coeficiente de uniformidad a lo largo del tiempo"""
        if len(particles_data) == 0:
            return None

        max_time = particles_data['time'].max()
        time_bins = np.arange(0, max_time + time_window, time_window)
        uniformity_over_time = []
        times = []

        for t_start, t_end in zip(time_bins[:-1], time_bins[1:]):
            window_data = particles_data[
                (particles_data['time'] >= t_start) &
                (particles_data['time'] < t_end) &
                (particles_data['exited'] == True)
                ]

            if len(window_data) > 0:
                exit_counts = window_data['exit_door'].value_counts()
                if len(exit_counts) > 0:
                    mean_density = exit_counts.mean()
                    std_density = exit_counts.std() if len(exit_counts) > 1 else 0
                    uniformity = 1 - (std_density / mean_density) if mean_density > 0 else 1
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
                    if uniformity_data is not None and len(uniformity_data['uniformity']) > 0:
                        results[ct][p] = uniformity_data

        return results

    def plot_average_curves(self, ct_values, p_values, results, output_dir="plots/uniformidad"):
        """Genera gráficos con las curvas promedio"""
        os.makedirs(output_dir, exist_ok=True)

        # Gráfico 1: Promedio vs ct
        plt.figure(figsize=(12, 8))
        ct_averages = []
        valid_cts = []

        for ct in ct_values:
            if ct in results:
                p_values_for_ct = []
                for p in p_values:
                    if p in results[ct] and len(results[ct][p]['uniformity']) > 0:
                        avg_uniformity = np.mean(results[ct][p]['uniformity'])
                        p_values_for_ct.append(avg_uniformity)

                if p_values_for_ct:
                    ct_averages.append(np.mean(p_values_for_ct))
                    valid_cts.append(ct)

        if valid_cts:
            plt.plot(valid_cts, ct_averages, 'b-', linewidth=2)
            plt.title('Promedio Global del Coeficiente de Uniformidad vs ct')
            plt.xlabel('ct')
            plt.ylabel('Promedio del Coeficiente de Uniformidad')
            plt.grid(True)
            plt.ylim(0, 1)
            plt.savefig(f"{output_dir}/avg_uniformity_vs_ct_global.png", bbox_inches='tight', dpi=300)
        plt.close()

        # Gráfico 2: Promedio vs p
        plt.figure(figsize=(12, 8))
        p_averages = []
        valid_ps = []

        for p in p_values:
            ct_values_for_p = []
            for ct in ct_values:
                if ct in results and p in results[ct] and len(results[ct][p]['uniformity']) > 0:
                    avg_uniformity = np.mean(results[ct][p]['uniformity'])
                    ct_values_for_p.append(avg_uniformity)

            if ct_values_for_p:
                p_averages.append(np.mean(ct_values_for_p))
                valid_ps.append(p)

        if valid_ps:
            plt.plot(valid_ps, p_averages, 'r-', linewidth=2)
            plt.title('Promedio Global del Coeficiente de Uniformidad vs p')
            plt.xlabel('p')
            plt.ylabel('Promedio del Coeficiente de Uniformidad')
            plt.grid(True)
            plt.ylim(0, 1)
            plt.savefig(f"{output_dir}/avg_uniformity_vs_p_global.png", bbox_inches='tight', dpi=300)
        plt.close()

def main():
    analyzer = UniformityAnalyzer()

    # Definir parámetros a analizar con los rangos correctos
    ct_values = list(range(5, 60))  # De 30 a 55
    p_values = [round(p/10, 1) for p in range(0, 11)]  # De 0.0 a 1.0 con paso de 0.1

    print("Iniciando análisis de uniformidad...")
    results = analyzer.analyze_multiple_parameters(ct_values, p_values)

    print("Generando gráficos promedio...")
    analyzer.plot_average_curves(ct_values, p_values, results)
    print("¡Análisis completado!")

if __name__ == "__main__":
    main()