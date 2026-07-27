"""
world.entities — places, institutions, households.

A Place is a bundle of capabilities with hours and an environment. The
simulator never knows it is talking to a bakery: it sees {bread, warmth,
conversation} with morning hours. Identity is what the historian finds
in the accumulated record, afterwards.

An Institution exists independently of any resident: it has members,
roles, a history and continuity. Residents pass through it.

A Household is a simulation entity of its own: shared possessions,
finances, upkeep, traces, traditions, a history.
"""
from collections import defaultdict


class Place:
    def __init__(self, pid, d):
        self.id = pid
        self.sat = dict(d.get("provides", {}))       # capability -> strength
        self.open = set(d.get("open", range(7)))
        self.days = d.get("days")                    # None = every day
        self.cover = d.get("cover", False)
        self.quiet = d.get("quiet", False)
        self.adults_only = d.get("adults_only", False)
        self.closes_holidays = d.get("closes_holidays", False)
        self.public = d.get("public", True)
        self.operator = d.get("operator")            # institution id or None
        self.season_profile = d.get("season_profile")
        self.matchday_only = d.get("matchday_only", False)
        self.loc = d.get("loc")

    def open_at(self, d, s):
        if self.days is not None and d not in self.days:
            return False
        return s in self.open


class Institution:
    def __init__(self, iid, d):
        self.id = iid
        self.name = d.get("name", iid)
        self.kind = d.get("kind", "association")
        self.places = list(d.get("places", []))
        self.staff = {}                              # name -> role
        self.members = {}                            # name -> since_day
        self.auto_member = d.get("auto_member")      # {"place":…, "uses":N}
        self.history = []                            # (day, text)

    def hire(self, day, name, role):
        self.staff[name] = role
        self.history.append((day, f"{name} joined as {role}"))

    def retire(self, day, name):
        role = self.staff.pop(name, None)
        if role:
            self.history.append((day, f"{name} retired after years as {role}"))

    def join(self, day, name):
        if name not in self.members:
            self.members[name] = day
            self.history.append((day, f"{name} became a member"))

    def note(self, day, text):
        self.history.append((day, text))


class Household:
    def __init__(self, hid, plot):
        self.id = hid
        self.plot = plot
        self.members = []                            # resident names
        self.poss = []                               # shared items
        self.balance = 120.0
        self.income = 0.0                            # per week, set from occupations
        self.upkeep = []                             # open problems
        self.history = []                            # (day, text)
        self.visitors = defaultdict(int)             # name -> times hosted
        self.traditions = []                         # detected post-hoc

    def note(self, day, text):
        self.history.append((day, text))
