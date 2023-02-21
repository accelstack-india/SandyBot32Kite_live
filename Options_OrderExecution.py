import sys
import json

# Retrieve the two objects from sys.argv
arg_str = sys.argv[1]
json_strs = arg_str.split('|')

user_data = json.loads(json_strs[0])
stock_data = json.loads(json_strs[1])

# Print the objects to confirm they were passed correctly
print(f"This is subprocess for option execution received the data: {user_data} and {stock_data}")
