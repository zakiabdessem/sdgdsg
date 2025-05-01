import requests
from lxml import etree
from flask import Response, abort
from db import insert_into_history
import os
from io import BytesIO
from PIL import Image

def fetch_and_process_file(url):
    try:
        response = requests.get(url, timeout=(5, 5))
        if response.status_code != 200:
            abort(400, f'Failed to fetch the file from the URL. Status code: {response.status_code}')

        content_type = response.headers.get('Content-Type')

        supported_mime_types = ['image/png', 'image/jpeg', 'image/svg+xml']

        if content_type not in supported_mime_types:
            abort(400, 'Unsupported file format.')

        filename = os.path.basename(url)
        insert_into_history(filename, content_type)

        if content_type in ['image/png', 'image/jpeg']:
            try:
                image = Image.open(BytesIO(response.content))
                image.verify()
            except Exception as e:
                abort(400, f'The fetched content is not a valid image: {str(e)}')

        if content_type == 'image/svg+xml':
            image_content = response.text

            try:
                parser = etree.XMLParser(no_network=False)
                doc = etree.fromstring(image_content.encode('utf-8'), parser)

                if doc.tag != '{http://www.w3.org/2000/svg}svg':
                    abort(400, "There was an error in the SVG content")

                image_data = etree.tostring(doc, pretty_print=True).decode('utf-8')
                if 'file:' in image_content:
                    abort(400, "There was an error in the SVG content")

                return Response(image_data, content_type='image/svg+xml')

            except Exception as e:
                abort(400, f'There was an error in the SVG content')

        return Response(response.content, content_type=content_type)

    except requests.exceptions.RequestException as e:
        abort(400, f'Error fetching the file')
