# cleaner.py
# Normaliza los datos crudos extraídos de cada portal.
# Cada portal devuelve texto diferente: este módulo los unifica.

import re


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_salary(raw: str) -> dict:
    if not raw or raw.strip() == "":
        return {"min": None, "max": None, "currency": "PEN", "period": None}

    # Clean S/. or S/ prefix
    raw_clean = raw.replace("S/.", "S/").strip()

    # Find all numeric parts after S/
    # Matches numbers like 2.800,00 or 2,800.00 or 2800
    matches = re.findall(r"S/\s*([\d.,]+)", raw_clean)

    parsed_numbers = []
    for val in matches:
        # If there's a decimal part at the end (,00 or .00), let's strip it
        if val.endswith(",00") or val.endswith(".00"):
            val = val[:-3]
        # Remove any remaining thousands separators (, or .)
        val_clean = val.replace(".", "").replace(",", "")
        try:
            parsed_numbers.append(int(val_clean))
        except ValueError:
            pass

    if len(parsed_numbers) >= 2:
        return {
            "min": parsed_numbers[0],
            "max": parsed_numbers[1],
            "currency": "PEN",
            "period": detect_period(raw),
        }
    elif len(parsed_numbers) == 1:
        return {
            "min": parsed_numbers[0],
            "max": None,
            "currency": "PEN",
            "period": detect_period(raw),
        }

    return {"min": None, "max": None, "currency": "PEN", "period": None}


def detect_period(text: str) -> str:
    text = text.lower()
    if "hora" in text:
        return "hora"
    if "día" in text or "diario" in text:
        return "día"
    if "quince" in text or "quincenal" in text:
        return "quincenal"
    if "año" in text or "anual" in text:
        return "anual"
    return "mensual"


def normalize_modality(raw: str) -> str:
    if not raw:
        return "no especificado"
    raw = raw.lower()
    if ("remoto" in raw or "teletrabajo" in raw or "home" in raw) and ("presencial" in raw or "oficina" in raw):
        return "híbrido"
    if "remoto" in raw or "teletrabajo" in raw or "home" in raw:
        return "remoto"
    if "híbrido" in raw or "hibrido" in raw or "mixto" in raw:
        return "híbrido"
    if "presencial" in raw or "oficina" in raw:
        return "presencial"
    return "no especificado"


def normalize_experience(raw: str) -> int:
    if not raw:
        return 0
    match = re.search(r"(\d+)\s*(año|year)", raw.lower())
    if match:
        return int(match.group(1))
    return 0