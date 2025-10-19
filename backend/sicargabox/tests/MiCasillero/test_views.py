import pytest
import test_helpers

from django.urls import reverse


pytestmark = [pytest.mark.django_db]


def tests_Alerta_list_view(client):
    instance1 = test_helpers.create_MiCasillero_Alerta()
    instance2 = test_helpers.create_MiCasillero_Alerta()
    url = reverse("MiCasillero_Alerta_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Alerta_create_view(client):
    url = reverse("MiCasillero_Alerta_create")
    data = {
        "tipo_alerta": "text",
        "mensaje": "text",
        "fecha_envio": datetime.now(),
        "estado": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Alerta_detail_view(client):
    instance = test_helpers.create_MiCasillero_Alerta()
    url = reverse("MiCasillero_Alerta_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Alerta_update_view(client):
    instance = test_helpers.create_MiCasillero_Alerta()
    url = reverse("MiCasillero_Alerta_update", args=[instance.pk, ])
    data = {
        "tipo_alerta": "text",
        "mensaje": "text",
        "fecha_envio": datetime.now(),
        "estado": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Articulo_list_view(client):
    instance1 = test_helpers.create_MiCasillero_Articulo()
    instance2 = test_helpers.create_MiCasillero_Articulo()
    url = reverse("MiCasillero_Articulo_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Articulo_create_view(client):
    url = reverse("MiCasillero_Articulo_create")
    data = {
        "valor_articulo": 1.0,
        "largo": 1.0,
        "ancho": 1.0,
        "alto": 1.0,
        "peso": 1.0,
        "impuesto_dai": 1.0,
        "impuesto_isc": 1.0,
        "impuesto_ispc": 1.0,
        "impuesto_isv": 1.0,
        "impuesto_total": 1.0,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Articulo_detail_view(client):
    instance = test_helpers.create_MiCasillero_Articulo()
    url = reverse("MiCasillero_Articulo_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Articulo_update_view(client):
    instance = test_helpers.create_MiCasillero_Articulo()
    url = reverse("MiCasillero_Articulo_update", args=[instance.pk, ])
    data = {
        "valor_articulo": 1.0,
        "largo": 1.0,
        "ancho": 1.0,
        "alto": 1.0,
        "peso": 1.0,
        "impuesto_dai": 1.0,
        "impuesto_isc": 1.0,
        "impuesto_ispc": 1.0,
        "impuesto_isv": 1.0,
        "impuesto_total": 1.0,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Cliente_list_view(client):
    instance1 = test_helpers.create_MiCasillero_Cliente()
    instance2 = test_helpers.create_MiCasillero_Cliente()
    url = reverse("MiCasillero_Cliente_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Cliente_create_view(client):
    url = reverse("MiCasillero_Cliente_create")
    data = {
        "nombres": "text",
        "apellidos": "text",
        "direccion": "text",
        "telefono": "text",
        "correo_electronico": "user@tempurl.com",
        "codigo_cliente": "text",
        "fecha_registro": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Cliente_detail_view(client):
    instance = test_helpers.create_MiCasillero_Cliente()
    url = reverse("MiCasillero_Cliente_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Cliente_update_view(client):
    instance = test_helpers.create_MiCasillero_Cliente()
    url = reverse("MiCasillero_Cliente_update", args=[instance.pk, ])
    data = {
        "nombres": "text",
        "apellidos": "text",
        "direccion": "text",
        "telefono": "text",
        "correo_electronico": "user@tempurl.com",
        "codigo_cliente": "text",
        "fecha_registro": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Cotizacion_list_view(client):
    instance1 = test_helpers.create_MiCasillero_Cotizacion()
    instance2 = test_helpers.create_MiCasillero_Cotizacion()
    url = reverse("MiCasillero_Cotizacion_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Cotizacion_create_view(client):
    url = reverse("MiCasillero_Cotizacion_create")
    data = {
        "fecha_creacion": datetime.now(),
        "estado": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Cotizacion_detail_view(client):
    instance = test_helpers.create_MiCasillero_Cotizacion()
    url = reverse("MiCasillero_Cotizacion_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Cotizacion_update_view(client):
    instance = test_helpers.create_MiCasillero_Cotizacion()
    url = reverse("MiCasillero_Cotizacion_update", args=[instance.pk, ])
    data = {
        "fecha_creacion": datetime.now(),
        "estado": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Envio_list_view(client):
    instance1 = test_helpers.create_MiCasillero_Envio()
    instance2 = test_helpers.create_MiCasillero_Envio()
    url = reverse("MiCasillero_Envio_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Envio_create_view(client):
    url = reverse("MiCasillero_Envio_create")
    data = {
        "tracking_number_original": "text",
        "tracking_number_final": "text",
        "direccion_casillero": "text",
        "estado_envio": "text",
        "flete": 1.0,
        "fecha_actualizacion": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Envio_detail_view(client):
    instance = test_helpers.create_MiCasillero_Envio()
    url = reverse("MiCasillero_Envio_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Envio_update_view(client):
    instance = test_helpers.create_MiCasillero_Envio()
    url = reverse("MiCasillero_Envio_update", args=[instance.pk, ])
    data = {
        "tracking_number_original": "text",
        "tracking_number_final": "text",
        "direccion_casillero": "text",
        "estado_envio": "text",
        "flete": 1.0,
        "fecha_actualizacion": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Factura_list_view(client):
    instance1 = test_helpers.create_MiCasillero_Factura()
    instance2 = test_helpers.create_MiCasillero_Factura()
    url = reverse("MiCasillero_Factura_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Factura_create_view(client):
    url = reverse("MiCasillero_Factura_create")
    data = {
        "flete": 1.0,
        "total_impuesto_dai": 1.0,
        "total_impuesto_isc": 1.0,
        "total_impuesto_ispc": 1.0,
        "total_impuesto_isv": 1.0,
        "total_impuesto": 1.0,
        "monto_total": 1.0,
        "fecha_emision": datetime.now(),
        "estado_pago": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Factura_detail_view(client):
    instance = test_helpers.create_MiCasillero_Factura()
    url = reverse("MiCasillero_Factura_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Factura_update_view(client):
    instance = test_helpers.create_MiCasillero_Factura()
    url = reverse("MiCasillero_Factura_update", args=[instance.pk, ])
    data = {
        "flete": 1.0,
        "total_impuesto_dai": 1.0,
        "total_impuesto_isc": 1.0,
        "total_impuesto_ispc": 1.0,
        "total_impuesto_isv": 1.0,
        "total_impuesto": 1.0,
        "monto_total": 1.0,
        "fecha_emision": datetime.now(),
        "estado_pago": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_ParametroSistema_list_view(client):
    instance1 = test_helpers.create_MiCasillero_ParametroSistema()
    instance2 = test_helpers.create_MiCasillero_ParametroSistema()
    url = reverse("MiCasillero_ParametroSistema_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_ParametroSistema_create_view(client):
    url = reverse("MiCasillero_ParametroSistema_create")
    data = {
        "nombre_parametro": "text",
        "valor": "text",
        "tipo_dato": "text",
        "fecha_actualizacion": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_ParametroSistema_detail_view(client):
    instance = test_helpers.create_MiCasillero_ParametroSistema()
    url = reverse("MiCasillero_ParametroSistema_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_ParametroSistema_update_view(client):
    instance = test_helpers.create_MiCasillero_ParametroSistema()
    url = reverse("MiCasillero_ParametroSistema_update", args=[instance.pk, ])
    data = {
        "nombre_parametro": "text",
        "valor": "text",
        "tipo_dato": "text",
        "fecha_actualizacion": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_PartidaArancelaria_list_view(client):
    instance1 = test_helpers.create_MiCasillero_PartidaArancelaria()
    instance2 = test_helpers.create_MiCasillero_PartidaArancelaria()
    url = reverse("MiCasillero_PartidaArancelaria_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_PartidaArancelaria_create_view(client):
    url = reverse("MiCasillero_PartidaArancelaria_create")
    data = {
        "item_no": "text",
        "descripcion": "text",
        "partida_arancelaria": "text",
        "impuesto_dai": 1.0,
        "impuesto_isc": 1.0,
        "impuesto_ispc": 1.0,
        "impuesto_isv": 1.0,
        "fecha_actualizacion": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_PartidaArancelaria_detail_view(client):
    instance = test_helpers.create_MiCasillero_PartidaArancelaria()
    url = reverse("MiCasillero_PartidaArancelaria_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_PartidaArancelaria_update_view(client):
    instance = test_helpers.create_MiCasillero_PartidaArancelaria()
    url = reverse("MiCasillero_PartidaArancelaria_update", args=[instance.pk, ])
    data = {
        "item_no": "text",
        "descripcion": "text",
        "partida_arancelaria": "text",
        "impuesto_dai": 1.0,
        "impuesto_isc": 1.0,
        "impuesto_ispc": 1.0,
        "impuesto_isv": 1.0,
        "fecha_actualizacion": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302
