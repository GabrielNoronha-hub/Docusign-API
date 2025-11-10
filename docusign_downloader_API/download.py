import os
import json
import re
from docusign_esign import EnvelopesApi
from datetime import datetime, timedelta

HISTORY_FILE = "downloaded_envelopes.json"

def sanitize_filename(filename):
    """Remove caracteres inválidos para nomes de arquivo."""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def load_downloaded_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_downloaded_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(history), f)

def list_completed_envelopes(api_client, account_id, days_back=30):
    envelopes_api = EnvelopesApi(api_client)
    date_from = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + "Z"
    options = {"from_date": date_from, "status": "completed"}
    results = envelopes_api.list_status_changes(account_id, **options)
    return results.envelopes or []

def download_envelope_documents(api_client, account_id, envelope_id, output_folder_base):
    envelopes_api = EnvelopesApi(api_client)

    # Obter informações do envelope
    envelope_info = envelopes_api.get_envelope(account_id, envelope_id)
    sender_info = envelope_info.sender  # Campo correto para remetente
    envelope_name = envelope_info.email_subject
    usuario = f"{sender_info.user_name} (userId {sender_info.user_id}, email {sender_info.email})"

    # Sanitizar nome do usuário
    safe_user_name = sanitize_filename(sender_info.user_name)
    safe_envelope_name = sanitize_filename(envelope_name)

    # Criar pasta com nome do remetente dentro da pasta base
    output_folder = os.path.join(output_folder_base, safe_user_name)
    os.makedirs(output_folder, exist_ok=True)

    # Baixar PDF combinado
    pdf_bytes = envelopes_api.get_document(account_id, "combined", envelope_id)

    # Nome do arquivo: remetente + envelope ID
    file_path = os.path.join(output_folder, f"{safe_envelope_name}.pdf")
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"TESTE!!! {usuario} _ {envelope_name}")
    #print(f"Envelope {envelope_id} baixado — enviado por {usuario}")
    return file_path
