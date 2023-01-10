#############################################################################
# NOTES:                                                                    #
#       You can find me on the RE Discord server as Billy Blacksmith#2276.  #
#                                                                           #
#       See available user settings below.                                  #
#                                                                           #
#############################################################################

import clr #, time, sys, System, math
clr.AddReference('System.Drawing','System.Windows.Forms')
import System.Drawing
from pathlib import Path
from datetime import datetime
from System.Drawing import *
from System.Threading import ThreadStart, Thread
from System.Collections.Generic import List
from System.Windows.Forms import (Application, Button, Form, BorderStyle, Label, FlatStyle, CheckBox, ListBox,
 FormBorderStyle, Orientation, TabControl, TabAlignment, TabPage, FormStartPosition, DockStyle, FormClosingEventHandler,
 FormClosedEventHandler)

####################   USER SETTINGS   ####################
    
positionH           = 500 # Horizontal starting position of the window
positionV           = 500 # Vertical starting position of the window
backgroundColor     = Color.FromArgb(193, 217, 224)
textboxColor        = Color.FromArgb(193, 217, 224)
textColor           = Color.FromArgb(31, 47, 61)
buttonColor         = Color.FromArgb(241, 241, 241)

# Add strings to this list to block messages containing them from showing in this script
# Remove strings from this list to unblock them
# This does not block messages from showing in game
blockMessagesContaining = ['Your arrow hits its mark with velocity!'
                           ,'You claim the corpse and recieve a reward.'
                           ,'mana to perform that attack'
                           ,'You launch two shots at once!'
                           ,'You have not yet recovered from casting a spell.']

####################   APP SETTINGS - DO NOT TOUCH UNLESS YOU KNOW WHAT YOU ARE DOING   ####################

scriptName =            'Journal Spy | {} ({})'.format(Player.Name,Misc.ShardName())
reScriptDirectory =     '{}'.format(Misc.CurrentScriptDirectory())
journalSpyFolder =      'Journal_Spy'
journalSpyDirectory =   '\\'.join([reScriptDirectory, journalSpyFolder])
exportFileName =        'Journal Spy - {} - {} -'.format(Misc.ShardName(),Player.Name)
appSize =               Size(850 + 20, 325)
#font =                  Font('Sans Serif',9)
tabCombinedCounter =    0
tabLocalCounter =       0
tabWorldCounter =       0
tabGuildCounter =       0
tabPartyCounter =       0
tabOtherCounter =       0
previousLocal =         ''
previousWorld =         ''
previousGuild =         ''
previousParty =         ''
previousOther =         ''

Misc.SetSharedValue('run',True)
 
####################   MAIN FORM - START   ####################
    
