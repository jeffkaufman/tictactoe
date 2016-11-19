def application(environ, start_response):
  query_string = environ["QUERY_STRING"]
  
  response_line = "200 OK"
  output = query_string

  start_response(response_line, [('content-type', 'text/plain')])
  return (output.encode('utf8'), )
