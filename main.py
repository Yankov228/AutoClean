import easyocr
import cv2
from matplotlib import pyplot as plt
import numpy as np

IMAGE_PATH = ''
reader = easyocr.Reader(['en'])
result = reader.readtext(IMAGE_PATH)
print(result)