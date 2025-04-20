from flask import Flask
import cv2
import numpy as np
from shapely.geometry import Polygon
import easyocr
from pathlib import Path

pictures = {}

reader = easyocr.Reader(['en'])

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'FDKLJSJLFDKSA'
    
    from .views import views

    app.register_blueprint(views, url_prefix='/')
    
    return app

def image_processing(input_folder, output_folder):
    
    images = sorted([f for f in input_folder.iterdir() if f.is_file() and f.suffix in ['.jpg', '.png']])

    for img_path in images:
        processed_img, clusters, boxes = text_recognition(str(img_path), reader)

        out_path_for_cv2 = output_folder / f"{img_path.stem}.jpg"
        out_path_for_html = Path('') / f"{img_path.stem}.jpg"
        
        pictures[str(out_path_for_html)] = {
            'clusters': clusters,
            'boxes': boxes
        }
        cv2.imwrite(str(out_path_for_cv2), processed_img)

def cluster_detection(polygons, boxes, img):
    n = len(polygons)

    adjacency = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if polygons[i].intersects(polygons[j]):
                adjacency[i].append(j)
                adjacency[j].append(i)

    visited = [False] * n
    clusters = []

    def dfs(node, cluster):
        visited[node] = True
        cluster.append(node)
        for neighbor in adjacency[node]:
            if not visited[neighbor]:
                dfs(neighbor, cluster)

    for i in range(n):
        if not visited[i]:
            cluster = []
            dfs(i, cluster)
            if len(cluster) > 1:
                clusters.append(cluster)

    for cluster in clusters:
        for idx in cluster:
            pts = np.array(boxes[idx]).astype(int)
            cv2.fillPoly(img, [pts], (255, 255, 255))

    return img, clusters, boxes

def text_recognition(image_path, reader):
    
    result = reader.readtext(image_path)

    img = cv2.imread(image_path)

    boxes = []
    polygons = []

    for detection in result:
        text = detection[1]
        
        if text.replace('.', '', 1).isdigit():
            continue

        box = detection[0]
        points = [tuple(map(int, pt)) for pt in box]
        poly = Polygon(points).buffer(2)

        boxes.append(points)
        polygons.append(poly)

    return cluster_detection(polygons, boxes, img)