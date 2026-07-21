#!/usr/bin/env python3
"""Sanity-check design/bible/world-coords.json against the locked bible px inputs."""
import json
wc = json.load(open('design/bible/world-coords.json'))
ann = json.load(open('design/bible/annotations.json'))
SX = 900/1024; OX, OY = 900, 100
def wu(px, py): return [round(OX+px*SX, 2), round(OY+py*SX, 2)]
fails = 0
for pl in ann['places']:
    exp = wu(*pl['px']); got = next(p['world'] for p in wc['places'] if p['n']==pl['n'])
    if exp != got: print("MISMATCH", pl['name'], exp, got); fails += 1
for k in ['loc_cafe','loc_stadium','loc_pub','loc_club_offices','loc_training_ground']:
    assert k in wc['sim_bindings'], k
print("places checked:", len(ann['places']), "| fails:", fails,
      "| sim_bindings:", len(wc['sim_bindings']))
print("OK" if fails==0 else "FAILED")
