from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import migrations


def create_user_groups(apps, schema_editor):
    # Crear grupo UsuariosClientes
    usuarios_clientes, created = Group.objects.get_or_create(name="UsuariosClientes")
    if created:
        # Añadir permisos al grupo UsuariosClientes
        content_type_cliente = ContentType.objects.get_for_model(
            apps.get_model("MiCasillero", "Cliente")
        )
        permissions_cliente = Permission.objects.filter(
            content_type=content_type_cliente
        )
        usuarios_clientes.permissions.set(permissions_cliente)
        usuarios_clientes.save()

    # Crear grupo Operadores
    operadores, created = Group.objects.get_or_create(name="Operadores")
    if created:
        # Permisos para Operadores
        content_types_operador = [
            ContentType.objects.get_for_model(apps.get_model("MiCasillero", model))
            for model in [
                "Cliente",
                "Cotizacion",
                "Articulo",
                "Envio",
                "Factura",
                "Alerta",
            ]
        ]
        permisos_operador = Permission.objects.filter(
            content_type__in=content_types_operador
        ).exclude(codename__in=["delete_cliente"])
        operadores.permissions.set(permisos_operador)
        operadores.save()

    # Crear grupo Vendedores
    vendedores, created = Group.objects.get_or_create(name="Vendedores")
    if created:
        # Permisos para Vendedores
        content_types_vendedor = [
            ContentType.objects.get_for_model(apps.get_model("MiCasillero", model))
            for model in [
                "Cliente",
                "Cotizacion",
                "Articulo",
                "Envio",
                "Factura",
                "Alerta",
            ]
        ]
        permisos_vendedor = Permission.objects.filter(
            content_type__in=content_types_vendedor
        ).exclude(codename__in=["delete_cliente", "add_cliente"])
        vendedores.permissions.set(permisos_vendedor)
        vendedores.save()

    # Crear grupo Administradores
    administradores, created = Group.objects.get_or_create(name="Administradores")
    if created:
        # Permisos para Administradores
        permisos_admin = Permission.objects.all()
        administradores.permissions.set(permisos_admin)
        administradores.save()


class Migration(migrations.Migration):
    dependencies = [
        ("MiCasillero", "0003_alter_cliente_user"),
        (
            "auth",
            "0012_alter_user_first_name_max_length",
        ),  # Ajustado según la última migración disponible
    ]

    operations = [
        migrations.RunPython(create_user_groups),
    ]
