# Resident sprites (Meshy 3D → plate-camera sheets)

`milo_walk_sheet.png` is Milo's walk cycle rendered from his rigged Meshy model at
the plate's three-quarter-above camera (16 frames, transparent). The compositor
draws res_milo from this sheet instead of the procedural figure.

## Regenerate a sheet
1. Export the rigged+animated model from Meshy as **glb** (Rigged Character on,
   Single file on) → place at `web/milo/<name>.glb` (git-ignored; large).
2. Vendor three.js for the headless renderer (git-ignored):
   `npm i three` → copy `three/build`→`web/vendor/three_build`, `three/examples/jsm`→`web/vendor/three_jsm`.
3. Serve `web/` and run `node tools/render_sprite.mjs` (env: `CLIP`, `N`, `FACE`, `OUT`).
   `render_sprite.html` is the three.js scene (soft matte-clay light, ortho plate camera).
4. Assemble frames → sheet (union-bbox crop, horizontal strip).
