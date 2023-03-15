"""A little puzzle game using basic pygame functionalities."""

# ------ Imports ------
import sys
import itertools
import random
import utils
import pygame
import animations

pygame.init()

# ------ Constants ------
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 153, 0)
TRANSPARENT = (0, 0, 0, 0)
BG_COLOR = GREEN
FPS = 30
IMAGE_NAME = "Tier_Puzzle"
FILE_PREFIX = "res/" + IMAGE_NAME + "/" + IMAGE_NAME
FILE_SUFFIX = ".png"
NUM_ROWS = 9
NUM_COLUMNS = 12
NUM_PIECES = NUM_ROWS * NUM_COLUMNS
IMAGE_WIDTH = 4032
IMAGE_HEIGHT = 3024
PIECE_WIDTH_ORIG = 500
PIECE_HEIGHT_ORIG = 500
CLIPPER_SIZE = 82
NO_CLIPPER_PIECE_SIZE = 335
NUM_ROTATIONS = 4
ROTATION_DEGREE = 90
PICTURE_TO_DISPLAY_RATIO = 0.9
CLIPPING_DISTANCE = 10
ZOOM_STEP = 0.1
VICTORY_SOUND_DURATION = 20000
PLAY_ANIMATION = pygame.event.custom_type()
STOP_ANIMATION = pygame.event.custom_type()

# ------ Global variables ------
main_surface = pygame.display.set_mode((0, 0))
clock = pygame.time.Clock()
piece_states = []
# piece_states keeps track of the state of all pieces. It's items are tuples with the following elements:
# [0] = Scaled Image (as Surface), [1] = Position, [2] = Rotation, [3] = Set of connected pieces, [4] = Original image
piece_idx_stack = []
# piece_idx_stack keeps track of the order of the pieces on the main_surface. Pieces at the beginning of piece_idx_stack
# are blitted first, pieces at the end are blitted last. The list doesn't hold the pieces itself, but rather the index
# of the piece in piece_states
if main_surface.get_width() / main_surface.get_height() > IMAGE_WIDTH / IMAGE_HEIGHT:
    puzzle_height = PICTURE_TO_DISPLAY_RATIO * main_surface.get_height()
    puzzle_width = puzzle_height * IMAGE_WIDTH / IMAGE_HEIGHT
else:
    puzzle_width = PICTURE_TO_DISPLAY_RATIO * main_surface.get_width()
    puzzle_height = puzzle_width * IMAGE_HEIGHT / IMAGE_WIDTH
scale_factor = puzzle_height / IMAGE_HEIGHT
scaled_clipper_size = scale_factor * CLIPPER_SIZE
piece_width_core = puzzle_width // NUM_COLUMNS
piece_height_core = puzzle_height // NUM_ROWS
piece_width = int(piece_width_core + 2 * scaled_clipper_size)
piece_height = int(piece_height_core + 2 * scaled_clipper_size)
cur_zoom = 1.0
pygame.mixer.init()
img_menu_bar = pygame.image.load("res/Menu_Bar.png")
sound_connected = pygame.mixer.Sound("res/Connected.wav")
sound_victory = pygame.mixer.Sound("res/Victory.wav")
fireworks_anim = animations.Animation("res/fireworks.gif", (1000, 1000))
anim_play_event = pygame.event.Event(PLAY_ANIMATION, {})
anim_stop_event = pygame.event.Event(STOP_ANIMATION, {})
# ------ Classes ------


