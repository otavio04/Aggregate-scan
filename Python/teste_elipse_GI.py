import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def plotter(img, data_quive = [0]):
    if len(data_quive) == 1:
        plt.imshow(img, cmap='gray' if len(img.shape) != 3 else None)
        plt.show()
    else:
        plt.imshow(img, cmap='gray' if len(img.shape) != 3 else None)
        plt.quiver(data_quive[0],
                    data_quive[1],
                    data_quive[2],
                    data_quive[3],
                    color = data_quive[4],
                    scale = data_quive[5],
                    width = data_quive[6])
        plt.show()

def save_txt(data):
    path_to_save = path + "/data.txt"
    df = pd.DataFrame(data, columns=['X', 'Y', 'Angle', 'Mag'])
    df.to_csv(path_to_save, sep=';', index=False)

path = "C:/Banco de Dados/1_OCS_010/blue"
path_img_blue = path + "/10.jpg"

img_blue = cv2.imread(path_img_blue, cv2.IMREAD_UNCHANGED)
img_blue_lab = cv2.cvtColor(img_blue, cv2.COLOR_BGR2LAB)
img_b_channel = img_blue_lab[:, :, 2]
# plotter(img_b_channel)
thres, img_mask = cv2.threshold(img_b_channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# plotter(img_mask)
contour, hier = cv2.findContours(img_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
major_contourn = max(contour, key=lambda x: len(x))
img_contour = np.zeros_like(img_mask)
img_contour = cv2.drawContours(img_contour, [major_contourn], 0, (255), 1) # uint8
# plotter(img_contour)
gradient_x = cv2.Sobel(img_mask, cv2.CV_64F, 1, 0, ksize=3)
gradient_y = cv2.Sobel(img_mask, cv2.CV_64F, 0, 1, ksize=3)
gradient_angle = np.arctan2(gradient_y, gradient_x) # float64 angles in rad (-pi to pi)
gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
# plotter(gradient_angle)
contour_gradient_angle = gradient_angle.copy()
contour_gradient_angle[img_contour == 0] = 0.0
# plotter(contour_gradient_angle)
points = major_contourn.squeeze() #sai do shape (a, b, c) para (a, b) - reduz a dimensão.
x_coord = points[:, 0]
y_coord = points[:, 1]
angles = contour_gradient_angle[y_coord, x_coord]
# print(angles)
mags = gradient_magnitude[y_coord, x_coord]
data_to_save = np.array([x_coord, y_coord, angles, mags]).T
save_txt(data_to_save)

sum = 0
for i in range(len(angles) - 3):
    diff = abs(np.arctan2(np.sin(angles[i] - angles[i+3]), np.cos(angles[i] - angles[i+3])))
    sum += diff
    if diff != 0.0:
        print(f'X:{x_coord[i]}Y:{y_coord[i]}Anglei:{round(angles[i], 2)}Anglei+3:{round(angles[i+3], 2)}Diff:{round(diff, 2)}')
print(sum)

dx = -np.cos(angles)
dy = np.sin(angles)
data_to_quiver = np.array([x_coord, # x coordinates
                           y_coord, # y coordinates
                           dx,      # x projection of vector inclination
                           dy,      # y projection of vector inclination
                           'red',   # color
                           15,      # scale
                           0.001],  # width
                           dtype=object)
plotter(cv2.cvtColor(img_blue, cv2.COLOR_BGR2RGB), data_to_quiver)
