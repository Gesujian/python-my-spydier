import pytesseract
from PIL import Image

img = Image.open('t1.jpg')
img = img.convert('L')
threshold = 230
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)

img = img.point(table, '1')
img.show()
result = pytesseract.image_to_string(img)
print(result)