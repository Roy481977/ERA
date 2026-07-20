//! The WorldClock: one shared, authoritative clock.
//!
//! 1 tick = **5 minutes**; 12 ticks = 1 hour; 288 ticks = 1 day. Finer than the
//! old hour-granularity so movement takes believable time and the day's events
//! can spread across the hour instead of clumping on the hour. Routines still
//! reason in whole hours (each activity's preferred arrival + flexibility window);
//! durations and travel are expressed in hours/edges and converted to ticks at
//! the point they are used (see `TICKS_PER_HOUR`, `TRAVEL_TICKS_PER_WEIGHT`).

pub const MINUTES_PER_TICK: u64 = 5;
pub const TICKS_PER_HOUR: u64 = 12;
pub const TICKS_PER_DAY: u64 = TICKS_PER_HOUR * 24; // 288
pub const DAYS_PER_WEEK: u64 = 7;

/// How many ticks it takes to walk one unit of navigation-graph edge weight.
/// One edge-weight unit ≈ 10 minutes on foot, so a short hop between adjacent
/// quarters is a couple of ticks and a longer walk is visibly longer — trips
/// take real time.
pub const TRAVEL_TICKS_PER_WEIGHT: u32 = 2;

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
    /// Hour of the current day, 0..24.
    pub fn hour(&self) -> u64 {
        (self.tick / TICKS_PER_HOUR) % 24
    }
    /// Minute of the current hour, 0..60 (in steps of 5).
    pub fn minute(&self) -> u64 {
        (self.tick % TICKS_PER_HOUR) * MINUTES_PER_TICK
    }
    /// True on the first tick of an hour (for once-per-hour events).
    pub fn on_the_hour(&self) -> bool {
        self.tick % TICKS_PER_HOUR == 0
    }
    /// Weekday of the current day, 0 = Monday … 6 = Sunday.
    pub fn weekday(&self) -> u64 {
        self.day() % DAYS_PER_WEEK
    }
    pub fn weekday_name(&self) -> &'static str {
        WEEKDAY_NAMES[(self.weekday()) as usize]
    }
}
