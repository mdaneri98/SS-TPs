import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.signal import savgol_filter
import os

def plot_smoothed_pressure(directory):
    pressure_path = os.path.join(directory, "pressure.csv")
    if not os.path.exists(pressure_path):
        print(f"Error: Archivo no encontrado en {pressure_path}")
        return
        
    # Leer datos
    pressure_df = pd.read_csv(pressure_path)
    
    # Configurar estilo
    plt.figure(figsize=(12, 6))
    colors = sns.color_palette("husl", 5)
    
    # Suavizar y graficar cada curva
    window = 51  # Debe ser impar
    poly_order = 3
    
    for idx, col in enumerate(['bottom', 'right', 'top', 'left', 'static']):
        # Aplicar filtro Savitzky-Golay para suavizar la curva
        if len(pressure_df[col]) > window:
            smoothed = savgol_filter(pressure_df[col], window, poly_order)
        else:
            smoothed = pressure_df[col]
            
        plt.plot(pressure_df['time'], smoothed, label=col, color=colors[idx], linewidth=2)
    
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Presión')
    plt.title('Evolución de la Presión en el Sistema')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Guardar y mostrar
    os.makedirs(directory, exist_ok=True)
    plt.savefig(os.path.join(directory, "pressure_curve.png"), dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    plot_smoothed_pressure("outputs/fixed_solution")