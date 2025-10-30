# Shipping Address Information & Authentication Fix Plan

## Overview

This document outlines the implementation plan for improving the shipping request workflow by displaying Miami warehouse address information at appropriate points in the user journey, and fixing authentication issues.

---

## Phase 1: Fix Authentication Issues (Priority: CRITICAL)

### 1.1 Create Logout Functionality

**Problem**: No logout page exists, preventing users from clearing invalid/expired JWT tokens.

**Implementation**:
- Create logout page at `/logout`
- Implement NextAuth `signOut()` functionality
- Clear session and redirect to login page
- Add logout button to header/navigation

**Files to modify**:
- `frontend/public_web/app/logout/page.tsx` (NEW)
- `frontend/public_web/components/Header.tsx` or navigation component

### 1.2 Debug and Fix Token Issue

**Current Error**: `"Token is invalid or expired"` when submitting shipping request

**Root Cause**: User logged in before authentication code was updated to store JWT tokens in session.

**Solution**:
- Users must logout and login again to get fresh tokens
- Add debug logging to verify token storage
- Test token persistence across navigation

**Verification**:
```typescript
// Check in browser console:
console.log('Session:', session);
console.log('Access token:', (session as any).accessToken);
```

---

## Phase 2: Enhance ParametroSistema Model

### 2.1 Add Description Field

**Current Structure**:
```python
class ParametroSistema(models.Model):
    nombre_parametro = models.CharField(max_length=50, unique=True)
    valor = models.CharField(max_length=255)
    tipo_dato = models.CharField(max_length=10, choices=TIPO_DATO_CHOICES)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
```

**Enhancement**:
Add `descripcion` field to provide context for each parameter.

```python
descripcion = models.TextField(blank=True, help_text="Descripción del parámetro")
```

**Migration Required**: Yes

**Files to modify**:
- `backend/sicargabox/MiCasillero/models.py`
- Create migration: `python manage.py makemigrations`
- Apply migration: `python manage.py migrate`

### 2.2 Add Required System Parameters

**New Parameters to Create via Django Admin**:

| Nombre Parámetro | Tipo Dato | Valor Ejemplo | Descripción |
|------------------|-----------|---------------|-------------|
| `Dirección Consolidador` | STRING | 1234 NW 72nd Ave, Suite 100<br>Miami, FL 33126, USA | Dirección del consolidador en Miami para recepción de paquetes |
| `Dirección Oficina` | STRING | Col. Alameda, Calle Principal #123<br>Tegucigalpa, Honduras | Dirección de la oficina para recoger paquetes |
| `WhatsApp Oficina` | STRING | +504 9999-9999 | Número de WhatsApp de la oficina para contacto |
| `Entrega a Domicilio` | BOOLEAN | false | Indica si la empresa ofrece servicio de entrega a domicilio |

**Note**: Use existing `ParametroSistema.objects.get_valor("parameter_name")` pattern

---

## Phase 3: Create API Endpoint for Frontend Access

### 3.1 Backend API Implementation

**Endpoint**: `GET /api/parametros/publicos/`

Returns system parameters needed for frontend (read-only, authenticated users only).

**Response Format**:
```json
{
  "direccion_consolidador": "1234 NW 72nd Ave...",
  "direccion_oficina": "Col. Alameda...",
  "whatsapp_oficina": "+504 9999-9999",
  "entrega_a_domicilio": false
}
```

**Files to create/modify**:
- `backend/sicargabox/api/views.py` - Add `get_parametros_publicos()` view
- `backend/sicargabox/api/urls.py` - Add route
- `backend/sicargabox/api/serializers.py` - Add `ParametrosPublicosSerializer` (optional)

**Implementation**:
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parametros_publicos(request):
    """Get public system parameters for frontend use."""
    parametros = {
        'direccion_consolidador': ParametroSistema.objects.get_valor('Dirección Consolidador'),
        'direccion_oficina': ParametroSistema.objects.get_valor('Dirección Oficina'),
        'whatsapp_oficina': ParametroSistema.objects.get_valor('WhatsApp Oficina'),
        'entrega_a_domicilio': ParametroSistema.objects.get_valor('Entrega a Domicilio'),
    }
    return Response({'success': True, 'data': parametros})
```

### 3.2 Frontend API Client

**Files to modify**:
- `frontend/public_web/lib/api.ts` - Add `getParametrosSistema()` method

**Interface**:
```typescript
export interface ParametrosSistema {
  direccion_consolidador: string;
  direccion_oficina: string;
  whatsapp_oficina: string;
  entrega_a_domicilio: boolean;
}

