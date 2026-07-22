#!/usr/bin/env python3
"""Bundle the plate compositor into one self-contained HTML (offline, no server):
inlines the replay, the plate-map, the graded plate (base64), and compositor.js.
Usage: python3 tools/bundle_compositor.py [out.html]"""
import base64, pathlib, sys

web = pathlib.Path(__file__).resolve().parent.parent / "web"
out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("/tmp/ERA-living-plate.html")

html = (web / "compositor.html").read_text()
js = (web / "compositor.js").read_text()
replay = (web / "assets/replay.json").read_text()
mp = (web / "assets/era-plate-map.json").read_text()
plate_b64 = base64.b64encode((web / "assets/plate-v1-graded.jpeg").read_bytes()).decode()
occ_b64 = base64.b64encode((web / "assets/occluder.png").read_bytes()).decode()

inline = ('<script>window.__INLINE={replay:' + replay + ',map:' + mp +
          ',plate:"data:image/jpeg;base64,' + plate_b64 + '"' +
          ',occluder:"data:image/png;base64,' + occ_b64 + '"};</script>\n')
html = html.replace('<script src="compositor.js"></script>',
                    inline + "<script>\n" + js + "\n</script>")
out.write_text(html)
print(f"standalone: {out} ({out.stat().st_size/1e6:.1f} MB)")
