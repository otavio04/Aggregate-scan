import cv2
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import numpy as np
from PIL import ImageTk, Image
import sys

class MainClass(object):

	p = 1.0
	x1 = 0
	y1 = 0
	x2 = 0
	y2 = 0

	def __init__(self):

		cor_bg 		= "#ddddee"
		cor_fg		= "#111122"
		cor_obj		= "#eeeeff"
		fonte_txt	= ('calibri', 9)
		fonte_enfas	= ('calibri', 9, "bold")

		self.path_folder_get = ""
		self.path_folder_save = ""

		self.imgs = []
		self.cropped_imgs = []
		self.edited_imgs = []

		self.root = Tk()
		self.root.title('Background remove tool')
		self.root.configure(bg = cor_bg)

		self.fCanvas = LabelFrame(self.root, text="First Image of Chosen Folder", bg = cor_bg)
		self.fCommands = LabelFrame(self.root, text="Commands", bg = cor_bg)

		self.canvas = Canvas(self.fCanvas, width = 600, height = 400, bg = cor_fg)

		self.name_get = Label(self.fCommands, text = "Escolha uma pasta com imagens", bg = cor_bg)
		self.entry_get = Entry(self.fCommands, width = 120)

		self.name_save = Label(self.fCommands, text = "Escolha uma pasta para salvar as novas imagens", bg = cor_bg)
		self.entry_save = Entry(self.fCommands, width = 120)

		self.button_load = Button(self.fCommands, text = "Load Photos", width = 20, cursor='hand2', command = self.load)
		self.button_process = Button(self.fCommands, text = "Process", width = 20, cursor='hand2', command = self.processar)
		self.button_save = Button(self.fCommands, text = "Save", width = 20, cursor='hand2', command = self.save)
		self.button_reset = Button(self.fCommands, text = "Reset", fg="red", width = 20, cursor='hand2', command = self.reset)

		self.fCanvas.grid(row = 0, column = 0, sticky="N")
		self.fCommands.grid(row = 0, column = 1, sticky="N")

		self.canvas.pack()

		self.name_get.grid(row = 0, column = 0, pady=5, columnspan=5, sticky="W")
		self.entry_get.grid(row = 1, column = 0, pady=5, columnspan=5)
		self.name_save.grid(row = 2, column = 0, pady=5, columnspan=5, sticky="W")
		self.entry_save.grid(row = 3, column = 0, pady=5, columnspan=5)
		self.button_load.grid(row = 4, column = 0, padx=5, pady=5)
		self.button_process.grid(row = 4, column = 1, padx=5, pady=5)
		self.button_save.grid(row = 4, column = 2, padx=5, pady=5)
		self.button_reset.grid(row = 4, column = 3, padx=5, pady=5)

		self.canvas.bind("<Button-1>", self.plot_point)  # Bind the left button click event to the plot_point function
		self.canvas.bind("<Button-3>", self.plot_point2)  # Bind the left button click event to the plot_point function

		self.entry_get.insert(0, "C:/Users/Otavio/Pictures/z")
		self.entry_save.insert(0, "C:/Users/Otavio/Pictures/z_")

		self.button_load.config(state="normal")
		self.button_process.config(state="disabled")
		self.button_save.config(state="disabled")
		self.button_reset.config(state="normal")

		self.root.mainloop()


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
			img_bgr_new[i_seg_blur!=1] = (255, 0, 0) #mudar para != para o produto final
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


	def load(self):

		self.button_load.config(state="normal")
		self.button_process.config(state="disabled")
		self.button_save.config(state="disabled")
		self.button_reset.config(state="normal")

		self.path_folder_get = str(self.entry_get.get())
		self.imgs = self.load_images_from_folder(self.path_folder_get)

		img_copy = self.resize(self.imgs[0].copy())

		image_pil = Image.fromarray(cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB))
			
		photo = ImageTk.PhotoImage(image_pil)
		self.canvas.photo = photo
		self.canvas.create_image(0, 0, anchor="nw", image=photo, tag='img')
		
	def processar(self):

		self.button_load.config(state="disabled")
		self.button_process.config(state="disabled")
		self.button_save.config(state="normal")
		self.button_reset.config(state="normal")

		global x1, y1, x2, y2, p
		i_x1 = int(x1*(1/p))
		i_y1 = int(y1*(1/p))
		i_x2 = int(x2*(1/p))
		i_y2 = int(y2*(1/p))

		for i in range(len(self.imgs)):
			img = self.imgs[i]
			self.cropped_imgs.append(img[i_y1:i_y2, i_x1:i_x2])

		self.edited_imgs = self.edit_images(self.cropped_imgs)
		
		img_copy = self.resize(self.edited_imgs[0].copy())

		image_pil = Image.fromarray(cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB))
			
		photo = ImageTk.PhotoImage(image_pil)
		self.canvas.delete('all')
		self.canvas.photo = photo
		self.canvas.create_image(0, 0, anchor="nw", image=photo, tag='img')
	
	def save(self):

		self.button_load.config(state="disabled")
		self.button_process.config(state="disabled")
		self.button_save.config(state="disabled")
		self.button_reset.config(state="normal")

		self.path_folder_save = str(self.entry_save.get())

		saved = self.save_images(self.path_folder_save, self.edited_imgs)

		if saved:
			self.button_save.config(text = "Successfully!")
			print('\a')
		else:
			self.button_save.config(text = "Erro")
			print('\a')

	def reset(self):
		os.execl(sys.executable, sys.executable, *sys.argv)


	def plot_lines(self):

		self.button_process.config(state="normal")

		self.canvas.delete('lines')
		self.canvas.create_line(x1, y1, x2, y1, fill = 'red', tag='lines')
		self.canvas.create_line(x1, y1, x1, y2, fill = 'red', tag='lines')
		self.canvas.create_line(x1, y2, x2, y2, fill = 'red', tag='lines')
		self.canvas.create_line(x2, y1, x2, y2, fill = 'red', tag='lines')

	def plot_point(self, event):
		global x1, y1
		x1 = event.x
		y1 = event.y
		self.canvas.delete('left')
		self.canvas.create_oval(x1 - 3, y1 - 3, x1 + 3, y1 + 3, fill='yellow', tag='left')  # Plot a small oval at the clicked coordinates
		if(self.canvas.find_withtag('right')):
			self.plot_lines()

	def plot_point2(self, event):
		global x2, y2
		x2 = event.x
		y2 = event.y
		self.canvas.delete('right')
		self.canvas.create_oval(x2 - 3, y2 - 3, x2 + 3, y2 + 3, fill='yellow', tag='right')  # Plot a small oval at the clicked coordinates
		if(self.canvas.find_withtag('left')):
			self.plot_lines()


if __name__ == '__main__':
	MainClass()