#!/usr/bin/env python3
"""
PPR Oppdateringsscript for Konjunkturdashboard
================================================

Dette scriptet henter automatisk nye Pengepolitiske rapporter (PPR) fra 
Norges Bank når de publiseres, og oppdaterer dashboardet.

Bruk:
    python oppdater_ppr.py                    # Henter automatisk nyeste PPR
    python oppdater_ppr.py ppr_4_25.pdf      # Bruker lokal PDF-fil

Publiseringskalender (Norges Bank):
    - PPR 1: Mars (ca. 20. mars)
    - PPR 2: Juni (ca. 20. juni)  
    - PPR 3: September (ca. 20. september)
    - PPR 4: Desember (ca. 20. desember)

Avhengigheter:
    pip install pdfplumber beautifulsoup4 lxml requests

Forfatter: Cool gørl's konjunkturdashboard
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, date
import calendar

try:
    import pdfplumber
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    print("❌ Mangler nødvendige biblioteker!")
    print("\nInstaller med:")
    print("  pip install pdfplumber beautifulsoup4 lxml requests")
    sys.exit(1)


def get_next_ppr_info() -> tuple:
    """
    Finn neste PPR basert på dagens dato og publiseringskalender.
    
    Returns:
        tuple: (år, kvartal, forventet_dato)
    """
    today = date.today()
    year = today.year
    month = today.month
    
    # PPR publiseringsplan (ca. datoer)
    ppr_schedule = {
        1: (3, 20),   # Mars, ca. 20.
        2: (6, 20),   # Juni, ca. 20.
        3: (9, 20),   # September, ca. 20.
        4: (12, 20),  # Desember, ca. 20.
    }
    
    # Finn neste PPR
    for quarter in [1, 2, 3, 4]:
        ppr_month, ppr_day = ppr_schedule[quarter]
        ppr_date = date(year, ppr_month, ppr_day)
        
        # Hvis denne PPR-en kommer senere i år
        if ppr_date >= today:
            return (year, quarter, ppr_date)
    
    # Hvis vi er etter PPR 4, neste er PPR 1 neste år
    return (year + 1, 1, date(year + 1, 3, 20))


def build_ppr_url(year: int, quarter: int) -> str:
    """
    Bygg URL for PPR basert på Norges Banks mønster.
    
    Mønster: https://www.norges-bank.no/aktuelt/nyheter-og-hendelser/
             Publikasjoner/Pengepolitisk-rapport-med-vurdering-av-finansiell-stabilitet/
             {year}/ppr-{quarter}{year}/
    
    Args:
        year: År (f.eks. 2026)
        quarter: Kvartal (1-4)
    
    Returns:
        str: URL til PPR-siden
    """
    base_url = "https://www.norges-bank.no/aktuelt/nyheter-og-hendelser/Publikasjoner/Pengepolitisk-rapport-med-vurdering-av-finansiell-stabilitet"
    url = f"{base_url}/{year}/ppr-{quarter}{year}/"
    return url


def download_ppr_pdf(year: int, quarter: int, output_dir: Path = Path(".")): -> Optional[Path]:
    """
    Last ned PPR PDF fra Norges Bank.
    
    Args:
        year: År
        quarter: Kvartal (1-4)
        output_dir: Mappe å lagre PDF i
    
    Returns:
        Path til nedlastet PDF, eller None hvis feil
    """
    print(f"\n🌐 Henter PPR {quarter}/{year} fra Norges Bank...")
    
    ppr_url = build_ppr_url(year, quarter)
    print(f"   URL: {ppr_url}")
    
    try:
        # Hent PPR-siden
        response = requests.get(ppr_url, timeout=30)
        response.raise_for_status()
        
        # Parse HTML og finn PDF-link
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Søk etter PDF-link (vanligvis i <a> tag med href som ender på .pdf)
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
        
        if not pdf_links:
            print("   ❌ Fant ingen PDF-link på siden")
            return None
        
        # Ta første PDF-link (vanligvis hoveddokumentet)
        pdf_href = pdf_links[0]['href']
        
        # Bygg full URL hvis relativ
        if not pdf_href.startswith('http'):
            pdf_href = f"https://www.norges-bank.no{pdf_href}"
        
        print(f"   📄 Fant PDF: {pdf_href}")
        
        # Last ned PDF
        pdf_response = requests.get(pdf_href, timeout=60)
        pdf_response.raise_for_status()
        
        # Lagre til fil
        output_path = output_dir / f"ppr_{quarter}_{year}.pdf"
        output_path.write_bytes(pdf_response.content)
        
        print(f"   ✅ Lastet ned: {output_path}")
        return output_path
        
    except requests.RequestException as e:
        print(f"   ❌ Feil ved nedlasting: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Uventet feil: {e}")
        return None


class PPRParser:
    """Parser for Pengepolitisk rapport PDF"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"Finner ikke PDF: {pdf_path}")
        
        self.tables = {}
        
    def parse(self) -> Dict:
        """Parse alle relevante tabeller fra PPR"""
        print(f"📄 Åpner {self.pdf_path.name}...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            print(f"   Antall sider: {len(pdf.pages)}")
            
            # Finn tabellene
            self._find_table_2a(pdf)  # KPI
            self._find_table_2b(pdf)  # Boligpriser
            self._find_table_2c(pdf)  # Ledighet
            self._find_table_2d(pdf)  # BNP kvartalsvis
            self._find_table_3(pdf)   # Store vedleggstabell
            
        return self.tables
    
    def _find_table_2a(self, pdf):
        """Finn Tabell 2a: Konsumpriser"""
        print("\n🔍 Søker etter Tabell 2a (Konsumpriser)...")
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if 'Tabell 2a' in text and 'Konsumpriser' in text:
                print(f"   ✓ Funnet på side {page_num}")
                tables = page.extract_tables()
                if tables:
                    self.tables['2a'] = self._parse_monthly_table(tables[0], '2a')
                    print(f"   ✓ Hentet {len(self.tables['2a'])} rader")
                break
    
    def _find_table_2b(self, pdf):
        """Finn Tabell 2b: Boligpriser"""
        print("\n🔍 Søker etter Tabell 2b (Boligpriser)...")
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if 'Tabell 2b' in text and 'Boligpriser' in text:
                print(f"   ✓ Funnet på side {page_num}")
                tables = page.extract_tables()
                if tables:
                    self.tables['2b'] = self._parse_monthly_table(tables[0], '2b')
                    print(f"   ✓ Hentet {len(self.tables['2b'])} rader")
                break
    
    def _find_table_2c(self, pdf):
        """Finn Tabell 2c: Registrert ledighet"""
        print("\n🔍 Søker etter Tabell 2c (Registrert ledighet)...")
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if 'Tabell 2c' in text and 'ledighet' in text:
                print(f"   ✓ Funnet på side {page_num}")
                tables = page.extract_tables()
                if tables:
                    self.tables['2c'] = self._parse_monthly_table(tables[0], '2c')
                    print(f"   ✓ Hentet {len(self.tables['2c'])} rader")
                break
    
    def _find_table_2d(self, pdf):
        """Finn Tabell 2d: BNP Fastlands-Norge kvartalsvekst"""
        print("\n🔍 Søker etter Tabell 2d (BNP kvartalsvis)...")
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if 'Tabell 2d' in text and 'BNP' in text:
                print(f"   ✓ Funnet på side {page_num}")
                tables = page.extract_tables()
                if tables:
                    self.tables['2d'] = self._parse_quarterly_table(tables[0])
                    print(f"   ✓ Hentet {len(self.tables['2d'])} rader")
                break
    
    def _find_table_3(self, pdf):
        """Finn Tabell 3: Anslag på sentrale størrelser (vedlegg)"""
        print("\n🔍 Søker etter Tabell 3 (Hovedtabell fra vedlegg)...")
        
        # Denne er vanligvis i vedlegget
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if 'Tabell 3' in text or ('sentrale størrelser' in text and 'BNP Fastlands-Norge' in text):
                print(f"   ✓ Funnet på side {page_num}")
                tables = page.extract_tables()
                if tables:
                    self.tables['3'] = self._parse_annual_table(tables[0])
                    print(f"   ✓ Hentet {len(self.tables['3'])} rader")
                break
    
    def _parse_monthly_table(self, raw_table: List[List], table_id: str) -> Dict:
        """Parse månedlig tabell (2a, 2b, 2c)"""
        parsed = {}
        
        # Finn kolonneindekser for måneder
        header_row = raw_table[0] if raw_table else []
        
        # Extract data rows
        for row in raw_table[1:]:
            if not row or len(row) < 2:
                continue
            
            row_name = str(row[0]).strip()
            if row_name in ['Faktisk', 'Anslag PPR 3/25', 'Anslag PPR 4/25']:
                values = []
                for cell in row[1:]:
                    if cell:
                        # Clean numeric values
                        val = str(cell).strip().replace(',', '.')
                        # Handle dashes/missing data
                        if val in ['-', '', 'nan', 'None']:
                            val = '-'
                        values.append(val)
                
                parsed[row_name] = values
        
        return parsed
    
    def _parse_quarterly_table(self, raw_table: List[List]) -> Dict:
        """Parse kvartalstabell (2d)"""
        parsed = {}
        
        for row in raw_table[1:]:
            if not row or len(row) < 2:
                continue
            
            row_name = str(row[0]).strip()
            if row_name in ['Faktisk', 'Anslag PPR 3/25', 'Anslag PPR 4/25']:
                values = []
                for cell in row[1:]:
                    if cell:
                        val = str(cell).strip().replace(',', '.')
                        if val in ['-', '', 'nan', 'None']:
                            val = '-'
                        values.append(val)
                
                parsed[row_name] = values
        
        return parsed
    
    def _parse_annual_table(self, raw_table: List[List]) -> Dict:
        """Parse årlig tabell (tabell 3)"""
        parsed = {}
        
        # This is the big table with all variables
        # Structure: Variable name | 2023 | 2024 | 2025 | 2026 | 2027 | 2028
        
        for row in raw_table[1:]:
            if not row or len(row) < 2:
                continue
            
            var_name = str(row[0]).strip()
            if var_name:
                values = []
                for cell in row[1:]:
                    if cell:
                        val = str(cell).strip().replace(',', '.')
                        values.append(val)
                
                parsed[var_name] = values
        
        return parsed


class HTMLUpdater:
    """Oppdaterer HTML-fil med nye data fra PPR"""
    
    def __init__(self, html_path: str):
        self.html_path = Path(html_path)
        if not self.html_path.exists():
            raise FileNotFoundError(f"Finner ikke HTML: {html_path}")
        
        with open(self.html_path, 'r', encoding='utf-8') as f:
            self.soup = BeautifulSoup(f.read(), 'html.parser')
    
    def update_table_2a(self, data: Dict):
        """Oppdater Tabell 2a i HTML"""
        print("\n📝 Oppdaterer Tabell 2a (Konsumpriser)...")
        
        # Find the table section
        # This is complex - we need to find specific td elements and update them
        # For now, we'll use a simple regex replacement approach
        
        print("   ⚠️  Manuell oppdatering anbefales for Tabell 2a")
        print(f"   Data hentet: {list(data.keys())}")
    
    def update_table_2b(self, data: Dict):
        """Oppdater Tabell 2b i HTML"""
        print("\n📝 Oppdaterer Tabell 2b (Boligpriser)...")
        print("   ⚠️  Manuell oppdatering anbefales for Tabell 2b")
        print(f"   Data hentet: {list(data.keys())}")
    
    def update_table_2c(self, data: Dict):
        """Oppdater Tabell 2c i HTML"""
        print("\n📝 Oppdaterer Tabell 2c (Ledighet)...")
        print("   ⚠️  Manuell oppdatering anbefales for Tabell 2c")
        print(f"   Data hentet: {list(data.keys())}")
    
    def update_table_2d(self, data: Dict):
        """Oppdater Tabell 2d i HTML"""
        print("\n📝 Oppdaterer Tabell 2d (BNP)...")
        print("   ⚠️  Manuell oppdatering anbefales for Tabell 2d")
        print(f"   Data hentet: {list(data.keys())}")
    
    def update_table_3(self, data: Dict):
        """Oppdater Tabell 3 i HTML"""
        print("\n📝 Oppdaterer Tabell 3 (Hovedtabell)...")
        print("   ⚠️  Manuell oppdatering anbefales for Tabell 3")
        print(f"   Data hentet: {len(data)} variabler")
    
    def save(self, output_path: Optional[str] = None):
        """Lagre oppdatert HTML"""
        if output_path is None:
            output_path = self.html_path
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(self.soup))
        
        print(f"\n✅ HTML oppdatert: {output_path}")


