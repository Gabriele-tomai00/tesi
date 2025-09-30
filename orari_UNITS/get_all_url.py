import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

# Imposta Chrome headless
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")


############### Funzioni get e set ####################
from urllib.parse import urlencode, quote

def build_orario_url(anno_scolastico, scuola, corso, anno2, date, lang="it"):
    base_url = "https://orari.units.it/agendaweb/index.php"

    params = {
        "view": "easycourse",
        "form-type": "corso",
        "include": "corso",
        "txtcurr": "",
        "anno": anno_scolastico,
        "scuola": scuola,
        "corso": corso,
        "anno2[]": anno2,  # verrà encodato
        "visualizzazione_orario": "cal",
        "date": date,
        "periodo_didattico": "",
        "_lang": lang,
        "list": "",
        "week_grid_type": "-1",
        "ar_codes_": "",
        "ar_select_": "",
        "col_cells": "0",
        "empty_box": "0",
        "only_grid": "0",
        "highlighted_date": "0",
        "all_events": "0",
        "faculty_group": "0",
    }

    return f"{base_url}?{urlencode(params, quote_via=quote)}"


def get_anni_scolastici():
    select_anno_scolastico = driver.find_element(By.ID, "cdl_aa")
    anni = [
        {"value": opt.get_attribute("value"), "label": opt.text}
        for opt in select_anno_scolastico.find_elements(By.TAG_NAME, "option")
        if opt.get_attribute("value")
    ]
    time.sleep(0.2)
    return anni


def set_anno_scolastico(anno):
    select_anno_scolastico = driver.find_element(By.ID, "cdl_aa")
    Select(select_anno_scolastico).select_by_value(anno["value"])
    time.sleep(0.2)


def get_dipartimenti():
    select_dipartimento = driver.find_element(By.ID, "cdl_scuola")
    dipartimenti = [
        {"value": opt.get_attribute("value"), "label": opt.text}
        for opt in select_dipartimento.find_elements(By.TAG_NAME, "option")
        if opt.get_attribute("value")
    ]
    time.sleep(0.2)
    return dipartimenti

def set_dipartimento(dipartimnento):
    select_dipartimento = driver.find_element(By.ID, "cdl_scuola")
    Select(select_dipartimento).select_by_value(dipartimnento["value"])
    scuola = dipartimnento["value"]
    time.sleep(0.2)  

def get_corsi_di_studio():
    select_corso = driver.find_element(By.ID, "cdl_co")
    corsi = [
        {"value": opt.get_attribute("value"), "label": opt.text}
        for opt in select_corso.find_elements(By.TAG_NAME, "option")
        if opt.get_attribute("value")
    ]
    return corsi


def set_corso_di_studio(corso):
    select_corso = driver.find_element(By.ID, "cdl_co")
    Select(select_corso).select_by_value(corso["value"])
    corso = corso["value"]
    time.sleep(0.2)

def get_anni_di_studio_e_curriculum():
    select_Anno_di_studio_e_curriculum = driver.find_element(By.ID, "cdl_a2_multi")
    anni = [
        {"value": opt.get_attribute("value"), "label": opt.text}
        for opt in select_Anno_di_studio_e_curriculum.find_elements(By.TAG_NAME, "option")
        if opt.get_attribute("value")
    ]
    time.sleep(0.2)
    return anni


def set_anno_di_studio_e_curriculum(anno):
    select_Anno_di_studio_e_curriculum = driver.find_element(By.ID, "cdl_a2_multi")
    Select(select_Anno_di_studio_e_curriculum).select_by_value(anno["value"])
    anno2 = anno["value"]
    time.sleep(0.2)

############### Inizializzazione WebDriver ####################

driver = webdriver.Chrome(options=chrome_options)

URL_FORM = "https://orari.units.it/agendaweb/index.php?view=easycourse&_lang=it&include=corso"
driver.get(URL_FORM)
time.sleep(0.2)

anni_scolastici = get_anni_scolastici()
latest_value = max(anni_scolastici, key=lambda x: int(x['value']))
set_anno_scolastico(latest_value)

dipartimenti = get_dipartimenti()


############### PROGRAMMA PRINCIPALE ####################
file_path = "url_orariUNITS.txt"
try:
    os.remove(file_path)
except:
    pass

for dip in dipartimenti:
    set_dipartimento(dip)
    corsi_di_studio = get_corsi_di_studio()
    
    for corso in corsi_di_studio:
        set_corso_di_studio(corso)
        anni_di_studio_e_curriculum = get_anni_di_studio_e_curriculum()
        
        for anno_studio in anni_di_studio_e_curriculum:
            set_anno_di_studio_e_curriculum(anno_studio)  
            # url
            log = "\n" + dip["label"] + "  --  Corso: " + corso["label"] + "  --  Anno di studio e curriculum: " + anno_studio["label"] + "\n"
            print(log)
            url = build_orario_url("2025", dip["value"], corso["value"], anno_studio["value"], "29/09/2025", lang="it")
            print(url + "\n")
            with open(file_path, 'a') as f:
                f.write(log)
                f.write(url + "\n")

            
driver.quit()




