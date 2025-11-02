# Ghid Multi-Provider LLM pentru AlpacaTradingAgent

## Situația Actuală

Aplicația folosește în prezent **exclusiv OpenAI** prin LangChain (`ChatOpenAI`):
- **Deep Think LLM**: `o3-mini` (default)
- **Quick Think LLM**: `gpt-4o-mini` (default)

## Noua Arhitectură Multi-Provider

Am implementat un **sistem de abstractizare** care permite folosirea mai multor furnizori de LLM:

### ✅ Furnizori Suportați

1. **OpenAI** (gpt-4o, o3, gpt-5, etc.)
2. **DeepSeek** (deepseek-chat, deepseek-coder)
3. **Anthropic/Claude** (claude-3-5-sonnet, claude-3-5-haiku)
4. **OpenRouter** ⭐ NOU - Acces unificat la 100+ modele (OpenAI, Claude, Gemini, Mistral, etc.)

---

## Cum să Folosești

### Opțiunea 1: Configurare în `default_config.py` sau `.env`

```python
# tradingagents/default_config.py sau în config-ul tău
config = {
    "llm_provider": "deepseek",  # Provider default pentru toate LLM-urile
    "deep_think_llm": "deepseek-chat",
    "quick_think_llm": "deepseek-chat",
}

# SAU folosind format "provider:model"
config = {
    "deep_think_llm": "deepseek:deepseek-chat",
    "quick_think_llm": "openai:gpt-4o-mini",  # Mix de providers!
}
```

### Opțiunea 2: Variabile de Mediu

Adaugă în `.env`:

```bash
# Provider settings
LLM_PROVIDER=deepseek
DEEP_THINK_LLM=deepseek-chat
QUICK_THINK_LLM=deepseek-chat

# API Keys
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
OPENAI_API_KEY=sk-your-openai-key-here  # Keep for fallback
```

### Opțiunea 3: Provider Diferit pentru Fiecare LLM

```python
config = {
    "llm_provider": "openai",  # Default
    "deep_think_provider": "deepseek",  # Deep thinking folosește DeepSeek
    "deep_think_llm": "deepseek-chat",
    "quick_think_provider": "openai",  # Quick thinking folosește OpenAI
    "quick_think_llm": "gpt-4o-mini",
}
```

---

## Modele Disponibile

### OpenAI
- `gpt-4o`, `gpt-4o-mini`
- `gpt-3.5-turbo`
- `o3`, `o3-mini`
- `gpt-5`, `gpt-5-mini`, `gpt-5-nano`

### DeepSeek
- `deepseek-chat` (recomandat pentru trading)
- `deepseek-coder` (pentru code analysis dacă e nevoie)
- `deepseek-reasoner` (dacă disponibil)

### Anthropic (Claude)
- `claude-3-5-sonnet-20241022` (best performance)
- `claude-3-5-haiku-20241022` (faster, cheaper)
- `claude-3-opus-20240229`

---

## Comparație Costuri (aprox.)

| Provider | Model | Cost per 1M tokens (input) | Cost per 1M tokens (output) | Best For |
|----------|-------|---------------------------|----------------------------|----------|
| OpenAI | gpt-4o-mini | $0.15 | $0.60 | Quick analysis |
| OpenAI | o3-mini | $0.80 | $3.00 | Deep reasoning |
| DeepSeek | deepseek-chat | $0.14 | $0.28 | **Cost-effective alternative** |
| Anthropic | claude-3-5-haiku | $0.25 | $1.25 | Balanced |
| Anthropic | claude-3-5-sonnet | $3.00 | $15.00 | Best quality |

**Recomandare pentru cost optimization:**
- Use **DeepSeek** pentru analiști (quick_think) → **~53% mai ieftin** decât gpt-4o-mini
- Use **OpenAI o3-mini** pentru trader/risk manager (deep_think) → Best reasoning

---

## Instalare Dependențe

### Pentru DeepSeek (folosește OpenAI-compatible API)

DeepSeek funcționează cu `langchain-openai` existent - **nu necesită pachete noi!**

Doar adaugă API key în `.env`:
```bash
DEEPSEEK_API_KEY=sk-your-key
```

### Pentru Anthropic (Claude)

```bash
pip install langchain-anthropic
```

Adaugă în `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key
```

---

## Exemple de Configurație

### Exemplu 1: DeepSeek pentru Tot (cel mai ieftin)

```python
config = {
    "llm_provider": "deepseek",
    "deep_think_llm": "deepseek-chat",
    "quick_think_llm": "deepseek-chat",
}
```

