import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='va_analysis.log'
)

class VaAnalyzer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path).absolute() / "outputs"
        if not self.base_path.exists():
            raise FileNotFoundError(f"No se encontró el directorio outputs en {base_path}")

    def parse_dynamic_file(self, file_path):
        """
        Parsea el archivo dynamic.txt y calcula va para cada timestep
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            times = []
            va_values = []
            
            i = 0
            while i < len(lines):
                # Leer tiempo
                try:
                    time = float(lines[i].strip())
                    times.append(time)
                except ValueError:
                    i += 1
                    continue
                
                i += 1
                if i >= len(lines):
                    break
                
                # Obtener velocidades de todos los agentes
                velocities = []
                while i < len(lines) and ',' in lines[i]:
                    parts = lines[i].strip().split(',')
                    if len(parts) >= 5:
                        vx = float(parts[3])
                        vy = float(parts[4])
                        if vx != 0 or vy != 0:  # Solo considerar agentes en movimiento
                            velocities.append([vx, vy])
                    i += 1
                
                # Calcular va para este timestep
                if velocities:
                    va = self.calculate_va(velocities)
                    va_values.append(va)
            
            return {
                'times': np.array(times),
                'va_values': np.array(va_values)
            }
            
        except Exception as e:
            logging.error(f"Error al parsear archivo {file_path}: {str(e)}")
            return None

    def calculate_va(self, velocities):
        """
        Calcula el parámetro de orden va (velocidad de alineación)
        VA = |< Σᵢ vᵢ/|vᵢ| >|/N
        donde <...> representa el promedio sobre realizaciones
        """
        N = len(velocities)
        if N == 0:
            return 0
        
        velocities = np.array(velocities)
        # Calcular las magnitudes de cada velocidad
        magnitudes = np.linalg.norm(velocities, axis=1)
        non_zero_mask = magnitudes > 0
        
        if not np.any(non_zero_mask):
            return 0
        
        # Normalizar cada vector por su magnitud
        v_normalized = velocities[non_zero_mask] / magnitudes[non_zero_mask, np.newaxis]
        
        # Sumar los vectores normalizados
        sum_v = np.sum(v_normalized, axis=0)
        
        # Calcular VA
        va = np.linalg.norm(sum_v) / N
        
        return va

    def analyze_va(self, ap_value, bp_value):
        """
        Analiza va para un ap y bp específicos
        """
        dir_name = f"ap_{ap_value:.2f}_bp_{bp_value:.2f}"
        param_dir = self.base_path / "heuristic_analysis" / dir_name
        
        if not param_dir.exists():
            logging.error(f"No se encontró el directorio: {param_dir}")
            return None
            
        try:
            # Lista para almacenar los VA de todas las realizaciones en cada tiempo
            all_va_times = []
            valid_simulations = 0
            
            # Procesar cada simulación
            for sim_dir in param_dir.glob("sim_*"):
                dynamic_file = sim_dir / "dynamic.txt"
                if not dynamic_file.exists():
                    continue
                    
                data = self.parse_dynamic_file(dynamic_file)
                if data is None or len(data['times']) <= 1:
                    continue
                
                # Normalizar tiempo a [0,1]
                max_time = data['times'][-1]
                if max_time <= 0:
                    continue
                    
                normalized_times = data['times'] / max_time
                all_va_times.append({
                    'times': normalized_times,
                    'va_values': data['va_values']
                })
                valid_simulations += 1
            
            if not all_va_times:
                return None
            
            # Puntos de tiempo uniformes para interpolación
            time_points = np.linspace(0, 1, 100)
            
            # Para cada punto de tiempo, calcular VA promediando sobre todas las realizaciones
            avg_va = np.zeros(len(time_points))
            std_va = np.zeros(len(time_points))
            
            for t_idx, t in enumerate(time_points):
                va_at_t = []
                for sim in all_va_times:
                    try:
                        # Interpolar VA para este tiempo
                        va = np.interp(t, sim['times'], sim['va_values'])
                        va_at_t.append(va)
                    except:
                        continue
                
                if va_at_t:
                    # Promedio sobre realizaciones para este tiempo
                    avg_va[t_idx] = np.mean(va_at_t)
                    std_va[t_idx] = np.std(va_at_t)
            
            print(f"\nSimulaciones válidas procesadas: {valid_simulations}")
            
            return {
                'times': time_points,
                'avg_va': avg_va,
                'std_va': std_va
            }
                
        except Exception as e:
            logging.error(f"Error procesando directorio {param_dir}: {str(e)}")
            return None

    def plot_va(self, data, ap_value, bp_value):
        """
        Genera gráfico de va a lo largo del tiempo normalizado
        """
        if data is None:
            logging.error("No hay datos para graficar")
            return
            
        plt.figure(figsize=(12, 8))
        
        plt.plot(data['times'], data['avg_va'], 
                label='VA promedio', color='blue', linewidth=2)
        plt.fill_between(data['times'], 
                        data['avg_va'] - data['std_va'],
                        data['avg_va'] + data['std_va'],
                        alpha=0.3, color='blue')
        
        #plt.title(f'Evolución del parámetro de orden VA (ap={ap_value}, bp={bp_value})')
        plt.xlabel('Tiempo normalizado (s)')
        plt.ylabel('VA')
        plt.ylim(0, 1)  # VA está entre 0 y 1
        plt.grid(True)
        plt.legend()
        
        output_file = self.base_path / f'va_analysis_ap_{ap_value:.2f}_bp_{bp_value:.2f}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\nGráfico guardado en: {output_file}")

if __name__ == "__main__":
    # Especificar los valores de ap y bp a analizar
    ap_value = 35.0  # Modifica este valor
    bp_value = 1.2   # Modifica este valor
    
    try:
        analyzer = VaAnalyzer()
        data = analyzer.analyze_va(ap_value, bp_value)
        
        if data is not None:
            print(f"\nEstadísticas de VA para ap={ap_value}, bp={bp_value}:")
            print(f"VA promedio global: {np.mean(data['avg_va']):.3f} ± "
                  f"{np.mean(data['std_va']):.3f}")
            print(f"VA máximo: {np.max(data['avg_va']):.3f}")
            print(f"VA mínimo: {np.min(data['avg_va']):.3f}")
            
            analyzer.plot_va(data, ap_value, bp_value)
        else:
            print("No se pudieron analizar los datos de VA")
            
    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")
        print(f"Error: {str(e)}")