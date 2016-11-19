import sys
import random

class TictactoeException(Exception):
  def __init__(self, message):
    self.message_ = message
  def ErrorMessage(self):
    return self.message_

def parse_board(board_string):
  board_string = board_string.replace("+", " ")
  if len(board_string) != 9:
    raise TictactoeException("input board should be length 9")

  board = [ [' '] * 3 for i in range(3)]
  for i, c in enumerate(board_string):
    if c not in "xo ":
      raise TictactoeException("invalid character '%s' at position %s" % (c, i))
    col_n = i % 3
    row_n = i / 3
    board[row_n][col_n] = c

  return board

def serialize_board(board):
  return "".join("".join(row) for row in board)

def verify_plausibly_my_turn(board):
  # Throws a TictactoeException if it's not plausbly our turn.
  #
  # Either player can go first, so we should play if either:
  # 1) There is one fewer o than x (they went first)
  # 2) There are the same number of os and xs (we went first)
  #
  # If the board is full, then it also can't be our turn.
  total_xs = 0
  total_os = 0
  for c in serialize_board(board):
    if c == "x":
      total_xs += 1
    elif c == "o":
      total_os += 1
  if total_xs + total_os == 9:
    raise TictactoeException("the board is full")
  if total_xs > total_os + 1:
    raise TictactoeException("you've taken too many turns")
  if total_xs == total_os - 1:
    raise TictactoeException("it's actually your turn")
  if total_xs < total_os - 1:
    raise TictactoeException("you're claiming I took too many turns")

def legal_moves(board):
  moves = []
  for row_n, row in enumerate(board):
    for col_n, val in enumerate(row):
      if val == ' ':
        moves.append((row_n, col_n))
  return moves

def update(board, row_n, col_n, val='o'):
  assert board[row_n][col_n] == ' '
  board[row_n][col_n] = val

def make_random_move(board):
  row_n, col_n = random.choice(legal_moves(board))
  update(board, row_n, col_n)

def make_book_move(board):
  # Strategy from https://www.quora.com/Is-there-a-way-to-never-lose-at-Tic-Tac-Toe
  book = {
    # They're letting us go first: play in the center.
    "         ": (1,1),

    # They took their first move in a corner: play in the center.
    "x        ": (1,1),
    "  x      ": (1,1),
    "      x  ": (1,1),
    "        x": (1,1),

    # They took their first move in the center: play in a corner.
    "    x    ": (0,0),

    # They took their first move on an edge: play in an adjacent corner.
    " x       ": (0,0),
    "   x     ": (0,0),
    "     x   ": (2,2),
    "       x ": (2,2),
  }

  serialized_board = serialize_board(board)

  if serialized_board in book:
    row_n, col_n = book[serialized_board]
    update(board, row_n, col_n)
    return True

  return False

def clone_board(board):
  return [row[:] for row in board]

# We can compute these once on startup, since they never change.
sequences = [] # start_row, start_col, row_increment, col_increment
for i in range(3):
  sequences.append((i, 0, 0, 1))  # row i
  sequences.append((0, i, 1, 0))  # column i
sequences.append((0, 0, 1 ,1))    # top-left to bottom-right diagonal
sequences.append((0, 2, 1, -1))   # top-right to bottom-left diagonal

def game_status(board):
  # returns:
  #  'x', 'o': that player won
  #  'd':      draw
  #  None:     game not over

  for start_row, start_col, row_increment, col_increment in sequences:
    row_n = start_row
    col_n = start_col

    potential_winner = board[start_row][start_col]

    for j in range(3):
      if board[start_row][start_col] != board[row_n][col_n]:
        potential_winner = ' ' # mixed path: no one has won it

      row_n += row_increment
      col_n += col_increment

    if potential_winner != ' ':
      # There was only one value along the path, and it wasn't ' '.
      return potential_winner

  if ' ' in serialize_board(board):
    # There are potential moves remaining, game not over.
    return None
  else:
    # Game over, no one won, draw.
    return 'd'

def other_player(player):
  return {'x': 'o',
          'o': 'x'}[player]

def search_and_move(board, player='o'):
  # Consider all possible game trees from here, trying to find one
  # where player can win.  If we can't win, then force a draw.
  categorized_moves = {}

  for row_n, col_n in legal_moves(board):
    # You could do this all in-place, making changes and then undoing
    # them, but that seems like a hack to me.  It would be faster,
    # though, because copying is slow.
    board_copy = clone_board(board)
    update(board_copy, row_n, col_n, player)
    winner = game_status(board_copy)
    if winner == None:
      # Game not over yet.
      winner = search_and_move(board_copy, other_player(player))
      assert winner

    # We don't need multiple moves in each cateogory, so we can just
    # overwrite.
    categorized_moves[winner] = row_n, col_n

    # If we found a winning move, might as well stop looking.
    if winner == player:
      break

  result = other_player(player)
  if player in categorized_moves:
    # prefer to win
    result = player
  elif 'd' in categorized_moves:
    # draws if need be
    result = 'd'

  row_n, col_n = categorized_moves[result]
  update(board, row_n, col_n, player)

  return result

def play_move(board):
  verify_plausibly_my_turn(board)
  if not make_book_move(board):
    search_and_move(board)

def run_game(query_string):
  response_line = "200 OK"

  if not query_string.startswith("board="):
    raise TictactoeException("expected a parameter, board")
  board = parse_board(query_string.replace("board=", "", 1))
  play_move(board)

  output = serialize_board(board)

  return response_line, output

def application(environ, start_response):
  query_string = environ["QUERY_STRING"]

  try:
    response_line, output = run_game(query_string)
  except TictactoeException, e:
    response_line = "400 Bad Request"
    output = e.ErrorMessage()

  start_response(response_line, [('content-type', 'text/plain')])
  return (output.encode('utf8'), )

# for debugging
def print_board(board_string):
  board = parse_board(board_string)
  print "\n-+-+-\n".join("|".join(row) for row in board)

# for debugging
if __name__ == "__main__":
  response_line, board_string = run_game("board=%s" % sys.argv[1])
  print response_line
  print
  print_board(board_string)
  print
  print "python tictactoe.py %s" % board_string.replace(" ", "+")
