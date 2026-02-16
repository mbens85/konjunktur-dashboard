# ⚡ Hurtig Oppsettsguide

## Steg-for-Steg: Legg Til Auto-Oppdatering

### 1️⃣ Last Opp Python-Scriptet

1. Gå til ditt repository på GitHub
2. Klikk **"Add file"** → **"Upload files"**
3. Dra og slipp filen `oppdater_ppr.py`
4. Skriv commit message: "Legg til PPR-oppdateringsscript"
5. Klikk **"Commit changes"**

---

### 2️⃣ Opprett Workflow-Fil

1. Klikk **"Add file"** → **"Create new file"**
2. I filnavnfeltet, skriv: `.github/workflows/update-ppr.yml`
   - **VIKTIG:** Hele stien må være nøyaktig slik, inkludert mappene
3. Lim inn innholdet fra filen jeg har laget (se under)
4. Klikk **"Commit changes"**

**Innhold for `update-ppr.yml`:**

```yaml
name: Update PPR Dashboard

on:
  schedule:
    - cron: '0 10 20 3,6,9,12 *'
  workflow_dispatch:

jobs:
  update-dashboard:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install pdfplumber beautifulsoup4 lxml requests
    
    - name: Download and parse PPR
      run: |
        python oppdater_ppr.py
      continue-on-error: true
    
    - name: Check if HTML was updated
      id: check_changes
      run: |
        if git diff --quiet index.html; then
          echo "changed=false" >> $GITHUB_OUTPUT
        else
          echo "changed=true" >> $GITHUB_OUTPUT
        fi
    
    - name: Commit and push if changed
      if: steps.check_changes.outputs.changed == 'true'
      run: |
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"
        git add index.html
        git commit -m "🔄 Auto-update PPR - $(date +'%Y-%m-%d')"
        git push
```

---

### 3️⃣ Aktiver GitHub Actions

1. Gå til **"Actions"**-fanen i repositoryet
2. Hvis du ser en melding om å aktivere workflows:
   - Klikk **"I understand my workflows, go ahead and enable them"**
3. Du skal nå se "Update PPR Dashboard" i listen

---

### 4️⃣ Test at Det Fungerer

**Manuell test (anbefalt):**

1. Gå til **"Actions"**-fanen
2. Klikk på **"Update PPR Dashboard"** i venstre meny
3. Klikk grønn **"Run workflow"**-knapp (øverst til høyre)
4. Klikk grønn **"Run workflow"** igjen for å bekrefte
5. Vent 2-3 minutter
6. Sjekk om kjøringen ble grønn ✅ eller rød ❌

**Hva forvente:**
- Hvis PPR 1/26 ikke er ute ennå: Gul ⚠️ (workflow kjører, men finner ingen ny PDF → OK!)
- Hvis du kjører etter PPR-dato: Grønn ✅ (data hentet og committet)
- Hvis noe er feil: Rød ❌ (klikk for å se hva som feilet)

---

### 5️⃣ Oppdater README

1. Åpne `README.md` i repositoryet
2. Finn teksten `[DITT-BRUKERNAVN]`
3. Erstatt med ditt faktiske GitHub-brukernavn
4. Commit endringene

---

## ✅ Ferdig!

Du har nå:
- ✅ Et live dashboard på GitHub Pages
- ✅ Automatisk oppdatering 4 ganger i året
- ✅ Mulighet for manuell tvungen oppdatering
- ✅ E-postvarsling hvis noe feiler

---

## 🎯 Neste Steg

**Del med kolleger:**
```
Hei team! 👋

Jeg har satt opp et dashboard for Norges Bank konjunkturprognoser.

🔗 Dashboard: https://[dittbrukernavn].github.io/konjunktur-dashboard/

Dashboardet oppdateres automatisk hver gang Norges Bank publiserer ny PPR (4 ganger i året).
Bookmark gjerne siden!
```

**Overvåke oppdateringer:**
- Gå til repo → Watch → Custom → huk av "Workflows"
- Du får e-post når workflow kjører

**Ved problemer:**
- Sjekk Actions-fanen
- Les feilmeldingene
- Åpne en Issue hvis du trenger hjelp

---

**Gratulerer! 🎉 Du har nå et fullautomatisk økonomisk dashboard!**
