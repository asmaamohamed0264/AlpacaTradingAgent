# OpenRouter Setup Guide pentru AlpacaTradingAgent

## Ce este OpenRouter?

**OpenRouter** este un serviciu care oferă acces unificat la **100+ modele LLM** printr-un singur API:
- ✅ OpenAI (GPT-4, o3, etc.)
- ✅ Anthropic (Claude 3.5 Sonnet, Haiku)
- ✅ Google (Gemini Pro, Flash)
- ✅ DeepSeek (Chat, Coder)
- ✅ Mistral AI
- ✅ Meta Llama
- ✅ Și multe altele!

**Avantaje:**
- 🎯 **Un singur API key** pentru toate modelele
- 💰 **Prețuri competitive** (uneori mai bune decât direct)
- 🔄 **Failover automat** între modele
- 📊 **Analytics** și tracking unificat
- 🚀 **Setup simplu** - API compatibil cu OpenAI

---

## Setup Rapid

### Pasul 1: Obține API Key de la OpenRouter

1. Mergi la https://openrouter.ai/keys
2. Creează cont (poți folosi GitHub/Gmail)
3. Obține API key gratuit (are $5 credit la signup)

### Pasul 2: Configurează în Dokploy

În Dokploy → Environment Settings → Adaugă:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=openai/gpt-4o-mini
```

**SAU** format complet:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
DEEP_THINK_LLM=openrouter:anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=openrouter:openai/gpt-4o-mini
```

### Pasul 3: Restart Aplicația

Done! 🎉

---

## Modele Populare Disponibile pe OpenRouter

### Pentru Quick Thinking (Analiști):
```python
"openai/gpt-4o-mini"          # Fast, cheap
"openai/gpt-3.5-turbo"         # Cheapest
"google/gemini-flash-1.5"      # Very fast
"deepseek/deepseek-chat"       # Cost-effective
"anthropic/claude-3.5-haiku"   # Balanced
```

### Pentru Deep Thinking (Trader/Risk Manager):
```python
"anthropic/claude-3.5-sonnet"  # Best quality
"openai/gpt-4o"                # Excellent
"openai/o3-mini"               # Best reasoning (if available)
"google/gemini-pro-1.5"        # Good alternative
"mistralai/mistral-large"      # European option
```

---

## Exemple de Configurație

### Exemplu 1: Claude pentru Tot (calitate maximă)

```bash
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=anthropic/claude-3.5-haiku
OPENROUTER_API_KEY=sk-or-v1-your-key
```

### Exemplu 2: Mix OpenAI + Claude

```bash
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=openai/gpt-4o-mini
OPENROUTER_API_KEY=sk-or-v1-your-key
```

### Exemplu 3: Cost-Optimized (DeepSeek + Gemini)

```bash
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=google/gemini-pro-1.5
QUICK_THINK_LLM=deepseek/deepseek-chat
OPENROUTER_API_KEY=sk-or-v1-your-key
```

### Exemplu 4: Format Explicite

```bash
DEEP_THINK_LLM=openrouter:anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=openrouter:openai/gpt-4o-mini
OPENROUTER_API_KEY=sk-or-v1-your-key
```

---

## Comparație Costuri (aprox. pe OpenRouter)

| Model | Cost per 1M input | Cost per 1M output | Provider |
|-------|-------------------|---------------------|----------|
| `openai/gpt-4o-mini` | ~$0.15 | ~$0.60 | OpenAI |
| `openai/gpt-4o` | ~$2.50 | ~$10.00 | OpenAI |
| `anthropic/claude-3.5-haiku` | ~$0.25 | ~$1.25 | Anthropic |
| `anthropic/claude-3.5-sonnet` | ~$3.00 | ~$15.00 | Anthropic |
| `deepseek/deepseek-chat` | ~$0.14 | ~$0.28 | DeepSeek |
| `google/gemini-flash-1.5` | ~$0.075 | ~$0.30 | Google |
| `google/gemini-pro-1.5` | ~$1.25 | ~$5.00 | Google |

