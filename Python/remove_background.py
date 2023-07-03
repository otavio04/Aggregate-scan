import cv2
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
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

		self.imgs = []
		self.cropped_imgs = []
		self.blue_images = []
		self.green_images = []
		self.png_images = []

		self.condition = [0, 0]

		self.root = Tk()
		self.root.title('Background remove tool')
		self.root.configure(bg = cor_bg)

		self.check_green_var =IntVar()
		self.check_png_var =IntVar()

		self.fCanvas = LabelFrame(self.root, text="First Image of Chosen Folder", bg = cor_bg)
		self.fCommands = LabelFrame(self.root, text="Commands", bg = cor_bg)
		self.fCheckboxs = LabelFrame(self.fCommands, text="Processing choices", bg = cor_bg)

		self.canvas = Canvas(self.fCanvas, width = 600, height = 400, bg = cor_fg, cursor='crosshair')

		self.name_get = Label(self.fCommands, text = "Choose a folder with images", bg = cor_bg)
		self.entry_get = Entry(self.fCommands, width = 120)

		self.CBGreenimg = Checkbutton(self.fCheckboxs, bg = cor_bg, text="Green segmentation", cursor='hand2', variable=self.check_green_var, onvalue=1, offvalue=0)
		self.CBPngimg = Checkbutton(self.fCheckboxs, bg = cor_bg, text="PNG image", cursor='hand2', variable=self.check_png_var, onvalue=1, offvalue=0)

		self.button_load = Button(self.fCommands, text = "Load Photos", width = 20, cursor='hand2', command = self.load)
		self.button_process = Button(self.fCommands, text = "Process", width = 20, cursor='hand2', command = self.process)
		self.button_save = Button(self.fCommands, text = "Save", width = 20, cursor='hand2', command = self.save)
		self.button_reset = Button(self.fCommands, text = "Reset", fg="red", width = 20, cursor='hand2', command = self.reset)

		self.fCanvas.grid(row = 0, column = 0, sticky="N")
		self.fCommands.grid(row = 0, column = 1, sticky="N")

		self.canvas.pack()

		self.name_get.grid(row = 0, column = 0, pady=5, columnspan=5, sticky="W")
		self.entry_get.grid(row = 1, column = 0, pady=5, columnspan=5)
		self.fCheckboxs.grid(row = 2, column = 0, pady=5, columnspan=5, sticky="W")
		self.button_load.grid(row = 3, column = 0, padx=5, pady=5)
		self.button_process.grid(row = 3, column = 1, padx=5, pady=5)
		self.button_save.grid(row = 3, column = 2, padx=5, pady=5)
		self.button_reset.grid(row = 3, column = 3, padx=5, pady=5)

		self.CBGreenimg.grid(row = 0, column = 0)
		self.CBPngimg.grid(row = 0, column = 1)

		self.canvas.bind("<Button-1>", self.plot_point)  # Bind the left button click event to the plot_point function
		self.canvas.bind("<Button-3>", self.plot_point2)  # Bind the left button click event to the plot_point function

		self.entry_get.insert(0, "C:/Users")

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

	def process_imgs(self, imgs, conditions_img):

		processed_image_b = []
		processed_image_g = []
		processed_image_p = []

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
			img_bgr_new_b = ifor.copy()
			#aplicando mascara
			img_bgr_new_b[i_seg_blur!=1] = (255, 0, 0) #mudar para != para o produto final
			#adicionando ao vetor
			processed_image_b.append(img_bgr_new_b)
			i_for_png = i_seg_blur.copy()

			if conditions_img[0] == 1:
				#decimal para inteiro do A
				i_a_8uc1 = (i_a*255).astype('uint8')
				#limiarização
				reta, i_c_segment_a = cv2.threshold(i_a_8uc1,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
				#tapando buracos com filtro de mediana
				i_seg_float32_a = (i_c_segment_a.astype('float32'))/255
				i_seg_blur_a = cv2.medianBlur(i_seg_float32_a, 5)
				#copiando imagem original
				img_bgr_new_g = img_bgr_new_b.copy()
				#aplicando mascara
				img_bgr_new_g[i_seg_blur_a!=1] = (255, 0, 0) #mudar para != para o produto final
				#adicionando ao vetor
				processed_image_g.append(img_bgr_new_g)
				i_for_png = i_seg_blur_a.copy()

			if conditions_img[1] == 1:
				#criando imagem png
				bgra_image = np.zeros((ifor.shape[0], ifor.shape[1], 4), np.uint8)
				#aplicando mascara
				ifor_with_alpha = cv2.cvtColor(ifor.copy(), cv2.COLOR_BGR2BGRA)
				indices_true = np.where(i_for_png==1)
				bgra_image[indices_true] = ifor_with_alpha[indices_true]
				bgra_image[i_for_png!=1] = (255, 0, 0, 0)
				bgra_image[i_seg_blur!=1] = (255, 0, 0, 0)
				#adicionando ao vetor
				processed_image_p.append(bgra_image)


		self.blue_images = processed_image_b
		self.green_images = processed_image_g
		self.png_images = processed_image_p

	def save_images(self, path_folder, imgs, condition_png):
		count = 0
		count_erro = 0

		for i in imgs:
			count += 1
			if condition_png == 0:
				file_name_img = str(count) + '.jpg'
			else:
				file_name_img = str(count) + '.png'
				
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
		
	def process(self):

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


		if self.check_green_var.get() == 1:
			self.condition[0] = 1
		
		if self.check_png_var.get() == 1:
			if self.check_green_var.get() == 1:
				self.condition[0] = 1
				self.condition[1] = 1
			else:
				self.condition[1] = 1


		self.process_imgs(self.cropped_imgs, self.condition)
		

		img_copy = self.resize(self.blue_images[0].copy())

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

		blue_folder = self.path_folder_get + "/blue"
		green_folder = self.path_folder_get + "/green"
		png_folder = self.path_folder_get + "/png"

		if not os.path.exists(blue_folder):
			os.mkdir(blue_folder)

		saved = False

		if self.condition[0] == 1 and self.condition[1] == 1:						#all 3 images will be saved
			if not os.path.exists(blue_folder):
				os.mkdir(blue_folder)
			if not os.path.exists(green_folder):
				os.mkdir(green_folder)
			if not os.path.exists(png_folder):
				os.mkdir(png_folder)

			sblue = self.save_images(blue_folder, self.blue_images, 0)
			sgreen = self.save_images(green_folder, self.green_images, 0)
			spng = self.save_images(png_folder, self.png_images, 1)
			if not sblue or not sgreen or not spng:
				saved = False
			else:
				saved = True

		elif self.condition[0] == 1 and self.condition[1] == 0:						#only blue and green images will be saved
			if not os.path.exists(blue_folder):
				os.mkdir(blue_folder)
			if not os.path.exists(green_folder):
				os.mkdir(green_folder)

			sblue = self.save_images(blue_folder, self.blue_images, 0)
			sgreen = self.save_images(green_folder, self.green_images, 0)
			
			if not sblue or not sgreen:
				saved = False
			else:
				saved = True

		elif self.condition[0] == 0 and self.condition[1] == 1:						#only blue and png images will be saved
			if not os.path.exists(blue_folder):
				os.mkdir(blue_folder)
			if not os.path.exists(png_folder):
				os.mkdir(png_folder)

			sblue = self.save_images(blue_folder, self.blue_images, 0)
			spng = self.save_images(png_folder, self.png_images, 1)

			if not sblue or not spng:
				saved = False
			else:
				saved = True

		elif self.condition[0] == 0 and self.condition[1] == 0:						#only blue images will be saved
			if not os.path.exists(blue_folder):
				os.mkdir(blue_folder)

			sblue = self.save_images(blue_folder, self.blue_images, 0)
			
			if not sblue:
				saved = False
			else:
				saved = True

		if saved:
			messagebox.showinfo(title="Info", message="All the images was successfully saved.")
		else:
			messagebox.showerror(title="Failed to save images", message="The images were not saved correctly.")

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