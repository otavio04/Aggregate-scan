import cv2
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import numpy as np

class MainClass(object):

	def __init__(self):

		cor_bg 		= "#ddddee"
		cor_fg		= "#111122"
		cor_obj		= "#eeeeff"
		fonte_txt	= ('calibri', 9)
		fonte_enfas	= ('calibri', 9, "bold")

		self.root = Tk()
		self.root.title('Background remove tool')
		self.root.configure(bg = cor_bg)

		self.name_get = Label(self.root, text = "Escolha uma pasta com imagens", bg = cor_bg)
		self.entry_get = Entry(self.root, width = 100)

		self.name_save = Label(self.root, text = "Escolha uma pasta para salvar as novas imagens", bg = cor_bg)
		self.entry_save = Entry(self.root, width = 100)

		self.button_process = Button(self.root, text = "Processar", width = 20, cursor='hand2', command = self.processar)

		self.name_get.grid(row = 0, column = 0)
		self.entry_get.grid(row = 1, column = 0)
		self.name_save.grid(row = 2, column = 0)
		self.entry_save.grid(row = 3, column = 0)
		self.button_process.grid(row = 4, column = 0)

		self.entry_get.insert(0, "C:/Users/Otavio/Desktop/teste_3D/i")
		self.entry_save.insert(0, "C:/Users/Otavio/Desktop/teste_3D/i_")

		self.root.mainloop()


	def load_images_from_folder(self, folder):
		images = []
		for filename in os.listdir(folder):
			img = cv2.imread(os.path.join(folder, filename))
			if img is not None:
				images.append(img)
		return images

	def resize(self, img):
			width_img = int(img.shape[1])
			height_img = int(img.shape[0])
			p=1.0

			w_r = self.root.winfo_width()
			h_r = self.root.winfo_height()
			h_fAcao = self.fAcao.winfo_reqheight()
			h_fLim = self.fLimiares.winfo_reqheight()

			if width_img >= height_img:
				if(width_img >= w_r/4):
					p = (w_r/4 - 30)/width_img
				else:
					p = 1.0
			else:
				if(height_img >= h_r - (h_fAcao + h_fLim)):
					p = (h_r - (h_fAcao + h_fLim) - 30)/height_img
				else:
					p = 1.0

			width_r = int(img.shape[1]*p)
			height_r = int(img.shape[0]*p)
			dim = (width_r, height_r)
			img_r = cv2.resize(img.copy(), dim)
			return img_r

	def edit_images(self, imgs):

		processed_image = []

		for ifor in imgs:
			#convertendo para o sistema LAB
			i_lab = cv2.cvtColor(ifor, cv2.COLOR_BGR2LAB)
			#inteiro para decimal
			i = (i_lab.astype('float32'))/255
			#pegando o canal L
			i_l = i[:, : ,0]
			#pegando o canal A
			i_a = i[:, : ,1]
			#pegando o canal B
			i_b = i[:, : ,2]
			#decimal para inteiro do B
			i_b_8uc1 = (i_b*255).astype('uint8')
			#limiarização
			ret, i_c_segment = cv2.threshold(i_b_8uc1,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
			#tapando buracos com filtro de mediana
			i_seg_float32 = (i_c_segment.astype('float32'))/255
			i_seg_blur = cv2.medianBlur(i_seg_float32, 5)
			#copiando imagem original
			img_bgr_new = ifor.copy()
			#aplicando mascara
			img_bgr_new[i_seg_blur==1] = (255, 0, 0) #mudar para != para o produto final
			#adicionando ao vetor
			processed_image.append(img_bgr_new)

		return processed_image

	def save_images(self, path_folder, imgs):
		count = 0
		count_erro = 0

		for i in imgs:
			count += 1
			file_name_img = str(count) + '.jpg'
			path_img = path_folder + '/' + file_name_img
			save = cv2.imwrite(path_img, i)
			if not save:
				count_erro += 1

		if count_erro == 0:
			return True
		else:
			return False

	def processar(self):
		path_folder_get = str(self.entry_get.get())
		path_folder_save = str(self.entry_save.get())

		images = self.load_images_from_folder(path_folder_get)
		edited_images = self.edit_images(images)
		saved = self.save_images(path_folder_save, edited_images)

		if saved:
			self.button_process.config(text = "Successfully!")
			print('\a')
		else:
			self.button_process.config(text = "Erro")
			print('\a')


if __name__ == '__main__':
	MainClass()