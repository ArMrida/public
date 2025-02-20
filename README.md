# RAG Expert - Java Maven Fejlesztő Asszisztens

RAG Expert egy intelligens fejlesztői asszisztens rendszer, amely a Retrieval-Augmented Generation (RAG) technológiát használja komplex Java Maven projektek fejlesztésének támogatására.

## Jelenlegi képességek

A rendszer jelenlegi verziója a következő funkciókat támogatja:

- **Dokumentumkezelés**
  - Java forráskód és dokumentáció automatikus betöltése a `data` mappából
  - Dokumentumok intelligens chunkolása szemantikai egységekre
  - Vektoros reprezentáció létrehozása HuggingFace embedding modellel
  - Chromadb vektoros adatbázis kezelése perzisztens tárolással

- **Szemantikus keresés**
  - Természetes nyelvi kérdések alapján releváns kódrészletek visszakeresése
  - Kontextus-érzékeny keresés a fejlesztési dokumentációban
  - Hiányzó gyűjtemény automatikus létrehozása kereséskor

- **LLM integráció**
  - Claude Haiku model (claude-3-haiku-20240307) használata
  - Kontextus-alapú válaszgenerálás a visszakeresett dokumentumok alapján
  - Kódrészletek és dokumentáció intelligens értelmezése

- **Webes felhasználói felület**
  - Interaktív chat felület fejlesztési kérdések feltevéséhez
  - Adatbázis-kezelési funkciók (létrehozás, törlés, frissítés)
  - Dokumentumok listázása és megjelenítése
  - Válaszok markdown formázása és kódkiemelés

- **Robusztus hibakezelés**
  - Részletes naplózás a működés követésére
  - Automatikus hibaelhárítási kísérletek
  - Jogosultsági problémák automatikus kezelése
  - Hibaállapotok kecses kezelése a felhasználói felületen

## Mappastruktúra

A RAG Expert rendszer a következő mappastruktúrával rendelkezik:

```
RAG 2/
├── app/
│   ├── database.py        # Dokumentum adatbázis kezelő
│   ├── __init__.py
│   ├── llm_service.py     # Claude API kapcsolat
│   ├── logs/              # Alkalmazás naplók 
│   ├── main.py            # Fő alkalmazás és webszerver
│   └── __pycache__/       # Python bytecode fájlok
├── chroma_db/             # Vektoros adatbázis tárolása
├── data/
│   ├── docs/
│   │   └── project.MD     # Projekt dokumentáció
│   └── readme.md          # Fejlesztési projekt leírása
├── logs/                  # Központi naplók
├── readme.md              # Projekt leírás
├── requirements.txt       # Függőségi lista
├── static/
│   └── js/
│       └── app.js         # Frontend JavaScript
└── templates/
    └── index.html         # Webes felület sablon
```

## Telepítési és használati útmutató

### Környezet beállítása

```bash
# Virtuális környezet létrehozása
python -m venv venv

# Virtuális környezet aktiválása (Linux/MacOS)
source venv/bin/activate
# VAGY Windows esetén
# venv\Scripts\activate

# Függőségek telepítése
pip install -r requirements.txt
```

### Szükséges függőségek

A rendszer a következő fő függőségeket használja:
```
langchain==0.1.0
langchain-anthropic==0.1.1
langchain-community==0.0.17
sentence-transformers==2.2.2
chromadb==0.6.3
flask==2.3.3
python-dotenv==1.0.0
anthropic==0.8.1
```

### Használat

```bash
# Környezeti változók beállítása
export ANTHROPIC_API_KEY="your_api_key_here"

# Alkalmazás indítása
cd RAG\ 2
python app/main.py
```

A webfelület elérhető: http://localhost:8080

## Hibaelhárítási útmutató

A rendszer robusztus hibakezelési mechanizmusokkal rendelkezik. Az alábbiakban összefoglaljuk a leggyakoribb problémákat és azok megoldásait:

### Naplófájlok elhelyezkedése

