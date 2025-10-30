# User Dashboard and Envío Workflow Enhancement Plan

## Problem Statement

### Current Workflow Issues

**Critical Gap Identified**: The current shipping request flow assumes tracking number and invoice are immediately available, but the actual user journey is:

1. ✅ User calculates quote
2. ✅ User accepts quote and "reserves" shipping request
3. ❌ **GAP**: User makes purchase with US provider (external, takes time)
4. ❌ **GAP**: User waits for provider to ship package (1-5 days)
5. ❌ **GAP**: Provider sends tracking number via email
6. ❌ **MISSING**: User needs to return and update pending envío with tracking/invoice

**Current Implementation Problem**: Form requires tracking number and invoice immediately, blocking envío creation.

### Additional Issues

- Using `nombre_corto` instead of full name for shipping address
- No user dashboard to manage pending envíos
- No way to update envíos after initial creation
- No visibility into user's envíos, cotizaciones, or account

---

## Solution Overview

### Phase 1: Immediate Fixes (Critical - Today)

1. **Fix Shipping Address Name**
   - Use `first_name + last_name` instead of `nombre_corto`
   - Ensures full legal name appears on Miami address

2. **Make Tracking/Invoice Optional**
   - Remove `required` attribute from tracking number input
   - Remove `required` attribute from invoice file input
   - Allow envío creation in "Pending Documentation" state

3. **Update Backend Validation**
   - Make `tracking_number_original` optional in serializer
   - Make `factura_compra` optional in serializer
   - Add new envío status: `Documentación Pendiente`

### Phase 2: Envío Update Workflow (High Priority - This Week)

1. **Create Envío Update Page**
   - Route: `/envio/[id]/actualizar`
   - Allow users to add/update tracking number
   - Allow users to upload/replace invoice
   - Only accessible by envío owner

2. **Update Envío API Endpoint**
   - PATCH `/api/shipping/update/[id]/`
   - Fields: tracking_number_original, factura_compra
   - Automatically change status from "Documentación Pendiente" to "Solicitado"

3. **Envío Status Flow Enhancement**

   ```bash
   Documentación Pendiente → (user adds docs) → Solicitado → Recibido en Miami → ...
   ```

### Phase 3: User Dashboard (High Priority - This Week)

**Route**: `/dashboard`

**Tab Structure**:

- 📦 **Mis Envíos** - View and manage shipping requests
- 📋 **Mis Cotizaciones** - Saved quotes
- 🧾 **Mis Facturas** - Invoices and liquidations
- 👤 **Mi Cuenta** - Profile and settings

**Header Component Update**:

**Logged Out State**:

```bash
🔒 [Lock Icon] ▼
  ├─ Ingresar
  └─ Registrarse
```

**Logged In State**:

```bash
👤 [Person Icon] - {First Name} ▼
  ├─ Mi Dashboard
  ├─ Mi Cuenta
  ├─ Cambiar Contraseña
  └─ Cerrar Sesión
```

---

## Detailed Implementation Plan

### Phase 1: Immediate Fixes

#### 1.1 Update Shipping Address to Use Full Name

**Files to modify**:

- `backend/sicargabox/api/auth_views.py` - Return full name in `/api/auth/me/`

**Change**:

```python
user_data['cliente'] = {
    'id': cliente.id,
    'codigo_cliente': cliente.codigo_cliente,
    'nombre_completo': f"{user.first_name} {user.last_name}",  # NEW
}
```

**Frontend updates**:

- `frontend/public_web/app/bienvenida/page.tsx`
- `frontend/public_web/components/QuoteResults.tsx`

#### 1.2 Make Tracking/Invoice Optional

**Backend** - `backend/sicargabox/api/serializers.py`:

```python
class ShippingRequestSerializer(serializers.Serializer):
    tracking_number_original = serializers.CharField(required=False, allow_blank=True)
    factura_compra = serializers.FileField(required=False, allow_null=True)
    # ... rest of fields
```

**Backend** - `backend/sicargabox/api/shipping_views.py`:

- Check if tracking/invoice provided
- If not, set envío status to "Documentación Pendiente"
- If yes, set status to "Solicitado"

**Frontend** - `frontend/public_web/app/envio/crear/page.tsx`:

- Remove `required` from tracking number input
- Remove `required` from invoice file input
- Update validation logic
- Update success message to indicate next steps

#### 1.3 Add New Envío Status

**Backend** - `backend/sicargabox/MiCasillero/models.py`:

```python
ESTADO_CHOICES = [
    ('Documentación Pendiente', 'Documentación Pendiente'),  # NEW
    ('Solicitado', 'Solicitado'),
    ('Recibido en Miami', 'Recibido en Miami'),
    # ... rest
]
```

**Migration required**: Yes

---

### Phase 2: Envío Update Workflow

#### 2.1 Backend Update Endpoint

**New file**: `backend/sicargabox/api/shipping_views.py` (extend existing)

```python
@extend_schema(tags=["Shipping"])
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_shipping_request(request, envio_id):
    """Update pending shipping request with tracking/invoice."""
    try:
        envio = Envio.objects.get(id=envio_id, cliente__user=request.user)
    except Envio.DoesNotExist:
        return Response(
            {"error": "Envío no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Update tracking number if provided
    if 'tracking_number_original' in request.data:
        envio.tracking_number_original = request.data['tracking_number_original']

    # Update invoice if provided
    if request.FILES.get('factura_compra'):
        envio.factura_compra = request.FILES['factura_compra']

    # If both tracking and invoice now exist, change status
    if envio.tracking_number_original and envio.factura_compra:
        envio.estado_envio = 'Solicitado'

    envio.save()

    return Response(EnvioSerializer(envio).data, status=status.HTTP_200_OK)
```

**URL**: Add to `backend/sicargabox/api/urls.py`:

```python
path("shipping/update/<uuid:envio_id>/", shipping_views.update_shipping_request, name="shipping_update"),
```

#### 2.2 Frontend Update Page

**New file**: `frontend/public_web/app/envio/[id]/actualizar/page.tsx`

**Features**:

- Fetch existing envío details
- Show current status
- Form to add/update tracking number
- Form to upload/replace invoice
- Submit button to update
- Success message and redirect to dashboard

#### 2.3 API Client Method

**File**: `frontend/public_web/lib/api.ts`

```typescript
async updateShippingRequest(
  envioId: string,
  updates: {
    tracking_number?: string;
    factura_compra?: File;
  },
  accessToken: string
): Promise<ShippingResponse | null> {
  // Implementation
}
```

---

### Phase 3: User Dashboard

#### 3.1 Dashboard Layout

**New file**: `frontend/public_web/app/dashboard/page.tsx`

**Structure**:

```tsx
<DashboardLayout>
  <Header /> {/* Updated with person icon menu */}
  <TabNavigation>
    <Tab>Mis Envíos</Tab>
    <Tab>Mis Cotizaciones</Tab>
    <Tab>Mis Facturas</Tab>
    <Tab>Mi Cuenta</Tab>
  </TabNavigation>
  <TabContent>
    {/* Render active tab content */}
  </TabContent>
</DashboardLayout>
```

#### 3.2 Mis Envíos Tab

**Features**:

- List all user's envíos with status badges
- Filter by status (Todos, Documentación Pendiente, En Tránsito, Entregado)
- Action buttons:
  - "Agregar Documentos" (if status = Documentación Pendiente)
  - "Ver Detalles" (all envíos)
  - "Rastrear" (if status >= Recibido en Miami)

**Data Structure**:

```typescript
interface EnvioListItem {
  id: string;
  tracking_sicarga: string;
  tracking_original?: string;
  estado: string;
  descripcion: string;
  costo_total: number;
  fecha_solicitud: string;
  has_invoice: boolean;
  needs_documentation: boolean;
}
```

#### 3.3 Mis Cotizaciones Tab

**Features**:

- List saved quotes (from sessionStorage or new Quote model)
- Show: producto, peso, costo estimado, fecha
- Actions:
  - "Crear Envío" - Convert quote to envío
  - "Recotizar" - Recalculate with current rates
  - "Eliminar"

**Future Enhancement**: Persist quotes to database with Quote model

#### 3.4 Mis Facturas Tab

**Features**:

- List finalized invoices/liquidations
- Show: envío, costo estimado, costo final, fecha
- Actions:
  - "Ver PDF" - Download invoice
  - "Ver Detalles" - Show breakdown

