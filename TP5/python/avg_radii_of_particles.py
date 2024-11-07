import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='radius_analysis.log'
)

class RadiusAnalyzer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path).absolute() / "outputs"
        if not self.base_path.exists():
            raise FileNotFoundError(f"No se encontró el directorio outputs en {base_path}")
            
    def parse_dynamic_file(self, file_path):
        """
        Parsea el archivo dynamic.txt y retorna los radios del jugador y los demás
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            times = []
            player_radii = []
            others_radii = []
            
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
                    
                # Leer línea del jugador
                player_line = lines[i].strip().split(',')
                if len(player_line) >= 6:  # Asumiendo que el radio está en la posición 5
                    radius = float(player_line[5])
                    player_radii.append(radius)
                
                # Leer radios de los otros jugadores
                other_rads = []
                i += 1
                while i < len(lines) and ',' in lines[i]:
                    parts = lines[i].strip().split(',')
                    if len(parts) >= 6:
                        radius = float(parts[5])
                        other_rads.append(radius)
                    i += 1
                
                if other_rads:
                    others_radii.append(np.mean(other_rads))
            
            return {
                'times': np.array(times),
                'player_radii': np.array(player_radii),
                'others_radii': np.array(others_radii)
            }
            
        except Exception as e:
            logging.error(f"Error al parsear archivo {file_path}: {str(e)}")
            return None

    def analyze_radii(self, ap_value, bp_value):
        """
        Analiza los radios para un ap y bp específicos
        """
        # Buscar directorio específico
        dir_name = f"ap_{ap_value:.2f}_bp_{bp_value:.2f}"
        param_dir = self.base_path / "heuristic_analysis" / dir_name
        
        if not param_dir.exists():
            logging.error(f"No se encontró el directorio: {param_dir}")
            return None
            
        try:
            sim_radii = []
            valid_simulations = 0
            
            # Procesar cada simulación
            for sim_dir in param_dir.glob("sim_*"):
                dynamic_file = sim_dir / "dynamic.txt"
                if not dynamic_file.exists():
                    continue
                    
                rad_data = self.parse_dynamic_file(dynamic_file)
                if rad_data is None or len(rad_data['times']) <= 1:
                    continue
                
                # Normalizar tiempo a [0,1]
                max_time = rad_data['times'][-1]
                if max_time <= 0:
                    continue
                    
                normalized_times = rad_data['times'] / max_time
                
                sim_radii.append({
                    'times': normalized_times,
                    'player_radii': rad_data['player_radii'],
                    'others_radii': rad_data['others_radii']
                })
                valid_simulations += 1
            
            if not sim_radii:
                logging.error("No se encontraron simulaciones válidas")
                return None
            
            # Calcular promedio en cada punto temporal
            time_points = np.linspace(0, 1, 100)  # 100 puntos normalizados
            avg_player = np.zeros(len(time_points))
            avg_others = np.zeros(len(time_points))
            std_player = np.zeros(len(time_points))
            std_others = np.zeros(len(time_points))
            
            for t_idx, t in enumerate(time_points):
                player_rads = []
                others_rads = []
                
                for sim in sim_radii:
                    try:
                        # Interpolar valores para este punto temporal
                        if len(sim['times']) > 1:
                            player_rad = np.interp(t, sim['times'], sim['player_radii'])
                            others_rad = np.interp(t, sim['times'], sim['others_radii'])
                            
                            player_rads.append(player_rad)
                            others_rads.append(others_rad)
                    except Exception as e:
                        continue
                
                if player_rads and others_rads:
                    avg_player[t_idx] = np.mean(player_rads)
                    avg_others[t_idx] = np.mean(others_rads)
                    std_player[t_idx] = np.std(player_rads)
                    std_others[t_idx] = np.std(others_rads)
            
            print(f"\nSimulaciones válidas procesadas: {valid_simulations}")
            
            return {
                'times': time_points,
                'avg_player': avg_player,
                'std_player': std_player,
                'avg_others': avg_others,
                'std_others': std_others
            }
                
        except Exception as e:
            logging.error(f"Error procesando directorio {param_dir}: {str(e)}")
            return None

    def plot_radii(self, data, ap_value, bp_value):
        """
        Genera gráfico de radios promedio a lo largo del tiempo
        """
        if data is None:
            logging.error("No hay datos para graficar")
            return
            
        plt.figure(figsize=(12, 8))
        
        # Graficar radio del jugador
        plt.plot(data['times'], data['avg_player'], 
                label='Jugador', color='blue', linewidth=2)
        plt.fill_between(data['times'], 
                        data['avg_player'] - data['std_player'],
                        data['avg_player'] + data['std_player'],
                        alpha=0.3, color='blue')
        
        # Graficar radio de los otros
        plt.plot(data['times'], data['avg_others'],
                label='Oponentes', color='red', linewidth=2)
        plt.fill_between(data['times'],
                        data['avg_others'] - data['std_others'],
                        data['avg_others'] + data['std_others'],
                        alpha=0.3, color='red')
        
        #plt.title(f'Evolución de radios (ap={ap_value}, bp={bp_value})')
        plt.xlabel('Tiempo normalizado (s)')
        plt.ylabel('Radio (m)')
        plt.grid(True)
        plt.legend()
        
        output_file = self.base_path / f'radius_analysis_ap_{ap_value:.2f}_bp_{bp_value:.2f}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\nGráfico guardado en: {output_file}")

if __name__ == "__main__":
    # Especificar los valores de ap y bp a analizar
    ap_value = 35.0  # Modifica este valor
    bp_value = 1.2   # Modifica este valor
    
    try:
        analyzer = RadiusAnalyzer()
        data = analyzer.analyze_radii(ap_value, bp_value)
        
        if data is not None:
            print(f"\nEstadísticas de radio para ap={ap_value}, bp={bp_value}:")
            print("\nRadio del jugador:")
            print(f"Promedio global: {np.mean(data['avg_player']):.3f} ± "
                  f"{np.mean(data['std_player']):.3f} m")
            print(f"Máximo: {np.max(data['avg_player']):.3f} m")
            print(f"Mínimo: {np.min(data['avg_player']):.3f} m")
            
            print("\nRadio de los otros jugadores:")
            print(f"Promedio global: {np.mean(data['avg_others']):.3f} ± "
                  f"{np.mean(data['std_others']):.3f} m")
            print(f"Máximo: {np.max(data['avg_others']):.3f} m")
            print(f"Mínimo: {np.min(data['avg_others']):.3f} m")
            
            analyzer.plot_radii(data, ap_value, bp_value)
        else:
            print("No se pudieron analizar los radios")
            
    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")
        print(f"Error: {str(e)}")