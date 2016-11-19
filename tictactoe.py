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

def update(board, row_n, col_n):
  assert board[row_n][col_n] == ' '
  board[row_n][col_n] = 'o'

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

def play_move(board):
  verify_plausibly_my_turn(board)
  if not make_book_move(board):
    make_random_move(board)

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
