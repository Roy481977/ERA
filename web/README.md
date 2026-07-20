# ERA — the live web client

Each visitor runs their **own copy** of ERA: the deterministic Rust engine is
compiled to WebAssembly and ticks live in the browser tab, and this client
(`index.html` + `era.js`) reads its behaviour state every frame and draws it —
the same behaviour vocabulary as the desktop viewer (facing, poses, staged
conversations, the follow-and-zoom camera), but running live rather than from a
recording.

## It's hosted for you — nothing to run

On every push to `main`, GitHub Actions (`.github/workflows/pages.yml`) builds the
engine to WebAssembly on GitHub's servers and publishes this folder to **GitHub
Pages**. You just open the URL:

```
https://roy481977.github.io/ERA/
```

No terminal, no local build. When we improve ERA, the push rebuilds the site and
the URL updates — refresh to see it.

### One-time setup (a few clicks, no terminal)

The workflow tries to enable Pages automatically. If the site doesn't appear, in
the repo on github.com go to **Settings → Pages → Build and deployment → Source**
and choose **GitHub Actions**. (GitHub Pages is free for public repositories; a
private repo needs GitHub Pro.) Then **Actions** tab shows each build; the green
"Deploy ERA to GitHub Pages" run publishes the URL.

## Deploying anywhere else

The built site is just static files — `index.html`, `era.js`, and the `pkg/`
folder wasm-pack produces. Any static host (Netlify, Vercel, S3, an app shell)
serves it identically; that's the "same result online later" with no changes.

## Building it yourself (optional)

Not required — CI does this. But if ever wanted:

```
rustup target add wasm32-unknown-unknown
cargo install wasm-pack
wasm-pack build development/sprint-1 --release --target web --out-dir ../../web/pkg --features wasm
# then serve the web/ folder with any static server and open it
```
