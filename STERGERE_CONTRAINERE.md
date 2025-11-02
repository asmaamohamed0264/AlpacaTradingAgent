# Pași pentru ștergerea containerelor Exited pentru AlpacaTradingAgent

## ⚠️ ATENȚIE
Acest document conține instrucțiuni pentru ștergerea **DOAR** containerelor Exited identificate pentru `alpacatradingagent-ata-nvm8bv`. 

## Containerele de șters (doar aceste 4):

1. `alpacatradingagent-ata-nvm8bv.1.0sztb90xjueljnrkjvli02pal`
2. `alpacatradingagent-ata-nvm8bv.1.fdx576ryuc25okyyan29r6q4d`
3. `alpacatradingagent-ata-nvm8bv.1.ik4a1qrvxhm9nt7c8bqa63yp6`
4. `alpacatradingagent-ata-nvm8bv.1.nmcop9lwy1np4x1k2p3221680`

## ✅ Containerul de PĂSTRAT (RUNNING):

- `alpacatradingagent-ata-nvm8bv.1.vxzyeoep69foopggthb8c2f58` - **NU ȘTERGE ACESTA!**

## Metodă 1: Prin SSH pe VPS (RECOMANDAT)

Conectează-te la VPS prin SSH și rulează:

```bash
# Pas 1: Verifică containerele (OPTIONAL - doar pentru verificare)
docker ps -a | grep alpacatradingagent-ata-nvm8bv

# Pas 2: Șterge doar containerele Exited specificate
docker rm alpacatradingagent-ata-nvm8bv.1.0sztb90xjueljnrkjvli02pal
docker rm alpacatradingagent-ata-nvm8bv.1.fdx576ryuc25okyyan29r6q4d
docker rm alpacatradingagent-ata-nvm8bv.1.ik4a1qrvxhm9nt7c8bqa63yp6
docker rm alpacatradingagent-ata-nvm8bv.1.nmcop9lwy1np4x1k2p3221680

# SAU - Șterge toate containerele Exited pentru această aplicație (MAI SIGUR)
docker ps -a --filter "name=alpacatradingagent-ata-nvm8bv" --filter "status=exited" --format "{{.ID}}" | xargs docker rm
```

## Metodă 2: Prin Dokploy Dashboard

1. Accesează `dokploy.qub3.uk/dashboard/docker`
2. Caută containerele cu numele de mai sus
3. Click pe fiecare container Exited
4. Selectează opțiunea "Delete" sau "Remove"

## Metodă 3: Comandă automată (UN SINGUR COMAND - RECOMANDAT)

```bash
# Șterge toate containerele Exited care încep cu "alpacatradingagent-ata-nvm8bv.1."
# dar NU șterge cel Running (care are status "Up")
docker ps -a --filter "name=alpacatradingagent-ata-nvm8bv.1" --filter "status=exited" -q | xargs -r docker rm
```

## Verificare după ștergere

```bash
# Verifică că au rămas doar containerele Running
docker ps -a | grep alpacatradingagent-ata-nvm8bv
```

Ar trebui să vezi doar:
- `alpacatradingagent-ata-nvm8bv.1.vxzyeoep69foopggthb8c2f58` cu status "Up"

## ⚠️ Dacă apare eroare

Dacă apare eroare că containerul este parte dintr-un serviciu Docker Swarm, folosește:

```bash
# Verifică serviciile Swarm
docker service ls | grep alpacatradingagent-ata

# Dacă e nevoie, forțează ștergerea (OPȚIONAL - doar dacă e necesar)
docker rm -f <container_id>
```

## Spațiu eliberat

După ștergere, poți verifica spațiul eliberat:
```bash
docker system df
```

