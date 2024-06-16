import time
import requests
import pandas as pd


# В последней вложенности собираем все категории предметов
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
    else:
        print("Ошибка при запросе к API")


def get_subcatalog(data_list, data, nesting_lvl):
    for item in data:
        try:
            id_item = item["id"]
            name = item["name"]
            data_list.append({
                "id_item": id_item,
                "name": name,
                "nesting_lvl": nesting_lvl})
            if "childs" in item:
                get_subcatalog(data_list, item["childs"], nesting_lvl + 1)
            else:
                if "shard" in item and "query" in item:
                    shard = item["shard"]
                    query = item["query"]
                    url_last_subcatalog = f"https://catalog.wb.ru/catalog/{shard}/v4/filters?appType=1&{query}&curr" \
                                          f"=rub&dest=-1257786&spp=30&uclusters=2 "
                    get_last(data_list, url_last_subcatalog)
                else:
                    url_last_subcatalog = item["url"]
                    get_last(data_list, url_last_subcatalog)
        except:
            continue


def get_catalog():
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v2.json'
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        res = dict()
        for item in data:
            try:
                name = item["name"]
                res[name] = []
                get_subcatalog(res[name], item["childs"], 1)
            except:
                continue
        return res
    else:
        print("Ошибка при запросе к API")


def save_excel(data, filename):
    with pd.ExcelWriter(f'{filename}.xlsx') as writer:
        for key, value in data.items():
            df = pd.DataFrame(value)
            df.to_excel(excel_writer=writer, sheet_name=key)
    print(f'Все сохранено в {filename}.xlsx')


def main():
    save_excel(get_catalog(), "catalog")


if __name__ == "__main__":
    main()