async getParametrosSistema(accessToken: string): Promise<ParametrosSistema | null> {
  // Implementation
}
```

---

## Phase 4: Shipping Address Composition & Display

### 4.1 Address Composition Logic

**Format**:
```
{Client Name} - {Client Code}
{Consolidator Address}
```

**Example**:
```
Juan Pérez - CLI-001234
1234 NW 72nd Ave, Suite 100
Miami, FL 33126, USA
```

**Utility Function**:
```typescript
// frontend/public_web/lib/addressUtils.ts
export function composeShippingAddress(
  clientName: string,
  clientCode: string,
  consolidatorAddress: string
): string {
  return `${clientName} - ${clientCode}\n${consolidatorAddress}`;
}
```

### 4.2 Client Name Retrieval

**Options**:
1. From session: `session.user.name`
2. From Cliente API: Need to add endpoint to get current user's Cliente info
3. From auth response: Already includes `first_name` and `last_name`

**Recommended**: Add to session during login
```typescript
// In auth.ts callback
session.user.clientCode = "CLI-XXXXXX"; // Fetch from Cliente
```

---

## Phase 5: Display Points for Shipping Address

### 5.1 New Client Flow - Welcome Page

**When**: After successful registration
**Location**: New page at `/bienvenida`

**Components**:
- Welcome message
- "Tu Casillero en Miami" section
- Composed address display (copyable)
- "Copiar Dirección" button with clipboard API
- Instructions: "Usa esta dirección como Dirección de Envío en tus compras online"
- Continue button → `/cotizador`

**Files to create**:
- `frontend/public_web/app/bienvenida/page.tsx`
- `frontend/public_web/components/ShippingAddressDisplay.tsx` (reusable)

**Redirect Logic**:
Modify registration page to redirect to `/bienvenida` instead of `/cotizador` or `/envio/crear`.

### 5.2 Returning Client Flow - Quote Results

**When**: After calculating quote (on `/cotizador`)
**Location**: Within quote results section, before "Aceptar Cotización" button

**Implementation**:
- Add expandable/collapsible section
- Title: "📦 Dirección de tu Casillero en Miami"
- Show composed address with copy button
- Reminder text: "Asegúrate de usar esta dirección al realizar tu compra con tu proveedor en USA"
- Auto-expand on first view (use localStorage flag)
- Stays collapsed on subsequent views

**Files to modify**:
- `frontend/public_web/components/QuoteResults.tsx`
- Add `ShippingAddressDisplay` component

**Layout**:
```
┌─────────────────────────────────────┐
│ Quote Results Summary               │
│ (existing content)                  │
├─────────────────────────────────────┤
│ ▼ Dirección de tu Casillero        │ ← Expandable
│   [Address with copy button]        │
│   Reminder text...                  │
└─────────────────────────────────────┘
│ [Aceptar Cotización] button         │
└─────────────────────────────────────┘
```

---

## Phase 6: Pickup Information Display

### 6.1 Shipping Request Page - Default Pickup Flow

**Condition**: `entrega_a_domicilio` = `false` (default)

**Changes to `/envio/crear`**:
1. **Hide delivery address fields** (direccion, ciudad, departamento)
2. **Show pickup information box**:

```
┌─────────────────────────────────────┐
│ 📍 Recoger en Oficina              │
│                                     │
│ Dirección Oficina                   │
│ [Office Address from parameter]     │
│                                     │
│ 📱 WhatsApp: [+504 9999-9999]      │ ← Clickable
│                                     │
│ Cómo llegar:                        │
│ [🗺️ Google Maps] [🧭 Waze]        │ ← Buttons
└─────────────────────────────────────┘
```

**Files to modify**:
- `frontend/public_web/app/envio/crear/page.tsx`

### 6.2 Map Integration

**Google Maps URL**:
```typescript
const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(officeAddress)}`;
```

