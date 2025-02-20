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
RAG-Expert/
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
cd RAG-Expert
python app/main.py
```

A webfelület elérhető: http://localhost:8080

## Hibaelhárítási útmutató

A rendszer robusztus hibakezelési mechanizmusokkal rendelkezik. Az alábbiakban összefoglaljuk a leggyakoribb problémákat és azok megoldásait.

(A teljes hibaelhárítási útmutató megtalálható az eredeti README-ben)

## Jelenlegi korlátok és jövőbeli fejlesztési célok

A rendszer jelenleg **nem képes** a következőkre, amelyek a jövőbeli fejlesztési célok között szerepelnek:

1. Projekt dokumentáció automatikus karbantartása
2. Git verziókezelés automatizálása
3. Maven build folyamat integrálása
4. Teszteredmények automatikus elemzése
5. Autonóm fejlesztési képesség

## Fejlesztési terv időbecslése

| Fejlesztési feladat | Becsült időigény | Claude AI segítségével |
|---------------------|------------------|------------------------|
| Project.md automatizálás | 2-3 nap | 1 nap |
| Git integráció | 1-2 hét | 3-5 nap |
| Maven integráció | 1 hét | 2-3 nap |
| Tesztelési integráció | 1-2 hét | 3-5 nap |
| Autonóm fejlesztés | 2-3 hét | 1-2 hét |

## Fejlesztési best practices

A projekt fejlesztése során követendő legjobb gyakorlatok:

1. Hibaellenállóság mindenütt
2. Részletes naplózás
3. Környezeti változók és konfiguráció kezelése
4. Egységes Frontend-backend kommunikáció
5. Átfogó tesztelés

## Licensz

MIT License

## Közreműködés

A projekt nyitott a közreműködésre. Kérjük, kövesse a standard fork-and-pull-request workflow-t.

---

Fejlesztő: Vitkovits Máté
Utolsó frissítés: 2025. február 20.
