#!/usr/bin/env python3
"""
ERA — roster -> Krea prompts compiler.

The "single biggest lever" from residents-production-pipeline.md: turn the sim's
cast data into ready, on-style Krea design prompts instead of hand-writing each.
Deterministic: same roster in -> same prompts out (no randomness, stable order).

Stage 1 of the funnel only (the Krea 2D clay reference). Stage 2 (Meshy image->3D
-> texture Remove-Lighting-OFF -> remesh 10K -> rig -> retarget shared motion
library -> sprite sheets) consumes the reference this produces; this script also
records, per subject, the Meshy body-archetype so the rig target is unambiguous.

The style recipe is the one PROVEN on Hana (baker) and Milo (busker), captured in
residents-track-progress.md:
  Krea tool "Nano Banana 2 Lite", 1376x768, text-only, gentle faces/features,
  matte clay + felt, one soft warm sun upper-right, 3/4-from-above, plain
  warm-grey studio background, sharp focus, no blur, no text.

Usage:
  python3 tools/roster_to_prompts.py animals      # emit the 7 animals
  python3 tools/roster_to_prompts.py animals --md  # markdown sheet to stdout
"""

import sys
import json

# ---------------------------------------------------------------------------
# The locked clay-diorama style law (shared preamble). Adapted per body plan
# (human vs animal) but the material/light/camera/background law is identical,
# so every subject reads as part of the same handmade miniature as the plate.
# ---------------------------------------------------------------------------

STYLE_MATERIAL = (
    "Matte sculpted clay and felt materials, smooth matte surface, tiny handmade "
    "imperfections, soft rounded edges, no hard outlines"
)
STYLE_LIGHT = (
    "one soft warm sun from the upper-right, gentle soft shadow and ambient occlusion"
)
STYLE_CAMERA = (
    "three-quarter view from slightly above, like a scale-model figurine on a table"
)
STYLE_BG = (
    "plain neutral warm-grey studio background, sharp focus, no depth of field, "
    "no blur, no text"
)

# Krea settings proven on Hana/Milo (Stage 1).
KREA = {
    "tool": "Nano Banana 2 Lite",
    "size": "1376x768 (aspect 455:256)",
    "mode": "text-only",
    "note": "one locked reference per subject; reference-lock later gens to stay on-model",
}

# Meshy body-archetype taxonomy (the six shared rigs) -> the animal's rig target.
# From residents-production-pipeline.md. Stage-2 rig target, recorded now so the
# design pose is authored rig-friendly.
ARCHETYPE = {
    "quadruped-mid": "quad rig (trot, run, sit, lie, sniff, startle)",
    "bird-small":    "wings rig (perch, hop, take-off, fly-loop)",
    "wader":         "long-legs rig (wade, stand, stab, take-off)",
    "small-ground":  "tiny-quad rig (shuffle, curl, forage)",
}

# ---------------------------------------------------------------------------
# ANIMAL ROSTER — mirrors development/sprint-1/src/sim/wildlife.rs::cast().
# id / name / species / color are copied verbatim from the sim so the design and
# the behaviour-stream `color` agree. `design` fields are the clay-figurine
# identity compiled for Krea; `pose` is a neutral, rig-friendly stance.
# ---------------------------------------------------------------------------

