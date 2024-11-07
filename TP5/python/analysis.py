import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='analysis.log'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class SimulationAnalyzer:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path).absolute()
        logging.info(f"Ruta base inicial: {self.base_path}")
        
        if not (self.base_path / "outputs").exists():
            logging.error(f"No se encontró el directorio outputs en {self.base_path}")
            raise FileNotFoundError(f"No se encontró el directorio outputs en {self.base_path}")
            
        self.base_path = self.base_path / "outputs"
        logging.info(f"Ruta base final: {self.base_path}")
    
    def parse_dynamic_file(self, file_path):
        """
        Parsea el archivo dynamic.txt y retorna todas las posiciones x
        """
        try:
            logging.debug(f"Intentando abrir archivo: {file_path}")
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            positions = []
            i = 0
            while i < len(lines):
                # Saltar el tiempo
                i += 1
                if i >= len(lines):
                    break
                
                # Leer la línea del jugador
                line = lines[i].strip()
                if not line:
                    continue
                
                try:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        x_pos = float(parts[1])
                        positions.append(x_pos)
                except (ValueError, IndexError) as e:
                    logging.debug(f"Error al procesar línea {i}: {line}")
                    continue
                
                # Avanzar hasta la próxima marca de tiempo
                i += 1
                while i < len(lines):
                    if ',' not in lines[i]:
                        i -= 1
                        break
                    i += 1
                i += 1
            
            return positions if positions else None
            
        except Exception as e:
            logging.error(f"Error al parsear dynamic.txt: {str(e)}")
            return None
    
    def analyze_trajectory(self, positions):
        """
        Analiza una trayectoria completa y retorna métricas relevantes
        """
        if not positions or len(positions) < 2:
            return None
            
        # Posición inicial (debería ser cercana a 100)
        start_pos = positions[0]
        
        # Máxima distancia recorrida desde la posición inicial
        distances = [abs(pos - start_pos) for pos in positions]
        max_distance = max(distances)
        
        # Verificar si se logró el try (llegó a x ≤ 0)
        min_x = min(positions)
        try_achieved = min_x <= 0
        
        return {
            'start_pos': start_pos,
            'max_distance': max_distance,
            'try_achieved': try_achieved,
            'min_x': min_x
        }
    
    def load_simulation_data(self, sim_path):
        """
        Carga y analiza los datos de una simulación individual
        """
        try:
            dynamic_path = sim_path / "dynamic.txt"
            logging.debug(f"Intentando cargar: {dynamic_path}")
            
            if not dynamic_path.exists():
                logging.error(f"Archivo no encontrado: {dynamic_path}")
                return None
            
            positions = self.parse_dynamic_file(dynamic_path)
            if not positions:
                return None
                
            return self.analyze_trajectory(positions)
            
        except Exception as e:
            logging.error(f"Error al cargar datos de {sim_path}: {str(e)}")
            return None
    
    def load_heuristic_data(self):
        """
        Carga los datos de las simulaciones con variación de parámetros heurísticos
        """
        results = []
        heuristic_path = self.base_path / "heuristic_analysis"
        
        if not heuristic_path.exists():
            logging.error(f"No se encontró el directorio: {heuristic_path}")
            return pd.DataFrame()
        
        logging.info(f"Buscando datos en: {heuristic_path}")
        
        param_dirs = [d for d in heuristic_path.iterdir() 
                     if d.is_dir() and d.name.startswith("ap_")]
        
        if not param_dirs:
            logging.error("No se encontraron directorios de parámetros")
            return pd.DataFrame()
        
        for param_dir in param_dirs:
            logging.info(f"Procesando directorio: {param_dir}")
            
            try:
                dir_parts = param_dir.name.split('_')
                ap_val = float(dir_parts[1])
                bp_val = float(dir_parts[3])
                
                distances = []
                tries_achieved = 0
                total_sims = 0
                valid_sims = 0
                
                sim_dirs = [d for d in param_dir.iterdir() 
                          if d.is_dir() and d.name.startswith("sim_")]
                
                for sim_dir in sim_dirs:
                    total_sims += 1
                    sim_data = self.load_simulation_data(sim_dir)
                    
                    if sim_data is None:
                        continue
                    
                    valid_sims += 1
                    distances.append(sim_data['max_distance'])
                    
                    if sim_data['try_achieved']:
                        tries_achieved += 1
                
                if valid_sims > 0:
                    results.append({
                        'ap': ap_val,
                        'bp': bp_val,
                        'avg_distance': np.mean(distances),
                        'std_distance': np.std(distances),
                        'try_ratio': (tries_achieved / valid_sims) * 100,
                        'total_sims': total_sims,
                        'valid_sims': valid_sims
                    })
                    logging.info(f"Procesado: ap={ap_val}, bp={bp_val}, "
                               f"sims válidas={valid_sims}/{total_sims}, "
                               f"tries={tries_achieved}")
                
            except Exception as e:
                logging.error(f"Error al procesar directorio {param_dir}: {str(e)}")
                continue
        
        return pd.DataFrame(results)
    
    def analyze_heuristic_parameters(self):
        """
        Analiza el impacto de los parámetros heurísticos
        """
        logging.info("Iniciando análisis de parámetros heurísticos")
        df = self.load_heuristic_data()
        
        if df.empty:
            logging.error("No hay datos para analizar")
            return None
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Heatmap para distancia promedio
            pivot_dist = df.pivot(index='ap', columns='bp', values='avg_distance')
            pivot_dist = pivot_dist.sort_index(ascending=False)  # Ordenar ap de mayor a menor
            pivot_dist = pivot_dist.sort_index(axis=1)  # Ordenar bp de menor a mayor
            
            sns.heatmap(pivot_dist, ax=ax1, cmap='viridis', 
                       annot=False, cbar_kws={'label': 'Distancia (m)'})
            #ax1.set_title('Distancia Promedio Recorrida')
            ax1.set_xlabel('Bp')
            ax1.set_ylabel('Ap')
            
            # Heatmap para ratio de tries
            pivot_tries = df.pivot(index='ap', columns='bp', values='try_ratio')
            pivot_tries = pivot_tries.sort_index(ascending=False)  # Ordenar ap de mayor a menor
            pivot_tries = pivot_tries.sort_index(axis=1)  # Ordenar bp de menor a mayor
            
            sns.heatmap(pivot_tries, ax=ax2, cmap='viridis',
                       annot=False, cbar_kws={'label': 'Tries ratio (%)'})
            #ax2.set_title('Ratio de Tries Logrados')
            ax2.set_xlabel('Bp')
            ax2.set_ylabel('Ap')
            
            plt.tight_layout()
            plt.savefig(self.base_path / 'heuristic_analysis_results.png')
            plt.close()
            
            df.to_csv(self.base_path / 'heuristic_analysis_results.csv', index=False)
            
            best_distance = df.loc[df['avg_distance'].idxmax()]
            best_tries = df.loc[df['try_ratio'].idxmax()]
            
            logging.info("Análisis completado exitosamente")
            
            return {
                'best_distance': {
                    'ap': best_distance['ap'],
                    'bp': best_distance['bp'],
                    'value': best_distance['avg_distance'],
                    'std': best_distance['std_distance'],
                    'valid_sims': best_distance['valid_sims']
                },
                'best_tries': {
                    'ap': best_tries['ap'],
                    'bp': best_tries['bp'],
                    'value': best_tries['try_ratio'],
                    'valid_sims': best_tries['valid_sims']
                }
            }
            
        except Exception as e:
            logging.error(f"Error durante el análisis: {str(e)}")
            return None

