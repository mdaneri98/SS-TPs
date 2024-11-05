import numpy as np
import matplotlib.pyplot as plt
import csv


def generate_data_from_file(filepath):
    data = {}
    Bp_values = set()
    Ap_values = set()

    # Leer el archivo CSV
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                Ap = float(row['ap'])
                Bp = float(row['bp'])
                try_ratio = float(row['try_ratio'])
            except ValueError:
                print(f"Error en la conversión de valores en la fila: {row}")
                continue

            # Agregar Ap y Bp a las listas únicas
            Ap_values.add(Ap)
            Bp_values.add(Bp)

            # Asegura que data tenga una entrada para este Ap
            if Ap not in data:
                data[Ap] = {}

            # Inicializa la lista para guardar ratios para este Bp específico
            if Bp not in data[Ap]:
                data[Ap][Bp] = []

            # Agregar el ratio de tries
            data[Ap][Bp].append(try_ratio)

    # Convertir Bp y Ap a listas ordenadas
    Bp_range = np.array(sorted(Bp_values))
    Ap_values = sorted(Ap_values)

    # Calcular el promedio de ratios para cada par (Ap, Bp)
    averaged_data = {Ap: [np.mean(data[Ap][Bp]) for Bp in Bp_range] for Ap in Ap_values}

    return Bp_range, Ap_values, averaged_data


def plot_ratio_vs_Bp(Bp_range, Ap_values, data):
    plt.figure(figsize=(10, 6))

    for Ap in Ap_values:
        plt.plot(Bp_range, data[Ap], marker='o', label=f'Ap = {Ap}')

    plt.xlabel('Bp')
    plt.ylabel('Ratio de tries (%)')
    plt.title('Ratio de tries vs Bp para diferentes valores de Ap')
    plt.grid(True)
    plt.legend()
    plt.savefig('ratio_vs_Bp.png')
    plt.close()


def plot_ratio_vs_Ap(Bp_range, Ap_values, data):
    Ap_points = np.linspace(min(Ap_values), max(Ap_values), 40)
    selected_Bp = [2, 4, 6, 8]  # Valores específicos de Bp para graficar

    plt.figure(figsize=(10, 6))

    for Bp in selected_Bp:
        bp_idx = np.abs(Bp_range - Bp).argmin()
        ratios = [data[Ap][bp_idx] for Ap in Ap_values]

        ratios_smooth = np.interp(Ap_points, Ap_values, ratios)
        plt.plot(Ap_points, ratios_smooth, marker='o', label=f'Bp = {Bp}')

    plt.xlabel('Ap')
    plt.ylabel('Ratio de tries (%)')
    plt.title('Ratio de tries vs Ap para diferentes valores de Bp')
    plt.grid(True)
    plt.legend()
    plt.savefig('ratio_vs_Ap.png')
    plt.close()


def main():
    # Especifica la ruta del archivo consolidado
    filepath = './outputs/heuristic_analysis_results.csv'

    # Genera datos desde el archivo consolidado
    Bp_range, Ap_values, data = generate_data_from_file(filepath)

    # Crear ambos gráficos
    plot_ratio_vs_Bp(Bp_range, Ap_values, data)
    plot_ratio_vs_Ap(Bp_range, Ap_values, data)


if __name__ == "__main__":
    main()
