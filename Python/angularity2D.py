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
        self.sobel_images = []

        self.list_of_contours = []
        self.angles_of_contours = []
        self.angularity_of_contours = []

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
        self.bAngu = Button(self.fLoad, width=10, text='Angularity', cursor='hand2', command=lambda:self.angular(self.angles_of_contours))
        self.lResults = Label(self.fLoad, text='RESULTS', bg=cor_bg)
        self.lResultsData = Label(self.fLoad, text="Average: - | Standard Dev.: - | Coef. of Variation: -", bg=cor_bg)

        self.ePath.grid(row=0, column=0, padx=5, pady=5, columnspan=3)
        self.bLoad.grid(row=1, column=0, padx=5, pady=5)
        self.bSegm.grid(row=1, column=1, padx=5, pady=5)
        self.bAngu.grid(row=1, column=2, padx=5, pady=5)
        self.lResults.grid(row=2, column=0, columnspan=3)
        self.lResultsData.grid(row=3, column=0, columnspan=3)

        # self.ePath.insert(0, "C:/imgs_test_aggegate_scan")
        self.ePath.insert(0, "C:/imgs_test_aggegate_scan/usaveis_sem_escala/brita1/blue")

        self.root.mainloop()


    def load(self):

        self.path_folder_get = str(self.ePath.get())

        self.imgs = self.load_images_from_folder(self.path_folder_get)

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
        kernel = np.ones((5,5),np.uint8)
        for i in imgs:
            i_lab = cv2.cvtColor(i, cv2.COLOR_BGR2LAB)
            i_b = i_lab[:, :, 2]
            thr, i_seg = cv2.threshold(i_b, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            i_close = cv2.morphologyEx(i_seg, cv2.MORPH_CLOSE, kernel)
            images.append(i_close)

        list_of_contours = self.contour(images)
        sobel_imgs, sobel_angles = self.sobel_process(images, list_of_contours)

        self.sobel_images = sobel_imgs
        self.angles_of_contours = sobel_angles

        self.canvas.delete('all')
        img_gray = sobel_imgs[0]
        img_copy = self.resize(img_gray)
        image_pil = Image.fromarray(img_copy)
        photo = ImageTk.PhotoImage(image_pil)
        self.canvas.photo = photo
        self.canvas.create_image(0, 0, anchor="nw", image=photo, tag='img')

    def contour(self, imgs):
        contours = []
        images = []

        for i in imgs:
            c, h = cv2.findContours(i, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            contours.append(c)

            image_with_contours = np.zeros_like(i)
            cv2.drawContours(image_with_contours, c, -1, (255), 1)
            images.append(image_with_contours)
            # np.savetxt("C:/imgs_test_aggegate_scan/gradient_angle_vs.txt", c[0][:, 0], delimiter=";")

        return contours
        
    def sobel_process(self, imgs, c):
        angles = []
        i_vectors = []

        for i in range(len(imgs)):
            gradient_x = cv2.Sobel(imgs[i], cv2.CV_64F, 1, 0, ksize=5)
            gradient_y = cv2.Sobel(imgs[i], cv2.CV_64F, 0, 1, ksize=5)
            gradient_angle = np.arctan2(gradient_y, gradient_x)
            gradient_angle_graus = (np.round(gradient_angle*180/np.pi, 0)).astype(np.uint32)

            ga_list = []
            coord_xi = []
            coord_yi = []
            mask = np.zeros_like(imgs[i])

            for j in c[i][0]:
                coord_xi.append(j[:, 0][0])
                coord_yi.append(j[:, 1][0])
                ga_list.append(gradient_angle[j[:, 1][0], j[:, 0][0]])
                mask[j[:, 1][0], j[:, 0][0]] = gradient_angle_graus[j[:, 1][0], j[:, 0][0]]
            
            angles.append(ga_list)

            ga_array = np.array(ga_list)
            xi_array = np.array(coord_xi)
            yi_array = np.array(coord_yi)

            seno = np.sin(ga_array)
            cosseno = np.cos(ga_array)

            xf_array = (coord_xi + np.round(cosseno*(-1)*30, 0)).astype(np.uint32)
            yf_array = (coord_yi + np.round(seno*(-1)*30, 0)).astype(np.uint32)

            count = 0
            for xi, yi, xf, yf in zip(xi_array, yi_array, xf_array, yf_array):
                if count%1 == 0:
                    cv2.arrowedLine(mask, (xi, yi), (xf, yf), (255), 1)
                count = count + 1

            i_vectors.append(mask)
        
        return i_vectors, angles

    def angular(self, angles):
        angularity_values = []

        for a in angles:
            n = len(a)
            if n < 4:
                raise ValueError("O contorno deve ter pelo menos 4 pontos.")

            angle_sum = 0.0
            for i in range(n - 3):
                angle_diff = abs(a[i] - a[i + 3])*180/np.pi
                angle_sum += angle_diff

            ang = (1 / ((n / 3) - 1)) * angle_sum
            
            angularity_values.append(ang)
        
        angularity_array = np.array(angularity_values)
        self.angularity_of_contours = angularity_array.copy()
        
        average = np.round(np.average(angularity_array), 2)
        standard_dev = np.round(np.std(angularity_array), 2)
        coefv = np.round(standard_dev/average, 2)
        
        self.lResultsData.config(text=f"Average: {average} | Standard Dev.: {standard_dev} | Coef. of Variation: {coefv}")

        self.save(angularity_array, average, standard_dev, coefv)

    def save(self, angularity, aver, std, cvar):
        arr = angularity.copy()
        arr1 = np.append(arr, 1000)
        arr2 = np.append(arr1, aver)
        arr3 = np.append(arr2, std)
        arr4 = np.append(arr3, cvar)

        path = str(self.ePath.get()) + "/angularity_results.txt"
        
        np.savetxt(path, arr4, delimiter=";")

if __name__ == '__main__':
    MainClass()