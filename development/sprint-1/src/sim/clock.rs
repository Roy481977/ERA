//! The WorldClock (Phase 2): one shared, authoritative clock.
//!
//! 1 tick = 1 hour; 24 ticks = 1 day. Time-blocks are derived from the hour so
//! routines can reason about *when* an activity is appropriate.

pub const TICKS_PER_DAY: u64 = 24;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Block {
    Night,
    Morning,
    Midday,
    Afternoon,
    Evening,
    Late,
}

impl Block {
    pub fn from_hour(hour: u64) -> Block {
        match hour {
            0..=5 => Block::Night,
            6..=9 => Block::Morning,
            10..=13 => Block::Midday,
            14..=17 => Block::Afternoon,
            18..=21 => Block::Evening,
            _ => Block::Late, // 22, 23
        }
    }
}

#[derive(Debug, Clone, Copy, Default)]
pub struct WorldClock {
    pub tick: u64,
}

impl WorldClock {
    pub fn new() -> Self {
        WorldClock { tick: 0 }
    }
    pub fn advance(&mut self) {
        self.tick += 1;
    }
    pub fn day(&self) -> u64 {
        self.tick / TICKS_PER_DAY
    }
    pub fn hour(&self) -> u64 {
        self.tick % TICKS_PER_DAY
    }
    pub fn block(&self) -> Block {
        Block::from_hour(self.hour())
    }
}