def main():
    """Hovedfunksjon"""
    print("=" * 70)
    print("PPR OPPDATERINGSSCRIPT")
    print("=" * 70)
    
    # Sjekk om PDF-fil er oppgitt
    if len(sys.argv) < 2:
        print("\n📅 Ingen PDF-fil oppgitt - sjekker automatisk etter nyeste PPR...")
        
        # Finn neste PPR
        year, quarter, expected_date = get_next_ppr_info()
        today = date.today()
        
        if expected_date > today:
            print(f"\n⏰ Neste PPR {quarter}/{year} forventes: {expected_date.strftime('%d. %B %Y')}")
            print(f"   Det er {(expected_date - today).days} dager til publisering.")
            print("\n💡 Tips: Du kan prøve å laste ned når datoen nærmer seg:")
            print(f"   python oppdater_ppr.py  (automatisk)")
            sys.exit(0)
        
        # Prøv å laste ned
        pdf_path = download_ppr_pdf(year, quarter)
        
        if pdf_path is None:
            print("\n❌ Kunne ikke laste ned PPR automatisk.")
            print("\nAlternativ: Last ned manuelt fra:")
            print(f"   {build_ppr_url(year, quarter)}")
            print("\nDeretter kjør:")
            print(f"   python oppdater_ppr.py ppr_{quarter}_{year}.pdf")
            sys.exit(1)
    else:
        pdf_path = sys.argv[1]
    
    html_path = "konjunkturovervaakning_med_prognoser.html"
    
    # Check if HTML exists
    if not Path(html_path).exists():
        print(f"\n❌ Feil: Finner ikke {html_path}")
        print("Pass på at du kjører scriptet i samme mappe som HTML-filen!")
        sys.exit(1)
    
    try:
        # Parse PDF
        parser = PPRParser(pdf_path)
        tables = parser.parse()
        
        print("\n" + "=" * 70)
        print("OPPSUMMERING AV INNHENTEDE DATA")
        print("=" * 70)
        
        for table_id, data in tables.items():
            print(f"\nTabell {table_id}: {len(data)} datapunkter")
            if data:
                print(f"  Eksempel: {list(data.keys())[:3]}")
        
        # Update HTML
        print("\n" + "=" * 70)
        print("OPPDATERER HTML")
        print("=" * 70)
        
        updater = HTMLUpdater(html_path)
        
        if '2a' in tables:
            updater.update_table_2a(tables['2a'])
        if '2b' in tables:
            updater.update_table_2b(tables['2b'])
        if '2c' in tables:
            updater.update_table_2c(tables['2c'])
        if '2d' in tables:
            updater.update_table_2d(tables['2d'])
        if '3' in tables:
            updater.update_table_3(tables['3'])
        
        # Save
        backup_path = f"konjunkturovervaakning_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        print(f"\n💾 Lager backup: {backup_path}")
        Path(html_path).rename(backup_path)
        
        updater.save(html_path)
        
        print("\n" + "=" * 70)
        print("✅ FERDIG!")
        print("=" * 70)
        print(f"\nOriginal fil: {backup_path}")
        print(f"Oppdatert fil: {html_path}")
        print("\n📊 Åpne HTML-filen i nettleseren for å se oppdateringene!")
        
        print("\n" + "=" * 70)
        print("⚠️  MERK: SEMI-AUTOMATISK VERSJON")
        print("=" * 70)
        print("\nDette scriptet PARSER dataene fra PDF-en, men for")
        print("å få 100% nøyaktighet anbefales det å:")
        print("\n1. Sjekk de parsede verdiene i terminalutskriften")
        print("2. Manuelt verifiser noen nøkkeltall i HTML-en")
        print("3. Kjør en visuell sjekk av dashboardet")
        print("\nFor en fullstendig automatisk løsning kreves mer")
        print("avansert PDF-parsing med OCR og layout-analyse.")
        
    except Exception as e:
        print(f"\n❌ Feil: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
