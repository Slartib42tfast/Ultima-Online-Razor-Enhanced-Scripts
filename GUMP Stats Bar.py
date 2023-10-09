# An alternative stat bar to show HP, Stam, Mana, plus Weight.
# If move_to_position is set to True below, upon starting the script, you have 10 seconds
#   to position the gump where you want it. After that you will not be able to move or
#   close the gump while the script is running.

# USER SETTINGS:

pos_x = 970             # The X screen position where you want the gump to open.
pos_y = 807             # The Y screen position where you want the gump to open.
move_to_position = True # Allow the gump to be moved for 10 seconds after start.

# DO NOT CHANGE ANYTHING BELOW UNLESS YOU KNOW WHAT YOU ARE DOING

def getColor(percent_full, is_weight):
    
    color = 0
    
    if is_weight == False:
        if percent_full <= 12.5:
            color = 37
        if percent_full > 12.5:
            color = 47
        if percent_full > 25:
            color = 52
        if percent_full > 37.5:
            color = 66
        if percent_full == 50:
            color = 1081
    else:
        if percent_full <= 12.5:
            color = 66
        if percent_full > 12.5:
            color = 52
        if percent_full > 25:
            color = 47
        if percent_full > 37.5:
            color = 37
    
    return color

def update_status_bar():

    rb = 50 * "|"
    hp = int(Player.Hits/Player.HitsMax * 50)
    mp = int(Player.Mana/Player.ManaMax * 50)
    sp = int(Player.Stam/Player.StamMax * 50)
    wt = int(Player.Weight/Player.MaxWeight * 50)
    
    if hp > 50: hp = 50
    if mp > 50: mp = 50
    if sp > 50: sp = 50
    if wt > 50: wt = 50
    
    hp_pipes = hp * "|"
    mp_pipes = mp * "|"
    sp_pipes = sp * "|"
    wt_pipes = wt * "|"

    gd = Gumps.CreateGump(True, True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 5, 98, 1755)
    
    hits_hue = getColor(hp, False)
    mana_hue = getColor(mp, False)
    stam_hue = getColor(sp, False)
    weight_hue = getColor(wt, True)

    Gumps.AddLabel(gd, 12, 10, 1081, "H:")
    Gumps.AddLabel(gd, 10, 30, 1081, "M:")
    Gumps.AddLabel(gd, 12, 50, 1081, "S:")
    Gumps.AddLabel(gd, 8, 70, 1081, "W:")

    Gumps.AddLabel(gd, 30, 10, hits_hue, rb)
    Gumps.AddLabel(gd, 30, 30, mana_hue, rb)
    Gumps.AddLabel(gd, 30, 50, stam_hue, rb)
    Gumps.AddLabel(gd, 30, 70, weight_hue, rb)

    if Player.Poisoned:     hp_hue = 72
    elif Player.YellowHits: hp_hue = 54
    else:                   hp_hue = 97

    Gumps.AddLabel(gd, 30, 10, hp_hue, hp_pipes)
    Gumps.AddLabel(gd, 30, 30, 97, mp_pipes)
    Gumps.AddLabel(gd, 30, 50, 97, sp_pipes)
    Gumps.AddLabel(gd, 30, 70, 97, wt_pipes)

    Gumps.AddLabel(gd, 135, 10, hits_hue, str(Player.Hits) + " /" + " " + str(Player.HitsMax))
    Gumps.AddLabel(gd, 135, 30, mana_hue, str(Player.Mana) + " /" + " " + str(Player.ManaMax))
    Gumps.AddLabel(gd, 135, 50, stam_hue, str(Player.Stam) + " /" + " " + str(Player.StamMax))
    Gumps.AddLabel(gd, 135, 70, weight_hue, str(Player.Weight) + " /" + " " + str(Player.MaxWeight))

    #Gumps.AddLabel(gd, 165, 10, 1081, "/")
    #Gumps.AddLabel(gd, 165, 30, 1081, "/")
    #Gumps.AddLabel(gd, 165, 50, 1081, "/")
    #Gumps.AddLabel(gd, 175, 70, 1081, "/")

    #Gumps.AddLabel(gd, 180, 10, 1081, str(Player.HitsMax))
    #Gumps.AddLabel(gd, 180, 30, 1081, str(Player.ManaMax))
    #Gumps.AddLabel(gd, 180, 50, 1081, str(Player.StamMax))
    #Gumps.AddLabel(gd, 190, 70, 1081, str(Player.MaxWeight))

    Gumps.CloseGump(123456)
    CUO.SetGumpOpenLocation( 123456, pos_x, pos_y)
    Gumps.SendGump(123456, Player.Serial, pos_x, pos_y, gd.gumpDefinition, gd.gumpStrings)

def position_status_bar():
    update_status_bar()
    Player.HeadMessage(68, "You have 10 seconds to move the status bar to final position")
    Misc.Pause(10000)

def main():
    
    if move_to_position == True:
        position_status_bar()

    while True:

        update_status_bar()
        Misc.Pause(200)

main()
