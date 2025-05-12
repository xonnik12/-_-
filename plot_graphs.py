import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import itertools
import re
import spacy
import community  # библиотека python-louvain
# python -m spacy download ru_core_news_sm


# Загружаем предобученную модель для русского языка
nlp = spacy.load("ru_core_news_sm")

# ИЗВЛЕЧЕНИЕ ЛЮДЕЙ ИЗ ТЕКСТОВ (через spaCy)
def extract_people_from_text(text):
    doc = nlp(text)  # Обрабатываем текст через spaCy
    people = [ent.text for ent in doc.ents if ent.label_ == "PER"]  # Извлекаем сущности типа "PER"
    return set(people)  # Возвращаем уникальные имена


def plot_graph_epoch(num_epoch):
    # функция строит граф только по 1 учебнику!!! иначе граф будет нереально большой и не отобразится
    current_merged = merged[merged['Код учебника'] == num_epoch]
    # # Уникальные имена
    person_texts = {}


    for index, row in current_merged.iterrows():
        # иногда в примечании могут быть пропуски
        try:
            text = row['ТЕКСТ'] + " " + row['Примечание']
        except:
            text = row['ТЕКСТ'] 
        epoch = str(row["Код учебника"]).strip()
        person = row['ФИО']
        text_clean = text.lower()
        if person not in person_texts:
            person_texts[person] = {"texts": [], "epoch": epoch}
        person_texts[person]["texts"].append(text)


    # Обновляем словарь person_texts, добавляя извлеченные имена людей
    for person, info in person_texts.items():
        all_texts = " ".join(info["texts"])  # Объединяем все тексты для данного человека
        extracted_people = extract_people_from_text(all_texts)  # Извлекаем имена людей
        info["extracted_people"] = extracted_people  # Добавляем их в словарь
    
    # for k,v in person_texts.items():
    #     print(k, ' - ', v)

    # # 4. Строим граф
    G = nx.Graph()


    # Добавляем вершины с атрибутом "эпоха"
    for person, info in person_texts.items():
        G.add_node(person, epoch=info["epoch"], extracted_people=info["extracted_people"])

    # ИЩЕМ СВЯЗИ ПО СОВПАДЕНИЯМ В ИЗВЛЕЧЕННЫХ ЛЮДЯХ
    persons = list(person_texts.keys())

    for i in range(len(persons)):
        for j in range(i + 1, len(persons)):
            p1, p2 = persons[i], persons[j]
            
            # Если хотя бы один человек извлечен из текстов обоих персон
            if person_texts[p1]["extracted_people"] & person_texts[p2]["extracted_people"]:
                G.add_edge(p1, p2)

    # КЛАСТЕРИЗАЦИЯ (алгоритм Louvain)
    partition = community.best_partition(G)

    # Создаем объект PyVis для визуализации
    net = Network(notebook=False, height="800px", width="100%", bgcolor="#ffffff", font_color="black")

    # Переносим вершины из графа NetworkX в PyVis
    for node in G.nodes:
        epoch = G.nodes[node]["epoch"]  # Получаем эпоху для цвета вершины
        cluster = partition[node]  # Получаем номер кластера для группы
        net.add_node(node, label=node, group=cluster)

    # Переносим ребра из графа NetworkX в PyVis
    for source, target in G.edges:
        net.add_edge(source, target)

    # Настройки визуализации (опционально)
    net.toggle_physics(True)  # Включаем физику для лучшей интерактивности
    net.show_buttons(filter_=['physics'])  # Показываем кнопки для настройки физики

    # Сохраняем и открываем
    net.show(f"graph_{num_epoch}.html", notebook=False)
    print(f"Готово! Файл graph_{num_epoch}.html открыт в браузере.")



df_persona = pd.read_csv("persons.csv")
df_uch = pd.read_csv("uch.csv")
df_content = pd.read_csv("content.csv")
df_record = pd.read_csv("records.csv")

# Сначала мержим записи с персонами
merged = df_record.merge(
    df_persona,
    left_on="Код персоны",
    right_on="Код",
    suffixes=('', '_персона')
)

# Потом подтягиваем учебник
merged = merged.merge(
    df_uch,
    left_on="Код учебника",
    right_on="Код",
    suffixes=('', '_учебник')
)

merged.to_csv("merged_csv")

# Загружаем предобученную модель для русского языка
nlp = spacy.load("ru_core_news_sm")

for i in range(1,8):
    plot_graph_epoch(i)