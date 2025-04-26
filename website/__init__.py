from flask import Flask
import cv2
import numpy as np
from shapely.geometry import Polygon
import easyocr
from pathlib import Path

pictures = {}


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'FDKLJSJLFDKSA'
    
    from .views import views

    app.register_blueprint(views, url_prefix='/')
    
    return app

def image_processing(input_folder, output_folder, lang):

    if lang:
        reader = easyocr.Reader([str(lang)], gpu=True)
    else:
        reader = easyocr.Reader(['en'], gpu=True)
        
    images = sorted([f for f in input_folder.iterdir() if f.is_file() and f.suffix in ['.jpg', '.png']])

    for img_path in images:
        processed_img, clusters, boxes, copy_path = text_recognition(str(img_path), reader)

        out_path_for_cv2 = output_folder / f"{img_path.stem}.jpg"
        out_path_for_html = Path('') / f"{img_path.stem}.jpg"
        
        pictures[str(out_path_for_html)] = {
            'clusters': clusters,
            'boxes': boxes,
            'source': str(copy_path.name)
        }
        cv2.imwrite(str(out_path_for_cv2), processed_img)

def image_altering(img, clusters, boxes, with_numbering):
    for cluster_index, cluster in enumerate(clusters):
        for idx in cluster:
            pts = np.array(boxes[idx]).astype(int)
            cv2.fillPoly(img, [pts], (255, 255, 255))

            if with_numbering:
                all_points = [pt for idx in cluster for pt in boxes[idx]]
                center_x = int(np.mean([pt[0] for pt in all_points]))
                center_y = int(np.mean([pt[1] for pt in all_points]))

                cv2.putText(
                    img,
                    f"{cluster_index + 1}",
                    (center_x - 30, center_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA
                )
    return img, clusters, boxes

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

    return image_altering(img, clusters, boxes, with_numbering=True)

def text_recognition(image_path, reader):

    result = reader.readtext(image_path)

    img = cv2.imread(image_path)

    copyFolder = Path('website/static/')
    copyFolder.mkdir(parents=True, exist_ok=True)

    original_name = Path(image_path).stem
    copy_path = copyFolder / f"{original_name}_source.jpg"

    cv2.imwrite(str(copy_path), img)

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

    processed_img, clusters, boxes = cluster_detection(polygons, boxes, img)
    return processed_img, clusters, boxes, copy_path