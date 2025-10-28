from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from MiCasillero.models import (
    PartidaArancelaria,
    Cliente,
    Cotizacion,
    Articulo,
    ParametroSistema,
)


class PartidaArancelariaViewSetTestCase(TestCase):
    """
    Test suite for PartidaArancelaria API endpoints.

    Tests CRUD operations, filtering, searching, and the custom search_products endpoint.
    """

    def setUp(self):
        """Set up test client and create test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        # Create test partidas arancelarias
        self.partida1 = PartidaArancelaria.objects.create(
            item_no="1234.56.78.90",
            descripcion="Test Product Electronics",
            partida_arancelaria="1234.56.78.90",
            impuesto_dai=Decimal("0.10"),
            impuesto_isc=Decimal("0.00"),
            impuesto_ispc=Decimal("0.00"),
            impuesto_isv=Decimal("0.15"),
            courier_category="ALLOWED",
            restrictions=["Test restriction"],
            package_type="CAJA_REGULAR",
            requires_special_handling=False,
            search_keywords=["electronics", "test", "product"],
        )

        self.partida2 = PartidaArancelaria.objects.create(
            item_no="9876.54.32.10",
            descripcion="Restricted Chemical Product",
            partida_arancelaria="9876.54.32.10",
            impuesto_dai=Decimal("0.15"),
            impuesto_isc=Decimal("0.05"),
            impuesto_ispc=Decimal("0.00"),
            impuesto_isv=Decimal("0.15"),
            courier_category="RESTRICTED",
            restrictions=["Requires special permit", "Hazardous material"],
            package_type="CAJA_ESPECIAL",
            requires_special_handling=True,
            search_keywords=["chemical", "restricted"],
        )

    def test_list_partidas_requires_authentication(self):
        """Test that listing partidas requires authentication."""
        response = self.client.get("/api/partidas-arancelarias/")
        # DRF returns 403 Forbidden when using SessionAuthentication for unauthenticated requests
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_partidas_authenticated(self):
        """Test listing partidas with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/partidas-arancelarias/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_partida(self):
        """Test retrieving a single partida."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/partidas-arancelarias/{self.partida1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["item_no"], "1234.56.78.90")
        self.assertEqual(response.data["courier_category"], "ALLOWED")

    def test_filter_by_courier_category(self):
        """Test filtering partidas by courier category."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            "/api/partidas-arancelarias/?courier_category=RESTRICTED"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["item_no"], "9876.54.32.10")

    def test_search_by_descripcion(self):
        """Test searching partidas by description."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/partidas-arancelarias/?search=Electronics")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["item_no"], "1234.56.78.90")

    def test_search_products_endpoint_public(self):
        """Test that search_products endpoint is publicly accessible."""
        response = self.client.get(
            "/api/partidas-arancelarias/search_products/?query=Electronics"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_search_products_without_query(self):
        """Test search_products endpoint without query parameter."""
        response = self.client.get("/api/partidas-arancelarias/search_products/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_ordering_by_dai(self):
        """Test ordering partidas by DAI tax rate."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/partidas-arancelarias/?ordering=impuesto_dai")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(results[0]["item_no"], "1234.56.78.90")  # 0.10
        self.assertEqual(results[1]["item_no"], "9876.54.32.10")  # 0.15


