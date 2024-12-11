import os
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


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

    def calculate_flow_rate(self, particles_data, dt=3.75):
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

    def analyze_fixed_t(self, t_value, selected_p_values, dt=3.75):
        """Analiza el caudal para un valor fijo de t y ciertos valores de p"""
        results = {}
        base_dir = self.base_path

        for p in selected_p_values:
            dir_name = f"t_{t_value}_&_p_{p:.2f}/sim_000"
            path = base_dir / dir_name
            particles_data = self.read_particles_file(path)

            if len(particles_data) > 0:
                flow_rate = self.calculate_flow_rate(particles_data, dt)
                if flow_rate:
                    results[p] = {
                        'times': flow_rate['times'],
                        'flow_rates': flow_rate['flow_rates'],
                    }

        return results

    def plot_fixed_t(self, t_value, results, output_dir="plots/caudal"):
        """Genera un gráfico de caudal en función del tiempo para un valor fijo de t"""
        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(12, 8))
        colors = plt.cm.viridis(np.linspace(0, 1, len(results)))

        for (p, data), color in zip(results.items(), colors):
            plt.plot(data['times'], data['flow_rates'],
                     label=f'p = {p:.2f}',
                     color=color)

        plt.title(f'Caudal vs Tiempo (t = {t_value})')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Caudal (partículas/s)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/caudal_vs_time_t{t_value}.png", bbox_inches='tight', dpi=300)
        plt.close()

def main():
    # Crear el analizador
    analyzer = FlowRateAnalyzer()

    # Valor fijo de t y valores seleccionados de p
    t_value = 25
    selected_p_values = [0.0, 0.50, 0.70, 1.00]  # Valores específicos de p para analizar

    # Analizar caudal para t fijo
    print(f"Iniciando análisis para t = {t_value}...")
    results = analyzer.analyze_fixed_t(t_value, selected_p_values)

    # Generar gráfico
    print("Generando gráfico...")
    analyzer.plot_fixed_t(t_value, results)
    print("¡Gráfico generado!")

if __name__ == "__main__":
    main()
