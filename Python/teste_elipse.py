import cv2
import numpy as np
from matplotlib import pyplot as plt

def min_square_ellip():
    rect = cv2.fitEllipse(contour)
    # rect = cv2.minAreaRect(contour)

    i_ellip = cv2.ellipse(i_contour, rect, 125, 1)

    box = cv2.boxPoints(rect)
    box = np.intp(box)
    i_rect = cv2.drawContours(i_ellip, [box], 0, 50)
    return i_rect

def aims_ellip():
    rect = cv2.minAreaRect(contour)

    i_ellip = cv2.ellipse(i_contour, rect, 125, 1)

    box = cv2.boxPoints(rect)
    box = np.intp(box)
    i_rect = cv2.drawContours(i_ellip, [box], 0, 50)
    return i_rect

#Make an image of min aggregate area
l = 500
s = (l, l, 1)

i_float32 = np.zeros(s, dtype=np.float32)
i_uint8_zeros = np.zeros(s, np.uint8)

offset_x = 150
offset_y = 100
thik = 1
corner_min = int(l/2-thik)
corner_max = int(l/2+thik)

i_float32[corner_min:corner_max, offset_x:500-offset_x] = 1
i_float32[offset_y:500-offset_y, corner_min:corner_max] = 1

i_uint8 = np.uint8(i_float32 * 255)

contours, _ = cv2.findContours(i_uint8, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
contour = contours[0]

i_contour = cv2.drawContours(i_uint8_zeros, contour, -1, 255, 1)

i_show = min_square_ellip()
# i_show = aims_ellip()

plt.imshow(i_show, cmap='magma')
plt.show()