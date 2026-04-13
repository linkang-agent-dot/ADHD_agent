from PIL import Image
import numpy as np

img1 = Image.open(r'C:\Users\linkang\.openclaw\media\inbound\dab95091-e150-45d6-84d6-f9d8fb2da2af.jpg')
img2 = Image.open(r'C:\Users\linkang\.openclaw\media\inbound\77b250f9-eb36-409f-be72-39a2b847f3cf.jpg')

# Analyze the image column by column to find the split point between icon and text
def find_split_point(img):
    arr = np.array(img)
    h, w = arr.shape[:2]
    
    # Look at each column - when text appears on right, brightness changes
    # Sum of pixel brightness per column
    brightness = arr.sum(axis=(0, 2))  # shape (w,)
    
    # Find where brightness drops significantly (black separator) 
    # vs where it picks up again (text area)
    # The text area should be brighter than pure black but different from icon area
    
    # Print brightness profile at key columns
    for x in range(0, w, 20):
        print('x={}: brightness={}'.format(x, brightness[x]))
    
    # Find the gap between icon and text
    # Look for columns with very low brightness between two bright regions
    in_figure = False
    split_col = None
    for x in range(w):
        col_brightness = brightness[x]
        if col_brightness > 5000 and not in_figure:
            in_figure = True
        elif col_brightness < 2000 and in_figure:
            # potential gap found
            if split_col is None:
                split_col = x
    print('Split column (rough):', split_col)
    return split_col

print('=== Image 1 ===')
find_split_point(img1)
print()
print('=== Image 2 ===')
find_split_point(img2)
