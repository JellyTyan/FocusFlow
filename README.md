# FocusFlow

**Zintegrowane środowisko do produktywnej nauki, które nie pozwala wypaść z flow**

## 🎯 Problem

Zoomers siadają do nauki, włączają timer, ale na 5. minucie napotykają niezrozumiały temat. Pojawia się frustracja → otwiera się Google → pojawia się powiadomienie w Telegramie → "na sekundę" wchodzą na TikToka → 20 minut stracone.

**Sesja fokusowa nieudana. Flow przerwane.**

## 💡 Rozwiązanie: "Pętla Fokusowa"

FocusFlow wychwytuje moment frustracji i zapobiega ucieczce z aplikacji. Zamiast uciekać do Google (gdzie czeka 1000 rozpraszaczy), użytkownik otrzymuje natychmiastową pomoc bezpośrednio w trakcie nauki.

### Jak to działa

1. **Prosty setup**: Tworzysz projekt (np. "Egzamin z Biologii"), dodajesz tematy tekstem
2. **Estetyczny timer**: Klikasz Play → uruchamia się minimalistyczny Pomodoro (25 min) z atmosferą Lo-Fi
3. **Przycisk "🤯 Utknąłem"**: Bezpośrednio na ekranie timera (który się nie zatrzymuje!)
4. **Kontekstowy asystent AI**: Wyjeżdża chat z boku, AI już zna Twój temat i jest gotowe pomóc
5. **Powrót do flow**: Otrzymałeś odpowiedź w 30 sekund → zamknąłeś chat → kontynuujesz naukę

## 🚀 Kluczowe funkcje

- **Nie przerywa flow**: Timer nadal działa, gdy rozmawiasz z AI
- **Kontekstowa pomoc**: AI wie, nad jakim tematem pracujesz
- **Szybciej niż Google**: Jeden przycisk zamiast odblokowywania telefonu i wyszukiwania
- **Psychologiczny trick**: Uznajemy frustrację i dajemy "wyjście awaryjne"

## 📋 Scenariusz użycia

**PRZED (bez FocusFlow):**
```
Siadłem do nauki → Utknąłem → Zdenerwowałem się → Otworzyłem TikToka → Sesja nieudana
```

**PO (z FocusFlow):**
```
Siadłem do nauki → Utknąłem → Kliknąłem "Utknąłem" → Otrzymałem odpowiedź od AI → Kontynuuję naukę
```

## 📦 Funkcjonalność MVP

### 1. Zarządzanie projektami
- Tworzenie projektu (nazwa, przedmiot, deadline)
- Dodawanie tematów do nauki
- Ocena pewności dla każdego tematu (1-5 gwiazdek)
- Automatyczna priorytetyzacja na podstawie:
  - Bliskości deadline'u
  - Poziomu pewności (niska pewność = wysoki priorytet)
  - Formuła: `priorytet = (dni do deadline'u)^-1 × (6 - poziom pewności)`

### 2. Timer fokusowy
- Pomodoro 25 minut
- Minimalistyczny interfejs pełnoekranowy
- Płynne animacje i gradienty
- Muzyka/dźwięki w tle (opcjonalnie)
- Przycisk "🤯 Utknąłem" zawsze widoczny

### 3. Asystent AI
- Kontekstowy chat (zna aktualny temat)
- Otwiera się z boku, nie zasłaniając timera
- Pierwsza wiadomość od AI automatycznie
- Historia dialogu jest zapisywana
- Integracja z Google Gemini / OpenAI

### 4. Statystyki
- Liczba ukończonych sesji
- Tematy, w których najczęściej utknąłeś
- Postęp w projekcie

## 🎨 Koncepcja designu

### Styl: Minimalizm + estetyka Gen Z

**Paleta kolorów:**
- Podstawowy: Ciemne tło (#1a1a2e, #16213e)
- Akcent: Gradienty (fioletowy → niebieski, #6a5acd → #4169e1)
- Tekst: Biały/jasnoszary (#f0f0f0)
- Sukces: Miękka zieleń (#4ade80)
- Ostrzeżenie: Ciepły pomarańczowy (#fb923c)

**Typografia:**
- Nagłówki: Inter / Poppins (pogrubione, 24-48px)
- Tekst: Inter / SF Pro (zwykły, 14-16px)
- Timer: Czcionka monospace (72-96px)

**Elementy UI:**
- Zaokrąglone rogi (border-radius: 16-24px)
- Efekty glassmorphism (backdrop-blur)
- Płynne cienie (box-shadow z rozmyciem)
- Animacje na hover (transform: scale(1.05))

### Ekrany

**1. Strona główna**
```
┌─────────────────────────────────────┐
│  FocusFlow                    [+]   │
├─────────────────────────────────────┤
│  📚 Egzamin z Biologii              │
│  Deadline: 15 maja • 3 tematy       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━ 60%   │
│                                     │
│  🔥 Tematy priorytetowe:            │
│  • Fotosynteza ⭐⭐☆☆☆ [Play ▶]    │
│  • Mitoza ⭐⭐⭐☆☆ [Play ▶]         │
└─────────────────────────────────────┘
```

**2. Ekran timera**
```
┌─────────────────────────────────────┐
│                                     │
│         Fotosynteza                 │
│                                     │
│           24:35                     │
│                                     │
│      [🤯 Utknąłem]                  │
│                                     │
│      [⏸ Pauza]  [⏹ Stop]           │
└─────────────────────────────────────┘
```

**3. Timer + chat AI**
```
┌──────────────────┬──────────────────┐
│                  │ 💬 Asystent AI   │
│   Fotosynteza    ├──────────────────┤
│                  │ 🤖: Widzę, że    │
│      24:35       │ pracujesz nad    │
│                  │ tematem "Foto-   │
│  [🤯 Utknąłem]   │ synteza". Co     │
│                  │ niejasne?        │
│  [⏸]  [⏹]       │                  │
│                  │ 👤: Czym jest    │
│                  │ cykl Calvina?    │
│                  │                  │
│                  │ 🤖: Cykl Cal-    │
│                  │ vina to...       │
│                  │                  │
│                  │ [Wyślij]     [×] │
└──────────────────┴──────────────────┘
```

## 🔮 Przyszły rozwój

- **Powtórki interwałowe**: System śledzi tematy, w których użytkownik często utyka, i dodaje je do kolejki powtórek
- **Multimodalność**: Voice-to-Setup do szybkiego tworzenia planów nauki głosem
- **Rozszerzona nauka z AI**: Podstawowa nauka tematów teoretycznych z interaktywnymi wyjaśnieniami
- **Funkcje społecznościowe**: Wspólne sesje z przyjaciółmi
- **Gamifikacja**: Osiągnięcia, streak'i, poziomy

## 🛠 Technologie

- **Frontend**: React + TypeScript
- **Backend**: FastAPI (Python)
- **AI**: Google Gemini / OpenAI API

## 📁 Struktura projektu

```
FocusFlow/
├── frontend/          # Aplikacja React
├── backend/           # Serwer FastAPI
├── start-frontend.sh  # Uruchomienie frontendu
└── start-backend.sh   # Uruchomienie backendu
```

## 🚀 Uruchomienie

### Backend (port 8000)
```bash
./start-backend.sh
```

### Frontend (port 3000)
```bash
./start-frontend.sh
```

## 📡 API

- `GET /` - Strona główna API
- `GET /api/health` - Sprawdzenie stanu serwera

---

**FocusFlow** — zabezpieczenie przed prokrastynacją, które zastępuje destrukcyjny wzorzec (ucieczka na TikToka) konstruktywnym (rozwiązanie problemu z AI).
