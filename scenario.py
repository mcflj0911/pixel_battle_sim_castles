"""Loads a battle scenario from a JSON file and checks it, so a mistake shows up as a readable message
instead of a crash in the middle of a battle."""
import json

import heroes
import weather

CONDITION_TYPES = ("time", "side_eliminated", "units_in_area", "side_reaches", "event_fired", "all", "any",
                   "not", "after", "terrain_hidden", "side_below", "wave")
ACTION_TYPES = ("spawn", "remove_terrain", "show_terrain", "hide_terrain", "set_goal", "message")
UNIT_STATS = ("hp", "attack", "defence", "speed", "reach", "sight", "cooldown")
SPRITES = ("foot", "archer", "rider", "huorn", "catapult", "trebuchet", "champion", "commander", "ranger", "mage", "king", "wyvern", "hawk", "ballista", "longbow", "halberdier", "berserker", "pavise_cross", "war_dog", "mangonel", "ram_crew", "griffon", "harpy",
           "longship", "galley", "catapult_ship", "landing_boat", "siege_tower")


class ScenarioError(ValueError):
    pass


def load(path):
    """Read and check a scenario file. Returns the scenario as a dict with defaults filled in."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        raise ScenarioError(f"{path} is not valid JSON: {err}") from err
    return validate(data, path)


def validate(d, where="scenario"):
    if not isinstance(d, dict):
        raise ScenarioError(f"{where}: top level must be a JSON object")

    def need(obj, key, ctx):
        if not isinstance(obj, dict) or key not in obj:
            raise ScenarioError(f"{where}: {ctx} is missing '{key}'")
        return obj[key]

    def rect(value, ctx):
        if not (isinstance(value, list) and len(value) == 4 and all(isinstance(v, (int, float)) for v in value)):
            raise ScenarioError(f"{where}: {ctx} must be a list of four numbers [x, y, width, height]")
        return [float(v) for v in value]

    def point(value, ctx):
        if not (isinstance(value, list) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value)):
            raise ScenarioError(f"{where}: {ctx} must be a list of two numbers [x, y]")
        return [float(v) for v in value]

    sc = {}
    sc["name"] = str(need(d, "name", "scenario"))
    sc["subtitle"] = str(d.get("subtitle", ""))
    sc["description"] = str(d.get("description", ""))
    sc["seed"] = int(d.get("seed", 1))
    m = need(d, "map", "scenario")
    sc["map"] = {"width": int(need(m, "width", "map")), "height": int(need(m, "height", "map"))}
    if m.get("shore") is not None:                       # the sea: every y from here down is water
        shore = float(m["shore"])
        if not 0 < shore < sc["map"]["height"] - 60:
            raise ScenarioError(f"{where}: map shore must lie inside the map with room for a sea below it")
        sc["map"]["shore"] = shore
    w = d.get("weather") or {}
    cycle = w.get("cycle", [60, 130])
    if not (isinstance(cycle, list) and len(cycle) == 2 and 0 < cycle[0] <= cycle[1]):
        raise ScenarioError(f"{where}: weather cycle must be [shortest, longest] seconds between changes")
    if w.get("start", "clear") not in weather.KINDS:
        raise ScenarioError(f"{where}: weather start must be one of {weather.KINDS}")
    sc["weather"] = {"enabled": bool(w.get("enabled", True)), "start": w.get("start", "clear"),
                     "cycle": (float(cycle[0]), float(cycle[1])), "weights": dict(w.get("weights", {}))}

    sides = need(d, "sides", "scenario")
    if not sides:
        raise ScenarioError(f"{where}: 'sides' must list at least one side")
    sc["sides"] = {}
    for sid, s in sides.items():
        color = need(s, "color", f"side '{sid}'")
        if not (isinstance(color, list) and len(color) == 3):
            raise ScenarioError(f"{where}: side '{sid}' color must be [r, g, b]")
        enemies = s.get("enemies")
        if enemies is not None and not isinstance(enemies, list):
            raise ScenarioError(f"{where}: side '{sid}' enemies must be a list of side ids (or left out)")
        sc["sides"][sid] = {
            "name": str(need(s, "name", f"side '{sid}'")),
            "color": tuple(int(c) for c in color),
            "goal": point(need(s, "goal", f"side '{sid}'"), f"side '{sid}' goal"),
            "enemies": enemies,          # None means every other side
            "emblem": [str(r) for r in s.get("emblem", [])],   # a small pixel pattern ('#') shown on its banners
            "style": str(s.get("style", "")),   # the look of its castle, engines and men: "ravensmere" or "ironvale"
        }
        for e in enemies or []:
            if e not in sides:
                raise ScenarioError(f"{where}: side '{sid}' lists unknown enemy side '{e}'")

    types = need(d, "unit_types", "scenario")
    sc["unit_types"] = {}
    for tid, t in types.items():
        for stat in UNIT_STATS:
            need(t, stat, f"unit type '{tid}'")
        sprite = t.get("sprite", "foot")
        if sprite not in SPRITES:
            raise ScenarioError(f"{where}: unit type '{tid}' sprite must be one of {SPRITES}")
        sc["unit_types"][tid] = {**{k: float(t[k]) for k in UNIT_STATS}, "name": str(t.get("name", tid)),
                                 "sprite": sprite, "hero": bool(t.get("hero", False)),
                                 "immortal": bool(t.get("immortal", False)),
                                 "hunts_routers": bool(t.get("hunts_routers", False)),
                                 "rout_at": float(t.get("rout_at", 20)),
                                 "siege": bool(t.get("siege", False)),
                                 "splash": float(t.get("splash", 0)),
                                 "angle": float(t.get("angle", 45)),     # launch angle of its shots, in degrees
                                 "volley": bool(t.get("volley", False)),    # can loose arrow showers at packed foes
                                 "fire": bool(t.get("fire", False)),        # loses flaming arrows that set men alight
                                 "fire_ammo": float(t.get("fire_ammo", 0)),   # share of a siege engine's shots that are burning pitch
                                 "mounted": bool(t.get("mounted", False)),  # rides a horse: charges and spear formations
                                 "naval":         bool(t.get("naval",         False)),  # a ship: sails the sea lane
                                 "naval_role":    _naval_role(t, tid, where),               # ram, archer, bombard, transport
                                 "bombard":       bool(t.get("bombard",       False)),  # throws stones, though not a siege engine
                                 "carry":         int(t.get("carry",          0)),      # marines a landing boat carries
                                 "anti_mounted":  bool(t.get("anti_mounted",  False)),  # bonus vs cavalry
                                 "pierce_shield": bool(t.get("pierce_shield", False)),  # ignores testudo
                                 "struct_only":   bool(t.get("struct_only",   False)),  # only attacks structures
                                 "swoop":         bool(t.get("swoop",         False)),  # harpy-style swoop
                                 "berserk":       bool(t.get("berserk",       False)),  # berserker perk
                                 "tower":         bool(t.get("tower",         False)),   # a siege tower: archers inside
                                 "garrison":      int(t.get("garrison",       0)),       # archers inside a siege tower
                                 "shoot_height":  float(t.get("shoot_height", 0.0)),     # how high its arrows leave from
                                 "air_only":      bool(t.get("air_only",      False)),   # shoots only flyers (a ballista)
                                 "flying": bool(t.get("flying", False)),     # a flyer: wings, no walls, no melee
                                 "air_role": _air_role(t, tid, where),       # "ground" (bomber) or "air" (interceptor)
                                 "altitude": float(t.get("altitude", 60)),   # how high a flyer flies
                                 "max_alive": int(t.get("max_alive", 99)),   # a side never has more of this flyer at once
                                 "skills": _skills(t, tid, where),          # a hero's four skills (heroes.SKILLS)
                                 "perks": heroes.perks_of(_skills(t, tid, where)),
                                 "respawn": float(t.get("respawn", 30)),    # seconds before a fallen hero returns
                                 "bolt": t.get("bolt"),                     # a hero who shoots magic ("holy" or "hex")
                                 "title": str(t.get("title", "")),
                                 "style": int(t.get("style", 0)),           # which side's look a hero's art takes
                                 "rout_after": None if t.get("rout_after") is None else str(t["rout_after"])}

    sc["variants"] = {}                  # (side, unit type) -> the side's own version of that unit
    for tid, t in types.items():
        if "replaces" in t:
            if t.get("side") not in sc["sides"] or t["replaces"] not in types:
                raise ScenarioError(f"{where}: unit type '{tid}' must name a side and a unit type it replaces")
            sc["variants"][(t["side"], t["replaces"])] = tid
    if any(t["naval"] for t in sc["unit_types"].values()) and "shore" not in sc["map"]:
        raise ScenarioError(f"{where}: ships need a sea: give the map a 'shore'")
    sc["terrain"] = []
    seen_ids = set()
    for i, t in enumerate(d.get("terrain", [])):
        tid = str(need(t, "id", f"terrain #{i}"))
        if tid in seen_ids:
            raise ScenarioError(f"{where}: terrain id '{tid}' is used twice")
        seen_ids.add(tid)
        color = t.get("color", [120, 120, 120])
        owner = t.get("owner")
        if owner is not None:
            _check_side(owner, sides, where, f"terrain '{tid}' owner")
        hp = t.get("hp")                       # hit points: a structure with hp can be breached by siege engines
        sc["terrain"].append({"id": tid, "rect": rect(need(t, "rect", f"terrain '{tid}'"), f"terrain '{tid}' rect"),
                              "color": tuple(int(c) for c in color), "solid": bool(t.get("solid", False)),
                              "label": t.get("label"), "hidden": bool(t.get("hidden", False)),
                              "height": float(t.get("height", 14)), "style": t.get("style"),
                              "name": t.get("name"), "owner": owner,
                              "hp": None if hp is None else float(hp)})

    sc["craters"] = []                         # old shell holes in the field: [x, y, radius]; they give cover
    for i, c in enumerate(d.get("craters", [])):
        if not (isinstance(c, list) and len(c) == 3 and all(isinstance(v, (int, float)) for v in c)):
            raise ScenarioError(f"{where}: crater #{i} must be a list of three numbers [x, y, radius]")
        sc["craters"].append([float(v) for v in c])

    sc["groups"] = []
    for i, g in enumerate(need(d, "groups", "scenario")):
        ctx = f"group #{i}"
        _check_side(need(g, "side", ctx), sc["sides"], where, ctx)
        _check_type(need(g, "unit_type", ctx), sc["unit_types"], where, ctx)
        sc["groups"].append({"side": g["side"], "unit_type": g["unit_type"], "count": int(need(g, "count", ctx)),
                             "area": rect(need(g, "area", ctx), f"{ctx} area"), "name": _name(g, where, ctx)})

    event_ids = [e.get("id") for e in d.get("events", [])]
    sc["events"] = []
    for i, e in enumerate(d.get("events", [])):
        eid = str(need(e, "id", f"event #{i}"))
        trig = need(e, "trigger", f"event '{eid}'")
        _check_condition(trig, sc, event_ids, where, f"event '{eid}' trigger")
        actions = []
        for a in need(e, "actions", f"event '{eid}'"):
            actions.append(_check_action(a, sc, seen_ids, where, f"event '{eid}'"))
        sc["events"].append({"id": eid, "trigger": trig, "actions": actions, "repeat": bool(e.get("repeat", False)),
                             "cooldown": float(e.get("cooldown", 0))})

    sc["objectives"] = []
    for i, o in enumerate(d.get("objectives", [])):
        ctx = f"objective #{i}"
        _check_condition(need(o, "when", ctx), sc, event_ids, where, ctx + " when")
        sc["objectives"].append({"id": str(need(o, "id", ctx)), "text": str(need(o, "text", ctx)),
                                 "side": str(o.get("side", "")), "when": o["when"]})

    return sc


def _naval_role(t, tid, where):
    role = t.get("naval_role")
    if role is not None and role not in ("ram", "archer", "bombard", "transport"):
        raise ScenarioError(f"{where}: unit type '{tid}' naval_role must be ram, archer, bombard or transport")
    if role is not None and not t.get("naval"):
        raise ScenarioError(f"{where}: unit type '{tid}' has a naval_role but is not naval")
    return role


def _air_role(t, tid, where):
    role = t.get("air_role")
    if role is not None and role not in ("ground", "air"):
        raise ScenarioError(f"{where}: unit type '{tid}' air_role must be 'ground' or 'air'")
    if role is not None and not t.get("flying"):
        raise ScenarioError(f"{where}: unit type '{tid}' has an air_role but does not fly")
    return role


def _skills(t, tid, where):
    ids = [str(s) for s in t.get("skills", [])]
    if ids and len(ids) != 4:
        raise ScenarioError(f"{where}: unit type '{tid}' must list four skills (two passive, two active)")
    for s in ids:
        if s not in heroes.SKILLS:
            raise ScenarioError(f"{where}: unit type '{tid}' has unknown skill '{s}'")
    if ids and [heroes.SKILLS[s]["passive"] for s in ids].count(True) != 2:
        raise ScenarioError(f"{where}: unit type '{tid}' needs exactly two passive and two active skills")
    if ids and not t.get("hero"):
        raise ScenarioError(f"{where}: unit type '{tid}' has skills but is not a hero")
    return ids


def _name(obj, where, ctx):
    """Optional name for a single, named unit (a hero). Shown on screen."""
    name = obj.get("name")
    if name is not None and not isinstance(name, str):
        raise ScenarioError(f"{where}: {ctx} name must be text")
    return name


def _check_side(name, sides, where, ctx):
    if name not in sides:
        raise ScenarioError(f"{where}: {ctx} refers to unknown side '{name}'")


def _check_type(name, types, where, ctx):
    if name not in types:
        raise ScenarioError(f"{where}: {ctx} refers to unknown unit type '{name}'")


def _check_condition(c, sc, event_ids, where, ctx):
    if not isinstance(c, dict) or c.get("type") not in CONDITION_TYPES:
        raise ScenarioError(f"{where}: {ctx} must have a 'type' of one of {CONDITION_TYPES}")
    k = c["type"]
    if k == "time":
        float(c["at"])
    elif k == "side_eliminated":
        _check_side(c["side"], sc["sides"], where, ctx)
    elif k in ("units_in_area", "side_reaches"):
        _check_side(c["side"], sc["sides"], where, ctx)
        if not (isinstance(c["area"], list) and len(c["area"]) == 4):
            raise ScenarioError(f"{where}: {ctx} area must be [x, y, width, height]")
        if k == "units_in_area":
            int(c["count"])
    elif k == "wave":
        if c["event"] not in event_ids:
            raise ScenarioError(f"{where}: {ctx} refers to unknown event '{c['event']}'")
        if int(c["every"]) < 1:
            raise ScenarioError(f"{where}: {ctx} 'every' must be at least 1")
    elif k in ("event_fired", "after"):
        if c["event"] not in event_ids:
            raise ScenarioError(f"{where}: {ctx} refers to unknown event '{c['event']}'")
        if k == "after":
            float(c["seconds"])
    elif k == "terrain_hidden":
        if c["id"] not in {t["id"] for t in sc["terrain"]}:
            raise ScenarioError(f"{where}: {ctx} refers to unknown terrain '{c['id']}'")
    elif k == "side_below":
        _check_side(c["side"], sc["sides"], where, ctx)
        int(c["count"])
    elif k == "not":
        _check_condition(c["condition"], sc, event_ids, where, ctx)
    elif k in ("all", "any"):
        for sub in c["conditions"]:
            _check_condition(sub, sc, event_ids, where, ctx)


def _check_action(a, sc, terrain_ids, where, ctx):
    if not isinstance(a, dict) or a.get("type") not in ACTION_TYPES:
        raise ScenarioError(f"{where}: {ctx} has an action with a 'type' of one of {ACTION_TYPES}")
    if a["type"] == "spawn":
        _check_side(a["side"], sc["sides"], where, ctx)
        _check_type(a["unit_type"], sc["unit_types"], where, ctx)
        return {"type": "spawn", "side": a["side"], "unit_type": a["unit_type"], "count": int(a["count"]),
                "area": [float(v) for v in a["area"]], "name": _name(a, where, ctx)}
    if a["type"] == "set_goal":
        _check_side(a["side"], sc["sides"], where, ctx)
        return {"type": "set_goal", "side": a["side"], "point": [float(v) for v in a["point"]]}
    if a["type"] in ("remove_terrain", "show_terrain", "hide_terrain"):
        if a["id"] not in terrain_ids:
            raise ScenarioError(f"{where}: {ctx} changes unknown terrain '{a['id']}'")
        return {"type": a["type"], "id": a["id"]}
    return {"type": "message", "text": str(a["text"])}
