import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_dynamic_data(filepath):
    """Carga los datos dinámicos de una simulación."""
    times = []
    player_positions = []  # Posiciones del jugador rojo
    
    with open(filepath, 'r') as f:
        current_time = None
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            try:
                time = float(line)
                current_time = time
                times.append(time)
                continue
            except ValueError:
                pass
                
            # Procesamos solo al jugador rojo (ID = 0)
            parts = line.split(',')
            if len(parts) == 6 and int(parts[0]) == 0:
                x = float(parts[1])
                player_positions.append(x)
    
    return np.array(times), np.array(player_positions)

def analyze_simulation(filepath):
    """Analiza una simulación individual."""
    if not os.path.exists(filepath):
        return None, False
        
    times, positions = load_dynamic_data(filepath)
    
    if len(positions) == 0:
        return None, False
    
    # Máxima distancia recorrida en x
    max_distance = abs(100 - np.min(positions))  # 100 es el ancho del campo
    
    # Determinar si fue try (llegó cerca del ingoal)
    is_try = np.min(positions) < 1.0  # consideramos try si llegó a x < 1
    
    return max_distance, is_try

def get_simulation_dirs(base_dir, prefix):
    """Obtiene las carpetas de simulación existentes."""
    if not os.path.exists(base_dir):
        return []
    return sorted([d for d in os.listdir(base_dir) if d.startswith(prefix)])

def run_heuristic_analysis():
    """Analiza el comportamiento variando el parámetro de la heurística."""
    base_dir = "outputs/heuristic_analysis"
    param_dirs = get_simulation_dirs(base_dir, "param_")
    
    if not param_dirs:
        print("No se encontraron simulaciones para análisis de heurística")
        return None, None, None
    
    # Extraer los valores de los parámetros de los nombres de las carpetas
    parameters = []
    avg_distances = []
    try_fractions = []
    
    for param_dir in param_dirs:
        try:
            param = float(param_dir.split('_')[1])
            sim_dirs = get_simulation_dirs(os.path.join(base_dir, param_dir), "sim_")
            
            if not sim_dirs:
                continue
                
            distances = []
            try_count = 0
            num_sims = len(sim_dirs)
            
            for sim_dir in sim_dirs:
                dynamic_file = os.path.join(base_dir, param_dir, sim_dir, "dynamic.txt")
                max_dist, is_try = analyze_simulation(dynamic_file)
                
                if max_dist is not None:
                    distances.append(max_dist)
                    if is_try:
                        try_count += 1
            
            if distances:
                parameters.append(param)
                avg_distances.append(np.mean(distances))
                try_fractions.append(try_count / num_sims)
                
        except (ValueError, IndexError):
            continue
    
    # Convertir a numpy arrays
    parameters = np.array(parameters)
    avg_distances = np.array(avg_distances)
    try_fractions = np.array(try_fractions)
    
    # Ordenar por parámetro
    sort_idx = np.argsort(parameters)
    parameters = parameters[sort_idx]
    avg_distances = avg_distances[sort_idx]
    try_fractions = try_fractions[sort_idx]
    
    # Guardar resultados
    results = np.column_stack((parameters, avg_distances, try_fractions))
    np.savetxt('heuristic_results.txt', results, 
               header='parameter,avg_distance,try_fraction', 
               delimiter=',', comments='')
    
    # Visualizar resultados
    plot_results(parameters, avg_distances, try_fractions, 'heuristic')
    
    return parameters, avg_distances, try_fractions

