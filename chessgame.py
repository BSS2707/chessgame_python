import sys
import random
import time
import pygame
import chess

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
SQ_SIZE = 80
BOARD_PX = SQ_SIZE * 8
SIDEBAR_W = 300
WIDTH = BOARD_PX + SIDEBAR_W
HEIGHT = BOARD_PX
FPS = 30

LIGHT = (238, 220, 185)
DARK = (150, 111, 82)
HILITE_SELECT = (246, 234, 90)
HILITE_MOVE = (106, 168, 79)
HILITE_CAPTURE = (200, 90, 80)
HILITE_LAST = (170, 200, 230)
CHECK_COLOR = (220, 60, 60)
BG_SIDEBAR = (34, 34, 38)
TEXT_COLOR = (235, 235, 235)
BTN_COLOR = (60, 60, 68)
BTN_HOVER = (85, 85, 95)
BTN_TEXT = (240, 240, 240)
ACCENT = (90, 170, 255)

PIECE_UNICODE = {
    "P": "\u2659", "N": "\u2658", "B": "\u2657", "R": "\u2656", "Q": "\u2655", "K": "\u2654",
    "p": "\u265F", "n": "\u265E", "b": "\u265D", "r": "\u265C", "q": "\u265B", "k": "\u265A",
}

# Piece values (centipawns)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

# Piece-square tables (from White's perspective, index 0 = a1 ... 63 = h8)
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10,-20,-20, 10, 10,  5,
     5, -5,-10,  0,  0,-10, -5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
     0,  0,  0,  0,  0,  0,  0,  0,
]
KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]
ROOK_TABLE = [
     0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     5, 10, 10, 10, 10, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -10,  5,  5,  5,  5,  5,  0,-10,
      0,  0,  5,  5,  5,  5,  0, -5,
     -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]
KING_TABLE = [
     20, 30, 10,  0,  0, 10, 30, 20,
     20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
]
KING_TABLE_ENDGAME = [
    -50,-30,-30,-30,-30,-30,-30,-50,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -50,-40,-30,-20,-20,-30,-40,-50,
]
PST = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}


# --------------------------------------------------------------------------
# Evaluation & Bot (minimax with alpha-beta pruning + quiescence search)
# --------------------------------------------------------------------------
def is_endgame(board: chess.Board) -> bool:
    """Rough endgame detector: little material left on the board besides kings/pawns."""
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
    minors_majors = 0
    for pt in (chess.KNIGHT, chess.BISHOP, chess.ROOK):
        minors_majors += len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK))
    return queens == 0 or minors_majors <= 2


def evaluate_board(board: chess.Board) -> int:
    """Positive = good for White, negative = good for Black."""
    if board.is_checkmate():
        # side to move is checkmated
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material() or \
       board.is_seventyfive_moves() or board.is_fivefold_repetition():
        return 0

    endgame = is_endgame(board)
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        value = PIECE_VALUES[piece.piece_type]
        if piece.piece_type == chess.KING and endgame:
            table = KING_TABLE_ENDGAME
        else:
            table = PST[piece.piece_type]
        idx = square if piece.color == chess.WHITE else chess.square_mirror(square)
        pst_val = table[idx]
        total = value + pst_val
        score += total if piece.color == chess.WHITE else -total

    # bishop pair bonus
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += 30
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= 30

    # symmetric mobility bonus: compare move counts for both sides, not just
    # whoever is currently to move (the old version only scored the side on
    # move, which is a weak and slightly misleading signal)
    white_mobility = _pseudo_mobility(board, chess.WHITE)
    black_mobility = _pseudo_mobility(board, chess.BLACK)
    score += 3 * (white_mobility - black_mobility)

    return score


def _pseudo_mobility(board: chess.Board, color: bool) -> int:
    """Cheap mobility estimate for a given side without flipping board.turn
    repeatedly (which is relatively expensive to do for both colors every
    node). Uses attacks from each piece's square as a fast proxy."""
    count = 0
    for square in board.pieces(chess.PAWN, color) | board.pieces(chess.KNIGHT, color) | \
                  board.pieces(chess.BISHOP, color) | board.pieces(chess.ROOK, color) | \
                  board.pieces(chess.QUEEN, color) | board.pieces(chess.KING, color):
        count += len(board.attacks(square))
    return count


