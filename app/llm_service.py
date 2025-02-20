import os
import sys
import logging
import traceback
from langchain_anthropic import ChatAnthropic

class LLMService:
    def __init__(self):
        """
        Initialize the Language Model Service
        Uses environment variables for API key and configuration
        """
        # Log könyvtár és fájl útvonalának meghatározása
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
        log_file = os.path.join(log_dir, 'llm_service.log')
        
        # Log könyvtár létrehozása, ha nem létezik
        os.makedirs(log_dir, exist_ok=True)
        
        # Logger létrehozása a basicConfig előtt
        self.logger = logging.getLogger(__name__)
        
        # Naplózás konfigurálása
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=log_file,
            filemode='a'
        )
        
        # Konzol kimenet hozzáadása
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
        
        # API kulcs ellenőrzése
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                self.logger.error("Hiányzó Anthropic API kulcs. Állítsa be az ANTHROPIC_API_KEY környezeti változót.")
                raise ValueError("Anthropic API kulcs szükséges")
        except Exception as e:
            self.logger.error(f"API kulcs ellenőrzési hiba: {e}")
            self.logger.error(traceback.format_exc())
            raise
        
        # Claude modell inicializálása
        try:
            self.model = ChatAnthropic(
                model_name="claude-3-haiku-20240307",
                anthropic_api_key=api_key,
                temperature=0.2  # Alacsony hőmérséklet a több determinisztikus válaszért
            )
            self.logger.info("Claude Haiku modell sikeresen inicializálva")
        except Exception as e:
            self.logger.error(f"LLM inicializálási hiba: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def generate_response(self, query, context_docs):
        """
        Válasz generálása RAG megközelítéssel
        
        :param query: Felhasználói kérdés
        :param context_docs: Visszakeresett kontextuális dokumentumok
        :return: Generált válasz a modelltől
        """
        try:
            # Kontextus előkészítése - ellenőrizzük, hogy van-e visszakeresett dokumentum
            if not context_docs or len(context_docs) == 0:
                context = "Nem találtunk releváns dokumentumot a kérdéshez. Próbáld meg más megfogalmazással."
                self.logger.warning("Üres kontextus dokumentumok")
            else:
                context = "\n\n".join([
                    f"--- Dokumentum {i+1} ---\n{doc.page_content}" 
                    for i, doc in enumerate(context_docs)
                ])
                self.logger.info(f"{len(context_docs)} dokumentum használata kontextusként")
            
            # Prompt összeállítása kontextussal
            prompt = f"""Te egy segítőkész AI asszisztens vagy, aki egy Java projekt fejlesztésén dolgozik.
Célod pontos, kontextusfüggő válaszokat adni a beolvasott dokumentumok alapján.

Visszakeresett Kontextus:
{context}

Felhasználói Kérdés: {query}

Kérlek, adj részletes, segítőkész választ, amely közvetlenül foglalkozik a kérdéssel a rendelkezésre álló kontextus alapján.
A válaszod legyen jól strukturált és könnyen érthető. Ha kódot írsz, használj markdown formázást a jobb olvashatóságért.
"""
            
            # Válasz generálása
            try:
                self.logger.info(f"Válasz generálása a következő kérdésre: '{query}'")
                response = self.model.invoke(prompt)
                
                # Ellenőrizzük, hogy van-e tartalom a válaszban
                if not hasattr(response, 'content') or not response.content:
                    self.logger.error("Üres válasz érkezett a modelltől")
                    return "Sajnos nem sikerült választ generálni a kérdésedre. Kérlek, próbáld meg később vagy fogalmazd át a kérdést."
                
                self.logger.info("Válasz sikeresen generálva")
                return response.content
            
            except Exception as e:
                self.logger.error(f"Válasz generálási hiba a modell meghívásakor: {e}")
                self.logger.error(traceback.format_exc())
                return f"Hiba történt a válasz generálása közben: {str(e)}"
        
        except Exception as e:
            self.logger.error(f"Válasz generálási folyamat hibája: {e}")
            self.logger.error(traceback.format_exc())
            return "Sajnos technikai hiba történt a válasz generálása közben. Kérlek, próbáld meg később."