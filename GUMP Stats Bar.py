# An alternative stat bar to show HP, Stam, Mana, plus Weight.
# Drag the bar by the thin strip on its left edge. It stays where you drop it.

# USER SETTINGS:

pos_x = 970             # The X screen position where the gump first opens.
pos_y = 807             # The Y screen position where the gump first opens.

# DO NOT CHANGE ANYTHING BELOW UNLESS YOU KNOW WHAT YOU ARE DOING

GUMP_ID = 123456         # Same as 0x1E240
BAR_LEN = 50             # Number of pipes in a full bar
REFRESH_MS = 200         # How often stats are checked
FORCE_REDRAW_LOOPS = 100 # Redraw at least this often (100 x 200ms = 20 sec) even if nothing changed

def bar_length(current, maximum):
    # Returns 0 to BAR_LEN. Guards against a zero max (login, loading, server lag)
    # and forces float math so it works on any IronPython version.
    if maximum <= 0:
        return 0
    filled = int(float(current) / maximum * BAR_LEN)
    if filled < 0:
        filled = 0
    if filled > BAR_LEN:
        filled = BAR_LEN
    return filled

def getColor(filled, is_weight):
    # filled is the pipe count (0 to 50), not a percent.
    # Thresholds are 1/4, 1/2, 3/4 of a full bar.
    if not is_weight:
        if filled == BAR_LEN:
            return 1081
        if filled > 37.5:
            return 66
        if filled > 25:
            return 52
        if filled > 12.5:
            return 47
        return 37
    else:
        if filled > 37.5:
            return 37
        if filled > 25:
            return 47
        if filled > 12.5:
            return 52
        return 66

def read_stats():
    # Snapshot of everything the gump displays. Used to skip redraws when nothing changed.
    return (
        Player.Hits, Player.HitsMax,
        Player.Mana, Player.ManaMax,
        Player.Stam, Player.StamMax,
        Player.Weight, Player.MaxWeight,
        Player.Poisoned, Player.YellowHits,
    )

def update_status_bar(stats):

    hits, hits_max, mana, mana_max, stam, stam_max, weight, weight_max, poisoned, yellow = stats

    rb = BAR_LEN * "|"
    hp = bar_length(hits, hits_max)
    mp = bar_length(mana, mana_max)
    sp = bar_length(stam, stam_max)
    wt = bar_length(weight, weight_max)

    hits_hue = getColor(hp, False)
    mana_hue = getColor(mp, False)
    stam_hue = getColor(sp, False)
    weight_hue = getColor(wt, True)

    if poisoned:   hp_hue = 72
    elif yellow:   hp_hue = 54
    else:          hp_hue = 97

    gd = Gumps.CreateGump(True, True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 5, 98, 1755)

    Gumps.AddLabel(gd, 12, 10, 1081, "H:")
    Gumps.AddLabel(gd, 10, 30, 1081, "M:")
    Gumps.AddLabel(gd, 12, 50, 1081, "S:")
    Gumps.AddLabel(gd, 8, 70, 1081, "W:")

    Gumps.AddLabel(gd, 30, 10, hits_hue, rb)
    Gumps.AddLabel(gd, 30, 30, mana_hue, rb)
    Gumps.AddLabel(gd, 30, 50, stam_hue, rb)
    Gumps.AddLabel(gd, 30, 70, weight_hue, rb)

    Gumps.AddLabel(gd, 30, 10, hp_hue, hp * "|")
    Gumps.AddLabel(gd, 30, 30, 97, mp * "|")
    Gumps.AddLabel(gd, 30, 50, 97, sp * "|")
    Gumps.AddLabel(gd, 30, 70, 97, wt * "|")

    Gumps.AddLabel(gd, 135, 10, hits_hue, "{} / {}".format(hits, hits_max))
    Gumps.AddLabel(gd, 135, 30, mana_hue, "{} / {}".format(mana, mana_max))
    Gumps.AddLabel(gd, 135, 50, stam_hue, "{} / {}".format(stam, stam_max))
    Gumps.AddLabel(gd, 135, 70, weight_hue, "{} / {}".format(weight, weight_max))

    # No SetGumpOpenLocation here. ClassicUO remembers where this gump ID was
    # last dragged and reopens it there. Forcing a location every redraw is
    # what used to snap the bar back.
    Gumps.CloseGump(GUMP_ID)
    Gumps.SendGump(GUMP_ID, Player.Serial, pos_x, pos_y, gd.gumpDefinition, gd.gumpStrings)

def main():

    last_stats = None
    loops_since_draw = 0

    # Place the bar at the starting position once. After this, the client
    # keeps track of wherever you drag it.
    CUO.SetGumpOpenLocation(GUMP_ID, pos_x, pos_y)

    try:
        while Player.Connected:
            stats = read_stats()
            if stats != last_stats or loops_since_draw >= FORCE_REDRAW_LOOPS:
                update_status_bar(stats)
                last_stats = stats
                loops_since_draw = 0
            else:
                loops_since_draw += 1
            Misc.Pause(REFRESH_MS)
    finally:
        # Remove the bar when the script stops or the player disconnects.
        Gumps.CloseGump(GUMP_ID)

main()