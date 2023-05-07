import open3d as o3d
import numpy as np
from sklearn.decomposition import PCA
import math

example = o3d.io.read_point_cloud('C:/sublime_projetos/Open3D/t_mesh_2.ply')

pts = np.asarray(example.points)

#Finding rotation matrix
pca = PCA(n_components=3)

pca.fit(pts)

r = np.array(pca.components_)
r = np.transpose(r)

#Rotating point cloud
rotation = np.dot(pts, r)

cx = np.average(rotation[:, 0])
cy = np.average(rotation[:, 1])
cz = np.average(rotation[:, 2])
print(cx)
print(cy)
print(cz)

rotation[:, 0] = rotation[:, 0] - cx
rotation[:, 1] = rotation[:, 1] - cy
rotation[:, 2] = rotation[:, 2] - cz

#Finding lenghts of the 3 axis
x = rotation[:, 0]
y = rotation[:, 1]
z = rotation[:, 2]

x_min = np.amin(x)
y_min = np.amin(y)
z_min = np.amin(z)

x_trans = x + x_min*(-1)
y_trans = y + y_min*(-1)
z_trans = z + z_min*(-1)

x_max = np.amax(x_trans)
y_max = np.amax(y_trans)
z_max = np.amax(z_trans)

print('x_max: ', x_max)
print('y_max: ', y_max)
print('z_max: ', z_max)

sphericity = ((z_max*y_max)/(x_max**2))**(1/3)
print("Sphericity: ", round(sphericity, 4))

#Draw perpendicular lines

x_index_max = np.argmax(x_trans)
x_index_min = np.argmin(x_trans)

y_index_max = np.argmax(y_trans)
y_index_min = np.argmin(y_trans)

z_index_max = np.argmax(z_trans)
z_index_min = np.argmin(z_trans)

#points_x = np.array([[rotation[x_index_max][0], rotation[x_index_max][1], rotation[x_index_max][2]], [rotation[x_index_min][0], rotation[x_index_min][1], rotation[x_index_min][2]]])
#points_y = np.array([[rotation[y_index_max][0], rotation[y_index_max][1], rotation[y_index_max][2]], [rotation[y_index_min][0], rotation[y_index_min][1], rotation[y_index_min][2]]])
#points_z = np.array([[rotation[z_index_max][0], rotation[z_index_max][1], rotation[z_index_max][2]], [rotation[z_index_min][0], rotation[z_index_min][1], rotation[z_index_min][2]]])


points_x = np.array([[rotation[x_index_max][0], 0, 0], [rotation[x_index_min][0], 0, 0]])
points_y = np.array([[0, rotation[y_index_max][1], 0], [0, rotation[y_index_min][1], 0]])
points_z = np.array([[0, 0, rotation[z_index_max][2]], [0, 0, rotation[z_index_min][2]]])


#Show objects
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(rotation)

linex = o3d.geometry.LineSet()
linex.points = o3d.utility.Vector3dVector(points_x)
linex.lines = o3d.utility.Vector2iVector([[0, 1]])
linex.colors = o3d.utility.Vector3dVector([[1, 0, 0]])

liney = o3d.geometry.LineSet()
liney.points = o3d.utility.Vector3dVector(points_y)
liney.lines = o3d.utility.Vector2iVector([[0, 1]])
liney.colors = o3d.utility.Vector3dVector([[0, 1, 0]])

linez = o3d.geometry.LineSet()
linez.points = o3d.utility.Vector3dVector(points_z)
linez.lines = o3d.utility.Vector2iVector([[0, 1]])
linez.colors = o3d.utility.Vector3dVector([[0, 0, 1]])

#Draw objects
o3d.visualization.draw([pcd, linex, liney, linez], raw_mode=True)