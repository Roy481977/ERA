//! A small seeded pseudo-random generator (SplitMix64).
//!
//! ERA's residents are fully determined (routines, seeded interactions) — the
//! world is reproducible. But a living thing needs a little genuine unpredictability
//! in the small choices: which way the fox turns tonight, whether the cat prowls or
//! curls up. This provides exactly that — *seeded* randomness, so a given world seed
//! always replays identically, yet a different seed grows a different life.
//!
//! Only the wildlife draws from this today; the residents remain deterministic, so
//! their behaviour (and every existing test) is unchanged.

#[derive(Debug, Clone)]
pub struct Rng {
    state: u64,
}

impl Rng {
    pub fn new(seed: u64) -> Self {
        // Avoid the all-zero fixed point.
        Rng { state: seed ^ 0x9E37_79B9_7F4A_7C15 }
    }

    /// Next 64 bits (SplitMix64).
    pub fn next_u64(&mut self) -> u64 {
        self.state = self.state.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.state;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }

    /// A value in `0..n` (0 if n == 0).
    pub fn below(&mut self, n: u64) -> u64 {
        if n == 0 {
            0
        } else {
            self.next_u64() % n
        }
    }

    /// True with probability `pct`%.
    pub fn chance(&mut self, pct: u32) -> bool {
        (self.below(100) as u32) < pct
    }

    /// An integer in `[lo, hi]` inclusive.
    pub fn range(&mut self, lo: i32, hi: i32) -> i32 {
        if hi <= lo {
            lo
        } else {
            lo + self.below((hi - lo + 1) as u64) as i32
        }
    }

    /// Pick one of `xs` (None if empty).
    pub fn pick<'a, T>(&mut self, xs: &'a [T]) -> Option<&'a T> {
        if xs.is_empty() {
            None
        } else {
            let i = self.below(xs.len() as u64) as usize;
            Some(&xs[i])
        }
    }
}
