# Scam Shield for Elders — Frontend

The React and Vite frontend checks SMS and WhatsApp text with the FastAPI
backend. Results include a risk verdict, matched reasons, and explanations in
English, Hindi, or Kannada.

## Run locally

Start the backend separately from the `backend/` directory:

```powershell
python -m uvicorn main:app --reload
```

In another terminal, open this `frontend/` directory and run:

```powershell
npm install
npm run dev
```

Open the local address printed by Vite (normally
`http://localhost:5173`). The frontend sends checks to
`http://127.0.0.1:8000` by default.

To use a different backend URL, copy `.env.example` to `.env.local`, set
`VITE_API_URL` to the backend origin, then restart Vite:

```text
VITE_API_URL=http://127.0.0.1:8000
```

The backend must allow the frontend's exact origin through its CORS settings.

## Production build

```powershell
npm run build
```

The built static site is written to `dist/`. Submitted messages are held only
in the page while checking; the frontend does not save a message history.
