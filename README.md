# Puzzle Hustle
Puzzle Hustle is a simple jigsaw puzzle game using basic pygame functionality.

## *Install*
The build_win64 directory contains a ready-to-use executable file for win64. Just download everything and open puzzle.exe.<br>
There are no pre-builds for non-win64 systems yet, so in that case you have to use the python source code files instead.

## *How to play*
In the start menu, choose one of the predefined images or select a folder with your own jigsaw pieces (see below) and click the play button. In the game, use the following controls:
- Drag and drop on a puzzle piece: Move that piece and all already connected ones
- Drag and drop on the background: Move the background
- Right-click on a puzzle piece: Rotate the piece and all already connected ones counter-clockwise
- Ctrl + mouse wheel: Zoom in or out
- Ctrl + 0: Reset zoom to standard
- Esc: Quit the game

If a piece is close enough to a fitting neighbor piece, the two will automatically be combined, and you'll hear a sound notification. If there's no sound, the pieces do not fit.<br>
**IMPORTANT**: If you move a group of multiple pieces at once (because they are already connected), the game only checks for fitting neighbors of the piece that is clicked on. So make sure that you grabbed the correct piece to connect the group to other pieces/ groups.

## *Using your own image*
You can play Puzzle Hustle with an own image as well: For creating the jigsaw pieces, use the GIMP script *GIMP_export_jigsaw* from https://github.com/BeXXsoR/gimp_export_jigsaw. See the README file there on how to use the script. Then in Puzzle Hustle, simply choose the folder that you saved the pieces into via the respective option in its start menu.

## *Troubleshooting*
- Error message "The following filename/s don't match the expected pattern.": Puzzle Hustle only supports specific row to column ratios for the jigsaw, namely 6x8, 9x12, 12x16 and 15x20, and it expects all files to be named *foldername\_i\_j*, where *foldername* matches the name of the selected folder, and *i* and *j* describe the position of the piece in the pattern (i.e. row number and column number). Make sure that the files mentioned in the error message follow this pattern as well.
- Error message "Invalid number of files in directory: Supported numbers are 48, 108, 192 or 300.": As Puzzle Hustle only supports specific row to column ratios as mentioned above, the number of files in the selected folder must correspond to the number of pieces in the respective ratio, which is 48, 108, 192 or 300. Make sure that the number of files in your folder matches one of these.

## *Credits*
- Game design and implementation: **Thomas Schneider**
- Background image: **Katja Maiwald**
- Puzzle images: Thomas Schneider
- Button artwork:
  - pyUh, https://opengameart.org/content/free-game-gui
  - https://www.flaticon.com/free-icons/file-explorer
- Fireworks animation: Graniginn, https://gifer.com/en/4M57
- Sounds:
  - original_sound, https://freesound.org/people/original_sound/sounds/366104/
  - waveplaySFX, https://freesound.org/people/waveplaySFX/sounds/399934/
  - FoolBoyMedia, https://freesound.org/people/FoolBoyMedia/sounds/397435/
  <br>
- Special thanks to: Dradra, Kokosnuss, Haselnuss, Tiger, Mausi, Muh. You're the best!