class mainForm(Form):
                    
    previousLocal = ''
    previousWorld = ''
    previousGuild = ''
    previousParty = ''
    previousOther = ''
    
    def __init__(self):
        #Form.__init__(self)
        self.Text = '{}'.format(scriptName)
        self.BackColor = backgroundColor
        self.ForeColor = textColor
        self.ClientSize = appSize
        self.MinimumSize = appSize
        self.FormBorderStyle = FormBorderStyle.Fixed3D
        self.StartPosition = FormStartPosition.Manual
        self.Location = Point(positionH,positionV)
        self.TopMost = True
        self.FormClosing += self.abortThreads
        self.FormClosed += self.abortThreads
        self.Show()
 
        ####################   DEFINE CONTROLS   ####################
   
        self.localSpeechCheck = CheckBox()
        self.localSpeechCheck.Text = 'Local Speech'
        self.localSpeechCheck.Checked = False
        self.localSpeechCheck.Location = Point(5, 5)
        self.localSpeechCheck.Size = Size(115, 20)
        self.Controls.Add(self.localSpeechCheck)
   
        self.worldChatCheck = CheckBox()
        self.worldChatCheck.Text = 'World Chat'
        self.worldChatCheck.Checked = False
        self.worldChatCheck.Location = Point(5, 25)
        self.worldChatCheck.Size = Size(115, 20)
        self.Controls.Add(self.worldChatCheck)
   
        self.guildChatCheck = CheckBox()
        self.guildChatCheck.Text = 'Guild Chat'
        self.guildChatCheck.Checked = False
        self.guildChatCheck.Location = Point(5, 45)
        self.guildChatCheck.Size = Size(115, 20)
        self.Controls.Add(self.guildChatCheck)
   
        self.partyChatCheck = CheckBox()
        self.partyChatCheck.Text = 'Party Chat'
        self.partyChatCheck.Checked = False
        self.partyChatCheck.Location = Point(5, 65)
        self.partyChatCheck.Size = Size(115, 20)
        self.Controls.Add(self.partyChatCheck)
   
        self.adminsCheck = CheckBox()
        self.adminsCheck.Text = '+Admins'
        self.adminsCheck.Checked = True
        self.adminsCheck.Location = Point(5, 85)
        self.adminsCheck.Size = Size(115, 20)
        self.Controls.Add(self.adminsCheck)
   
        self.levelUpsCheck = CheckBox()
        self.levelUpsCheck.Text = 'Pet/Weap Level'
        self.levelUpsCheck.Checked = True
        self.levelUpsCheck.Location = Point(5, 105)
        self.levelUpsCheck.Size = Size(115, 20)
        self.Controls.Add(self.levelUpsCheck)
   
        self.combatCheck = CheckBox()
        self.combatCheck.Text = 'Combat'
        self.combatCheck.Checked = False
        self.combatCheck.Location = Point(5, 125)
        self.combatCheck.Size = Size(115, 20)
        self.Controls.Add(self.combatCheck)
   
        self.loggedInOutCheck = CheckBox()
        self.loggedInOutCheck.Text = 'Logged In / Out'
        self.loggedInOutCheck.Checked = False
        self.loggedInOutCheck.Location = Point(5, 145)
        self.loggedInOutCheck.Size = Size(115, 20)
        self.Controls.Add(self.loggedInOutCheck)
   
        self.coreMacroCheck = CheckBox()
        self.coreMacroCheck.Text = 'Core / Macro'
        self.coreMacroCheck.Checked = False
        self.coreMacroCheck.Location = Point(5, 165)
        self.coreMacroCheck.Size = Size(115, 20)
        self.Controls.Add(self.coreMacroCheck)
   
        self.newestMemberCheck = CheckBox()
        self.newestMemberCheck.Text = 'Newest Member'
        self.newestMemberCheck.Checked = False
        self.newestMemberCheck.Location = Point(5, 185)
        self.newestMemberCheck.Size = Size(115, 20)
        self.Controls.Add(self.newestMemberCheck)
   
        self.stealthStepsCheck = CheckBox()
        self.stealthStepsCheck.Text = 'Stealth Steps'
        self.stealthStepsCheck.Checked = False
        self.stealthStepsCheck.Location = Point(5, 205)
        self.stealthStepsCheck.Size = Size(115, 20)
        self.Controls.Add(self.stealthStepsCheck)
   
        self.youSeeCheck = CheckBox()
        self.youSeeCheck.Text = 'Character Names'
        self.youSeeCheck.Checked = False
        self.youSeeCheck.Location = Point(5, 225)
        self.youSeeCheck.Size = Size(115, 20)
        self.Controls.Add(self.youSeeCheck)
   
        self.worldSaveCheck = CheckBox()
        self.worldSaveCheck.Text = 'World Save'
        self.worldSaveCheck.Checked = False
        self.worldSaveCheck.Location = Point(5, 245)
        self.worldSaveCheck.Size = Size(115, 20)
        self.Controls.Add(self.worldSaveCheck)
   
        self.deathRollCheck = CheckBox()
        self.deathRollCheck.Text = 'Death Roll'
        self.deathRollCheck.Checked = False
        self.deathRollCheck.Location = Point(5, 265)
        self.deathRollCheck.Size = Size(115, 20)
        self.Controls.Add(self.deathRollCheck)
   
        self.miscCheck = CheckBox()
        self.miscCheck.Text = 'Miscellaneous'
        self.miscCheck.Checked = False
        self.miscCheck.Location = Point(5, 285)
        self.miscCheck.Size = Size(115, 20)
        self.Controls.Add(self.miscCheck)

        self.exportButton = Button()
        if Path(journalSpyDirectory).exists():
            self.exportButton.Text = 'Export All Checked'
        else:
            self.exportButton.Text = 'Enable Export to File'
        self.exportButton.BackColor = buttonColor
        self.exportButton.Location = Point(120, 295)
        self.exportButton.Size = Size(150, 25)
        self.exportButton.FlatStyle = FlatStyle.Flat
        self.exportButton.FlatAppearance.BorderSize = 1 
        self.exportButton.Click += self.btnPressedEvent
        self.Controls.Add(self.exportButton)
   
        self.autoScroll = CheckBox()
        self.autoScroll.Text = 'Auto-scroll'
        self.autoScroll.Checked = True
        self.autoScroll.Location = Point(793, 298)
        self.autoScroll.Size = Size(77, 20)
        self.Controls.Add(self.autoScroll)
   
        self.systemNotification = Label()
        self.systemNotification.Text = ''
        self.systemNotification.ForeColor = textColor
        self.systemNotification.Location = Point(270, 301)
        self.systemNotification.Size = Size(540, 20)
        self.Controls.Add(self.systemNotification)
 
        ####################   TAB CONTROLS - START   ####################
        
        self.tabControl = TabControl()        
        self.tabControl.Location = Point(120, 0)
        self.tabControl.Size = Size(750, 290)
        self.tabControl.Alignment = TabAlignment.Top
        self.tabControl.SelectedIndexChanged += self.tabSelectedEvent
        self.Controls.Add(self.tabControl)
 
        ####################   DEFINE TAB 1   ####################
        
        self.tabCombined = TabPage()
        self.tabCombined.Text = '← All Checked'
        self.tabCombined.BackColor = backgroundColor
        self.tabControl.TabPages.Add(self.tabCombined)
        
        self.chatBoxCombined = ListBox()
        self.chatBoxCombined.Dock = DockStyle.Fill
        self.chatBoxCombined.BackColor = textboxColor
        #self.chatBoxCombined.Font = font
        self.chatBoxCombined.ForeColor = textColor
        self.chatBoxCombined.HorizontalScrollbar = True
        self.tabCombined.Controls.Add(self.chatBoxCombined)
 
        ####################   DEFINE TAB 2   ####################
        
        self.tabLocal = TabPage()
        self.tabLocal.Text = 'Local Speech'
        self.tabLocal.BackColor = backgroundColor
        self.tabControl.TabPages.Add(self.tabLocal)
        
        self.chatBoxLocal = ListBox()
        self.chatBoxLocal.Dock = DockStyle.Fill
        self.chatBoxLocal.BackColor = textboxColor
        #self.chatBoxLocal.Font = font
        self.chatBoxLocal.ForeColor = textColor
        self.chatBoxLocal.HorizontalScrollbar = True
        self.tabLocal.Controls.Add(self.chatBoxLocal)
 
        ####################   DEFINE TAB 3   ####################
        
        self.tabWorld = TabPage()
        self.tabWorld.Text = 'World Chat'
        self.tabWorld.BackColor = backgroundColor
        self.tabControl.TabPages.Add(self.tabWorld)
        
        self.chatBoxWorld = ListBox()
        self.chatBoxWorld.Dock = DockStyle.Fill
        self.chatBoxWorld.BackColor = textboxColor
        #self.chatBoxWorld.Font = font
        self.chatBoxWorld.ForeColor = textColor
        self.chatBoxWorld.HorizontalScrollbar = True
        self.tabWorld.Controls.Add(self.chatBoxWorld)
 
        ####################   DEFINE TAB 4   ####################
        
        self.tabGuild = TabPage()
        self.tabGuild.Text = 'Guild Chat'
        self.tabGuild.BackColor = backgroundColor
        self.tabControl.TabPages.Add(self.tabGuild)
        
        self.chatBoxGuild = ListBox()
        self.chatBoxGuild.Dock = DockStyle.Fill
        self.chatBoxGuild.BackColor = textboxColor
        #self.chatBoxGuild.Font = font
        self.chatBoxGuild.ForeColor = textColor
        self.chatBoxGuild.HorizontalScrollbar = True
        self.tabGuild.Controls.Add(self.chatBoxGuild)
 
        ####################   DEFINE TAB 5   ####################
        
        self.tabParty = TabPage()
        self.tabParty.Text = 'Party Chat'
        self.tabParty.BackColor = backgroundColor
        self.tabControl.TabPages.Add(self.tabParty)
        
        self.chatBoxParty = ListBox()
        self.chatBoxParty.Dock = DockStyle.Fill
        self.chatBoxParty.BackColor = textboxColor
        #self.chatBoxParty.Font = font
        self.chatBoxParty.ForeColor = textColor
        self.chatBoxParty.HorizontalScrollbar = True
        self.tabParty.Controls.Add(self.chatBoxParty)
 
        ####################   DEFINE TAB 6   ####################
        
        self.tabOther = TabPage()
        self.tabOther.Text = 'Other'
        self.tabOther.BackColor = backgroundColor
        self.tabControl.TabPages.Add(self.tabOther)
        
        self.chatBoxOther = ListBox()
        self.chatBoxOther.Dock = DockStyle.Fill
        self.chatBoxOther.BackColor = textboxColor
        #self.chatBoxOther.Font = font
        self.chatBoxOther.ForeColor = textColor
        self.chatBoxOther.HorizontalScrollbar = True
        self.tabOther.Controls.Add(self.chatBoxOther)
        
        ####################   TAB CONTROLS - END   ####################
        
        self.Shown += self.startManager
        
    ####################   MAIN FORM - END   ####################
    

