import requests
from bs4 import BeautifulSoup
import csv
import time
from tqdm import tqdm

BASE_URL = "https://transparencia.gob.es/servicios-buscador/buscar.htm"
PARAMS = {
    "categoria": "retribuciones",
    "categoriasPadre": "altcar",
    "lang": "es",
    "pag": 1
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/128.0.0.0 Safari/537.36"
}

OUTPUT_FILE = "retribuciones_altos_cargos_todas.csv"

def parse_page(html):
    """Extrae las filas de la tabla de retribuciones."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    data = []

    if not table:
        return data

    for row in table.select("tbody tr"):
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) >= 5:
            data.append({
                "Alto Cargo": cols[0],
                "Organismo": cols[1],
                "Ministerio": cols[2],
                "Retribución": cols[3],
                "Año": cols[4]
            })
    return data


def scrape_all(delay=1):
    """Descarga todas las páginas hasta que no haya más resultados."""
    all_data = []
    page = 1

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = None

        for page in tqdm(range(1, 2000)):  # límite de seguridad
            PARAMS["pag"] = page
            resp = requests.get(BASE_URL, params=PARAMS, headers=HEADERS)

            if resp.status_code != 200:
                print(f"❌ Error {resp.status_code} en la página {page}")
                break

            page_data = parse_page(resp.text)
            if not page_data:
                print(f"🚫 Fin de los resultados en página {page}")
                break

            if writer is None:
                writer = csv.DictWriter(f, fieldnames=page_data[0].keys())
                writer.writeheader()

            writer.writerows(page_data)
            all_data.extend(page_data)

            time.sleep(delay)

    print(f"✅ {len(all_data)} registros guardados en '{OUTPUT_FILE}'")
    return all_data


if __name__ == "__main__":
    scrape_all(delay=1)
