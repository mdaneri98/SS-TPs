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

    def analyze_flow_rates(self, t_values, p_value):
        """Analiza el caudal para varios valores de t y un valor fijo de p"""
        results = {}

        for t_value in t_values:
            path = self.base_path / f"t_{t_value}_&_p_{p_value:.2f}" / "sim_000"
            particles_data = self.read_particles_file(path)
            if len(particles_data) > 0:
                flow_rate = self.calculate_flow_rate(particles_data)
                if flow_rate:
                    results[t_value] = {
                        'times': flow_rate['times'],
                        'flow_rates': flow_rate['flow_rates'],
                    }

        return results

    def plot_flow_rates(self, results, p_value, output_dir="plots"):
        """Genera gráfico de caudal vs tiempo para diferentes valores de t"""
        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(12, 8))

        # Color map para diferentes valores de t
        colors = plt.cm.viridis(np.linspace(0, 1, len(results)))

        for (t_value, data), color in zip(results.items(), colors):
            plt.plot(data['times'], data['flow_rates'],
                     label=f'ct = {t_value}',
                     color=color)

        plt.title(f'Caudal vs Tiempo (p = {p_value:.2f})')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Caudal (partículas/s)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/flow_rates_p{p_value:.2f}.png",
                    bbox_inches='tight',
                    dpi=300)
        plt.close()

def main():
    # Crear el analizador
    analyzer = FlowRateAnalyzer()

    # Definir parámetros
    p_value = 0.5  # Probabilidad fija
    t_values = [5, 10, 15, 20, 25, 30]  # Valores de tiempo de redecisión a analizar

    # Analizar caudales
    print("Analizando caudales...")
    results = analyzer.analyze_flow_rates(t_values, p_value)

    # Generar gráfico
    print("Generando gráfico...")
    analyzer.plot_flow_rates(results, p_value)
    print("¡Análisis completado!")

if __name__ == "__main__":
    main()