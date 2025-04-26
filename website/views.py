from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from . import pictures, image_altering
import cv2 
from pathlib import Path

views = Blueprint('views', __name__)

saved_data = False
pages = []

@views.route('/', methods=['GET', 'POST'])
def home():
    global saved_data, pages

    if not saved_data:
        sorted_paths = sorted(pictures.keys())
        pages = []

        for i, path in enumerate(sorted_paths, start=1):
            pages.append({
                'page_number': i,
                'path': path,
                'clusters': pictures[path]['clusters'],
                'boxes': pictures[path]['boxes'],
                'source': pictures[path]['source']
            })

        saved_data = True

    return render_template("home.html", pages=pages)
# Returns user to home page if they refresh site
@views.route('/page/<int:page_id>')
def page(page_id):
    return redirect(url_for('views.home'))
# Erases "cluster" from "pages" and from image
@views.route('/erase_cluster', methods=['POST'])
def erase_cluster():
    global pages

    data = request.get_json()
    page_number = data.get('page_number')
    cluster_index = data.get('cluster_index')

    for page in pages:
        if page.get('page_number') == page_number:

            if 0 <= cluster_index < len(page['clusters']):
                del page['clusters'][cluster_index]

                source_img_path = Path(f"website/static/{page['source']}")
                out_img_path = Path(f"website/static/{page['path']}")

                img = cv2.imread(source_img_path)
                updated_img, _, _ = image_altering(img, page['clusters'], page['boxes'], with_numbering=True)

                cv2.imwrite(out_img_path, updated_img)

                return jsonify({
                    'status': 'success',
                    'clusters': page['clusters'],
                    'path': page['path']
                })

    return jsonify({'status': 'error'})
# Saves images to "Output" folder
@views.route('/submit_changes', methods=['POST'])
def submit_changes():

    for page in pages:

        img_path = Path(f"website/static/{page['source']}")
        output_path = Path(f'Output/{page['path']}')

        img = cv2.imread(img_path)

        altered_image, _, _ = image_altering(img, page['clusters'], page['boxes'], with_numbering=False)

        cv2.imwrite(output_path, altered_image)

    return jsonify({
        'status': 'success'
    })
# Clears /static folder from all .jpg files
@views.route('/clearing_static', methods=['DELETE'])
def clearing_static():
    from pathlib import Path

    folder = Path('website/static')

    for file in folder.glob('*.jpg'):
        file.unlink()
        
    return jsonify({
        'status': 'success'
    })
