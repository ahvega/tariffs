from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm as UserRegisterForm
from django.contrib.auth.forms import AuthenticationForm as LoginForm
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from guardian.decorators import permission_required_or_403
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import assign_perm
import json

from .forms import ClienteForm, CotizacionForm, ArticuloForm, \
    PartidaArancelariaForm, ParametroSistemaForm, AlertaForm, \
    EnvioForm, FacturaForm
from .models import Cliente, Cotizacion, Articulo, PartidaArancelaria, \
    ParametroSistema, Alerta, Envio, Factura
from django.urls import reverse_lazy
from elasticsearch_dsl import Q as ES_Q
from .documents import PartidaArancelariaDocument


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        cliente_form = ClienteForm(request.POST)
        if user_form.is_valid() and cliente_form.is_valid():
            user = user_form.save()
            cliente = cliente_form.save(commit=False)
            cliente.user = user
            cliente.save()

            # Obtener el grupo UsuariosClientes, crearlo si no existe
            grupo, created = Group.objects.get_or_create(name='UsuariosClientes')
            # Agregar el usuario creado al grupo UsuariosClientes
            grupo.user_set.add(user)

            # Automatically log in the user
            login(request, user)

            # Check if there's a quote in session
            if 'current_quote' in request.session:
                # Redirect to accept_quote to create the cotizacion
                return redirect('accept_quote')

            return HttpResponse('¡Registro exitoso! <a href="/">Ir al inicio</a></p>'
                                '<p>Tu código de cliente es: <strong>{}</strong></p>'.format(cliente.codigo_cliente))
    else:
        user_form = UserRegisterForm()
        cliente_form = ClienteForm()
    return render(request, 'registration/register.html', {'user_form': user_form, 'cliente_form': cliente_form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Check if there's a quote in session that needs to be associated
            if 'current_quote' in request.session:
                # Redirect to accept_quote to create the cotizacion
                return redirect('accept_quote')

            # Redirigir al usuario a la página de inicio o a la página desde la que inició sesión
            next_url = request.GET.get('next', '/')
            if 'register' in next_url:
                next_url = '/'
            return redirect(next_url)

        else:
            # Mensaje de error
            return render(request, 'partials/error_message.html',
                          {'message': 'Usuario o contraseña incorrectos'},
                          content_type='text/html')

    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def create_cotizacion(request):
    cliente = request.user.cliente
    if request.method == 'POST':
        cotizacion = Cotizacion.objects.create(cliente=cliente)
        assign_perm('change_cotizacion', request.user, cotizacion)
        assign_perm('delete_cotizacion', request.user, cotizacion)
        assign_perm('view_cotizacion', request.user, cotizacion)
        return redirect('add_articulo', cotizacion_id=cotizacion.id)
    return render(request, 'create_cotizacion.html')


def actualizar_cotizacion(cotizacion):
    pass


def formatear_numero(valor, decimales=2, dolar=False, porcentaje=False):
    format_string = f"{{:.{decimales}f}}"
    formatted_value = format_string.format(valor)
    if dolar:
        formatted_value = "$" + formatted_value
    if porcentaje:
        formatted_value += "%"
    return formatted_value


def cotizar(request):
    if request.method == 'POST':
        form = ArticuloForm(request.POST)
        if form.is_valid():
            articulo = form.save(commit=False)
            articulo.calcular_impuestos()
            valor_cif = articulo.valor_articulo + articulo.costo_transporte

            cargos_totales = articulo.impuesto_total + articulo.costo_transporte
            total_incluido_valor = articulo.valor_articulo + cargos_totales

            # Store quote in session for anonymous users
            quote_data = {
                'valor_articulo': float(articulo.valor_articulo),
                'peso': float(articulo.peso),
                'largo': float(articulo.largo) if articulo.largo else None,
                'ancho': float(articulo.ancho) if articulo.ancho else None,
                'alto': float(articulo.alto) if articulo.alto else None,
                'unidad_peso': articulo.unidad_peso,
                'descripcion_original': articulo.descripcion_original,
                'partida_arancelaria_id': articulo.partida_arancelaria.id if articulo.partida_arancelaria else None,
                'impuesto_dai': float(articulo.impuesto_dai),
                'impuesto_isc': float(articulo.impuesto_isc),
                'impuesto_ispc': float(articulo.impuesto_ispc),
                'impuesto_isv': float(articulo.impuesto_isv),
                'impuesto_total': float(articulo.impuesto_total),
                'costo_transporte': float(articulo.costo_transporte),
                'total': float(total_incluido_valor),
            }
            request.session['current_quote'] = quote_data
            request.session.modified = True

            context = {
                'valor_declarado': articulo.valor_articulo,
                'valor_cif': valor_cif,
                'peso': articulo.peso,
                'peso_a_usar': articulo.peso_a_usar,
                'costo_por_libra': formatear_numero(articulo.costo_flete_por_lb, 2, True),
                'impuesto_dai': articulo.impuesto_dai,
                'impuesto_isc': articulo.impuesto_isc,
                'impuesto_ispc': articulo.impuesto_ispc,
                'impuestos_importacion': articulo.impuesto_total - articulo.impuesto_isv,
                'impuesto_isv': articulo.impuesto_isv,
                'costo_transporte': articulo.costo_transporte,
                'cargos_totales': cargos_totales,
                'total_incluido_valor': total_incluido_valor,
                'porcentaje_dai': formatear_numero(articulo.porcentaje_dai, 2, False, True),
                'porcentaje_isc': formatear_numero(articulo.porcentaje_isc, 2, False, True),
                'porcentaje_ispc': formatear_numero(articulo.porcentaje_ispc, 2, False, True),
                'porcentaje_isv': formatear_numero(articulo.porcentaje_isv, 2, False, True),
                'partida_item_no': articulo.partida_item_no,
                'partida_descripcion': articulo.partida_arancelaria,
                'partida_arancelaria_numero': articulo.partida_numero,
                'descripcion_original': articulo.descripcion_original,
                'articulo': articulo,
                'is_authenticated': request.user.is_authenticated,
            }
            return render(request, 'partials/resumen.html', context)
        else:
            return render(request, 'partials/invalid-form.html', {'form': form})
    else:
        error = "No es un GET"
        return render(request, 'partials/noget-error.html', {'error': error})


@csrf_exempt
def cotizar_json(request):
    """
    JSON API endpoint for quote calculation (for Next.js frontend)
    """
    if request.method == 'POST':
        try:
            # Parse JSON body
            data = json.loads(request.body)

            # Create form data with defaults for optional fields
            form_data = {
                'valor_articulo': data.get('valor'),
                'peso': data.get('peso'),
                'unidad_peso': data.get('unidad_peso', 'lb'),
                'largo': data.get('largo', 1),  # Default to 1 if not provided
                'ancho': data.get('ancho', 1),  # Default to 1 if not provided
                'alto': data.get('alto', 1),    # Default to 1 if not provided
                'descripcion_original': data.get('descripcion_original', ''),
                'partida_arancelaria': data.get('partida_arancelaria'),
            }

            # Validate form
            form = ArticuloForm(form_data)
            if form.is_valid():
                articulo = form.save(commit=False)
                articulo.calcular_impuestos()

                valor_cif = articulo.valor_articulo + articulo.costo_transporte
                cargos_totales = articulo.impuesto_total + articulo.costo_transporte
                total_incluido_valor = articulo.valor_articulo + cargos_totales

                # Store quote in session for anonymous users
                quote_data = {
                    'valor_articulo': float(articulo.valor_articulo),
                    'peso': float(articulo.peso),
                    'largo': float(articulo.largo) if articulo.largo else None,
                    'ancho': float(articulo.ancho) if articulo.ancho else None,
                    'alto': float(articulo.alto) if articulo.alto else None,
                    'unidad_peso': data.get('unidad_peso', 'lb'),  # Get from request data
                    'descripcion_original': articulo.descripcion_original,
                    'partida_arancelaria_id': articulo.partida_arancelaria.id if articulo.partida_arancelaria else None,
                    'impuesto_dai': float(articulo.impuesto_dai),
                    'impuesto_isc': float(articulo.impuesto_isc),
                    'impuesto_ispc': float(articulo.impuesto_ispc),
                    'impuesto_isv': float(articulo.impuesto_isv),
                    'impuesto_total': float(articulo.impuesto_total),
                    'costo_transporte': float(articulo.costo_transporte),
                    'total': float(total_incluido_valor),
                }
                request.session['current_quote'] = quote_data
                request.session.modified = True

                # Return JSON response
                response_data = {
                    'success': True,
                    'data': {
                        'valor_declarado': float(articulo.valor_articulo),
                        'valor_cif': float(valor_cif),
                        'peso': float(articulo.peso),
                        'peso_a_usar': float(articulo.peso_a_usar),
                        'costo_por_libra': str(articulo.costo_flete_por_lb),
                        'impuesto_dai': float(articulo.impuesto_dai),
                        'impuesto_isc': float(articulo.impuesto_isc),
                        'impuesto_ispc': float(articulo.impuesto_ispc),
                        'impuestos_importacion': float(articulo.impuesto_total - articulo.impuesto_isv),
                        'impuesto_isv': float(articulo.impuesto_isv),
                        'costo_transporte': float(articulo.costo_transporte),
                        'cargos_totales': float(cargos_totales),
                        'total_incluido_valor': float(total_incluido_valor),
                        'porcentaje_dai': str(articulo.porcentaje_dai),
                        'porcentaje_isc': str(articulo.porcentaje_isc),
                        'porcentaje_ispc': str(articulo.porcentaje_ispc),
                        'porcentaje_isv': str(articulo.porcentaje_isv),
                        'partida_item_no': articulo.partida_item_no,
                        'partida_descripcion': str(articulo.partida_arancelaria),
                        'partida_arancelaria_numero': articulo.partida_numero,
                        'descripcion_original': articulo.descripcion_original,
                    }
                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    else:
        return JsonResponse({
            'success': False,
            'error': 'Only POST method allowed'
        }, status=405)


@login_required
@permission_required_or_403('change_cotizacion', (Cotizacion, 'id', 'cotizacion_id'))
def add_articulo(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    permitir_consolidacion = ParametroSistema.objects.get_valor("Permitir Consolidación de Paquetes")

    if request.method == 'POST':
        form = ArticuloForm(request.POST)
        if form.is_valid():
            articulo = form.save(commit=False)
            articulo.cotizacion = cotizacion

            # Calcular los impuestos
            articulo.calcular_impuestos()

            articulo.save()
            # Actualizar cotizacion con cálculos
            actualizar_cotizacion(cotizacion)
            if not permitir_consolidacion:
                return redirect('view_cotizacion', cotizacion_id=cotizacion.id)
            return redirect('add_articulo', cotizacion_id=cotizacion.id)
    else:
        form = ArticuloForm()

    # Si la consolidación no está permitida y ya hay un artículo en la cotización, redirigir a la vista de la cotización
    if not permitir_consolidacion and cotizacion.articulos.count() > 0:
        return redirect('view_cotizacion', cotizacion_id=cotizacion.id)

    return render(request, 'add_articulo.html', {
        'form': form,
        'cotizacion': cotizacion,
        'permitir_consolidacion': permitir_consolidacion
    })


@login_required
@permission_required_or_403('view_cotizacion', (Cotizacion, 'id', 'cotizacion_id'))
def view_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    articulos = cotizacion.articulos.all()
    return render(request, 'view_cotizacion.html', {'cotizacion': cotizacion, 'articulos': articulos})


def partida_arancelaria_autocomplete(request):
    if 'q' in request.GET:
        q = request.GET['q']
        partidas = PartidaArancelaria.objects.filter(descripcion__icontains=q).order_by('descripcion')
        results = [{'id': partida.id, 'text': partida} for partida in partidas]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})


def cotizador_view(request):
    # Filtrar partidas arancelarias permitidas
    partidas = PartidaArancelaria.objects.filter(
        courier_category='ALLOWED'
    ).order_by('descripcion')
    
    # Crear el formulario con las partidas filtradas
    form = ArticuloForm()
    form.fields['partida_arancelaria'].queryset = partidas
    
    # Agregar información de contexto
    context = {
        'form': form,
        'total_partidas': partidas.count(),
        'total_restricted': PartidaArancelaria.objects.filter(courier_category='RESTRICTED').count(),
        'total_prohibited': PartidaArancelaria.objects.filter(courier_category='PROHIBITED').count()
    }
    
    # Preparar datos para el select2
    partidas_data = []
    for p in partidas:
        partidas_data.append({
            'id': p.id,
            'codigo': p.item_no,
            'descripcion': p.descripcion,
            'keywords': p.search_keywords,
            'search_text': f"{p.item_no} {p.descripcion} {' '.join(p.search_keywords if p.search_keywords else [])}"
        })
    
    # Modificar las opciones del select para incluir los datos de búsqueda
    form.fields['partida_arancelaria'].widget.attrs.update({
        'class': 'select2',
        'data-partidas': json.dumps(partidas_data),
        'placeholder': 'Busque o seleccione una partida arancelaria',
        'aria-label': 'Seleccione la partida arancelaria que mejor corresponda a su producto'
    })
    
    # Mejorar la ayuda visual para la descripción original
    form.fields['descripcion_original'].widget.attrs.update({
        'class': 'mt-1 block w-full p-2 border rounded',
        'placeholder': 'Ingrese la descripción exacta del producto como aparece en su factura de compra'
    })
    
    return render(request, 'cotizador.html', context)


def buscar_partidas(request):
    """Vista para búsqueda de partidas usando Elasticsearch"""
    q = request.GET.get('q', '')
    results = []

    if len(q) >= 3:  # Mínimo 3 caracteres para buscar
        try:
            # Construir la consulta Elasticsearch
            search = PartidaArancelariaDocument.search()

            # Usar multi_match para buscar en campos relevantes con fuzziness
            query = ES_Q(
                'multi_match',
                query=q,
                fields=[
                    'item_no^3', # Dar más peso al código
                    'descripcion^2', # Peso medio a la descripción
                    'full_text_search', # Búsqueda general en texto combinado
                    'search_keywords' # Búsqueda en keywords
                ],
                fuzziness='AUTO' # Permitir errores tipográficos
            )

            search = search.query(query)

            # Limitar resultados (puedes hacerlo configurable o paginar)
            search = search[:20]

            response = search.execute()

            # Formatear resultados para Select2 AJAX
            results = [{
                'id': hit.meta.id, # Usar el ID del modelo Django original
                'text': f"{hit.item_no} - {hit.descripcion}",
                'codigo': hit.item_no,
                'descripcion': hit.descripcion,
                'keywords': list(getattr(hit, 'search_keywords', [])),  # Convert AttrList to list
                'score': hit.meta.score # Puntaje de relevancia de ES
            } for hit in response]

        except Exception as e:
            # Manejo básico de errores (idealmente loggear el error)
            print(f"Error searching Elasticsearch: {e}")
            pass # Devolver lista vacía en caso de error

    return JsonResponse({'results': results})


def accept_quote(request):
    """Vista para aceptar una cotización y redirigir a registro/login"""
    # Check if there's a quote in the session
    if 'current_quote' not in request.session:
        return redirect('cotizador')

    # If user is authenticated, create cotizacion and redirect to shipping request
    if request.user.is_authenticated:
        quote_data = request.session.get('current_quote')

        try:
            # Get or create cliente
            cliente = Cliente.objects.get(user=request.user)

            # Create cotizacion
            cotizacion = Cotizacion.objects.create(cliente=cliente)
            assign_perm('change_cotizacion', request.user, cotizacion)
            assign_perm('delete_cotizacion', request.user, cotizacion)
            assign_perm('view_cotizacion', request.user, cotizacion)

            # Create articulo from quote data
            partida = PartidaArancelaria.objects.get(id=quote_data['partida_arancelaria_id'])
            articulo = Articulo.objects.create(
                cotizacion=cotizacion,
                valor_articulo=quote_data['valor_articulo'],
                peso=quote_data['peso'],
                largo=quote_data.get('largo'),
                ancho=quote_data.get('ancho'),
                alto=quote_data.get('alto'),
                unidad_peso=quote_data['unidad_peso'],
                descripcion_original=quote_data['descripcion_original'],
                partida_arancelaria=partida,
            )
            articulo.calcular_impuestos()
            articulo.save()

            # Clear quote from session
            del request.session['current_quote']
            request.session.modified = True

            # Redirect to view cotizacion
            return redirect('view_cotizacion', cotizacion_id=cotizacion.id)

        except Cliente.DoesNotExist:
            # User doesn't have a cliente profile, redirect to complete registration
            return redirect('register')
        except Exception as e:
            print(f"Error creating cotizacion: {e}")
            return redirect('cotizador')

    # If user is not authenticated, redirect to registration page
    return redirect('register')


# Las vistas de clase ya tienen la implementación de PermissionRequiredMixin


class AlertaListView(PermissionRequiredMixin, generic.ListView):
    model = Alerta
    form_class = AlertaForm
    permission_required = 'view_alerta'


class AlertaCreateView(PermissionRequiredMixin, generic.CreateView):
    model = Alerta
    form_class = AlertaForm
    permission_required = 'add_alerta'


class AlertaDetailView(PermissionRequiredMixin, generic.DetailView):
    model = Alerta
    form_class = AlertaForm
    permission_required = 'view_alerta'


class AlertaUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = Alerta
    form_class = AlertaForm
    pk_url_kwarg = "pk"
    permission_required = 'change_alerta'


class AlertaDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Alerta
    success_url = reverse_lazy("MiCasillero_Alerta_list")
    permission_required = 'delete_alerta'


class ArticuloListView(PermissionRequiredMixin, generic.ListView):
    model = Articulo
    form_class = ArticuloForm
    permission_required = 'view_articulo'


class ArticuloCreateView(PermissionRequiredMixin, generic.CreateView):
    model = Articulo
    form_class = ArticuloForm
    permission_required = 'add_articulo'


class ArticuloDetailView(PermissionRequiredMixin, generic.DetailView):
    model = Articulo
    form_class = ArticuloForm
    permission_required = 'view_articulo'


class ArticuloUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = Articulo
    form_class = ArticuloForm
    pk_url_kwarg = "pk"
    permission_required = 'change_articulo'


class ArticuloDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Articulo
    success_url = reverse_lazy("MiCasillero_Articulo_list")
    permission_required = 'delete_articulo'


class ClienteListView(PermissionRequiredMixin, generic.ListView):
    model = Cliente
    form_class = ClienteForm
    permission_required = 'view_cliente'


class ClienteCreateView(PermissionRequiredMixin, generic.CreateView):
    model = Cliente
    form_class = ClienteForm
    permission_required = 'add_cliente'


class ClienteDetailView(PermissionRequiredMixin, generic.DetailView):
    model = Cliente
    form_class = ClienteForm
    permission_required = 'view_cliente'


class ClienteUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = Cliente
    form_class = ClienteForm
    pk_url_kwarg = "pk"
    permission_required = 'change_cliente'


class ClienteDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Cliente
    success_url = reverse_lazy("MiCasillero_Cliente_list")
    permission_required = 'delete_cliente'


class CotizacionListView(PermissionRequiredMixin, generic.ListView):
    model = Cotizacion
    form_class = CotizacionForm
    permission_required = 'view_cotizacion'


class CotizacionCreateView(PermissionRequiredMixin, generic.CreateView):
    model = Cotizacion
    form_class = CotizacionForm
    permission_required = 'add_cotizacion'


class CotizacionDetailView(PermissionRequiredMixin, generic.DetailView):
    model = Cotizacion
    form_class = CotizacionForm
    permission_required = 'view_cotizacion'


class CotizacionUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = Cotizacion
    form_class = CotizacionForm
    pk_url_kwarg = "pk"
    permission_required = 'change_cotizacion'


class CotizacionDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Cotizacion
    success_url = reverse_lazy("MiCasillero_Cotizacion_list")
    permission_required = 'delete_cotizacion'


class EnvioListView(PermissionRequiredMixin, generic.ListView):
    model = Envio
    form_class = EnvioForm
    permission_required = 'view_envio'


class EnvioCreateView(PermissionRequiredMixin, generic.CreateView):
    model = Envio
    form_class = EnvioForm
    permission_required = 'add_envio'


class EnvioDetailView(PermissionRequiredMixin, generic.DetailView):
    model = Envio
    form_class = EnvioForm
    permission_required = 'view_envio'


class EnvioUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = Envio
    form_class = EnvioForm
    pk_url_kwarg = "pk"
    permission_required = 'change_envio'


class EnvioDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Envio
    success_url = reverse_lazy("MiCasillero_Envio_list")
    permission_required = 'delete_envio'


class FacturaListView(PermissionRequiredMixin, generic.ListView):
    model = Factura
    form_class = FacturaForm
    permission_required = 'view_factura'


class FacturaCreateView(PermissionRequiredMixin, generic.CreateView):
    model = Factura
    form_class = FacturaForm
    permission_required = 'add_factura'


class FacturaDetailView(PermissionRequiredMixin, generic.DetailView):
    model = Factura
    form_class = FacturaForm
    permission_required = 'view_factura'


class FacturaUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = Factura
    form_class = FacturaForm
    pk_url_kwarg = "pk"
    permission_required = 'change_factura'


class FacturaDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Factura
    success_url = reverse_lazy("MiCasillero_Factura_list")
    permission_required = 'delete_factura'


class PartidaArancelariaListView(PermissionRequiredMixin, generic.ListView):
    model = PartidaArancelaria
    form_class = PartidaArancelariaForm
    permission_required = 'view_partidaarancelaria'


class PartidaArancelariaCreateView(PermissionRequiredMixin, generic.CreateView):
    model = PartidaArancelaria
    form_class = PartidaArancelariaForm
    permission_required = 'add_partidaarancelaria'


class PartidaArancelariaDetailView(PermissionRequiredMixin, generic.DetailView):
    model = PartidaArancelaria
    form_class = PartidaArancelariaForm
    permission_required = 'view_partidaarancelaria'


class PartidaArancelariaUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = PartidaArancelaria
    form_class = PartidaArancelariaForm
    pk_url_kwarg = "pk"
    permission_required = 'change_partidaarancelaria'


class PartidaArancelariaDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = PartidaArancelaria
    success_url = reverse_lazy("MiCasillero_PartidaArancelaria_list")
    permission_required = 'delete_partidaarancelaria'


class ParametroSistemaListView(PermissionRequiredMixin, generic.ListView):
    model = ParametroSistema
    form_class = ParametroSistemaForm
    permission_required = 'view_parametrosistema'
    permission_object = None


class ParametroSistemaCreateView(PermissionRequiredMixin, generic.CreateView):
    model = ParametroSistema
    form_class = ParametroSistemaForm
    permission_required = 'add_parametrosistema'
    permission_object = None


class ParametroSistemaDetailView(PermissionRequiredMixin, generic.DetailView):
    model = ParametroSistema
    form_class = ParametroSistemaForm
    permission_required = 'view_parametrosistema'
    permission_object = None


class ParametroSistemaUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = ParametroSistema
    form_class = ParametroSistemaForm
    pk_url_kwarg = "pk"
    permission_required = 'change_parametrosistema'
    permission_object = None


class ParametroSistemaDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = ParametroSistema
    success_url = reverse_lazy("MiCasillero_ParametroSistema_list")
    permission_required = 'delete_parametrosistema'
    permission_object = None
