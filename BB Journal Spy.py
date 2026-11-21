#############################################################################
# NOTES:                                                                    #
#       You can find me on the RE Discord server as Billy Blacksmith#2276.  #
#                                                                           #
#       See available user settings below.                                  #
#                                                                           #
#############################################################################

import clr
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')

import re
from datetime import datetime, timedelta
from System import Action, Array
from System.ComponentModel import ListSortDirection
from System.IO import Directory, File
from System.IO import Path as IOPath
from System.Reflection import BindingFlags
from System.Text import UTF8Encoding
from System.Threading import ApartmentState, Thread, ThreadStart
from System.Drawing import Color, Point, Size
from System.Windows.Forms import (AnchorStyles, Application, Button, CheckBox, Clipboard, ContextMenuStrip,
    DataGridView, DataGridViewAutoSizeColumnMode, DataGridViewCellBorderStyle, DataGridViewCellStyle,
    DataGridViewClipboardCopyMode, DataGridViewColumnSortMode, DataGridViewContentAlignment,
    DataGridViewSelectionMode, DataGridViewTextBoxColumn, DockStyle, FlatStyle, Form, FormBorderStyle,
    FormStartPosition, Keys, Label, MouseButtons, SortOrder, TabAlignment, TabControl, TabPage,
    ToolStripMenuItem)

####################   USER SETTINGS   ####################

positionH           = 500 # Horizontal starting position of the window
positionV           = 500 # Vertical starting position of the window
backgroundColor     = Color.FromArgb(193, 217, 224)
textboxColor        = Color.FromArgb(193, 217, 224)
textColor           = Color.FromArgb(31, 47, 61)
buttonColor         = Color.FromArgb(241, 241, 241)
gridLineColor       = Color.FromArgb(168, 193, 202)

maxLinesPerTab      = 5000 # Oldest lines are dropped past this so memory use and redraw time stay flat
duplicateWindowSecs = 3    # An identical line in the same tab within this many seconds is skipped (0 = never skip)
pollIntervalMs      = 100  # How often the journal is read, in milliseconds

# Column widths in pixels. 0 = the column fills the remaining width.
# If more than one column is 0, those columns share the remaining width equally.
# If none is 0, every column keeps its width and any extra space stays empty.
timeColumnWidth     = 90
typeColumnWidth     = 50
speakerColumnWidth  = 80
messageColumnWidth  = 0

# Type cell colors: type label -> (cell color, text color)
# Types not listed here use the normal grid colors
white = Color.White
dark  = Color.FromArgb(31, 47, 61)
typeColors = {
    'Staff':      (Color.FromArgb(190, 30, 45),   white),
    'Public':     (Color.FromArgb(40, 100, 190),  white),
    'Trade':      (Color.FromArgb(150, 95, 20),   white),
    'Guild':      (Color.FromArgb(35, 130, 60),   white),
    'Alliance':   (Color.FromArgb(20, 115, 120),  white),
    'Party':      (Color.FromArgb(115, 60, 165),  white),
    'Say':        (Color.FromArgb(240, 240, 240), dark),
    'Emote':      (Color.FromArgb(215, 215, 215), dark),
    'Whisper':    (Color.FromArgb(105, 105, 105), white),
    'Yell':       (Color.FromArgb(215, 110, 20),  white),
    'Combat':     (Color.FromArgb(140, 35, 35),   white),
    'Death':      (Color.FromArgb(40, 40, 40),    white),
    'Invasion':   (Color.FromArgb(225, 75, 0),    white),
    'Save':       (Color.FromArgb(85, 85, 135),   white),
    'Level Up':   (Color.FromArgb(225, 180, 40),  dark),
    'Login':      (Color.FromArgb(120, 140, 150), white),
    'New Member': (Color.FromArgb(55, 155, 135),  white),
    'Stealth':    (Color.FromArgb(75, 75, 75),    white),
    'You See':    (Color.FromArgb(165, 185, 195), dark),
    'Spell':      (Color.FromArgb(95, 75, 190),   white),
}

# Add strings to this list to block messages containing them from showing in this script
# Remove strings from this list to unblock them
# This does not block messages from showing in game
blockMessagesContaining = ['Your arrow hits its mark with velocity!'
                           ,'You claim the corpse and recieve a reward.'
                           ,'mana to perform that attack'
                           ,'You launch two shots at once!'
                           ,'You have not yet recovered from casting a spell.']

