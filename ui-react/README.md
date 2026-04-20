# alpha-autopilot React UI

React + Vite version of the novel recommendation quant dashboard.

## Run

```bash
npm install
npm run dev
```

## API integration

By default the UI calls `http://127.0.0.1:8000/api/dashboard`.
You can override it with `VITE_API_BASE_URL`.

## Build

```bash
npm run build
```

## Structure

- `src/App.tsx` - shell composition and API fallback logic
- `src/api.ts` - dashboard API contract
- `src/data.ts` - local fallback data
- `src/components/*` - panelized UI sections
- `src/styles.css` - visual system