# ------ Methods ------
def main():
    """Main entry point for the game"""
    initialize_puzzle_pieces()
    sel_piece_idx = None
    zoom_key_pressed = False
    is_running = True
    while is_running:
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                # Quit
                is_running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL:
                # Activate zoom
                zoom_key_pressed = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_0 and zoom_key_pressed:
                # Zoom back to standard
                zoom(1.0)
            elif event.type == pygame.KEYUP and event.key == pygame.K_LCTRL:
                # Deactivate zoom
                zoom_key_pressed = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Left click - get the clicked piece
                sel_piece_idx = get_idx_of_selected_piece(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                # Right click - rotate the clicked piece
                piece_idx = get_idx_of_selected_piece(event.pos)
                if piece_idx is not None:
                    rotate_piece(piece_idx)
                    update_display()
            elif event.type == pygame.MOUSEBUTTONUP:
                # release the clicked piece
                sel_piece_idx = None
                pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))
            elif event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
                # Drag and drop
                pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZEALL))
                if sel_piece_idx is not None:
                    # Drag and drop on a piece - update position of selected piece and put it at the end of the stack
                    move_piece(sel_piece_idx, event.rel)
                    piece_idx_stack.remove(sel_piece_idx)
                    piece_idx_stack.append(sel_piece_idx)
                    # i.p., connect with nearby neighbors - if successful, release the focus on the selected piece
                    if check_neighbors(sel_piece_idx):
                        sound_connected.play()
                        sel_piece_idx = None
                        check_win()
                else:
                    # Drag and drop on the background - move background (i.e. move all pieces)
                    move_all_pieces(event.rel)
                update_display()
            elif event.type == pygame.MOUSEWHEEL and zoom_key_pressed:
                # Zoom in or out
                zoom(cur_zoom + event.y * ZOOM_STEP)
            elif event.type == PLAY_ANIMATION:
                # Show fireworks
                update_display()
                frame = fireworks_anim.get_next_frame()
                position = ((main_surface.get_width() - frame.get_width()) // 2,
                            (main_surface.get_height() - frame.get_height()) // 2)
                main_surface.blit(frame, position)
                pygame.display.update()
            elif event.type == STOP_ANIMATION:
                pygame.time.set_timer(anim_play_event, 0)
                update_display()
        clock.tick(FPS)
    pygame.quit()


def move_piece(piece_idx: int, movement: tuple) -> None:
    """Move the given piece and all connected ones by the given movement"""
    for cur_idx in piece_states[piece_idx][3]:
        piece_states[cur_idx][1] = utils.add_tuples(piece_states[cur_idx][1], movement)


def move_all_pieces(movement: tuple) -> None:
    """Move all pieces by the given movement"""
    remaining_pieces = {i for i in range(NUM_PIECES)}
    while remaining_pieces:
        cur_idx = remaining_pieces.pop()
        move_piece(cur_idx, movement)
        remaining_pieces -= set(piece_states[cur_idx][3])


def rotate_piece(sel_piece_idx: int) -> None:
    """Rotate the selected piece and all connected ones counter-clockwise."""
    sel_pos = piece_states[sel_piece_idx][1]
    for cur_piece_idx in piece_states[sel_piece_idx][3]:
        cur_pos = piece_states[cur_piece_idx][1]
        dist_pre = utils.subtract_tuples(cur_pos, sel_pos)
        new_pos = [sel_pos[0] + dist_pre[1], sel_pos[1] - dist_pre[0]]
        piece_states[cur_piece_idx][1] = new_pos
        piece_states[cur_piece_idx][2] = (piece_states[cur_piece_idx][2] + 1) % NUM_ROTATIONS
        piece_states[cur_piece_idx][0] = pygame.transform.rotate(piece_states[cur_piece_idx][0], 90)


def initialize_puzzle_pieces() -> None:
    """Initialize the puzzle pieces randomly on the main surface and fill piece_states and piece_idx_stack"""
    for i, j in itertools.product(range(NUM_ROWS), range(NUM_COLUMNS)):
        cur_idx = i * NUM_COLUMNS + j
        cur_state = [None, (0, 0), 0, {cur_idx}, None]
        # load image and assign random start position and rotation
        cur_state[1] = (random.randrange(main_surface.get_width() - piece_width),
                        random.randrange(main_surface.get_height() - piece_height))
        cur_state[2] = random.randrange(NUM_ROTATIONS)
        orig_image = pygame.image.load(FILE_PREFIX + str(i) + str(j) + FILE_SUFFIX).convert_alpha()
        cur_state[4] = orig_image
        scaled_image = pygame.transform.scale(orig_image, (piece_width, piece_height))
        scaled_image = pygame.transform.rotate(scaled_image, cur_state[2] * ROTATION_DEGREE)
        cur_state[0] = scaled_image
        piece_states.append(cur_state)
        piece_idx_stack.append(cur_idx)
    update_display()


def update_display() -> None:
    """Blit all puzzle pieces to the main surface"""
    main_surface.fill(BG_COLOR)
    for idx in piece_idx_stack:
        main_surface.blit(piece_states[idx][0], piece_states[idx][1])
    pygame.display.update()


def get_idx_of_selected_piece(mouse_pos: tuple):
    """Return the index of the foremost puzzle piece at the mouse position, or None if there is no piece at that
    position"""
    scs = scaled_clipper_size
    sel_indices = [idx for idx in piece_idx_stack
                   if scs <= mouse_pos[0] - piece_states[idx][1][0] < piece_states[idx][0].get_width() - scs
                   and scs <= mouse_pos[1] - piece_states[idx][1][1] < piece_states[idx][0].get_height() - scs]
    if sel_indices:
        return sel_indices[-1]
    else:
        return None


def check_neighbors(sel_piece_idx: int) -> bool:
    """Check for nearby neighbor pieces of the given piece. If found, connect them."""
    # determine target positions for neighbors. Neighbor order: top, left, bottom, right
    neighbor_idxs = (sel_piece_idx - NUM_COLUMNS if sel_piece_idx >= NUM_COLUMNS else None,
                     sel_piece_idx - 1 if sel_piece_idx % NUM_COLUMNS != 0 else None,
                     sel_piece_idx + NUM_COLUMNS if sel_piece_idx + NUM_COLUMNS < NUM_PIECES else None,
                     sel_piece_idx + 1 if (sel_piece_idx + 1) % NUM_COLUMNS != 0 else None)
    cur_rotation = piece_states[sel_piece_idx][2]
    # rotate neighbor indices to match the current orientation
    for i in range(cur_rotation):
        neighbor_idxs = neighbor_idxs[3:4] + neighbor_idxs[0:3]
    sel_piece_width_core, sel_piece_height_core = (piece_width_core, piece_height_core) \
        if cur_rotation == 0 or cur_rotation == 2 else (piece_height_core, piece_width_core)
    neighbor_found = False
    for direction_idx, cur_neighbor_idx in enumerate(neighbor_idxs):
        # First check for situations that can be ignored: (a) Neighbor_idx is out of range or (b) rotations don't match
        # or (c) pieces are already connected.
        if cur_neighbor_idx is None or piece_states[cur_neighbor_idx][2] != cur_rotation or \
           cur_neighbor_idx in piece_states[sel_piece_idx][3]:
            continue
        cur_neighbor_pos = piece_states[cur_neighbor_idx][1]
        # Now determine target position for neighbors (in order top, left, bottom, right)
        if direction_idx == 0:
            cur_trg_pos = (cur_neighbor_pos[0], cur_neighbor_pos[1] + sel_piece_height_core)
        elif direction_idx == 1:
            cur_trg_pos = (cur_neighbor_pos[0] + sel_piece_width_core, cur_neighbor_pos[1])
        elif direction_idx == 2:
            cur_trg_pos = (cur_neighbor_pos[0], cur_neighbor_pos[1] - sel_piece_height_core)
        else:
            cur_trg_pos = (cur_neighbor_pos[0] - sel_piece_width_core, cur_neighbor_pos[1])
        dist = max([abs(a - b) for a, b in zip(piece_states[sel_piece_idx][1], cur_trg_pos)])
        if dist <= CLIPPING_DISTANCE:
            # Fitting piece: Move selected piece right into the target position and combine the already connected
            # neighbors of both pieces to one block
            move_piece(sel_piece_idx, utils.subtract_tuples(cur_trg_pos, piece_states[sel_piece_idx][1]))
            new_block = piece_states[sel_piece_idx][3].union(piece_states[cur_neighbor_idx][3])
            for idx in new_block:
                piece_states[idx][3] = new_block
            neighbor_found = True
    return neighbor_found


def check_win() -> bool:
    """Check if the puzzle is completely solved, i.e. all pieces are connected"""
    if len(piece_states[0][3]) == NUM_PIECES:
        pygame.time.set_timer(anim_play_event, fireworks_anim.duration, 0)
        pygame.time.set_timer(anim_stop_event, VICTORY_SOUND_DURATION, 1)
        sound_victory.play()
        return True
    else:
        return False


def zoom(new_zoom: float) -> None:
    """Zoom in or out and adjust the piece positions accordingly
    new_zoom is the new zoom factor"""
    global piece_width, piece_height, piece_width_core, piece_height_core, scale_factor, scaled_clipper_size, cur_zoom
    # Compute zoom: Compute new size of the piece's core, round it to integer, adjust the zoom to reflect that rounding
    # and continue with this zoom factor. This is necessary to keep the core size as ints while still avoiding rounding
    # errors after multiple zooms.
    new_zoom_rel = new_zoom / cur_zoom
    new_piece_size_core = utils.mult_tuple_to_int((piece_width_core, piece_height_core), new_zoom_rel)
    if any([a <= 0 for a in new_piece_size_core]):
        # No further zoom possible -> ignore this zoom request
        return
    new_zoom_rel = new_piece_size_core[0] / piece_width_core
    piece_width_core, piece_height_core = new_piece_size_core
    piece_width, piece_height, scale_factor, scaled_clipper_size, cur_zoom = utils.multiply_tuple(
        (piece_width, piece_height, scale_factor, scaled_clipper_size, cur_zoom), new_zoom_rel)
    # Perform zoom. Formula for new position: new = center + zoom_factor * (old - center)
    center = main_surface.get_rect().center
    for idx in piece_idx_stack:
        piece_states[idx][1] = (center[0] + new_zoom_rel * (piece_states[idx][1][0] - center[0]),
                                center[1] + new_zoom_rel * (piece_states[idx][1][1] - center[1]))
        piece_states[idx][0] = pygame.transform.scale(piece_states[idx][4], (piece_width, piece_height))
        if piece_states[idx][2] > 0:
            piece_states[idx][0] = pygame.transform.rotate(piece_states[idx][0], piece_states[idx][2] * ROTATION_DEGREE)
    update_display()


# ------ Main script ------
if __name__ == "__main__":
    sys.exit(main())


