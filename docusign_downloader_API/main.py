from config import get_api_client
from download import list_completed_envelopes, download_envelope_documents, load_downloaded_history, save_downloaded_history
import os
import time

def main():
    output_folder = "C:\\Users\\"
    api_client = get_api_client()
    account_id = os.getenv("ACCOUNT_ID")
    print("\n" + "Buscando envelopes concluídos...")
    envelopes = list_completed_envelopes(api_client, account_id)
    print(f"Foram encontrados {len(envelopes)} envelopes concluídos..." + "\n")

    downloaded_history = load_downloaded_history()
    envelopes = list_completed_envelopes(api_client, account_id)

    for env in envelopes:
        if env.envelope_id not in downloaded_history:
            print(f"📥 Baixando envelope {env.envelope_id}...")
            file_path = download_envelope_documents(api_client, account_id, env.envelope_id, output_folder)
            print(f"✅ Salvo em {file_path}")
            downloaded_history.add(env.envelope_id)
        else:
            print(f"⏩ Envelope {env.envelope_id} já foi baixado. Pulando...")

    save_downloaded_history(downloaded_history)

if __name__ == "__main__":
    execucao = True
    while execucao == True:
        main()
        time.sleep(900)