Hiba esetén első lépésként ellenőrizd a naplófájlokat:
- **Fő alkalmazás napló**: `RAG 2/logs/app.log`
- **Adatbázis napló**: `RAG 2/app/logs/database.log`
- **LLM szolgáltatás napló**: `RAG 2/app/logs/llm_service.log`

### Gyakori hibák és megoldásaik

#### 1. Adatbázis inicializálási hibák

**Hibaüzenet**: `Collection létrehozási hiba: attempt to write a readonly database`

**Megoldás**:
- Ellenőrizd a `chroma_db` mappa jogosultságait: `ls -la RAG\ 2/chroma_db`
- Állítsd be a megfelelő jogosultságokat: `chmod -R 777 RAG\ 2/chroma_db`
- A rendszer automatikusan kezeli a jogosultsági problémákat, de ha a sudo jelszót kéri, add meg

#### 2. Embedding API hibák

**Hibaüzenet**: `'SentenceTransformer' object has no attribute 'embed_documents'`

**Megoldás**:
- Ez az API inkompatibilitási hiba a legfrissebb verzióval megoldódott
- Ha mégis előfordul, ellenőrizd a HuggingFaceEmbeddingsAdapter osztályt a database.py fájlban

#### 3. ChromaDB verziókompatibilitási hibák

**Hibaüzenet**: `You are using a deprecated configuration of Chroma.`

**Megoldás**:
- A ChromaDB 0.6.3 verzióval kompatibilis konfigurációt használunk
- Ha más verziót használsz, frissítsd azt: `pip install chromadb==0.6.3`

#### 4. API kulcs hibák

**Hibaüzenet**: `Hiányzó Anthropic API kulcs.`

**Megoldás**:
- Ellenőrizd, hogy a környezeti változó be van-e állítva: `echo $ANTHROPIC_API_KEY`
- Állítsd be újra: `export ANTHROPIC_API_KEY="your_key_here"`
- Használj `.env` fájlt a környezeti változók tárolására

#### 5. Frontendről nem érkezik válasz

**Hibaüzenet**: `Hiba történt a kérdés feldolgozása közben`

**Megoldás**:
- Ellenőrizd a böngésző konzolját (`F12` -> Console fül)
- Ellenőrizd a backend naplókat (lásd fent)
- Próbáld újratölteni az oldalt (`Ctrl+F5`) vagy újraindítani a szervert

### Diagnosztikai tippek

1. **Naplózás bekapcsolása fejlettebb szinten**:
   ```python
   # app/main.py módosítása
   logging.basicConfig(
       level=logging.DEBUG,  # INFO helyett DEBUG
       ...
   )
   ```

2. **ChromaDB részletes hibaelhárítás**:
   ```bash
   # Adatbázis mappájának tisztítása
   rm -rf RAG\ 2/chroma_db/*
   mkdir -p RAG\ 2/chroma_db
   chmod -R 777 RAG\ 2/chroma_db
   ```

3. **Válaszgenerálás tesztelése**:
   ```bash
   # LLM szolgáltatás önálló tesztelése
   python -c "
   from app.llm_service import LLMService
   service = LLMService()
   response = service.generate_response('Tesztválasz', [])
   print(response)
   "
   ```

4. **Frontend hibakeresés**:
   - Nyisd meg a böngésző fejlesztői eszközeit (F12)
   - Ellenőrizd a hálózati kéréseket (Network fül)
   - Ellenőrizd a JavaScript konzolon az esetleges hibákat (Console fül)

### Teljesítmény-optimalizálási tippek

1. **ChromaDB teljesítmény optimalizálása**:
   - Kisebb chunk_size (500-1000 között) használata a felbontásnál
   - A `chunk_overlap` értékének csökkentése 100-ra
   - A similarity_search `k` paraméterének csökkentése 3-ra

2. **API hívás optimalizálása**:
   - A Claude modell hőmérsékletének (temperature) 0.1-re csökkentése
   - A kontextus méretének optimalizálása - válaszd a legfontosabb 2-3 dokumentumot

## Jelenlegi korlátok és jövőbeli fejlesztési célok

