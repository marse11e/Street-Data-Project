import osmnx as ox
import pandas as pd
import geopandas as gpd
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


def extract_street_data(edge, G):
    """Извлекает данные о улице: название, длина, начальные и конечные координаты."""
    street_name = edge['name']
    if isinstance(street_name, list):
        street_name = street_name[0] if street_name else None
    length = edge['length']
    start_coord = edge.geometry.coords[0]
    end_coord = edge.geometry.coords[-1]
    return {
        'Название улицы': street_name,
        'Длина': length,
        'Начальные координаты': start_coord,
        'Конечные координаты': end_coord
    }


def save_street_data_to_csv(edges, G, output_path):
    """Сохраняет данные о улицах в CSV файл."""
    street_data = []
    for idx, edge in edges.iterrows():
        street_data.append(extract_street_data(edge, G))

    df = pd.DataFrame(street_data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Данные о улицах сохранены в {output_path}")


def main():
    """Основная функция для выполнения скрипта."""
    start_time = time.time()
    city = input("Введите название города: ").title()

    admin_poly = get_city_geometry(city)
    G = fetch_graph_with_parallel_processing(admin_poly)
    nodes, edges = ox.graph_to_gdfs(G)

    output_csv_path = f'static/street_data_csv/{city}_street_data.csv'
    save_street_data_to_csv(edges, G, output_csv_path)

    end_time = time.time()
    print(f"Количество узлов: {G.number_of_nodes()}, Количество дорог: {G.number_of_edges()}")
    print(f"Время выполнения: {end_time - start_time} секунд")
    print(f"Данные о улицах сохранены в {output_csv_path}")


if __name__ == "__main__":
    main()