####################   APP SETTINGS - DO NOT TOUCH UNLESS YOU KNOW WHAT YOU ARE DOING   ####################

scriptName          = 'Journal Spy | {} ({})'.format(Player.Name, Misc.ShardName())
journalSpyDirectory = IOPath.Combine(Misc.CurrentScriptDirectory(), 'Journal_Spy')
exportFileName      = 'Journal Spy - {} - {} -'.format(Misc.ShardName(), Player.Name)
appSize             = Size(850 + 20, 324)
unixTimeBegin       = datetime(1970, 1, 1)
trimBatchSize       = 200 # Trim old rows in batches instead of one by one

# Tabs in display order: key, tab label, name used in export file names
TABS = [
    ('combined', '← All Checked', 'All Checked'),
    ('local',    'Local Speech',       'Local Speech'),
    ('world',    'World Chat',         'World Chat'),
    ('guild',    'Guild Chat',         'Guild Chat'),
    ('party',    'Party Chat',         'Party Chat'),
    ('other',    'Other',              'Other'),
]

# Grid columns: name, header, width (0 = fill the remaining width)
COLUMNS = [
    ('time',    'Time',    timeColumnWidth),
    ('type',    'Type',    typeColumnWidth),
    ('speaker', 'Speaker', speakerColumnWidth),
    ('message', 'Message', messageColumnWidth),
]
fillMinimumWidth    = 60 # A filling column never gets narrower than this
fixedMinimumWidth   = 20 # A set width below this is raised to it
TIME_COLUMN = 0
TYPE_COLUMN = 1
SPEAKER_COLUMN = 2

# Check boxes in display order: key, label, checked at start
# A checked box copies lines of that kind into the All Checked tab
FILTERS = [
    ('local',        'Local Speech',    False),
    ('world',        'World Chat',      False),
    ('guild',        'Guild Chat',      False),
    ('party',        'Party Chat',      False),
    ('admins',       '+Admins',         True),
    ('levelUps',     'Pet/Weap Level',  True),
    ('combat',       'Combat',          False),
    ('loggedInOut',  'Logged In / Out', False),
    ('coreMacro',    'Core / Macro',    False), # Not matched by any rule yet
    ('newestMember', 'Newest Member',   False),
    ('stealthSteps', 'Stealth Steps',   False),
    ('youSee',       'Character Names', False),
    ('worldSave',    'World Save',      False),
    ('deathRoll',    'Death Roll',      False),
    ('misc',         'Miscellaneous',   False),
]

####################   MESSAGE MATCHING   ####################

COMBAT_PHRASES = (
    'enveloped by a noxious gas', 'stepped onto a blade trap', 'stepped onto a spike trap',
    'feel pain throughout your body', 'damage has been healed', 'wracked with extreme pain',
    'around in confusion and pain', 'Your deeds in the city of', 'You deliver a mortal wound',
    'You play jarring music,', 'You heal what little damage', 'You attempt to disrupt',
    'Choose the target for ', 'You pierce your opponent', 'You launch two shots at ',
    'You have delivered a conc', 'The whirling attack strike', 'You are bleeding!',
    'That being is not damaged', 'You have been cured of all', 'You finish applying the ',
    'You begin applying the ', 'You did not earn the right', 'Warmode dismount blocked.',
    'Choose a corpse to claim', 'Choose another corpse to', 'As a reward for slaying ',
    'You have delivered a crushing', 'Your concentration is ', 'bleeding profusely',
    're already casting a spell.', 'vered from casting a spell.', 'corpse and receive a reward.',
    'and are in severe pain!', 'you are no longer bleeding!', 'You must have at least',
    'spasm uncontrollably', 'can breathe normally', 'resisting magical energy',
    'target is not affected', 'Oath has been broken', 'dry and corpselike', 'looks ill',
    'hits its mark with velocity', 'Your target is bleeding', 'looks extrememly ill', '%]',
    't claim a corpse you did not kill', 'You are too far away to claim that corpse',
    'You feel a bit nauseous', 'You are in extreme pain,', 'You feel disoriented and nauseous',
    'poison seems to have no effect', 'looks extremely ill.', 'seems resistant to the poison',
)

