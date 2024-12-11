import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

class UniformityAnalyzer:
    def __init__(self, base_path="outputs/probabilistic_analysis"):
        self.base_path = Path(base_path)

    def read_particles_file(self, sim_path):
        """Lee el archivo `dynamic.txt` y devuelve un diccionario con datos de partículas por tiempo."""
        particles_path = sim_path / "dynamic.txt"
        particles_data = {}
        current_time = None

        try:
            with open(particles_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        current_time = float(line)
                        particles_data[current_time] = []
                        continue
                    except ValueError:
                        values = line.split(',')
                        if len(values) == 7:
                            particles_data[current_time].append({
                                'x': float(values[1]),
                                'y': float(values[2])
                            })
            return {t: pd.DataFrame(particles) for t, particles in particles_data.items()}
        except Exception as e:
            print(f"Error reading particles file: {e}")
            return {}

    def read_doors_file(self, sim_path):
        """Lee el archivo `doors.csv` con la información de las puertas."""
        doors_path = sim_path / "doors.csv"
        try:
            df = pd.read_csv(doors_path, skipinitialspace=True)
            df['door_number'] = range(len(df))
            return df
        except Exception as e:
            print(f"Error reading doors file: {e}")
            return pd.DataFrame()

    def compute_densities(self, particles_data, doors_data, r_k=5):
        """Calcula las densidades para cada puerta."""
        if particles_data.empty or doors_data.empty:
            return []

        densities = []
        for _, door in doors_data.iterrows():
            door_center_x = (door['initial_x'] + door['end_x']) / 2
            door_center_y = (door['initial_y'] + door['end_y']) / 2

            distances = np.sqrt(
                (particles_data['x'] - door_center_x) ** 2 +
                (particles_data['y'] - door_center_y) ** 2
            )

            if len(distances) >= r_k:
                r = np.sort(distances.values)[r_k - 1]
                n = len(distances[distances <= r])
                area = np.pi * r ** 2 / 2
                density = n / area
            else:
                density = 0

            densities.append(density)
        return densities

    def compute_uniformity(self, densities):
        """Calcula el coeficiente de uniformidad."""
        densities = np.array(densities)
        if len(densities) == 0:
            return 0  # No hay datos, uniformidad mínima

        mu = np.mean(densities)
        if mu == 0:
            return 0  # Densidades todas cero, uniformidad mínima

        sigma = np.std(densities)
        uniformity = 1 - (sigma / mu)

        # Garantizar que U esté entre [0, 1]
        return max(0, min(uniformity, 1))

    def analyze_uniformity_over_time(self, t_value, p_values):
        """Analiza el coeficiente de uniformidad como función del tiempo para varios valores de p."""
        results = {}

        for p_value in p_values:
            path = self.base_path / f"t_{t_value}_&_p_{p_value:.2f}"
            sim_dirs = sorted(path.glob("sim_*"))

            uniformities_over_time = {}
            for sim_dir in sim_dirs:
                particles_data = self.read_particles_file(sim_dir)
                doors_data = self.read_doors_file(sim_dir)

                for time, particles_df in particles_data.items():
                    if time not in uniformities_over_time:
                        uniformities_over_time[time] = []

                    if not particles_df.empty and not doors_data.empty:
                        densities = self.compute_densities(particles_df, doors_data)
                        uniformity = self.compute_uniformity(densities)
                        uniformities_over_time[time].append(uniformity)

            # Promedia los valores de uniformidad para cada tiempo
            averaged_uniformities = {time: np.mean(values) for time, values in uniformities_over_time.items()}
            results[p_value] = averaged_uniformities

        return results

    def plot_uniformity_vs_time(self, uniformity_results, t_value, output_dir="plots/uniformity"):
        """Genera un gráfico de uniformidad vs tiempo para cada valor de p."""
        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(10, 6))
        for p_value, uniformities in uniformity_results.items():
            times = sorted(uniformities.keys())
            values = [uniformities[time] for time in times]
            plt.plot(times, values, marker='o', label=f'p = {p_value:.2f}')

        plt.title(f'Coeficiente de Uniformidad vs Tiempo (t = {t_value})')
        plt.xlabel('Tiempo (t)')
        plt.ylabel('Coeficiente de Uniformidad (U)')
        plt.legend(title='Probabilidad (p)')
        plt.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/uniformity_vs_time_t{t_value}.png", bbox_inches='tight', dpi=300)
        plt.close()

def main():
    analyzer = UniformityAnalyzer()

    t_value = 5  # Valor fijo de t
    p_values = [0.1, 0.3, 0.5, 0.7, 0.9]  # Valores de p

    print("Analizando coeficientes de uniformidad en función del tiempo...")
    results = analyzer.analyze_uniformity_over_time(t_value, p_values)

    print("Generando gráficos...")
    analyzer.plot_uniformity_vs_time(results, t_value)

    print("¡Análisis completado!")

if __name__ == "__main__":
    main()
