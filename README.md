# FocusFlow

Aplikacja do nauki, która pomaga nie wypaść z flow, gdy utkniesz na trudnym temacie.


**Dostępna online:** [focusflow.jellytyan.de](http://focusflow.jellytyan.de/)


## Problem

Siedzisz do nauki, włączasz timer, a po 5 minutach trafiasz na coś, czego nie rozumiesz. Zamiast kontynuować, otwierasz Google, potem przypadkiem TikToka, i nagle minęło 20 minut. Sesja zmarnowana.

FocusFlow rozwiązuje to inaczej - zamiast uciekać z aplikacji, dostajesz pomoc AI bezpośrednio w trakcie nauki. Timer dalej działa, a ty szybko wracasz do tematu.

## Jak to działa

Tworzysz projekt (np. "Egzamin z Biologii"), dodajesz tematy, klikasz Play i zaczynasz 25-minutową sesję Pomodoro. Gdy utkniesz, klikasz "🤯 Utknąłem" - z boku wyjeżdża chat z AI, które już wie, nad jakim tematem pracujesz. Timer dalej działa, dostajesz odpowiedź w 30 sekund i wracasz do nauki.

Kluczowe jest to, że timer się nie zatrzymuje - to zmienia psychologię. Nie masz wymówki, żeby wyjść z aplikacji, bo wszystko masz w jednym miejscu.

## Co jest w środku

**Zarządzanie projektami** - tworzysz projekt, dodajesz tematy, ustawiasz deadline. Aplikacja sama priorytetyzuje tematy na podstawie tego, jak blisko deadline i jak niska jest twoja pewność co do tematu.

**Timer Pomodoro** - 25 minut, minimalistyczny interfejs, lo-fi w tle. Przycisk "🤯 Utknąłem" zawsze pod ręką.

**Chat z AI** - wyjeżdża z boku, nie zasłania timera. AI wie, nad jakim tematem pracujesz, więc nie musisz tłumaczyć kontekstu. Historia jest zapisywana.

**Statystyki** - widzisz, ile sesji ukończyłeś, w jakich tematach najczęściej utykasz, i postęp w projekcie.

## Design

Minimalistyczny, ciemny interfejs z gradientami i efektami glassmorphism. Timer jest duży i czytelny, wszystko inne jest na drugim planie. Chat wyjeżdża z boku, nie przeszkadzając w fokusie.

Paleta: ciemne tło, gradienty fioletowo-niebieskie, zielony dla sukcesu, pomarańczowy dla ostrzeżeń. Czcionka monospace dla timera, Inter dla reszty.

## Co dalej

Pomysły na przyszłość: powtórki interwałowe dla tematów, w których często utykasz, voice-to-setup do szybkiego tworzenia planów głosem, wspólne sesje z przyjaciółmi. Na razie skupiamy się na MVP.

## Tech stack

- Frontend: Vue 3 + TypeScript + Tailwind
- Backend: FastAPI (Python)
- AI: ChatGPT 5 Mini
- Baza danych: MySQL (można też SQLite dla dev)

## Jak uruchomić

Backend:
```bash
cd backend
pip install -r requirements.txt
./start-backend.sh
```

Frontend:
```bash
cd frontend
npm install
./start-frontend.sh
```

Lub użyj docker-compose:
```bash
docker-compose up
```

## Struktura

```
FocusFlow/
├── frontend/     # Vue app
├── backend/      # FastAPI
└── docker-compose.yml
```

Backend ma standardową strukturę FastAPI: `routers/`, `services/`, `database/`, `models/`. Frontend używa Pinia do state management i Vue Router.

---

FocusFlow powstał z frustracji - ile razy siadałem do nauki i kończyło się na TikToku. Teraz mam wszystko w jednym miejscu, timer nie przerywa się, a AI pomaga bez wychodzenia z aplikacji. 