class ClienteViewSetTestCase(TestCase):
    """
    Test suite for Cliente API endpoints.

    Tests CRUD operations, filtering, and searching for customers.
    """

    def setUp(self):
        """Set up test client and create test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        # Create required system parameter for Cliente codigo generation
        ParametroSistema.objects.create(
            nombre_parametro="Prefijo del Código de Cliente",
            valor="CLI",
            tipo_dato="STRING",
        )

        # Create test cliente
        self.cliente = Cliente.objects.create(
            user=self.user,
            nombres="Juan",
            apellidos="Perez",
            telefono="12345678",
            correo_electronico="juan.perez@example.com",
            direccion="Calle Principal 123",
            ciudad="Tegucigalpa",
            departamento="Francisco Morazan",
            pais="Honduras",
        )

    def test_list_clientes_requires_authentication(self):
        """Test that listing clientes requires authentication."""
        response = self.client.get("/api/clientes/")
        # DRF returns 403 Forbidden when using SessionAuthentication for unauthenticated requests
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_clientes_authenticated(self):
        """Test listing clientes with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/clientes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_retrieve_cliente(self):
        """Test retrieving a single cliente."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/clientes/{self.cliente.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombres"], "Juan")
        self.assertEqual(response.data["apellidos"], "Perez")

    def test_create_cliente(self):
        """Test creating a new cliente."""
        # Create a new user for the new cliente (OneToOneField constraint)
        new_user = User.objects.create_user(
            username="mariauser", password="testpass123", email="maria@example.com"
        )
        self.client.force_authenticate(user=new_user)
        data = {
            "nombres": "Maria",
            "apellidos": "Lopez",
            "telefono": "87654321",
            "correo_electronico": "maria.lopez@example.com",
            "direccion": "Avenida Central 456",
            "ciudad": "San Pedro Sula",
            "departamento": "Cortes",
            "pais": "Honduras",
        }
        response = self.client.post("/api/clientes/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nombres"], "Maria")
        self.assertIn("codigo_cliente", response.data)  # Auto-generated

    def test_search_clientes_by_name(self):
        """Test searching clientes by name."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/clientes/?search=Juan")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["nombres"], "Juan")

    def test_update_cliente(self):
        """Test updating a cliente."""
        self.client.force_authenticate(user=self.user)
        data = {
            "nombres": "Juan",
            "apellidos": "Perez Martinez",
            "telefono": "12345678",
            "correo_electronico": "juan.perez@example.com",
            "direccion": "Calle Principal 123",
            "ciudad": "Tegucigalpa",
            "departamento": "Francisco Morazan",
            "pais": "Honduras",
        }
        response = self.client.put(f"/api/clientes/{self.cliente.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["apellidos"], "Perez Martinez")


class CotizacionViewSetTestCase(TestCase):
    """
    Test suite for Cotizacion API endpoints.

    Tests CRUD operations, filtering, and permission-based access.
    """

    def setUp(self):
        """Set up test client and create test data."""
        self.client = APIClient()
        self.regular_user = User.objects.create_user(
            username="regular", password="testpass123", email="regular@example.com"
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            password="testpass123",
            email="staff@example.com",
            is_staff=True,
        )

        # Create required system parameter for Cliente codigo generation
        ParametroSistema.objects.create(
            nombre_parametro="Prefijo del Código de Cliente",
            valor="CLI",
            tipo_dato="STRING",
        )

        # Create test clientes
        self.cliente1 = Cliente.objects.create(
            nombres="Cliente",
            apellidos="Uno",
            telefono="12345678",
            correo_electronico="cliente1@example.com",
            user=self.regular_user,
        )

        self.cliente2 = Cliente.objects.create(
            user=self.staff_user,
            nombres="Cliente",
            apellidos="Dos",
            telefono="87654321",
            correo_electronico="cliente2@example.com",
        )

        # Create test cotizaciones
        self.cotizacion1 = Cotizacion.objects.create(
            cliente=self.cliente1, estado="Pendiente"
        )

        self.cotizacion2 = Cotizacion.objects.create(
            cliente=self.cliente2, estado="Aceptada"
        )

    def test_list_cotizaciones_requires_authentication(self):
        """Test that listing cotizaciones requires authentication."""
        response = self.client.get("/api/cotizaciones/")
        # DRF returns 403 Forbidden when using SessionAuthentication for unauthenticated requests
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_sees_only_own_cotizaciones(self):
        """Test that regular users only see their own cotizaciones."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/cotizaciones/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.cotizacion1.id)

    def test_staff_user_sees_all_cotizaciones(self):
        """Test that staff users see all cotizaciones."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get("/api/cotizaciones/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_create_cotizacion(self):
        """Test creating a new cotizacion."""
        self.client.force_authenticate(user=self.regular_user)
        data = {"cliente": self.cliente1.id, "estado": "Pendiente"}
        response = self.client.post("/api/cotizaciones/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("fecha_creacion", response.data)  # Auto-generated

    def test_filter_cotizaciones_by_estado(self):
        """Test filtering cotizaciones by estado."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get("/api/cotizaciones/?estado=Aceptada")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["estado"], "Aceptada")


class ArticuloViewSetTestCase(TestCase):
    """
    Test suite for Articulo API endpoints.

    Tests CRUD operations, automatic tax calculation, and filtering.
    """

    def setUp(self):
        """Set up test client and create test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        # Create required system parameter for Cliente codigo generation
        ParametroSistema.objects.create(
            nombre_parametro="Prefijo del Código de Cliente",
            valor="CLI",
            tipo_dato="STRING",
        )

        # Create test partida
        self.partida = PartidaArancelaria.objects.create(
            item_no="1234.56.78.90",
            descripcion="Test Product",
            partida_arancelaria="1234.56.78.90",
            impuesto_dai=Decimal("0.10"),
            impuesto_isc=Decimal("0.05"),
            impuesto_ispc=Decimal("0.00"),
            impuesto_isv=Decimal("0.15"),
        )

        # Create test cliente and cotizacion
        self.cliente = Cliente.objects.create(
            user=self.user,
            nombres="Test",
            apellidos="User",
            telefono="12345678",
            correo_electronico="test@example.com",
        )

        self.cotizacion = Cotizacion.objects.create(
            cliente=self.cliente, estado="PENDIENTE"
        )

    def test_list_articulos_requires_authentication(self):
        """Test that listing articulos requires authentication."""
        response = self.client.get("/api/articulos/")
        # DRF returns 403 Forbidden when using SessionAuthentication for unauthenticated requests
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_articulo_calculates_taxes(self):
        """Test that creating an articulo automatically calculates taxes."""
        self.client.force_authenticate(user=self.user)
        data = {
            "cotizacion": self.cotizacion.id,
            "valor_articulo": "1000.00",
            "largo": "10.0",
            "ancho": "10.0",
            "alto": "10.0",
            "peso": "5.0",
            "partida_arancelaria": self.partida.id,
        }
        response = self.client.post("/api/articulos/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that taxes were calculated
        self.assertIn("impuesto_dai", response.data)
        self.assertIn("impuesto_isc", response.data)
        self.assertIn("impuesto_isv", response.data)
        self.assertIn("impuesto_total", response.data)

        # Verify calculated values are not empty
        self.assertIsNotNone(response.data["impuesto_total"])

    def test_articulo_has_readonly_tax_fields(self):
        """Test that tax fields are read-only."""
        self.client.force_authenticate(user=self.user)
        data = {
            "cotizacion": self.cotizacion.id,
            "valor_articulo": "1000.00",
            "largo": "10.0",
            "ancho": "10.0",
            "alto": "10.0",
            "peso": "5.0",
            "partida_arancelaria": self.partida.id,
            "impuesto_dai": "9999.99",  # Try to override
            "impuesto_total": "9999.99",  # Try to override
        }
        response = self.client.post("/api/articulos/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify that the override was ignored and taxes were calculated
        self.assertNotEqual(str(response.data["impuesto_dai"]), "9999.99")

    def test_filter_articulos_by_cotizacion(self):
        """Test filtering articulos by cotizacion."""
        self.client.force_authenticate(user=self.user)

        # Create an articulo
        articulo = Articulo.objects.create(
            cotizacion=self.cotizacion,
            valor_articulo=Decimal("1000.00"),
            largo=Decimal("10.0"),
            ancho=Decimal("10.0"),
            alto=Decimal("10.0"),
            peso=Decimal("5.0"),
            partida_arancelaria=self.partida,
        )

        response = self.client.get(f"/api/articulos/?cotizacion={self.cotizacion.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], articulo.id)

    def test_articulo_calculated_fields(self):
        """Test that peso_volumetrico and peso_a_usar are calculated."""
        self.client.force_authenticate(user=self.user)
        data = {
            "cotizacion": self.cotizacion.id,
            "valor_articulo": "1000.00",
            "largo": "30.0",
            "ancho": "30.0",
            "alto": "30.0",
            "peso": "2.0",  # Actual weight is less than volumetric
            "partida_arancelaria": self.partida.id,
        }
        response = self.client.post("/api/articulos/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that calculated fields are present
        self.assertIn("peso_volumetrico", response.data)
        self.assertIn("peso_a_usar", response.data)
