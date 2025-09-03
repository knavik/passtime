# 🛂 Pass-timevarsler

Et lite Python-skript som sjekker jevnlig etter nye ledige passtimer hos Politiet.  
Du kan velge **lokasjon**, **tjeneste** og et **datointervall** (fra–til).  
Dersom nye timer åpnes i det valgte intervallet, får du varsel – enten på e-post eller i terminalen.  

---

## 🚀 Funksjoner
- Henter **alle lokasjoner** (politistasjoner) og tjenester (pass, ID-kort osv.) fra Politiets API.  
- Brukeren velger selv hvilken stasjon og hvilken tjeneste det skal overvåkes på.  
- Overvåker **datointervall** (fra dato → til dato).  
- Varsler om nye timer dukker opp i intervallet.  
- Sender e-postvarsler dersom e-post er konfigurert, ellers kun utskrift til terminal.  
- Email/secrets gjennom `.env`-fil (ikke hardkodet i skriptet).  
---

## 📦 Forutsetninger
- Python 3.8 eller nyere  
- Installer avhengigheter:  
  ```bash
  pip install -r requirements.txt

## ⚙️ Konfigurasjon

Kopier .env.example til .env:

cp .env.example .env


Rediger .env og legg inn opplysninger dersom du vil bruke e-postvarsler:

EMAIL_USER=din.email@gmail.com

EMAIL_PASS=app-passord-fra-gmail

EMAIL_RECEIVER=mottaker.email@gmail.com


Hvis du lar disse stå tomme, kjører skriptet uten e-postvarsler.