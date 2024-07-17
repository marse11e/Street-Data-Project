import osmnx as ox
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import time
import os


def get_graph(polygon):
    """Получает граф на основе полигона."""
    return ox.graph_from_polygon(polygon)


def get_city_geometry(city_name):
    """Получает геометрию города по его названию."""
    admin = ox.geocode_to_gdf(city_name)
    admin_poly = admin.geometry.values[0]
    return admin_poly


def fetch_graph_with_parallel_processing(polygon):
    """Получает граф с использованием параллельной обработки."""
    with ThreadPoolExecutor() as executor:
        future = executor.submit(get_graph, polygon)
        return future.result()


def plot_graph(city, nodes, edges, num_nodes, num_edges, output_path):
    """Отображает граф и сохраняет визуализацию."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(1, figsize=(10, 10))
    edges.plot(ax=ax, edgecolor='white', linewidth=0.3)

    ax.set_title(f'Уличная сеть города {city}', fontsize=20, color='white')
    ax.text(0.02, 0.94, f'Количество узлов: {num_nodes}',
            transform=ax.transAxes, fontsize=12, color='red', verticalalignment='top')
    ax.text(0.02, 0.90, f'Количество дорог: {num_edges}',
            transform=ax.transAxes, fontsize=12, color='red', verticalalignment='top')
    ax.axis('off')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor=fig.get_facecolor())


def main():
    """Основная функция для выполнения скрипта."""
    start_time = time.time()
    city = input("Введите название города: ").title()

    admin_poly = get_city_geometry(city)
    G = fetch_graph_with_parallel_processing(admin_poly)

    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    print(f"Количество узлов: {num_nodes}, Количество дорог: {num_edges}")

    nodes, edges = ox.graph_to_gdfs(G)

    output_path = f'static/street_graph_img/{city}_street_network.png'
    plot_graph(city, nodes, edges, num_nodes, num_edges, output_path)

    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time} секунд")
    print(f"Визуализация сохранена в {output_path}")


if __name__ == "__main__":
    main()
