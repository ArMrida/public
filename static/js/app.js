// Naplózás beállítása
function log(message, level = 'info') {
    const timestamp = new Date().toISOString();
    console[level](`[${timestamp}] ${message}`);
}

// Adatbázis létrehozása
function setupDatabase() {
    log('Adatbázis létrehozásának kezdeményezése...');
    fetch('/setup-database', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            log('Adatbázis sikeresen létrehozva');
            showMessage('Adatbázis sikeresen létrehozva', 'success');
        } else {
            log(`Adatbázis létrehozási hiba: ${data.message}`, 'error');
            showMessage(`Adatbázis létrehozási hiba: ${data.message}`, 'danger');
        }
    })
    .catch(error => {
        log(`Hiba az adatbázis létrehozása közben: ${error}`, 'error');
        showMessage('Hiba történt az adatbázis létrehozása közben', 'danger');
    });
}

// Adatbázis törlése
function deleteDatabase() {
    log('Adatbázis törlésének kezdeményezése...');
    fetch('/delete-database', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            log('Adatbázis sikeresen törölve');
            showMessage('Adatbázis sikeresen törölve', 'success');
        } else {
            log(`Adatbázis törlési hiba: ${data.message}`, 'error');
            showMessage(`Adatbázis törlési hiba: ${data.message}`, 'danger');
        }
    })
    .catch(error => {
        log(`Hiba az adatbázis törlése közben: ${error}`, 'error');
        showMessage('Hiba történt az adatbázis törlése közben', 'danger');
    });
}

// Adatbázis frissítése
function updateDatabase() {
    log('Adatbázis frissítésének kezdeményezése...');
    fetch('/update-database', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            log('Adatbázis sikeresen frissítve');
            showMessage('Adatbázis sikeresen frissítve', 'success');
        } else {
            log(`Adatbázis frissítési hiba: ${data.message}`, 'error');
            showMessage(`Adatbázis frissítési hiba: ${data.message}`, 'danger');
        }
    })
    .catch(error => {
        log(`Hiba az adatbázis frissítése közben: ${error}`, 'error');
        showMessage('Hiba történt az adatbázis frissítése közben', 'danger');
    });
}

// Dokumentumok listázása
function listDocuments() {
    log('Dokumentumok listázásának kezdeményezése...');
    fetch('/list-documents')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            log(`Dokumentumok sikeresen listázva. Talált dokumentumok: ${data.documents.length}`);
            displayDocuments(data.documents);
        } else {
            log(`Dokumentum listázási hiba: ${data.message}`, 'error');
            showMessage(`Hiba a dokumentumok listázása közben: ${data.message}`, 'danger');
        }
    })
    .catch(error => {
        log(`Hiba a dokumentumok listázása közben: ${error}`, 'error');
        showMessage('Hiba történt a dokumentumok listázása közben', 'danger');
    });
}

// Kérdés küldése
function askQuestion() {
    const question = document.getElementById('user-input').value.trim();
    if (!question) {
        log('Üres kérdés elküldésének kísérlete', 'warn');
        showMessage('Kérjük, írjon be egy kérdést!', 'danger');
        return;
    }

    log(`Kérdés küldése: "${question}"`);
    
    // Felhasználói kérdés megjelenítése
    const userMessageElement = document.createElement('div');
    userMessageElement.className = 'user-message';
    userMessageElement.textContent = question;
    document.getElementById('chat-messages').appendChild(userMessageElement);
    
    // Betöltés jelzése
    const loadingElement = document.createElement('div');
    loadingElement.className = 'assistant-message';
    loadingElement.innerHTML = '<div class="spinner-border spinner-border-sm text-secondary" role="status"><span class="visually-hidden">Betöltés...</span></div> Válasz generálása...';
    document.getElementById('chat-messages').appendChild(loadingElement);
    
    // Görgetés a chat végére
    document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
    
    // Input mező kiürítése
    document.getElementById('user-input').value = '';

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question }),
    })
    .then(response => response.json())
    .then(data => {
        // Betöltő eltávolítása
        document.getElementById('chat-messages').removeChild(loadingElement);
        
        if (data.status === 'success') {
            log('Válasz sikeresen megérkezett');
            displayResponse(data.response);
        } else {
            log(`Hiba a válasz generálása közben: ${data.message}`, 'error');
            showMessage(`Hiba történt a válasz generálása közben: ${data.message}`, 'danger');
            
            // Hibaüzenet megjelenítése a chatben
            const errorElement = document.createElement('div');
            errorElement.className = 'assistant-message error';
            errorElement.textContent = `Hiba történt a kérdés feldolgozása közben: ${data.message}`;
            document.getElementById('chat-messages').appendChild(errorElement);
            document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
        }
    })
    .catch(error => {
        // Betöltő eltávolítása
        if (document.getElementById('chat-messages').contains(loadingElement)) {
            document.getElementById('chat-messages').removeChild(loadingElement);
        }
        
        log(`Hiba a kérdés feldolgozása közben: ${error}`, 'error');
        showMessage('Hiba történt a kérdés feldolgozása közben', 'danger');
        
        // Hibaüzenet megjelenítése a chatben
        const errorElement = document.createElement('div');
        errorElement.className = 'assistant-message error';
        errorElement.textContent = 'Hiba történt a kérdés feldolgozása közben';
        document.getElementById('chat-messages').appendChild(errorElement);
        document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
    });
}

