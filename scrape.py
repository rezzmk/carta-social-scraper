import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.keys import Keys


base_url = "https://www.cartasocial.pt/resultados-da-pesquisa"

intervention_areas = {
    '1': 'Infância e Juventude',
    #'11': 'Crianças e Jovens',
    #'12': 'Crianças e Jovens com Deficiência',
    #'13': 'Crianças e Jovens em Situação de Perigo',
    '2': 'População Adulta',
    #'21': 'Pessoas Idosas',
    #'22': 'Pessoas Adultas com Deficiência',
    #'23': 'Pessoas em Situação de Dependência',
    #'24': 'Pessoas com Doença do Foro Mental/Psiquiátrico',
    #'25': 'Pessoas Sem-Abrigo',
    '3': 'Família e Comunidade',
    #'31': 'Familia e Comunidade em Geral',
    #'32': 'Pessoas com VIH/SIDA e suas Famílias',
    #'33': 'Pessoas Toxicodependentes',
    #'34': 'Pessoas Vítimas de Violência Doméstica',
    '4': 'Grupo Fechado',
    #'41': 'Respostas Pontuais'
}

social_answers = {
    "1": {
        "1101": "Ama",
        "1102": "Ama (Creche Familiar)",
        "1307": "Atividades Sócio-Educativas",
        "1305": "Casa de Acolhimento",
        "1306": "Casa de Acolhimento com Unidade de Apoio e Promoção de Autonomia dos Jovens",
        "1304": "Casa de Acolhimento para Resposta a Situações de Emergência",
        "1301": "Centro de Apoio Familiar e Aconselhamento Parental",
        "1105": "Centro de Atividades de Tempos Livres",
        "1103": "Creche",
        "1302": "Equipa de Rua Apoio a Crianças e Jovens",
        "1104": "Estabelecimento de Educação Pré-escolar",
        "1201": "Intervenção Precoce",
        "1202": "Lar de Apoio",
        "1203": "Transporte de Pessoas com Deficiência (Crianças e Jovens)"
    },
    "2": {
        "2302": "Apoio Domiciliário Integrado",
        "2502": "Atelier Ocupacional",
        "2201": "Centro de Atendimento, Acompanhamento e Reabilitação Social para Pessoas com Deficiência e incapacidade (CAARPD)",
        "2203": "Centro de Atividades e Capacitação para a Inclusão (CACI)",
        "2102": "Centro de Convívio",
        "2103": "Centro de Dia",
        "2104": "Centro de Noite",
        "2412": "Equipa de Apoio Domiciliário de CCI em saúde mental (EAD)",
        "2413": "Equipa de Apoio Domiciliário de CCI em saúde mental (EAD) - infância e juventude",
        "2304": "Equipa de Cuidados Continuados Integrados (ECCI)",
        "2501": "Equipa de Rua para Pessoas Sem-Abrigo",
        "2107": "Estrutura Residencial para Pessoas Idosas  ( Lar de Idosos e Residência)",
        "2401": "Fórum Sócio-Ocupacional",
        "2205": "Lar Residencial (Deficiência)",
        "2409": "Residência Autónoma de Saúde Mental (RA)",
        "2406": "Residência de Apoio Moderado (RAMo)",
        "2405": "Residência de Apoio Máximo (RAMa)",
        "2207": "Residência de Autonomização e Inclusão (RAI) ",
        "2407": "Residência de Treino de Autonomia (RTA)",
        "2408": "Residência de Treino de Autonomia tipo A - infância e adolescência (RTA/A)",
        "2202": "Serviço de Apoio Domiciliário (Deficiência)",
        "2301": "Serviço de Apoio Domiciliário (Dependência)",
        "2101": "Serviço de Apoio Domiciliário (Idosos)",
        "2206": "Transporte de Pessoas com Deficiência (Adultos)",
        "2309": "Unidade Ambulatória Pediátrica (UAP)",
        "2410": "Unidade Sócio-Ocupacional (USOa)",
        "2411": "Unidade Sócio-Ocupacional infância e adolescência (USO/IA)",
        "2303": "Unidade de Apoio Integrado",
        "2307": "Unidade de Convalescença (UC)",
        "2308": "Unidade de Cuidados Integrados Pediátricos (UCIP)",
        "2310": "Unidade de Cuidados Paliativos (UCP)",
        "2306": "Unidade de Longa Duração e Manutenção (ULDM)",
        "2305": "Unidade de Média Duração e Reabilitação (UMDR)",
        "2404": "Unidade de Vida Apoiada",
        "2403": "Unidade de Vida Autónoma",
        "2402": "Unidade de Vida Protegida"
    },
    "3": {
        "3109": "Ajuda Alimentar a Carenciados",
        "3302": "Apartamento de Reinserção Social",
        "3402": "Casa de Abrigo",
        "3201": "Centro  de Atendimento/Acompanhamento Psicossocial(VIH/SIDA) ",
        "3103": "Centro Comunitário (Família e Comunidade)",
        "3108": "Centro de Alojamento Temporário",
        "3106": "Centro de Apoio à Vida",
        "3104": "Centro de Férias e Lazer",
        "3107": "Comunidade de Inserção",
        "3301": "Equipa de Intervenção Directa",
        "3401": "Estrutura de Atendimento  (Pessoas vitimas de violência doméstica)",
        "3102": "Grupo de Auto-Ajuda (Família e Comunidade)",
        "3105": "Refeitório/Cantina Social",
        "3203": "Residência para Pessoas com VIH/SIDA",
        "3202": "Serviço de Apoio Domiciliário (VIH/SIDA)",
        "3101": "a Serviço de Atendimento e Acompanhamento Social   (Família e Comunidade)"
    },
    "4": {
        "4101": "Apoio Domiciliário para Guarda Crianças",
        "4102": "Apoio em Regime Ambulatório",
        "4105": "Centro de Reabilitação de Pessoas com Cegueira",
        "4104": "Escola de Cães-Guia",
        "4103": "Imprensa Braille",
        "4106": "Quinta Pedagógica"
    }
}

