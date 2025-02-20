import os
import sys
import time
import logging
import traceback
from dotenv import load_dotenv

# Az aktuális script könyvtárának meghatározása
current_dir = os.path.dirname(os.path.abspath(__file__))
# Projekt gyökérkönyvtár (egy szinttel feljebb az app könyvtártól)
project_root = os.path.dirname(current_dir)

# Az app könyvtár hozzáadása a Python útvonalhoz
sys.path.append(current_dir)

# Környezeti változók betöltése
load_dotenv()

# Log könyvtár és fájl útvonalának meghatározása
log_dir = os.path.join(project_root, 'logs')
log_file = os.path.join(log_dir, 'app.log')

# Log könyvtár létrehozása, ha nem létezik
os.makedirs(log_dir, exist_ok=True)

# Naplózás konfigurálása
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='a'
)
logger = logging.getLogger(__name__)

# Konzol kimenet hozzáadása
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Saját modulok importálása
from database import DocumentDatabase
from llm_service import LLMService
from flask import Flask, render_template, request, jsonify

class RAGAssistant:
    def __init__(self, auto_setup=False):
        """
        RAG Asszisztens inicializálása
        Beállítja a forrás és adatbázis könyvtárakat
        
        :param auto_setup: Automatikus adatbázis inicializálás
        """
        # Alapértelmezett könyvtárak
        self.data_dir = os.path.join(project_root, 'data')
        
        # Use /tmp directory with unique name for database
        unique_id = str(int(time.time()))
        self.db_dir = os.path.join('/tmp', f'chroma_db_{unique_id}')
        
        # Könyvtárak létrehozása, ha nem léteznek
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.db_dir, exist_ok=True)
        
        # Explicit permissions for tmp directory
        os.chmod(self.db_dir, 0o777)
        
        logger.info(f"Adatbázis létrehozva a következő helyen: {self.db_dir}")
        
        # Szolgáltatások inicializálása
        self.document_db = DocumentDatabase(self.data_dir, self.db_dir)
        self.llm_service = LLMService()
        
        # Opcionális adatbázis inicializálás
        if auto_setup:
            try:
                setup_result = self.document_db.check_and_update_if_needed()
                if setup_result:
                    logger.info("Adatbázis inicializálás vagy frissítés sikeres")
                else:
                    logger.warning("Adatbázis inicializálás vagy frissítés sikertelen")
            except Exception as e:
                logger.error(f"Adatbázis inicializálási hiba: {e}")
                logger.error(traceback.format_exc())
    
    def setup_assistant_database(self):
        """
        Asszisztens adatbázisának létrehozása
        
        :return: Művelet sikeressége
        """
        try:
            return self.document_db.setup_database()
        except Exception as e:
            logger.error(f"Asszisztens adatbázis létrehozási hiba: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def delete_assistant_database(self):
        """
        Asszisztens adatbázisának törlése
        
        :return: Művelet sikeressége
        """
        try:
            self.document_db.delete_database()
            return True
        except Exception as e:
            logger.error(f"Asszisztens adatbázis törlési hiba: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def update_assistant_database(self, new_source_dir=None):
        """
        Asszisztens adatbázisának frissítése
        
        :param new_source_dir: Opcionális új forrás könyvtár
        :return: Művelet sikeressége
        """
        try:
            return self.document_db.update_database(new_source_dir)
        except Exception as e:
            logger.error(f"Asszisztens adatbázis frissítési hiba: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def list_assistant_documents(self):
        """
        Asszisztens dokumentumainak listázása
        
        :return: Dokumentumok listája
        """
        try:
            return self.document_db.list_documents()
        except Exception as e:
            logger.error(f"Asszisztens dokumentumok listázási hiba: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def process_question(self, query):
        """
        Kérdés feldolgozása RAG módszerrel
        
        :param query: Felhasználói kérdés
        :return: Generált válasz
        """
        try:
            # Kontextus lekérése hasonlósági kereséssel
            context_docs = self.document_db.similarity_search(query)
            
            # Válasz generálása LLM segítségével
            response = self.llm_service.generate_response(query, context_docs)
            
            return response
        except Exception as e:
            logger.error(f"Kérdés feldolgozási hiba: {e}")
            logger.error(traceback.format_exc())
            raise

# Flask alkalmazás létrehozása
app = Flask(__name__, 
            template_folder=os.path.join(project_root, 'templates'),
            static_folder=os.path.join(project_root, 'static'))

# RAG asszisztens inicializálása auto_setup=True beállítással
rag_assistant = RAGAssistant(auto_setup=True)

@app.route('/')
def index():
    """
    Főoldal megjelenítése
    
    :return: index.html template
    """
    return render_template('index.html')

@app.route('/list-documents', methods=['GET'])
def list_documents():
    """
    Dokumentumok listázásának végpontja
    
    :return: JSON válasz a dokumentumok listájával
    """
    try:
        documents = rag_assistant.list_assistant_documents()
        return jsonify({
            "status": "success", 
            "documents": documents
        })
    except Exception as e:
        logger.error(f"Dokumentumok listázási hiba: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/setup-database', methods=['POST'])
def handle_setup_database_request():
    """
    Adatbázis létrehozásának végpontja
    
    :return: JSON válasz a művelet sikerességéről
    """
    try:
        success = rag_assistant.setup_assistant_database()
        return jsonify({
            "status": "success" if success else "error", 
            "message": "Adatbázis sikeresen létrehozva" if success else "Nem sikerült az adatbázis létrehozása"
        })
    except Exception as e:
        logger.error(f"Adatbázis létrehozási hiba: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/delete-database', methods=['POST'])
def handle_delete_database_request():
    """
    Adatbázis törlésének végpontja
    
    :return: JSON válasz a művelet sikerességéről
    """
    try:
        rag_assistant.delete_assistant_database()
        return jsonify({
            "status": "success", 
            "message": "Adatbázis sikeresen törölve"
        })
    except Exception as e:
        logger.error(f"Adatbázis törlési hiba: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/update-database', methods=['POST'])
def handle_update_database_request():
    """
    Adatbázis frissítésének végpontja
    
    :return: JSON válasz a művelet sikerességéről
    """
    try:
        data = request.get_json(silent=True)
        if data is None:
            data = {}  # Üres objektum, ha nincs kérés body
            
        new_source_dir = data.get('source_dir')
        success = rag_assistant.update_assistant_database(new_source_dir)
        return jsonify({
            "status": "success" if success else "error", 
            "message": "Adatbázis sikeresen frissítve" if success else "Nem sikerült az adatbázis frissítése"
        })
    except Exception as e:
        logger.error(f"Adatbázis frissítési hiba: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/ask', methods=['POST'])
def handle_question():
    """
    Kérdés feldolgozásának végpontja
    
    :return: JSON válasz a generált válasszal
    """
    try:
        data = request.get_json(silent=True)
        if data is None:
            logger.error("Érvénytelen JSON vagy üres kérés")
            return jsonify({
                "status": "error", 
                "message": "Érvénytelen JSON vagy üres kérés"
            }), 400
        
        question = data.get('question', '').strip()
        logger.info(f"Beérkező kérdés: '{question}'")
        
        # Üres kérdés ellenőrzése
        if not question:
            logger.warning("Üres kérdés beküldve")
            return jsonify({
                "status": "error", 
                "message": "A kérdés nem lehet üres"
            }), 400
        
        # Válasz generálása
        try:
            response = rag_assistant.process_question(question)
            logger.info(f"Válasz sikeresen legenerálva ({len(response)} karakter)")
            
            return jsonify({
                "status": "success", 
                "response": response
            })
        except Exception as e:
            logger.error(f"Kérdés feldolgozási hiba: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                "status": "error", 
                "message": f"Hiba a válasz generálása során: {str(e)}"
            }), 500
            
    except Exception as e:
        logger.error(f"Kérdés feldolgozási hiba: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)