**Recomandare cost-optimized:**
```bash
QUICK_THINK_LLM=google/gemini-flash-1.5  # Cel mai ieftin
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet  # Best quality
```

---

## Avantaje OpenRouter vs. Direct Providers

### ✅ Avantaje OpenRouter:

1. **Un singur API key** - nu mai ai nevoie de keys separate
2. **Failover automat** - dacă un model e down, OpenRouter routează automat
3. **Rate limiting unified** - un singur sistem de rate limiting
4. **Analytics dashboard** - vezi toate calls într-un singur loc
5. **Prețuri competitive** - uneori mai bune decât direct
6. **Acces la modele private** - unele modele disponibile doar prin OpenRouter

### ⚠️ Considerații:

- Depinzi de un serviciu intermediar (OpenRouter)
- Latency ușor mai mare (routing extra)
- Unele modele pot fi mai noi și mai puțin testate

---

## Testing OpenRouter

```python
from tradingagents.llm_providers import LLMFactory

# Test cu Claude prin OpenRouter
llm = LLMFactory.create_llm(
    "anthropic/claude-3.5-sonnet",
    provider="openrouter"
)
response = llm.invoke("What is 2+2?")
print(f"Provider: {response.provider}")
print(f"Model: {response.model}")
print(f"Content: {response.content}")
```

---

## Listează Modelele Disponibile

```python
from tradingagents.llm_providers import LLMFactory

# Listează toate modelele OpenRouter
models = LLMFactory.get_available_models("openrouter")
for model in models:
    print(model)
```

**Notă**: OpenRouter are peste 100 de modele! Pentru lista completă, verifică: https://openrouter.ai/models

---

## Configurație Recomandată pentru Trading

### Opțiunea 1: Quality + Cost Balance

```bash
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=google/gemini-flash-1.5
```

**De ce:**
- Claude Sonnet pentru decizii critice (trader) - best quality
- Gemini Flash pentru analiști - foarte rapid și ieftin

### Opțiunea 2: Maxim Cost Savings

```bash
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=google/gemini-pro-1.5
QUICK_THINK_LLM=deepseek/deepseek-chat
```

**Economii: ~60-70% vs OpenAI pure**

### Opțiunea 3: Best Performance

```bash
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=openai/gpt-4o-mini
```

---

## Troubleshooting

### Problemă: "OpenRouter API key not found"
**Soluție**: Verifică că `OPENROUTER_API_KEY` este setat și începe cu `sk-or-v1-`

### Problemă: "Model not found"
**Soluție**: Verifică formatul modelului. Trebuie să fie `provider/model-name`:
- ✅ `anthropic/claude-3.5-sonnet`
- ✅ `openai/gpt-4o-mini`
- ❌ `claude-3.5-sonnet` (lipsește provider)

### Problemă: Rate limiting
**Soluție**: OpenRouter are rate limits. Upgrade plan-ul sau reduce numărul de calls.

---

## Comparație: Direct vs. OpenRouter

| Aspect | Direct Provider | OpenRouter |
|--------|----------------|------------|
| **Setup** | Multiple API keys | Un singur key |
| **Cost** | Varies | Competitiv |
| **Flexibility** | Doar provider-ul tău | 100+ modele |
| **Failover** | Manual | Automatic |
| **Latency** | Lower | Slightly higher |

**Recomandare**: OpenRouter e perfect dacă:
- Vrei să testezi multiple modele
- Vrei failover automat
- Preferi un singur API key
- Vrei analytics unificat

---

## Next Steps

1. **Obține API key** de la https://openrouter.ai/keys
2. **Configurează în Dokploy** cu modelul preferat
3. **Testează** cu un symbol și verifică rezultatele
4. **Monitorizează costurile** în dashboard-ul OpenRouter
5. **Experimentează** cu diferite modele pentru găsirea optimului

---

**Notă**: OpenRouter oferă $5 credit gratuit la signup - perfect pentru testare! 🎁

