from typing import Literal
Intent = Literal["upload_file","ask_question","unknown"]

def route(text: str) -> Intent:
    t = (text or "").strip().lower()
    if any(k in t for k in ["upload","import","fichier","file"]):
        return "upload_file"
    if t:
        return "ask_question"
    return "unknown"
