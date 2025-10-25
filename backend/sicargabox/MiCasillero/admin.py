from django.contrib import admin
from django import forms
from guardian.admin import GuardedModelAdmin

from . import models


class ParametroSistemaAdminForm(forms.ModelForm):
    class Meta:
        model = models.ParametroSistema
        fields = "__all__"


class ParametroSistemaAdmin(GuardedModelAdmin):
    form = ParametroSistemaAdminForm
    list_display = [
        "nombre_parametro",
        "valor",
        "tipo_dato",
        "fecha_actualizacion",
    ]
    readonly_fields = [
        "fecha_actualizacion",
    ]


class PartidaArancelariaAdminForm(forms.ModelForm):
    class Meta:
        model = models.PartidaArancelaria
        fields = "__all__"
        widgets = {
            "descripcion": forms.Textarea(attrs={
                "rows": 3,
                "style": "width:100%;",  # full row
            }),
            "restrictions": forms.Textarea(attrs={
                "rows": 3,
                "style": "width:100%;",  # full row
            }),
            "special_instructions": forms.Textarea(attrs={
                "rows": 3,
                "style": "width:100%;",  # full row
            }),
        }

class PartidaArancelariaAdmin(GuardedModelAdmin):
    form = PartidaArancelariaAdminForm
    list_display = [
        'item_no',
        'descripcion',
        'partida_arancelaria',
        'impuesto_dai',
        'impuesto_isc',
        'impuesto_ispc',
        'impuesto_isv',
        'courier_category',
        'requires_special_handling'
    ]
    list_filter = ['courier_category', 'requires_special_handling']
    search_fields = ['item_no', 'descripcion', 'partida_arancelaria', 'search_keywords']
    readonly_fields = ['chapter_code', 'heading_code', 'parent_item_no', 'hierarchy_level']
    fieldsets = (
        ('Información Básica', {
            'fields': ('item_no', 'descripcion', 'partida_arancelaria'),
            'classes': ('collapse',)
        }),
        ('Información Fiscal', {
            'fields': ('impuesto_dai', 'impuesto_isc', 'impuesto_ispc', 'impuesto_isv'),
            'classes': ('collapse',)
        }),
        ('Configuración de Courier', {
            'fields': (
                'courier_category',
                'restrictions',
                'package_type',
                'max_weight_allowed',
                'requires_special_handling',
                'special_instructions'
            ),
            'classes': ('collapse',)
        }),
        ('Jerarquía y Búsqueda', {
            'fields': (
                'chapter_code',
                'heading_code',
                'parent_item_no',
                'hierarchy_level',
                'search_keywords'
            ),
            'classes': ('collapse',)
        })
    )


class ClienteAdminForm(forms.ModelForm):
    class Meta:
        model = models.Cliente
        fields = "__all__"


class ClienteAdmin(GuardedModelAdmin):
    form = ClienteAdminForm
    list_display = [
        "nombres",
        "apellidos",
        "nombre_corto",
        "direccion",
        "telefono",
        "correo_electronico",
        "codigo_cliente",
        "fecha_registro",
    ]
    readonly_fields = [
        "nombre_corto",
        "codigo_cliente",
        "fecha_registro",
    ]


class CotizacionAdminForm(forms.ModelForm):
    class Meta:
        model = models.Cotizacion
        fields = "__all__"


class CotizacionAdmin(GuardedModelAdmin):
    form = CotizacionAdminForm
    list_display = [
        "cliente",
        "fecha_creacion",
        "estado",
    ]
    readonly_fields = [
        "cliente",
        "fecha_creacion",
        "estado",
    ]


class ArticuloAdminForm(forms.ModelForm):
    class Meta:
        model = models.Articulo
        fields = "__all__"


class ArticuloAdmin(GuardedModelAdmin):
    form = ArticuloAdminForm
    list_display = [
        "cotizacion",
        "valor_articulo",
        "largo",
        "ancho",
        "alto",
        "peso",
        "impuesto_dai",
        "impuesto_isc",
        "impuesto_ispc",
        "impuesto_isv",
        "impuesto_total",
    ]
    readonly_fields = [
        "cotizacion",
        "valor_articulo",
        "largo",
        "ancho",
        "alto",
        "peso",
        "impuesto_dai",
        "impuesto_isc",
        "impuesto_ispc",
        "impuesto_isv",
        "impuesto_total",
    ]


class EnvioAdminForm(forms.ModelForm):
    class Meta:
        model = models.Envio
        fields = "__all__"


class EnvioAdmin(GuardedModelAdmin):
    form = EnvioAdminForm
    list_display = [
        "cotizacion",
        "cliente",
        "tracking_number_original",
        "tracking_number_sicarga",
        "estado_envio",
        "fecha_actualizacion",
    ]
    readonly_fields = [
        "cotizacion",
        "cliente",
        "tracking_number_original",
        "tracking_number_sicarga",
        "estado_envio",
        "fecha_actualizacion",
    ]


class FacturaAdminForm(forms.ModelForm):
    class Meta:
        model = models.Factura
        fields = "__all__"


class FacturaAdmin(GuardedModelAdmin):
    form = FacturaAdminForm
    list_display = [
        "envio",
        "cliente",
        "flete",
        "total_impuesto_dai",
        "total_impuesto_isc",
        "total_impuesto_ispc",
        "total_impuesto_isv",
        "total_impuesto",
        "monto_total",
        "fecha_emision",
        "estado_pago",
    ]
    readonly_fields = [
        "envio",
        "cliente",
        "flete",
        "total_impuesto_dai",
        "total_impuesto_isc",
        "total_impuesto_ispc",
        "total_impuesto_isv",
        "total_impuesto",
        "monto_total",
        "fecha_emision",
        "estado_pago",
    ]


class AlertaAdminForm(forms.ModelForm):
    class Meta:
        model = models.Alerta
        fields = "__all__"


class AlertaAdmin(GuardedModelAdmin):
    form = AlertaAdminForm
    list_display = [
        "envio",
        "cliente",
        "tipo_alerta",
        "mensaje",
        "fecha_envio",
        "estado",
    ]
    readonly_fields = [
        "envio",
        "cliente",
        "tipo_alerta",
        "mensaje",
        "fecha_envio",
        "estado",
    ]


admin.site.register(models.Alerta, AlertaAdmin)
admin.site.register(models.Articulo, ArticuloAdmin)
admin.site.register(models.Cliente, ClienteAdmin)
admin.site.register(models.Cotizacion, CotizacionAdmin)
admin.site.register(models.Envio, EnvioAdmin)
admin.site.register(models.Factura, FacturaAdmin)
admin.site.register(models.ParametroSistema, ParametroSistemaAdmin)
admin.site.register(models.PartidaArancelaria, PartidaArancelariaAdmin)
