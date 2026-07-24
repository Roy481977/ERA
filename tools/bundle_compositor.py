#!/usr/bin/env python3
"""Bundle the plate compositor into one self-contained HTML (offline, no server):
inlines the replay, the plate-map (v2), the graded plate + sprite sheets (base64),
and compositor.js. Owl flight + real-speed movers included.
Usage: python3 tools/bundle_compositor.py [out.html]"""
import base64, pathlib, sys

web = pathlib.Path(__file__).resolve().parent.parent / "web"
out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("/tmp/ERA-living-plate.html")

def b64(p): return base64.b64encode((web / p).read_bytes()).decode()

html = (web / "compositor.html").read_text()
js = (web / "compositor.js").read_text()
replay = (web / "assets/replay.json").read_text()
mp = (web / "assets/era-plate-map-v2.json").read_text()
plate_b64 = b64("assets/plate-v2.jpeg")
milo_b64 = b64("milo/milo_walk_sheet.png")
owl = {k: b64(f"owl/owl_{k}_sheet.png") for k in ("perch", "takeoff", "soar", "land")}
animals = {f"ani_{n}": b64(f"animals/{n}_walk_sheet.png") for n in ("fox", "tabby", "blackcat")}

owl_js = ",".join(f'{k}:"data:image/png;base64,{v}"' for k, v in owl.items())
ani_js = ",".join(f'{k}:"data:image/png;base64,{v}"' for k, v in animals.items())
inline = ('<script>window.__INLINE={replay:' + replay + ',map:' + mp +
          ',plate:"data:image/jpeg;base64,' + plate_b64 + '"' +
          ',miloSheet:"data:image/png;base64,' + milo_b64 + '"' +
          ',owl:{' + owl_js + '}' +
          ',animals:{' + ani_js + '}};</script>\n')
html = html.replace('<script src="compositor.js"></script>',
                    inline + "<script>\n" + js + "\n</script>")
out.write_text(html)
print(f"standalone: {out} ({out.stat().st_size/1e6:.1f} MB)")
