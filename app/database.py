import os
import logging
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Optional

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document

class HuggingFaceEmbeddingsAdapter:
    """
    Adapter osztály a SentenceTransformer és LangChain kompatibilitás biztosításához
    """
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts):
        """
        Dokumentumok beágyazása vektorokká
        
        :param texts: Dokumentum szövegek listája
        :return: Beágyazott vektorok listája
        """
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts, convert_to_tensor=False).tolist()
    
    def embed_query(self, text):
        """
        Lekérdezés beágyazása vektorrá
        
        :param text: Lekérdezés szövege
        :return: Beágyazott vektor
        """
        return self.model.encode(text, convert_to_tensor=False).tolist()

class DocumentDatabase:
    def __init__(self, source_dir, db_dir):
        """
        Dokumentum adatbázis inicializálása
        
        :param source_dir: Forrás dokumentumok könyvtára
        :param db_dir: Adatbázis tárolási könyvtár
        """
        # Könyvtárak létrehozása szükség esetén sudo jogosultsággal
        os.makedirs(source_dir, exist_ok=True)
        self._ensure_directory_with_permissions(db_dir)
        os.makedirs('logs', exist_ok=True)
        
        self.source_dir = source_dir
        self.db_dir = db_dir
        
        # Naplózás beállítása
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
        log_file = os.path.join(log_dir, 'database.log')
        
        # Log könyvtár létrehozása
        os.makedirs(log_dir, exist_ok=True)
        
        # Logger létrehozása a basicConfig előtt
        self.logger = logging.getLogger(__name__)
        
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
        
        # Bővített diagnosztikai információk
        self.logger.info(f"Forrás könyvtár: {source_dir}")
        self.logger.info(f"Adatbázis könyvtár: {db_dir}")
        
        # Jogosultságok ellenőrzése és beállítása
        try:
            # Explicit jogosultság beállítás
            self._set_directory_permissions(self.db_dir)
            
            # Ellenőrizzük a tényleges jogosultságokat
            self.logger.info(f"DB könyvtár jogosultságai: {oct(os.stat(self.db_dir).st_mode)}")
        except Exception as e:
            self.logger.error(f"Jogosultság módosítási hiba: {e}")
            self.logger.error(self._get_traceback())
            raise
        
        # Embedding modell inicializálása
        try:
            # Figyelmeztető üzenet kezelése
            sys.stderr = open(os.devnull, 'w')  # Elnyeljük a deprecation warning-ot
            self.embeddings = HuggingFaceEmbeddingsAdapter(model_name="all-MiniLM-L6-v2")
            sys.stderr = sys.__stderr__  # Visszaállítjuk a szabványos hibakimenetet
            
            self.logger.info("Embedding modell sikeresen inicializálva")
        except Exception as e:
            self.logger.error(f"Embedding modell inicializálási hiba: {e}")
            self.logger.error(self._get_traceback())
            raise
        
        # ChromaDB konfigurálása
        try:
            # Ellenőrizzük, hogy tudunk-e fájlt írni
            self._test_write_permissions()
            
            # ChromaDB kliens inicializálása
            self.chroma_client = chromadb.PersistentClient(
                path=self.db_dir, 
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            self.logger.info("ChromaDB kliens sikeresen inicializálva")
        
        except PermissionError as pe:
            self.logger.error(f"Jogosultság hiba: {pe}")
            self.logger.error(self._get_traceback())
            raise
        except IOError as io:
            self.logger.error(f"IO hiba: {io}")
            self.logger.error(self._get_traceback())
            raise
        except Exception as e:
            self.logger.error(f"ChromaDB inicializálási hiba: {e}")
            self.logger.error(self._get_traceback())
            raise

    def _ensure_directory_with_permissions(self, directory):
        """
        Könyvtár létrehozása szükség esetén sudo jogosultsággal
        
        :param directory: Létrehozandó könyvtár útvonala
        """
        try:
            os.makedirs(directory, exist_ok=True)
        except PermissionError:
            self.logger.warning(f"Jogosultság hiánya a könyvtár létrehozásához: {directory}")
            try:
                # Próbáljuk meg sudo-val létrehozni
                subprocess.run(['sudo', 'mkdir', '-p', directory], check=True)
                self.logger.info(f"Könyvtár sikeresen létrehozva sudo-val: {directory}")
            except subprocess.SubprocessError as e:
                self.logger.error(f"Hiba a könyvtár sudo létrehozása során: {e}")
                raise

    def _set_directory_permissions(self, directory):
        """
        Könyvtár jogosultságainak beállítása
        
        :param directory: Könyvtár útvonala
        """
        try:
            os.chmod(directory, 0o777)  # Teljes olvasási, írási és végrehajtási jogok
        except PermissionError:
            self.logger.warning(f"Jogosultság hiánya a könyvtár jogainak módosításához: {directory}")
            try:
                # Próbáljuk meg sudo-val beállítani a jogokat
                subprocess.run(['sudo', 'chmod', '-R', '777', directory], check=True)
                self.logger.info(f"Könyvtár jogosultságai sikeresen beállítva sudo-val: {directory}")
            except subprocess.SubprocessError as e:
                self.logger.error(f"Hiba a könyvtár jogosultságainak sudo beállítása során: {e}")
                raise

    def _test_write_permissions(self):
        """
        Írási jogosultság tesztelése a DB könyvtárban
        """
        test_file = os.path.join(self.db_dir, 'write_test.txt')
        try:
            with open(test_file, 'w') as f:
                f.write('Test write')
            os.remove(test_file)
            self.logger.info("Sikeres írási teszt a DB könyvtárban")
        except PermissionError as e:
            self.logger.error(f"Írási jogosultság hiba a DB könyvtárban: {e}")
            self._set_directory_permissions(self.db_dir)
            # Próbáljuk újra a tesztet a jogosultságbeállítás után
            try:
                with open(test_file, 'w') as f:
                    f.write('Test write after permission change')
                os.remove(test_file)
                self.logger.info("Sikeres írási teszt a DB könyvtárban jogosultságmódosítás után")
            except Exception as e2:
                self.logger.error(f"Írási jogosultság hiba továbbra is fennáll: {e2}")
                raise

    def _get_traceback(self):
        """
        Aktuális stack trace lekérése hibakereséshez
        
        :return: Formázott stack trace szöveg
        """
        import traceback
        return traceback.format_exc()

    def check_and_update_if_needed(self):
        """
        Ellenőrzi, hogy az adatbázis létezik-e és naprakész-e
        Csak szükség esetén épít újra
        
        :return: Művelet sikeressége
        """
        try:
            # Ellenőrizzük, hogy létezik-e az adatbázis
            collection_exists = False
            try:
                self.chroma_client.get_collection(name="documents")
                collection_exists = True
            except Exception as e:
                self.logger.info(f"Collection nem létezik: {e}")
                collection_exists = False
                
            # Jelenlegi dokumentumok listázása
            current_files = self.list_documents()
            current_file_timestamps = {}
            for filepath in current_files:
                full_path = os.path.join(self.source_dir, filepath)
                current_file_timestamps[filepath] = os.path.getmtime(full_path)
                
            # Ha nem létezik az adatbázis, létrehozzuk
            if not collection_exists:
                self.logger.info("Adatbázis nem létezik, új létrehozása...")
                return self.setup_database()
                
            # Változások ellenőrzése
            if collection_exists:
                try:
                    # Collection lekérése
                    collection = self.chroma_client.get_collection(name="documents")
                    
                    # Metaadatok lekérése a fájltípusok ellenőrzéséhez
                    metadata = collection.get(include=["metadatas"])
                    stored_files = {}
                    
                    # Timestamp-ek kinyerése a metaadatokból
                    if metadata and 'metadatas' in metadata:
                        for meta in metadata['metadatas']:
                            if meta and 'filepath' in meta and 'modified_time' in meta:
                                stored_files[meta['filepath']] = meta['modified_time']
                    
                    # Változások ellenőrzése
                    files_changed = False
                    for filepath, timestamp in current_file_timestamps.items():
                        if filepath not in stored_files or stored_files[filepath] != timestamp:
                            files_changed = True
                            break
                    
                    # Törölt fájlok ellenőrzése
                    if len(stored_files) != len(current_file_timestamps):
                        files_changed = True
                        
                    # Adatbázis frissítése, ha változás történt
                    if files_changed:
                        self.logger.info("Változások észlelve a fájlokban, adatbázis frissítése...")
                        return self.update_database()
                    else:
                        self.logger.info("Adatbázis naprakész, nincs szükség frissítésre")
                        return True
                        
                except Exception as e:
                    self.logger.error(f"Hiba az adatbázis ellenőrzésekor: {e}")
                    self.logger.error(self._get_traceback())
                    return False
                    
        except Exception as e:
            self.logger.error(f"Adatbázis ellenőrzési hiba: {e}")
            self.logger.error(self._get_traceback())
            return False

    def _load_documents(self) -> List[Document]:
        """
        Dokumentumok betöltése a forrás könyvtárból
        
        :return: Betöltött dokumentumok listája
        """
        self.logger.info(f"Dokumentumok betöltése innen: {self.source_dir}")
        
        text_extensions = ["py", "java", "md", "txt", "json"]
        self.logger.info(f"Támogatott kiterjesztések: {text_extensions}")
        
        documents = []
        
        for root, dirs, files in os.walk(self.source_dir):
            self.logger.info(f"Vizsgált könyvtár: {root}")
            self.logger.info(f"Talált fájlok: {files}")
            
            for file in files:
                file_path = os.path.join(root, file)
                ext = file.split('.')[-1].lower()
                if ext in text_extensions:
                    try:
                        loader = TextLoader(file_path, encoding='utf8')
                        docs = loader.load()
                        documents.extend(docs)
                        self.logger.info(f"Sikeresen betöltve: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Hiba a fájl betöltése közben {file_path}: {e}")
                        self.logger.error(self._get_traceback())
        
        self.logger.info(f"Összes betöltött dokumentum száma: {len(documents)}")
        
        if len(documents) == 0:
            self.logger.warning(f"Nem találhatók dokumentumok a következő könyvtárban: {self.source_dir}")
        
        return documents

    def setup_database(self):
        """
        Adatbázis létrehozása dokumentumok alapján
        
        :return: Művelet sikeressége
        """
        try:
            # Dokumentumok betöltése
            documents = self._load_documents()
            
            if not documents:
                self.logger.warning("Nem találhatók dokumentumok a feldolgozáshoz")
                return False
            
            # Dokumentumok felosztása
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(documents)
            
            self.logger.info(f"Dokumentumok felosztva {len(chunks)} darabra")
            
            # Meglévő adatbázis törlése
            self.delete_database()
            
            # Új Collection létrehozása
            try:
                collection = self.chroma_client.get_or_create_collection(name="documents")
                self.logger.info("Collection sikeresen létrehozva vagy megnyitva")
            except Exception as e:
                self.logger.error(f"Collection létrehozási hiba: {e}")
                self.logger.error(self._get_traceback())
                return False
            
            # Dokumentumok hozzáadása
            for i, chunk in enumerate(chunks):
                try:
                    # Forrásfájl információk lekérése
                    source_path = chunk.metadata.get('source') if hasattr(chunk, 'metadata') else None
                    if source_path:
                        filepath = os.path.relpath(source_path, self.source_dir)
                        modified_time = os.path.getmtime(source_path)
                    else:
                        filepath = f"chunk_{i}"
                        modified_time = time.time()
                        
                    # Embedding előállítása 
                    embedding = self.embeddings.embed_documents([chunk.page_content])[0]
                    
                    # Dokumentum hozzáadása metaadatokkal
                    collection.add(
                        ids=[f"doc_{i}"],
                        embeddings=[embedding],
                        documents=[chunk.page_content],
                        metadatas=[{
                            "filepath": filepath,
                            "modified_time": modified_time,
                            "chunk_index": i
                        }]
                    )
                except Exception as e:
                    self.logger.error(f"Dokumentum hozzáadási hiba (index {i}): {e}")
                    self.logger.error(f"Chunk tartalma: {chunk.page_content[:100]}...")
            
            self.logger.info(f"Vektoros adatbázis sikeresen létrehozva és elmentve: {self.db_dir}")
            return True
        
        except Exception as e:
            self.logger.error(f"Adatbázis létrehozási hiba: {e}")
            self.logger.error(self._get_traceback())
            return False

    def delete_database(self):
        """
        Meglévő adatbázis törlése
        """
        try:
            # Ha létezik a 'documents' collection, töröljük
            try:
                self.chroma_client.delete_collection(name="documents")
                self.logger.info("Meglévő 'documents' collection törölve")
            except Exception as e:
                self.logger.warning(f"Collection törlési hiba: {e}")
            
            # Próbáljuk használni a ChromaDB reset metódust
            try:
                self.chroma_client.reset()
                self.logger.info("ChromaDB kliens sikeresen visszaállítva")
            except Exception as e:
                self.logger.warning(f"ChromaDB reset hiba: {e}")
                
                # Ha a reset nem működik, manuálisan töröljük a fájlokat
                if os.path.exists(self.db_dir):
                    for item in os.listdir(self.db_dir):
                        item_path = os.path.join(self.db_dir, item)
                        try:
                            if os.path.isfile(item_path):
                                os.unlink(item_path)
                            elif os.path.isdir(item_path):
                                import shutil
                                shutil.rmtree(item_path)
                        except Exception as e:
                            self.logger.error(f"Hiba fájl törlésekor: {e}")
                            self.logger.error(self._get_traceback())
                
                # Könyvtár újralétrehozása és jogosultságok beállítása
                self._ensure_directory_with_permissions(self.db_dir)
                self._set_directory_permissions(self.db_dir)
                
                self.logger.info("Meglévő adatbázis sikeresen törölve")
                
        except Exception as e:
            self.logger.error(f"Adatbázis törlési hiba: {e}")
            self.logger.error(self._get_traceback())
            raise

    def update_database(self, new_source_dir=None):
        """
        Adatbázis frissítése
        
        :param new_source_dir: Opcionális új forrás könyvtár
        :return: Művelet sikeressége
        """
        try:
            if new_source_dir:
                self.source_dir = new_source_dir
            
            self.delete_database()
            return self.setup_database()
        
        except Exception as e:
            self.logger.error(f"Adatbázis frissítési hiba: {e}")
            self.logger.error(self._get_traceback())
            return False

    def list_documents(self) -> List[str]:
        """
        Dokumentumok listázása a forrás könyvtárban
        
        :return: Dokumentumok relatív elérési útjainak listája
        """
        try:
            text_extensions = ["py", "java", "md", "txt", "json"]
            
            documents = []
            for ext in text_extensions:
                documents.extend(list(Path(self.source_dir).glob(f"**/*.{ext}")))
            
            relative_docs = [str(doc.relative_to(self.source_dir)) for doc in documents]
            
            self.logger.info(f"Talált dokumentumok: {len(relative_docs)}")
            return relative_docs
        except Exception as e:
            self.logger.error(f"Dokumentumok listázási hiba: {e}")
            self.logger.error(self._get_traceback())
            return []

    def similarity_search(self, query, k=5):
        """
        Hasonlósági keresés a vektoros adatbázisban
        
        :param query: Keresési lekérdezés
        :param k: Visszaadott találatok száma
        :return: Hasonló dokumentumok listája
        """
        try:
            self.logger.info(f"Hasonlósági keresés indítása: '{query}'")
            
            # Ellenőrizzük, hogy létezik-e a collection
            try:
                collection = self.chroma_client.get_collection(name="documents")
                self.logger.info("Collection sikeresen lekérve a kereséshez")
            except Exception as e:
                self.logger.error(f"Collection lekérési hiba: {e}")
                self.logger.info("Próbálom létrehozni az adatbázist...")
                
                setup_result = self.setup_database()
                if not setup_result:
                    self.logger.error("Nem sikerült létrehozni az adatbázist a kereséshez")
                    return []
                
                try:
                    collection = self.chroma_client.get_collection(name="documents")
                except Exception as e2:
                    self.logger.error(f"Collection még mindig nem elérhető létrehozás után: {e2}")
                    return []
            
            # Query beágyazása
            query_embedding = self.embeddings.embed_query(query)
            
            # Keresés végrehajtása
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Eredmények ellenőrzése
            if (not results or 
                'documents' not in results or 
                not results['documents'] or 
                len(results['documents'][0]) == 0):
                self.logger.warning("Nem találtunk egyező dokumentumot")
                return []
                
            # Eredmények feldolgozása
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0] if 'distances' in results else None
            
            # Document objektumok létrehozása
            result_docs = []
            
            for i, (content, metadata) in enumerate(zip(documents, metadatas)):
                dist_info = f" (távolság: {distances[i]:.4f})" if distances else ""
                self.logger.info(f"Találat {i+1}{dist_info}: {metadata.get('filepath', 'ismeretlen')}")
                
                doc = Document(
                    page_content=content,
                    metadata=metadata
                )
                result_docs.append(doc)
            
            self.logger.info(f"Összesen {len(result_docs)} találat visszaadva")
            return result_docs
            
        except Exception as e:
            self.logger.error(f"Hasonlósági keresés sikertelen: {e}")
            # Hibaelhárítási diagnosztika
            self.logger.error(f"Részletes hiba: {str(e)}")
            self.logger.error(self._get_traceback())
            return []