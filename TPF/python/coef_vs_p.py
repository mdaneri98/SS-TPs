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

    def analyze_uniformity(self, t_value, p_values):
        """Analiza el coeficiente de uniformidad usando densidad media como criterio."""
        results = []

        for p_value in p_values:
            path = self.base_path / f"t_{t_value}_&_p_{p_value:.2f}"
            sim_dirs = sorted(path.glob("sim_*"))

            densities_over_time = []
            for sim_dir in sim_dirs:
                particles_data = self.read_particles_file(sim_dir)
                doors_data = self.read_doors_file(sim_dir)

                for time, particles_df in particles_data.items():
                    if not particles_df.empty and not doors_data.empty:
                        densities = self.compute_densities(particles_df, doors_data)
                        densities_over_time.append(densities)

            # Calcular la densidad media para cada puerta
            densities_over_time = np.array(densities_over_time)
            mean_densities = np.mean(densities_over_time, axis=0)

            # Calcular el coeficiente de uniformidad
            uniformity = self.compute_uniformity(mean_densities)
            results.append((p_value, uniformity))

        return results

    def plot_uniformity_vs_p(self, uniformity_results, t_value, output_dir="plots/uniformity"):
        """Genera un gráfico de uniformidad vs p para un valor fijo de t."""
        os.makedirs(output_dir, exist_ok=True)

        # Extraer los valores de p y sus correspondientes coeficientes de uniformidad
        p_values, uniformities = zip(*uniformity_results)

        plt.figure(figsize=(10, 6))
        plt.plot(p_values, uniformities, marker='o', linestyle='-', color='b')

        plt.title(f'Coeficiente de Uniformidad vs p (t = {t_value})')
        plt.xlabel('Probabilidad (p)')
        plt.ylabel('Coeficiente de Uniformidad (U)')
        plt.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/uniformity_vs_p_t{t_value}.png", bbox_inches='tight', dpi=300)
        plt.close()

def main():
    analyzer = UniformityAnalyzer()

    t_value = 35  # Valor fijo de t
    p_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.00]  # Valores de p

    print("Analizando coeficientes de uniformidad...")
    results = analyzer.analyze_uniformity(t_value, p_values)

    print("Generando gráficos...")
    analyzer.plot_uniformity_vs_p(results, t_value)

    print("¡Análisis completado!")

if __name__ == "__main__":
    main()
