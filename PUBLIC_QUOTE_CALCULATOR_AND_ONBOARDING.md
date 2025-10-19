# Development Plan: Public Quote Calculator & Onboarding

## 1. Goal

To create a seamless and intuitive entry point for both new and existing clients, allowing them to get instant shipping quotes and easily transition to creating a shipping request. This module is critical for user acquisition and conversion.

## 2. User Stories

* **As an anonymous user, I want to be able to calculate the estimated cost of shipping an item** so that I can get a quick idea of the cost without having to create an account.
* **As an anonymous user, after getting a quote, I want a clear call-to-action to create an account or log in** so that I can proceed with my shipping request.
* **As a new user, I want a simple and quick registration process** so that I can create an account and accept my quote without unnecessary friction.
* **As an existing user, I want to be able to log in easily from the quote page** so that I can accept my quote and associate it with my account.
* **As a user, I want the system to provide intelligent suggestions for the tariff classification of my item** so that I don't have to be an expert in customs regulations.

## 3. Proposed Solution

I will develop a public-facing quote calculator that does not require authentication. This calculator will use the AI-powered semantic search to suggest tariff classifications. After a quote is generated, the user will be presented with clear options to either register for a new account or log in to an existing one. The registration process will be streamlined to minimize the number of required fields. Upon successful login or registration, the user will be redirected to a page where they can accept the quote and complete the shipping request.

## 4. Development Tasks & Subtasks

### **Phase 1: Public Quote Calculator (1-2 weeks)**

* **Task 1.1: Create the Public Quote Calculator View**
  * Subtask 1.1.1: Create a new view in `MiCasillero/views.py` for the public quote calculator.
  * Subtask 1.1.2: Create a URL for the view in `MiCasillero/urls.py`.
  * Subtask 1.1.3: Create a template for the calculator.
* **Task 1.2: Implement the Quote Calculation Logic**
  * Subtask 1.2.1: Implement the backend logic to calculate the shipping costs based on the item's value, dimensions, weight, and tariff classification.
  * Subtask 1.2.2: Integrate the AI-powered semantic search to provide tariff classification suggestions.
* **Task 1.3: Implement Session-Based Quote Storage**
  * Subtask 1.3.1: Use Django's session framework to store the quote details for anonymous users.
  * Subtask 1.3.2: When a user logs in or registers, associate the session quote with their account.

### **Phase 2: Client Onboarding (1-2 weeks)**

* **Task 2.1: Streamline the Registration Process**
  * Subtask 2.1.1: Create a new, simplified registration form with minimal fields (name, email, phone, address).
  * Subtask 2.1.2: Implement the logic to automatically generate a client code upon registration.
  * Subtask 2.1.3: Implement email verification (optional but recommended).
* **Task 2.2: Implement the Login and Redirect Flow**
  * Subtask 2.2.1: Create a login form that can be accessed from the quote page.
  * Subtask 2.2.2: Upon successful login or registration, redirect the user to a page where they can accept the quote.
* **Task 2.3: Implement the Quote Acceptance Workflow**
  * Subtask 2.3.1: Create a view to handle the acceptance of a quote.
  * Subtask 2.3.2: When a quote is accepted, create a new `Envio` record with the status "Solicitado".
  * Subtask 2.3.3: Send a confirmation email to the client with the new shipping request details.
