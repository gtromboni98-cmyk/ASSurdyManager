import pandas as pd
import json
import pywhatkit as kit
from pathlib import Path
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class PaymentManager:
    def __init__(self, excel_path: str, json_path: str, email_settings: dict = None):
        self.excel_path = Path(excel_path)
        self.json_path = Path(json_path)
        self.email_settings = email_settings or {}
        
    def load_data(self):
        """Carica i dati da Excel e JSON"""
        try:
            self.df = pd.read_excel(self.excel_path)
            with open(self.json_path) as f:
                self.json_data = json.load(f)
            print("✓ Dati caricati con successo")
        except Exception as e:
            print(f"Errore nel caricamento dei dati: {str(e)}")
            raise
    
    def update_excel(self, match_column: str = 'Nome'):
        """Aggiorna Excel basandosi sui dati JSON"""
        updates = 0
        for item in self.json_data:
            # Trova la riga corrispondente in Excel
            mask = self.df[match_column] == item['nome']
            
            if mask.any():
                # Aggiorna i valori nelle colonne specificate
                for key, value in item.items():
                    if key in self.df.columns:
                        self.df.loc[mask, key] = value
                        updates += 1
        
        print(f"✓ Aggiornate {updates} celle nel file Excel")
    
    def send_whatsapp_alert(self, phone: str, message: str):
        """Invia un messaggio WhatsApp"""
        try:
            now = datetime.now()
            # Invia il messaggio 2 minuti dopo
            kit.sendwhatmsg(phone, message, 
                           now.hour, 
                           now.minute + 2)
            time.sleep(20)
            return True
        except Exception as e:
            print(f"Errore nell'invio del messaggio: {str(e)}")
            return False
    
    def get_smtp_settings(self, email: str) -> tuple:
        """Determina le impostazioni SMTP basandosi sull'indirizzo email"""
        email_lower = email.lower()
        
        # Dizionario dei provider più comuni
        smtp_settings = {
            'gmail.com': ('smtp.gmail.com', 587),
            'outlook.com': ('smtp-mail.outlook.com', 587),
            'hotmail.com': ('smtp-mail.outlook.com', 587),
            'live.com': ('smtp-mail.outlook.com', 587),
            'yahoo.com': ('smtp.mail.yahoo.com', 587),
            'libero.it': ('smtp.libero.it', 587),
            'virgilio.it': ('out.virgilio.it', 587),
            'tim.it': ('smtp.tim.it', 587)
        }
        
        # Trova il dominio dell'email
        domain = email_lower.split('@')[-1]
        
        # Restituisci le impostazioni SMTP appropriate
        return smtp_settings.get(domain, ('smtp.gmail.com', 587))

    def send_email_alert(self, to_email: str, subject: str, message: str) -> bool:
        """Invia un alert via email"""
        if not self.email_settings:
            print("⚠️ Configurazione email mancante")
            return False

        try:
            # Crea il messaggio
            msg = MIMEMultipart()
            from_email = self.email_settings.get('from_email')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Aggiungi il corpo del messaggio
            msg.attach(MIMEText(message, 'plain'))

            # Ottieni le impostazioni SMTP appropriate
            smtp_server, smtp_port = self.get_smtp_settings(from_email)
            
            # Crea la connessione SMTP
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(
                    self.email_settings.get('from_email'),
                    self.email_settings.get('password')
                )
                server.send_message(msg)
                print(f"✓ Email inviata con successo a {to_email}")
            return True

        except Exception as e:
            print(f"Errore nell'invio dell'email: {str(e)}")
            return False

    def check_and_send_alerts(self):
        """Controlla i pagamenti e invia alert se necessario"""
        whatsapp_sent = 0
        email_sent = 0
        
        for item in self.json_data:
            if not item.get('pagato', True):
                message = (f"Gentile {item['nome']}, "
                         f"le ricordiamo il pagamento in scadenza "
                         f"di {item['importo']} euro "
                         f"previsto per il {item.get('scadenza', 'quanto prima')}.")
                
                # Invia WhatsApp se disponibile
                if 'telefono' in item:
                    if self.send_whatsapp_alert(item['telefono'], message):
                        whatsapp_sent += 1
                
                # Invia Email se disponibile
                if 'email' in item:
                    if self.send_email_alert(
                        item['email'],
                        "Promemoria Pagamento",
                        message
                    ):
                        email_sent += 1
        
        print(f"✓ Inviati {whatsapp_sent} messaggi WhatsApp e {email_sent} email")
    
    def save_excel(self):
        """Salva le modifiche nel file Excel"""
        try:
            self.df.to_excel(self.excel_path, index=False)
            print("✓ File Excel salvato con successo")
        except Exception as e:
            print(f"Errore nel salvataggio del file Excel: {str(e)}")
            raise

def main():
    # Configurazione email
    email_settings = {
        'from_email': 'tuo.email@gmail.com',  # Il tuo indirizzo Gmail
        'password': 'la_tua_password_app',     # Password per le app di Google
    }

    # Inizializza il manager
    manager = PaymentManager(
        excel_path="data/pagamenti.xlsx",
        json_path="data/updates.json",
        email_settings=email_settings
    )
    
    try:
        # Carica i dati
        manager.load_data()
        
        # Aggiorna Excel
        manager.update_excel(match_column="Nome")
        
        # Controlla e invia alert WhatsApp
        manager.check_and_send_alerts()
        
        # Salva le modifiche
        manager.save_excel()
        
        print("\n✓ Processo completato con successo!")
        
    except Exception as e:
        print(f"\n❌ Errore durante l'esecuzione: {str(e)}")

if __name__ == "__main__":
    main()
