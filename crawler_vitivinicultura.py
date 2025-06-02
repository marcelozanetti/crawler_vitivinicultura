from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium_config import get_chrome_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import logger
import time

def crawler_lista_producaoEComercializacao(url):
    listaProdutos = []
    for exercicio in range(2022, 2024):
        try:
            driver = get_chrome_driver()
            driver.get(url)

            # Aguarda o input do ano estar pronto e preenche
            input_ano = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.text_pesq'))
            )
            input_ano.clear()
            input_ano.send_keys(str(exercicio))

            # Aguarda o botão de submit e clica
            botao_ok = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.subm_pesq'))
            )
            botao_ok.click()

            # Aguarda a tabela carregar
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.tb_base.tb_dados tbody tr'))
            )
            time.sleep(0.5)  # Pequeno delay extra para garantir o carregamento total

            linhas = driver.find_elements(By.CSS_SELECTOR, 'table.tb_base.tb_dados tbody tr')
            registro = None
            subitens = []

            for tr in linhas:
                try:
                    td_items = tr.find_elements(By.CSS_SELECTOR, 'td.tb_item')
                    td_subitems = tr.find_elements(By.CSS_SELECTOR, 'td.tb_subitem')
                    if td_items and len(td_items) >= 2:
                        # Salva o registro anterior, se houver
                        if registro:
                            registro["Subitens"] = subitens
                            listaProdutos.append(registro)
                            subitens = []
                        # Nova linha: [exercicio, produto, quantidade]
                        registro = {
                            "Exercicio": exercicio,
                            "Grupo": td_items[0].text.strip(),
                            "Quantidade": td_items[1].text.strip()
                        }
                    elif td_subitems and len(td_subitems) >= 2:
                        subitens.append({
                            "Subgrupo": td_subitems[0].text.strip(),
                            "Quantidade": td_subitems[1].text.strip()
                        })
                except StaleElementReferenceException:
                    logger.warning("Elemento ficou obsoleto, ignorando linha.")
                    continue
            # Salva o último registro do ano                
            if registro:
                registro["Subitens"] = subitens
                listaProdutos.append(registro)
        except (NoSuchElementException, TimeoutException):
            logger.warning(f"Erro ao processar o ano {exercicio}")
        finally:
            driver.quit()
    return listaProdutos