**Note**: Requires Phase 1.4 (Liquidation & Invoicing) completion

#### 3.5 Mi Cuenta Tab

**Features**:

- Display user info (name, email, cliente code)
- Edit profile form
- Change password form
- Email preferences (future)

#### 3.6 Header Component Enhancement

**File**: `frontend/public_web/components/Header.tsx`

**Current**:

```tsx
Hola, {name} | Cerrar Sesión
```

**New**:

```tsx
// Logged out
<LockIcon /> ▼
  <Menu>
    <MenuItem href="/login">Ingresar</MenuItem>
    <MenuItem href="/register">Registrarse</MenuItem>
  </Menu>

// Logged in
<PersonIcon /> {firstName} ▼
  <Menu>
    <MenuItem href="/dashboard">Mi Dashboard</MenuItem>
    <MenuItem href="/dashboard?tab=cuenta">Mi Cuenta</MenuItem>
    <MenuItem href="/cambiar-password">Cambiar Contraseña</MenuItem>
    <Divider />
    <MenuItem href="/logout">Cerrar Sesión</MenuItem>
  </Menu>
```

---

## Backend API Endpoints Summary

### New Endpoints Needed

1. **PATCH `/api/shipping/update/<uuid:envio_id>/`**
   - Update pending envío with tracking/invoice
   - Authentication required
   - Owner validation

2. **GET `/api/shipping/list/`**
   - List user's envíos with filtering
   - Query params: status, page, page_size
   - Returns: paginated envío list

3. **GET `/api/quotes/list/`** (Future)
   - List user's saved quotes
   - Requires Quote model creation

4. **GET `/api/facturas/list/`** (Future)
   - List user's invoices
   - Requires Factura completion

5. **PATCH `/api/auth/profile/`**
   - Update user profile
   - Fields: first_name, last_name, email

6. **POST `/api/auth/change-password/`**
   - Change user password
   - Fields: old_password, new_password

---

## Database Changes Required

### 1. New Envío Status

**Migration**: Add "Documentación Pendiente" to ESTADO_CHOICES

### 2. Make Fields Optional

**Migration**: Modify Envío model

- `tracking_number_original`: `null=True, blank=True`
- `factura_compra`: `null=True, blank=True`

### 3. Future: Quote Model (Optional)

If we want to persist quotes instead of using sessionStorage:

```python
class QuoteSaved(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descripcion_original = models.CharField(max_length=500)
    partida_arancelaria = models.ForeignKey(PartidaArancelaria, on_delete=models.PROTECT)
    valor_declarado = models.DecimalField(max_digits=10, decimal_places=2)
    peso = models.DecimalField(max_digits=10, decimal_places=2)
    # ... calculation results
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    convertido_a_envio = models.BooleanField(default=False)
```

---

## Implementation Sprints

### Sprint 1: Critical Fixes (Today - 2 hours)

**Tasks**:

1. ✅ Update auth endpoint to return full name
2. ✅ Make tracking/invoice optional in frontend
3. ✅ Make tracking/invoice optional in backend
4. ✅ Add "Documentación Pendiente" status
5. ✅ Update shipping request creation logic
6. ✅ Update success message with next steps
7. ✅ Test complete flow

**Deliverable**: Users can create envíos without immediate tracking/invoice

### Sprint 2: Envío Update Workflow (1 day)

**Tasks**:

1. Create backend update endpoint
2. Create frontend update page
3. Add API client method
4. Add "Agregar Documentos" button in relevant places
5. Test update flow
6. Update documentation

**Deliverable**: Users can return later to add tracking/invoice

### Sprint 3: Dashboard Foundation (2 days)

**Tasks**:

1. Create dashboard layout
2. Create tab navigation component
3. Implement "Mis Envíos" tab with list
4. Create envío list API endpoint
5. Add status badges and filters
6. Add action buttons
7. Update header component
8. Test navigation flow

**Deliverable**: Working dashboard with envíos management

### Sprint 4: Dashboard Completion (2 days)

**Tasks**:

1. Implement "Mis Cotizaciones" tab (sessionStorage-based)
2. Implement "Mi Cuenta" tab
3. Create profile update API
4. Create password change flow
5. Add icons and menu interactions
6. Mobile responsiveness
7. Test all dashboard features

