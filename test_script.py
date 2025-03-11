import pytest
from unittest.mock import patch, MagicMock
from parcial import download_and_upload  # Asegúrate de importar tu código correctamente

@patch("parcial.requests.get")  # Simula requests.get()
def test_descarga_exitosa(mock_get):
    """ Prueba si la función maneja correctamente una descarga exitosa. """

    # Configurar el mock para simular una respuesta exitosa con HTML falso
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Casas en Bogotá</body></html>"
    mock_get.return_value = mock_response

    download_and_upload()  # Llamamos a la función principal

    # Verificamos que `requests.get()` se llamó 10 veces (una por cada página)
    assert mock_get.call_count == 10

@patch("parcial.s3_client.put_object")  # Simula boto3 S3 put_object
@patch("parcial.requests.get")  # Simula requests.get()
def test_subida_a_s3(mock_get, mock_put_object):
    """ Prueba si los archivos se suben correctamente a S3. """

    # Simular una respuesta exitosa de la página
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Contenido de prueba</body></html>"
    mock_get.return_value = mock_response

    # Simular la subida exitosa a S3
    mock_put_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

    download_and_upload()  # Ejecutamos la función

    # Verificar que `put_object` se llamó 10 veces (una por cada página descargada)
    assert mock_put_object.call_count == 10


@patch("parcial.requests.get")
def test_error_en_descarga(mock_get):
    """ Prueba si la función maneja correctamente un error al descargar. """

    # Simular un error 404 en la respuesta
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    download_and_upload()  # Llamamos la función

    # Verificar que `requests.get()` se llamó 10 veces a pesar del error
    assert mock_get.call_count == 10
