import re

test_string = "bc"
is_valid = False

try:
  re.compile(test_string)
  is_valid = True
except re.error:
  is_valid = False

print(is_valid)
