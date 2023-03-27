"""A little puzzle game using basic pygame functionalities."""

# ------ Imports ------
import sys
import itertools
import random
import utils
import animations
import start_menu
import pygame

pygame.init()

# ------ Constants ------
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 153, 0)
BG_COLOR = GREEN
FPS = 30
BG_FILE_NAME = "../res/background.png"
IMAGE_NAMES = [["Tier_48", "Tier_108", "Tier_192"],
               ["SPO_48", "SPO_108", "SPO_192"],
               ["Dradra_48", "Dradra_108", "Dradra_192"],
               ["Wuerfeln_48", "Wuerfeln_108", "Wuerfeln_192"]]
FILE_NAME = "../res/{image_name}/{image_name}_{row}_{column}.png"
SOUND_CONNECTED_FILE_NAME = "../res/Connected.wav"
SOUND_VICTORY_FILE_NAME = "../res/Victory.wav"
FIREWORKS_FILE_NAME = "../res/fireworks.gif"
NUM_ROWS = [6, 9, 12]
NUM_COLUMNS = [8, 12, 16]
IMAGE_WIDTH = 4032
IMAGE_HEIGHT = 3024
CLIPPER_SIZE = [125, 82, 62]
NUM_ROTATIONS = 4
ROTATION_DEGREE = 90
PICTURE_TO_DISPLAY_RATIO = 0.9
CLIPPING_DISTANCE = 5
ZOOM_STEP = 0.1
VICTORY_SOUND_DURATION = 20000
PLAY_ANIMATION = pygame.event.custom_type()
STOP_ANIMATION = pygame.event.custom_type()


