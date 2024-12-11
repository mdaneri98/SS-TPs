import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

class FlowRateAnalyzer:
    def __init__(self, base_path="outputs/probabilistic_analysis"):
        self.base_path = Path(base_path)

    def read_particles_file(self, sim_path):
        """Lee el archivo dynamic.txt con la información de las partículas"""
        particles_path = sim_path / "dynamic.txt"
        particles_data = []
        current_time = None

        try:
            with open(particles_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        current_time = float(line)
                        continue
                    except ValueError:
                        if current_time is not None:
                            values = line.split(',')
                            if len(values) == 7:
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

            df = pd.DataFrame(particles_data)
            return df.sort_values('time')

        except Exception as e:
            print(f"Error reading particles file: {e}")
            return pd.DataFrame()

    def calculate_flow_rate(self, particles_data, dt=1.0):
        """Calcula el caudal instantáneo como la cantidad de partículas que salen en cada intervalo dt"""
        if len(particles_data) == 0:
            return None

        last_appearances = particles_data.groupby('id')['time'].max()
        max_time = particles_data['time'].max()
        time_bins = np.arange(0, max_time + dt, dt)
        particle_exits = pd.cut(last_appearances, bins=time_bins).value_counts().sort_index()
        flow_rates = particle_exits.values / dt
        times = time_bins[:-1]

        return {
            'times': times,
            'flow_rates': flow_rates
        }

    def analyze_multiple_parameters(self, ct_values, p_values):
        """Analiza el caudal para múltiples valores de ct y p"""
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
                    flow_rate = self.calculate_flow_rate(particles_data)
                    if flow_rate:
                        results[ct][p] = {
                            'times': flow_rate['times'],
                            'flow_rates': flow_rate['flow_rates'],
                        }

        return results

    def plot_all_combinations(self, results, output_dir="plots/caudal"):
        """Genera gráficos para todas las combinaciones analizadas"""
        os.makedirs(output_dir, exist_ok=True)

        # Plot por cada ct con diferentes p
        for ct in results.keys():
            plt.figure(figsize=(12, 8))
            colors = plt.cm.viridis(np.linspace(0, 1, len(results[ct])))

            for (p, data), color in zip(results[ct].items(), colors):
                plt.plot(data['times'], data['flow_rates'],
                         label=f'p = {p:.2f}',
                         color=color)

            plt.title(f'Caudal vs Tiempo (ct = {ct})')
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Caudal (partículas/s)')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/flow_rates_ct{ct}.png", bbox_inches='tight', dpi=300)
            plt.close()

        # Plot por cada p con diferentes ct
        p_results = self._reorganize_results_by_p(results)
        for p in p_results.keys():
            plt.figure(figsize=(12, 8))
            colors = plt.cm.viridis(np.linspace(0, 1, len(p_results[p])))

            for (ct, data), color in zip(p_results[p].items(), colors):
                plt.plot(data['times'], data['flow_rates'],
                         label=f'ct = {ct}',
                         color=color)

            #plt.title(f'Caudal vs Tiempo (p = {p:.2f})')
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Caudal (partículas/s)')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/flow_rates_p{p:.2f}.png", bbox_inches='tight', dpi=300)
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
    analyzer = FlowRateAnalyzer()

    # Definir parámetros a analizar
    ct_values = [5, 10, 15, 20, 25, 30]  # Valores de tiempo de redecisión
    p_values = [0.5]  # Valores de probabilidad

    # Analizar todas las combinaciones
    print("Iniciando análisis de caudales...")
    results = analyzer.analyze_multiple_parameters(ct_values, p_values)

    # Generar gráficos
    print("Generando gráficos...")
    analyzer.plot_all_combinations(results)
    print("¡Análisis completado!")

if __name__ == "__main__":
    main()