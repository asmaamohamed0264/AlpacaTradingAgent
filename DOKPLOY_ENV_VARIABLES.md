# Variabile de Mediu pentru Dokploy - AlpacaTradingAgent

## 📋 Copiază și adaugă în Dokploy → Environment Settings

### 🔑 API Keys Esențiale (OBLIGATORII)

```bash
# Alpaca Trading API - Pentru trading real
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_USE_PAPER=True

# OpenAI API - Pentru LLM agents (folosit ca fallback dacă altele eșuează)
OPENAI_API_KEY=your_openai_api_key_here
```

### 💰 API Keys pentru Date Financiare (OBLIGATORII)

```bash
# Finnhub - Știri financiare și date în timp real
FINNHUB_API_KEY=your_finnhub_api_key_here

# FRED - Date macroeconomice (GDP, inflație, rate dobânzi)
FRED_API_KEY=your_fred_api_key_here

# CoinDesk/CryptoCompare - Știri și date crypto
COINDESK_API_KEY=your_cryptocompare_api_key_here
```

### 🤖 LLM Provider Settings (NOU - Multi-Provider Support)

```bash
# Provider Default (opțiuni: "openai", "deepseek", "openrouter", "anthropic")
LLM_PROVIDER=openai

# Modeluri LLM
DEEP_THINK_LLM=o3-mini
QUICK_THINK_LLM=gpt-4o-mini

# Provider-uri specifice (opțional - dacă vrei provider diferit pentru fiecare)
# DEEP_THINK_PROVIDER=openai
# QUICK_THINK_PROVIDER=openai
```

### 🔐 LLM Provider API Keys (OPȚIONAL - Doar pentru provider-ul ales)

#### Dacă folosești DeepSeek:
```bash
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
LLM_PROVIDER=deepseek
DEEP_THINK_LLM=deepseek-chat
QUICK_THINK_LLM=deepseek-chat
```

#### Dacă folosești OpenRouter (acces la 100+ modele):
```bash
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=openai/gpt-4o-mini
```

#### Dacă folosești Anthropic/Claude direct:
```bash
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
LLM_PROVIDER=anthropic
DEEP_THINK_LLM=claude-3-5-sonnet-20241022
QUICK_THINK_LLM=claude-3-5-haiku-20241022
```

---

## 📝 Template Complet (Copy-Paste Ready)

Copiază blocul de mai jos și înlocuiește `your_*_key_here` cu valorile reale:

```bash
# ============================================
# ALPACATRADINGAGENT - ENVIRONMENT VARIABLES
# ============================================

# --- ALPACA TRADING API (OBLIGATORIU) ---
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_USE_PAPER=True

# --- OPENAI API (OBLIGATORIU - pentru fallback) ---
OPENAI_API_KEY=your_openai_api_key_here

# --- FINANCIAL DATA APIs (OBLIGATORIU) ---
FINNHUB_API_KEY=your_finnhub_api_key_here
FRED_API_KEY=your_fred_api_key_here
COINDESK_API_KEY=your_cryptocompare_api_key_here

# --- LLM PROVIDER SETTINGS ---
LLM_PROVIDER=openai
DEEP_THINK_LLM=o3-mini
QUICK_THINK_LLM=gpt-4o-mini

# --- OPTIONAL: Alternative LLM Providers (adăugă doar dacă vrei să folosești) ---
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
# OPENROUTER_API_KEY=your_openrouter_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

---

## 🎯 Configurație Recomandată pentru Costuri Minime

```bash
# Trading APIs
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_USE_PAPER=True

# Financial Data APIs
FINNHUB_API_KEY=your_finnhub_api_key_here
FRED_API_KEY=your_fred_api_key_here
COINDESK_API_KEY=your_cryptocompare_api_key_here

# LLM Provider - DeepSeek (mai ieftin decât OpenAI)
DEEPSEEK_API_KEY=sk-your-deepseek-key
LLM_PROVIDER=deepseek
DEEP_THINK_LLM=deepseek-chat
QUICK_THINK_LLM=deepseek-chat

# OpenAI ca fallback
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 🎯 Configurație pentru Calitate Maximă

```bash
# Trading APIs
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_USE_PAPER=True

# Financial Data APIs
FINNHUB_API_KEY=your_finnhub_api_key_here
FRED_API_KEY=your_fred_api_key_here
COINDESK_API_KEY=your_cryptocompare_api_key_here

# LLM Provider - OpenRouter cu Claude (best quality)
OPENROUTER_API_KEY=sk-or-v1-your-key
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=openai/gpt-4o-mini

# OpenAI ca fallback
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 📍 Unde să Obții API Keys

### Alpaca Trading API
- 🌐 https://app.alpaca.markets/signup
- 📝 Necesită: Cont Alpaca, verificare identitate

### OpenAI API
- 🌐 https://platform.openai.com/api-keys
- 💳 Necesită: Card pentru credit

### DeepSeek API
- 🌐 https://platform.deepseek.com/api_keys
- 💰 Mai ieftin decât OpenAI

### OpenRouter API
- 🌐 https://openrouter.ai/keys
- 🎁 $5 credit gratuit la signup
- 🌟 Acces la 100+ modele

### Anthropic/Claude API
- 🌐 https://console.anthropic.com/
- 💳 Necesită: Card pentru credit

### Finnhub API
- 🌐 https://finnhub.io/register
- 🆓 Plan gratuit disponibil

### FRED API
- 🌐 https://fred.stlouisfed.org/docs/api/api_key.html
- 🆓 Complet gratuit, fără credit card

### CoinDesk/CryptoCompare API
- 🌐 https://www.cryptocompare.com/cryptopian/api-keys
- 🆓 Plan gratuit disponibil

---

## ✅ Checklist Pre-Deploy

Înainte de deploy, asigură-te că ai:

- [ ] `ALPACA_API_KEY` - Setat și validat
- [ ] `ALPACA_SECRET_KEY` - Setat și validat
- [ ] `ALPACA_USE_PAPER` - Setat la `True` (pentru testare) sau `False` (pentru live)
- [ ] `OPENAI_API_KEY` - Setat (minim pentru fallback)
- [ ] `FINNHUB_API_KEY` - Setat
- [ ] `FRED_API_KEY` - Setat (gratuit, ușor de obținut)
- [ ] `COINDESK_API_KEY` - Setat
- [ ] `LLM_PROVIDER` - Setat (default: `openai`)
- [ ] Provider-specific API key dacă nu folosești OpenAI (ex: `DEEPSEEK_API_KEY`)

---

## 🔍 Verificare după Adăugare

După ce adaugi variabilele în Dokploy:

1. **Redeploy** aplicația
2. **Verifică logs** - Caută mesaje:
   ```
   [LLM] Initializing Deep Think LLM - Provider: ...
   [LLM] ✅ LLM initialized successfully
   ```
3. **Testează** aplicația - Rulează o analiză pentru un symbol
4. **Verifică erori** - Dacă vezi erori despre API keys, verifică că:
   - Numele variabilei este exact corect (case-sensitive!)
   - Valoarea nu are spații în jur
   - API key-ul este valid

---

## ⚠️ Note Importante

1. **Nu expune API keys** în logs sau în cod public
2. **Păstrează OpenAI API key** setat pentru fallback automat
3. **ALPACA_USE_PAPER=True** înseamnă trading pe cont demo (fără bani reali)
4. **FRED_API_KEY** este gratuit - obține-l imediat
5. **COINDESK_API_KEY** - verifică că folosești formatul corect pentru CryptoCompare

---

**Gata de copiat în Dokploy!** 📋