####################   EVENT HANDLERS / THREAD MANAGEMENT   ####################

####################   TAB SELECTION EVENT HANDLER   ####################
        
    def tabSelectedEvent(self,sender,args):
        
        if self.tabControl.SelectedIndex == 0:
            if Path(journalSpyDirectory).exists():
                self.exportButton.Text = 'Export All Checked'
            self.tabCombined.Text = '← All Checked'
            global tabCombinedCounter
            tabCombinedCounter = 0
        
        elif self.tabControl.SelectedIndex == 1:
            if Path(journalSpyDirectory).exists():
                self.exportButton.Text = 'Export Local Speech'
            self.tabLocal.Text = 'Local Speech'
            global tabLocalCounter
            tabLocalCounter = 0
        
        elif self.tabControl.SelectedIndex == 2:
            if Path(journalSpyDirectory).exists():
                self.exportButton.Text = 'Export World Chat'
            self.tabWorld.Text = 'World Chat'
            global tabWorldCounter
            tabWorldCounter = 0
        
        elif self.tabControl.SelectedIndex == 3:
            if Path(journalSpyDirectory).exists():
                self.exportButton.Text = 'Export Guild Chat'
            self.tabGuild.Text = 'Guild Chat'
            global tabGuildCounter
            tabGuildCounter = 0
        
        elif self.tabControl.SelectedIndex == 4:
            if Path(journalSpyDirectory).exists():
                self.exportButton.Text = 'Export Party Chat'
            self.tabParty.Text = 'Party Chat'
            global tabPartyCounter
            tabPartyCounter = 0
        
        elif self.tabControl.SelectedIndex == 5:
            if Path(journalSpyDirectory).exists():
                self.exportButton.Text = 'Export Other'
            self.tabOther.Text = 'Other'
            global tabOtherCounter
            tabOtherCounter = 0