### Exemplu 2: Mix - DeepSeek Quick, OpenAI Deep

```python
config = {
    "deep_think_provider": "openai",
    "deep_think_llm": "o3-mini",
    "quick_think_provider": "deepseek",
    "quick_think_llm": "deepseek-chat",
}
```

### Exemplu 3: Format "provider:model" (flexibil)

```python
config = {
    "deep_think_llm": "deepseek:deepseek-chat",
    "quick_think_llm": "openai:gpt-4o-mini",
}
```

### Exemplu 4: Claude pentru Calitate Maximă

```python
config = {
    "llm_provider": "anthropic",
    "deep_think_llm": "claude-3-5-sonnet-20241022",
    "quick_think_llm": "claude-3-5-haiku-20241022",
}
```

---

## Testing Multi-Provider

### Verifică Providerii Disponibili

```python
from tradingagents.llm_providers import LLMFactory

# Listează providerii disponibili
providers = LLMFactory.list_providers()
print(f"Available providers: {providers}")
# Output: ['openai', 'deepseek', 'anthropic']

# Listează modelele pentru un provider
models = LLMFactory.get_available_models("deepseek")
print(f"DeepSeek models: {models}")
# Output: ['deepseek-chat', 'deepseek-coder']
```

### Test Rapid

```python
from tradingagents.llm_providers import LLMFactory

# Test DeepSeek
llm = LLMFactory.create_llm("deepseek-chat", provider="deepseek")
response = llm.invoke("What is 2+2?")
print(response.content)

# Test OpenAI
llm = LLMFactory.create_llm("gpt-4o-mini", provider="openai")
response = llm.invoke("What is 2+2?")
print(response.content)
```

---

## Compatibilitate Înapoi

✅ **Sistemul este 100% compatibil înapoi** - dacă nu specifici provider, folosește OpenAI ca înainte.

✅ **Toate componentele existente** (agenti, tool nodes, etc.) funcționează fără modificări.

✅ **Fallback automat** la OpenAI dacă un provider nu este disponibil sau eșuează.

---

## Avantaje Multi-Provider

1. **Cost Optimization**: Poți mixa providers pentru costuri minime
2. **Redundancy**: Dacă un provider e down, fallback automat
3. **Flexibility**: Poți testa diferite modele pentru performance
4. **Vendor Lock-in Avoidance**: Nu ești blocat la un singur furnizor

---

## Troubleshooting

### Problemă: "Provider 'deepseek' not found"
**Soluție**: Verifică că `DEEPSEEK_API_KEY` este setat în `.env`

### Problemă: "Could not initialize deep_think_llm"
**Soluție**: Sistemul face fallback automat la OpenAI. Verifică API keys.

### Problemă: Model nu este recunoscut
**Soluție**: Folosește formatul `provider:model` explicit:
```python
"deep_think_llm": "deepseek:deepseek-chat"
```

---

## Recomandări pentru Trading

### Configurație Optimizată pentru Costuri:

```python
{
    "quick_think_provider": "deepseek",
    "quick_think_llm": "deepseek-chat",  # Analiști - mai ieftin
    "deep_think_provider": "openai",
    "deep_think_llm": "o3-mini",  # Trader/Risk - best reasoning
}
```

**Economii estimate: ~40-50% pe analiști** (cei mai mulți calls), păstrând calitatea la trader.

### Configurație pentru Performanță Maximă:

```python
{
    "deep_think_provider": "anthropic",
    "deep_think_llm": "claude-3-5-sonnet-20241022",
    "quick_think_provider": "openai",
    "quick_think_llm": "gpt-4o-mini",
}
```

---

## Adăugare Provider Nou

Dacă vrei să adaugi un alt provider (ex: Google Gemini, Mistral AI):

1. Creează `tradingagents/llm_providers/your_provider.py`
2. Implementează `BaseLLM` și `LLMProvider`
3. Adaugă provider-ul în `LLMFactory._initialize_providers()`

Vezi `deepseek_provider.py` ca exemplu - e simplu de urmat!

---

## Next Steps

1. **Testează cu DeepSeek** pentru a vedea dacă îți convine calitatea
2. **Monitorizează costurile** - compară OpenAI vs DeepSeek
3. **Ajustează configurația** bazat pe rezultate
4. **Consideră mix providers** - DeepSeek pentru analiști, OpenAI pentru trader

---

**Notă**: DeepSeek oferă **API compatible cu OpenAI**, deci funcționează out-of-the-box cu LangChain!

