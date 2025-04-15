import easyocr
import cv2
from pathlib import Path

def is_number(text):
    return text.replace('.', '', 1).isdigit()

def Detections(image_path, reader):
    img = cv2.imread(str(image_path))
    results = reader.readtext(str(image_path))
    for detection in results:
        box = detection[0]
        text = detection[1]

        top_left = tuple(map(int, box[0]))
        bottom_right = tuple(map(int, box[2]))

        if not is_number(text):
            cv2.rectangle(img, top_left, bottom_right, (255, 255, 255), -1)

    return img

reader = easyocr.Reader(['en'])
input_folder = Path('Input')
output_folder = Path('Output')
output_folder.mkdir(exist_ok=True)

images = sorted([f for f in input_folder.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.png']])
for img_path in images:
    processed_img = Detections(img_path, reader)
    out_path = output_folder / f"{img_path.stem}_out.jpg"
    cv2.imwrite(str(out_path), processed_img)
