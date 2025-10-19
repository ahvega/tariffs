from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import HttpResponse
from django.views import generic
from django.template import Template, RequestContext
from django.template.response import TemplateResponse

from . import models
from . import forms


class HTMXAlertaListView(generic.ListView):
    model = models.Alerta
    form_class = forms.AlertaForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "objects": self.get_queryset()
        }
        return TemplateResponse(request, 'htmx/list.html', context)


class HTMXAlertaCreateView(generic.CreateView):
    model = models.Alerta
    form_class = forms.AlertaForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(request, 'htmx/form.html', context)

    def form_valid(self, form):
        super().form_valid(form)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "object": self.object,
            "form": form
        }
        return TemplateResponse(self.request, 'htmx/create.html', context)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(self.request, 'htmx/form.html', context)


class HTMXAlertaDeleteView(generic.DeleteView):
    model = models.Alerta
    success_url = reverse_lazy("MiCasillero_Alerta_htmx_list")

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse()


class HTMXArticuloListView(generic.ListView):
    model = models.Articulo
    form_class = forms.ArticuloForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "objects": self.get_queryset()
        }
        return TemplateResponse(request, 'htmx/list.html', context)


class HTMXArticuloCreateView(generic.CreateView):
    model = models.Articulo
    form_class = forms.ArticuloForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(request, 'htmx/form.html', context)

    def form_valid(self, form):
        super().form_valid(form)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "object": self.object,
            "form": form
        }
        return TemplateResponse(self.request, 'htmx/create.html', context)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(self.request, 'htmx/form.html', context)


class HTMXArticuloDeleteView(generic.DeleteView):
    model = models.Articulo
    success_url = reverse_lazy("MiCasillero_Articulo_htmx_list")

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse()


class HTMXClienteListView(generic.ListView):
    model = models.Cliente
    form_class = forms.ClienteForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "objects": self.get_queryset()
        }
        return TemplateResponse(request, 'htmx/list.html', context)


class HTMXClienteCreateView(generic.CreateView):
    model = models.Cliente
    form_class = forms.ClienteForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(request, 'htmx/form.html', context)

    def form_valid(self, form):
        super().form_valid(form)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "object": self.object,
            "form": form
        }
        return TemplateResponse(self.request, 'htmx/create.html', context)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(self.request, 'htmx/form.html', context)


class HTMXClienteDeleteView(generic.DeleteView):
    model = models.Cliente
    success_url = reverse_lazy("MiCasillero_Cliente_htmx_list")

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse()


class HTMXCotizacionListView(generic.ListView):
    model = models.Cotizacion
    form_class = forms.CotizacionForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "objects": self.get_queryset()
        }
        return TemplateResponse(request, 'htmx/list.html', context)


class HTMXCotizacionCreateView(generic.CreateView):
    model = models.Cotizacion
    form_class = forms.CotizacionForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(request, 'htmx/form.html', context)

    def form_valid(self, form):
        super().form_valid(form)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "object": self.object,
            "form": form
        }
        return TemplateResponse(self.request, 'htmx/create.html', context)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(self.request, 'htmx/form.html', context)


class HTMXCotizacionDeleteView(generic.DeleteView):
    model = models.Cotizacion
    success_url = reverse_lazy("MiCasillero_Cotizacion_htmx_list")

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse()


class HTMXEnvioListView(generic.ListView):
    model = models.Envio
    form_class = forms.EnvioForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "objects": self.get_queryset()
        }
        return TemplateResponse(request, 'htmx/list.html', context)


class HTMXEnvioCreateView(generic.CreateView):
    model = models.Envio
    form_class = forms.EnvioForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(request, 'htmx/form.html', context)

    def form_valid(self, form):
        super().form_valid(form)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "object": self.object,
            "form": form
        }
        return TemplateResponse(self.request, 'htmx/create.html', context)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(self.request, 'htmx/form.html', context)


class HTMXEnvioDeleteView(generic.DeleteView):
    model = models.Envio
    success_url = reverse_lazy("MiCasillero_Envio_htmx_list")

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse()


class HTMXFacturaListView(generic.ListView):
    model = models.Factura
    form_class = forms.FacturaForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "objects": self.get_queryset()
        }
        return TemplateResponse(request, 'htmx/list.html', context)


class HTMXFacturaCreateView(generic.CreateView):
    model = models.Factura
    form_class = forms.FacturaForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(request, 'htmx/form.html', context)

    def form_valid(self, form):
        super().form_valid(form)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "object": self.object,
            "form": form
        }
        return TemplateResponse(self.request, 'htmx/create.html', context)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(self.request, 'htmx/form.html', context)


class HTMXFacturaDeleteView(generic.DeleteView):
    model = models.Factura
    success_url = reverse_lazy("MiCasillero_Factura_htmx_list")

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse()


class HTMXParametroSistemaListView(generic.ListView):
    model = models.ParametroSistema
    form_class = forms.ParametroSistemaForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "objects": self.get_queryset()
        }
        return TemplateResponse(request, 'htmx/list.html', context)


class HTMXParametroSistemaCreateView(generic.CreateView):
    model = models.ParametroSistema
    form_class = forms.ParametroSistemaForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(request, 'htmx/form.html', context)

    def form_valid(self, form):
        super().form_valid(form)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "object": self.object,
            "form": form
        }
        return TemplateResponse(self.request, 'htmx/create.html', context)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(self.request, 'htmx/form.html', context)


class HTMXParametroSistemaDeleteView(generic.DeleteView):
    model = models.ParametroSistema
    success_url = reverse_lazy("MiCasillero_ParametroSistema_htmx_list")

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse()


class HTMXPartidaArancelariaListView(generic.ListView):
    model = models.PartidaArancelaria
    form_class = forms.PartidaArancelariaForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "objects": self.get_queryset()
        }
        return TemplateResponse(request, 'htmx/list.html', context)


class HTMXPartidaArancelariaCreateView(generic.CreateView):
    model = models.PartidaArancelaria
    form_class = forms.PartidaArancelariaForm

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(request, 'htmx/form.html', context)

    def form_valid(self, form):
        super().form_valid(form)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "object": self.object,
            "form": form
        }
        return TemplateResponse(self.request, 'htmx/create.html', context)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(self.request, 'htmx/form.html', context)


class HTMXPartidaArancelariaDeleteView(generic.DeleteView):
    model = models.PartidaArancelaria
    success_url = reverse_lazy("MiCasillero_PartidaArancelaria_htmx_list")

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse()
