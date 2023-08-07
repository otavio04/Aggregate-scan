import os
import re
import sys
import cv2
import numpy as np
from tkinter import *
from PIL import ImageTk, Image
import matplotlib.pyplot as plt

class MainClass(object):

    def __init__(self):
        
        cor_bg 		= "#ddddee"
        cor_fg		= "#111122"

        self.resto = 5

        self.imgs = []
        self.rgb_imgs = []
        self.ai_images = []

        self.root = Tk()
        self.root.title('AI Angularity 2D tool')
        self.root.configure(bg = cor_bg)

        self.check_exportimg_var =IntVar()

        self.canvas = Canvas(self.root, width=600, height=400, bg=cor_fg)
        self.fLoad = LabelFrame(self.root, bg=cor_bg, text='File')
        self.canvas.grid(row=0, column=0)
        self.fLoad.grid(row=0, column=1, sticky='N')

        self.ePath = Entry(self.fLoad, width=60, cursor='xterm')
        self.cbExportimg = Checkbutton(self.fLoad, bg = cor_bg, text="Export Images", cursor='hand2', variable=self.check_exportimg_var, onvalue=1, offvalue=0)
        self.bLoad = Button(self.fLoad, width=10, text='Load images', cursor='hand2', command=self.load)
        self.bAngu = Button(self.fLoad, width=10, text='Angularity', cursor='hand2', command=lambda:self.segment(self.imgs))
        self.bReset = Button(self.fLoad, width = 10, text = "Reset", cursor='hand2', command = self.reset, fg="red")
        self.lResults = Label(self.fLoad, text='RESULTS', bg=cor_bg)
        self.lResultsData = Label(self.fLoad, text="Average: - | Standard Dev.: - | Coef. of Variation: -", bg=cor_bg)

        self.ePath.grid(row=0, column=0, padx=5, pady=5, columnspan=3)
        self.cbExportimg.grid(row=1, column=0, padx=5, pady=5, columnspan=3)
        self.bLoad.grid(row=2, column=0, padx=5, pady=5)
        self.bAngu.grid(row=2, column=1, padx=5, pady=5)
        self.bReset.grid(row=2, column=2, padx=5, pady=5)
        self.lResults.grid(row=3, column=0, columnspan=4)
        self.lResultsData.grid(row=4, column=0, columnspan=3)

        # self.ePath.insert(0, "C:/imgs_test_aggegate_scan")
        self.ePath.insert(0, "C:/imgs_test_aggegate_scan/ensaio_de_forma-sem_escala/JPG_files/1/blue")

        self.root.mainloop()

    def load(self):

        self.path_folder_get = str(self.ePath.get())

        self.imgs = self.load_images_from_folder(self.path_folder_get)

        for i in self.imgs:
            j = cv2.cvtColor(i, cv2.COLOR_BGR2RGB)
            self.rgb_imgs.append(j)

        img_rgb = cv2.cvtColor(self.imgs[0].copy(), cv2.COLOR_BGR2RGB)
        img_copy = self.resize(img_rgb)
        image_pil = Image.fromarray(img_copy)
        photo = ImageTk.PhotoImage(image_pil)
        self.canvas.photo = photo
        self.canvas.create_image(0, 0, anchor="nw", image=photo, tag='img')

    def load_images_from_folder(self, folder):
        images = []
        for filename in os.listdir(folder):
            img = cv2.imread(os.path.join(folder, filename))
            if img is not None:
                images.append((filename, img))

        # Ordenar a lista de imagens pelo valor numérico presente nos nomes dos arquivos
        images.sort(key=lambda x: int(re.findall(r'\d+', x[0])[0]))

        # Retornar apenas as imagens (removendo os nomes dos arquivos que foram usados apenas para ordenação)
        return [img for _, img in images]

    def resize(self, img):
        global p
        width_img = int(img.shape[1])
        height_img = int(img.shape[0])

        width_canvas = self.canvas.winfo_width()
        height_canvas = self.canvas.winfo_height()

        if (width_img - width_canvas) >= (height_img - height_canvas):
            p = (width_canvas)/width_img
        else:
            p = (height_canvas)/height_img

        width_r = int(img.shape[1]*p)
        height_r = int(img.shape[0]*p)
        dim = (width_r, height_r)
        img_r = cv2.resize(img.copy(), dim)
        return img_r

    def segment(self, imgs):
        images = []
        kernel = np.ones((5,5),np.uint8)
        for i in imgs:
            i_lab = cv2.cvtColor(i, cv2.COLOR_BGR2LAB)
            i_b = i_lab[:, :, 2]
            thr, i_seg = cv2.threshold(i_b, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            i_close = cv2.morphologyEx(i_seg, cv2.MORPH_CLOSE, kernel)
            images.append(i_close)

        self.contours_obj, self.contours_elli, self.centers_elli = self.contour(images)

        self.angular(self.contours_obj, self.contours_elli, self.centers_elli)

    def contour(self, imgs):
        contours_o = []
        contours_e = []
        centers = []

        for i in imgs:
            c, h = cv2.findContours(i, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            c_maior = self.major_contour(c)
            contours_o.append(c_maior)

            image_with_contours = np.zeros_like(i)
            cv2.drawContours(image_with_contours, c_maior, -1, (255), -1)

            ellipse = cv2.fitEllipse(c_maior)

            i_mask_e = np.zeros_like(i)
            i_mask_e = cv2.ellipse(i_mask_e, ellipse, (255), -1)

            center = tuple(map(int, ellipse[0]))
            centers.append(center)

            c_, hist_e = cv2.findContours(i_mask_e, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            c_e = self.major_contour(c_)
            contours_e.append(c_e)
            

        return contours_o, contours_e, centers

    def angular(self, c_o, c_e, centers_e):
        
        angularity_values = []

        for i in range(len(c_o)):

            ang_rai_contour = self.raios(c_o[i], centers_e[i][0], centers_e[i][1])
            ang_rai_ellipse = self.raios(c_e[i], centers_e[i][0], centers_e[i][1])

            angularity = 0.0

            for j in range(len(ang_rai_contour)):
                a = abs(ang_rai_contour[j, 1] - ang_rai_ellipse[j, 1])/ang_rai_ellipse[j, 1]
                angularity += a

            self.coord(self.imgs[i].copy(), centers_e[i], ang_rai_contour, ang_rai_ellipse)
            
            angularity_values.append(angularity)
        
        angularity_array = np.array(angularity_values)
        
        average = np.round(np.average(angularity_array), 2)
        standard_dev = np.round(np.std(angularity_array), 2)
        coefv = np.round(100*standard_dev/average, 2)

        self.canvas.delete('all')
        img_show = cv2.cvtColor(self.ai_images[0], cv2.COLOR_BGR2RGB)
        img_copy = self.resize(img_show)
        image_pil = Image.fromarray(img_copy)
        photo = ImageTk.PhotoImage(image_pil)
        self.canvas.photo = photo
        self.canvas.create_image(0, 0, anchor="nw", image=photo, tag='img')
        
        self.lResultsData.config(text=f"Average: {average} | Standard Dev.: {standard_dev} | Coef. of Variation: {coefv}%")

        self.save(angularity_array, average, standard_dev, coefv)


    def major_contour(self, c):
        maior_contorno = None
        maior_area = 0

        for contorno in c:
            area = cv2.contourArea(contorno)
            if area > maior_area:
                maior_area = area
                maior_contorno = contorno

        return maior_contorno

    def raios(self, contour, x_centro, y_centro):

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

    def coord(self, img, cent, ar_contour, ar_ellipse):

        cv2.circle(img, cent, 10, (0, 0, 255), -1)

        xc = np.round(cent[0] + ar_contour[:, 1] * np.cos(np.radians(ar_contour[:, 0])), 0).astype(np.int32)
        yc = np.round(cent[1] + ar_contour[:, 1] * np.sin(np.radians(ar_contour[:, 0])), 0).astype(np.int32)
        
        c_c = np.column_stack((xc, yc))
        c_c_final = c_c.reshape((-1, 1, 2))
        
        cv2.drawContours(img, c_c_final, -1, (0, 0, 0), 10)

        xe = np.round(cent[0] + ar_ellipse[:, 1] * np.cos(np.radians(ar_ellipse[:, 0])), 0).astype(np.int32)
        ye = np.round(cent[1] + ar_ellipse[:, 1] * np.sin(np.radians(ar_ellipse[:, 0])), 0).astype(np.int32)

        c_e = np.column_stack((xe, ye))
        c_e_final = c_e.reshape((-1, 1, 2))
        
        cv2.drawContours(img, c_e_final, -1, (0, 255, 255), 10)

        for i in range(len(xc)):
            cv2.line(img, (xc[i], yc[i]), ((xe[i], ye[i])), (0, 0, 255), 2)
        
        self.ai_images.append(img)

    def save(self, angularity, aver, std, cvar):
        arr = angularity.copy()
        arr1 = np.append(arr, 1000)
        arr2 = np.append(arr1, aver)
        arr3 = np.append(arr2, std)
        arr4 = np.append(arr3, cvar)

        path = str(self.ePath.get()) + "/angularity_results_AI.txt"
        
        np.savetxt(path, arr4, delimiter=";")

        if self.check_exportimg_var.get() == 1:
            path_i = str(self.ePath.get()) + "/AI_imags"
            if not os.path.exists(path_i):
                os.makedirs(path_i)

            for i in range(len(self.ai_images)):
                name_i = path_i + "/" + f"{i+1}.jpg"
                cv2.imwrite(name_i, self.ai_images[i])

    def reset(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == '__main__':
    MainClass()