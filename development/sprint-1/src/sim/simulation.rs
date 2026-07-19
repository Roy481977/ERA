//! The simulation loop (Phase 2 / 4): advances the clock and moves residents
//! through their routines. Deterministic; every state change is observable via
//! the event log.

use crate::sim::clock::{WorldClock, TICKS_PER_DAY};
use crate::sim::resident::{Resident, Status};
use crate::world::location::{location_for_affordance, LocationId};
use crate::world::navigation::NavGraph;
use crate::world::{build_world, World};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Event {
    pub tick: u64,
    pub day: u64,
    pub hour: u64,
    pub resident: &'static str,
    pub message: String,
}

pub struct Simulation {
    pub world: World,
    pub clock: WorldClock,
    pub residents: Vec<Resident>,
    pub log: Vec<Event>,
    last_day: u64,
}

fn edge_weight(nav: &NavGraph, a: LocationId, b: LocationId) -> u32 {
    nav.neighbors(a)
        .into_iter()
        .find(|(n, _)| *n == b)
        .map(|(_, w)| w)
        .unwrap_or_else(|| nav.travel_time(a, b).unwrap_or(1))
}

fn target_of(affordance: &str, home: LocationId) -> Option<LocationId> {
    if affordance == "HOME" {
        Some(home)
    } else {
        location_for_affordance(affordance)
    }
}

impl Simulation {
    pub fn new(residents: Vec<Resident>) -> Self {
        Simulation {
            world: build_world(),
            clock: WorldClock::new(),
            residents,
            log: Vec::new(),
            last_day: 0,
        }
    }

    pub fn run(&mut self, days: u64) {
        for _ in 0..(days * TICKS_PER_DAY) {
            self.step();
        }
    }

    /// Advance one tick.
    pub fn step(&mut self) {
        let day = self.clock.day();
        if day != self.last_day {
            for r in &mut self.residents {
                r.done_today.clear();
            }
            self.last_day = day;
        }
        let block = self.clock.block();

        // Disjoint borrows: nav (read) + residents (write) + log (write) + clock.
        let Simulation { world, residents, log, clock, .. } = self;
        let nav: &NavGraph = &world.nav;

        for r in residents.iter_mut() {
            // 1) advance the current status by one step.
            let status = std::mem::replace(&mut r.status, Status::Idle);
            match status {
                Status::Performing { activity, left } => {
                    if left > 1 {
                        r.status = Status::Performing { activity, left: left - 1 };
                    } else {
                        r.done_today.push(activity); // finished -> Idle (selects below)
                    }
                }
                Status::Traveling { activity, purpose, dest, dur, path, mut idx, leg_left } => {
                    if leg_left > 1 {
                        r.status = Status::Traveling {
                            activity, purpose, dest, dur, path, idx, leg_left: leg_left - 1,
                        };
                    } else {
                        idx += 1;
                        r.place = path[idx];
                        if r.place == dest {
                            r.status = Status::Performing { activity, left: dur };
                            log.push(Event {
                                tick: clock.tick, day: clock.day(), hour: clock.hour(),
                                resident: r.name,
                                message: format!("{purpose} — at {}", r.place),
                            });
                        } else {
                            let leg = edge_weight(nav, path[idx], path[idx + 1]);
                            r.status = Status::Traveling {
                                activity, purpose, dest, dur, path, idx, leg_left: leg,
                            };
                        }
                    }
                }
                Status::Idle => {}
            }

            // 2) if idle, select the next activity and start it (this tick).
            if let Status::Idle = r.status {
                if let Some(a) = r.select(block) {
                    let (aid, apurpose, adur, aff) = (a.id, a.purpose, a.duration, a.affordance);
                    let home = r.home;
                    if let Some(dest) = target_of(aff, home) {
                        if dest == r.place {
                            r.status = Status::Performing { activity: aid, left: adur };
                            log.push(Event {
                                tick: clock.tick, day: clock.day(), hour: clock.hour(),
                                resident: r.name,
                                message: format!("{apurpose} — at {}", r.place),
                            });
                        } else if let Some(path) = nav.shortest_path(r.place, dest) {
                            let leg = edge_weight(nav, path[0], path[1]);
                            let route = path.join(" -> ");
                            log.push(Event {
                                tick: clock.tick, day: clock.day(), hour: clock.hour(),
                                resident: r.name,
                                message: format!("sets out for {dest} ({apurpose}) via {route}"),
                            });
                            r.status = Status::Traveling {
                                activity: aid, purpose: apurpose, dest, dur: adur,
                                path, idx: 0, leg_left: leg,
                            };
                        }
                    }
                }
            }
        }

        clock.advance();
    }

    pub fn resident(&self, id: &str) -> Option<&Resident> {
        self.residents.iter().find(|r| r.id == id)
    }
}
