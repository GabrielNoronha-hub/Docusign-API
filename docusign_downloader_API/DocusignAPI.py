import win32serviceutil
import win32service
import win32event
import servicemanager
import os
import time
from config import get_api_client
from download import list_completed_envelopes, download_envelope_documents

class DocusignAPI(win32serviceutil.ServiceFramework):
    _svc_name_ = "DocuSignAPIService"          # Nome interno
    _svc_display_name_ = "DocuSign API Service" # Nome visível
    _svc_description_ = "Baixa automaticamente envelopes concluídos do DocuSign a cada 15 minutos."

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("Serviço DocuSign iniciado.")
        while self.running:
            try:
                self.baixar_envelopes()
            except Exception as e:
                servicemanager.LogErrorMsg(f"Erro no serviço: {e}")
            time.sleep(900)  # 15 minutos

    def baixar_envelopes(self):
        output_folder = "C:/Users/"
        os.makedirs(output_folder, exist_ok=True)

        api_client = get_api_client()
        account_id = os.getenv("ACCOUNT_ID")

        servicemanager.LogInfoMsg("Buscando envelopes concluídos...")
        envelopes = list_completed_envelopes(api_client, account_id)

        if not envelopes:
            servicemanager.LogInfoMsg("Nenhum envelope concluído encontrado.")
            return

        servicemanager.LogInfoMsg(f"Encontrados {len(envelopes)} envelopes.")
        for env in envelopes:
            subject = getattr(env, "email_subject", "Sem assunto")
            servicemanager.LogInfoMsg(f"Baixando: {env.envelope_id} - {subject}")
            path = download_envelope_documents(api_client, account_id, env.envelope_id, output_folder)
            servicemanager.LogInfoMsg(f"Salvo em: {path}")
