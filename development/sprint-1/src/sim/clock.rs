//! The WorldClock (Phase 2): one shared, authoritative clock.
//!
//! 1 tick = 1 hour; 24 ticks = 1 day. Routines reason about the *hour* directly
//! (via each activity's preferred arrival + flexibility window), so the clock
//! stays a plain counter with no notion of named blocks.

pub const TICKS_PER_DAY: u64 = 24;
pub const DAYS_PER_WEEK: u64 = 7;

/// Weekday names, index 0 = Monday … 6 = Sunday.
pub const WEEKDAY_NAMES: [&str; 7] =
    ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

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
    /// Weekday of the current day, 0 = Monday … 6 = Sunday.
    pub fn weekday(&self) -> u64 {
        self.day() % DAYS_PER_WEEK
    }
    pub fn weekday_name(&self) -> &'static str {
        WEEKDAY_NAMES[(self.weekday()) as usize]
    }
}
