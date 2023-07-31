import os
import cv2
import numpy as np
from tkinter import *
from PIL import ImageTk, Image
import matplotlib.pyplot as plt


class MainClass (object):

    def __init__(self):
        
        cor_bg 		= "#ddddee"
        cor_fg		= "#111122"

        self.imgs = []
        self.binar_imgs = []

        self.root = Tk()
        self.root.title('Background remove tool')
        self.root.configure(bg = cor_bg)

        self.canvas = Canvas(self.root, width=600, height=400, bg=cor_fg)
        self.fLoad = LabelFrame(self.root, bg=cor_bg, text='File')
        self.canvas.grid(row=0, column=0)
        self.fLoad.grid(row=0, column=1, sticky='N')

        self.ePath = Entry(self.fLoad, width=60, cursor='xterm')
        self.bLoad = Button(self.fLoad, width=10, text='Load images', cursor='hand2', command=self.load)
        self.bSegm = Button(self.fLoad, width=10, text='Segmentation', cursor='hand2', command=lambda:self.segment(self.imgs))
        self.bAngu = Button(self.fLoad, width=10, text='Angularity', cursor='hand2', command=self.angular)

        self.ePath.grid(row=0, column=0, padx=5, pady=5, columnspan=3)
        self.bLoad.grid(row=1, column=0, padx=5, pady=5, sticky='W')
        self.bSegm.grid(row=1, column=1, padx=5, pady=5, sticky='W')
        self.bAngu.grid(row=1, column=2, padx=5, pady=5, sticky='W')

        # self.ePath.insert(0, "C:/imgs_test_aggegate_scan")
        self.ePath.insert(0, "C:/imgs_test_aggegate_scan/usaveis_sem_escala/brita1/blue")

        self.root.mainloop()


    def load(self):

        self.path_folder_get = str(self.ePath.get())

        self.imgs = self.load_images_from_folder(self.path_folder_get)
        img_copy = self.resize(self.imgs[0].copy())

        # print(img_copy.dtype)

        image_pil = Image.fromarray(cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB))

        photo = ImageTk.PhotoImage(image_pil)
        self.canvas.photo = photo
        self.canvas.create_image(0, 0, anchor="nw", image=photo, tag='img')

    def load_images_from_folder(self, folder):
        images = []
        for filename in os.listdir(folder):
            img = cv2.imread(os.path.join(folder, filename))
            if img is not None:
                images.append(img)
        return images

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
        contours = []
        for i in imgs:
            i_lab = cv2.cvtColor(i, cv2.COLOR_BGR2LAB)
            i_b = i_lab[:, :, 2]
            i_seg = cv2.threshold(i_b, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            # i_seg3c = i.copy()
            # i_seg3c[i_seg[1] == 0] = (0, 0, 0)
            # i_seg3c[i_seg[1] == 255] = (255, 255, 255)
            # print(i_seg3c.dtype)

            c, h = cv2.findContours(i_seg[1], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            c2 = c[0]
            if len(c) == 1:
                c2 = c
            elif len(c) > 1:
                indice_maior_contorno = 0
                maior_tamanho_contorno = len(c[0])

                for i in range(1, len(c)):
                    tamanho_contorno_atual = len(c[i])
                    if tamanho_contorno_atual > maior_tamanho_contorno:
                        maior_tamanho_contorno = tamanho_contorno_atual
                        indice_maior_contorno = i
                c2 = c[indice_maior_contorno]
            
            contours.append(c2)

            image_with_contours = i.copy()
            cv2.drawContours(image_with_contours, c2, -1, (0, 0, 255), 2)
            images.append(image_with_contours)

        cv2.imshow('i', images[0])
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def angular(self, imgs):
        pass

if __name__ == '__main__':
    MainClass()