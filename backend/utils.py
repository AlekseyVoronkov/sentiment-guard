import time
from datetime import datetime

MONTHS = {
    "января": "01", "февраля": "02", "марта": "03", "апреля": "04",
    "мая": "05", "июня": "06", "июля": "07", "августа": "08",
    "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"
}

def convert_date(date_str: str) -> str:
    try:
        clean_str = date_str.split(',')[0].strip().lower()
        
        if "сегодня" in clean_str: return datetime.now().strftime("%Y-%m-%d")
        if "вчера" in clean_str: return datetime.now().strftime("%Y-%m-%d")
            
        parts = clean_str.split()
        if len(parts) >= 2:
            day = parts[0].zfill(2)
            month = MONTHS.get(parts[1], "01")
            year = parts[2] if len(parts) > 2 else str(datetime.now().year)
            return f"{year}-{month}-{day}"
    except:
        pass
    return datetime.now().isoformat()
