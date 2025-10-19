# Development Plan: Liquidation and Invoicing System

## 1. Goal

To create a robust system for calculating the final costs of a shipment, generating a professional PDF invoice, and tracking the payment status. This system is the financial core of the application and is critical for the business's revenue cycle.

## 2. User Stories

* **As a staff member, I want the system to automatically calculate the final costs of a shipment** based on the actual measurements and any other adjustments, so that I can avoid manual calculations and reduce errors.
* **As a staff member, I want to be able to review and approve the final costs** before an invoice is generated, so that I can ensure accuracy.
* **As a staff member, I want to be able to generate a professional PDF invoice** for each shipment, so that I can provide the client with a clear and official document for payment.
* **As a staff member, I want to be able to mark an invoice as paid** so that I can keep track of the payment status of each shipment.
* **As a client, I want to be able to view and download my final invoice** from my account dashboard, so that I have a record of my expenses.

## 3. Proposed Solution

I will develop a comprehensive liquidation and invoicing system that is tightly integrated with the shipment tracking module. The system will automatically calculate the final costs of a shipment based on the actual measurements entered by the staff. Once the costs are reviewed and approved, the system will generate a professional PDF invoice using the data from the `Factura` model. The invoice will be available for clients to download from their dashboard, and staff will be able to update the payment status.

## 4. Development Tasks & Subtasks

### **Phase 1: Backend (2 weeks)**

* **Task 1.1: Implement the Final Cost Calculation Logic**
  * Subtask 1.1.1: Implement the logic to calculate the final costs based on the actual measurements of the package.
  * Subtask 1.1.2: Implement a workflow for staff to review and approve the final costs.
  * Subtask 1.1.3: Once approved, populate the `Factura` model with the final, accurate data.
* **Task 1.2: Implement PDF Invoice Generation**
  * Subtask 1.2.1: Use a library like ReportLab or WeasyPrint to generate a PDF invoice from the data in the `Factura` model.
  * Subtask 1.2.2: The invoice should include a detailed breakdown of costs, including the variance from the original estimate.
* **Task 1.3: Implement Payment Status Tracking**
  * Subtask 1.3.1: Create a view for staff to mark an invoice as paid.
  * Subtask 1.3.2: Update the `Factura` model to include the payment status.

### **Phase 2: Frontend (2 weeks)**

* **Task 2.1: Create the Client-Facing Invoice Interface**
  * Subtask 2.1.1: Allow clients to view and download their final invoices from their dashboard.
  * Subtask 2.1.2: Display the payment status on the invoice.
* **Task 2.2: Create the Staff-Facing Invoicing Interface**
  * Subtask 2.2.1: Create an interface for reviewing and approving liquidations.
  * Subtask 2.2.2: Implement the generation of PDF invoices from the liquidation data.
  * Subtask 2.2.3: Add a feature for staff to mark invoices as paid.
