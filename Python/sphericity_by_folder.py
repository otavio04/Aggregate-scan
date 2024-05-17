import os
import numpy as np
import pandas as pd
import open3d as o3d
from sklearn.decomposition import PCA

def list_files(folder_):
    directories = []
    names = []
    for file_ in os.listdir(folder_):
        if file_.lower().endswith(('.ply')):
            p = os.path.join(folder_, file_)
            directories.append(p)

            name = os.path.basename(p).split('.')[0]
            names.append(name)

    
    return directories, names

folder_setted = "C:/imgs_test_aggegate_scan/ensaio_de_forma-sem_escala/PLY_files"

files_, names_ = list_files(folder_setted)

x_ = []
y_ = []
z_ = []

for i, file__ in enumerate(files_):
    cloud_of_points = o3d.io.read_point_cloud(file__)
    pts = np.asarray(cloud_of_points.points)

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

    x_.append(x_max)
    y_.append(y_max)
    z_.append(z_max)

    # sphericity = ((z_max*y_max)/(x_max**2))**(1/3)

data_frame = {
    'Arquivo'   : names_,
    'x Axis'    : x_,
    'y Axis'    : y_,
    'z Axis'    : z_
}

df = pd.DataFrame(data_frame)
df.to_csv(str(folder_setted + "/data_frame.csv"), sep=';', index=False)
