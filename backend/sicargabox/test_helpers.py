import random
import string
from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser, AbstractUser, Group, User
from django.contrib.contenttypes.models import ContentType

from MiCasillero import models as MiCasillero_models


def random_string(length=10):
    # Create a random string of length length
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def create_User(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_AbstractUser(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return AbstractUser.objects.create(**defaults)


def create_AbstractBaseUser(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return AbstractBaseUser.objects.create(**defaults)


def create_Group(**kwargs):
    defaults = {
        "name": "%s_group" % random_string(5),
    }
    defaults.update(**kwargs)
    return Group.objects.create(**defaults)


def create_ContentType(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ContentType.objects.create(**defaults)


def create_MiCasillero_ParametroSistema(**kwargs):
    defaults = {}
    defaults["nombre_parametro"] = "param_" + random_string(5)
    defaults["valor"] = "test_value"
    defaults["tipo_dato"] = "STRING"
    defaults.update(**kwargs)
    return MiCasillero_models.ParametroSistema.objects.create(**defaults)


def create_MiCasillero_PartidaArancelaria(**kwargs):
    defaults = {}
    defaults["item_no"] = random_string(8)
    defaults["descripcion"] = "Test description"
    defaults["partida_arancelaria"] = random_string(10)
    defaults["impuesto_dai"] = Decimal("0.10")
    defaults["impuesto_isc"] = Decimal("0.10")
    defaults["impuesto_ispc"] = Decimal("0.05")
    defaults["impuesto_isv"] = Decimal("0.15")
    defaults.update(**kwargs)
    return MiCasillero_models.PartidaArancelaria.objects.create(**defaults)


def create_MiCasillero_Cliente(**kwargs):
    defaults = {}
    if "user" not in kwargs:
        defaults["user"] = create_User()
    defaults["nombres"] = "Test"
    defaults["apellidos"] = "User"
    defaults["direccion"] = "Test Address"
    defaults["telefono"] = "12345678"
    defaults["correo_electronico"] = "%s@test.com" % random_string(5)
    defaults.update(**kwargs)

    # Create system parameter if it doesn't exist
    if not MiCasillero_models.ParametroSistema.objects.filter(
        nombre_parametro="Prefijo del Código de Cliente"
    ).exists():
        create_MiCasillero_ParametroSistema(
            nombre_parametro="Prefijo del Código de Cliente",
            valor="CLI",
            tipo_dato="STRING",
        )

    return MiCasillero_models.Cliente.objects.create(**defaults)


def create_MiCasillero_Cotizacion(**kwargs):
    defaults = {}
    if "cliente" not in kwargs:
        defaults["cliente"] = create_MiCasillero_Cliente()
    defaults["estado"] = "Pendiente"
    defaults["subtotal_articulos"] = Decimal("100.00")
    defaults["total_flete"] = Decimal("10.00")
    defaults["total_impuestos"] = Decimal("20.00")
    defaults["total_estimado"] = Decimal("130.00")
    defaults.update(**kwargs)

    # Create system parameter if it doesn't exist
    if not MiCasillero_models.ParametroSistema.objects.filter(
        nombre_parametro="Días Validez Cotización"
    ).exists():
        create_MiCasillero_ParametroSistema(
            nombre_parametro="Días Validez Cotización",
            valor="30",
            tipo_dato="INTEGER",
        )

    return MiCasillero_models.Cotizacion.objects.create(**defaults)


def create_MiCasillero_Articulo(**kwargs):
    defaults = {}
    if "cotizacion" not in kwargs:
        defaults["cotizacion"] = create_MiCasillero_Cotizacion()
    if "partida_arancelaria" not in kwargs:
        defaults["partida_arancelaria"] = create_MiCasillero_PartidaArancelaria()

    defaults["descripcion_original"] = "Test article"
    defaults["valor_articulo"] = Decimal("100.00")
    defaults["largo"] = Decimal("10.00")
    defaults["ancho"] = Decimal("10.00")
    defaults["alto"] = Decimal("10.00")
    defaults["peso"] = Decimal("5.00")
    defaults.update(**kwargs)

    # Create system parameter if it doesn't exist
    if not MiCasillero_models.ParametroSistema.objects.filter(
        nombre_parametro="Costo Flete por Libra en USD$"
    ).exists():
        create_MiCasillero_ParametroSistema(
            nombre_parametro="Costo Flete por Libra en USD$",
            valor="2.50",
            tipo_dato="FLOAT",
        )

    return MiCasillero_models.Articulo.objects.create(**defaults)


def create_MiCasillero_Envio(**kwargs):
    defaults = {}
    if "cotizacion" not in kwargs:
        defaults["cotizacion"] = create_MiCasillero_Cotizacion()
    if "cliente" not in kwargs:
        defaults["cliente"] = defaults["cotizacion"].cliente

    defaults["tracking_number_original"] = "TRK" + random_string(10)
    defaults["tracking_number_sicarga"] = "SIC" + random_string(10)
    defaults["direccion_entrega"] = "Test delivery address"
    defaults["estado_envio"] = "Solicitado"
    defaults["peso_estimado"] = Decimal("5.00")
    defaults.update(**kwargs)
    return MiCasillero_models.Envio.objects.create(**defaults)


def create_MiCasillero_Factura(**kwargs):
    defaults = {}
    if "envio" not in kwargs:
        defaults["envio"] = create_MiCasillero_Envio()
    if "cliente" not in kwargs:
        defaults["cliente"] = defaults["envio"].cliente

    defaults["estado_pago"] = "Pendiente"
    defaults.update(**kwargs)
    return MiCasillero_models.Factura.objects.create(**defaults)


def create_MiCasillero_Alerta(**kwargs):
    defaults = {}
    if "envio" not in kwargs:
        defaults["envio"] = create_MiCasillero_Envio()
    if "cliente" not in kwargs:
        defaults["cliente"] = defaults["envio"].cliente

    defaults["tipo_alerta"] = "SMS"
    defaults["mensaje"] = "Test alert message"
    defaults["estado"] = "Enviado"
    defaults.update(**kwargs)
    return MiCasillero_models.Alerta.objects.create(**defaults)