def run_players_analysis():
    """Analiza el comportamiento variando el número de jugadores."""
    base_dir = "outputs/players_analysis"
    player_dirs = get_simulation_dirs(base_dir, "N_")
    
    if not player_dirs:
        print("No se encontraron simulaciones para análisis de jugadores")
        return None, None, None
    
    player_counts = []
    avg_distances = []
    try_fractions = []
    
    for player_dir in player_dirs:
        try:
            N = int(player_dir.split('_')[1])
            sim_dirs = get_simulation_dirs(os.path.join(base_dir, player_dir), "sim_")
            
            if not sim_dirs:
                continue
                
            distances = []
            try_count = 0
            num_sims = len(sim_dirs)
            
            for sim_dir in sim_dirs:
                dynamic_file = os.path.join(base_dir, player_dir, sim_dir, "dynamic.txt")
                max_dist, is_try = analyze_simulation(dynamic_file)
                
                if max_dist is not None:
                    distances.append(max_dist)
                    if is_try:
                        try_count += 1
            
            if distances:
                player_counts.append(N)
                avg_distances.append(np.mean(distances))
                try_fractions.append(try_count / num_sims)
                
        except (ValueError, IndexError):
            continue
    
    # Convertir a numpy arrays
    player_counts = np.array(player_counts)
    avg_distances = np.array(avg_distances)
    try_fractions = np.array(try_fractions)
    
    # Ordenar por número de jugadores
    sort_idx = np.argsort(player_counts)
    player_counts = player_counts[sort_idx]
    avg_distances = avg_distances[sort_idx]
    try_fractions = try_fractions[sort_idx]
    
    # Guardar resultados
    results = np.column_stack((player_counts, avg_distances, try_fractions))
    np.savetxt('players_results.txt', results, 
               header='players,avg_distance,try_fraction', 
               delimiter=',', comments='')
    
    # Visualizar resultados
    plot_results(player_counts, avg_distances, try_fractions, 'players')
    
    return player_counts, avg_distances, try_fractions

def plot_results(x_values, distances, fractions, analysis_type):
    """Genera gráficos de los resultados."""
    plt.figure(figsize=(15, 5))
    
    # Gráfico de distancia promedio
    plt.subplot(1, 3, 1)
    plt.plot(x_values, distances, 'b-o')
    plt.xlabel('Parámetro' if analysis_type == 'heuristic' else 'Número de jugadores')
    plt.ylabel('Distancia promedio recorrida (m)')
    plt.grid(True)
    plt.title('Distancia Promedio')
    
    # Gráfico de fracción de tries
    plt.subplot(1, 3, 2)
    plt.plot(x_values, fractions, 'r-o')
    plt.xlabel('Parámetro' if analysis_type == 'heuristic' else 'Número de jugadores')
    plt.ylabel('Fracción de tries logrados')
    plt.grid(True)
    plt.title('Fracción de Tries')
    
    # Gráfico combinado (producto normalizado)
    plt.subplot(1, 3, 3)
    # Normalizar cada métrica
    norm_distances = distances / np.max(distances) if np.max(distances) > 0 else distances
    norm_fractions = fractions / np.max(fractions) if np.max(fractions) > 0 else fractions
    combined = norm_distances * norm_fractions
    plt.plot(x_values, combined, 'g-o')
    plt.xlabel('Parámetro' if analysis_type == 'heuristic' else 'Número de jugadores')
    plt.ylabel('Métrica combinada')
    plt.grid(True)
    plt.title('Métrica Combinada')
    
    plt.tight_layout()
    plt.savefig(f'{analysis_type}_analysis_results.png')
    plt.close()

if __name__ == "__main__":
    print("Analizando parámetro de heurística...")
    params, h_distances, h_fractions = run_heuristic_analysis()
    
    if params is not None and len(params) > 0:
        # Encontrar mejor parámetro usando métricas normalizadas
        norm_distances = h_distances / np.max(h_distances)
        norm_fractions = h_fractions / np.max(h_fractions)
        combined_metric = norm_distances * norm_fractions
        best_idx = np.argmax(combined_metric)
        
        print(f"\nMejor parámetro encontrado: {params[best_idx]:.2f}")
        print(f"Distancia promedio: {h_distances[best_idx]:.2f}")
        print(f"Fracción de tries: {h_fractions[best_idx]:.2f}")
        
        print("\nAnalizando número de jugadores...")
        players, p_distances, p_fractions = run_players_analysis()
        
        if players is not None and len(players) > 0:
            print("\nResultados para diferentes números de jugadores:")
            for i, N in enumerate(players):
                print(f"N={N}: Distancia={p_distances[i]:.2f}, "
                      f"Fracción tries={p_fractions[i]:.2f}")
    
    print("\nAnálisis completado. Se han generado archivos de resultados y gráficos.")