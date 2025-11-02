# Quick Start: Folosire DeepSeek sau Alți Providers

## ✅ Ce am Implementat

Am adăugat **suport complet pentru multi-provider LLM**:
- ✅ OpenAI (existent)
- ✅ DeepSeek (nou)
- ✅ Anthropic/Claude (nou)
- ✅ Extensibil pentru alți providers

## 🚀 Cum să Folosești DeepSeek (Imediat)

### Pasul 1: Obține API Key de la DeepSeek

1. Mergi la https://platform.deepseek.com/api_keys
2. Creează cont și obține API key
3. Copiază key-ul

### Pasul 2: Adaugă în Environment Variables (Dokploy)

În Dokploy → Environment Settings → Adaugă:

```bash
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
LLM_PROVIDER=deepseek
DEEP_THINK_LLM=deepseek-chat
QUICK_THINK_LLM=deepseek-chat
```

**SAU** pentru mix (recomandat):

```bash
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
OPENAI_API_KEY=sk-your-openai-key-here
QUICK_THINK_PROVIDER=deepseek
QUICK_THINK_LLM=deepseek-chat
DEEP_THINK_PROVIDER=openai
DEEP_THINK_LLM=o3-mini
```

### Pasul 3: Restart Aplicația

Aplicația va folosi automat DeepSeek după restart!

## 📊 Comparație Rapidă

| Aspect | OpenAI | DeepSeek | Recomandare |
|--------|--------|----------|-------------|
| **Cost** | Mai scump | ~50% mai ieftin | ✅ DeepSeek pentru analiști |
| **Calitate** | Excelentă | Foarte bună | ✅ OpenAI pentru decizii critice |
| **Setup** | ✅ Funcționează | ✅ Funcționează | ✅ Ambii |

## 💡 Configurație Recomandată

### Pentru Costuri Minime:
```bash
LLM_PROVIDER=deepseek
DEEP_THINK_LLM=deepseek-chat
QUICK_THINK_LLM=deepseek-chat
```
**Economii: ~50% pe LLM costs**

### Pentru Calitate + Cost (Recomandat):
```bash
QUICK_THINK_PROVIDER=deepseek
QUICK_THINK_LLM=deepseek-chat
DEEP_THINK_PROVIDER=openai
DEEP_THINK_LLM=o3-mini
```
**Economii: ~40% pe total, păstrează calitatea la trader**

## ⚠️ Notă Importantă

Funcțiile care folosesc **web search** (în `get_stock_news_openai`, `get_global_news_openai`, `get_fundamentals_openai`) vor continua să folosească OpenAI pentru moment, deoarece DeepSeek nu suportă web search direct în API.

Pentru acestea, sistemul folosește automat OpenAI (cu fallback).

## 🔄 Rollback la OpenAI

Dacă vrei să revii la OpenAI:

```bash
LLM_PROVIDER=openai
# SAU șterge setările DeepSeek
```

## ✅ Verificare

După configurare, verifică în logs că vede provider-ul:

```
[INFO] Using provider: deepseek for quick_think_llm
[INFO] Using provider: openai for deep_think_llm
```

---

**Nu necesită recompile sau rebuild!** Doar restart aplicației în Dokploy.

