# Rapidly [claim all the corpses for gold within the tileRange set below. Feature must be available on your server.

# User Settings:

command = '[claim'  # Can change this to [claimall to grab all the mobs loot.
tileRange = 4       # Does not check for line of sight, so I keep the range fairly low to avoid walls, etc.
                    # In hilly areas you might have to move around to have line of sight on a corpse.
lineOfSight = False # Items filter does not currently support LoS. Hopefully in the future it will.
claimDelay = 50     # Milliseconds between claims. Too low may stall the script or trip the server spam limit.

# DO NOT CHANGE ANYTHING BELOW UNLESS YOU KNOW WHAT YOU ARE DOING

noClaimMsg = 'You cannot use claim in this area'

def findCorpses():
    corpses = Items.Filter()
    corpses.Enabled = True
    corpses.IsCorpse = True
    corpses.OnGround = True
    corpses.Movable = False
    corpses.RangeMin = -1
    corpses.RangeMax = tileRange
    corpses.CheckIgnoreObject = True   # Skip corpses already attempted
    if lineOfSight == True:
        corpses.CheckLineOfSight = lineOfSight
    return Items.ApplyFilter(corpses)

def claimBlocked():
    return Journal.Search(noClaimMsg)

tried = []          # Corpses this script has ignored, so only these get un-ignored at the end
blocked = False     # Set when the server says claim is not allowed here

Journal.Clear(noClaimMsg)   # Remove only old copies of this message so they cannot trigger a false stop

try:
    corpseList = findCorpses()
    while Player.Connected and len(corpseList) > 0 and not blocked:

        for corpse in corpseList:
            # Ignore it right away so a failed claim never gets retried
            Misc.IgnoreObject(corpse.Serial)
            tried.append(corpse)

            Items.WaitForProps(corpse, 2000)
            name = Items.GetPropStringByIndex(corpse, 0) or ''
            if Player.Name.lower() not in name.lower():
                # Claim by serial so no target cursor is needed
                Player.ChatSay(89, '{0} {1}'.format(command, corpse.Serial))
                Misc.Pause(claimDelay)

                # Server refused the claim for this area, so stop trying entirely
                if claimBlocked():
                    blocked = True
                    break

            Misc.Pause(1)

        if not blocked:
            corpseList = findCorpses()
        Misc.Pause(1)

finally:
    # Remove from the ingnore list only the corpses this script ignored, leaving ignores from other scripts intact
    for corpse in tried:
        Misc.UnIgnoreObject(corpse.Serial)
        Misc.Pause(1)

if blocked:
    Journal.Clear(noClaimMsg)
    Player.HeadMessage(89, '*Claim is not allowed in this area*')
else:
    Player.HeadMessage(89, '*There are no corpses nearby*')
