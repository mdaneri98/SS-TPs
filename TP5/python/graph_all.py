import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_data(filename):
    # Cargar los datos desde el archivo CSV
    df = pd.read_csv(filename)
    return df


def plot_ratio_vs_Bp(df):
    plt.figure(figsize=(10, 6))

    # Obtener los valores únicos de Ap
    Ap_values = sorted(df['ap'].unique())

    # Graficar el ratio de tries para cada valor de Ap en función de Bp
    for Ap in Ap_values:
        subset = df[df['ap'] == Ap]
        plt.plot(subset['bp'], subset['try_ratio'] * 100, marker='o', label=f'Ap = {Ap}')

    plt.xlabel('Bp')
    plt.ylabel('Ratio de tries (%)')
    plt.title('Ratio de tries vs Bp para diferentes valores de Ap')
    plt.grid(True)
    plt.legend()
    plt.savefig('ratio_vs_Bp_all.png')
    plt.close()


def plot_ratio_vs_Ap(df):
    plt.figure(figsize=(10, 6))

    # Obtener los valores únicos de Bp
    Bp_values = sorted(df['bp'].unique())

    # Graficar el ratio de tries para cada valor de Bp en función de Ap
    for Bp in Bp_values:
        subset = df[df['bp'] == Bp]
        plt.plot(subset['ap'], subset['try_ratio'] * 100, marker='o', label=f'Bp = {Bp}')

    plt.xlabel('Ap')
    plt.ylabel('Ratio de tries (%)')
    plt.title('Ratio de tries vs Ap para diferentes valores de Bp')
    plt.grid(True)
    plt.legend()
    plt.savefig('ratio_vs_Ap_all.png')
    plt.close()


def main():
    # Cargar datos
    filename = './outputs/heuristic_analysis_results.csv'  # Reemplaza con el nombre real del archivo CSV
    df = load_data(filename)

    # Crear ambos gráficos
    plot_ratio_vs_Bp(df)
    plot_ratio_vs_Ap(df)


if __name__ == "__main__":
    main()
