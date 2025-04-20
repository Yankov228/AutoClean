from website import create_app, image_processing
from pathlib import Path

app = create_app()

if __name__ == '__main__':

    input_folder = Path('Input')
    output_folder = Path('website/static/')
    output_folder.mkdir(exist_ok=True)

    image_processing(input_folder, output_folder)

    app.run(debug=True)