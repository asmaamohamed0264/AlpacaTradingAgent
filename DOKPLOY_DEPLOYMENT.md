# Ghid de Deployment pe Dokploy pentru AlpacaTradingAgent

## Configurare în Dokploy

### 1. Creare Aplicație în Dokploy

1. **Tip aplicație**: Alege "Docker Image" sau "Git Repository"
2. **Repository URL**: `https://github.com/asmaamohamed0264/AlpacaTradingAgent.git`
3. **Build Type**: 
   - Dacă folosești Docker: `Dockerfile`
   - Dacă folosești Git: Setează build command și working directory

### 2. Variabile de Mediu Necesare

Configurează următoarele variabile de mediu în Dokploy:

#### API Keys Esențiale (OBLIGATORII)

```bash
# Alpaca Trading API
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_USE_PAPER=True  # True pentru paper trading, False pentru live

# OpenAI API pentru LLM agents
OPENAI_API_KEY=your_openai_api_key_here
```

#### API Keys pentru Date Financiare (OBLIGATORII)

```bash
# Finnhub - știri financiare și date
FINNHUB_API_KEY=your_finnhub_api_key_here

# FRED - date macroeconomice
FRED_API_KEY=your_fred_api_key_here

# CoinDesk/CryptoCompare - știri crypto
COINDESK_API_KEY=your_cryptocompare_api_key_here
```

#### API Keys Opționale

```bash
# Twitter - pentru sentiment analysis (opțional)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
```

### 3. Configurare Port

- **Port expus**: `7860`
- **Protocol**: HTTP
- **Path**: `/` (root)

### 4. Comandă de Rulare

Dacă folosești Docker:
```bash
python run_webui_dash.py --server-name 0.0.0.0 --port 7860
```

### 5. Configurare Docker (dacă folosești Dockerfile)

Dockerfile-ul din repository este deja configurat corect:
- Expune portul 7860
- Rulează pe 0.0.0.0 (pentru acces extern)
- Folosește Python 3.11

### 6. Verificare Deployment

După deployment, verifică:
1. Aplicația rulează pe `http://your-domain:7860`
2. Web UI-ul se încarcă corect
3. Verifică logs pentru erori legate de API keys

### 7. Probleme Comune și Soluții

#### Problemă: Aplicația nu pornește
- Verifică că toate variabilele de mediu sunt setate
- Verifică logs pentru erori de conexiune
- Asigură-te că portul 7860 este expus

#### Problemă: Erori API
- Verifică că toate API keys sunt valide
- Pentru Alpaca, asigură-te că ai cont activat
- Pentru OpenAI, verifică că ai credit disponibil

#### Problemă: Aplicația se oprește
- Verifică resursele VPS (CPU, RAM)
- Aplicatia poate consuma resurse semnificative
- Verifică timeout-uri în Dokploy

### 8. Resurse Recomandate pentru VPS

- **RAM**: Minimum 2GB, recomandat 4GB+
- **CPU**: Minimum 2 cores
- **Disk**: Minimum 10GB pentru cache și date

### 9. Monitorizare

Monitorizează:
- Utilizarea memoriei (aplicația poate consuma multă memorie)
- Rate limiting de la API-uri (OpenAI, Alpaca, etc.)
- Logs pentru erori

### 10. Securitate

⚠️ **IMPORTANT**: 
- Nu partaja niciodată API keys în repository
- Folosește variabile de mediu în Dokploy
- Pentru paper trading, folosește `ALPACA_USE_PAPER=True`
- Pentru live trading, folosește `ALPACA_USE_PAPER=False` și asigură-te că știi ce faci

## Comandă Rapidă de Verificare

După deployment, testează accesarea:
```bash
curl http://your-vps-ip:7860
```

Ar trebui să primești HTML-ul paginii Dash.

