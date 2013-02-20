                                    SpaceWar
                                    v0.7.2.2
                        February "1 Game A Month" entry
                              © 2013 by MageKing17
                              MageKing17@gmail.com

################################################################################

            CHANGELOG:

Key:
  + New feature
  ? Changed feature
  - Removed feature
  ! Bugfix

v0.1 - Initial Release

v0.2 - Post-Release High version (Unreleased)
  + Added after-battle statistics (who did how much damage?)
  + Added team-play option (ships of the same race fight together)
  ? Made the AI name selector not pick names already taken (no more fighting two
    identically-named captains, unless you somehow have more ships than there
    are names for that race... which shouldn't happen, by default)
  ! You can now see other cloaked ships if they're on your team or you're dead.
  ! You can no longer click on cloaked hostiles to see their info box.

v0.5 - Campaign Mode version
  + Able to create, play with, save, and load persistent characters that gain
    experience points, rank up, earn bonus points, and spend those points on
    ship upgrades. Or you can continue playing the current gameplay with
    "instant action", even though it's basically the same as playing with a
    character that never levels up against enemies that are also always Cadets.
  ? Death no longer causes the game to automatically start new turns every time
    one ends; now you can observe the AI's info boxes and start the next turn on
    your own terms. Or let it fast-forward to the end like it always used to.
    Just click on a blank hex to trigger the new menu.

v0.5.1 - "First Ever Reported Bug" Fix Version
  ! Executable now includes codecs that, for some reason, aren't included by
    default. Typing no longer causes a crash.
  ! While I'm at it, enabled key repeat so erasing a name is less of a chore.

v0.5.2 - "Whoops, That Was Silly" Fix Version
  ! "Fast-forward" state now cleared after the end of a game, which means the
    game will no longer run turns with no ships when you look at a text box
    after a game you fast-forwarded to the end of. Yeah, that was silly.

v0.5.3 - "Yup, That Too" Fix Version
  ! Rank bonus was being calculated incorrectly. Basic algebra fail, sadly.

v0.6 - Sentry Gun Version
  + Added Sentry Guns to both Instant Action and Battle Setup. They sit in
    either the top right or bottom left corner (or both, if you have two) and
    endlessly fire torpedoes at random. They don't count towards victory
    conditions, so you don't have to destroy them to win, but they can provide
    an extra challenge or some extra points.
  ? Gave everyone the same hitbox as the Borg; later, there will be a config
    file to choose whether to use "pixel perfect" collision detection for
    weaponsfire, but for now, I think game balance works a bit better if it gets
    handled the way the original did it; with squares.
  ? Made the key repeat delay and frequency shorter. Just a slight difference.
  ? Changed the statistics viewer to have the "reset" button on the same page as
    the statistics. Also added a confirmation check before you reset.
  ? While I was at it, rearranged the kill count statistics so that S:BitI ships
    are in the left column while the classic ships (including the Sentry Gun)
    are in the right column. Just looks a bit nicer.
  ? Along the same lines, the player setup menu was tightened up, so smaller
    screens won't have player XP or bonus points being shoved off the side of
    the window.
  ? After-battle statistics now list dead ships in the reverse of the order that
    they used to, putting most-recently destroyed ships near the top (so the
    "second-place" ship is no longer at the bottom of the list).
  ! Trying to click on a cloaked ship after death no longer results in a crash.
  ! Ending your turn in the same hex as another ship while another ship explodes
    no longer causes extra collision damage during the explosion.

v0.7 - Data File Version
  + Rewrote a wide variety of code to externalize previously hard-coded features
    and information. Almost all strings displayed to the user should now be
    loaded from a localization file. Settings are now stored in spacewar.ini
    (for general items, like where to store save files or which localization
    file to load) or settings.cfg (for computer-specific settings like whether
    or not to run fullscreen).
  + To demonstrate the new theme format, added a Babylon 5 theme. It relies only
    on the sentry gun file from the classic theme, and has its own localization
    file to leave the default uncluttered. It also shows off new combinations of
    the special abilities that can have interesting consequences. No super-duper
    combo theme to let you play with all three groups, though... I'll leave that
    as an exercise for the reader. ;)
  ? Save files from the old version are no longer compatible, because they now
    use YAML syntax instead of the old "writing the repr() of the value" method.
    On the plus side, they also now don't care which theme they were saved
    for... although, to be safe, you should probably set your character's race
    to "random" before editing your character's theme so that you don't wind up
    trying to load a ship that's not in your current theme... that will almost
    certainly cause an error.
  ! Remember how I said I'd reversed the display order of dead ships? Yeah, I
    accidentally didn't do that. I definitely did that this time, though.