driver_url = 'http://localhost:9515'
chrome_options = Options()
driver = webdriver.Remote(command_executor=driver_url, options=chrome_options)

#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

excel_data = []
processed = {}

def process_data(source_code, intervention_area, social_response):
    soup = BeautifulSoup(source_code, 'html.parser')
    main_content_div = soup.find('div', id='_SocialLetterPortlet_WAR_cartasocialportlet_:form:maincontent')

    if not main_content_div:
        print(f"Main content div not found in {link}")
        return

    # Extract the name of the place
    name = main_content_div.find('h2').get_text(strip=True).replace("ui-button", "")
    duplication_key = f'{intervention_area}:{social_response}:{name}'
    if duplication_key in processed:
        print('duplicate record detected, skipping...')
        return

    processed[duplication_key] = True

    # Extract the contact info
    contact_divs = main_content_div.find_all('div', class_='span5')
    contact_info = {}
    for div in contact_divs:
        labels = div.find_all('label')
        ps = div.find_all('p')
        for label, p in zip(labels, ps):
            contact_info[label.get_text(strip=True)] = p.get_text(strip=True)

    services = []
    table_body = main_content_div.find('tbody')
    if table_body:
       rows = table_body.find_all('tr')
       for row in rows:
           first_column_text = row.find('td').get_text(strip=True)
           if first_column_text.replace(" ", "") in social_answer.replace(" ", ""):
               service_details = [td.get_text(strip=True) for td in row.find_all('td')]
               services.append(service_details)
           else:
               continue

    # Store or print the extracted information
    #print(name)
    #print(services)
    print(f'    processing {name} :: ({services[0][1]}, {services[0][3]})')
    if services[0][0].replace(" ", "") not in social_answer.replace(" ", ""):
        print("ERROR: Capacity failed")

    contact_info = {}
    for div in contact_divs:
        labels = div.find_all('label')
        ps = div.find_all('p')
        for label, p in zip(labels, ps):
            contact_info_key = label.get_text(strip=True)
            contact_info[contact_info_key] = p.get_text(strip=True)

    entry = {
        'Area de Intervencao': intervention_area,
        'Resposta Social': social_answer,
        'Nome': name,
        **contact_info,
        'Capacidade': services[0][1],
        'Horario': services[0][3]
    }
    excel_data.append(entry)