# ------ Classes ------
class PuzzleHustle:
    def __init__(self):
        self.main_surface = pygame.display.set_mode((0, 0))
        self.bg_image = pygame.transform.scale(pygame.image.load(BG_FILE_NAME).convert_alpha(),
                                               self.main_surface.get_size())
        self.clock = pygame.time.Clock()
        self.piece_states = []
        # piece_states keeps track of the state of all pieces. It's items are tuples with the following elements: [0]
        # = Scaled Image (as Surface), [1] = Position, [2] = Rotation, [3] = Set of connected pieces, [4] = Original
        # image
        self.piece_idx_stack = []
        # piece_idx_stack keeps track of the order of the pieces on the main_surface. Pieces at the beginning of
        # piece_idx_stack are blitted first, pieces at the end are blitted last. The list doesn't hold the pieces
        # itself, but rather the index of the piece in piece_states
        if self.main_surface.get_width() / self.main_surface.get_height() > IMAGE_WIDTH / IMAGE_HEIGHT:
            self.puzzle_height = PICTURE_TO_DISPLAY_RATIO * self.main_surface.get_height()
            self.puzzle_width = self.puzzle_height * IMAGE_WIDTH / IMAGE_HEIGHT
        else:
            self.puzzle_width = PICTURE_TO_DISPLAY_RATIO * self.main_surface.get_width()
            self.puzzle_height = self.puzzle_width * IMAGE_HEIGHT / IMAGE_WIDTH
        self.scale_factor = self.puzzle_height / IMAGE_HEIGHT
        self.cur_zoom = 1.0
        pygame.mixer.init()
        self.sound_connected = pygame.mixer.Sound(SOUND_CONNECTED_FILE_NAME)
        self.sound_victory = pygame.mixer.Sound(SOUND_VICTORY_FILE_NAME)
        self.fireworks_anim = animations.Animation(FIREWORKS_FILE_NAME, (1000, 1000))
        self.anim_play_event = pygame.event.Event(PLAY_ANIMATION, {})
        self.anim_stop_event = pygame.event.Event(STOP_ANIMATION, {})
        self.start_menu = start_menu.StartMenu(self.main_surface, self.bg_image)
        self.image_id = None
        self.difficulty = None
        self.image_name = None
        self.num_rows = None
        self.num_columns = None
        self.clipper_size = None
        self.num_pieces = None
        self.scaled_clipper_size = None
        self.piece_width_core = None
        self.piece_height_core = None
        self.piece_width = None
        self.piece_height = None

    def set_image_and_difficulty(self, image_id: int = None, difficulty: int = None):
        if image_id is not None:
            self.image_id = image_id
        if difficulty is not None:
            self.difficulty = difficulty
        self.image_name = IMAGE_NAMES[self.image_id][self.difficulty]
        self.num_rows = NUM_ROWS[self.difficulty]
        self.num_columns = NUM_COLUMNS[self.difficulty]
        self.clipper_size = CLIPPER_SIZE[self.difficulty]
        self.num_pieces = self.num_rows * self.num_columns
        self.scaled_clipper_size = self.scale_factor * self.clipper_size
        self.piece_width_core = self.puzzle_width // self.num_columns
        self.piece_height_core = self.puzzle_height // self.num_rows
        self.piece_width = int(self.piece_width_core + 2 * self.scaled_clipper_size)
        self.piece_height = int(self.piece_height_core + 2 * self.scaled_clipper_size)

    def main_game_loop(self):
        """Main entry point for the game"""
        # Handle start menu
        start_puzzle, image_id, difficulty = self.start_menu.handle_events()
        if not start_puzzle:
            return
        self.set_image_and_difficulty(image_id, difficulty)
        self.initialize_puzzle_pieces()
        sel_piece_idx = None
        zoom_key_pressed = False
        move_bg = False
        is_running = True
        while is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    # Quit
                    is_running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL:
                    # Activate zoom
                    zoom_key_pressed = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_0 and zoom_key_pressed:
                    # Zoom back to standard
                    self.zoom(1.0)
                elif event.type == pygame.KEYUP and event.key == pygame.K_LCTRL:
                    # Deactivate zoom
                    zoom_key_pressed = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Left click - get the clicked piece
                    sel_piece_idx = self.get_idx_of_selected_piece(event.pos)
                    if sel_piece_idx is None:
                        move_bg = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    # Right click - rotate the clicked piece
                    piece_idx = self.get_idx_of_selected_piece(event.pos)
                    if piece_idx is not None:
                        self.rotate_piece(piece_idx)
                        self.update_display()
                elif event.type == pygame.MOUSEBUTTONUP:
                    # release the clicked piece
                    sel_piece_idx = None
                    move_bg = False
                    pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))
                elif event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
                    # Drag and drop
                    pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZEALL))
                    if sel_piece_idx is not None:
                        # Drag and drop on a piece - update pos of selected piece and put it at the end of the stack
                        self.move_piece(sel_piece_idx, event.rel)
                        self.piece_idx_stack.remove(sel_piece_idx)
                        self.piece_idx_stack.append(sel_piece_idx)
                        # i.p., connect with nearby neighbors - if successful, release the focus on the selected piece
                        if self.check_neighbors(sel_piece_idx):
                            self.sound_connected.play()
                            sel_piece_idx = None
                            self.check_win()
                    elif move_bg:
                        # Drag and drop on the background - move background (i.e. move all pieces)
                        self.move_all_pieces(event.rel)
                    self.update_display()
                elif event.type == pygame.MOUSEWHEEL and zoom_key_pressed:
                    # Zoom in or out
                    self.zoom(self.cur_zoom + event.y * ZOOM_STEP)
                elif event.type == PLAY_ANIMATION:
                    # Show fireworks
                    self.update_display()
                    frame = self.fireworks_anim.get_next_frame()
                    position = ((self.main_surface.get_width() - frame.get_width()) // 2,
                                (self.main_surface.get_height() - frame.get_height()) // 2)
                    self.main_surface.blit(frame, position)
                    pygame.display.update()
                elif event.type == STOP_ANIMATION:
                    pygame.time.set_timer(self.anim_play_event, 0)
                    self.update_display()
            self.clock.tick(FPS)
        pygame.quit()

    def move_piece(self, piece_idx: int, movement: tuple) -> None:
        """Move the given piece and all connected ones by the given movement"""
        for cur_idx in self.piece_states[piece_idx][3]:
            self.piece_states[cur_idx][1] = utils.add_tuples(self.piece_states[cur_idx][1], movement)

    def move_all_pieces(self, movement: tuple) -> None:
        """Move all pieces by the given movement"""
        remaining_pieces = {i for i in range(self.num_pieces)}
        while remaining_pieces:
            cur_idx = remaining_pieces.pop()
            self.move_piece(cur_idx, movement)
            remaining_pieces -= set(self.piece_states[cur_idx][3])

    def rotate_piece(self, sel_piece_idx: int) -> None:
        """Rotate the selected piece and all connected ones counter-clockwise."""
        sel_pos = self.piece_states[sel_piece_idx][1]
        for cur_piece_idx in self.piece_states[sel_piece_idx][3]:
            cur_pos = self.piece_states[cur_piece_idx][1]
            dist_pre = utils.subtract_tuples(cur_pos, sel_pos)
            new_pos = [sel_pos[0] + dist_pre[1], sel_pos[1] - dist_pre[0]]
            self.piece_states[cur_piece_idx][1] = new_pos
            self.piece_states[cur_piece_idx][2] = (self.piece_states[cur_piece_idx][2] + 1) % NUM_ROTATIONS
            self.piece_states[cur_piece_idx][0] = pygame.transform.rotate(self.piece_states[cur_piece_idx][0],
                                                                          ROTATION_DEGREE)

    def initialize_puzzle_pieces(self) -> None:
        """Initialize the puzzle pieces randomly on the main surface and fill piece_states and piece_idx_stack"""
        for i, j in itertools.product(range(self.num_rows), range(self.num_columns)):
            cur_idx = i * self.num_columns + j
            cur_state = [None, (0, 0), 0, {cur_idx}, None]
            # load image and assign random start position and rotation
            cur_state[1] = (random.randrange(self.main_surface.get_width() - self.piece_width),
                            random.randrange(self.main_surface.get_height() - self.piece_height))
            cur_state[2] = random.randrange(NUM_ROTATIONS)
            orig_image = pygame.image.load(FILE_NAME.format(image_name=self.image_name, row=i, column=j)).convert_alpha()
            cur_state[4] = orig_image
            scaled_image = pygame.transform.scale(orig_image, (self.piece_width, self.piece_height))
            scaled_image = pygame.transform.rotate(scaled_image, cur_state[2] * ROTATION_DEGREE)
            cur_state[0] = scaled_image
            self.piece_states.append(cur_state)
            self.piece_idx_stack.append(cur_idx)
        self.update_display()

    def update_display(self) -> None:
        """Blit all puzzle pieces to the main surface"""
        self.main_surface.fill(BG_COLOR)
        # self.main_surface.blit(self.bg_image, (0, 0))
        for idx in self.piece_idx_stack:
            self.main_surface.blit(self.piece_states[idx][0], self.piece_states[idx][1])
        pygame.display.update()

    def get_idx_of_selected_piece(self, mouse_pos: tuple):
        """Return the index of the foremost puzzle piece at the mouse position, or None if there is no piece at that
        position"""
        scs = self.scaled_clipper_size
        sel_indices = [idx for idx in self.piece_idx_stack
                       if scs <= mouse_pos[0] - self.piece_states[idx][1][0] < self.piece_states[idx][0].get_width() - scs
                       and scs <= mouse_pos[1] - self.piece_states[idx][1][1] < self.piece_states[idx][0].get_height() - scs]
        if sel_indices:
            return sel_indices[-1]
        else:
            return None

    def check_neighbors(self, sel_piece_idx: int) -> bool:
        """Check for nearby neighbor pieces of the given piece. If found, connect them."""
        # determine target positions for neighbors. Neighbor order: top, left, bottom, right
        neighbor_idxs = (sel_piece_idx - self.num_columns if sel_piece_idx >= self.num_columns else None,
                         sel_piece_idx - 1 if sel_piece_idx % self.num_columns != 0 else None,
                         sel_piece_idx + self.num_columns if sel_piece_idx + self.num_columns < self.num_pieces else None,
                         sel_piece_idx + 1 if (sel_piece_idx + 1) % self.num_columns != 0 else None)
        cur_rotation = self.piece_states[sel_piece_idx][2]
        # rotate neighbor indices to match the current orientation
        for i in range(cur_rotation):
            neighbor_idxs = neighbor_idxs[3:4] + neighbor_idxs[0:3]
        sel_piece_width_core, sel_piece_height_core = (self.piece_width_core, self.piece_height_core) \
            if cur_rotation == 0 or cur_rotation == 2 else (self.piece_height_core, self.piece_width_core)
        neighbor_found = False
        for direction_idx, cur_neighbor_idx in enumerate(neighbor_idxs):
            # First check for situations that can be ignored: (a) Neighbor_idx is out of range or (b) rotations don't
            # match or (c) pieces are already connected.
            if cur_neighbor_idx is None or self.piece_states[cur_neighbor_idx][2] != cur_rotation or \
               cur_neighbor_idx in self.piece_states[sel_piece_idx][3]:
                continue
            cur_neighbor_pos = self.piece_states[cur_neighbor_idx][1]
            # Now determine target position for neighbors (in order top, left, bottom, right)
            if direction_idx == 0:
                cur_trg_pos = (cur_neighbor_pos[0], cur_neighbor_pos[1] + sel_piece_height_core)
            elif direction_idx == 1:
                cur_trg_pos = (cur_neighbor_pos[0] + sel_piece_width_core, cur_neighbor_pos[1])
            elif direction_idx == 2:
                cur_trg_pos = (cur_neighbor_pos[0], cur_neighbor_pos[1] - sel_piece_height_core)
            else:
                cur_trg_pos = (cur_neighbor_pos[0] - sel_piece_width_core, cur_neighbor_pos[1])
            dist = max([abs(a - b) for a, b in zip(self.piece_states[sel_piece_idx][1], cur_trg_pos)])
            if dist <= CLIPPING_DISTANCE:
                # Fitting piece: Move selected piece right into the target position and combine the already connected
                # neighbors of both pieces to one block
                self.move_piece(sel_piece_idx, utils.subtract_tuples(cur_trg_pos, self.piece_states[sel_piece_idx][1]))
                new_block = self.piece_states[sel_piece_idx][3].union(self.piece_states[cur_neighbor_idx][3])
                for idx in new_block:
                    self.piece_states[idx][3] = new_block
                neighbor_found = True
        return neighbor_found

    def check_win(self) -> bool:
        """Check if the puzzle is completely solved, i.e. all pieces are connected"""
        if len(self.piece_states[0][3]) == self.num_pieces:
            pygame.time.set_timer(self.anim_play_event, self.fireworks_anim.duration, 0)
            pygame.time.set_timer(self.anim_stop_event, VICTORY_SOUND_DURATION, 1)
            self.sound_victory.play()
            return True
        else:
            return False

    def zoom(self, new_zoom: float) -> None:
        """Zoom in or out and adjust the piece positions accordingly
        new_zoom is the new zoom factor"""
        # Compute zoom: Compute new size of the piece's core, round it to integer, adjust the zoom to reflect that rounding
        # and continue with this zoom factor. This is necessary to keep the core size as ints while still avoiding rounding
        # errors after multiple zooms.
        new_zoom_rel = new_zoom / self.cur_zoom
        new_piece_size_core = utils.mult_tuple_to_int((self.piece_width_core, self.piece_height_core), new_zoom_rel)
        if any([a <= 0 for a in new_piece_size_core]):
            # No further zoom possible -> ignore this zoom request
            return
        new_zoom_rel = new_piece_size_core[0] / self.piece_width_core
        self.piece_width_core, self.piece_height_core = new_piece_size_core
        self.piece_width, self.piece_height, self.scale_factor, self.scaled_clipper_size, self.cur_zoom = utils.multiply_tuple(
            (self.piece_width, self.piece_height, self.scale_factor, self.scaled_clipper_size, self.cur_zoom), new_zoom_rel)
        # Perform zoom. Formula for new position: new = center + zoom_factor * (old - center)
        center = self.main_surface.get_rect().center
        for idx in self.piece_idx_stack:
            self.piece_states[idx][1] = (center[0] + new_zoom_rel * (self.piece_states[idx][1][0] - center[0]),
                                    center[1] + new_zoom_rel * (self.piece_states[idx][1][1] - center[1]))
            self.piece_states[idx][0] = pygame.transform.scale(self.piece_states[idx][4], (self.piece_width, self.piece_height))
            if self.piece_states[idx][2] > 0:
                self.piece_states[idx][0] = pygame.transform.rotate(self.piece_states[idx][0], self.piece_states[idx][2] * ROTATION_DEGREE)
        self.update_display()


# ------ Main script ------
if __name__ == "__main__":
    game = PuzzleHustle()
    sys.exit(game.main_game_loop())