v0.7.1 - "D'oh!" Fix Version
  ! Fixed three bugs related to draws. You can now have everyone blow each other
    up simultaneously without crashing... probably.
  ! Altered the command menu so that it now guarantees that it'll be wide enough
    to display the longest possible action string. Or tries to guarantee it,
    anyway... we'll see how it actually pans out. Also moved click priorities
    from changing actions to changing targets, so if it does start running over
    again for some obscure reason, you'll still be able to click the drawn-on-
    top-anyway button.
  + Added a font size setting to the settings.cfg file, if you want to make
    things more readable on large screens or shrink windows down on small ones.
    Personally I don't recommend setting the scaling multiplier below 4, but as
    somebody who plays this game on a device that has to use a multiplier of 3
    (the Pandora), I really don't have a leg to stand on... might as well make
    it so you can actually have a chance to read some of those long messages.

v0.7.2 - Minor Optimization Fix Version
  ! Fixed an inefficiency with loading text from localization files that was
    causing slowdown on my Pandora, and probably would've caused minor problems
    on other systems as well.

v0.7.2.1 - Icon-ified Version
  + Added an icon, showing various S:BitI ships shooting at each other. Looks a
    lot more interesting than the default Windows icon, at least.

v0.7.2.2 - GitHub Version
  - Removed all but the S:BitI theme, and removed references to the removed
    content.
  ? While I was at it, slightly fixed up a couple alignment issues in the
    localization file.

################################################################################

            CONTROLS:

Unlike last month's game, this one has relatively few controls:

Q/ESCAPE	- Quit
F12		- Take screenshot

Everything else is controlled with the mouse, so get clicking!

################################################################################

            RANDOM TECHNICAL DETAILS:

Most game-related graphics (and collisions and whatnot) are processed internally
at 160x160 and then scaled up to the window. Most of the UI, however, is drawn
and processed directly on the full-sized window, so that text doesn't look so
pixelated (except the top bar, because that's drawn with the regular graphics
for... obscure reasons). The window size is determined by looking at your
current desktop resolution and figuring out how many multiples of 160 can fit
into it (with a small leeway for the frame). If your desktop happens to have a
resolution of 800x480, the game will run fullscreen at 480x480, because that
makes it more convenient for playing on the Pandora.

The game uses your system to find its fonts; if you don't have a system font
that Pygame can identify as either Courier New or Liberation Mono, the game will
either use the default font... or crash, depending. If this turns out to be a
huge problem, I can find a font to bundle with the game.

################################################################################

            GENERAL INFO:

This is a clone of the old PalmOS freeware game called (surprise!) "SpaceWar".
SpaceWar was a turn-based tactics game played on a hex grid; you chose one of
five different Star Trek-inspired ships (Federation, Klingon, Tholian, Dominion,
or Borg), chose where to move and where to shoot, and then watch as your ship
and up to three computer-controlled ships moved and fired simultaneously. If you
outmanuvered your opponent, you'd watch them explode. If you didn't, well, then
YOU get to explode, don't you?

As of v0.6, the only features missing from the original are... victory pictures,
I guess? Well, there's also no in-game instructions, and no multiplayer. The AI
could really use some work, too. Still, you can make a character and rank it up
just like in the original, so if you never played multiplayer, there's
effectively no difference!

You can choose from one of five different ships with different special
abilities. The included "S:BitI" theme ("S:BitI" stands for "Space: Battles in
the Infinite", a card game a friend of mine and I made that never went
anywhere), has the following five ships:

Terran		- Ablative Armor (take half damage when not attacking)
Psiloth		- Psionic Cloak (turn invisible when not attacking, but take
                      twice as much damage)
Zlorg		- Rapid Acceleration (accelerate or decelerate twice as quickly
                      when not attacking)