def get_table(html):
    soup = BeautifulSoup(html, 'html.parser')

    ul_id = "_SocialLetterPortlet_WAR_cartasocialportlet_:sidebarForm:j_idt49_list"
    ul_element = soup.find('ul', id=ul_id)
    result = ul_element.text
    #print(result)
    return result

def process_links(html, intervention_area, social_response):
    soup = BeautifulSoup(html, 'html.parser')

    ul_id = "_SocialLetterPortlet_WAR_cartasocialportlet_:sidebarForm:j_idt49_list"
    ul_element = soup.find('ul', id=ul_id)

    links = []
    if ul_element:
        for a in ul_element.find_all('a', href=True):
            response = requests.get(a['href'])
            if response.status_code == 200:
                process_data(response.content, intervention_area, social_response)
    print()

filter_locality = 'Oeiras'
for vt, intervention_area in intervention_areas.items():
    for tp, social_answer in social_answers[vt].items():
        url = f"{base_url}?vt={vt}&tp={tp}&l=11-00-00"
        driver.get(url)
        print(f'[+] {intervention_area}, {tp}: {social_answer}')

        locality_filter_id = "_SocialLetterPortlet_WAR_cartasocialportlet_:sidebarForm:comboCity_input"
        locality_filter_element = driver.find_element(By.ID, locality_filter_id)

        locality_filter_element.clear()
        locality_filter_element.send_keys(filter_locality)

        autocomplete_selector = ".ui-autocomplete-item.ui-autocomplete-list-item.ui-state-highlight"
        highlighted_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, autocomplete_selector))
        )
        highlighted_element.click()

        time.sleep(0.2)

        page_number = 1
        print(f'processing page {page_number}')
        process_links(driver.page_source, intervention_area, social_answer)

        # Check if pagination controls are present
        pagination_controls = driver.find_elements(By.CSS_SELECTOR, "span.ui-paginator-next.ui-state-default.ui-corner-all")
        if pagination_controls:
            print('pagination controls present')
            # Pagination controls are present, handle paginated results
            prev_page = get_table(driver.page_source)
            while True:
                try:
                    page_number += 1
                    print(f'processing page {page_number}')

                    css_selector = "span.ui-paginator-next.ui-state-default.ui-corner-all:not(.ui-state-disabled)"
                    next_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
                    )
                    next_button.click()

                    css_selector = "span.ui-paginator-prev.ui-state-default.ui-corner-all"
                    next_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
                    )

                    while get_table(driver.page_source) == prev_page:
                        time.sleep(0.05)

                    prev_page = get_table(driver.page_source)

                    #print(driver.page_source)
                    #sec = input('asd')
                    process_links(driver.page_source, intervention_area, social_answer)
                except TimeoutException:
                    process_links(driver.page_source, intervention_area, social_answer)
                    print(f"- Processed page {page_number}")
                    print("Timed out waiting for the next button to be clickable or new content to load.")
                    break
                except (ElementClickInterceptedException, ElementNotInteractableException):
                    process_links(driver.page_source, intervention_area, social_answer)
                    print("The 'next' button is not interactable. Waiting and trying again.")
        else:
            print("No pagination controls found.")

df = pd.DataFrame(excel_data)
writer = pd.ExcelWriter('SocialServices.xlsx', engine='openpyxl')

# Write the DataFrame to an Excel file
df.to_excel(writer, index=False)

# Save the Excel file
writer.close()
