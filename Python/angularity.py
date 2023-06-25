import open3d as o3d
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import random
import math
from scipy.spatial import ConvexHull

#Getting data
def getting_data():
    example = o3d.io.read_point_cloud('C:/sublime_projetos/Open3D/t_mesh_2.ply')
    pts = np.asarray(example.points)

    return pts

#Finding rotation matrix
def finding_rotation_matrix(pts):
    pca = PCA(n_components=3) #3 axis
    pca.fit(pts)

    r = np.array(pca.components_)
    r = np.transpose(r)

    return r

#Rotating point cloud and finding center
def rotating_points(pts, r):
    rotation = np.dot(pts, r)

    cx = np.average(rotation[:, 0])
    cy = np.average(rotation[:, 1])
    cz = np.average(rotation[:, 2])

    rotation[:, 0] = rotation[:, 0] - cx
    rotation[:, 1] = rotation[:, 1] - cy
    rotation[:, 2] = rotation[:, 2] - cz

    #Getting point cloud
    x = rotation[:, 0]
    y = rotation[:, 1]
    z = rotation[:, 2]

    return x, y, z

#Sorting point cloud by X-axis (major axis)
def sorting_point_cloud(x, y, z):
    x = x + abs(np.amin(x))
    sorted_indices = np.argsort(x)
    new_x = np.take(x, sorted_indices)
    new_y = np.take(y, sorted_indices)
    new_z = np.take(z, sorted_indices)

    return new_x, new_y, new_z

#Choosing number of partitions and starting the color array
def color_array(p, new_x):
    step = float(np.amax(new_x)/p)
    color_to_paint = np.ones(shape=(p, 3))
    colors = np.ones(shape=(len(new_x), 3))

    #Creating a random color arrays for the partitions
    for i in range(partitions):
        r = random.randint(0, 255)/256.00
        g = random.randint(0, 255)/256.00
        b = random.randint(0, 255)/256.00
        color_to_paint[i] = (r, g, b)

    #Creating one array of colors
    the_turn = 1

    for i in range(len(new_x)):
        if new_x[i] <= step * the_turn:
            colors[i] = color_to_paint[the_turn-1]
        else:
            the_turn += 1
   
    return colors
            
#sorting out main array
def main_array_sorted(new_x, new_y, new_z, p):
    l = []
    step_int = int(len(new_x)/p)

    for i in range(p):
        if i == p-1:
            l.append(np.dstack((new_y[i*step_int:], new_z[i*step_int:])))
        else:
            l.append(np.dstack((new_y[i*step_int:(i+1)*step_int], new_z[i*step_int:(i+1)*step_int])))

    return l

def convexH(separated_arrays):
    hull_list = []
    for i in separated_arrays:
        hull = ConvexHull(i)
        # hull_vertices = i[hull.vertices]
        # hull_list.append(hull_vertices)
        print(i)
        print("=============================")

    # print(separated_arrays[0])
    
    return hull_list

#Rows and columns to plot in 2D
def calculate_rows_columns(num_caixas):
    lado = int(math.sqrt(num_caixas))  # Encontra a raiz quadrada do número de caixas e arredonda para baixo

    while num_caixas % lado != 0:
        lado -= 1  # Diminui o valor do lado até que seja um divisor exato do número de caixas

    colunas = lado
    linhas = num_caixas // colunas

    return linhas, colunas

#plotting images
def plot_(new_x, new_y, new_z, p, separated_arrays, colors, rows, columns):
    #Create a 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(new_x, new_y, new_z, c=colors)

    #Customize the plot
    ax.set_title(f"Particle with {p} slices")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_zlabel("Z-axis")
    # ax.set_xlim3d([-1, 1])
    # ax.set_ylim3d([-1, 1])
    # ax.set_zlim3d([-1, 1])


    #2D image
    fig2 = plt.figure()
    for i in range(p):
        ax2 = fig2.add_subplot(rows, columns, i+1)
        ax2.scatter(separated_arrays[i][0, :][:, 0], separated_arrays[i][0, :][:, 1])
        ax2.set_title(f"Slice {i+1}")
        ax2.set_xlabel("Y-axis")
        ax2.set_ylabel("Z-axis")
        # ax2.set_xlim([-2, 2])
        # ax2.set_ylim([-2, 2])
        ax2.set_aspect('equal')

    #Display the plot
    plt.show()

pts = getting_data()
r = finding_rotation_matrix(pts)
x, y, z = rotating_points(pts, r)
new_x, new_y, new_z = sorting_point_cloud(x, y, z)
partitions = 10
colors = color_array(partitions, new_x)
separated_arrays = main_array_sorted(new_x, new_y, new_z, partitions)
columns, rows = calculate_rows_columns(partitions)
# convex_hull = convexH(separated_arrays)
plot_(new_x, new_y, new_z, partitions, separated_arrays, colors, rows, columns)