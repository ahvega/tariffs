# **Development Plan: Elasticsearch Admin Management**

## **1. Goal**

To create a secure, user-friendly interface within the Django admin that allows administrators to perform essential Elasticsearch maintenance tasks without needing direct server access or command-line knowledge. This will streamline the management of the search index and AI-related data processing.

## **2. User Stories**

* **As an administrator, I want to view the health and status of the Elasticsearch cluster and the `partidas_arancelarias` index** so that I can quickly assess the state of the search system.
* **As an administrator, I want to trigger a full rebuild of the search index** so that I can ensure the search data is perfectly synchronized with the database after major data imports or updates.
* **As an administrator, I want to be able to delete and then re-populate the search index** so that I can perform a clean reset if I suspect data corruption or inconsistencies.
* **As an administrator, I want to initiate the AI keyword generation process for all tariff items** so that I can enrich the search index with new, relevant keywords to improve search accuracy.
* **As an administrator, I want to see the progress and status of long-running tasks** (like index rebuilding and keyword generation) so that I am informed about the state of the background processes.

## **3. Proposed Solution**

I will develop a custom admin view within the Django admin site, accessible only to superusers. This view will serve as a central dashboard for all Elasticsearch-related tasks. The interface will provide:

1. **Status Dashboard:** A read-only section displaying key metrics about the Elasticsearch cluster and the `partidas_arancelarias` index (e.g., cluster health, number of documents, index size).
2. **Management Actions:** A set of buttons that trigger the underlying management commands (`search_index --rebuild`, `generate_search_keywords`, etc.).
3. **Background Task Handling:** To prevent the admin interface from freezing or timing out during long-running operations, all management tasks will be executed asynchronously using a background task queue. I will use Celery with Redis for this, as it's a robust and common solution in the Django ecosystem.
4. **Real-time Feedback:** The interface will provide feedback on the status of any running tasks, indicating whether a task is pending, in progress, or has completed (successfully or with an error).

## **4. Development Tasks & Subtasks**

---

### **Phase 1: Backend Foundation & Task Asynchrony (2 days)**

* **Task 1.1: Create a New Django App for Admin Tooling**
  * Subtask 1.1.1: Generate a new app named `admintools` using `python manage.py startapp admintools`.
  * Subtask 1.1.2: Add `admintools` to the `INSTALLED_APPS` list in `backend/sicargabox/SicargaBox/settings.py`.

* **Task 1.2: Integrate Celery for Background Task Processing**
  * Subtask 1.2.1: Add `celery` and `redis` to the `requirements.txt` file and install them.
  * Subtask 1.2.2: Configure Celery in `settings.py` to use Redis as the message broker and result backend.
  * Subtask 1.2.3: Create the `celery.py` module within the `SicargaBox` project directory to define the Celery application instance.
  * Subtask 1.2.4: Create a `tasks.py` file inside the new `admintools` app to define the asynchronous tasks.

* **Task 1.3: Wrap Management Commands in Celery Tasks**
  * Subtask 1.3.1: In `admintools/tasks.py`, create a Celery task `rebuild_elasticsearch_index` that programmatically calls the `search_index --rebuild` management command.
  * Subtask 1.3.2: Create a Celery task `delete_elasticsearch_index` that calls `search_index --delete`.
  * Subtask 1.3.3: Create a Celery task `populate_elasticsearch_index` that calls `search_index --populate`.
  * Subtask 1.3.4: Create a Celery task `generate_ai_keywords` that calls the `generate_search_keywords` management command. Ensure this task can accept parameters like the AI provider.

---

### **Phase 2: Django Admin Interface (2-3 days)**

* **Task 2.1: Develop a Custom Admin View**
  * Subtask 2.1.1: In `admintools/admin.py`, create a new `AdminSite` or use a proxy model to register a custom admin page without a corresponding database model.
  * Subtask 2.1.2: Define a URL for this custom view in a new `admintools/urls.py` and include it in the main `SicargaBox/urls.py`.
  * Subtask 2.1.3: Create the view logic in `admintools/views.py` that will render the management dashboard. This view will be protected to only allow superuser access.
  * Subtask 2.1.4: Design an HTML template (`templates/admin/elasticsearch_management.html`) for the dashboard.

