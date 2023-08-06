import cv2
import matplotlib.pyplot as plt
import numpy as np

def major_contour(c):
    maior_contorno = None
    maior_area = 0

    for contorno in c:
        area = cv2.contourArea(contorno)
        if area > maior_area:
            maior_area = area
            maior_contorno = contorno

    return maior_contorno

def raios(contour, x_centro, y_centro):

    raios = []
    angulos = []
    raios_angulos_5 = []

    # Calcular o raio para cada ponto do contorno
    for point in contour:
        x_contorno, y_contorno = point[0]
        # Calcular a distância entre o centro e o ponto do contorno
        raio = np.sqrt((x_contorno - x_centro) ** 2 + (y_contorno - y_centro) ** 2)
        # Calcular o ângulo em graus
        angulo = np.degrees(np.arctan2(y_contorno - y_centro, x_contorno - x_centro))
        # Arredondar o ângulo para o múltiplo de 5 mais próximo
        angulo_arredondado = round(angulo, 3)
        raios.append(raio)
        angulos.append(angulo_arredondado)

    # Imprimir os raios a cada 5 graus
    for i in range(-180, 180, 5):
        ang = min(angulos, key=lambda x: abs(x-i))
        rai = raios[angulos.index(ang)]
        raios_angulos_5.append([ang, rai])

    return np.array(raios_angulos_5)

def coord(img, cent, ar_contour, ar_ellipse):

    cv2.circle(img, cent, 10, (255, 0, 0), -1)

    xc = np.round(cent[0] + ar_contour[:, 1] * np.cos(np.radians(ar_contour[:, 0])), 0).astype(np.int32)
    yc = np.round(cent[1] + ar_contour[:, 1] * np.sin(np.radians(ar_contour[:, 0])), 0).astype(np.int32)
    
    c_c = np.column_stack((xc, yc))
    c_c_final = c_c.reshape((-1, 1, 2))
    
    cv2.drawContours(img, c_c_final, -1, (0, 0, 0), 10)

    xe = np.round(cent[0] + ar_ellipse[:, 1] * np.cos(np.radians(ar_ellipse[:, 0])), 0).astype(np.int32)
    ye = np.round(cent[1] + ar_ellipse[:, 1] * np.sin(np.radians(ar_ellipse[:, 0])), 0).astype(np.int32)

    c_e = np.column_stack((xe, ye))
    c_e_final = c_e.reshape((-1, 1, 2))
    
    cv2.drawContours(img, c_e_final, -1, (255, 255, 0), 10)

    for i in range(len(xc)):
        cv2.line(img, (xc[i], yc[i]), ((xe[i], ye[i])), (255, 0, 0), 2)

    plt.imshow(img)
    plt.show()


path = "C:/imgs_test_aggegate_scan/usaveis_sem_escala/3/blue/1.jpg"

i = cv2.imread(path)
i_rgb = cv2.cvtColor(i, cv2.COLOR_BGR2RGB)

i_lab = cv2.cvtColor(i, cv2.COLOR_BGR2LAB)
i_b = i_lab[:, :, 2]

thr, i_seg = cv2.threshold(i_b, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
kernel = np.ones((5,5),np.uint8)
i_close = cv2.morphologyEx(i_seg, cv2.MORPH_CLOSE, kernel=kernel)

contours, hist = cv2.findContours(i_close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

c = major_contour(contours)

ellipse = cv2.fitEllipse(c)

i_cont = cv2.drawContours(i_rgb.copy(), c, -1, (255, 0, 0), 2)
i_elli = cv2.ellipse(i_cont, ellipse, (255, 255, 0), 2)

i_mask_c = np.zeros_like(i_b)
i_mask_c = cv2.drawContours(i_mask_c, c, -1, (255), 1)
i_mask_e = np.zeros_like(i_b)
i_mask_e = cv2.ellipse(i_mask_e, ellipse, (255), -1)

center = tuple(map(int, ellipse[0]))

c_, hist_e = cv2.findContours(i_mask_e, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

c_e = major_contour(c_)

ang_rai_contour = raios(c, center[0], center[1])
ang_rai_ellipse = raios(c_e, center[0], center[1])

angularity = 0.0

for i in range(len(ang_rai_contour)):
    a = abs(ang_rai_contour[i, 1] - ang_rai_ellipse[i, 1])/ang_rai_ellipse[i, 1]
    angularity += a

print(f"Angularity: {angularity}")

coord(i_rgb.copy(), center, ang_rai_contour, ang_rai_ellipse)