ADMIN_PHRASES = ('] +', '> +', '] Announcement by +', 'Staff message from +')

WORLD_SAVE_PHRASES = (
    'The world will save in ', 'The world is saving, please wait.', 'No Current News',
    'World save complete. ', 'Power Save! All players online ', 'Power Save! All online players ',
)

LEVEL_UP_PHRASES = (
    'Your strength has changed', 'Your dexterity has changed', 'Your intelligence has changed',
    'Your skill in', 'has gained a level',
)

DEATH_PHRASES = (
    'Pray, bretheren', 'Alas, poor', 'Another soul has', 'Rest in peace,', 'We mourn the passing',
    ' is heard throughout the land.', 'shall arise again for vengance!', ' the regions beyond the grave.',
    'has fallen victim to', 'shall rise again for vengance', 'has been slain in a br',
    'inflicted the final wo', 'has lost their life in battle to',
    'has succumbed to their wounds and has perished', 'may god have mercy on your soul',
    'Death comes for us all, but on this day, for',
)

STEALTH_PHRASES = ('Stealth steps', 'You begin to move quietely', 'You begin to move quietly')

REGULAR_MISC_PHRASES = (
    ' : ', 'lock quickly yields', 'appears to be locked.', 'make anything of the map',
    'decode a treasure map', 'marked by the red pin', 'hidden yourself well', 'seem to hide right now',
)

# Chat lines that carry their own channel and speaker, in the formats shards commonly use:
#   <Public> Name: text      [Guild] Name: text      [Guild][Name]: text      <Guild> [Name]: text
CHANNEL_LINE = re.compile(
    r'^\s*[<\[]\s*([^<>\[\]]{1,24}?)\s*[>\]]\s*'     # channel in <...> or [...]
    r'(?:\[\s*([^\[\]]{1,40}?)\s*\]|([^:<>\[\]]{1,40}?))'  # speaker, with or without brackets
    r'\s*:\s?(.*)$', re.S)                           # colon, then the message

def parseChannelLine(t):
    # Returns (channel, speaker, message), or None when the line is not a chat line
    m = CHANNEL_LINE.match(t)
    if m is None:
        return None
    speaker = (m.group(2) or m.group(3) or '').strip()
    if speaker.startswith('Announcement by '):
        speaker = speaker[len('Announcement by '):]
    return m.group(1).strip(), speaker, m.group(4)

def containsAny(text, phrases):
    return any(p in text for p in phrases)

def isCombat(t):
    if 'corpse' in t and (' a ' in t or ' an ' in t or "'s " in t):
        return True
    if 'You received' in t and 'tokens.' in t:
        return True
    return containsAny(t, COMBAT_PHRASES)

def isInvasion(t):
    return (('is being invaded by' in t and '. Please come help!' in t)
            or ('is safe!' in t and 'has been defeated!' in t)
            or ('has been protected but' in t and 'for the final battle!' in t))

def isDeathRoll(t):
    return ('couldn' in t and 't withstand' in t) or containsAny(t, DEATH_PHRASES)

def groupChannel(channel):
    # Guild, alliance and party channels: returns (tab key, filter key, type label), or None
    name = channel.lower()
    if name == 'party':
        return 'party', 'party', 'Party'
    if name == 'alliance':
        return 'guild', 'guild', 'Alliance'
    if name == 'guild':
        return 'guild', 'guild', 'Guild'
    return None

def classifySystem(t, parsed):
    # Returns (tab key, filter key, type label)
    channel = parsed[0] if parsed else ''
    if '<' in t and '> ' in t:
        if '> +' in t:
            return 'world', 'admins', 'Staff'
        if '<Public> ' in t:
            return 'world', 'world', 'Public'
        if '<Trade> ' in t:
            return 'world', 'world', 'Trade'
        if '<ESC> to cancel' in t:
            return 'other', 'misc', 'System'
        return groupChannel(channel) or ('guild', 'guild', 'Guild')
    if groupChannel(channel):
        return groupChannel(channel)
    if 'You see:' in t:
        return 'other', 'youSee', 'You See'
    if isCombat(t):
        return 'other', 'combat', 'Combat'
    if containsAny(t, ADMIN_PHRASES):
        return 'world', 'admins', 'Staff'
    if isInvasion(t):
        return 'world', 'misc', 'Invasion'
    if ' has logged ' in t:
        return 'other', 'loggedInOut', 'Login'
    if containsAny(t, WORLD_SAVE_PHRASES):
        return 'other', 'worldSave', 'Save'
    if containsAny(t, LEVEL_UP_PHRASES):
        return 'other', 'levelUps', 'Level Up'
    if isDeathRoll(t):
        return 'other', 'deathRoll', 'Death'
    if 'elcome the newest member ' in t:
        return 'other', 'newestMember', 'New Member'
    if containsAny(t, STEALTH_PHRASES):
        return 'other', 'stealthSteps', 'Stealth'
    return 'other', 'misc', 'System'

