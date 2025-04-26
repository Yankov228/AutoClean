import logging
from website import create_app, image_processing
from pathlib import Path

app = create_app()

if __name__ == '__main__':
    
    print('\033[31mWait while the images are processed (it may take several minutes depending on the number of images)\033[0m')
    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    input_folder = Path('Input')
    output_folder = Path('website/static/')
    output_folder.mkdir(exist_ok=True)

    language = 'en'

    image_processing(input_folder, output_folder, language)

    print('\033[31mOpen your browser and paste URL http://127.0.0.1:5000/ to the URL bar to start editing your pages\033[0m')

    app.run()