def order_moves(board: chess.Board, moves, tt_move=None):
    def score(move):
        s = 0
        if tt_move is not None and move == tt_move:
            s += 100000
        if board.is_capture(move):
            captured = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            cap_val = PIECE_VALUES[captured.piece_type] if captured else 100
            att_val = PIECE_VALUES[attacker.piece_type] if attacker else 0
            s += 10 * cap_val - att_val
        if move.promotion:
            s += 800
        if board.gives_check(move):
            s += 50
        return -s
    return sorted(moves, key=score)


def quiescence(board: chess.Board, alpha: float, beta: float, color: int, qdepth: int = 6):
    """Extend search along captures/checks past the nominal depth limit so the
    bot doesn't stop searching mid-exchange and misjudge a hanging piece
    (the classic 'horizon effect')."""
    stand_pat = color * evaluate_board(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat
    if qdepth == 0:
        return alpha

    noisy_moves = [m for m in board.legal_moves if board.is_capture(m) or m.promotion]
    noisy_moves = order_moves(board, noisy_moves)
    for move in noisy_moves:
        board.push(move)
        score = -quiescence(board, -beta, -alpha, -color, qdepth - 1)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha


def negamax(board: chess.Board, depth: int, alpha: float, beta: float, color: int, deadline=None):
    if board.is_game_over():
        return color * evaluate_board(board), None
    if depth == 0:
        return quiescence(board, alpha, beta, color), None

    best_move = None
    best_val = -float("inf")
    moves = order_moves(board, list(board.legal_moves))
    for move in moves:
        board.push(move)
        val, _ = negamax(board, depth - 1, -beta, -alpha, -color, deadline)
        val = -val
        board.pop()
        if val > best_val:
            best_val = val
            best_move = move
        alpha = max(alpha, val)
        if alpha >= beta:
            break
        if deadline is not None and time.time() > deadline:
            break
    if best_move is None and moves:
        best_move = moves[0]
    return best_val, best_move


# Difficulty setting (1-4) -> (max search depth, time budget in seconds).
# Iterative deepening means we always have a legal best move ready even if
# time runs out mid-search at a deeper ply.
DIFFICULTY_SETTINGS = {
    1: (3, 1.0),
    2: (4, 2.0),
    3: (5, 4.0),
    4: (6, 8.0),
}


def bot_choose_move(board: chess.Board, difficulty: int) -> chess.Move:
    max_depth, time_budget = DIFFICULTY_SETTINGS.get(difficulty, (4, 2.0))
    color = 1 if board.turn == chess.WHITE else -1
    deadline = time.time() + time_budget

    best_move = None
    for depth in range(1, max_depth + 1):
        val, move = negamax(board, depth, -float("inf"), float("inf"), color, deadline)
        if move is not None:
            best_move = move
        if time.time() > deadline:
            break

    if best_move is None:
        legal = list(board.legal_moves)
        best_move = random.choice(legal) if legal else None
    return best_move


# --------------------------------------------------------------------------
# UI helpers
# --------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback

    def draw(self, surf, font):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        color = BTN_HOVER if hovered else BTN_COLOR
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, (20, 20, 24), self.rect, width=2, border_radius=8)
        label = font.render(self.text, True, BTN_TEXT)
        surf.blit(label, label.get_rect(center=self.rect.center))

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()
            return True
        return False


def get_piece_font(size):
    candidates = "segoeuisymbol,applesymbols,dejavusans,dejavu sans,arialunicodems,freeserif,arial"
    return pygame.font.SysFont(candidates, size)


