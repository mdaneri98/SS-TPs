import os

import numpy as np
from matplotlib import pyplot as plt
import os
import numpy as np
import matplotlib.pyplot as plt

class DensityAnalyzer:
    def __init__(self):
        """Inicializa el analizador de densidad."""
        self.results = {}

    def analyze_densities(self, t_values, p_values):
        """
        Simula la densidad total para diferentes valores de t y p.

        Args:
            t_values (list): Lista de valores de tiempo de redecisión.
            p_values (list): Lista de valores de probabilidad.

        Returns:
            dict: Resultados organizados en un diccionario con claves como (t, p).
        """
        for t in t_values:
            for p in p_values:
                total_density = self.simulate_density(t, p)
                self.results[(t, p)] = {'total_density': total_density}
        return self.results

    def simulate_density(self, t, p):
        """
        Simula valores ficticios de densidad para un tiempo de redecisión y probabilidad específicos.

        Args:
            t (float): Tiempo de redecisión.
            p (float): Probabilidad de redecisión.

        Returns:
            np.array: Densidades simuladas.
        """
        np.random.seed(int(t * 100 + p * 100))  # Semilla para reproducibilidad
        return np.random.rand(10) * p * t  # Valores ficticios para densidad

    def plot_average_density_vs_t(self, results, p_value, output_dir="plots/average_density"):
        """
        Genera un gráfico de densidad media vs t para un valor fijo de p.

        Args:
            results (dict): Resultados del análisis.
            p_value (float): Valor de probabilidad para el gráfico.
            output_dir (str): Directorio de salida para guardar los gráficos.
        """
        os.makedirs(output_dir, exist_ok=True)

        densities = []
        t_values = []

        for (t, p), data in results.items():
            if p == p_value:
                avg_density = np.mean(data['total_density'])
                densities.append(avg_density)
                t_values.append(t)

        # Generar el gráfico
        plt.figure(figsize=(10, 6))
        plt.plot(t_values, densities, marker='o', color='red', linewidth=2)
        plt.title(f'Densidad Media vs t (p = {p_value})')
        plt.xlabel('t (Tiempo de Redecisión)')
        plt.ylabel('Densidad Media (partículas/m²)')
        plt.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/average_density_p{p_value:.2f}.png", bbox_inches='tight', dpi=300)
        plt.close()


def plot_average_density_vs_t(self, results, p_value, output_dir="plots/average_density"):
    """Genera un gráfico de densidad media vs t para un valor fijo de p"""
    os.makedirs(output_dir, exist_ok=True)

    # Filtrar resultados para el valor específico de p
    densities = []
    t_values = []

    for (t_value, current_p), data in results.items():
        if current_p == p_value:
            avg_density = np.mean(data['total_density'])
            densities.append(avg_density)
            t_values.append(t_value)

    # Generar el gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(t_values, densities, marker='o', color='red', linewidth=2)
    plt.title(f'Densidad Media vs t (p = {p_value})')
    plt.xlabel('t (Tiempo de Redecisión)')
    plt.ylabel('Densidad Media (partículas/m²)')
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/average_density_p{p_value:.2f}.png", bbox_inches='tight', dpi=300)
    plt.close()

def main():
    # Crear el analizador
    analyzer = DensityAnalyzer()

    # Definir parámetros a analizar
    t_values = [5, 15, 25, 35, 45, 55]  # Valores de tiempo de redecisión
    p_values = [0.0]  # Valores de probabilidad

    # Analizar densidades
    print("Analizando densidades...")
    results = analyzer.analyze_densities(t_values, p_values)

    # Generar gráficos de densidad media vs t para cada p
    for p_value in p_values:
        print(f"Generando gráfico para p = {p_value}...")
        analyzer.plot_average_density_vs_t(results, p_value)

    print("¡Análisis completado!")

if __name__ == "__main__":
    main()
