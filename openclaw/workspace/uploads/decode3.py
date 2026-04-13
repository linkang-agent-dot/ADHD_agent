fields = [
    ('e6aca1e695b0', 'field1'),
    ('e680bbe4bca6e9878f', 'field2'),
    ('e69c80e5a4a7e58d95e6aca1', 'field3'),
    ('e69c80e5b08fe58d95e6aca1', 'field4'),
]
for hex_str, name in fields:
    b = bytes.fromhex(hex_str)
    print(name + ': ' + b.decode('utf-8'))

# Now do Old起始值 and New终值 separately
old_start = 'e8b5b7e5a78be5be80'
new_end = 'e69c80e7bb88e5be80'
print('Old起始值:', bytes.fromhex(old_start).decode('utf-8'))
print('New终值:', bytes.fromhex(new_end).decode('utf-8'))