* **Task 2.2: Implement the Admin Dashboard UI**
  * Subtask 2.2.1: In the template, create a "Status" section. The view will fetch and display Elasticsearch cluster health, index name, number of indexed documents, and other relevant stats.
  * Subtask 2.2.2: Add a set of clearly labeled buttons for each management action: "Rebuild Index," "Delete Index," "Populate Index," and "Generate AI Keywords."
  * Subtask 2.2.3: Implement the view logic so that clicking these buttons dispatches the corresponding Celery tasks defined in Phase 1.
  * Subtask 2.2.4: Use the Django messages framework to provide immediate feedback to the admin (e.g., "Index rebuild task has been started.").

* **Task 2.3: Implement Task Status Display**
  * Subtask 2.3.1: Create a new API endpoint that can be polled to get the status of a Celery task by its ID.
  * Subtask 2.3.2: Use JavaScript in the admin template to poll this endpoint after a task is initiated.
  * Subtask 2.3.3: Update the UI to show the live status of the task (e.g., "PENDING," "IN_PROGRESS," "SUCCESS," "FAILURE") and display a progress bar if possible.

---

### **Phase 3: Testing & Documentation (1 day)**

* **Task 3.1: End-to-End Testing**
  * Subtask 3.1.1: Manually test each button in the admin interface to confirm that the correct Celery task is triggered and completes successfully.
  * Subtask 3.1.2: Verify that the Elasticsearch status information is accurate and updates correctly.
  * Subtask 3.1.3: Test the real-time task status display to ensure it provides correct and timely feedback.
  * Subtask 3.1.4: Write unit tests for the Celery tasks to ensure they call the management commands correctly.

* **Task 3.2: Update Project Documentation**
  * Subtask 3.2.1: Add a new section to the `GEMINI.md` file titled "Elasticsearch Admin Management," explaining the purpose and usage of the new interface.
  * Subtask 3.2.2: Add a brief mention of this feature in the main `README.md` for project contributors.

---

## **5. Estimated Timeline**

* **Phase 1 (Backend & Celery):** 2 days
* **Phase 2 (Admin Interface):** 2-3 days
* **Phase 3 (Testing & Docs):** 1 day
* **Total Estimated Time:** 5-6 days

## **6. Success Metrics**

* **Functionality:** All Elasticsearch management tasks can be successfully initiated and completed from the Django admin.
* **Usability:** The interface is intuitive for a non-technical administrator, with clear labels and feedback.
* **Performance:** Long-running tasks execute in the background without impacting the responsiveness of the admin site.
* **Reliability:** The status of the Elasticsearch cluster and background tasks is accurately reported.

## **7. Continuous Learning and Index Enrichment**

This feature is the cornerstone of the AI-powered search system. It's designed to make the system smarter over time by learning from user interactions.

### **7.1. Data Capture**

* **Workflow Step:** This process is initiated during the quote creation workflow.
* **Trigger:** When a user selects a `PartidaArancelaria` (tariff classification) for an `Articulo` (item) based on their own description, this action is captured.
* **Data Stored:** The system will store a mapping between the user's original item description and the selected `PartidaArancelaria`. This is handled by the `ItemPartidaMapping` model, as detailed in the `AI_SEMANTIC_MATCHING_DESIGN.md` file.

### **7.2. Index Enrichment**

* **Process:** Instead of updating the search index in real-time (which could impact performance), a periodic background task will be used.
* **Task:** A Celery task will run on a schedule (e.g., nightly or weekly) to process the new `ItemPartidaMapping` records.
* **Logic:** The task will aggregate the new mappings, identify frequently used item descriptions for specific tariff items, and add these descriptions to the `search_keywords` field of the corresponding `PartidaArancelaria` records.
* **Outcome:** Over time, the search index will be enriched with a growing list of real-world, user-provided keywords, making it much more likely that future users will find the correct tariff item quickly and accurately.
