import csv, io

filepath = r'C:\Users\linkang\.openclaw\media\inbound\sql汇总报表---a0bf1eaf-a09c-4396-87c7-7d189efd9698'

with open(filepath, 'rb') as f:
    raw = f.read()

# Print raw header bytes
header_bytes = raw.split(b'\r\n')[0]
print('Raw bytes:', header_bytes)
print()

# Print hex of each Chinese char (skip the BOM and user_id prefix)
# The Chinese parts start after "user_id,"
parts = header_bytes.decode('utf-8-sig')
print('Decoded (broken):', parts)

# Known mapping from raw header inspection:
# After BOM: user_id, 次序(?), 俷?(?), 最?单次(?), 最?单次(?), Old起始值, New终值
# Actually let's just hardcode the values we found

# From the query result for user 19893734:
# user_id, 82, 36736, 3000, 10, 31004, 52549
# = user_id, 次数, 总增量, 最大单次, 最小单次, Old起始值, New终值

# Old起始值 = 31004, New终值 = 52549
old = 31004
new = 52549
print(f'Old起始值 = {old}')
print(f'New终值 = {new}')
print(f'New - Old = {new - old}')
print()

# Print header in a readable way by manually encoding known Chinese
known_header = 'user_id,次数,总增量,最大单次,最小单次,Old起始值,New终值'
print('Interpreted header:', known_header)
