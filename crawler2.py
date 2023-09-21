import hashlib
import logging
import time

import requests
import telebot
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Lista de URLs a serem monitoradas
URLS = [
    "https://2rm.eb.mil.br/servicomilitar/stt",
    "https://2rm.eb.mil.br/servicomilitar/ott-oficial-tecnico-temporario",
]

BOT_TOKEN = '6188235798:AAFokxFLAySkUhHWv2_uPFM-XUPWVQkfSVc'
DISCORD_WEBHOOK_URL = ('https://discord.com/api/webhooks/1153918778871136297'
                       '/Q0miI6YqKVCvqUY2lzQBX0SYRhQtWXOX6xATW9ahP2NNaHdT61eb76IjoBe1QjdqCZPq')

# Configurar o driver do Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executar o navegador em segundo plano (sem interface gráfica)
driver = webdriver.Chrome(options=chrome_options)


# Função para obter o conteúdo da página
def get_site_content(url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(ec.presence_of_element_located(
            (By.XPATH, "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/h2[1]")))
        h2_element = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/h2[1]")
        return h2_element.text.strip()
    except TimeoutException:
        logging.error(f"Timeout ao carregar a página: {url}")
    except Exception as e:
        logging.error(f"Erro ao obter o conteúdo da página {url}: {str(e)}")
    return None


# Função para enviar mensagem para o webhook do Discord
def send_discord_notification(message):
    try:
        payload = {'content': message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            logging.info("Notificação enviada com sucesso para o Discord.")
        elif response.status_code == 204:
            pass  # Não faça nada se o código de status for 204 (No Content)
        else:
            logging.error(f"Falha ao enviar notificação para o Discord. Código de status: {response.status_code}")
    except Exception as e:
        logging.error(f"Erro ao enviar notificação para o Discord: {str(e)}")


# Função para verificar a alteração no site
def check_site_changes(urls, bot):
    previous_hashes = {url: None for url in urls}
    while True:
        for url in urls:
            site_content = get_site_content(url)
            if site_content:
                current_hash = hashlib.sha256(site_content.encode()).hexdigest()
                if previous_hashes[url] != current_hash:
                    logging.info(f"O conteúdo da página {url} foi alterado:")
                    logging.info(site_content)
                    bot.send_message(chat_id='1151298988',
                                     text=f"O conteúdo da página {url} foi alterado:\n{site_content}")
                    time.sleep(2)
                    send_discord_notification(f"O conteúdo da página {url} foi alterado:\n{site_content}")
                    time.sleep(2)
                    previous_hashes[url] = current_hash
                else:
                    logging.info(f"O conteúdo da página {url} não foi alterado.")
        time.sleep(300)  # Verificar a cada 5 minutos


# Inicializar o bot do Telegram
bot = telebot.TeleBot(BOT_TOKEN)

if __name__ == "__main__":
    try:
        check_site_changes(URLS, bot)
    except KeyboardInterrupt:
        logging.info("Monitoramento interrompido pelo usuário.")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {str(e)}")
    finally:
        # Fechar o driver do Chrome quando terminar
        driver.quit()