// Segédfüggvények
function showMessage(message, type) {
    const messageElement = document.getElementById('message');
    messageElement.textContent = message;
    messageElement.className = `alert alert-${type}`;
    messageElement.style.display = 'block';

    setTimeout(() => {
        messageElement.style.display = 'none';
    }, 5000);
}

function displayDocuments(documents) {
    const documentList = document.getElementById('document-list');
    documentList.innerHTML = '<h5>Talált dokumentumok:</h5>';
    
    if (documents.length === 0) {
        const emptyNotice = document.createElement('p');
        emptyNotice.textContent = 'Nem található dokumentum az adatbázisban.';
        documentList.appendChild(emptyNotice);
    } else {
        const ul = document.createElement('ul');
        documents.forEach(doc => {
            const li = document.createElement('li');
            li.textContent = doc;
            ul.appendChild(li);
        });
        documentList.appendChild(ul);
    }
    documentList.style.display = 'block';
}

function displayResponse(response) {
    log(`Válasz megjelenítése (${response.length} karakter)`);
    
    try {
        // Asszisztens válaszának megjelenítése
        const assistantMessage = document.createElement('div');
        assistantMessage.className = 'assistant-message';
        
        // Markdown konvertálása, ha van ilyen függvény
        if (typeof markdownToHtml === 'function') {
            assistantMessage.innerHTML = markdownToHtml(response);
        } else {
            // Egyszerű formázás, ha nincs markdown konvertáló
            assistantMessage.innerHTML = formatText(response);
        }
        
        document.getElementById('chat-messages').appendChild(assistantMessage);
        
        // Görgetés a chat végére
        document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
        
        // Syntax highlighting alkalmazása, ha elérhető a Prism
        if (typeof Prism !== 'undefined') {
            Prism.highlightAllUnder(assistantMessage);
        }
    } catch (error) {
        log(`Hiba a válasz megjelenítése közben: ${error}`, 'error');
        
        // Egyszerű szövegként próbáljuk megjeleníteni
        const fallbackMessage = document.createElement('div');
        fallbackMessage.className = 'assistant-message';
        fallbackMessage.textContent = response;
        document.getElementById('chat-messages').appendChild(fallbackMessage);
    }
}

// Egyszerű szövegformázás a markdown helyett, ha az nem elérhető
function formatText(text) {
    // Kódblokkok kezelése
    text = text.replace(/```([\s\S]*?)```/g, function(match, code) {
        return `<pre><code>${code}</code></pre>`;
    });
    
    // Inline kód kezelése
    text = text.replace(/`([^`]+)`/g, function(match, code) {
        return `<code>${code}</code>`;
    });
    
    // Bekezdések
    text = text.replace(/\n\n/g, '</p><p>');
    
    // Sortörések
    text = text.replace(/\n/g, '<br>');
    
    return `<p>${text}</p>`;
}

// Markdown konvertálása HTML-re, ha a markdown-it könyvtár elérhető
function markdownToHtml(markdown) {
    if (typeof markdownit !== 'undefined') {
        const md = markdownit({
            html: false,
            linkify: true,
            typographer: true,
            highlight: function (str, lang) {
                if (lang && Prism.languages[lang]) {
                    try {
                        return Prism.highlight(str, Prism.languages[lang], lang);
                    } catch (__) {}
                }
                return ''; // Hagyjuk a Prism.highlightAll-ra
            }
        });
        return md.render(markdown);
    } else {
        // Fallback a saját egyszerű formázóra
        return formatText(markdown);
    }
}

// Eseményfigyelők hozzáadása
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('setup-db').addEventListener('click', setupDatabase);
    document.getElementById('delete-db').addEventListener('click', deleteDatabase);
    document.getElementById('update-db').addEventListener('click', updateDatabase);
    document.getElementById('list-documents').addEventListener('click', listDocuments);
    document.getElementById('send-btn').addEventListener('click', askQuestion);
    
    // Enter billentyű kezelése
    document.getElementById('user-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            askQuestion();
        }
    });
    
    // Log indítása
    log('Alkalmazás betöltve, használatra kész');
});