def classify(entry):
    # Returns (tab key, filter key, type label, speaker, message), or None to ignore the entry
    kind = entry.Type
    name = entry.Name or ''
    if name == 'System':
        name = ''
    t = entry.Text or ''

    if kind == 'System':
        parsed = parseChannelLine(t)
        tabKey, filterKey, label = classifySystem(t, parsed)
        if parsed:
            return tabKey, filterKey, label, parsed[1], parsed[2]
        return tabKey, filterKey, label, '', t

    if kind in ('Guild', 'Party', 'Alliance'):
        speaker, message = name, t
        if not name:
            parsed = parseChannelLine(t)
            if parsed:
                speaker, message = parsed[1], parsed[2]
        if kind == 'Guild':
            return 'guild', 'guild', 'Guild', speaker, message
        if kind == 'Party':
            return 'party', 'party', 'Party', speaker, message
        return 'other', 'misc', 'Alliance', speaker, message

    if kind == 'Regular':
        if isCombat(t):
            return 'other', 'combat', 'Combat', name, t
        if containsAny(t, REGULAR_MISC_PHRASES):
            return 'other', 'misc', 'Misc', name, t
        return 'local', 'local', 'Say', name, t
    if kind == 'Emote':
        if 'poison seems to have no effect' in t or 'seems resistant to the poison' in t:
            return 'other', 'combat', 'Combat', name, t
        if 'begins taming a creature' in t:
            return 'other', 'misc', 'Emote', name, t
        return 'local', 'local', 'Emote', name, t
    if kind == 'Label':
        return 'other', 'youSee', 'You See', '', t
    if kind == 'Whisper':
        return 'local', 'local', 'Whisper', name, t
    if kind == 'Yell':
        return 'local', 'local', 'Yell', name, t
    if kind == 'Spell':
        return 'other', 'misc', 'Spell', name, t
    if kind in ('Focus', 'Encoded', 'Special'):
        return 'other', 'misc', kind, name, t
    return None

####################   HELPERS   ####################

def journalTimeNow():
    # Same clock RE uses for journal timestamps: local time as seconds since 1970
    return (datetime.now() - unixTimeBegin).total_seconds()

def formatTime(timestamp):
    return (unixTimeBegin + timedelta(seconds=float(timestamp))).strftime('%m/%d  %X')

def safeFileName(name):
    for ch in IOPath.GetInvalidFileNameChars():
        name = name.replace(str(ch), '_')
    return name

def csvField(value):
    text = '' if value is None else str(value)
    # A cell starting with these is run as a formula by Excel, so chat text could trigger one.
    # A leading apostrophe makes Excel treat it as plain text.
    if text[:1] in ('=', '+', '-', '@', '\t', '\r'):
        text = "'" + text
    return '"' + text.replace('"', '""') + '"'

def copyToClipboard(text):
    # The clipboard only works from a single thread apartment (STA) thread, so use a short lived one
    result = {}
    def run():
        try:
            Clipboard.SetText(text)
        except Exception as e:
            result['error'] = e
    worker = Thread(ThreadStart(run))
    worker.SetApartmentState(ApartmentState.STA)
    worker.IsBackground = True
    worker.Start()
    if not worker.Join(2000):
        raise Exception('clipboard did not respond')
    if 'error' in result:
        raise result['error']

