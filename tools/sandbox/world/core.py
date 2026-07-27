"""
world.core — WORLD layer: time, calendar, weather.

Everything here is configuration with English-year defaults. A district
(or a whole other world) can override any of it with data. Nothing below
this layer knows what a bakery is.

Determinism: one Rng per world, md5-seeded (CD-007). No wall clock, no
random module, anywhere in the engine.
"""
import hashlib

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class Rng:
    def __init__(self, seed):
        self.seed = seed

    def h(self, *a):
        s = ":".join(map(str, a)) + f":{self.seed}"
        return int(hashlib.md5(s.encode()).hexdigest(), 16) % 10000

    def f(self, *a):
        return self.h(*a) / 10000.0


# ---------------------------------------------------------------- calendar
DEFAULT_CALENDAR = {
    "start_month": "Aug",
    "months": [("Aug", 31), ("Sep", 30), ("Oct", 31), ("Nov", 30),
               ("Dec", 31), ("Jan", 31), ("Feb", 28), ("Mar", 31),
               ("Apr", 30), ("May", 31), ("Jun", 30), ("Jul", 31)],
    "seasons": {"Aug": "summer", "Sep": "autumn", "Oct": "autumn",
                "Nov": "autumn", "Dec": "winter", "Jan": "winter",
                "Feb": "winter", "Mar": "spring", "Apr": "spring",
                "May": "spring", "Jun": "summer", "Jul": "summer"},
    # public holidays: (kind, args) resolved against the month table
    "holidays": [("last_monday", "Aug"), ("month_day", "Dec", 25),
                 ("month_day", "Dec", 26), ("month_day", "Jan", 1),
                 ("month_day_next", "Jan", 1), ("month_day", "Apr", 7),
                 ("month_day", "Apr", 10), ("month_day", "May", 1),
                 ("last_monday", "May")],
    "family_day": ("Dec", 25),          # the day the town stays home
    # school terms: closed ranges, as (month, day, month, day)
    "term_breaks": [("Aug", 1, "Sep", 4), ("Oct", 24, "Oct", 30),
                    ("Dec", 18, "Jan", 2), ("Feb", 13, "Feb", 19),
                    ("Apr", 3, "Apr", 16), ("May", 29, "Jun", 4),
                    ("Jul", 21, "Jul", 31)],
}

DEFAULT_WEATHER = {          # per season: rain threshold, wind band (of 10000)
    "summer": (1700, 900), "autumn": (3100, 1700),
    "winter": (3400, 2000), "spring": (2600, 1500),
    "dark_season": "winter", "dark_from_slot": 5,
}

# how a place's season profile scales its appeal — WORLD knowledge, not place
DEFAULT_SEASON_PROFILES = {
    "garden":   {"spring": 1.35, "summer": 1.15, "autumn": 0.8, "winter": 0.25},
    "open_air": {"winter": 0.65},
    None:       {},
}


class Clock:
    def __init__(self, weeks, cal=None):
        self.weeks = weeks
        self.ndays = weeks * 7
        cal = cal or DEFAULT_CALENDAR
        self.mname = [m for m, _ in cal["months"]]
        self.mlen = [l for _, l in cal["months"]]
        self.mstart = []
        acc = 0
        for l in self.mlen:
            self.mstart.append(acc)
            acc += l
        self.season_by_month = [cal["seasons"][m] for m in self.mname]
        self.holidays = set()
        for spec in cal["holidays"]:
            self.holidays.add(self._resolve(spec))
        fm, fd = cal["family_day"]
        self.family_day = self._day(fm, fd)
        self.breaks = [(self._day(a, b), self._day(c, d))
                       for (a, b, c, d) in cal["term_breaks"]]

    def _mi(self, name):
        return self.mname.index(name)

    def _day(self, mname, dom):
        return self.mstart[self._mi(mname)] + dom - 1

    def _resolve(self, spec):
        if spec[0] == "last_monday":
            mi = self._mi(spec[1])
            end = self.mstart[mi] + self.mlen[mi] - 1
            return end - (end % 7)
        if spec[0] == "month_day":
            return self._day(spec[1], spec[2])
        if spec[0] == "month_day_next":
            return self._day(spec[1], spec[2]) + 1
        raise ValueError(spec)

    def month_of(self, day):
        for i in range(len(self.mstart) - 1, -1, -1):
            if day >= self.mstart[i]:
                return i
        return 0

    def date_str(self, day):
        mi = self.month_of(day)
        return f"{DAYS[day % 7]} {day - self.mstart[mi] + 1} {self.mname[mi]}"

    def season_of(self, day):
        return self.season_by_month[self.month_of(day)]

    def school_holiday(self, day):
        return any(a <= day <= b for a, b in self.breaks)


class Weather:
    def __init__(self, rng, clock, cfg=None):
        self.rng, self.clock = rng, clock
        self.cfg = cfg or DEFAULT_WEATHER

    def at(self, day):
        sn = self.clock.season_of(day)
        rain, wind = self.cfg[sn]
        r = self.rng.h("wx", day)
        return "rain" if r < rain else ("wind" if r < rain + wind else "dry")

    def dark(self, day, slot):
        return (self.clock.season_of(day) == self.cfg["dark_season"]
                and slot >= self.cfg["dark_from_slot"])
