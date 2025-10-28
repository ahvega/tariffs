import json

from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django_select2.forms import Select2Widget

from . import models


class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "password",
        ]


class ClienteForm(forms.ModelForm):
    class Meta:
        model = models.Cliente
        fields = [
            "nombres",
            "apellidos",
            "telefono",
            "correo_electronico",
            "direccion",
            "ciudad",
            "departamento",
            "pais",
        ]


class AlertaForm(forms.ModelForm):
    class Meta:
        model = models.Alerta
        fields = [
            "envio",
            "cliente",
            "tipo_alerta",
            "mensaje",
            "estado",
        ]


class ArticuloForm(forms.ModelForm):
    descripcion_original = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-full p-2 border border-gray-300 rounded bg-gray-200 text-black",
                "placeholder": "Ej: Cuerdas para Guitarra",
            }
        ),
        label=mark_safe(
            "Descripción del Producto <small>(según factura de compra)</small>"
        ),
        help_text="Ingresa la descripción exacta del producto según aparece en tu factura de compra",
    )

    partida_arancelaria = forms.ModelChoiceField(
        queryset=models.PartidaArancelaria.objects.all().order_by("descripcion"),
        widget=Select2Widget(
            attrs={
                "class": "form-control select2",
                "style": "width: 100%",
            }
        ),
        label=mark_safe(
            "Partida Arancelaria <small>(Selecciona la que mejor se ajuste)</small>"
        ),
        help_text="Busca y selecciona la partida arancelaria que mejor se ajuste a tu producto",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agregar los keywords como data attribute
        choices = []
        for partida in self.fields["partida_arancelaria"].queryset:
            option_attrs = {"data-keywords": json.dumps(partida.search_keywords or [])}
            choices.append((partida.id, partida.descripcion, option_attrs))

        self.fields["partida_arancelaria"].widget.choices = choices

    class Meta:
        model = models.Articulo
        fields = [
            "descripcion_original",
            "partida_arancelaria",
            "valor_articulo",
            "peso",
            "largo",
            "ancho",
            "alto",
        ]
        labels = {
            "valor_articulo": mark_safe(
                "Valor en USD$ <small>(Incluir Envío e Impuestos)</small>"
            ),
            "peso": mark_safe("Peso"),
            "largo": mark_safe("Largo"),
            "ancho": mark_safe("Ancho"),
            "alto": mark_safe("Alto"),
        }
        widgets = {
            "valor_articulo": forms.NumberInput(
                attrs={
                    "class": "w-full p-2 border border-gray-300 rounded bg-gray-200 text-black"
                }
            ),
            "peso": forms.NumberInput(
                attrs={
                    "class": "w-full p-2 border border-gray-300 rounded bg-gray-200 text-black"
                }
            ),
            "largo": forms.NumberInput(
                attrs={
                    "class": "w-full p-2 border border-gray-300 rounded bg-gray-200 text-black"
                }
            ),
            "ancho": forms.NumberInput(
                attrs={
                    "class": "w-full p-2 border border-gray-300 rounded bg-gray-200 text-black"
                }
            ),
            "alto": forms.NumberInput(
                attrs={
                    "class": "w-full p-2 border border-gray-300 rounded bg-gray-200 text-black"
                }
            ),
        }
        error_messages = {
            "descripcion_original": {
                "required": "Por favor ingresa la descripción del producto según tu factura.",
            },
            "partida_arancelaria": {
                "required": "Por favor selecciona una partida arancelaria que se ajuste a tu producto.",
            },
            "valor_articulo": {
                "required": "Este campo es obligatorio.",
                "invalid": "Introduce un valor válido.",
            },
            "peso": {
                "required": "Este campo es obligatorio.",
                "invalid": "Introduce un peso válido.",
            },
            "largo": {
                "required": "Este campo es obligatorio.",
                "invalid": "Introduce un valor válido.",
            },
            "ancho": {
                "required": "Este campo es obligatorio.",
                "invalid": "Introduce un valor válido.",
            },
            "alto": {
                "required": "Este campo es obligatorio.",
                "invalid": "Introduce un valor válido.",
            },
        }


class CotizacionForm(forms.ModelForm):
    class Meta:
        model = models.Cotizacion
        fields = [
            "cliente",
            "estado",
        ]


class EnvioForm(forms.ModelForm):
    class Meta:
        model = models.Envio
        fields = [
            "cotizacion",
            "cliente",
            "tracking_number_original",
            "tracking_number_sicarga",
            "estado_envio",
            "peso_estimado",
            "peso_real",
            "largo_real",
            "ancho_real",
            "alto_real",
            "factura_compra",
            "foto_paquete",
            "direccion_entrega",
            "instrucciones_especiales",
        ]


class FacturaForm(forms.ModelForm):
    class Meta:
        model = models.Factura
        fields = [
            "envio",
            "cliente",
            "flete",
            "total_impuesto_dai",
            "total_impuesto_isc",
            "total_impuesto_ispc",
            "total_impuesto_isv",
            "total_impuesto",
            "monto_total",
            "estado_pago",
        ]


class ParametroSistemaForm(forms.ModelForm):
    class Meta:
        model = models.ParametroSistema
        fields = [
            "nombre_parametro",
            "valor",
            "tipo_dato",
        ]


class PartidaArancelariaForm(forms.ModelForm):
    class Meta:
        model = models.PartidaArancelaria
        fields = [
            "item_no",
            "descripcion",
            "partida_arancelaria",
            "impuesto_dai",
            "impuesto_isc",
            "impuesto_ispc",
            "impuesto_isv",
        ]


class CotizarForm(forms.Form):
    partida_arancelaria = forms.IntegerField()
    valor_articulo = forms.DecimalField(max_digits=10, decimal_places=2)
    peso = forms.DecimalField(max_digits=10, decimal_places=2)
    largo = forms.DecimalField(max_digits=10, decimal_places=2)
    ancho = forms.DecimalField(max_digits=10, decimal_places=2)
    alto = forms.DecimalField(max_digits=10, decimal_places=2)
