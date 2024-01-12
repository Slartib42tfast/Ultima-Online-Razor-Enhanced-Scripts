# Place the pile of ore in a subcontainer inside your backpack.
# Target the ore pile.
# Target a forge within range.

orePile = Items.FindBySerial(Target.PromptTarget('Place the pile of ore in a subcontainer inside your backpack and then target the ore pile.', 89))
oreID = orePile.ItemID
oreHue = orePile.Hue
pileContainer = orePile.Container
forge = Items.FindBySerial(Target.PromptTarget('Target the forge within range that you want to smelt the ore on.', 89))

while Items.FindByID(oreID, oreHue, pileContainer) != None:
    ore = Items.FindByID(oreID, oreHue, pileContainer)
    Items.Move(ore, Player.Backpack, 1, 0, 0)
    Misc.Pause(500)
    for item in Player.Backpack.Contains:
        if item.ItemID == oreID and item.Hue == oreHue:
            while Items.FindBySerial(item.Serial) :
                Items.UseItem(item)
                Target.WaitForTarget(5000, False)
                Target.TargetExecute(forge)
                Misc.Pause(500)
        Misc.Pause(1)
    Misc.Pause(1)