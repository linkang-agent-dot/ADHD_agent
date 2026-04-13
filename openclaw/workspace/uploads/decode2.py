fields = [
    ('e6aca1e695b0', 'field1'),
    ('e680bbe4bca6e9878f', 'field2'),
    ('e69c80e5a4a7e58d95e6aca1', 'field3'),
    ('e69c80e5b08fe58d95e6aca1', 'field4'),
    ('Olde8b5b7e5a78be5be80', 'field5'),
    ('Newe69c80e7bb88e5be80', 'field6'),
]
for hex_str, name in fields:
    b = bytes.fromhex(hex_str)
    print(name + ' (' + hex_str + '): ' + b.decode('utf-8'))
