import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_system_data(directory):
    try:
        # Verificar si existen los archivos
        pressure_path = os.path.join(directory, "pressure.csv")
        count_path = os.path.join(directory, "count.csv")
        
        if not os.path.exists(pressure_path) or not os.path.exists(count_path):
            print(f"Error: Archivos no encontrados en {directory}")
            print(f"Pressure file exists: {os.path.exists(pressure_path)}")
            print(f"Count file exists: {os.path.exists(count_path)}")
            return
        
        # Leer datos
        pressure_df = pd.read_csv(pressure_path)
        count_df = pd.read_csv(count_path)
        
        # Configurar estilo
        plt.style.use('default')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Gráfico de presiones
        for col in ['bottom', 'right', 'top', 'left', 'static']:
            ax1.plot(pressure_df['time'], pressure_df[col], label=col, linewidth=2)
        
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Presión')
        ax1.set_title('Evolución de la Presión')
        ax1.legend()
        ax1.grid(True)
        
        # Gráfico de colisiones
        for col in ['bottom', 'right', 'top', 'left', 'static']:
            ax2.plot(count_df['time'], count_df[col], label=col, linewidth=2)
        
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Número de Colisiones')
        ax2.set_title('Evolución de las Colisiones')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        # Crear directorio si no existe
        os.makedirs(directory, exist_ok=True)
        plt.savefig(os.path.join(directory, "analysis.png"), dpi=300, bbox_inches='tight')
        
    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")
        print(f"Directorio actual: {os.getcwd()}")

if __name__ == "__main__":
    # Intentar diferentes rutas comunes
    paths = [
        "outputs/fixed_solution",
    ]
    
    for path in paths:
        print(f"Intentando con ruta: {path}")
        plot_system_data(path)