def enableDoubleBuffering(control):
    # Less flicker while rows are added. DoubleBuffered is not public on DataGridView.
    try:
        prop = clr.GetClrType(DataGridView).GetProperty('DoubleBuffered', BindingFlags.Instance | BindingFlags.NonPublic)
        prop.SetValue(control, True, None)
    except Exception:
        pass

####################   MAIN FORM   ####################

class JournalSpyForm(Form):

    def __init__(self):
        self.stopping = False
        self.lastTimestamp = None
        self.seenAtLastTimestamp = set()
        self.lastLineByTab = {}
        self.lastError = ''

        self.Text = scriptName
        self.BackColor = backgroundColor
        self.ForeColor = textColor
        self.FormBorderStyle = FormBorderStyle.Sizable # Set before the size so the border is counted correctly
        self.ClientSize = appSize
        self.MinimumSize = self.Size # Can grow, but never smaller than the starting size
        self.StartPosition = FormStartPosition.Manual
        self.Location = Point(positionH, positionV)
        self.TopMost = True
        self.FormClosing += self.onClosing
        self.Shown += self.onShown

        ####################   CHECK BOXES   ####################

        self.checks = {}
        for i, (key, label, checked) in enumerate(FILTERS):
            box = CheckBox()
            box.Text = label
            box.Checked = checked
            box.Location = Point(5, 5 + 20 * i)
            box.Size = Size(115, 20)
            self.Controls.Add(box)
            self.checks[key] = box

        ####################   BOTTOM ROW   ####################

        self.exportButton = Button()
        self.exportButton.BackColor = buttonColor
        self.exportButton.Location = Point(120, 295)
        self.exportButton.Size = Size(150, 25)
        self.exportButton.FlatStyle = FlatStyle.Flat
        self.exportButton.FlatAppearance.BorderSize = 1
        self.exportButton.Click += self.onExport
        self.exportButton.Anchor = AnchorStyles.Bottom | AnchorStyles.Left
        self.Controls.Add(self.exportButton)

        self.autoScroll = CheckBox()
        self.autoScroll.Text = 'Auto-scroll'
        self.autoScroll.Checked = True
        self.autoScroll.Location = Point(793, 298)
        self.autoScroll.Size = Size(77, 20)
        self.autoScroll.Anchor = AnchorStyles.Bottom | AnchorStyles.Right
        self.autoScroll.CheckedChanged += self.onAutoScrollChanged
        self.Controls.Add(self.autoScroll)

        self.systemNotification = Label()
        self.systemNotification.Text = ''
        self.systemNotification.ForeColor = textColor
        self.systemNotification.Location = Point(270, 301)
        self.systemNotification.Size = Size(520, 20)
        self.systemNotification.Anchor = AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right
        self.Controls.Add(self.systemNotification)

        ####################   GRID STYLES AND MENU   ####################

        self.typeStyles = {}
        for label, (back, fore) in typeColors.items():
            style = DataGridViewCellStyle()
            style.BackColor = back
            style.ForeColor = fore
            style.SelectionBackColor = back # Keeps the type color visible on selected rows
            style.SelectionForeColor = fore
            self.typeStyles[label] = style

        self.gridMenu = ContextMenuStrip()
        copyItem = ToolStripMenuItem('Copy selected rows')
        copyItem.Click += self.onCopyMenu
        self.gridMenu.Items.Add(copyItem)

        ####################   TABS   ####################

        self.tabControl = TabControl()
        self.tabControl.Location = Point(120, 0)
        self.tabControl.Size = Size(750, 291)
        self.tabControl.Alignment = TabAlignment.Top
        self.tabControl.SelectedIndexChanged += self.onTabSelected
        self.tabControl.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right
        self.Controls.Add(self.tabControl)

        self.tabKeys = []
        self.tabLabels = {}
        self.exportNames = {}
        self.tabPages = {}
        self.grids = {}
        self.unread = {}
        for key, label, exportName in TABS:
            page = TabPage()
            page.Text = label
            page.BackColor = backgroundColor
            self.tabControl.TabPages.Add(page)

            grid = self.makeGrid()
            page.Controls.Add(grid)

            self.tabKeys.append(key)
            self.tabLabels[key] = label
            self.exportNames[key] = exportName
            self.tabPages[key] = page
            self.grids[key] = grid
            self.unread[key] = 0

        self.updateExportButton()

    def makeGrid(self):
        grid = DataGridView()
        grid.Dock = DockStyle.Fill
        grid.ReadOnly = True
        grid.AllowUserToAddRows = False
        grid.AllowUserToDeleteRows = False
        grid.AllowUserToResizeRows = False
        grid.RowHeadersVisible = False
        grid.SelectionMode = DataGridViewSelectionMode.FullRowSelect
        grid.MultiSelect = True
        grid.ClipboardCopyMode = DataGridViewClipboardCopyMode.Disable # Copy is handled in onGridKeyDown
        grid.BackgroundColor = textboxColor
        grid.GridColor = gridLineColor
        grid.CellBorderStyle = DataGridViewCellBorderStyle.SingleHorizontal
        grid.DefaultCellStyle.BackColor = textboxColor
        grid.DefaultCellStyle.ForeColor = textColor
        grid.RowTemplate.Height = 20
        grid.ContextMenuStrip = self.gridMenu

        for name, header, width in COLUMNS:
            column = DataGridViewTextBoxColumn()
            column.Name = name
            column.HeaderText = header
            column.SortMode = DataGridViewColumnSortMode.Automatic
            if width > 0:
                column.Width = max(int(width), fixedMinimumWidth)
            else:
                # All filling columns have the same fill weight, so they split the space equally
                column.AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill
                column.MinimumWidth = fillMinimumWidth
            grid.Columns.Add(column)
        grid.Columns[TYPE_COLUMN].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter
        grid.Columns[SPEAKER_COLUMN].DefaultCellStyle.Alignment = DataGridViewContentAlignment.MiddleCenter

        grid.CellFormatting += self.onCellFormatting
        grid.CellMouseDown += self.onGridMouseDown
        grid.KeyDown += self.onGridKeyDown
        grid.Sorted += self.onGridSorted
        enableDoubleBuffering(grid)
        return grid

    ####################   WINDOW EVENTS (window thread)   ####################

    def selectedTabKey(self):
        index = self.tabControl.SelectedIndex
        if index < 0:
            index = 0
        return self.tabKeys[index]

    def updateExportButton(self):
        self.exportButton.Text = 'Export {}'.format(self.exportNames[self.selectedTabKey()])

    def onTabSelected(self, sender, args):
        key = self.selectedTabKey()
        self.unread[key] = 0
        self.tabPages[key].Text = self.tabLabels[key]
        self.updateExportButton()
        if self.autoScroll.Checked:
            self.scrollToNewest(self.grids[key])

    def onAutoScrollChanged(self, sender, args):
        if self.autoScroll.Checked:
            self.scrollToNewest(self.grids[self.selectedTabKey()])

    def onGridSorted(self, sender, args):
        if self.autoScroll.Checked:
            self.scrollToNewest(sender)

    def showStatus(self, text, isError):
        self.systemNotification.ForeColor = Color.FromArgb(225, 0, 0) if isError else textColor
        self.systemNotification.Text = text

    def onCellFormatting(self, sender, e):
        # The time column stores the raw journal timestamp so it sorts correctly, and is shown formatted
        if e.ColumnIndex == TIME_COLUMN and e.Value is not None:
            try:
                e.Value = formatTime(e.Value)
                e.FormattingApplied = True
            except Exception:
                pass

    def onGridMouseDown(self, sender, e):
        # Right click selects the row under the mouse, unless it is already part of the selection
        if e.Button == MouseButtons.Right and e.RowIndex >= 0:
            row = sender.Rows[e.RowIndex]
            if not row.Selected:
                sender.ClearSelection()
                row.Selected = True

    def onGridKeyDown(self, sender, e):
        if e.Control and e.KeyCode == Keys.C:
            e.Handled = True
            e.SuppressKeyPress = True
            self.copySelected(sender)

    def onCopyMenu(self, sender, args):
        grid = self.gridMenu.SourceControl
        if grid is not None:
            self.copySelected(grid)

    def rowValues(self, row):
        values = []
        for i in range(len(COLUMNS)):
            value = row.Cells[i].Value
            if i == TIME_COLUMN and value is not None:
                value = formatTime(value)
            values.append('' if value is None else str(value))
        return values

    def copySelected(self, grid):
        try:
            rows = sorted(grid.SelectedRows, key=lambda r: r.Index)
            if not rows:
                return
            text = '\r\n'.join('\t'.join(self.rowValues(row)) for row in rows)
            copyToClipboard(text)
            self.showStatus('Copied {} rows.'.format(len(rows)), False)
        except Exception as e:
            self.showStatus('Copy failed: {}'.format(e), True)

    def onExport(self, sender, args):
        key = self.selectedTabKey()
        try:
            Directory.CreateDirectory(journalSpyDirectory) # Does nothing if the folder already exists
            stamp = datetime.now().strftime('%m%d%Y %H%M%S')
            fileName = safeFileName('{} {} - {}.csv'.format(exportFileName, self.exportNames[key], stamp))
            fullPath = IOPath.Combine(journalSpyDirectory, fileName)
            lines = [','.join(csvField(header) for name, header, width in COLUMNS)]
            for row in self.grids[key].Rows: # In the order shown, so a sorted tab exports sorted
                lines.append(','.join(csvField(v) for v in self.rowValues(row)))
            File.WriteAllLines(fullPath, Array[str](lines), UTF8Encoding(True)) # With BOM so Excel reads UTF-8
            self.showStatus('Saved {} rows to: {}'.format(len(lines) - 1, journalSpyDirectory), False)
        except Exception as e:
            self.showStatus('Export failed: {}'.format(e), True)

    def onShown(self, sender, args):
        worker = Thread(ThreadStart(self.workerLoop))
        worker.IsBackground = True # Never keeps running after the script or client ends
        worker.Start()

    def onClosing(self, sender, args):
        self.stopping = True

    def markDisconnected(self):
        self.Text = '{} [DISCONNECTED]'.format(scriptName)
        self.showStatus('Disconnected: journal reading stopped. You can still export.', True)

    ####################   GRID UPDATES (window thread)   ####################

    def sortState(self, grid):
        # Returns (sorted by time, newest first, sorted by another column)
        column = grid.SortedColumn
        if column is None:
            return True, False, False
        if column.Index == TIME_COLUMN:
            return True, grid.SortOrder == SortOrder.Descending, False
        return False, False, True

    def scrollToNewest(self, grid):
        count = grid.Rows.Count
        byTime, newestFirst, otherSort = self.sortState(grid)
        if count == 0 or otherSort:
            return # Sorted by type, speaker or message: there is no newest end to follow
        try:
            grid.FirstDisplayedScrollingRowIndex = 0 if newestFirst else count - 1
        except Exception:
            pass # The grid can refuse while its tab has never been shown

    def addRows(self, grid, rows):
        byTime, newestFirst, otherSort = self.sortState(grid)
        wasEmpty = grid.Rows.Count == 0

        for timestamp, label, speaker, message in rows:
            # New rows are always the newest, so they go at the newest end of a time sort.
            # The grid does not place new rows into a sort by itself.
            if newestFirst:
                grid.Rows.Insert(0, timestamp, label, speaker, message)
                index = 0
            else:
                index = grid.Rows.Add(timestamp, label, speaker, message)
            style = self.typeStyles.get(label)
            if style is not None:
                grid.Rows[index].Cells[TYPE_COLUMN].Style = style

        if otherSort:
            # Put the new rows in their sorted place and keep the view where the user left it
            first = grid.FirstDisplayedScrollingRowIndex
            direction = ListSortDirection.Descending if grid.SortOrder == SortOrder.Descending else ListSortDirection.Ascending
            grid.Sort(grid.SortedColumn, direction)
            if 0 <= first < grid.Rows.Count:
                try:
                    grid.FirstDisplayedScrollingRowIndex = first
                except Exception:
                    pass

        self.trimOldest(grid)
        if wasEmpty:
            grid.ClearSelection() # No highlighted first row on start
        if self.autoScroll.Checked:
            self.scrollToNewest(grid)

    def trimOldest(self, grid):
        extra = grid.Rows.Count - maxLinesPerTab
        if extra < trimBatchSize:
            return
        times = [(grid.Rows[i].Cells[TIME_COLUMN].Value, i) for i in range(grid.Rows.Count)]
        times.sort()
        oldest = sorted((i for value, i in times[:extra]), reverse=True)
        for i in oldest: # Highest index first so the remaining indexes stay valid
            grid.Rows.RemoveAt(i)

    def isDuplicate(self, tabKey, line, timestamp):
        if duplicateWindowSecs <= 0:
            return False
        last = self.lastLineByTab.get(tabKey)
        if last is not None and last[0] == line and timestamp - last[1] < duplicateWindowSecs:
            return True
        self.lastLineByTab[tabKey] = (line, timestamp)
        return False

    def addLines(self, lines):
        if self.IsDisposed:
            return

        pending = {}
        for timestamp, tabKey, filterKey, label, speaker, message in lines:
            row = (timestamp, label, speaker, message)
            if self.isDuplicate(tabKey, (label, speaker, message), timestamp):
                continue
            pending.setdefault(tabKey, []).append(row)
            check = self.checks.get(filterKey)
            if check is not None and check.Checked:
                pending.setdefault('combined', []).append(row)

        selected = self.selectedTabKey()
        for tabKey, rows in pending.items():
            self.addRows(self.grids[tabKey], rows)
            if tabKey != selected:
                self.unread[tabKey] += len(rows)
                self.tabPages[tabKey].Text = '{} ({})'.format(self.tabLabels[tabKey], self.unread[tabKey])

    ####################   THREAD HELPERS   ####################

    def postToUI(self, fn):
        # Runs fn on the window thread without waiting for it
        def safe():
            try:
                fn()
            except Exception as e:
                self.reportError('window update', e)
        try:
            if not self.IsDisposed and self.IsHandleCreated:
                self.BeginInvoke(Action(safe))
        except Exception:
            pass

    def reportError(self, where, e):
        # Same message is shown at most once every 10 seconds
        try:
            msg = 'Journal Spy ({}) error: {}'.format(where, e)
            if msg != self.lastError or not Timer.Check('journalSpyError'):
                Misc.SendMessage(msg, 33)
                self.lastError = msg
                Timer.Create('journalSpyError', 10000)
        except Exception:
            pass

    ####################   JOURNAL WORKER (background thread)   ####################
    # One thread reads the journal and sorts lines. It never touches the window directly:
    # it hands each batch to the window thread through postToUI.
    # Every error is caught so nothing can escape the thread and close the client.

    def readNewLines(self):
        # RE returns entries with a timestamp strictly after the one given. Entries made in the
        # same clock tick share a timestamp, so ask from slightly earlier and skip the ones already seen.
        if self.lastTimestamp is not None and journalTimeNow() < self.lastTimestamp - 5:
            # Local clock moved back (daylight saving or a time sync). Start again from now.
            self.lastTimestamp = journalTimeNow()
            self.seenAtLastTimestamp = set()

        if self.lastTimestamp is None:
            entries = Journal.GetJournalEntry(-1.0)
        else:
            entries = Journal.GetJournalEntry(float(self.lastTimestamp) - 0.001)

        lines = []
        for entry in entries:
            timestamp = entry.Timestamp
            key = (entry.Type, entry.Name, entry.Serial, entry.Text)
            if self.lastTimestamp is not None:
                if timestamp < self.lastTimestamp:
                    continue
                if timestamp == self.lastTimestamp and key in self.seenAtLastTimestamp:
                    continue
            if self.lastTimestamp is None or timestamp > self.lastTimestamp:
                self.lastTimestamp = timestamp
                self.seenAtLastTimestamp = set()
            self.seenAtLastTimestamp.add(key)

            if containsAny(entry.Text or '', blockMessagesContaining):
                continue
            result = classify(entry)
            if result is None:
                continue
            tabKey, filterKey, label, speaker, message = result
            lines.append((timestamp, tabKey, filterKey, label, speaker, message))
        return lines

    def workerLoop(self):
        while Player.Connected and not self.stopping:
            try:
                lines = self.readNewLines()
                if lines:
                    self.postToUI(lambda batch=lines: self.addLines(batch))
            except Exception as e:
                self.reportError('journal', e)
            Misc.Pause(pollIntervalMs)

        if not self.stopping:
            self.postToUI(self.markDisconnected)

####################   RUN APP   ####################

Application.EnableVisualStyles()
journalSpyForm = JournalSpyForm()
try:
    Application.Run(journalSpyForm)
finally:
    journalSpyForm.stopping = True # Also stops the worker when the script is stopped from RE