# --------------------------------------------------------------------------
# Main Game class
# --------------------------------------------------------------------------
class ChessGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Chess - Human vs Bot / Human vs Human")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.piece_font = get_piece_font(int(SQ_SIZE * 0.72))
        self.ui_font = pygame.font.SysFont("arial", 20)
        self.ui_font_small = pygame.font.SysFont("arial", 16)
        self.title_font = pygame.font.SysFont("arial", 26, bold=True)
        self.big_font = pygame.font.SysFont("arial", 40, bold=True)
        self.setup_title_font = pygame.font.SysFont("arial", 44, bold=True)

        self.board = chess.Board()
        self.selected_square = None
        self.legal_targets = []          # list of chess.Move from selected square
        self.last_move = None
        self.move_log = []               # list of SAN strings
        self.flipped = False
        self.vs_bot = True
        self.human_color = chess.WHITE
        self.bot_depth = 2
        self.bot_thinking = False
        self.game_over_msg = None
        self.awaiting_promotion = None   # (from_sq, to_sq, color) if choosing promotion piece
        self.status_msg = ""

        # --- fullscreen state ---
        self.fullscreen = False
        self.native_size = (WIDTH, HEIGHT)

        # --- name/color setup screen state ---
        self.state = "setup"             # "setup" or "playing"
        self.player_name = ""            # White player's name (or the human, vs bot)
        self.player_black_name = ""      # used only in Human vs Human mode
        self.name_active = 1             # 1 = White/solo name box focused, 2 = Black name box focused
        self.pending_mode_vs_bot = True  # mode chosen on the setup screen

        self._build_buttons()
        self._build_setup_widgets()

    # ---------------------------------------------------------------- UI
    def _build_buttons(self):
        bx = BOARD_PX + 20
        bw = SIDEBAR_W - 40
        bh = 36
        gap = 6
        y = 370
        self.buttons = []
        self.buttons.append(Button(bx, y, bw, bh, "New Game", self.new_game)); y += bh + gap
        self.buttons.append(Button(bx, y, bw, bh, "Undo Move", self.undo_move)); y += bh + gap
        self.buttons.append(Button(bx, y, bw, bh, "Resign", self.resign)); y += bh + gap
        self.buttons.append(Button(bx, y, bw, bh, "Flip Board", self.flip_board)); y += bh + gap
        self.buttons.append(Button(bx, y, bw, bh, "Toggle Mode", self.toggle_mode)); y += bh + gap
        self.buttons.append(Button(bx, y, (bw - 6) // 2, bh, "Difficulty -", lambda: self.change_depth(-1)))
        self.buttons.append(Button(bx + (bw - 6) // 2 + 6, y, (bw - 6) // 2, bh, "Difficulty +", lambda: self.change_depth(1))); y += bh + gap
        self.buttons.append(Button(bx, y, bw, bh, "Change Name/Side", self.go_to_setup)); y += bh + gap
        self.buttons.append(Button(bx, y, bw, bh, "Fullscreen (F11)", self.toggle_fullscreen))

    def _build_setup_widgets(self):
        cx = WIDTH // 2

        # Name entry boxes
        box_w, box_h = 280, 42
        self.name_box_rect = pygame.Rect(cx - box_w // 2, 150, box_w, box_h)
        self.name2_box_rect = pygame.Rect(cx - box_w // 2, 232, box_w, box_h)

        # Mode toggle button
        bw, bh, gap = 220, 50, 16
        y = 320
        self.setup_mode_button = Button(cx - bw // 2, y, bw, bh, "Mode: vs Bot", self.toggle_pending_mode)

        # Color choice buttons
        y2 = y + bh + gap
        self.setup_color_buttons = [
            Button(cx - bw - gap // 2, y2, bw, bh, "Play as White", lambda: self.finish_setup(chess.WHITE)),
            Button(cx + gap // 2, y2, bw, bh, "Play as Black", lambda: self.finish_setup(chess.BLACK)),
        ]

        # Random side button
        y3 = y2 + bh + gap
        self.setup_random_button = Button(cx - bw // 2, y3, bw, bh, "Random Side", lambda: self.finish_setup(random.choice([chess.WHITE, chess.BLACK])))

    def toggle_pending_mode(self):
        self.pending_mode_vs_bot = not self.pending_mode_vs_bot
        self.setup_mode_button.text = "Mode: vs Bot" if self.pending_mode_vs_bot else "Mode: 2 Players"
        self.name_active = 1

    def go_to_setup(self):
        self.state = "setup"
        self.pending_mode_vs_bot = self.vs_bot
        self.setup_mode_button.text = "Mode: vs Bot" if self.pending_mode_vs_bot else "Mode: 2 Players"
        self.name_active = 1

    def finish_setup(self, chosen_color):
        self.human_color = chosen_color
        self.vs_bot = self.pending_mode_vs_bot
        if not self.player_name.strip():
            self.player_name = "Player 1" if self.vs_bot else "White Player"
        if not self.vs_bot and not self.player_black_name.strip():
            self.player_black_name = "Black Player"
        self.flipped = (chosen_color == chess.BLACK)
        self.state = "playing"
        self.new_game()

    def new_game(self):
        self.board = chess.Board()
        self.selected_square = None
        self.legal_targets = []
        self.last_move = None
        self.move_log = []
        self.game_over_msg = None
        self.awaiting_promotion = None
        self.status_msg = "New game started."

    def undo_move(self):
        if self.awaiting_promotion is not None:
            self.awaiting_promotion = None
            return
        if not self.board.move_stack:
            return
        self.board.pop()
        if self.move_log:
            self.move_log.pop()
        # if playing vs bot, undo bot's move too so it's human's turn again
        if self.vs_bot and self.board.move_stack and self.board.turn != self.human_color:
            self.board.pop()
            if self.move_log:
                self.move_log.pop()
        self.selected_square = None
        self.legal_targets = []
        self.game_over_msg = None
        self.last_move = self.board.peek() if self.board.move_stack else None
        self.status_msg = "Move undone."

    def resign(self):
        if self.state != "playing" or self.game_over_msg is not None:
            return
        white_name = self.player_name or "White"
        black_name = self.player_black_name or "Black"
        if self.vs_bot:
            # Only the human can resign; the bot takes the win.
            human_name = self.player_name or "You"
            self.game_over_msg = f"{human_name} resigned. Bot wins!"
        else:
            # In hotseat mode, whoever's turn it is resigns.
            if self.board.turn == chess.WHITE:
                resigner, winner = white_name, black_name
            else:
                resigner, winner = black_name, white_name
            self.game_over_msg = f"{resigner} resigned. {winner} wins!"
        self.status_msg = "Game ended by resignation."
        self.selected_square = None
        self.legal_targets = []
        self.awaiting_promotion = None

    def flip_board(self):
        self.flipped = not self.flipped

    def toggle_mode(self):
        self.vs_bot = not self.vs_bot
        self.status_msg = "Mode: Human vs Bot" if self.vs_bot else "Mode: Human vs Human"
        self.selected_square = None
        self.legal_targets = []

    def change_depth(self, delta):
        self.bot_depth = max(1, min(4, self.bot_depth + delta))
        self.status_msg = f"Bot difficulty = {self.bot_depth}"

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # Switch to fullscreen: get the current display info to use native resolution
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED
            )
            self.status_msg = "Fullscreen ON (F11 to toggle)"
        else:
            self.screen = pygame.display.set_mode(self.native_size)
            self.status_msg = "Windowed mode (F11 to toggle)"
        # Rebuild setup widgets since their positions depend on WIDTH/HEIGHT constants
        # (setup uses WIDTH // 2 for centering, which is fine whether scaled or not)

    # ------------------------------------------------------------ Geometry
    def square_to_pixel(self, square):
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        if self.flipped:
            col = 7 - file
            row = rank
        else:
            col = file
            row = 7 - rank
        return col * SQ_SIZE, row * SQ_SIZE

    def pixel_to_square(self, x, y):
        if x < 0 or x >= BOARD_PX or y < 0 or y >= BOARD_PX:
            return None
        col = x // SQ_SIZE
        row = y // SQ_SIZE
        if self.flipped:
            file = 7 - col
            rank = row
        else:
            file = col
            rank = 7 - row
        return chess.square(file, rank)

    # --------------------------------------------------------------- Draw
    def draw_board(self):
        for square in chess.SQUARES:
            x, y = self.square_to_pixel(square)
            file, rank = chess.square_file(square), chess.square_rank(square)
            is_light = (file + rank) % 2 == 1
            color = LIGHT if is_light else DARK
            pygame.draw.rect(self.screen, color, (x, y, SQ_SIZE, SQ_SIZE))

        # last move highlight
        if self.last_move is not None:
            for sq in (self.last_move.from_square, self.last_move.to_square):
                x, y = self.square_to_pixel(sq)
                s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
                s.fill((*HILITE_LAST, 120))
                self.screen.blit(s, (x, y))

        # check highlight
        if self.board.is_check():
            king_sq = self.board.king(self.board.turn)
            if king_sq is not None:
                x, y = self.square_to_pixel(king_sq)
                s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
                s.fill((*CHECK_COLOR, 130))
                self.screen.blit(s, (x, y))

        # selected square highlight
        if self.selected_square is not None:
            x, y = self.square_to_pixel(self.selected_square)
            s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
            s.fill((*HILITE_SELECT, 150))
            self.screen.blit(s, (x, y))

            # legal destinations
            for move in self.legal_targets:
                tx, ty = self.square_to_pixel(move.to_square)
                center = (tx + SQ_SIZE // 2, ty + SQ_SIZE // 2)
                if self.board.is_capture(move):
                    pygame.draw.circle(self.screen, HILITE_CAPTURE, center, SQ_SIZE // 2 - 4, width=5)
                else:
                    pygame.draw.circle(self.screen, HILITE_MOVE, center, SQ_SIZE // 7)

        # coordinates
        for i in range(8):
            file_label = chr(ord('a') + (7 - i if self.flipped else i))
            rank_label = str(i + 1 if self.flipped else 8 - i)
            lbl = self.ui_font_small.render(file_label, True, (0, 0, 0))
            self.screen.blit(lbl, (i * SQ_SIZE + SQ_SIZE - 14, BOARD_PX - 16))
            lbl2 = self.ui_font_small.render(rank_label, True, (0, 0, 0))
            self.screen.blit(lbl2, (2, i * SQ_SIZE + 2))

    def draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is None:
                continue
            x, y = self.square_to_pixel(square)
            symbol = PIECE_UNICODE[piece.symbol()]
            # shadow for contrast
            shadow = self.piece_font.render(symbol, True, (0, 0, 0))
            self.screen.blit(shadow, shadow.get_rect(center=(x + SQ_SIZE // 2 + 2, y + SQ_SIZE // 2 + 2)))
            color = (255, 255, 255) if piece.color == chess.WHITE else (25, 25, 25)
            text = self.piece_font.render(symbol, True, color)
            self.screen.blit(text, text.get_rect(center=(x + SQ_SIZE // 2, y + SQ_SIZE // 2)))

    def draw_sidebar(self):
        panel = pygame.Rect(BOARD_PX, 0, SIDEBAR_W, HEIGHT)
        pygame.draw.rect(self.screen, BG_SIDEBAR, panel)

        title = self.title_font.render("Chess", True, ACCENT)
        self.screen.blit(title, (BOARD_PX + 20, 15))

        mode_txt = "Mode: Human vs Bot" if self.vs_bot else "Mode: Human vs Human"
        self.screen.blit(self.ui_font.render(mode_txt, True, TEXT_COLOR), (BOARD_PX + 20, 55))

        white_name = self.player_name or "White"
        black_name = "Bot" if self.vs_bot and self.human_color == chess.WHITE else \
                     (self.player_name if self.vs_bot and self.human_color == chess.BLACK else self.player_black_name)
        if self.vs_bot:
            white_label = self.player_name if self.human_color == chess.WHITE else "Bot"
            black_label = self.player_name if self.human_color == chess.BLACK else "Bot"
        else:
            white_label = self.player_name or "White"
            black_label = self.player_black_name or "Black"
        self.screen.blit(self.ui_font_small.render(f"White: {white_label}", True, TEXT_COLOR), (BOARD_PX + 20, 80))
        self.screen.blit(self.ui_font_small.render(f"Black: {black_label}", True, TEXT_COLOR), (BOARD_PX + 20, 100))

        if self.vs_bot:
            self.screen.blit(self.ui_font.render(f"Bot depth: {self.bot_depth}", True, TEXT_COLOR), (BOARD_PX + 20, 122))

        turn_txt = "Turn: White" if self.board.turn == chess.WHITE else "Turn: Black"
        self.screen.blit(self.ui_font.render(turn_txt, True, TEXT_COLOR), (BOARD_PX + 20, 150))

        if self.board.is_check() and not self.board.is_checkmate():
            chk = self.ui_font.render("CHECK!", True, (255, 90, 90))
            self.screen.blit(chk, (BOARD_PX + 20, 175))

        if self.bot_thinking:
            think = self.ui_font.render("Bot is thinking...", True, (255, 210, 90))
            self.screen.blit(think, (BOARD_PX + 20, 200))

        if self.status_msg:
            msg = self.ui_font_small.render(self.status_msg, True, (170, 210, 255))
            self.screen.blit(msg, (BOARD_PX + 20, 225))

        # move history
        hist_title = self.ui_font.render("Move History", True, TEXT_COLOR)
        self.screen.blit(hist_title, (BOARD_PX + 20, 250))
        pygame.draw.line(self.screen, (80, 80, 90), (BOARD_PX + 20, 275), (WIDTH - 20, 275), 1)

        max_lines = 4
        start_idx = max(0, len(self.move_log) - max_lines * 2)
        y = 280
        i = start_idx
        while i < len(self.move_log) and y < 365:
            move_no = i // 2 + 1
            if i % 2 == 0:
                white_move = self.move_log[i]
                black_move = self.move_log[i + 1] if i + 1 < len(self.move_log) else ""
                line = f"{move_no}. {white_move}   {black_move}"
                self.screen.blit(self.ui_font_small.render(line, True, TEXT_COLOR), (BOARD_PX + 20, y))
                y += 22
                i += 2
            else:
                i += 1

        # buttons
        for btn in self.buttons:
            btn.draw(self.screen, self.ui_font_small)

    def draw_promotion_picker(self):
        if self.awaiting_promotion is None:
            return
        from_sq, to_sq, color = self.awaiting_promotion
        options = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        box_w, box_h = 4 * SQ_SIZE, SQ_SIZE + 40
        bx = (BOARD_PX - box_w) // 2
        by = (BOARD_PX - box_h) // 2
        pygame.draw.rect(self.screen, (245, 245, 245), (bx, by, box_w, box_h), border_radius=10)
        pygame.draw.rect(self.screen, (20, 20, 20), (bx, by, box_w, box_h), width=3, border_radius=10)
        label = self.ui_font.render("Choose promotion:", True, (20, 20, 20))
        self.screen.blit(label, (bx + 10, by + 5))
        self.promo_rects = []
        for idx, ptype in enumerate(options):
            rx = bx + idx * SQ_SIZE
            ry = by + 35
            rect = pygame.Rect(rx, ry, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(self.screen, (225, 225, 225), rect)
            pygame.draw.rect(self.screen, (20, 20, 20), rect, width=1)
            symbol_char = chess.piece_symbol(ptype).upper() if color == chess.WHITE else chess.piece_symbol(ptype)
            symbol = PIECE_UNICODE[symbol_char]
            piece_color = (0, 0, 0) if color == chess.WHITE else (0, 0, 0)
            text = self.piece_font.render(symbol, True, piece_color)
            self.screen.blit(text, text.get_rect(center=rect.center))
            self.promo_rects.append((rect, ptype))

    def draw_game_over(self):
        if not self.game_over_msg:
            return
        overlay = pygame.Surface((BOARD_PX, BOARD_PX), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))
        # Wrap long messages (e.g. resignation text with names) onto two lines if needed
        text_surf = self.big_font.render(self.game_over_msg, True, (255, 255, 255))
        if text_surf.get_width() > BOARD_PX - 40:
            small_over_font = pygame.font.SysFont("arial", 28, bold=True)
            text_surf = small_over_font.render(self.game_over_msg, True, (255, 255, 255))
        self.screen.blit(text_surf, text_surf.get_rect(center=(BOARD_PX // 2, BOARD_PX // 2 - 20)))
        sub = self.ui_font.render("Click 'New Game' to play again", True, (220, 220, 220))
        self.screen.blit(sub, sub.get_rect(center=(BOARD_PX // 2, BOARD_PX // 2 + 30)))

    # ---------------------------------------------------------- Setup UI
    def _draw_text_box(self, rect, text, active):
        pygame.draw.rect(self.screen, (50, 50, 58), rect, border_radius=6)
        border_color = ACCENT if active else (95, 95, 105)
        pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=6)
        txt_surf = self.ui_font.render(text, True, (240, 240, 240))
        self.screen.blit(txt_surf, (rect.x + 10, rect.y + (rect.height - txt_surf.get_height()) // 2))
        # blinking cursor
        if active and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = rect.x + 10 + txt_surf.get_width() + 2
            pygame.draw.line(self.screen, (240, 240, 240),
                              (cursor_x, rect.y + 8), (cursor_x, rect.bottom - 8), 2)

    def render_setup(self):
        self.screen.fill((22, 22, 26))
        title = self.setup_title_font.render("Chess - New Game Setup", True, ACCENT)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 70)))

        name1_label = "Your name:" if self.pending_mode_vs_bot else "White player name:"
        lbl1 = self.ui_font.render(name1_label, True, TEXT_COLOR)
        self.screen.blit(lbl1, (self.name_box_rect.x, self.name_box_rect.y - 26))
        self._draw_text_box(self.name_box_rect, self.player_name, self.name_active == 1)

        if not self.pending_mode_vs_bot:
            lbl2 = self.ui_font.render("Black player name:", True, TEXT_COLOR)
            self.screen.blit(lbl2, (self.name2_box_rect.x, self.name2_box_rect.y - 26))
            self._draw_text_box(self.name2_box_rect, self.player_black_name, self.name_active == 2)

        self.setup_mode_button.draw(self.screen, self.ui_font)
        for btn in self.setup_color_buttons:
            btn.draw(self.screen, self.ui_font)
        self.setup_random_button.draw(self.screen, self.ui_font)

        hint1 = self.ui_font_small.render("Click a box to type your name(s), pick a mode,", True, (170, 210, 255))
        hint2 = self.ui_font_small.render("then choose a side to start the game.", True, (170, 210, 255))
        self.screen.blit(hint1, hint1.get_rect(center=(WIDTH // 2, HEIGHT - 50)))
        self.screen.blit(hint2, hint2.get_rect(center=(WIDTH // 2, HEIGHT - 28)))

    def handle_setup_click(self, pos):
        if self.name_box_rect.collidepoint(pos):
            self.name_active = 1
            return
        if not self.pending_mode_vs_bot and self.name2_box_rect.collidepoint(pos):
            self.name_active = 2
            return
        if self.setup_mode_button.handle_click(pos):
            return
        for btn in self.setup_color_buttons:
            if btn.handle_click(pos):
                return
        self.setup_random_button.handle_click(pos)

    def handle_setup_keydown(self, event):
        target_attr = "player_name" if self.name_active == 1 else "player_black_name"
        current = getattr(self, target_attr)
        if event.key == pygame.K_BACKSPACE:
            current = current[:-1]
        elif event.key == pygame.K_TAB:
            if not self.pending_mode_vs_bot:
                self.name_active = 2 if self.name_active == 1 else 1
            return
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return
        else:
            ch = event.unicode
            if ch and ch.isprintable() and len(current) < 18:
                current += ch
        setattr(self, target_attr, current)

    def render(self):
        self.screen.fill((0, 0, 0))
        if self.state == "setup":
            self.render_setup()
        else:
            self.draw_board()
            self.draw_pieces()
            self.draw_sidebar()
            self.draw_promotion_picker()
            self.draw_game_over()
        pygame.display.flip()

    # ------------------------------------------------------------- Logic
    def check_game_over(self):
        white_label = self.player_name or "White"
        if self.vs_bot:
            white_label = self.player_name if self.human_color == chess.WHITE else "Bot"
            black_label = self.player_name if self.human_color == chess.BLACK else "Bot"
        else:
            black_label = self.player_black_name or "Black"

        if self.board.is_checkmate():
            winner = black_label if self.board.turn == chess.WHITE else white_label
            self.game_over_msg = f"Checkmate! {winner} wins"
        elif self.board.is_stalemate():
            self.game_over_msg = "Stalemate! Draw"
        elif self.board.is_insufficient_material():
            self.game_over_msg = "Draw: insufficient material"
        elif self.board.is_seventyfive_moves():
            self.game_over_msg = "Draw: 75-move rule"
        elif self.board.is_fivefold_repetition():
            self.game_over_msg = "Draw: fivefold repetition"
        elif self.board.can_claim_draw():
            self.game_over_msg = None  # claimable but not forced; keep playing

    def push_move(self, move):
        san = self.board.san(move)
        self.board.push(move)
        self.move_log.append(san)
        self.last_move = move
        self.selected_square = None
        self.legal_targets = []
        self.check_game_over()

    def is_promotion_move(self, from_sq, to_sq):
        piece = self.board.piece_at(from_sq)
        if piece is None or piece.piece_type != chess.PAWN:
            return False
        rank = chess.square_rank(to_sq)
        return (piece.color == chess.WHITE and rank == 7) or (piece.color == chess.BLACK and rank == 0)

    def handle_square_click(self, square):
        if self.game_over_msg is not None:
            return
        if self.vs_bot and self.board.turn != self.human_color:
            return  # not human's turn
        if self.bot_thinking:
            return

        piece = self.board.piece_at(square)

        if self.selected_square is None:
            if piece is not None and piece.color == self.board.turn:
                self.selected_square = square
                self.legal_targets = [m for m in self.board.legal_moves if m.from_square == square]
            return

        if square == self.selected_square:
            self.selected_square = None
            self.legal_targets = []
            return

        # clicking another own piece re-selects
        if piece is not None and piece.color == self.board.turn:
            self.selected_square = square
            self.legal_targets = [m for m in self.board.legal_moves if m.from_square == square]
            return

        # attempt move
        candidate = [m for m in self.legal_targets if m.to_square == square]
        if not candidate:
            return

        if self.is_promotion_move(self.selected_square, square):
            self.awaiting_promotion = (self.selected_square, square, self.board.turn)
            return

        self.push_move(candidate[0])

    def handle_promotion_click(self, pos):
        if self.awaiting_promotion is None:
            return
        from_sq, to_sq, color = self.awaiting_promotion
        for rect, ptype in getattr(self, "promo_rects", []):
            if rect.collidepoint(pos):
                move = chess.Move(from_sq, to_sq, promotion=ptype)
                if move in self.board.legal_moves:
                    self.push_move(move)
                self.awaiting_promotion = None
                return

    def maybe_bot_move(self):
        if self.state != "playing":
            return
        if self.game_over_msg is not None:
            return
        if not self.vs_bot:
            return
        if self.board.turn == self.human_color:
            return
        if self.bot_thinking:
            return
        self.bot_thinking = True
        self.render()  # show "thinking" before blocking computation
        move = bot_choose_move(self.board, self.bot_depth)
        self.bot_thinking = False
        if move is not None:
            self.push_move(move)

    # --------------------------------------------------------------- Loop
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if self.state == "setup":
                        self.handle_setup_click(pos)
                        continue
                    if self.awaiting_promotion is not None:
                        self.handle_promotion_click(pos)
                        continue
                    handled = False
                    for btn in self.buttons:
                        if btn.handle_click(pos):
                            handled = True
                            break
                    if not handled and pos[0] < BOARD_PX:
                        sq = self.pixel_to_square(*pos)
                        if sq is not None:
                            self.handle_square_click(sq)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif self.state == "setup":
                        self.handle_setup_keydown(event)

            self.maybe_bot_move()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = ChessGame()
    game.run()


if __name__ == "__main__":
    main()