**Deliverable**: Complete user dashboard

### Sprint 5: Polish & Future Features (1 day)

**Tasks**:

1. Add "Mis Facturas" tab placeholder
2. Improve error handling
3. Add loading states
4. Add empty states for lists
5. Add confirmation dialogs
6. Update documentation
7. End-to-end testing

**Deliverable**: Production-ready dashboard

---

## User Journey - Updated

### New User Flow

1. Anonymous user calculates quote
2. User clicks "Aceptar Cotización"
3. User registers → Welcome page shows Miami address
4. User creates "reservation" envío (without tracking/invoice)
5. **System shows**: "Tu solicitud ha sido guardada. Realiza tu compra y regresa a agregar el número de rastreo."
6. User makes purchase with US provider
7. User waits for tracking email from provider
8. User returns to dashboard → "Mis Envíos"
9. User clicks "Agregar Documentos" on pending envío
10. User enters tracking number and uploads invoice
11. Envío status changes to "Solicitado"
12. User can track progress from dashboard

### Returning User Flow

1. User logs in
2. User calculates quote
3. User sees expandable Miami address in results
4. User creates "reservation" envío
5. **System shows**: "Tu solicitud ha sido guardada. Ve a tu Dashboard para agregar documentación cuando esté lista."
6. User navigates to Dashboard
7. [Rest same as new user from step 8]

---

## UI/UX Improvements

### Success Messages

**After creating pending envío**:

```bash
✅ ¡Solicitud de Envío Creada!

Número de Rastreo SicargaBox: SC-XXXXXXXXXX

📝 Próximos Pasos:
1. Realiza tu compra con tu proveedor en USA usando tu dirección de Miami
2. Espera el correo con el número de rastreo
3. Regresa a tu Dashboard para agregar la documentación

[Ir a Mi Dashboard] [Crear Nueva Cotización]
```

### Envío Status Badges

```tsx
<Badge color="yellow">Documentación Pendiente</Badge>
<Badge color="blue">Solicitado</Badge>
<Badge color="purple">Recibido en Miami</Badge>
<Badge color="green">Entregado</Badge>
```

### Empty States

**No envíos yet**:

```bash
📦 No tienes envíos todavía

Crea tu primera cotización y solicita un envío para comenzar.

[Ir al Cotizador]
```

**No pending documentation**:

```bash
✅ Todos tus envíos están actualizados

No tienes envíos pendientes de documentación.
```

---

## Testing Checklist

### Phase 1: Critical Fixes

- [ ] User can create envío without tracking
- [ ] User can create envío without invoice
- [ ] Envío saves with "Documentación Pendiente" status
- [ ] Success message shows next steps
- [ ] Full name appears in shipping address (not nombre_corto)

### Phase 2: Update Workflow

- [ ] User can access update page from dashboard
- [ ] User can add tracking number to pending envío
- [ ] User can upload invoice to pending envío
- [ ] Status changes to "Solicitado" when both added
- [ ] Only envío owner can update
- [ ] 404 for non-existent envíos

### Phase 3: Dashboard

- [ ] Dashboard accessible only when logged in
- [ ] Tabs switch correctly
- [ ] Envíos list shows all user's envíos
- [ ] Filters work correctly
- [ ] Action buttons appear based on status
- [ ] Header menu works for logged in/out states
- [ ] Mobile responsive

---

## Success Metrics

- ✅ Users can complete envío creation without provider data (100% success rate)
- ✅ Users return to add documentation (track adoption rate)
- ✅ Dashboard reduces support questions about "Where's my package?" (measure tickets)
- ✅ Average time from quote to complete envío creation < 5 minutes
- ✅ User satisfaction with new workflow (user feedback)

---

## Future Enhancements

1. **Email Notifications**
   - Remind users to add documentation after 24h
   - Notify when envío status changes

2. **Quote Persistence**
   - Save quotes to database
   - Allow quote expiration (30 days)
   - Quote versioning for rate changes

3. **Envío Templates**
   - Save common purchase patterns
   - Quick-create from template

4. **Bulk Operations**
   - Create multiple envíos at once
   - Batch documentation upload

5. **Mobile App**
   - Native dashboard experience
   - Push notifications for status changes
