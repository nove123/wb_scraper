import time
from aiohttp import ClientSession
import asyncio
import json
import requests
import pandas as pd
import openpyxl
def make_url(shard, query):
    return f"https://catalog.wb.ru/catalog/{shard}/v4/filters?appType=1&{query}&curr=rub&dest=-1257786&spp=30&uclusters=2"

#В последней вложенности получаем все категории предметов
def get_last(data_list, url):
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]["filters"]
        if data[0]["key"] == "xsubject":
            for item in data[0]["items"]:
                try:
                    id_item = item["id"]
                    name = item["name"]
                    nesting_lvl = 99
                    data_list.append({
                        "id_item": id_item,
                        "name": name,
                        "nesting_lvl": nesting_lvl})
                except:
                    continue
        return data_list
    else:
        print("Ошибка при запросе к API")

#проходимся по подкаталогам
def get_subcatalog(data_list, data, nesting_lvl):
    for item in data:
        try:
            id_item = item["id"]
            name = item["name"]
            shard = item["shard"]
            query = item["query"]
            data_list.append({
                "id_item": id_item,
                "name": name,
                "nesting_lvl": nesting_lvl})
            if "childs" in item:
                get_subcatalog(data_list, item["childs"], nesting_lvl + 1)
            else:
                url_last_subcatalog = f"https://catalog.wb.ru/catalog/{shard}/v4/filters?appType=1&{query}&curr=rub&dest=-1257786&spp=30&uclusters=2"
                get_last(data_list, url_last_subcatalog)
        except:
            continue


def get_catalog(filename):
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v2.json'
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with pd.ExcelWriter(f'{filename}.xlsx') as writer:
            data = response.json()
            for item in data[2:5]:
                try:
                    if "childs" in item:
                        name = item["name"]
                        data_list = []
                        get_subcatalog(data_list, item["childs"], 1)
                        #Сохраняем лист с одной главной категорией
                        df = pd.DataFrame(data_list)
                        df.to_excel(excel_writer=writer, sheet_name=name)
                        print(f"Сохранили -- {name}")
                except:
                    continue
        print(f'Все сохранено в {filename}.xlsx')
    else:
        print("Ошибка при запросе к API")

def save_excel(data, filename):
    with pd.ExcelWriter(f'{filename}.xlsx') as writer:
        for key, value in data.items():
            df = pd.DataFrame(value)
            df.to_excel(excel_writer=writer, sheet_name=key)
    print(f'Все сохранено в {filename}.xlsx')

def main():
    print(time.strftime('%X'))
    get_catalog("catalog")
    print(time.strftime('%X'))

if __name__ == "__main__":
    main()