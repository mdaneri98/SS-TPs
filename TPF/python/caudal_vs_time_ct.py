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

    def analyze_fixed_p(self, p_value, selected_t_values, dt=3.75):
        """Analiza el caudal para un valor fijo de p y ciertos valores de t"""
        results = {}
        base_dir = self.base_path

        for t in selected_t_values:
            dir_name = f"t_{t}_&_p_{p_value:.2f}/sim_000"
            path = base_dir / dir_name
            particles_data = self.read_particles_file(path)

            if len(particles_data) > 0:
                flow_rate = self.calculate_flow_rate(particles_data, dt)
                if flow_rate:
                    mean_flow_rate = np.mean(flow_rate['flow_rates'])
                    results[t] = {
                        'times': flow_rate['times'],
                        'flow_rates': flow_rate['flow_rates'],
                        'mean_flow_rate': mean_flow_rate
                    }

        return results

    def plot_fixed_p(self, p_value, results, output_dir="plots/caudal"):
        """Genera un gráfico de caudal en función del tiempo para un valor fijo de p"""
        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(12, 8))
        colors = plt.cm.plasma(np.linspace(0, 1, len(results)))

        for (t, data), color in zip(results.items(), colors):
            plt.plot(data['times'], data['flow_rates'],
                     label=f't = {t}',
                     color=color)
            #plt.axhline(y=data['mean_flow_rate'], color=color, linestyle='--', alpha=0.7,
             #           label=f'Mean (t = {t}): {data["mean_flow_rate"]:.2f}')

        plt.title(f'Caudal vs Tiempo (p = {p_value})')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Caudal (partículas/s)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/flow_rates_p{p_value}.png", bbox_inches='tight', dpi=300)
        plt.close()

def main():
    # Crear el analizador
    analyzer = FlowRateAnalyzer()

    # Valor fijo de p y valores seleccionados de t
    p_value = 0.50
    selected_t_values = [15, 25, 35, 45]  # Valores específicos de t para analizar

    # Analizar caudal para p fijo
    print(f"Iniciando análisis para p = {p_value}...")
    results = analyzer.analyze_fixed_p(p_value, selected_t_values)

    # Generar gráfico
    print("Generando gráfico...")
    analyzer.plot_fixed_p(p_value, results)
    print("¡Gráfico generado!")

if __name__ == "__main__":
    main()
