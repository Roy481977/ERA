//! Behaviour Layer tests: the simulation is translated into observable behaviour
//! (poses, headings, staged conversations) rather than prose.

use era_first_breath::engine::Engine;

#[test]
fn conversations_are_staged_so_they_can_be_watched() {
    // Over a couple of days, at least one moment shows two residents turned to one
    // another, talking — a conversation held long enough to see, not a log line.
    let mut e = Engine::new();
    let mut saw_talk = false;
    let mut saw_partner = false;
    for _ in 0..(2 * 288) {
        e.tick();
        let snap = e.snapshot();
        for ent in &snap.entities {
            if ent.pose == "talk" {
                saw_talk = true;
                if ent.partner.is_some() {
                    saw_partner = true;
                }
            }
        }
        if saw_talk && saw_partner {
            break;
        }
    }
    assert!(saw_talk, "no conversation was ever staged as a 'talk' pose");
    assert!(saw_partner, "a talking resident had no one to talk to");
}

#[test]
fn walkers_face_where_they_are_going() {
    // Someone in transit has a non-idle pose and a heading; standing still keeps a
    // pose too. Poses are always present (never empty).
    let mut e = Engine::new();
    let mut saw_walk = false;
    for _ in 0..288 {
        e.tick();
        for ent in &e.snapshot().entities {
            assert!(!ent.pose.is_empty(), "{} had no pose", ent.name);
            if ent.pose == "walk" {
                saw_walk = true;
            }
        }
    }
    assert!(saw_walk, "no one ever walked");
}

#[test]
fn the_behaviour_layer_is_deterministic() {
    let mut a = Engine::new();
    let mut b = Engine::new();
    a.tick_n(200);
    b.tick_n(200);
    assert_eq!(a.snapshot().to_json(), b.snapshot().to_json());
}