####################   FILE CREATOR   ####################
                
    def fileCreator(self, tabName, chatBox):
        
        timeStamp = datetime.now().strftime('%m%d%Y %H%M%S')
        fileName =  '{} {} - {}.txt'.format(exportFileName, tabName, timeStamp)
        theFile =   '\\'.join([journalSpyDirectory, fileName])
        file = open(theFile, 'w+')
        if Path(theFile).exists():
            self.systemNotification.ForeColor = textColor
            self.systemNotification.Text = 'File saved to: {}'.format(journalSpyDirectory)
            
            for item in chatBox.Items:
                
                file.write(''.join(item))
                file.write('\n')
        else:
            self.systemNotification.ForeColor = Color.FromArgb(225, 0, 0)
            self.systemNotification.Text = 'The file was not created successfully.'
            
        file.close()
        

####################   BUTTON PRESSED EVENT HANDLER   ####################
        
    def btnPressedEvent(self, sender, args):
        
        if sender == self.exportButton:
            
            if sender.Text == 'Enable Export to File':
                self.exportButton.Text = 'Create Subfolder'
   
                self.systemNotification.ForeColor = Color.FromArgb(225, 0, 0)
                self.systemNotification.Text = '*** Subfolder \'Journal_Spy\' is required in the RE script folder. Click \'Create Subfolder\' to continue. ***'
                
            elif sender.Text == 'Create Subfolder':
                Path(journalSpyDirectory).mkdir(True, True)
                
                if Path(journalSpyDirectory).exists():
                    if self.tabControl.SelectedIndex == 0:
                        self.exportButton.Text = 'Export All Checked'
                    elif self.tabControl.SelectedIndex == 1:
                        self.exportButton.Text = 'Export Local Speech'
                    elif self.tabControl.SelectedIndex == 2:
                        self.exportButton.Text = 'Export World Chat'
                    elif self.tabControl.SelectedIndex == 3:
                        self.exportButton.Text = 'Export Guild Chat'
                    elif self.tabControl.SelectedIndex == 4:
                        self.exportButton.Text = 'Export Party Chat'
                    elif self.tabControl.SelectedIndex == 5:
                        self.exportButton.Text = 'Export Other'
                    
                    self.systemNotification.ForeColor = textColor
                    self.systemNotification.Text = 'Exporting Enabled to: {}'.format(journalSpyDirectory)
            
            elif sender.Text == 'Export All Checked':
                #Player.HeadMessage(89, '{}'.format(reScriptDirectory))
                if Path(journalSpyDirectory).exists():
                    self.fileCreator(sender.Text, self.chatBoxCombined)
            
            elif sender.Text == 'Export Local Speech':
                #Player.HeadMessage(89, '{}'.format(reScriptDirectory))
                if Path(journalSpyDirectory).exists():
                    self.fileCreator(sender.Text, self.chatBoxLocal)
            
            elif sender.Text == 'Export World Chat':
                #Player.HeadMessage(89, '{}'.format(reScriptDirectory))
                if Path(journalSpyDirectory).exists():
                    self.fileCreator(sender.Text, self.chatBoxWorld)
            
            elif sender.Text == 'Export Guild Chat':
                #Player.HeadMessage(89, '{}'.format(reScriptDirectory))
                if Path(journalSpyDirectory).exists():
                    self.fileCreator(sender.Text, self.chatBoxGuild)
            
            elif sender.Text == 'Export Party Chat':
                #Player.HeadMessage(89, '{}'.format(reScriptDirectory))
                if Path(journalSpyDirectory).exists():
                    self.fileCreator(sender.Text, self.chatBoxParty)
            
            elif sender.Text == 'Export Other':
                #Player.HeadMessage(89, '{}'.format(reScriptDirectory))
                if Path(journalSpyDirectory).exists():
                    self.fileCreator(sender.Text, self.chatBoxOther)

