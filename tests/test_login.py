import time
import pytest
import subprocess
import pytest_html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


@pytest.fixture
def driver():
    # Configuracion del path del EdgeDriver
    edge_driver_path = r"C:\Users\UserGPC\Downloads\edgedriver_win64\msedgedriver.exe"

    # Configuracion de las opciones de Microsoft Edge
    options = EdgeOptions()
    options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"  # Path al ejecutable de Edge

    # Creacion de una instancia del navegador Microsoft Edge
    driver = webdriver.Edge(service=EdgeService(edge_driver_path), options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


# Funcion para guardar capturas de pantalla automáticamente
def take_screenshot(driver, name):
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    path = os.path.join(screenshots_dir, f"{name}.png")
    driver.save_screenshot(path)
    return path


# Agregar capturas al reporte HTML si una prueba falla
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Hook para capturar detalles de cada prueba
    outcome = yield
    report = outcome.get_result()

    # Solo actuar en pruebas fallidas
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")  # Obtener el driver de la prueba
        if driver:
            screenshot_path = take_screenshot(driver, item.name)
            if screenshot_path:
                # Adjuntar la captura de pantalla al reporte
                report.extra = getattr(report, "extra", [])
                report.extra.append(pytest_html.extras.image(screenshot_path))


# Historia de Usuario 1: Verificar que el logo de Wikipedia está visible en la página principal
def test_logo_visibility(driver):
    driver.get("https://www.wikipedia.org/")
    time.sleep(5)

    logo = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "img.central-featured-logo"))
    )
    assert logo.is_displayed(), "El logo de Wikipedia no está visible."
    take_screenshot(driver, "logo_visibility")


# Historia de Usuario 2: Verificar que la barra de búsqueda funciona correctamente
def test_search_function(driver):
    driver.get("https://www.wikipedia.org/")
    time.sleep(5)

    search_field = driver.find_element(By.CSS_SELECTOR, "input#searchInput")
    search_field.send_keys("Selenium WebDriver")
    search_field.submit()

    search_results = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.searchresults"))
    )
    assert search_results.is_displayed(), "No se encontraron resultados para 'Selenium WebDriver'."
    take_screenshot(driver, "search_results")


# Historia de Usuario 3: Verificar que el enlace "Acerca de Wikipedia" redirige correctamente
def test_about_link(driver):
    driver.get("https://es.wikipedia.org/wiki/Wikipedia:Portada")
    time.sleep(5)

    about_link = driver.find_element(By.LINK_TEXT, "Acerca de Wikipedia")
    about_link.click()

    about_page = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1#firstHeading"))
    )
    assert about_page.is_displayed(), "La página 'Acerca de Wikipedia' no se cargó correctamente."
    take_screenshot(driver, "about_page")


# Historia de Usuario 4: Verificar búsqueda de término inexistente
def test_search_nonexistent_term(driver):
    driver.get("https://es.wikipedia.org/wiki/Wikipedia:Portada")
    time.sleep(5)

    search_field = driver.find_element(By.CSS_SELECTOR, "input#searchInput")
    search_field.send_keys("jkjskfjskajd")
    search_field.submit()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.searchresults"))
    )
    page_content = driver.page_source
    assert "Resultados de la búsqueda" in page_content, "El texto 'Resultados de la búsqueda' no aparece."
    take_screenshot(driver, "no_results_search")


# Historia de Usuario 5: Comprobar texto "La enciclopedia libre"
def test_wikipedia_text(driver):
    driver.get("https://www.wikipedia.org/")
    time.sleep(5)

    page_content = driver.page_source
    assert "La enciclopedia libre" in page_content, "El texto 'La enciclopedia libre' no está presente."
    take_screenshot(driver, "wikipedia_text_check")


# Función para ejecutar pytest y generar el reporte en HTML
def run_pytest_report():
    subprocess.run(["pytest", "--maxfail=3", "--disable-warnings", "--html=report/test_report.html", "--self-contained-html", "--tb=short"])


if __name__ == "__main__":
    run_pytest_report()
