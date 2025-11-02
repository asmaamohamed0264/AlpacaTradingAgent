# Quick Start: OpenRouter în AlpacaTradingAgent

## 🚀 Setup în 3 Pași

### Pasul 1: Obține API Key
1. Mergi la https://openrouter.ai/keys
2. Sign up (gratuit, primești $5 credit!)
3. Copiază API key-ul (format: `sk-or-v1-...`)

### Pasul 2: Configurează în Dokploy

În Dokploy → Environment Settings → Adaugă:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
LLM_PROVIDER=openrouter
DEEP_THINK_LLM=anthropic/claude-3.5-sonnet
QUICK_THINK_LLM=openai/gpt-4o-mini
```

### Pasul 3: Restart

Done! 🎉 Aplicația folosește acum OpenRouter.

---

## 💡 De Ce OpenRouter?

✅ **100+ modele** printr-un singur API  
✅ **Un singur API key** în loc de multiple  
✅ **Prețuri competitive**  
✅ **Failover automat**  
✅ **Analytics dashboard**  

---

## 📊 Modele Recomandate

### Pentru Analiști (Quick):
- `google/gemini-flash-1.5` - Cel mai ieftin și rapid
- `openai/gpt-4o-mini` - Balanced
- `deepseek/deepseek-chat` - Cost-effective

### Pentru Trader/Risk (Deep):
- `anthropic/claude-3.5-sonnet` - Best quality
- `openai/gpt-4o` - Excellent
- `google/gemini-pro-1.5` - Good alternative

---

## 🔄 Switch Rapid între Modele

Vrei să testezi un alt model? Doar schimbă în Dokploy:

```bash
# Testează Gemini
QUICK_THINK_LLM=google/gemini-flash-1.5

# Testează Mistral
QUICK_THINK_LLM=mistralai/mistral-small

# Revino la OpenAI
QUICK_THINK_LLM=openai/gpt-4o-mini
```

**Restart aplicația** și gata!

---

## 📚 Documentație Completă

Vezi `OPENROUTER_SETUP.md` pentru:
- Liste complete de modele
- Comparație costuri
- Exemple avansate
- Troubleshooting

