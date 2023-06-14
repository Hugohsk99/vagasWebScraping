import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}

def raspar_dados_vagas(url):
    time.sleep(2)  
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    vagas = []
    
    jobs = soup.find_all("div", {"class": "job job__vip__candidacy"})
    
    for job in jobs:
        title_tag = job.find("h2").find("strong").find("a")
        title = title_tag.text.strip() if title_tag else None

        num_jobs = re.search(r'\d+', title)
        num_jobs = int(num_jobs.group()) if num_jobs else 1

        location_tag = job.find('dt', string='Localização:').find_next_sibling('dd')
        location = location_tag.text.strip() if location_tag else None

        salary_tag = job.find('dt', string='Salário:').find_next_sibling('dd')
        salary = salary_tag.text.strip() if salary_tag else None

        company_tag = job.find('dt', string='Empresa:').find_next_sibling('dd')
        company = company_tag.text.strip() if company_tag else None

        description_tag = job.find("p", {"class": "job__description__value"})
        description = description_tag.text.strip() if description_tag else None

        vagas.append({"Título da Vaga": title, 
                      "Localização": location, 
                      "Salário": salary, 
                      "Empresa": company,
                      "Número de Vagas": num_jobs,
                      "Descrição": description}) 
    
    return vagas


base_url = "https://www.bne.com.br/vagas-de-emprego-em-rio-de-janeiro-rj/?Page={}&CityName=rio-de-janeiro-rj&Sort=0"

todos_dados_vagas = []
for page_number in range(1, 60):  
    page_url = base_url.format(page_number)
    dados_vagas = raspar_dados_vagas(page_url)
    todos_dados_vagas.extend(dados_vagas)

df_vagas = pd.DataFrame(todos_dados_vagas)

df_vagas_com_salario = df_vagas[df_vagas['Salário'] != 'a combinar']
df_vagas_a_combinar = df_vagas[df_vagas['Salário'] == 'a combinar']

df_vagas = pd.concat([df_vagas_com_salario, df_vagas_a_combinar])

df_vagas.to_excel("vagas.xlsx", index=False)

print(df_vagas)