Wental		- Regeneration (regenerate 5 shields if you don't attack)
Riftbound	- Subspace Jumpdrive (If you try to move to a hex you normally
                      couldn't while not attacking, you instantly teleport
                      there, but your speed gets set to 0) + Regeneration (if
                      your movement hex would otherwise be valid, you regenerate
                      5 shields just like the Wental)

For added fun, each ship has a different phaser color (and some even have
multiple colors):

Terran		- Light blue (Ion Cannons ahoy!)
Psiloth		- Red (they may be psychic, but they're not very imaginative)
Zlorg		- Rainbow (cycles through Red, Yellow, Green, Blue, and Purple)
Wental		- Purple (the dreaded Icelaser!)
Riftbound	- Black fading to Yellow (because... well, it looks cool)

You can choose a theme when you start an instant action round or create a new
character, but your only choice will be "Space: Battles in the Infinite" unless
you add a new theme.

Characters have a specific theme they always play with, but you can always just
edit your character file to change their theme (it's the third line in the .chr
file). If you play Instant Action (basically just pre-v0.5 gameplay), you choose
your theme before every battle.

################################################################################

            CAMPAIGN:

Okay, it's not really a campaign, but this is just the "persistent character"
menu. You can choose to setup a battle, enter the player setup menu, view
statistics, save your character, or quit to the main menu.

      BATTLE SETUP:

Here you can add or remove AI ships or sentry guns, and choose their rank and
race. Once you have the setup you want, you can begin the battle. Every time you
enter this menu, it has the same setup it had the last time you left it, so you
can set it to your favourite settings and leave them there.

      PLAYER SETUP:

Here you can change the name of your character and your ship, as well as spend
bonus points upgrading your ship. Your bonus points are determined by your rank,
which is determined by your experience points (earned after every battle):

0	- Cadet
1500	- Ensign
5000	- Lieutenant JG
12000	- Lieutenant
25000	- Commander
50000	- Captain
100000	- Commodore
200000	- Rear Admiral
350000	- Vice Admiral
550000	- Admiral
800000	- Fleet Admiral

Each rank above Cadet gives you 5 bonus points, up to a maximum of 50 at Fleet
Admiral. Each bonus point spent gives you one of the following:

10 shield points, up to a max of 360
5 phaser points, up to a max of 100
5 torpedo points, up to a max of 120
1 engine point, up to a max of 10

Given the starting stats (100 shields, 20 phasers, 30 torpedoes, 5 engines), it
is easy to see that a ship can accept up to 65 bonus points. This means that no
ship can be at maximum strength everywhere, not even a Fleet Admiral's ship. It
is up to you to spend your points wisely, to complement your playstyle and keep
yourself alive in the face of the opposition.

      VIEW STATISTICS:

Here you can view various statistics about your character, such as weapon
accuracy, average points per game, average shields remaining, and ship kills.
You can also reset them, if for some reason you don't like your statistics (this
won't clear your experience points).

      SAVE CHARACTER:

Enter a filename; this saves your character's progress to that file so you can
load it again later. The game won't stop you from quitting without saving, but
if you try to return to the main menu, it'll ask if you're sure you want to
erase any unsaved character data.

################################################################################

            INSTANT ACTION:

After choosing your theme, the game will ask you to choose your race. After
that, you choose whether it will be a team game and the number of AI-controlled
ships, and then the race of each. Once all ships are on the board, you can go
ahead and start playing!

################################################################################

            BATTLE:

Click on another ship to bring up the info box, containing the rank (always
"Cadet" in instant action) of the captain, the captain's name, the name of the
ship, its current shield strength, and its last recorded speed. You can right-
click on your own ship to get the same info box, or left-click to bring up the
command menu. Here you can choose where to move by clicking the "Destination"
button, what action to take (by clicking on your current action; defaults to "Do
nothing"), and if that action is firing a weapon, where to fire it by clicking
the "Target" button. If you want to go back to looking at your enemies' current
locations and info boxes, you can hit "Cancel" to close the command menu. If you
click "Okay", the game will make sure your actions are valid (within your
movement capabilities, for example) and then the turn will execute.

Your ship and your enemies' ships will move simultaneously. Torpedoes launch
very shortly after the turn begins, but take time to reach the target; in
contrast, phasers take more time to charge up before firing, but travel
instantaneously. Phasers also spread their damage out over a short period of
time; with proper aiming, this can let you "rake" your phaser blasts over
multiple hexes, but keep in mind that you deal less damage with a partial hit
than a full barrage. When you deal enough damage to bring an enemy ship's
shields below 0, they explode (dealing damage to any ships unfortunate enough to
be caught nearby), and if you're the last one standing, you win! Unfortunately,
it is possible for no ships to survive the battle (colliding with an enemy ship
without enough shields to survive, or getting caught in an enemy's explosion
being the most common reasons), in which case nobody wins.

Now get out there and blow something up!

################################################################################

            CREDITS:

All code was written by me in the month of February, 2013. Hopefully I'll be
upgrading this game with more features before the month is out, but if not, I'll
be busy focusing on whatever my March game is. If you want to talk to me about
this game or anything else, my email address is at the top of this readme (but
here it is again: MageKing17@gmail.com)

Hex grid graphics and sentry gun sprite copied from the original SpaceWar,
mostly for the nostalgia factor. If Michael Read ever sees this and cares, I can
remove all the "classic" stuff from this clone. SpaceWar © 2001 by Michael Read.

Space: Battles in the Infinite is my intellectual property, and I'd appreciate
it if you talked to me before using anything from it. Not that I expect anyone
to, but still; just throwing it out there. S:BitI graphics, ship names, captain
names, and victory quotes were created by myself and S:BitI's co-creator.

Sound effects were generated by me with sfxr by DrPetter. I love that tool so
much.