####################   CHECK BOX HANDLER   ####################

    def startManager(self,s,a):
        
        def threadManager():
    
            runningThreads = []
    
            ####################   READ JOURNAL THREAD   ####################
            
            global lastLine
            lastLine = None
            
            def readJournal():
                
                ####################   UNREAD MESSAGES TAB COUNTERS   ####################

                def tabUnreadCounters(tabIndex):
                    
                    if tabIndex == 0:
                        global tabCombinedCounter
                        tabCombinedCounter += 1
                        self.tabCombined.Text = '← All Checked ({})'.format(tabCombinedCounter)
            
                    elif tabIndex == 1:
                        global tabLocalCounter
                        tabLocalCounter += 1
                        self.tabLocal.Text = 'Local Speech ({})'.format(tabLocalCounter)
                    
                    elif tabIndex == 2:
                        global tabWorldCounter
                        tabWorldCounter += 1
                        self.tabWorld.Text = 'World Chat ({})'.format(tabWorldCounter)
                    
                    elif tabIndex == 3:
                        global tabGuildCounter
                        tabGuildCounter += 1
                        self.tabGuild.Text = 'Guild Chat ({})'.format(tabGuildCounter)
                    
                    elif tabIndex == 4:
                        global tabPartyCounter
                        tabPartyCounter += 1
                        self.tabParty.Text = 'Party Chat ({})'.format(tabPartyCounter)
                    
                    elif tabIndex == 5:
                        global tabOtherCounter
                        tabOtherCounter += 1
                        self.tabOther.Text = 'Other ({})'.format(tabOtherCounter)
                
                ####################   HANDLE JOURNAL ENTRIES   ####################
                
                def processJournalEntry(chatBox, entry, tabIndex, checkBox):
                    
                    currentEntry = '{}{}'.format(chatBox, entry)
                    
                    blockMessage = False
                    for message in blockMessagesContaining:
                        if message in entry:
                            blockMessage = True
                            break
                            
                    if blockMessage == False and currentEntry != self.previousLocal and currentEntry != self.previousWorld and currentEntry != self.previousGuild and currentEntry != self.previousParty and currentEntry != self.previousOther:
                        timeStamp = datetime.now().strftime('%m/%d  %X')
                        formattedEntry = '{}  {}'.format(timeStamp,entry)
                        chatBox.Items.Add(formattedEntry)
                        
                        if chatBox == self.chatBoxLocal:
                            self.previousLocal = '{}{}'.format(chatBox, entry)
                        elif chatBox == self.chatBoxWorld:
                            self.previousWorld = '{}{}'.format(chatBox, entry)
                        elif chatBox == self.chatBoxGuild:
                            self.previousGuild = '{}{}'.format(chatBox, entry)
                        elif chatBox == self.chatBoxParty:
                            self.previousParty = '{}{}'.format(chatBox, entry)
                        elif chatBox == self.chatBoxOther:
                            self.previousOther = '{}{}'.format(chatBox, entry)
                        
                        if self.autoScroll.Checked == True:
                            boxCount = chatBox.Items.Count
                            boxIndex = boxCount - 1
                            chatBox.SetSelected(boxIndex, True)
                            
                        if self.tabControl.SelectedIndex != tabIndex:
                            tabUnreadCounters(tabIndex)
                            
                        if checkBox.Checked == True:
                            self.chatBoxCombined.Items.Add(formattedEntry)
                            
                            if self.autoScroll.Checked == True:
                                boxCount = self.chatBoxCombined.Items.Count
                                boxIndex = boxCount - 1
                                self.chatBoxCombined.SetSelected(boxIndex, True)
                                
                            if self.tabControl.SelectedIndex != 0:
                                tabUnreadCounters(0)
                
                
                global lastLine
                journalBuffer = Journal.GetJournalEntry(lastLine)
                journalBufferList = list(journalBuffer)
                if len(journalBufferList) > 0:
                    lastLine = journalBufferList[-1]
                if len(journalBuffer) > 0:
                    
                    for entry in journalBuffer:
                        
                        if entry.Type == 'System':
                        
                            if '<' in entry.Text and '> ' in entry.Text:
                                    
                                if '> +' in entry.Text:
                                    processJournalEntry(self.chatBoxWorld, entry.Text, 2, self.adminsCheck)
                                    
                                elif ('<Public> ' in entry.Text or '<Trade> ' in entry.Text):
                                    processJournalEntry(self.chatBoxWorld, entry.Text, 2, self.worldChatCheck)
                                    
                                #elif '<Party> ' in entry.Text:
                                    #processJournalEntry(self.chatBoxParty, entry.Text, 4, self.partyChatCheck)
                                    
                                elif '<ESC> to cancel' in entry.Text:
                                    processJournalEntry(self.chatBoxOther, entry.Text, 5, self.miscCheck)
                                    
                                else:
                                    processJournalEntry(self.chatBoxGuild, entry.Text, 3, self.guildChatCheck)
                        
                            elif 'You see:' in entry.Text:
                                processJournalEntry(self.chatBoxOther, entry.Text, 5, self.youSeeCheck)
                                    
                            elif 'enveloped by a noxious gas' in entry.Text or 'stepped onto a blade trap' in entry.Text or 'stepped onto a spike trap' in entry.Text or 'feel pain throughout your body' in entry.Text or ((' a ' in entry.Text or ' an ' in entry.Text or '\'s ' in entry.Text) and 'corpse' in entry.Text) or 'damage has been healed' in entry.Text or 'wracked with extreme pain' in entry.Text or 'around in confusion and pain' in entry.Text or (': a ' in entry.Text and 'corpse' in entry.Text) or ('You received' in entry.Text and 'tokens.' in entry.Text) or 'Your deeds in the city of' in entry.Text or 'You deliver a mortal wound' in entry.Text or 'You play jarring music,' in entry.Text or 'You heal what little damage' in entry.Text or 'You attempt to disrupt' in entry.Text or 'Choose the target for ' in entry.Text or 'You pierce your opponent' in entry.Text or 'You launch two shots at ' in entry.Text or 'You have delivered a conc' in entry.Text or 'The whirling attack strike' in entry.Text or 'You are bleeding!' in entry.Text or 'That being is not damaged' in entry.Text or 'You have been cured of all' in entry.Text or 'Some damage has been healed' in entry.Text or 'You finish applying the ' in entry.Text or 'You begin applying the ' in entry.Text or 'You did not earn the right' in entry.Text or 'Warmode dismount blocked.' in entry.Text or 'Choose a corpse to claim' in entry.Text or 'Choose another corpse to' in entry.Text or 'As a reward for slaying ' in entry.Text or 'You have delivered a crushing' in entry.Text or 'Your concentration is ' in entry.Text or 'bleeding profusely' in entry.Text or 're already casting a spell.' in entry.Text or 'vered from casting a spell.' in entry.Text or 'corpse and receive a reward.' in entry.Text or 'and are in severe pain!' in entry.Text or 'you are no longer bleeding!' in entry.Text or 'You must have at least' in entry.Text or 'spasm uncontrollably' in entry.Text or 'can breathe normally' in entry.Text or 'resisting magical energy' in entry.Text or 'target is not affected' in entry.Text or 'Oath has been broken' in entry.Text or 'dry and corpselike' in entry.Text or 'looks ill' in entry.Text or 'hits its mark with velocity' in entry.Text or 'Your target is bleeding' in entry.Text or 'looks extrememly ill' in entry.Text or '%]' in entry.Text or 't claim a corpse you did not kill' in entry.Text or 'You are too far away to claim that corpse' in entry.Text or 'You feel a bit nauseous' in entry.Text or 'You are in extreme pain,' in entry.Text or 'You feel disoriented and nauseous' in entry.Text or 'poison seems to have no effect' in entry.Text or 'looks extremely ill.' in entry.Text or 'seems resistant to the poison' in entry.Text or '*You feel a bit nauseous*' in entry.Text:
                                processJournalEntry(self.chatBoxOther, entry.Text, 5, self.combatCheck)
                            
                            elif '] +' in entry.Text or '> +' in entry.Text or '] Announcement by +' in entry.Text or 'Staff message from +' in entry.Text or '] +' in entry.Text:
                                processJournalEntry(self.chatBoxWorld, entry.Text, 2, self.adminsCheck)
                            
                            elif ('is being invaded by' in entry.Text and '. Please come help!' in entry.Text) or ('is safe!' in entry.Text and 'has been defeated!' in entry.Text) or ('has been protected but' in entry.Text and 'for the final battle!' in entry.Text):
                                processJournalEntry(self.chatBoxWorld, entry.Text, 2, self.miscCheck)
                                    
                            elif ' has logged ' in entry.Text:
                                processJournalEntry(self.chatBoxOther, entry.Text, 5, self.loggedInOutCheck)
                                    
                            elif 'The world will save in ' in entry.Text or 'The world is saving, please wait.' in entry.Text or 'No Current News' in entry.Text or 'World save complete. ' in entry.Text or 'Power Save! All players online ' in entry.Text or 'Power Save! All online players ' in entry.Text:
                                processJournalEntry(self.chatBoxOther, entry.Text, 5, self.worldSaveCheck)
                                    
                            elif 'Your strength has changed' in entry.Text or 'Your dexterity has changed' in entry.Text or 'Your intelligence has changed' in entry.Text or 'Your skill in' in entry.Text or 'has gained a level' in entry.Text:
                                processJournalEntry(self.chatBoxOther, entry.Text, 5, self.levelUpsCheck)
                                    
                            elif 'Pray, bretheren' in entry.Text or 'Alas, poor' in entry.Text or 'Another soul has' in entry.Text or 'Rest in peace,' in entry.Text or 'We mourn the passing' in entry.Text or ' is heard throughout the land.' in entry.Text or 'shall arise again for vengance!' in entry.Text or ' the regions beyond the grave.' in entry.Text or 'has fallen victim to' in entry.Text or 'shall rise again for vengance' in entry.Text or 'has been slain in a br' in entry.Text or 'inflicted the final wo' in entry.Text or ('couldn' in entry.Text and 't withstand' in entry.Text) or 'has lost their life in battle to' in entry.Text or 'has succumbed to their wounds and has perished' in entry.Text or 'may god have mercy on your soul' in entry.Text or 'Death comes for us all, but on this day, for' in entry.Text:
                                processJournalEntry(self.chatBoxOther, entry.Text, 5, self.deathRollCheck)
                                    
                            elif 'elcome the newest member ' in entry.Text:
                                processJournalEntry(self.chatBoxOther, entry.Text, 5, self.newestMemberCheck)
                                    
                            elif 'Stealth steps' in entry.Text or 'You begin to move quietely' in entry.Text:
                                processJournalEntry(self.chatBoxOther, entry.Text, 5, self.stealthStepsCheck)
                            
                            elif ' : ' in entry.Text or 'hidden yourself well' in entry.Text or 'seem to hide right now' in entry.Text:
                                processJournalEntry(self.chatBoxOther, entry.Text, 5, self.miscCheck)
                        
                            else: # This is the catch-all for everything else
                                processJournalEntry(self.chatBoxOther, entry.Text, 5, self.miscCheck)
                            
                        elif entry.Type == 'Guild':
                            formattedEntry = '[Guild] {}: {}'.format(entry.Name, entry.Text)
                            processJournalEntry(self.chatBoxGuild, formattedEntry, 3, self.guildChatCheck)
                            
                        elif entry.Type == 'Party':
                            formattedEntry = '[Party] {}: {}'.format(entry.Name, entry.Text)
                            processJournalEntry(self.chatBoxParty, formattedEntry, 4, self.partyChatCheck)
                            
                        elif entry.Type == 'Regular':
                            formattedEntry = '{}: {}'.format(entry.Name, entry.Text)
                            if 'enveloped by a noxious gas' in entry.Text or 'stepped onto a blade trap' in entry.Text or 'stepped onto a spike trap' in entry.Text or 'feel pain throughout your body' in entry.Text or ((' a ' in entry.Text or ' an ' in entry.Text or '\'s ' in entry.Text) and 'corpse' in entry.Text) or 'damage has been healed' in entry.Text or 'wracked with extreme pain' in entry.Text or 'around in confusion and pain' in entry.Text or (': a ' in entry.Text and 'corpse' in entry.Text) or ('You received' in entry.Text and 'tokens.' in entry.Text) or 'Your deeds in the city of' in entry.Text or 'You deliver a mortal wound' in entry.Text or 'You play jarring music,' in entry.Text or 'You heal what little damage' in entry.Text or 'You attempt to disrupt' in entry.Text or 'Choose the target for ' in entry.Text or 'You pierce your opponent' in entry.Text or 'You launch two shots at ' in entry.Text or 'You have delivered a conc' in entry.Text or 'The whirling attack strike' in entry.Text or 'You are bleeding!' in entry.Text or 'That being is not damaged' in entry.Text or 'You have been cured of all' in entry.Text or 'Some damage has been healed' in entry.Text or 'You finish applying the ' in entry.Text or 'You begin applying the ' in entry.Text or 'You did not earn the right' in entry.Text or 'Warmode dismount blocked.' in entry.Text or 'Choose a corpse to claim' in entry.Text or 'Choose another corpse to' in entry.Text or 'As a reward for slaying ' in entry.Text or 'You have delivered a crushing' in entry.Text or 'Your concentration is ' in entry.Text or 'bleeding profusely' in entry.Text or 're already casting a spell.' in entry.Text or 'vered from casting a spell.' in entry.Text or 'corpse and receive a reward.' in entry.Text or 'and are in severe pain!' in entry.Text or 'you are no longer bleeding!' in entry.Text or 'You must have at least' in entry.Text or 'spasm uncontrollably' in entry.Text or 'can breathe normally' in entry.Text or 'resisting magical energy' in entry.Text or 'target is not affected' in entry.Text or 'Oath has been broken' in entry.Text or 'dry and corpselike' in entry.Text or 'looks ill' in entry.Text or 'hits its mark with velocity' in entry.Text or 'Your target is bleeding' in entry.Text or 'looks extrememly ill' in entry.Text or '%]' in entry.Text or 't claim a corpse you did not kill' in entry.Text or 'You are too far away to claim that corpse' in entry.Text or 'You feel a bit nauseous' in entry.Text or 'You are in extreme pain,' in entry.Text or 'You feel disoriented and nauseous' in entry.Text or 'poison seems to have no effect' in entry.Text or 'looks extremely ill.' in entry.Text or 'seems resistant to the poison' in entry.Text or '*You feel a bit nauseous*' in entry.Text:
                                processJournalEntry(self.chatBoxOther, formattedEntry, 5, self.combatCheck)
                            elif ' : ' in entry.Text or 'lock quickly yields' in entry.Text or 'appears to be locked.' in entry.Text or 'make anything of the map' in entry.Text or 'decode a treasure map' in entry.Text or 'marked by the red pin' in entry.Text or 'hidden yourself well' in entry.Text or 'seem to hide right now' in entry.Text:
                                processJournalEntry(self.chatBoxOther, formattedEntry, 5, self.miscCheck)
                            else:
                                processJournalEntry(self.chatBoxLocal, formattedEntry, 1, self.localSpeechCheck)
                            
                        elif entry.Type == 'Emote':
                            formattedEntry = '{}: *Emote* {}'.format(entry.Name, entry.Text)
                            if 'poison seems to have no effect' in entry.Text or 'seems resistant to the poison' in entry.Text:
                                processJournalEntry(self.chatBoxOther, formattedEntry, 5, self.combatCheck)
                            elif 'begins taming a creature' in entry.Text:
                                processJournalEntry(self.chatBoxOther, formattedEntry, 5, self.miscCheck)
                            else:
                                processJournalEntry(self.chatBoxLocal, formattedEntry, 1, self.localSpeechCheck)
                            
                        elif entry.Type == 'Label':
                            formattedEntry = 'You see: {}'.format(entry.Text)
                            processJournalEntry(self.chatBoxOther, formattedEntry, 5, self.youSeeCheck)
                            
                        elif entry.Type == 'Focus':
                            formattedEntry = '***FOCUS TYPE***{}: {}'.format(entry.Name, entry.Text)
                            processJournalEntry(self.chatBoxOther, formattedEntry, 5, self.miscCheck)
                            
                        elif entry.Type == 'Whisper':
                            formattedEntry = '{}: *Whisper* {}'.format(entry.Name, entry.Text)
                            processJournalEntry(self.chatBoxLocal, formattedEntry, 1, self.localSpeechCheck)
                            
                        elif entry.Type == 'Yell':
                            formattedEntry = '{}: *Yell* {}'.format(entry.Name, entry.Text)
                            processJournalEntry(self.chatBoxLocal, formattedEntry, 1, self.localSpeechCheck)
                            
                        elif entry.Type == 'Spell':
                            formattedEntry = '{}: {}'.format(entry.Name, entry.Text)
                            processJournalEntry(self.chatBoxOther, formattedEntry, 5, self.miscCheck)
                            
                        elif entry.Type == 'Alliance':
                            formattedEntry = '[Alliance] {}: {}'.format(entry.Name, entry.Text)
                            processJournalEntry(self.chatBoxOther, formattedEntry, 5, self.miscCheck)
                            
                        elif entry.Type == 'Encoded':
                            formattedEntry = '***ENCODED TYPE***{}: {}'.format(entry.Name, entry.Text)
                            processJournalEntry(self.chatBoxOther, formattedEntry, 5, self.miscCheck)
                            
                        elif entry.Type == 'Special':
                            formattedEntry = '***SPECIAL TYPE***{}: {}'.format(entry.Name, entry.Text)
                            processJournalEntry(self.chatBoxOther, formattedEntry, 5, self.miscCheck)
                            
                    
                runningThreads.remove('readJournal')
                    
                
            ####################   THREAD STARTER   ####################

            while Misc.ReadSharedValue('run') == True:
                if not 'readJournal' in runningThreads:
                    runningThreads.append('readJournal')
                    Thread(ThreadStart(readJournal)).Start()
                    
                Misc.Pause(50)

        Thread(ThreadStart(threadManager)).Start()
                    
    ####################   THREAD STOPPER   ####################
        
    def abortThreads(self, sender, args):
        Misc.SetSharedValue('run',False)
        #Thread(ThreadStart(readJournal)).Abort()
        #Thread(ThreadStart(threadManager)).Abort()
                    
####################   RUN APP   ####################
    
#for item in blockMessagesContaining:
    #Journal.FilterText(item)
    
Application.EnableVisualStyles()
Application.Run(mainForm())
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    