def crawler_lista_processamento():
    url = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_03"
    listaProdutos = []
    driver = get_chrome_driver()
    try:
        driver.get(url)
        # 1 - Listar todos os botões de grupo
        botoes_grupo_textos = [b.text.strip() for b in driver.find_elements(By.CSS_SELECTOR, 'button.btn_sopt')]
        for idx, grupo_nome in enumerate(botoes_grupo_textos):
            # Recarregar a página e reler os botões (evita StaleElementReference)
            driver.get(url)
            botoes_grupo = WebDriverWait(driver, 10).until(
               EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button.btn_sopt'))
            )
            grupo_registro = {
                "GrupoDescricao": grupo_nome,
                "Produtos": []
            }
            for exercicio in range(2022, 2024):
                try:
                    # Clique no botão do grupo a cada exercício!
                    botoes_grupo = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button.btn_sopt'))
                    )
                    botao = botoes_grupo[idx]
                    botao.click()

                    logger.warning("raspando exercicio: %s, grupo: %s", exercicio, grupo_nome)
                    # Preencher o ano
                    input_ano = driver.find_element(By.CSS_SELECTOR, 'input.text_pesq')
                    input_ano = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.text_pesq'))
                    )
                    input_ano.clear()
                    input_ano.send_keys(str(exercicio))
                    # Clicar em "Ok"
                    driver.find_element(By.CSS_SELECTOR, 'input.subm_pesq').click()
                    # Esperar a tabela carregar
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'table.tb_base.tb_dados tbody tr'))
                    )
                    # Pequeno delay extra para garantir o carregamento total
                    time.sleep(1)  

                    linhas = driver.find_elements(By.CSS_SELECTOR, 'table.tb_base.tb_dados tbody tr')
                    registro = None
                    subitens = []
                    for tr in linhas:
                        try:
                            td_items = tr.find_elements(By.CSS_SELECTOR, 'td.tb_item')
                            td_subitems = tr.find_elements(By.CSS_SELECTOR, 'td.tb_subitem')
                            if td_items and len(td_items) >= 2:
                                # Salva o registro anterior, se houver
                                if registro:
                                    registro["Subitens"] = subitens
                                    grupo_registro["Produtos"].append(registro)
                                    subitens = []
                                # Nova linha: [exercicio, produto, quantidade]
                                registro = {
                                    "Exercicio": exercicio,
                                    "Grupo": td_items[0].text.strip(),
                                    "Quantidade": td_items[1].text.strip(),
                                    "Subitens": []
                                }
                                logger.warning("raspando grupo: %s",td_items[0].text.strip())
                            elif td_subitems and len(td_subitems) >= 2:
                                 # Verifica se os elementos realmente existem e têm texto
                                subgrupo = td_subitems[0].text.strip() if td_subitems[0] else ""
                                quantidade = td_subitems[1].text.strip() if td_subitems[1] else ""
                                if subgrupo or quantidade:
                                    subitens.append({
                                        "Subgrupo": subgrupo,
                                        "Quantidade": quantidade
                                    })
                                    logger.warning("raspando subgrupo: %s", subgrupo)
                        except StaleElementReferenceException:
                            logger.warning("Elemento ficou obsoleto, ignorando linha.")
                            continue
                    # Salva o último registro do ano                
                    if registro:
                        registro["Subitens"] = subitens
                        grupo_registro["Produtos"].append(registro)
                except (NoSuchElementException, TimeoutException):
                    logger.warning(f"Erro ao processar o ano {exercicio}")
                    continue
            listaProdutos.append(grupo_registro)
            # Após processar um grupo, recarregue a página para garantir que os botões estejam válidos
    finally:
        driver.quit()
    return listaProdutos

def crawler_lista_importexport(url):
    #url = "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06"
    listaPaises = []

    driver = get_chrome_driver()
    driver.get(url)

    for tipo_idx in range(len(driver.find_elements(By.CSS_SELECTOR, 'button.btn_sopt'))):
        exercicio = 2021

        while exercicio < 2023:
            exercicio += 1

            # Sempre recarregue a página ANTES de buscar elementos
            driver.get(url)

            tiposVinhos = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button.btn_sopt'))
            )

            # Clicar no botão do tipo de vinho
            botao = tiposVinhos[tipo_idx]
            botao_nome = botao.text.strip()
            botao.click()
            
            # Pequeno delay para garantir que o DOM estável após o clique
            time.sleep(0.5)

            logger.warning("raspando exercicio: %s, tipo de vinho: %s", exercicio, botao_nome)

            # Preencher o ano
            input_ano = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.text_pesq'))
            )
            input_ano.clear()
            input_ano.send_keys(str(exercicio))

            # Aguarde o botão "Ok" e clique
            botao_ok = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input.subm_pesq'))
            )
            botao_ok.click()

            # Esperar a tabela carregar
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.tb_base.tb_dados tbody tr'))
            )
            time.sleep(0.5)  # Pequeno delay extra para garantir o carregamento total
            
            linhas = driver.find_elements(By.CSS_SELECTOR, 'table.tb_base.tb_dados tbody tr')

            # Montar array de países
            paises = []
            for tr in linhas:
                try:
                    tds = tr.find_elements(By.TAG_NAME, 'td')
                    if len(tds) == 3:
                        pais = tds[0].text.strip()
                        quantidade = tds[1].text.strip()
                        valor = tds[2].text.strip()
                        paises.append({
                            "Pais": pais,
                            "Quantidade": quantidade,
                            "Valor U$": valor
                        })
                    logger.warning("raspando paises: %s",tds[0].text.strip())
                except StaleElementReferenceException:
                    logger.warning("Linha obsoleta, ignorando.")
                continue

            registro = {
                "Exercicio": exercicio,
                "Tipo de vinho": botao_nome,
                "Paises": paises
            }
            
            listaPaises.append(registro)

    driver.quit()
    return listaPaises