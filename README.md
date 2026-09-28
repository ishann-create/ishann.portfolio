# Ishan Mondal — Portfolio

Personal portfolio for Ishan Mondal (frontend, UI/UX and data for D2C brands). Dark retro-future visual style, inspired by the design of ohsh.in.

## Run locally

```bash
python server.py     # opens on http://localhost:3000
```

## Edit your content

- `index_data.json` — hero, bio paragraphs, Spotify playlists, books, social links (home page)
- `work_data.json` — projects, reach-out channels, tech stack, experience, social links (work page)
- `profile.png` — replace with your photo (portrait, ~900x1100)

After editing a JSON file, also paste the same JSON into the `window.__remixContext = ...` line of the matching HTML (`index.html` / `work.html`, and `work/index.html`), or the page will render the old data first.

## Static hosting

`assets/static-loader-shim.js` is loaded first in `index.html`, `work.html` and `work/index.html`. It answers Remix's `?_data=routes/...` loader requests from `index_data.json` / `work_data.json`, so client-side navigation (e.g. `/work` -> `/#about`) works on static hosts that have no `server.py`. Keep it before the Remix entry script.
