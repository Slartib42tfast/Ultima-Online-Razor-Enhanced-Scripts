# Rapidly [claim all the corpses for gold within the tileRange set below. Feature must be available on your server.

# User Settings:

command = '[claim'  # Can change this to [claimall to grab all the mobs loot.
tileRange = 4       # Does not check for line of sight, so keep the range fairly low to avoid walls, etc.
                    # In hilly areas you might have to move around to have line of sight on a corpse.
lineOfSight = False # Items filter does not currently support LoS. Hopefully in the future it will.

# DO NOT CHANGE ANYTHING BELOW UNLESS YOU KNOW WHAT YOU ARE DOING

if Misc.ScriptStatus('LOOP Auto Battle.py'):
    Misc.ScriptStop('LOOP Auto Battle.py')

def findCorpses():
    corpses = Items.Filter()
    corpses.Enabled = True
    corpses.IsCorpse = True
    corpses.OnGround = True
    corpses.Movable = False
    corpses.RangeMin = -1
    corpses.RangeMax = tileRange
    if lineOfSight == True:
        corpses.CheckLineOfSight = lineOfSight
    corpseCount = Items.ApplyFilter(corpses)
    return corpseCount

while len(findCorpses()) > 0:
    
    for corpse in findCorpses():
        
        if not Target.HasTarget():
            Player.ChatSay(89, command)
        Target.WaitForTarget(1000)
        Target.TargetExecute(corpse.Serial)
        Target.WaitForTarget(1000)
        
        Misc.Pause(1)
        
    Misc.Pause(1)
    
if Target.HasTarget():
    Target.Cancel()
Player.HeadMessage(89, '*There are no corpses nearby*')