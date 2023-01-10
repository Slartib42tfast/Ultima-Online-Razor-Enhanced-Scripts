# USER GUIDE:
# 1. Some customization is available under USER SETTINGS below.
# 2. Keyword/ItemID/Color are all optional. If you do not fill in any of them, all items in the
#    Source Container will be found. Use any combination of Keyword/ItemID/Color to select
#    a specific type of item.
#    You can type in those boxes or you can click the button to target something and it will
#       automatically fill those boxes, using the item name as the keyword.
#       ***PLEASE NOTIFY BILLY BLACKSMITH#2276 IN DISCORD IF ANY SPECIAL CHARACTERS CAUSE ERRORS!
#    The keyword is NOT case-sensitive but must be an exact word or phrase found in any of
#       the item properties.
#       EXAMPLES:
#       Keyword "Gold Coin" will only find gold coins, whereas "Gold" will find golden nuggets,
#           gold coins, goldilocks, gold ingots, etc.
#       Keyword "whirlwind" will find all weapons with that ability, whereas "whirl wind" will
#           find none.
#       ItemID "0xeed" with Keyword and Color blank will find gold, voting tokens and anything
#           else that shares that graphic, whereas an ItemID of "0xeed" and Color of "0x0000"
#           will find only gold.
#       Color "0x495" or "0x0495" alone will find everything of that color, such as your Token
#           Ledger and Trash 4 Tokens Backpack.
#    ItemID and Color, if used, must be in hex format 0x0000. Leading zeros after the x are
#       optional - "0x495" and "0x0495" both work.
# 3. The Source Container and Destination Container both default to your main backpack unless
#    you click the buttons and target other containers or mobiles.
#    To set your bank box as one of the containers, target yourself or a banker NPC while in a
#    banking zone.
# 4. Position is optional. If you want the things to be placed in a certain spot in the
#    Destination Container then fill in X (horizontal) and Y (vertical) positions.
# 5. Quantity is optional. It is only used if Count Only is NOT checked. If this box does not
#    contain a valid number then the quantity moved will not be limited.
# 6. Vendor Price and Description is optional. If using this script to stock your vendor, you
#    must target a container inside your vendor inventory as the Destination Container,
#    DO NOT TARGET THE VENDOR ITSELF.
# 7. Count Only is optional. If checked, it will not move the things found, it will only count
#    them for you.

import clr
clr.AddReference('System.Drawing','System.Windows.Forms')
import System.Drawing
from System.Drawing import *
from System.Threading import ThreadStart, Thread
from System.Windows.Forms import (Application, Button, CheckBox, ComboBox, FlatStyle, Form, FormBorderStyle, FormClosingEventHandler, FormStartPosition, Label, ListBox, TabAlignment, TabControl, TabPage, TextBox)
from System.Collections.Generic import List

####################   USER SETTINGS   ####################
    
delay =             410     #Milliseconds between moving items. Increase if it moves them too fast.
positionH =         0    #Horizontal position where the form opens on the screen.
positionV =         600     #Vertical position where the form opens on the screen.
backgroundColor =   Color.FromArgb(193, 217, 224)
textColor =         Color.FromArgb(31, 47, 61)
buttonColor =       Color.FromArgb(241, 241, 241)
textboxColor =      Color.FromArgb(255, 255, 255)
placeholderColor =  Color.FromArgb(125, 198, 224)

####################   DO NOT CHANGE ANYTHING BELOW THIS POINT   ####################

fontBtn = Font('Arial',6.5)
 
####################   MAIN FORM - START   ####################
    
