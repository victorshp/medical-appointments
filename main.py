from playwright.sync_api import Playwright, sync_playwright
import time
from datetime import datetime

# Hospitals
# >> Sta. Catarina
# >> Rede D'Or

# TODO Sta. Catarina steps
# 1. GET https://redesantacatarina.org.br/hospital/santacatarina-paulista/Paciente/agendamento-consultas-exames
# 2. Click on agendamento de consultas and start process
def is_date_until_last_day_of_next_month(days_list):
    for (day_to_check, month_to_check) in days_list: 
        month_mapping = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
        today = datetime.now()
        current_month = today.month

        month_to_check_num = month_mapping.get(month_to_check)
        if month_to_check and current_month + 1 < month_to_check_num:
            return 'stop'
        elif 20 <= day_to_check <= 31 and today.strftime('%b') == month_to_check:
            return True
    return False

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.rededorsaoluiz.com.br/paciente/marcar-consulta")
    page.get_by_role("button", name="ENTRE").click()

    page.wait_for_load_state('networkidle')
    print('Starting to log in...')
    time.sleep(2)
    page.get_by_placeholder("E-mail ou cpf").fill("")
    page.get_by_placeholder("E-mail ou cpf").press("Tab")
    page.get_by_placeholder("Senha").fill("")
    page.get_by_role("button", name="Entre", exact=True).click()

    page.wait_for_load_state('networkidle')
    print('Choosing user...')
    time.sleep(1)
    page.get_by_role("img", name="").click()

    page.wait_for_load_state('networkidle')
    print('Choosing doctor...')
    time.sleep(1)
    page.get_by_placeholder("DIGITE A ESPECIALIDADE OU MÉ").click()
    page.get_by_label("Digite a especialidade ou mé").fill("")
    page.get_by_role("listbox").locator("#list-item-1").get_by_text("").click()
    page.locator("#select-forma-de-pagamento svg").click()

    page.wait_for_load_state('networkidle')
    print('Choosing health plan stuff...')
    time.sleep(1)
    page.get_by_text("PLANO DE SAÚDE", exact=True).click()
    page.get_by_placeholder("DIGITE O NOME DO CONVÊNIO", exact=True).fill("")
    page.get_by_role("option").get_by_text("").click()
    page.get_by_placeholder("DIGITE O NOME DO PLANO", exact=True).click()
    page.get_by_placeholder("DIGITE O NOME DO PLANO", exact=True).fill("")
    page.get_by_text("").first.click()
    page.get_by_role("button", name="PROSSEGUIR").click()

    page.wait_for_load_state('networkidle')
    print('Choosing hospitals...')
    time.sleep(2)
    page.get_by_role("button", name="Selecionar todos").click()
    page.get_by_role("heading", name="Hospital Villa Lobos").click()
    page.get_by_role("button", name="Prosseguir").click()

    try:
        page.wait_for_load_state('networkidle')
        time.sleep(5)
        page.wait_for_selector('.dayOptionWrapper', timeout=120000)
        print("Days are available. Starting the verification process...")

        # Get the 3 days on the screen currently
        scheduled_days_on_display = page.query_selector_all('.dayOptionWrapper')
        print('this is scheduled_days_on_display')
        print(scheduled_days_on_display)

        result_list = [
            [
                int(div.get_property('innerText').json_value().split('\n')[1]),
                div.get_property('innerText').json_value().split('\n')[2].lower()
            ]
            for div in scheduled_days_on_display
        ]

        print('this is result_list')
        print(result_list)

        valid_date_found = False 
        while not valid_date_found:
            time.sleep(2)
            valid_date_found = is_date_until_last_day_of_next_month(result_list)
            if valid_date_found == 'stop':
                print("Nothing found... Exiting")
                context.close()
                browser.close()
            elif not valid_date_found:
                print("Condition not satisfied. Pressing the button...")

        print('Got something! Lets see...')

    except Exception as e:
        print(f"Error: {e}")
    finally:
        browser.close()
    # context.close()
    # browser.close()

with sync_playwright() as playwright:
    run(playwright)
