import os
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d, distance
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import pickle

# Loading the shp file each time takes a long time
# Loading the pickle object also takes a bit, but it's still faster
if not os.path.exists("shape.pickle"):
    london_bounds = gpd.read_file("./lp-consultation-oct-2009-inner-outer-london-shp/lp-consultation-oct-2009-inner-outer-london.shp")
    with open("shape.pickle", "wb") as file:
        pickle.dump(london_bounds, file)
else:
    with open("shape.pickle", "rb") as file:
        london_bounds = pickle.load(file)

# Convert to lat/long coordinates
london_bounds = london_bounds.to_crs({'proj':'longlat', 'ellps':'WGS84', 'datum':'WGS84'})
london = london_bounds.geometry.iloc[0]

bbox_min = london.bounds[0:2]
bbox_max = london.bounds[2:4]

def is_in_london(p) -> bool:
    return Point(p[0], p[1]).within(london)

points = [(0, 0)]
with open("pret.pickle", "rb") as file:
    points = pickle.load(file)

# Flip order, and convert from string to floats
points = [(float(lat), float(lon)) for (lon, lat) in points]

# Create a grid within the bounding box
m_xx, m_yy = np.meshgrid(np.linspace(bbox_min[0], bbox_max[0], 100), np.linspace(bbox_min[1], bbox_max[1], 100))
m_grid_points = list(filter(is_in_london, np.c_[m_xx.ravel(), m_yy.ravel()]))

# Compute pairwise distances between grid points and input points
m_distances = distance.cdist(m_grid_points, points)

# Find the minimum distance for each grid point
m_min_distances = np.min(m_distances, axis=1)

# Find the index of the grid point that maximizes the minimum distance
m_max_distance_index = np.argmax(m_min_distances)

# Find the coordinates of the point that maximizes the minimum distance
m_max_distance_point = m_grid_points[m_max_distance_index]
m_min_distances = np.min(m_distances, axis=1)

min_distance_to_selected = distance.cdist(points, [m_max_distance_point])
closest_pret = points[np.argmin(min_distance_to_selected)]

print(f"Coordinate of point farthest from all Prets: {m_max_distance_point[1]}N {m_max_distance_point[0]}E")
print(f"Coordinates of the closest Pret to that point: {closest_pret[1]}N {closest_pret[0]}E")

plt.figure(figsize=(10, 5))

# Pret locations
plt.scatter([p[0] for p in points], [p[1] for p in points], c='red', marker='o', s=50, label='Points')

# Farthest point from all Prets
plt.plot(m_max_distance_point[0], m_max_distance_point[1], "go")

# Inner London border
plt.plot(*london.exterior.xy, c="blue")

plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Distance Map')
plt.legend()

plt.show()