class mainForm(Form):
    
    ####################   SCRIPT SETTINGS   ####################

    scriptName = 'Thing Mover | {} ({})'.format(Player.Name, Misc.ShardName())
    global sourceContainer
    sourceContainer =       Player.Backpack
    global destinationContainer
    destinationContainer =  Player.Backpack
    positionX =             'X'
    positionY =             'Y'
    Misc.SetSharedValue('containerType', 'normal')
    
    def __init__(self):
        Form.__init__(self)
        self.Text = '{}'.format(self.scriptName)
        self.BackColor = backgroundColor
        self.ForeColor = textColor
        captionHeight = System.Windows.Forms.SystemInformation.CaptionHeight
        self.Size = Size(300 + 20, (234 + captionHeight + 20))
        self.FormBorderStyle = FormBorderStyle.Fixed3D
        self.StartPosition = FormStartPosition.Manual
        self.Location = Point(positionH,positionV)
        self.TopMost = True
        self.Show()
 
        ####################   DEFINE CONTROLS   ####################
        
        self.keywordTextBox = TextBox()
        self.keywordTextBox.Multiline = False
        self.keywordTextBox.Location = Point(5, 5)
        self.keywordTextBox.Size = Size(210, 22)
        self.keywordTextBox.Font = Font('Arial',9.5)
        self.keywordTextBox.Text = '[Type a Keyword or Target a Thing]'
        self.keywordTextBox.BackColor = textboxColor
        self.keywordTextBox.ForeColor = placeholderColor
        self.keywordTextBox.GotFocus += self.gotFocusEvents
        self.keywordTextBox.LostFocus += self.lostFocusEvents
        self.Controls.Add(self.keywordTextBox)

        self.targetThingButton = Button()
        self.targetThingButton.Text = 'Target a Thing'
        self.targetThingButton.BackColor = buttonColor
        self.targetThingButton.Location = Point(210, 5)
        self.targetThingButton.Width = 85
        self.targetThingButton.Height = 22
        #self.targetThingButton.Size = Size(85, 22)
        self.targetThingButton.Font = fontBtn
        self.targetThingButton.FlatStyle = FlatStyle.Flat
        self.targetThingButton.FlatAppearance.BorderSize = 1 
        self.targetThingButton.Click += self.btnPressedEvent
        self.Controls.Add(self.targetThingButton)
   
        self.itemIDLabel = Label()
        self.itemIDLabel.Text = 'ItemID:'
        self.itemIDLabel.ForeColor = textColor
        self.itemIDLabel.Location = Point(5, 36)
        self.itemIDLabel.Size = Size(41, 22)
        self.Controls.Add(self.itemIDLabel)
        
        self.itemIDTextBox = TextBox()
        self.itemIDTextBox.Multiline = False
        self.itemIDTextBox.Location = Point(46, 32)
        self.itemIDTextBox.Size = Size(95, 22)
        self.itemIDTextBox.Font = Font('Arial',9)
        self.itemIDTextBox.Text = '[ 0x0000 ]'
        self.itemIDTextBox.BackColor = textboxColor
        self.itemIDTextBox.ForeColor = placeholderColor
        self.itemIDTextBox.GotFocus += self.gotFocusEvents
        self.itemIDTextBox.LostFocus += self.lostFocusEvents
        self.Controls.Add(self.itemIDTextBox)
   
        self.colorLabel = Label()
        self.colorLabel.Text = 'Color:'
        self.colorLabel.ForeColor = textColor
        self.colorLabel.Location = Point(165, 36)
        self.colorLabel.Size = Size(35, 22)
        self.Controls.Add(self.colorLabel)
        
        self.colorTextBox = TextBox()
        self.colorTextBox.Multiline = False
        self.colorTextBox.Location = Point(200, 32)
        self.colorTextBox.Size = Size(95, 22)
        self.colorTextBox.Font = Font('Arial',9)
        self.colorTextBox.Text = '[ 0x0000 ]'
        self.colorTextBox.BackColor = textboxColor
        self.colorTextBox.ForeColor = placeholderColor
        self.colorTextBox.GotFocus += self.gotFocusEvents
        self.colorTextBox.LostFocus += self.lostFocusEvents
        self.Controls.Add(self.colorTextBox)

        self.targetSourceButton = Button()
        self.targetSourceButton.Text = 'Target Source Container'
        self.targetSourceButton.BackColor = buttonColor
        self.targetSourceButton.Location = Point(5, 59)
        self.targetSourceButton.Size = Size(290, 22)
        self.targetSourceButton.Font = fontBtn
        self.targetSourceButton.FlatStyle = FlatStyle.Flat
        self.targetSourceButton.FlatAppearance.BorderSize = 1 
        self.targetSourceButton.Click += self.btnPressedEvent
        self.Controls.Add(self.targetSourceButton)

        self.targetDestinationButton = Button()
        self.targetDestinationButton.Text = 'Target Destination Container'
        self.targetDestinationButton.BackColor = buttonColor
        self.targetDestinationButton.Location = Point(5, 86)
        self.targetDestinationButton.Size = Size(290, 22)
        self.targetDestinationButton.Font = fontBtn
        self.targetDestinationButton.FlatStyle = FlatStyle.Flat
        self.targetDestinationButton.FlatAppearance.BorderSize = 1 
        self.targetDestinationButton.Click += self.btnPressedEvent
        self.Controls.Add(self.targetDestinationButton)
   
        self.positionLabel = Label()
        self.positionLabel.Text = 'Position:'
        self.positionLabel.ForeColor = textColor
        self.positionLabel.Location = Point(5, 117)
        self.positionLabel.Size = Size(48, 22)
        self.Controls.Add(self.positionLabel)
        
        self.xTextBox = TextBox()
        self.xTextBox.Multiline = False
        self.xTextBox.Location = Point(53, 113)
        self.xTextBox.Size = Size(30, 22)
        self.xTextBox.Font = Font('Arial',9)
        self.xTextBox.Text = 'X'
        self.xTextBox.BackColor = textboxColor
        self.xTextBox.ForeColor = placeholderColor
        self.xTextBox.GotFocus += self.gotFocusEvents
        self.xTextBox.LostFocus += self.lostFocusEvents
        self.Controls.Add(self.xTextBox)
        
        self.yTextBox = TextBox()
        self.yTextBox.Multiline = False
        self.yTextBox.Location = Point(82, 113)
        self.yTextBox.Size = Size(30, 22)
        self.yTextBox.Font = Font('Arial',9)
        self.yTextBox.Text = 'Y'
        self.yTextBox.BackColor = textboxColor
        self.yTextBox.ForeColor = placeholderColor
        self.yTextBox.GotFocus += self.gotFocusEvents
        self.yTextBox.LostFocus += self.lostFocusEvents
        self.Controls.Add(self.yTextBox)
   
        self.quantityLabel = Label()
        self.quantityLabel.Text = 'Quantity:'
        self.quantityLabel.ForeColor = textColor
        self.quantityLabel.Location = Point(150, 117)
        self.quantityLabel.Size = Size(50, 22)
        self.Controls.Add(self.quantityLabel)
        
        self.quantityTextBox = TextBox()
        self.quantityTextBox.Multiline = False
        self.quantityTextBox.Location = Point(200, 113)
        self.quantityTextBox.Size = Size(95, 22)
        self.quantityTextBox.Font = Font('Arial',9)
        self.quantityTextBox.Text = '[ All or # ]'
        self.quantityTextBox.BackColor = textboxColor
        self.quantityTextBox.ForeColor = placeholderColor
        self.quantityTextBox.GotFocus += self.gotFocusEvents
        self.quantityTextBox.LostFocus += self.lostFocusEvents
        self.Controls.Add(self.quantityTextBox)
        
        self.vendorTextBox = TextBox()
        self.vendorTextBox.Multiline = False
        self.vendorTextBox.Location = Point(5, 140)
        self.vendorTextBox.Size = Size(290, 22)
        self.vendorTextBox.Font = Font('Arial',9)
        self.vendorTextBox.Text = '[ Vendor Price and Description if Applicable ]'
        self.vendorTextBox.BackColor = textboxColor
        self.vendorTextBox.ForeColor = placeholderColor
        self.vendorTextBox.GotFocus += self.gotFocusEvents
        self.vendorTextBox.LostFocus += self.lostFocusEvents
        self.Controls.Add(self.vendorTextBox)
   
        self.countOnlyCheckBox = CheckBox()
        self.countOnlyCheckBox.Text = 'Count only (don\'t move)'
        self.countOnlyCheckBox.Checked = False
        self.countOnlyCheckBox.Location = Point(5, 167)
        self.countOnlyCheckBox.Size = Size(145, 16)
        self.Controls.Add(self.countOnlyCheckBox)
   
        self.numberFoundLabel = Label()
        self.numberFoundLabel.Text = '# Found: Waiting on you...'
        self.numberFoundLabel.ForeColor = Color.FromArgb(200, 0, 0)
        self.numberFoundLabel.Location = Point(150, 167)
        self.numberFoundLabel.Size = Size(145, 22)
        self.Controls.Add(self.numberFoundLabel)

        self.moveCountButton = Button()
        self.moveCountButton.Text = 'Move/Count the Thing'
        self.moveCountButton.BackColor = buttonColor
        self.moveCountButton.Location = Point(5, 194)
        self.moveCountButton.Size = Size(290, 35)
        self.moveCountButton.Font = Font('Arial',12)
        self.moveCountButton.FlatStyle = FlatStyle.Flat
        self.moveCountButton.FlatAppearance.BorderSize = 1 
        self.moveCountButton.Click += self.btnPressedEvent
        self.Controls.Add(self.moveCountButton)

    ####################   BUTTON PRESSED EVENT HANDLER   ####################
        
    def btnPressedEvent(self, sender, args):
            
        if sender == self.targetThingButton:
            thing = Items.FindBySerial(Target.PromptTarget('Target an item to move and/or count.',89))
            global thingName
            thingName = Items.GetPropStringByIndex(thing.Serial, 0)
            global thingItemID
            thingItemID = hex(thing.ItemID)
            global thingColor
            thingColor = hex(thing.Hue)
            global sourceContainer
            sourceContainer = Items.FindBySerial(thing.Container)
            containerName = Items.GetPropStringByIndex(sourceContainer.Serial, 0)
            
            self.keywordTextBox.ForeColor = textColor
            self.itemIDTextBox.ForeColor =  textColor
            self.colorTextBox.ForeColor =   textColor
            self.keywordTextBox.Text =      '{}'.format(thingName.title())
            self.itemIDTextBox.Text =       '{}'.format(thingItemID.lower())
            self.colorTextBox.Text =        '{}'.format(thingColor.lower())
            self.targetSourceButton.Text =  'Source: {} ({})'.format(containerName.title(), hex(sourceContainer.Serial))
            if self.colorTextBox.Text == '0x0':
                self.colorTextBox.Text = '0x0000'
            
            Misc.SendMessage('Keyword: {}\nItemID: {}\nColor: {}\nSource: {} ({}) ({})'.format(thingName.title(), thingItemID, thingColor, containerName.title(), hex(sourceContainer.ItemID), hex(sourceContainer.Serial)), 89)
            
        def getContainer():
            Misc.SetSharedValue('containerType', 'normal')
            target = Target.PromptTarget()
            container = Items.FindBySerial(target)
            if container is None:
                container = Mobiles.FindBySerial(target)
                Mobiles.WaitForProps(container, 5000)
                props = Mobiles.GetPropStringList(container)
                if container.IsHuman:
                    if 'banker' in props[0].lower():
                        #Player.ChatSay(89, 'Bank')
                        Misc.UseContextMenu(container.Serial, 'Open Bankbox', 5000)
                        Gumps.WaitForGump(1173999599, 5000)
                        Gumps.SendAction(1173999599, 0)
                        Items.WaitForContents(Player.Bank, 5000)
                        container = Player.Bank
                        Misc.SetSharedValue('containerType', 'bank')
                    elif container.Serial == Player.Serial:
                        Player.ChatSay(89, 'Bank')
                        Items.WaitForContents(Player.Bank, 5000)
                        container = Player.Bank
                        if container is not None:
                            Misc.SetSharedValue('containerType', 'bank')
                        else:
                            Misc.SendMessage('You are outside banking range!\nDefaulting to your main backpack.', 89)
                            container = Player.Backpack
                    elif 'shop name:' in props[1].lower():
                        Misc.SendMessage('You can target a container inside a vendor but cannot target a vendor! \nDefaulting to your main backpack.', 89)
                        container = Player.Backpack
                    else:
                        Misc.SendMessage('{} is not a container! \nDefaulting to your main backpack.'.format(props[0].title()), 89)
                        #container = Player.Backpack
                        #container = container.Backpack
                else:
                    Misc.SendMessage('{} is not a container! \nDefaulting to your main backpack.'.format(props[0].title()), 89)
                    container = Player.Backpack
            else:
                Items.WaitForProps(container, 5000)
                props = Items.GetPropStringList(container)
                if container.IsContainer == False:
                    if 'bank stone' in props[0].lower():
                        Items.UseItem(container)
                        Items.WaitForContents(Player.Bank, 5000)
                        container = Player.Bank
                        Misc.SetSharedValue('containerType', 'bank')
                    elif 'trash 4 tokens' in props[0].lower():
                        Items.UseItem(container)
                    elif 'bones' in props[0].lower():
                        Items.UseItem(container)
                    else:
                        Misc.SendMessage('{} is not a container! \nDefaulting to your main backpack.'.format(props[0].title()), 89)
                        container = Player.Backpack
            
            return container
            
        if sender == self.targetSourceButton:
            container = getContainer()
            type = ''
            getType = Items.FindBySerial(container.Serial)
            if getType:
                type = 'item'
            else:
                type = 'mobile'
            #global sourceContainer
            sourceContainer = container
            Items.WaitForProps(container.Serial, 5000)
            props = Items.GetPropStringList(container.Serial)
            if Misc.ReadSharedValue('containerType') == 'bank':
                name = 'Bank Box'
            elif container.Serial == Player.Backpack.Serial:
                name = 'Main Backpack'
            else:
                if type == 'item':
                    Items.UseItem(container.Serial)
                    Items.WaitForProps(container.Serial, 500)
                    name = Items.GetPropStringByIndex(container.Serial, 0)
                elif type == 'mobile':
                    Mobiles.UseMobile(container.Serial)
                    Mobiles.WaitForProps(container.Serial, 500)
                    name = Mobiles.GetPropStringByIndex(container.Serial, 0)
            if type == 'item':
                contID = container.ItemID
            elif type == 'mobile':
                contID = container.MobileID
            Misc.SendMessage('Source: {} ({}) ({})'.format(name.title(), hex(contID), hex(container.Serial)), 89)
            sender.Text = 'Source: {} ({})'.format(name.title(), hex(container.Serial))
            
        if sender == self.targetDestinationButton:
            container = getContainer()
            type = ''
            getType = Items.FindBySerial(container.Serial)
            if getType:
                type = 'item'
            else:
                type = 'mobile'
            global destinationContainer
            destinationContainer = container
            Items.WaitForProps(container.Serial, 5000)
            props = Items.GetPropStringList(container.Serial)
            if Misc.ReadSharedValue('containerType') == 'bank':
                name = 'Bank Box'
            elif container.Serial == Player.Backpack.Serial:
                name = 'Main Backpack'
            else:
                if type == 'item':
                    Items.UseItem(container.Serial)
                    Items.WaitForProps(container.Serial, 500)
                    name = Items.GetPropStringByIndex(container.Serial, 0)
                elif type == 'mobile':
                    Mobiles.UseMobile(container.Serial)
                    Mobiles.WaitForProps(container.Serial, 500)
                    name = Mobiles.GetPropStringByIndex(container.Serial, 0)
            if type == 'item':
                contID = container.ItemID
            elif type == 'mobile':
                contID = container.MobileID
            Misc.SendMessage('Destination: {} ({}) ({})'.format(name.title(), hex(contID), hex(container.Serial)), 89)
            sender.Text = 'Destination: {} ({})'.format(name.title(), hex(container.Serial))
            
        if sender == self.moveCountButton:
            
            def moveTheThing():
            
                keyword = self.keywordTextBox.Text.lower()
                itemID = self.itemIDTextBox.Text
                while '0x0' in itemID and itemID != '0x0000' and itemID != '[ 0x0000 ]':
                    itemID = itemID.replace('0x0', '0x')
                    Misc.Pause(1)
                color = self.colorTextBox.Text
                while '0x0' in color and color != '0x0000' and color != '[ 0x0000 ]':
                    color = color.replace('0x0', '0x')
                    Misc.Pause(1)
                if color == '0x0000':
                    color = '0x0'
                vendor = self.vendorTextBox.Text
                
                useKeyword =    False
                useItemID =     False
                useColor =      False
                useVendor =     False
                
                if keyword != '' and keyword != ' ' and keyword != '[type a keyword or target a thing]':
                    useKeyword = True
                    #Misc.SendMessage('useKeyword = True', 89)
                if itemID != '' and itemID != ' ' and itemID != '[ 0x0000 ]':
                    useItemID = True
                    #Misc.SendMessage('useItemID = True', 89)
                if color != '' and color != ' ' and color != '[ 0x0000 ]':
                    useColor = True
                    #Misc.SendMessage('useColor = True', 89)
                if vendor != '' and vendor != ' ' and vendor != '[ Vendor Price and Description if Applicable ]':
                    useVendor = True
                    #Misc.SendMessage('useVendor = True', 89)
                
                global thingCount
                thingCount = 0
                global quantity
                if self.quantityTextBox.Text.isdigit():
                    quantity = int(self.quantityTextBox.Text)
                else:
                    quantity = -1
                    
                #filter = Items.Filter()
                #filter.Enabled =    True
                #filter.Name =       thingName
                #thingList = Items.ApplyFilter(filter)
                
                if self.xTextBox.Text.isdigit():
                    global positionX
                    positionX = int(self.xTextBox.Text)
                if self.yTextBox.Text.isdigit():
                    global positionY
                    positionY = int(self.yTextBox.Text)
                    
                self.numberFoundLabel.Text = '# Found: Searching...'
                
                def moveIt(thing):
                    
                    global thingCount
                    global quantity
                    
                    if self.countOnlyCheckBox.Checked == False:
                        if self.xTextBox.Text.isdigit() and self.yTextBox.Text.isdigit():
                            Items.Move(thing, destinationContainer, quantity, positionX, positionY)
                        else:
                            Items.Move(thing, destinationContainer, quantity)
                            
                        Misc.Pause(delay)
                        
                        if useVendor == True:
                            Misc.WaitForPrompt(500)
                            if Misc.HasPrompt():
                                Misc.ResponsePrompt(vendor)
                            #else:
                                #useVendor = False
                                #self.vendorTextBox.Text = '[ Vendor Price and Description if Applicable ]'
                                #self.vendorTextBox.ForeColor = placeholderColor
                        
                    if thing.Amount <= quantity :
                        quantity -= thing.Amount
                        thingCount += thing.Amount
                    else:
                        quantity = 0
                        if self.quantityTextBox.Text.isdigit():
                            thingCount = int(self.quantityTextBox.Text)
                        else:
                            thingCount += thing.Amount
                            
                    self.numberFoundLabel.Text = '# Moved: {:,}'.format(thingCount)
                
                for thing in sourceContainer.Contains:
                    #Misc.SendMessage('{} {}'.format(thing, thingList[0]), 89)
                    #Items.WaitForProps(thing,5000)
                    props = Items.GetPropStringList(thing)
                    propString = ''
                    for prop in props:
                        propString += '{} '.format(prop.lower())
                        Misc.Pause(1)
                        
                    if useKeyword == True and keyword in propString:
                        #Misc.SendMessage('{} == {}\nItemID: {} == {}\nColor: {} == {}'.format(keyword, props[0].lower(), itemID, hex(thing.ItemID), color, hex(thing.Hue)), 89)
                        if useItemID == True and itemID == hex(thing.ItemID) and useColor == True and color == hex(thing.Hue):
                            moveIt(thing)
                            #Misc.SendMessage('True True True', 89)
                        elif useItemID == True and itemID == hex(thing.ItemID) and useColor == False:
                            moveIt(thing)
                            #Misc.SendMessage('True True False', 89)
                        elif useItemID == False and useColor == True and color == hex(thing.Hue):
                            moveIt(thing)
                            #Misc.SendMessage('True False True', 89)
                        elif useItemID == False and useColor == False:
                            moveIt(thing)
                            #Misc.SendMessage('True False False', 89)
                    elif useItemID == True and itemID == hex(thing.ItemID) and useKeyword == False:
                        if useColor == True and color == hex(thing.Hue):
                            moveIt(thing)
                            #Misc.SendMessage('False True True', 89)
                        elif useColor == False:
                            moveIt(thing)
                            #Misc.SendMessage('False True False', 89)
                    elif useColor == True and color == hex(thing.Hue) and useKeyword == False and useItemID == False:
                        moveIt(thing)
                        #Misc.SendMessage('False False True', 89)
                    elif useKeyword == False and useItemID == False and useColor == False:
                        moveIt(thing)
                        #Misc.SendMessage('False False False', 89)
                    
                    if self.quantityTextBox.Text.isdigit():
                        quantityBoxValue = int(self.quantityTextBox.Text)
                    else:
                        quantityBoxValue = -1
                        
                    if self.countOnlyCheckBox.Checked == False and quantityBoxValue > 0 and thingCount >= quantityBoxValue:
                        break
                    Misc.Pause(1)
                    
                if self.countOnlyCheckBox.Checked == False:
                    self.numberFoundLabel.Text = '# Moved: {:,}'.format(thingCount)
                    Misc.SendMessage('Matching items moved: {:,}'.format(thingCount), 89)
                else:
                    self.numberFoundLabel.Text = '# Found: {:,}'.format(thingCount)
                    Misc.SendMessage('Matching items found: {:,}'.format(thingCount), 89)
                        
            Thread(ThreadStart(moveTheThing)).Start()
                
 
    ####################   GOT/LOST FOCUS EVENT HANDLER   ####################
    
    def gotFocusEvents(self, sender, args):
        
        if sender == self.keywordTextBox:
            sender.BackColor = textboxColor
            sender.ForeColor = textColor
            if sender.Text == '[Type a Keyword or Target a Thing]':
                sender.Text = ''
        
        if sender == self.itemIDTextBox:
            sender.BackColor = textboxColor
            sender.ForeColor = textColor
            if sender.Text == '[ 0x0000 ]':
                sender.Text = ''
        
        if sender == self.colorTextBox:
            sender.BackColor = textboxColor
            sender.ForeColor = textColor
            if sender.Text == '[ 0x0000 ]':
                sender.Text = ''
        
        if sender == self.xTextBox:
            sender.BackColor = textboxColor
            sender.ForeColor = textColor
            if sender.Text == 'X':
                sender.Text = ''
        
        if sender == self.yTextBox:
            sender.BackColor = textboxColor
            sender.ForeColor = textColor
            if sender.Text == 'Y':
                sender.Text = ''
        
        if sender == self.quantityTextBox:
            sender.BackColor = textboxColor
            sender.ForeColor = textColor
            if sender.Text == '[ All or # ]':
                sender.Text = ''
        
        if sender == self.vendorTextBox:
            sender.BackColor = textboxColor
            sender.ForeColor = textColor
            if sender.Text == '[ Vendor Price and Description if Applicable ]':
                sender.Text = ''
    
    def lostFocusEvents(self, sender, args):
        
        if sender == self.keywordTextBox:
            if sender.Text == '':
                sender.Text = '[Type a Keyword or Target a Thing]'
                sender.ForeColor = placeholderColor
            else:
                self.thingName = sender.Text
        
        if sender == self.itemIDTextBox:
            if sender.Text == '':
                sender.Text = '[ 0x0000 ]'
                sender.ForeColor = placeholderColor
        
        if sender == self.colorTextBox:
            if sender.Text == '':
                sender.Text = '[ 0x0000 ]'
                sender.ForeColor = placeholderColor
        
        if sender == self.xTextBox:
            if sender.Text == '':
                sender.Text = 'X'
                sender.ForeColor = placeholderColor
        
        if sender == self.yTextBox:
            if sender.Text == '':
                sender.Text = 'Y'
                sender.ForeColor = placeholderColor
        
        if sender == self.quantityTextBox:
            if sender.Text == '':
                sender.Text = '[ All or # ]'
                sender.ForeColor = placeholderColor
        
        if sender == self.vendorTextBox:
            if sender.Text == '':
                sender.Text = '[ Vendor Price and Description if Applicable ]'
                sender.ForeColor = placeholderColor

                    
####################   RUN APP   ####################
Application.EnableVisualStyles()
Application.Run(mainForm())


# TC Vendor Box Serial = 0x403BC625


















