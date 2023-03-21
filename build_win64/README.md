# Puzzle Hustle
Puzzle Hustle is a simple puzzle game using basic pygame functionality.

## *Install*
The build directory contains a ready-to-use executable file for win64, and the res directory contains all additional needed files. Just download these two directories and open puzzlehustle.exe.
There are no pre-builds for non-win64 systems yet, so in that case you have to use the python source code files instead.

## *How to play*
In the start menu, select your favourite image and the difficulty and click the play button. In the game, use the following controls:
- Drag and drop on a puzzle piece: move that piece and all already connected ones
- Drag and drop on the background: move the background
- Right-click on a puzzle piece: Rotate the piece and all already connected ones counter-clockwise
- Ctrl + mouse wheel: zoom in or out
- Ctrl + 0: Reset zoom to standard
- Esc: Quit the game

If a piece is close enough to a fitting neighbor piece, the two will automatically be combined, and you'll hear a sound notification. If there's no sound, the pieces do not fit. 
**IMPORTANT**: If you move a group of multiple pieces at once (because they are already connected), the game only checks for fitting neighbors of the piece that is clicked on. So make sure that you select the correct piece to connect the group to other pieces/ groups.

## *Credits*
- Game design and implementation: **Thomas Schneider**
- Background image: **Katja Maiwald**
- Puzzle images: Thomas Schneider
- Button artwork: pyUh, https://opengameart.org/content/free-game-gui
- Fireworks animation: Graniginn, https://gifer.com/en/4M57 by Graniginn
- Sounds:
  - original_sound, https://freesound.org/people/original_sound/sounds/366104/
  - waveplaySFX, https://freesound.org/people/waveplaySFX/sounds/399934/
  - FoolBoyMedia, https://freesound.org/people/FoolBoyMedia/sounds/397435/
- Special thanks to: Dradra, Kokosnuss, Haselnuss, Tiger, Mausi, Muh. You're the best!