ANIMALS = [
    {
        "id": "ani_fox", "name": "the riverside fox", "species": "fox",
        "color": "#c1502e", "archetype": "quadruped-mid",
        "descriptor": "a slender wild fox",
        "coat": "rusty red-orange clay coat, cream chest and throat, dark "
                "stocking legs, a full brush tail carried level with a soft "
                "cream tip, large upright triangular ears, a fine pointed snout",
        "pose": "standing four-square in a neutral alert stance, head slightly "
                "turned, full body and all four legs clearly visible",
        "palette": "rust, cream, and soft charcoal",
    },
    {
        "id": "ani_tabby", "name": "the bakery cat", "species": "cat",
        "color": "#b0895f", "archetype": "quadruped-mid",
        "descriptor": "a plump, confident house cat",
        "coat": "warm sandy-brown tabby clay coat with soft darker stripes, a "
                "pale cream belly, a rounded face and cheeks, an upright curled "
                "tail, small rounded ears",
        "pose": "standing four-square in a calm neutral stance, tail up, full "
                "body and all four legs clearly visible",
        "palette": "sandy brown, cream, and warm ochre",
    },
    {
        "id": "ani_blackcat", "name": "the black cat", "species": "cat",
        "color": "#4b4b52", "archetype": "quadruped-mid",
        "descriptor": "a sleek, slim house cat",
        "coat": "soft charcoal-black clay coat with a faint cool sheen, a slim "
                "build, a neat narrow face, tall pointed ears, a long slender "
                "upright tail, a hint of pale green eyes",
        "pose": "standing four-square in a poised neutral stance, full body and "
                "all four legs clearly visible",
        "palette": "charcoal black with cool grey highlights",
    },
    {
        "id": "ani_owl", "name": "the church owl", "species": "owl",
        "color": "#d9c9a3", "archetype": "bird-small",
        "descriptor": "a small, shy tawny owl",
        "coat": "soft pale-tawny clay plumage mottled with cream and warm brown, "
                "a broad round facial disc, large gentle dark eyes, folded rounded "
                "wings, small feathered feet",
        "pose": "perched upright and facing forward in a neutral compact stance, "
                "wings folded, full body and feet visible",
        "palette": "pale tawny, cream, and warm brown",
    },
    {
        "id": "ani_heron", "name": "the grey heron", "species": "heron",
        "color": "#7f8fa0", "archetype": "wader",
        "descriptor": "a tall, still grey heron",
        "coat": "cool blue-grey clay plumage, a white head with a fine black eye-"
                "stripe and a slender trailing crest plume, a long S-curved neck, "
                "a long straight dagger bill, very long thin legs",
        "pose": "standing tall on both long legs in a neutral upright stance, neck "
                "gently folded, full body, bill and both legs clearly visible",
        "palette": "blue-grey, white, and soft slate",
    },
    {
        "id": "ani_crows", "name": "the museum crows", "species": "crow",
        "color": "#2e2e33", "archetype": "bird-small",
        "descriptor": "a glossy black crow",
        "coat": "deep glossy blue-black clay plumage, a stout heavy bill, a "
                "compact rounded body, sturdy dark feet, a knowing sideways eye",
        "pose": "standing upright on both feet in a neutral alert stance, wings "
                "folded, full body and feet clearly visible",
        "palette": "blue-black with faint cool highlights",
        "note": "sim entity is a pair ('the museum crows'); design ONE crow — the "
                "compositor renders the group from the single sprite.",
    },
    {
        "id": "ani_hedgehog", "name": "the hedgehog", "species": "hedgehog",
        "color": "#8a7a5c", "archetype": "small-ground",
        "descriptor": "a small round hedgehog",
        "coat": "a rounded coat of soft clay spines in warm greige, a small pale "
                "furred face and belly, a tiny pointed snout, little dark eyes, "
                "small rounded feet",
        "pose": "standing on all four little feet in a neutral snuffling stance, "
                "snout slightly forward, full body clearly visible",
        "palette": "warm greige, tan, and soft cream",
    },
]


def build_prompt(a):
    """Compile one animal's on-style Krea design prompt (deterministic)."""
    return (
        f"A single handmade clay-and-felt miniature figurine of {a['descriptor']}. "
        f"{a['pose'][0].upper() + a['pose'][1:]}. "
        f"Rounded toy-figurine proportions with a slightly large head and gentle "
        f"features. {a['coat']}. "
        f"{STYLE_MATERIAL}. {STYLE_LIGHT}. {STYLE_CAMERA}. {STYLE_BG}. "
        f"{a['palette']} palette."
    )


def emit_json(roster):
    out = []
    for a in roster:
        out.append({
            "id": a["id"], "name": a["name"], "species": a["species"],
            "sim_color": a["color"], "archetype": a["archetype"],
            "rig": ARCHETYPE[a["archetype"]],
            "prompt": build_prompt(a),
            **({"note": a["note"]} if a.get("note") else {}),
        })
    return out


def emit_md(roster):
    L = []
    L.append("# ERA — Animal Krea prompt sheet (compiled)\n")
    L.append("*Generated by `tools/roster_to_prompts.py animals`. Deterministic: "
             "regenerate any time from the sim roster.*\n")
    L.append("## Krea settings (Stage 1 — proven on Hana/Milo)\n")
    L.append(f"- Tool: **{KREA['tool']}**, size **{KREA['size']}**, {KREA['mode']}.")
    L.append("- **Gentle faces/features** (Roy's figurines have soft faces — supersedes "
             "the old 'no faces' note).")
    L.append("- At the **Meshy texture** step: **Remove Lighting OFF** (keep the baked "
             "matte clay shading — the plate is pre-rendered with baked light, so the "
             "animal must be baked-lit to match).")
    L.append(f"- {KREA['note']}\n")
    L.append("## The 7 animals\n")
    for a in roster:
        L.append(f"### {a['name']} (`{a['id']}`) — {a['species']}")
        L.append(f"- **Body archetype:** `{a['archetype']}` → {ARCHETYPE[a['archetype']]}")
        L.append(f"- **Sim color (must match texture):** `{a['color']}`")
        if a.get("note"):
            L.append(f"- **Note:** {a['note']}")
        L.append("\n> " + build_prompt(a) + "\n")
    return "\n".join(L)


def main():
    args = sys.argv[1:]
    which = args[0] if args else "animals"
    as_md = "--md" in args
    if which != "animals":
        print("only 'animals' is wired so far (residents next)", file=sys.stderr)
        sys.exit(2)
    if as_md:
        print(emit_md(ANIMALS))
    else:
        print(json.dumps(emit_json(ANIMALS), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
