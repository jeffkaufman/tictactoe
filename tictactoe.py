import sys

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
    col = i % 3
    row = i / 3
    board[row][col] = c

  return board

def serialize_board(board):
  return "".join("".join(row) for row in board)

def run_game(query_string):
  response_line = "200 OK"

  if not query_string.startswith("board="):
    raise TictactoeException("expected a parameter, board")
  board = parse_board(query_string.replace("board=", "", 1))

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
  response_line, board_string = run_game(sys.argv[1])
  print response_line
  print
  print_board(board_string)