A rendszer jelenleg **nem képes** a következőkre, amelyek a jövőbeli fejlesztési célok között szerepelnek:

### 1. Projekt dokumentáció automatikus karbantartása
- **Jelenlegi korlát**: A `project.md` fájl manuális frissítést igényel
- **Fejlesztési cél**: Automatikus projekt dokumentáció frissítés
  - Fejlesztési állapot intelligens követése és dokumentálása
  - Változások és döntések automatikus rögzítése
  - Fejlesztési mérföldkövek és nyitott feladatok nyomon követése

### 2. Git verziókezelés automatizálása
- **Jelenlegi korlát**: A rendszer nem végez Git műveleteket
- **Fejlesztési cél**: Integrált Git verziókezelés
  - Automatikus commit, push, pull és branch műveletek
  - Intelligens commit üzenetek generálása
  - Változások követése és összekapcsolása a dokumentációval

### 3. Maven build folyamat integrálása
- **Jelenlegi korlát**: Nincs build automatizálás
- **Fejlesztési cél**: Teljes Maven életciklus kezelés
  - Build folyamatok automatikus futtatása
  - Függőségek kezelése és frissítése
  - Build hibák elemzése és javítási javaslatok

### 4. Teszteredmények automatikus elemzése
- **Jelenlegi korlát**: Nem dolgozza fel a teszteredményeket
- **Fejlesztési cél**: Teljes tesztelési integráció
  - Tesztek automatikus futtatása
  - Teszteredmények feldolgozása és elemzése
  - Hibajavítási javaslatok generálása

### 5. Autonóm fejlesztési képesség
- **Jelenlegi korlát**: Felhasználói irányítást igényel
- **Fejlesztési cél**: Felügyelet nélküli fejlesztési képesség
  - Önálló fejlesztési döntéshozatal
  - Többlépéses fejlesztési feladatok végrehajtása
  - Proaktív hibaelhárítás és optimalizálás

## Fejlesztési terv időbecslése

| Fejlesztési feladat | Becsült időigény | Claude AI segítségével |
|---------------------|------------------|------------------------|
| Project.md automatizálás | 2-3 nap | 1 nap |
| Git integráció | 1-2 hét | 3-5 nap |
| Maven integráció | 1 hét | 2-3 nap |
| Tesztelési integráció | 1-2 hét | 3-5 nap |
| Autonóm fejlesztés | 2-3 hét | 1-2 hét |

## Fejlesztési best practices

A RAG Expert projekt fejlesztése során a következő legjobb gyakorlatokat érdemes követni:

1. **Hibaellenállóság mindenütt**
   - Mindig használj try-except blokkokat a kritikus funkcióknál
   - Biztosíts fallback mechanizmusokat a hibák esetére
   - A hibákat mind a felhasználói felületen, mind a naplókban rögzítsd

2. **Részletes naplózás**
   - Használj különböző naplózási szinteket (INFO, DEBUG, ERROR)
   - A hibáknál mindig naplózd a stacktrace-t
   - Kritikus műveleteknél naplózd a bemenetet és a kimenetet is

3. **Környezeti változók és konfiguráció**
   - Használj .env fájlt a környezeti változók tárolására
   - Kerüld az érzékeny adatok (pl. API kulcsok) közvetlen beégetését a kódba
   - Használj konfigurációs fájlt a beállításokhoz

4. **Frontend-backend kommunikáció**
   - Egységes JSON válasz formátum: `{"status": "success|error", "response|message": "..."}`
   - A hibákat explicit módon jelezd a frontenddel
   - Minden API végpont legyen dokumentálva és konzisztens

5. **Tesztelés**
   - Írj egységteszteket a kritikus komponensekhez
   - Használj integration teszteket az API végpontokhoz
   - Teszteld a hibaállapotokat is, ne csak a sikeres eseteket

## Licensz

MIT License
Fejlesztő: Vitkovits Máté

## Közreműködés

A projekt nyitott a közreműködésre. Kérjük, kövesse a standard fork-and-pull-request workflow-t.

---

Utolsó frissítés: 2025. február 20.
