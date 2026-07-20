# Pygame Chess (Human vs Bot / Human vs Human)

A complete chess game built with **pygame** (UI) and **python-chess** (rules engine).

## Features
- Full legal chess rules: castling, en passant, pawn promotion, check, checkmate,
  stalemate, 75-move rule, fivefold repetition, insufficient material.
- **Human vs Bot** or **Human vs Human** mode (toggle anytime).
- Bot AI using minimax + alpha-beta pruning with piece-square tables and move
  ordering. Adjustable difficulty (search depth 1–4).
- Click-to-select / click-to-move with legal-move highlighting (dots for quiet
  moves, rings for captures).
- Promotion picker popup (choose Queen / Rook / Bishop / Knight).
- Last-move highlight and check highlight on the king.
- Move history panel in algebraic notation.
- Undo move, Flip board, New Game buttons.
- Game-over overlay showing checkmate/stalemate/draw result.

## Setup
```bash
pip install pygame chess
python3 chess_game.py
```

## How to Play
1. Run the script — a window opens with the board on the left and a control
   panel on the right.
2. Click a piece to select it; legal destinations light up.
3. Click a highlighted square to move there. Click the same piece again to
   deselect, or click another of your own pieces to switch selection.
4. If a pawn move reaches the last rank, a popup lets you choose the
   promotion piece.
5. In **Human vs Bot** mode, the bot automatically replies after your move.
   Use "Difficulty -/+" to make the bot weaker/stronger (deeper search = stronger
   but slower).
6. Use **Toggle Mode** to switch between playing against the bot or against
   another human on the same computer (hot-seat play).
7. **Flip Board** rotates the view (useful when playing Black or hot-seat).
8. **Undo Move** takes back the last move (and the bot's reply too, in Bot mode).
9. **New Game** resets the board.

## Notes
- Piece glyphs use Unicode chess symbols rendered via system fonts
  (Segoe UI Symbol / DejaVu Sans / Apple Symbols, etc. — whichever your OS has).
  If pieces appear as boxes, install a font with chess symbol coverage
  (e.g. `sudo apt install fonts-dejavu` on Linux).
- The bot's strength is intentionally lightweight (a teaching/hobby-grade
  engine, not a tournament-strength one) — depth 3-4 already takes a
  noticeable moment to think.
