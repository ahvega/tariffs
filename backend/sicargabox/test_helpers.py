import random
import string

from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

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


def create_MiCasillero_Alerta(**kwargs):
    defaults = {}
    defaults["tipo_alerta"] = ""
    defaults["mensaje"] = ""
    defaults["fecha_envio"] = datetime.now()
    defaults["estado"] = ""
    defaults.update(**kwargs)
    return MiCasillero_models.Alerta.objects.create(**defaults)


def create_MiCasillero_Articulo(**kwargs):
    defaults = {}
    defaults["valor_articulo"] = ""
    defaults["largo"] = ""
    defaults["ancho"] = ""
    defaults["alto"] = ""
    defaults["peso"] = ""
    defaults["impuesto_dai"] = ""
    defaults["impuesto_isc"] = ""
    defaults["impuesto_ispc"] = ""
    defaults["impuesto_isv"] = ""
    defaults["impuesto_total"] = ""
    defaults.update(**kwargs)
    return MiCasillero_models.Articulo.objects.create(**defaults)


def create_MiCasillero_Cliente(**kwargs):
    defaults = {}
    defaults["nombres"] = ""
    defaults["apellidos"] = ""
    defaults["direccion"] = ""
    defaults["telefono"] = ""
    defaults["correo_electronico"] = ""
    defaults["codigo_cliente"] = ""
    defaults["fecha_registro"] = datetime.now()
    defaults.update(**kwargs)
    return MiCasillero_models.Cliente.objects.create(**defaults)


def create_MiCasillero_Cotizacion(**kwargs):
    defaults = {}
    defaults["fecha_creacion"] = datetime.now()
    defaults["estado"] = ""
    defaults.update(**kwargs)
    return MiCasillero_models.Cotizacion.objects.create(**defaults)


def create_MiCasillero_Envio(**kwargs):
    defaults = {}
    defaults["tracking_number_original"] = ""
    defaults["tracking_number_final"] = ""
    defaults["direccion_casillero"] = ""
    defaults["estado_envio"] = ""
    defaults["flete"] = ""
    defaults["fecha_actualizacion"] = datetime.now()
    defaults.update(**kwargs)
    return MiCasillero_models.Envio.objects.create(**defaults)


def create_MiCasillero_Factura(**kwargs):
    defaults = {}
    defaults["flete"] = ""
    defaults["total_impuesto_dai"] = ""
    defaults["total_impuesto_isc"] = ""
    defaults["total_impuesto_ispc"] = ""
    defaults["total_impuesto_isv"] = ""
    defaults["total_impuesto"] = ""
    defaults["monto_total"] = ""
    defaults["fecha_emision"] = datetime.now()
    defaults["estado_pago"] = ""
    defaults.update(**kwargs)
    return MiCasillero_models.Factura.objects.create(**defaults)


def create_MiCasillero_ParametroSistema(**kwargs):
    defaults = {}
    defaults["nombre_parametro"] = ""
    defaults["valor"] = ""
    defaults["tipo_dato"] = ""
    defaults["fecha_actualizacion"] = datetime.now()
    defaults.update(**kwargs)
    return MiCasillero_models.ParametroSistema.objects.create(**defaults)


def create_MiCasillero_PartidaArancelaria(**kwargs):
    defaults = {}
    defaults["item_no"] = ""
    defaults["descripcion"] = ""
    defaults["partida_arancelaria"] = ""
    defaults["impuesto_dai"] = ""
    defaults["impuesto_isc"] = ""
    defaults["impuesto_ispc"] = ""
    defaults["impuesto_isv"] = ""
    defaults["fecha_actualizacion"] = datetime.now()
    defaults.update(**kwargs)
    return MiCasillero_models.PartidaArancelaria.objects.create(**defaults)
