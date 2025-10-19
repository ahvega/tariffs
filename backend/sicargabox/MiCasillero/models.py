from decimal import Decimal
from typing import Union, Dict
from typing import TYPE_CHECKING
import json
from datetime import timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm, remove_perm, get_users_with_perms
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.db.models import F
from django.contrib.postgres.search import SearchVector
from django.utils import timezone
from typing import TYPE_CHECKING


class ParametroSistemaManager(models.Manager):
    @staticmethod
    def get_valor(parametro: str) -> Union[str, int, float, bool, None]:
        try:
            parametro_obj = ParametroSistema.objects.get(nombre_parametro=parametro)
            if parametro_obj.tipo_dato == 'STRING':
                return parametro_obj.valor
            elif parametro_obj.tipo_dato == 'INTEGER':
                return int(parametro_obj.valor)
            elif parametro_obj.tipo_dato == 'FLOAT':
                return float(parametro_obj.valor)
            elif parametro_obj.tipo_dato == 'BOOLEAN':
                return parametro_obj.valor.lower() in ['true', '1']
            else:
                raise ValidationError(f"Tipo de dato no soportado: {parametro_obj.tipo_dato}")
        except ParametroSistema.DoesNotExist:
            raise ValidationError(f"El parámetro {parametro} no está definido.")


