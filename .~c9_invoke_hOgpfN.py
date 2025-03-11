import boto3
import datetime
import pytest
from unittest.mock import MagicMock
from parser import procesar_archivos

dest_bucket = "casasprueba"
html_test = """
<html>
<body>
    <a class="listing listing-card" data-location="Bogotá, Centro" data-price="$300,000,000" data-floorarea="80 m²">
        <p data-test="bedrooms" content="3"></p>
        <p data-test="bathrooms" content="2"></p>
    </a>
</body>
</html>
"""

@pytest.fixture
def s3_mock():
    with mock_s3():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=dest_bucket)
        yield s3

def decode_chunked(chunked_str: str) -> str:
    """
    Decodifica una cadena en formato chunked encoding y devuelve la concatenación de los chunks.
    """
    lines = chunked_str.split("\r\n")
    chunks = []
    i = 0
    while i < len(lines):
        if not lines[i]:
            i += 1
            continue
        try:
            size = int(lines[i], 16)
        except ValueError:
            i += 1
            continue
        if size == 0:
            break
        if i + 1 < len(lines):
            chunks.append(lines[i + 1])
        i += 2
    return "".join(chunks).strip()

def test_procesar_archivos(s3_mock, mocker):
    """Verifica que procesar_archivos extrae datos y sube el CSV correctamente."""
    
    mocker.patch("parser.s3_client", s3_mock)
    filename = "test_output.csv"
    procesar_archivos(html_test, filename)
    
    response = s3_mock.get_object(Bucket=dest_bucket, Key=filename)
    raw_content = response["Body"].read().decode("utf-8")
    content = decode_chunked(raw_content)
    
    header = "FechaDescarga,Barrio,Valor,NumHabitaciones,NumBanos,mts2"
    fecha_descarga = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    expected_content = f"{header}\n{fecha_descarga},Bogotá, Centro,300000000,3,2,80"
    
    assert content == expected_content, f"El contenido no coincide: {content}"