**Waze URL**:
```typescript
const wazeUrl = `https://waze.com/ul?q=${encodeURIComponent(officeAddress)}`;
```

**WhatsApp Link**:
```typescript
const whatsappUrl = `https://wa.me/${whatsappNumber.replace(/[^0-9]/g, '')}`;
```

### 6.3 Future - Home Delivery Option

**Condition**: `entrega_a_domicilio` = `true`

**When Implemented**:
- Add checkbox: "□ Requiero entrega a domicilio"
- If checked: Show delivery address fields
- If unchecked: Show pickup info (default)

**Implementation Priority**: Future enhancement, not in current scope

---

## Phase 7: Additional Fixes

### 7.1 Format Peso to 2 Decimal Places

**Status**: ✅ Already fixed

```typescript
{quote.peso_a_usar.toFixed(2)} lb
```

### 7.2 Improved Error Display

**Status**: ✅ Already fixed

- Parse JSON error responses
- Show user-friendly messages
- Display in red error box at top of form

---

## Implementation Order

### Sprint 1: Authentication & Infrastructure (1-2 days)
1. ✅ Fix peso formatting
2. ✅ Improve error handling
3. 🔄 Create logout page
4. 🔄 Fix token debugging
5. 🔄 Add descripcion field to ParametroSistema (migration)
6. 🔄 Create system parameters via admin
7. 🔄 Create API endpoint for parameters

### Sprint 2: Address Display - New Clients (1 day)
8. Create address composition utility
9. Create ShippingAddressDisplay component
10. Create welcome page (`/bienvenida`)
11. Update registration redirect logic

### Sprint 3: Address Display - Returning Clients (1 day)
12. Fetch cliente info for current user
13. Add address section to QuoteResults
14. Implement expandable/collapsible UI

### Sprint 4: Pickup Information (1 day)
15. Update shipping request page
16. Hide delivery fields when pickup-only
17. Show office address and contact info
18. Add map/navigation buttons

### Sprint 5: Testing & Polish (1 day)
19. End-to-end workflow testing
20. Edge case handling
21. Mobile responsiveness
22. Documentation updates

---

## Technical Details

### Backend Files to Modify/Create
- ✅ `backend/sicargabox/MiCasillero/models.py` - Add descripcion field
- ✅ `backend/sicargabox/api/views.py` - Add parametros endpoint
- ✅ `backend/sicargabox/api/urls.py` - Add route
- ⚠️  Migration file (auto-generated)

### Frontend Files to Modify/Create
- 🔄 `frontend/public_web/app/logout/page.tsx` (NEW)
- 🔄 `frontend/public_web/app/bienvenida/page.tsx` (NEW)
- 🔄 `frontend/public_web/lib/addressUtils.ts` (NEW)
- 🔄 `frontend/public_web/components/ShippingAddressDisplay.tsx` (NEW)
- ✅ `frontend/public_web/app/envio/crear/page.tsx` - Add pickup info
- ✅ `frontend/public_web/components/QuoteResults.tsx` - Add address section
- ✅ `frontend/public_web/lib/api.ts` - Add parametros method
- ✅ `frontend/public_web/app/register/page.tsx` - Update redirect

---

## User Workflow Summary

### New User Journey
1. User visits `/cotizador` (anonymous)
2. User calculates quote
3. User clicks "Aceptar Cotización"
4. User is redirected to `/register`
5. User registers → Redirected to `/bienvenida`
6. **Welcome page shows Miami address** 📦
7. User clicks Continue → `/envio/crear`
8. **Pickup info displayed** (no delivery fields)
9. User fills tracking, uploads invoice
10. Shipping request created ✅

### Returning User Journey
1. User logs in
2. User visits `/cotizador`
3. User calculates quote
4. **Quote results show expandable Miami address section** 📦
5. User reviews address reminder
6. User clicks "Aceptar Cotización" → `/envio/crear`
7. **Pickup info displayed**
8. User fills tracking, uploads invoice
9. Shipping request created ✅

---

## Success Metrics

- ✅ Users can logout and clear invalid tokens
- ✅ New users see Miami address immediately after registration
- ✅ Returning users see address reminder in quote results
- ✅ Clear pickup instructions displayed (no confusion about delivery)
- ✅ One-click navigation to office via Google Maps/Waze
- ✅ Successful shipping request creation with proper authentication

---

## Notes

- All ParametroSistema access uses existing pattern: `ParametroSistema.objects.get_valor("param_name")`
- No changes to core ParametroSistema manager logic needed
- System parameters are managed via Django Admin (no code changes after setup)
- Frontend fetches parameters once and caches during session
- Home delivery feature left as future enhancement (controlled by boolean parameter)

---

## Dependencies

- None (uses existing infrastructure)
- Optional: Clipboard API polyfill for older browsers
- Optional: Add loading states for parameter fetching
