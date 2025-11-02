# Ghid de Testare Multi-Provider LLM

## 🧪 Testare Locală (Înainte de Deploy)

### Opțiunea 1: Test Complet (Toți Providerii)

```bash
# Asigură-te că ai API keys în .env
python test_multi_provider.py
```

Acest script va testa toți providerii disponibili și va afișa un rezumat.

### Opțiunea 2: Test Rapid (Un Provider)

```bash
# Test cu OpenAI
LLM_PROVIDER=openai TEST_MODEL=gpt-4o-mini python test_provider_simple.py

# Test cu DeepSeek
LLM_PROVIDER=deepseek TEST_MODEL=deepseek-chat python test_provider_simple.py

# Test cu OpenRouter
LLM_PROVIDER=openrouter TEST_MODEL=openai/gpt-4o-mini python test_provider_simple.py
```

---

## 🚀 Testare în Aplicație (După Deploy)

### Pasul 1: Configurare în Dokploy

1. Mergi în Dokploy → Proiectul tău → Application ATA
2. Click pe "Environment Settings"
3. Adaugă variabilele pentru testare:

#### Test cu DeepSeek:
```bash
DEEPSEEK_API_KEY=sk-your-key
LLM_PROVIDER=deepseek
DEEP_THINK_LLM=deepseek-chat
QUICK_THINK_LLM=deepseek-chat
```

#### Test cu OpenRouter:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=openai/gpt-4o-mini
```

### Pasul 2: Redeploy

1. În Dokploy, fă click pe "Redeploy" sau "Deploy"
2. Așteaptă ca build-ul să se termine
3. Verifică logs pentru mesaje de eroare

### Pasul 3: Verificare în Logs

1. În Dokploy → Application → Logs
2. Caută mesaje care indică provider-ul folosit:
   - `Using provider: deepseek for quick_think_llm`
   - `Using provider: openrouter for deep_think_llm`
   - Sau mesaje de eroare dacă ceva nu merge

### Pasul 4: Test Funcțional

1. Deschide Web UI-ul aplicației
2. Rulează o analiză pentru un symbol (ex: AAPL)
3. Verifică că:
   - Analiza se execută fără erori
   - Rezultatele sunt coerente
   - Nu apar erori în console/logs

---

## 🔍 Verificări Post-Deploy

### 1. Verificare Configurație

Testează că configurația este citită corect:

```python
# În Python console sau script
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import get_config

config = get_config()
print(f"LLM Provider: {config.get('llm_provider')}")
print(f"Deep Think Model: {config.get('deep_think_llm')}")
print(f"Quick Think Model: {config.get('quick_think_llm')}")
```

### 2. Verificare API Keys

Asigură-te că API keys sunt setate corect:

```bash
# În Dokploy logs sau terminal
echo $DEEPSEEK_API_KEY  # Sau OPENROUTER_API_KEY, etc.
```

### 3. Test Direct în Cod

Puteți adăuga logging în `trading_graph.py` pentru a verifica provider-ul folosit:

```python
# După linia de inițializare LLM
print(f"[DEBUG] Deep Think Provider: {deep_think_provider}, Model: {deep_think_model}")
print(f"[DEBUG] Quick Think Provider: {quick_think_provider}, Model: {quick_think_model}")
```

---

## ⚠️ Troubleshooting

### Problemă: "Provider 'xxx' not found"

**Soluție**: Verifică că provider-ul este în lista:
```python
from tradingagents.llm_providers import LLMFactory
print(LLMFactory.list_providers())
```

### Problemă: "API key not found"

**Soluție**: 
1. Verifică că API key-ul este setat în Dokploy Environment Settings
2. Verifică că numele variabilei este corect (ex: `DEEPSEEK_API_KEY`, nu `DEEPSEEK_KEY`)
3. Redeploy aplicația după adăugarea key-ului

### Problemă: "Model not found"

**Soluție**: 
- Pentru OpenRouter: verifică formatul `provider/model-name` (ex: `openai/gpt-4o-mini`)
- Pentru DeepSeek: verifică că modelul este `deepseek-chat` sau `deepseek-coder`
- Verifică lista de modele disponibile:
```python
from tradingagents.llm_providers import LLMFactory
models = LLMFactory.get_available_models("deepseek")  # sau "openrouter"
print(models)
```

### Problemă: Fallback la OpenAI

**Soluție**: Dacă vedeți "Warning: Could not initialize... Falling back to OpenAI":
1. Verifică logs pentru mesajul de eroare exact
2. Verifică că API key-ul este valid
3. Verifică că provider-ul este în lista de providers disponibili

---

## 📊 Comparație Rezultate

După testare, compară:

1. **Costuri**: Verifică în dashboard-ul provider-ului (OpenRouter, DeepSeek) costurile
2. **Calitate**: Compară rezultatele analizei cu OpenAI vs DeepSeek vs OpenRouter
3. **Viteză**: Compară timpul de execuție

---

## ✅ Checklist Pre-Deploy

- [ ] Testat local cu `test_multi_provider.py`
- [ ] Cel puțin un provider funcționează
- [ ] API keys setate în `.env` local
- [ ] Codul se compilează fără erori
- [ ] Nu există erori de linting

## ✅ Checklist Post-Deploy

- [ ] API keys setate în Dokploy Environment Settings
- [ ] Aplicația se rebuild-ează fără erori
- [ ] Logs arată provider-ul corect
- [ ] Analiza rulează fără erori
- [ ] Rezultatele sunt coerente

---

## 🎯 Test Scenarii

### Scenariu 1: DeepSeek pentru Tot
```bash
LLM_PROVIDER=deepseek
DEEP_THINK_LLM=deepseek-chat
QUICK_THINK_LLM=deepseek-chat
DEEPSEEK_API_KEY=sk-your-key
```
**Așteptat**: Analiza rulează, costuri mai mici, calitate similară

### Scenariu 2: OpenRouter Mix
```bash
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=google/gemini-flash-1.5
OPENROUTER_API_KEY=sk-or-v1-your-key
```
**Așteptat**: Analiza rulează, acces la multiple modele, costuri competitive

### Scenariu 3: Fallback Test
```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=invalid-key
```
**Așteptat**: Fallback automat la OpenAI, warning în logs

---

**Notă**: Păstrează OpenAI API key setat pentru fallback în caz de probleme!

