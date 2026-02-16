# 📊 Konjunkturovervåkning Dashboard

Et dashboard for å følge med på Norges Banks prognoser fra Pengepolitisk Rapport (PPR).

**🔗 Live Dashboard:** [Klikk her for å se dashboardet](https://[DITT-BRUKERNAVN].github.io/konjunktur-dashboard/)

---

## 📋 Om Dashboardet

Dette dashboardet viser økonomiske nøkkeltall fra Norges Bank:
- **Konsumpriser (KPI)** - Månedlig inflasjon
- **Boligpriser** - Månedlig utvikling  
- **Registrert ledighet** - Arbeidsledighet over tid
- **BNP Fastlands-Norge** - Kvartalsvekst
- **Sentrale økonomiske størrelser** - Årlige prognoser

**Datakilde:** Norges Banks Pengepolitiske Rapport (PPR)  
**Oppdateringsfrekvens:** Kvartalsvis (mars, juni, september, desember)

---

## 🚀 Hvordan Det Fungerer

### Automatiske Oppdateringer ✨

Dashboardet oppdateres **automatisk** fire ganger i året:
- **20. mars** - PPR 1/26
- **20. juni** - PPR 2/26  
- **20. september** - PPR 3/26
- **20. desember** - PPR 4/26

GitHub Actions kjører et Python-script som:
1. ⬇️ Laster ned nyeste PPR-PDF fra Norges Bank
2. 🔍 Parser ut tallene fra tabellene
3. 📝 Oppdaterer dashboardet automatisk
4. 🚀 Publiserer endringene (live innen 2 minutter)

### Manuell Oppdatering (Tvungen oppdatering)

**Metode 1: Via GitHub Actions (Anbefalt) 🎯**
1. Gå til **Actions**-fanen i repositoryet
2. Klikk på **"Update PPR Dashboard"** i venstre meny
3. Klikk **"Run workflow"** (grønn knapp øverst til høyre)
4. Klikk grønn **"Run workflow"** igjen for å bekrefte
5. Vent 2-3 minutter → Dashboardet oppdateres automatisk

**Metode 2: Manuell redigering 📝**
1. Klikk på `index.html` i repositoryet
2. Klikk på blyant-ikonet ✏️ ("Edit this file")
3. Oppdater tallene manuelt i HTML-koden
4. Scroll ned og klikk **"Commit changes"**
5. Dashboardet oppdateres innen 2 minutter

---

## 📁 Filstruktur

```
konjunktur-dashboard/
├── index.html                    # Hovedfilen - selve dashboardet
├── oppdater_ppr.py              # Python-script for å hente nye PPR-data
├── .github/
│   └── workflows/
│       └── update-ppr.yml       # GitHub Actions workflow (automatisering)
└── README.md                     # Denne filen
```

---

## 🎮 Brukerveiledning

### For Sluttbrukere (Kun Se Dashboard)

**Åpne dashboardet:**
- Gå til: `https://[brukernavn].github.io/konjunktur-dashboard/`
- Bookmarke siden for enkel tilgang
- Fungerer på mobil, nettbrett og PC
- **Ingen pålogging nødvendig**

### For Administratorer (Vedlikeholde Dashboard)

**Sjekke status på siste oppdatering:**
1. Gå til **Actions**-fanen
2. Se grønn ✅ eller rød ❌ status
3. Klikk på kjøringen for å se detaljer

**Få e-postvarsling:**
- GitHub sender automatisk e-post hvis workflow feiler
- Gå til repository → Watch → Custom → Workflows

---

## 🔧 Teknisk Dokumentasjon

### For Utviklere

**Stack:**
- **Frontend:** Ren HTML/CSS (ingen JavaScript, ingen dependencies)
- **Backend:** Python 3.11 med pdfplumber, BeautifulSoup4
- **Hosting:** GitHub Pages (gratis, ubegrenset båndbredde)
- **Automatisering:** GitHub Actions (2000 gratis minutter/måned)

**Python-avhengigheter:**
```bash
pip install pdfplumber beautifulsoup4 lxml requests
```

**Kjør lokalt:**
```bash
# Last ned og parser nyeste PPR automatisk
python oppdater_ppr.py

# Eller bruk en spesifikk PDF-fil
python oppdater_ppr.py ppr_4_25.pdf
```

### GitHub Actions Workflow

Workflow-filen (`.github/workflows/update-ppr.yml`) gjør følgende:

1. **Scheduled run:** Kjører automatisk kl. 10:00 UTC på PPR-datoer
2. **Manual trigger:** Kan trigges manuelt via GitHub UI
3. **Python setup:** Installerer Python 3.11 og avhengigheter
4. **Data fetch:** Kjører `oppdater_ppr.py` for å hente ny PPR
5. **Diff check:** Sjekker om `index.html` faktisk ble endret
6. **Commit:** Committer endringer hvis data er oppdatert
7. **Auto-deploy:** GitHub Pages deployer automatisk ved commit til main

---

## ⚙️ Konfigurering

### Endre Oppdateringstidspunkter

Rediger `.github/workflows/update-ppr.yml`:

```yaml
schedule:
  # Syntaks: 'minutt time dag måned ukedag'
  # 0 10 20 3,6,9,12 * = Kl 10:00 UTC (11:00 CET), 20. dag i mars/juni/sep/des
  - cron: '0 10 20 3,6,9,12 *'
```

**Eksempler:**
- `0 14 20 3,6,9,12 *` - Kl 14:00 UTC (15:00 CET)
- `0 10 19 3,6,9,12 *` - Dagen før (19.) i tilfelle tidlig publisering
- `0 10 * * 1` - Hver mandag (testing)

### Legge Til Nye Tabeller

**I HTML:**
1. Åpne `index.html`
2. Kopier en eksisterende `<div class="section">`
3. Endre overskrift og tabelldata
4. Commit

**I Python-scriptet:**
1. Åpne `oppdater_ppr.py`
2. Legg til ny `_find_table_X()` metode
3. Oppdater `parse()` til å kalle den nye metoden
4. Test lokalt før commit

---

## 🐛 Feilsøking

### Problem: Dashboardet viser gamle data

**Løsning:**
1. Sjekk **Actions**-fanen → Er siste kjøring grønn ✅ eller rød ❌?
2. Hvis rød: Klikk på den → Se loggene → Identifiser feilen
3. Hvis grønn: Sjekk commit-historikken → Ble `index.html` faktisk oppdatert?
4. **Tvungen oppdatering:** Kjør workflow manuelt (se instruksjon over)

### Problem: GitHub Actions feiler

**Vanlige årsaker:**

| Feil | Årsak | Løsning |
|------|-------|---------|
| "PDF not found" | PPR ikke publisert ennå | Vent noen dager, prøv igjen |
| "Table parsing error" | Norges Bank endret PDF-format | Oppdater `oppdater_ppr.py` |
| "Connection timeout" | Nettverksfeil | Workflow prøver igjen automatisk |
| "Permission denied" | GitHub token mangler rettigheter | Sjekk repo settings → Actions → Permissions |

**Debug-tips:**
1. Gå til **Actions** → Klikk på rød kjøring
2. Expand alle steg (klikk på pilene)
3. Les feilmeldingen i rødt
4. Google feilen eller spør ChatGPT/Claude

### Problem: Dashboardet vises ikke på GitHub Pages

**Sjekkliste:**
- [ ] Er repositoryet **Public**? (Private krever GitHub Pro)
- [ ] Er GitHub Pages aktivert? **Settings → Pages → Source: main branch**
- [ ] Heter filen `index.html`? (ikke Index.html eller index.htm)
- [ ] Venter du 2-3 minutter etter endringer?

**Tvungen refresh:**
- Hard refresh: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
- Eller åpne inkognito-vindu

---

## 📊 Datakvalitet og Begrensninger

### Viktig å Vite

Python-scriptet gjør **semi-automatisk parsing** av PDF-er. Dette betyr:

✅ **Fungerer godt for:**
- Standard tabellformater Norges Bank har brukt historisk
- Numeriske verdier i kjente kolonner/rader
- Konsistente PDF-layouter

⚠️ **Krever manuell verifikasjon:**
- Første gang etter hvert kvartal (sammenlign med original PDF)
- Hvis Norges Bank endrer PDF-design
- Ved uventede verdier (f.eks. negative tall der det skal være positive)

❌ **Kan feile ved:**
- Store layout-endringer i PPR
- Nye tabellformater
- Scannede PDF-er uten OCR
- Tabeller som spenner over flere sider

### Best Practice for Datakvalitet

**Anbefalt prosedyre hvert kvartal:**

1. **Dag 0 (20. mars/juni/sep/des):**
   - Workflow kjører automatisk kl 10:00 UTC
   - Du får e-post hvis det feiler

2. **Dag 0-1:**
   - Åpne dashboardet
   - Åpne [original PPR fra Norges Bank](https://www.norges-bank.no/aktuelt/nyheter-og-hendelser/Publikasjoner/Pengepolitisk-rapport-med-vurdering-av-finansiell-stabilitet/)
   - Spot-sjekk 5-10 nøkkeltall:
     - KPI for siste måned
     - BNP-vekst for inneværende år
     - Styringsrente-prognose
     - Et par tilfeldige tall

3. **Hvis avvik funnet:**
   - Rediger `index.html` manuelt for å rette
   - Eller oppdater `oppdater_ppr.py` hvis systematisk feil
   - Commit endringene

4. **Del med kolleger:**
   - Send melding: "Dashboard oppdatert med PPR X/26 ✅"

---

## 🤝 Bidra til Prosjektet

### Forslag til Forbedringer?

**Enkel måte:**
1. Åpne en **Issue** i dette repositoryet
2. Beskriv forslaget eller problemet
3. Legg gjerne ved skjermbilder

**Avansert måte (utviklere):**
1. **Fork** dette repositoryet (knapp øverst til høyre)
2. Klon din fork lokalt: `git clone https://github.com/dittbrukernavn/konjunktur-dashboard.git`
3. Lag en branch: `git checkout -b feature/min-forbedring`
4. Gjør endringer og test lokalt
5. Commit: `git commit -m "Legg til X funksjonalitet"`
6. Push: `git push origin feature/min-forbedring`
7. Åpne en **Pull Request** på GitHub

---

## 📜 Lisens og Krediteringer

**Kode:** Fri å bruke, modifisere og dele (MIT-lisens)  
**Data:** © Norges Bank (offentlig tilgjengelig data)  
**Opphavsrett:** Data fra Norges Bank er underlagt deres vilkår

**Laget av:** Sir Markus, Innovasjonsleder AI @ Telenor  
**Med hjelp fra:** Claude (Anthropic)  
**For:** Telenor kolleger og alle som er interessert i norsk økonomi

---

## 🎯 Roadmap (Fremtidige Forbedringer)

### Fase 2 - Interaktivitet
- [ ] **Interaktive grafer** med Chart.js (velg tidsperiode, zoom, sammenlign)
- [ ] **Sammenligning mellom PPR-rapporter** ("hva endret seg siden sist?")
- [ ] **Eksport til Excel/CSV** for videre analyse
- [ ] **Dark mode** for bedre lesbarhet

### Fase 3 - Integrasjoner  
- [ ] **API-integrasjon** direkte mot Norges Bank (hvis de får API)
- [ ] **E-postvarsling** når nye data er tilgjengelige
- [ ] **Slack-integrasjon** for team-varsling
- [ ] **Power BI embed** for Telenor-interne dashboards

### Fase 4 - Avansert Analyse
- [ ] **Historisk trendanalyse** (sammenlign prognoser med faktisk utfall)
- [ ] **Prediksjonsmodeller** (ML for å forutsi neste PPR)
- [ ] **Benchmark mot andre land** (sammenlign med Sverige, Danmark, EU)
- [ ] **Real-time data** fra andre kilder (SSB, IMF, etc.)

**Vil du jobbe på en av disse?** Åpne en Issue og si fra! 🚀

---

## 📞 Kontakt og Support

**Prosjektansvarlig:** Sir Markus  
**Rolle:** Innovasjonsleder AI, Telenor  
**GitHub:** [@dittbrukernavn](https://github.com/dittbrukernavn)

**Spørsmål?**
- Åpne en [Issue](https://github.com/dittbrukernavn/konjunktur-dashboard/issues)
- Send intern melding via Telenor Slack
- E-post: [din-epost]

---

## 🙏 Takk til

- **Norges Bank** for tilgjengeliggjøring av data
- **GitHub** for gratis hosting og CI/CD
- **Python-communityet** for fantastiske biblioteker (pdfplumber, BeautifulSoup)
- **Alle som bidrar** med forbedringer og rapporterer bugs

---

## 📚 Nyttige Lenker

- [Norges Bank - PPR Arkiv](https://www.norges-bank.no/aktuelt/nyheter-og-hendelser/Publikasjoner/Pengepolitisk-rapport-med-vurdering-av-finansiell-stabilitet/)
- [GitHub Pages Dokumentasjon](https://docs.github.com/en/pages)
- [GitHub Actions Dokumentasjon](https://docs.github.com/en/actions)
- [Python pdfplumber](https://github.com/jsvine/pdfplumber)

---

**Sist oppdatert:** 16. februar 2026  
**Versjon:** 1.0 (MVP)  
**Status:** ✅ I produksjon

---

*Laget med ❤️ for bedre økonomisk innsikt*