if __name__ == "__main__":
    try:
        current_dir = Path.cwd()
        print(f"Directorio actual: {current_dir}")
        print(f"Contenido del directorio:")
        for item in current_dir.iterdir():
            print(f"  {item}")
            
        analyzer = SimulationAnalyzer()
        
        print("\nAnalizando parámetros heurísticos...")
        best_params = analyzer.analyze_heuristic_parameters()
        
        if best_params:
            print("\nMejores parámetros encontrados:")
            print("\nPara distancia máxima recorrida:")
            print(f"ap={best_params['best_distance']['ap']}, "
                  f"bp={best_params['best_distance']['bp']}")
            print(f"Distancia promedio: {best_params['best_distance']['value']:.2f} "
                  f"± {best_params['best_distance']['std']:.2f}")
            print(f"Simulaciones válidas: {best_params['best_distance']['valid_sims']}")
            
            print("\nPara ratio de tries:")
            print(f"ap={best_params['best_tries']['ap']}, "
                  f"bp={best_params['best_tries']['bp']}")
            print(f"Ratio de tries: {best_params['best_tries']['value']:.3f}")
            print(f"Simulaciones válidas: {best_params['best_tries']['valid_sims']}")
        else:
            print("\nNo se pudieron determinar los mejores parámetros")
            
    except Exception as e:
        logging.error(f"Error en la ejecución principal: {str(e)}")