class ParametroSistema(models.Model):
    TIPO_DATO_CHOICES = [
        ('STRING', 'String'),
        ('INTEGER', 'Integer'),
        ('FLOAT', 'Float'),
        ('BOOLEAN', 'Boolean'),
    ]

    nombre_parametro = models.CharField(max_length=50, unique=True)
    valor = models.CharField(max_length=255)
    tipo_dato = models.CharField(max_length=10, choices=TIPO_DATO_CHOICES)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Annotate the manager so static analyzers (Pylance/mypy) know about custom methods
    if TYPE_CHECKING:
        objects: 'ParametroSistemaManager'
    objects = ParametroSistemaManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_parametro}: {self.valor}"

    def get_absolute_url(self):
        return reverse("MiCasillero_ParametroSistema_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("MiCasillero_ParametroSistema_update", args=(self.pk,))

    @staticmethod
    def get_htmx_create_url():
        return reverse("MiCasillero_ParametroSistema_htmx_create")

    def get_htmx_delete_url(self):
        return reverse("MiCasillero_ParametroSistema_htmx_delete", args=(self.pk,))


def assign_permissions_to_groups(instance, permissions, model_name):
    groups = ['Operadores', 'Administradores']
    for group in groups:
        users = User.objects.filter(groups__name=group)
        for user in users:
            for permission in permissions:
                assign_perm(f'{permission}_{model_name}', user, instance)


class PartidaArancelaria(models.Model):
    CATEGORY_CHOICES = [
        ('ALLOWED', 'Permitido para Courier'),
        ('RESTRICTED', 'Articulos restringidos para Courier'),
        ('PROHIBITED', 'Articulos prohibidos para Courier'),
    ]

    item_no = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=1255)
    partida_arancelaria = models.CharField(max_length=50)
    impuesto_dai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    impuesto_isc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    impuesto_ispc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    impuesto_isv = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # New fields for courier-specific information
    courier_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='ALLOWED')
    restrictions = models.JSONField(default=list, blank=True)
    package_type = models.CharField(max_length=100, blank=True)
    max_weight_allowed = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    requires_special_handling = models.BooleanField(default=False)
    special_instructions = models.TextField(blank=True)
    
    # Search optimization fields
    search_keywords = models.JSONField(default=list, blank=True, null=True)  # Para keywords generados por AI
    search_vector = SearchVectorField(null=True)  # Campo para búsqueda de texto completo
    parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        indexes = [
            models.Index(fields=['item_no']),
            models.Index(fields=['descripcion']),
            models.Index(fields=['courier_category']),
            GinIndex(fields=['search_vector'], name='partida_search_vector_idx'),
        ]
        
    def update_search_vector(self):
        """Actualiza el vector de búsqueda combinando descripción y keywords"""
        # Crear vector con diferentes pesos para cada campo
        vector = SearchVector('descripcion', weight='A')
        if self.search_keywords:
            # Convertir la lista de keywords a texto
            keywords_text = ' '.join(self.search_keywords)
            vector = vector + SearchVector(F('search_keywords'), weight='B')
        
        # Actualizar el campo search_vector
        self.search_vector = vector
        
    def save(self, *args, **kwargs):
        # Asegurarse de que search_keywords sea una lista válida
        if self.search_keywords is None:
            self.search_keywords = []
        elif isinstance(self.search_keywords, str):
            # Si es un string, intentar convertirlo a lista
            try:
                self.search_keywords = json.loads(self.search_keywords)
            except json.JSONDecodeError:
                # Si no es JSON válido, convertirlo a lista de un elemento
                self.search_keywords = [self.search_keywords] if self.search_keywords.strip() else []

        # Set search_vector to None on insert (will be updated later with a query)
        # F() expressions can only be used for updates, not inserts
        if not self.pk:
            self.search_vector = None

        super().save(*args, **kwargs)

        # Update search_vector after insert using an UPDATE query
        if not kwargs.get('update_fields'):
            PartidaArancelaria.objects.filter(pk=self.pk).update(
                search_vector=SearchVector('descripcion', weight='A') + SearchVector('search_keywords', weight='B')
            )
    
    def generate_search_keywords(self):
        """Generate additional search keywords for the item"""
        # This could be enhanced with AI-generated keywords
        keywords = [
            self.descripcion,
            self.item_no,
            self.partida_arancelaria
        ]
        return ' '.join(keywords)

    def is_courier_safe(self) -> bool:
        """Check if item is safe for courier shipping"""
        return self.courier_category == 'ALLOWED'

    def get_shipping_requirements(self) -> Dict:
        """Get shipping requirements for this item"""
        return {
            'category': self.courier_category,
            'restrictions': self.restrictions,
            'package_type': self.package_type,
            'special_handling': self.requires_special_handling,
            'instructions': self.special_instructions
        }

    def __str__(self):
        suma_impuestos = (self.impuesto_dai + self.impuesto_isc + self.impuesto_ispc + self.impuesto_isv) * 100
        return f"{self.descripcion} [{suma_impuestos:.2f}%]"

    def get_absolute_url(self):
        return reverse("MiCasillero_PartidaArancelaria_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("MiCasillero_PartidaArancelaria_update", args=(self.pk,))

    @staticmethod
    def get_htmx_create_url():
        return reverse("MiCasillero_PartidaArancelaria_htmx_create")

    def get_htmx_delete_url(self):
        return reverse("MiCasillero_PartidaArancelaria_htmx_delete", args=(self.pk,))


class Cliente(models.Model):
    if TYPE_CHECKING:
        id: int
        pk: int
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    correo_electronico = models.EmailField(unique=True)
    nombre_corto = models.CharField(max_length=50, blank=True)  # Este campo se generará programáticamente
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=50, default='San Pedro Sula')
    departamento = models.CharField(max_length=50, default='Cortés')
    pais = models.CharField(max_length=50, default='Honduras')
    codigo_cliente = models.CharField(max_length=13, unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generar nombre_corto
        if not self.nombre_corto:
            if self.nombres and self.apellidos:
                nombres_iniciales = ''.join([n[0].upper() + '.' for n in self.nombres.split() if n])
                apellidos = self.apellidos.split()
                if apellidos:
                    apellidos_iniciales = ''.join([a[0].upper() for a in apellidos[1:] if a])
                    self.nombre_corto = f"{nombres_iniciales}{apellidos[0]} {apellidos_iniciales}"
                else:
                    self.nombre_corto = nombres_iniciales
            else:
                self.nombre_corto = ''

        # Generar codigo_cliente
        needs_second_save = False
        if not self.codigo_cliente:
            # Remove force_insert for the first save since we'll need to update the codigo_cliente
            kwargs_first_save = kwargs.copy()
            kwargs_first_save.pop('force_insert', None)
            super().save(*args, **kwargs_first_save)  # Guardar primero para obtener el ID
            prefijo_any = ParametroSistema.objects.get_valor("Prefijo del Código de Cliente")
            if prefijo_any is None:
                raise ValidationError("El parámetro 'Prefijo del Código de Cliente' no está definido.")
            prefijo = str(prefijo_any)
            self.codigo_cliente = f"{prefijo}-{str(self.id).zfill(6)}"
            needs_second_save = True

        # Llenar los campos de User email first_name y last_name
        self.user.email = self.correo_electronico
        self.user.first_name = self.nombres
        self.user.last_name = self.apellidos
        self.user.save()

        # Only save again if we haven't already saved or if codigo_cliente was updated
        if needs_second_save or not self.pk:
            # Remove force_insert for the second save since the record already exists
            kwargs_second_save = kwargs.copy()
            kwargs_second_save.pop('force_insert', None)
            super().save(*args, **kwargs_second_save)
        elif kwargs.get('update_fields') or not needs_second_save:
            # Normal update path - respects force_insert if provided
            super().save(*args, **kwargs)

        # Asignar permisos de objeto al usuario
        assign_perm('view_cliente', self.user, self)
        assign_perm('change_cliente', self.user, self)
        assign_perm('delete_cliente', self.user, self)

        # Asignar permisos de objeto a los operadores y administradores
        permissions = ['view', 'change']
        if 'Administradores' in [group.name for group in self.user.groups.all()]:
            permissions.append('delete')
        assign_permissions_to_groups(self, permissions, 'cliente')

        # Remover permisos de objeto a los usuarios que no sean el creador
        users_with_perms = get_users_with_perms(self, with_group_users=False)
        for user in users_with_perms:
            if user != self.user:
                remove_perm('view_cliente', user, self)
                remove_perm('change_cliente', user, self)
                remove_perm('delete_cliente', user, self)

    def __str__(self):
        return f"{self.user.username} - {self.nombre_corto}"

    def get_absolute_url(self):
        return reverse("MiCasillero_Cliente_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("MiCasillero_Cliente_update", args=(self.pk,))

    @staticmethod
    def get_htmx_create_url():
        return reverse("MiCasillero_Cliente_htmx_create")

    def get_htmx_delete_url(self):
        return reverse("MiCasillero_Cliente_htmx_delete", args=(self.pk,))


# Agregar una propiedad al modelo User para acceder al Cliente asociado
User.add_to_class('cliente', property(lambda u: Cliente.objects.get_or_create(user=u)[0]))


class Cotizacion(models.Model):
    if TYPE_CHECKING:
        id: int
        pk: int
    ESTADO_CHOICES = [
        ('Pendiente', 'Cotización Pendiente'),
        ('Aceptada', 'Aceptada - Envío Solicitado'),
        ('Expirada', 'Expirada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)  # Null for anonymous
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()  # Auto-calculate (fecha_creacion + días de validez from ParametroSistema)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    subtotal_articulos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_flete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    session_key = models.CharField(max_length=40, blank=True)

    def save(self, *args, **kwargs):
        if self.fecha_creacion is None:
            self.fecha_creacion = timezone.now()

        dias_validez = ParametroSistema.objects.get_valor("Días Validez Cotización")
        if dias_validez is None:
            raise ValidationError("El parámetro 'Días Validez Cotización' no está definido.")
        try:
            dias_validez = int(dias_validez)
        except (TypeError, ValueError):
            raise ValidationError("El parámetro 'Días Validez Cotización' debe ser un número entero.")

        self.fecha_expiracion = self.fecha_creacion + timedelta(days=dias_validez)

        super().save(*args, **kwargs)
        assign_perm('view_cotizacion', self.cliente.user, self)
        assign_perm('change_cotizacion', self.cliente.user, self)
        assign_perm('delete_cotizacion', self.cliente.user, self)

        # Asignar permisos de objeto a los operadores y administradores
        permissions = ['view', 'change']
        if 'Administradores' in [group.name for group in self.cliente.user.groups.all()]:
            permissions.append('delete')
        assign_permissions_to_groups(self, permissions, 'cotizacion')

    def __str__(self):
        return f"Cotización {self.id} - Cliente {self.cliente.codigo_cliente}"

    def get_absolute_url(self):
        return reverse("MiCasillero_Cotizacion_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("MiCasillero_Cotizacion_update", args=(self.pk,))

    @staticmethod
    def get_htmx_create_url():
        return reverse("MiCasillero_Cotizacion_htmx_create")

    def get_htmx_delete_url(self):
        return reverse("MiCasillero_Cotizacion_htmx_delete", args=(self.pk,))


class Envio(models.Model):
    if TYPE_CHECKING:
        id: int
        pk: int
    ESTADO_ENVIO_CHOICES = [
        ('Solicitado', 'Solicitud Recibida'),
        ('Recibido en Miami', 'Recibido en Miami'),
        ('Procesado', 'Procesado y Listo para Envío'),
        ('En tránsito a Honduras', 'En Tránsito a Honduras'),
        ('En aduana', 'En Proceso de Aduana'),
        ('Liberado de aduana', 'Liberado de Aduana'),
        ('En bodega local', 'En Bodega Local'),
        ('Disponible para entrega', 'Disponible para Entrega'),
        ('Entregado', 'Entregado al Cliente'),
    ]

    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tracking_number_original = models.CharField(max_length=50)  # From retailer
    tracking_number_sicarga = models.CharField(max_length=50, unique=True)  # Internal
    estado_envio = models.CharField(max_length=50, choices=ESTADO_ENVIO_CHOICES, default='Solicitado')
    peso_estimado = models.DecimalField(max_digits=8, decimal_places=2)
    peso_real = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    largo_real = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ancho_real = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    alto_real = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    factura_compra = models.FileField(upload_to='invoices/', null=True, blank=True)
    foto_paquete = models.ImageField(upload_to='packages/', null=True, blank=True)
    direccion_entrega = models.CharField(max_length=255)
    instrucciones_especiales = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_recibido_miami = models.DateTimeField(null=True, blank=True)
    fecha_salida_miami = models.DateTimeField(null=True, blank=True)
    fecha_llegada_honduras = models.DateTimeField(null=True, blank=True)
    fecha_liberacion_aduana = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calcular el volumen total de los artículos
        volumen_total = sum(
            articulo.largo * articulo.ancho * articulo.alto
            for articulo in self.cotizacion.articulos.all()
        )
        peso_volumetrico_total: Decimal | float = volumen_total / Articulo.FACTOR_VOL

        # Calcular el peso total
        peso_total = sum(articulo.peso for articulo in self.cotizacion.articulos.all())

        # Seleccionar el mayor peso entre el real y el volumétrico total
        peso_a_usar = max(Decimal(peso_total), Decimal(peso_volumetrico_total))

        # Obtener el costo por libra desde ParametroSistema
        costo_por_libra = ParametroSistema.objects.get_valor("Costo Flete por Libra en USD$")

        if costo_por_libra is None:
            raise ValidationError("El parámetro 'Costo Flete por Libra en USD$' no está definido.")
        try:
            costo_decimal = Decimal(str(costo_por_libra))
        except Exception:
            raise ValidationError("El parámetro 'Costo Flete por Libra en USD$' no es convertible a Decimal.")

        # Calcular el flete
        self.flete = peso_a_usar * costo_decimal

        super().save(*args, **kwargs)
        # Asignar permisos de objeto al usuario
        assign_perm('view_envio', self.cotizacion.cliente.user, self)
        assign_perm('change_envio', self.cotizacion.cliente.user, self)
        assign_perm('delete_envio', self.cotizacion.cliente.user, self)
        # Asignar permisos de objeto a los operadores y administradores
        permissions = ['view', 'change']
        if 'Administradores' in [group.name for group in self.cotizacion.cliente.user.groups.all()]:
            permissions.append('delete')
        assign_permissions_to_groups(self, permissions, 'envio')

    def __str__(self):
        return f"Envío {self.id} - Cliente {self.cliente.codigo_cliente}"

    def get_absolute_url(self):
        return reverse("MiCasillero_Envio_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("MiCasillero_Envio_update", args=(self.pk,))

    @staticmethod
    def get_htmx_create_url():
        return reverse("MiCasillero_Envio_htmx_create")

    def get_htmx_delete_url(self):
        return reverse("MiCasillero_Envio_htmx_delete", args=(self.pk,))


class StatusUpdate(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE, related_name='status_history')
    estado_anterior = models.CharField(max_length=50, blank=True)
    estado_nuevo = models.CharField(max_length=50)
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-fecha']


class Factura(models.Model):
    if TYPE_CHECKING:
        id: int
        pk: int
    ESTADO_PAGO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Pagada', 'Pagada'),
        ('Cancelada', 'Cancelada'),
    ]

    envio = models.ForeignKey(Envio, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    flete = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_impuesto_dai = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_impuesto_isc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_impuesto_ispc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_impuesto_isv = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_impuesto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES)

    def save(self, *args, **kwargs):
        # Obtener los valores de la cotización asociada
        articulos = self.envio.cotizacion.articulos.all()

        self.flete = self.envio.flete
        self.total_impuesto_dai = sum(articulo.impuesto_dai for articulo in articulos)
        self.total_impuesto_isc = sum(articulo.impuesto_isc for articulo in articulos)
        self.total_impuesto_ispc = sum(articulo.impuesto_ispc for articulo in articulos)
        self.total_impuesto_isv = sum(articulo.impuesto_isv for articulo in articulos)
        self.total_impuesto = sum(articulo.impuesto_total for articulo in articulos)

        # Calcular el monto total
        self.monto_total = self.flete + self.total_impuesto

        super().save(*args, **kwargs)
        # Asignar permisos de objeto al usuario
        assign_perm('view_factura', self.cliente.user, self)
        assign_perm('change_factura', self.cliente.user, self)
        assign_perm('delete_factura', self.cliente.user, self)
        # Asignar permisos de objeto a los operadores y administradores
        permissions = ['view', 'change']
        if 'Administradores' in [group.name for group in self.cliente.user.groups.all()]:
            permissions.append('delete')
        assign_permissions_to_groups(self, permissions, 'factura')

    def __str__(self):
        return f"Factura {self.id} - Envío {self.envio.id}"

    def get_absolute_url(self):
        return reverse("MiCasillero_Factura_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("MiCasillero_Factura_update", args=(self.pk,))

    @staticmethod
    def get_htmx_create_url():
        return reverse("MiCasillero_Factura_htmx_create")

    def get_htmx_delete_url(self):
        return reverse("MiCasillero_Factura_htmx_delete", args=(self.pk,))


class Alerta(models.Model):
    if TYPE_CHECKING:
        id: int
        pk: int
    TIPO_ALERTA_CHOICES = [
        ('SMS', 'SMS'),
        ('WhatsApp', 'WhatsApp'),
    ]

    ESTADO_ALERTA_CHOICES = [
        ('Enviado', 'Enviado'),
        ('Error', 'Error'),
    ]

    envio = models.ForeignKey(Envio, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo_alerta = models.CharField(max_length=50, choices=TIPO_ALERTA_CHOICES)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_ALERTA_CHOICES)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Asignar permisos de objeto al usuario
        assign_perm('view_alerta', self.cliente.user, self)
        assign_perm('change_alerta', self.cliente.user, self)
        assign_perm('delete_alerta', self.cliente.user, self)
        # Asignar permisos de objeto a los operadores y administradores
        permissions = ['view', 'change']
        if 'Administradores' in [group.name for group in self.cliente.user.groups.all()]:
            permissions.append('delete')
        assign_permissions_to_groups(self, permissions, 'alerta')

    def __str__(self):
        return f"Alerta {self.id} - Envío {self.envio.id}"

    def get_absolute_url(self):
        return reverse("MiCasillero_Alerta_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("MiCasillero_Alerta_update", args=(self.pk,))

    @staticmethod
    def get_htmx_create_url():
        return reverse("MiCasillero_Alerta_htmx_create")

    def get_htmx_delete_url(self):
        return reverse("MiCasillero_Alerta_htmx_delete", args=(self.pk,))


class Articulo(models.Model):
    if TYPE_CHECKING:
        id: int
        pk: int
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='articulos')
    descripcion_original = models.CharField(max_length=255, help_text="Descripción del producto según la factura de compra")
    valor_articulo = models.DecimalField(max_digits=10, decimal_places=2)
    largo = models.DecimalField(max_digits=5, decimal_places=2)
    ancho = models.DecimalField(max_digits=5, decimal_places=2)
    alto = models.DecimalField(max_digits=5, decimal_places=2)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    partida_arancelaria = models.ForeignKey(PartidaArancelaria, on_delete=models.CASCADE)
    impuesto_dai = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    impuesto_isc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    impuesto_ispc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    impuesto_isv = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    impuesto_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)

    # AI matching fields
    ai_suggested_partidas = models.JSONField(
        null=True,
        blank=True,
        help_text="Top 5 sugerencias del sistema AI: [{partida_id, score, reason}, ...]"
    )
    ai_confidence_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Nivel de confianza de la sugerencia seleccionada (0-1)"
    )
    was_manually_corrected = models.BooleanField(
        default=False,
        help_text="¿Fue corregida manualmente por el personal?"
    )
    correction_reason = models.TextField(
        blank=True,
        help_text="Razón de la corrección manual"
    )

    FACTOR_VOL = 166  # Factor de volumen estándar en pulgadas cúbicas por libra

    @property
    def partida_item_no(self):
        return self.partida_arancelaria.item_no

    @property
    def partida_descripcion(self):
        return self.partida_arancelaria.descripcion

    @property
    def partida_numero(self):
        return self.partida_arancelaria.partida_arancelaria

    @property
    def porcentaje_dai(self):
        return self.partida_arancelaria.impuesto_dai * 100

    @property
    def porcentaje_isc(self):
        return self.partida_arancelaria.impuesto_isc * 100

    @property
    def porcentaje_ispc(self):
        return self.partida_arancelaria.impuesto_ispc * 100

    @property
    def porcentaje_isv(self):
        return self.partida_arancelaria.impuesto_isv * 100

    @property
    def peso_volumetrico(self):
        """Calculate volumetric weight in kg based on dimensions."""
        volumen = self.largo * self.ancho * self.alto
        return volumen / Decimal(self.FACTOR_VOL)

    @property
    def peso_a_usar(self):
        """Return the greater of actual weight or volumetric weight."""
        return max(self.peso, self.peso_volumetrico)

    @property
    def costo_flete_por_lb(self):
        costo_any = ParametroSistema.objects.get_valor("Costo Flete por Libra en USD$")
        if costo_any is None:
            raise ValidationError("El parámetro 'Costo Flete por Libra en USD$' no está definido.")
        try:
            return Decimal(str(costo_any))
        except Exception:
            raise ValidationError("El parámetro 'Costo Flete por Libra en USD$' no es convertible a Decimal.")

    @property
    def costo_transporte(self):
        return self.peso_a_usar * self.costo_flete_por_lb

    def calcular_impuestos(self):
        impuesto_dai = self.valor_articulo * (self.porcentaje_dai / 100)
        impuesto_isc = self.valor_articulo * (self.porcentaje_isc / 100)
        impuesto_ispc = self.valor_articulo * (self.porcentaje_ispc / 100)
        impuesto_isv = self.valor_articulo * (self.porcentaje_isv / 100)
        impuesto_total = (
                impuesto_dai +
                impuesto_isc +
                impuesto_ispc +
                impuesto_isv
        )

        self.impuesto_dai = impuesto_dai
        self.impuesto_isc = impuesto_isc
        self.impuesto_ispc = impuesto_ispc
        self.impuesto_isv = impuesto_isv
        self.impuesto_total = impuesto_total

    def save(self, *args, **kwargs):
        self.calcular_impuestos()

        super().save(*args, **kwargs)

        # Asignar permisos de objeto al usuario
        assign_perm('view_articulo', self.cotizacion.cliente.user, self)
        assign_perm('change_articulo', self.cotizacion.cliente.user, self)
        assign_perm('delete_articulo', self.cotizacion.cliente.user, self)

        # Asignar permisos de objeto a los operadores y administradores
        permissions = ['view', 'change']
        if 'Administradores' in [group.name for group in self.cotizacion.cliente.user.groups.all()]:
            permissions.append('delete')
        assign_permissions_to_groups(self, permissions, 'articulo')

    def __str__(self):
        return f"Artículo {self.id} - Cotización {self.cotizacion.id}"

    def get_absolute_url(self):
        return reverse("MiCasillero_Articulo_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("MiCasillero_Articulo_update", args=(self.pk,))

    @staticmethod
    def get_htmx_create_url():
        return reverse("MiCasillero_Articulo_htmx_create")

    def get_htmx_delete_url(self):
        return reverse("MiCasillero_Articulo_htmx_delete", args=(self.pk,))


class ItemPartidaMapping(models.Model):
    """
    Records historical mappings between item descriptions and tariff classifications.
    Powers the AI learning system to improve semantic search accuracy over time.
    """
    # Item information
    item_description_original = models.CharField(
        max_length=500,
        help_text="Descripción del producto como aparece en la factura del cliente"
    )
    item_description_normalized = models.CharField(
        max_length=500,
        db_index=True,
        help_text="Descripción normalizada (lowercase, sin caracteres especiales)"
    )
    item_embedding = models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embedding del item para búsqueda semántica"
    )

    # Matched partida
    partida_arancelaria = models.ForeignKey(
        PartidaArancelaria,
        on_delete=models.CASCADE,
        related_name='item_mappings'
    )

    # Match quality metrics
    confidence_score = models.FloatField(
        default=0,
        help_text="Nivel de confianza de la sugerencia AI (0-1)"
    )
    ranking_position = models.IntegerField(
        default=1,
        help_text="Posición en las sugerencias (1=primera sugerencia, 2=segunda, etc.)"
    )
    was_ai_suggestion = models.BooleanField(
        default=True,
        help_text="¿Fue sugerido por el sistema AI?"
    )

    # Context
    selected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partida_selections'
    )
    is_staff_verified = models.BooleanField(
        default=False,
        help_text="¿Seleccionado/verificado por personal administrativo?"
    )
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partida_mapping'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(
        max_length=40,
        blank=True,
        help_text="Session key para usuarios anónimos"
    )

    # Validation tracking
    staff_override = models.BooleanField(
        default=False,
        help_text="¿Fue corregido por el personal?"
    )
    override_from = models.ForeignKey(
        PartidaArancelaria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='overridden_mappings',
        help_text="Partida original antes de la corrección"
    )
    override_reason = models.TextField(
        blank=True,
        help_text="Razón de la corrección"
    )

    class Meta:
        indexes = [
            models.Index(fields=['item_description_normalized']),
            models.Index(fields=['partida_arancelaria', '-created_at']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_staff_verified']),
        ]
        verbose_name = "Mapeo Item-Partida"
        verbose_name_plural = "Mapeos Item-Partida"

    def normalize_description(self, description):
        """Normaliza la descripción del item para comparación."""
        import re
        # Convertir a minúsculas y eliminar espacios extras
        normalized = description.lower().strip()
        # Eliminar caracteres especiales, mantener solo letras y espacios
        normalized = re.sub(r'[^a-záéíóúñ\s]', '', normalized)
        # Eliminar espacios múltiples
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized

    def save(self, *args, **kwargs):
        if not self.item_description_normalized:
            self.item_description_normalized = self.normalize_description(
                self.item_description_original
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_description_original[:50]} → {self.partida_arancelaria.item_no}"


class PartidaArancelariaEmbedding(models.Model):
    """
    Almacena los embeddings semánticos para las partidas arancelarias.
    Permite búsqueda por similitud vectorial.
    """
    partida_arancelaria = models.OneToOneField(
        PartidaArancelaria,
        on_delete=models.CASCADE,
        related_name='embedding_data'
    )

    # Embedding vector (1536 dimensiones para OpenAI text-embedding-3-small)
    embedding_vector = models.JSONField(
        help_text="Vector de embedding (1536 dimensiones)"
    )
    embedding_model = models.CharField(
        max_length=50,
        default='text-embedding-3-small',
        help_text="Modelo usado para generar el embedding"
    )

    # Texto combinado usado para generar el embedding
    embedding_text = models.TextField(
        help_text="Texto combinado: descripción + keywords + términos aprendidos"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(
        default=1,
        help_text="Versión del embedding, se incrementa con cada actualización"
    )

    class Meta:
        indexes = [
            models.Index(fields=['partida_arancelaria']),
            models.Index(fields=['-updated_at']),
        ]
        verbose_name = "Embedding de Partida"
        verbose_name_plural = "Embeddings de Partidas"

    def __str__(self):
        return f"Embedding v{self.version} - {self.partida_arancelaria.item_no}"
