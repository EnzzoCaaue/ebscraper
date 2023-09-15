from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
import hashlib
import time
import telebot

# URL do site que você deseja monitorar
url = "https://2rm.eb.mil.br/servicomilitar/stt"

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
        print("Timeout ao carregar a página.")
    except Exception as e:
        print("Erro ao obter o conteúdo da página:", str(e))
    return None


# Função para verificar a alteração no site
def check_site_change(url, bot):
    previous_hash = None
    while True:
        site_content = get_site_content(url)
        if site_content:
            current_hash = hashlib.sha256(site_content.encode()).hexdigest()
            if previous_hash != current_hash:
                print("O conteúdo da página foi alterado:")
                print(site_content)
                bot.send_message(chat_id='CHAT_ID', text="O conteúdo da página foi alterado:\n" + site_content)
                previous_hash = current_hash
            else:
                print("O conteúdo da página não foi alterado.")
        time.sleep(120)  # Verificar a cada 2 minutos


# Configurar o token do bot do Telegram
bot_token = 'BOT_TOKEN'


# Inicializar o bot do Telegram
bot = telebot.TeleBot(bot_token)


if __name__ == "__main__":
    check_site_change(url, bot)

# Fechar o driver do Chrome quando terminar
driver.quit()
