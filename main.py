import time
import json
import requests
from tqdm import tqdm
import pandas as pd
from collections import Counter
from wordcloud import WordCloud

def dump_json(obj, filename):
    """Функция сохранения JSON-файла на диск"""
    with open(filename, 'w', encoding='UTF-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)


def get_vacancies(text="python", experience=None, employment=None, schedule=None):
    """Функция для скачивания данных по API HeadHunter"""
    params = {
        "per_page": 100,
        "page": 0,
        "period": 30,
        "text": text,
        "experience": experience,
        "employment": employment,
        "schedule": schedule
    }

    res = requests.get("https://api.hh.ru/vacancies", params=params)
    if not res.ok:
        print('Error:', res)
    vacancies = res.json()["items"]

    pages = res.json()['pages']

    for page in tqdm(range(1, pages)):
        params['page'] = page
        res = requests.get("https://api.hh.ru/vacancies", params=params)
        if res.ok:
            response_json = res.json()
            vacancies.extend(response_json["items"])
        else:
            print(res)

    dump_json(vacancies, 'vacancies.json')

    return vacancies


def get_full_descriptions(vacancies):
    """Функция для скачивания полного описания вакансий (работает 20 минут!)"""
    vacancies_full = []
    for entry in tqdm.tqdm(vacancies):
        vacancy_id = entry['id']
        description = requests.get(f"https://api.hh.ru/vacancies/{vacancy_id}")
        vacancies_full.append(description.json())
        print(description.json())
        time.sleep(0.2)

    dump_json(vacancies_full, 'vacancies_full.json')

    return vacancies_full


def load_from_google_drive(file_id, filename):
    """Функция для загрузки уже скаченного файла вместо get_full_descriptions"""
    url = f"https://drive.google.com/uc?export=view&id={file_id}"
    res = requests.get(url)
    data = res.json()
    dump_json(data, filename)
    return data


vacancies = get_vacancies()
print('Загружено', len(vacancies), 'вакансий')
# vacancies_full = get_full_descriptions(vacancies)  # Выполняется ≈20 мин
vacancies_full = load_from_google_drive('1d2NfxfM2n48m5WS6oCCc3rcQ4hdnTQ1v', 'vacancies_full.json')

all_skills = []
for vacancy in vacancies_full:
    for skill in vacancy['key_skills']:
        all_skills.append(skill['name'])

frequencies = Counter(all_skills)

pd.DataFrame(vacancies).to_excel('Cписок вакансий.xlsx')
pd.DataFrame(vacancies_full).to_excel('Подробное описание вакансий.xlsx')

print('Топ навыков Python-разработчика:')
cloud = WordCloud()
cloud.generate_from_frequencies(frequencies=frequencies).to_image().show()
