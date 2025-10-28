# --------------------------------------------------------------------------
# Django Management Command: generate_llm_keywords
# Generates search keywords for PartidaArancelaria using specified LLM provider/model.
# Includes: Parameterization, .env support, Dynamic Fallback (if DeepSeek exceeds limit),
#           Context Optimization, API Retries, DB Saving, and tqdm Progress Bar.
# --------------------------------------------------------------------------

import json
import logging
import os
from time import sleep

from django.core.management.base import BaseCommand, CommandError
from django.core.paginator import Paginator
from django.db import transaction
from dotenv import load_dotenv

# --- Model Import ---
try:
    # Asume que tu modelo está en MiCasillero.models
    from MiCasillero.models import PartidaArancelaria
except ImportError:
    raise ImportError(
        "Asegúrate de que tu modelo PartidaArancelaria esté accesible desde MiCasillero.models"
    )

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- LLM & Utility Library Imports ---
SUPPORTED_PROVIDERS = []
try:
    from openai import APIError as OpenAIAPIError
    from openai import OpenAI, RateLimitError

    SUPPORTED_PROVIDERS.extend(["openai", "deepseek"])
except ImportError:
    OpenAI = None
    logger.warning(
        "Librería 'openai' no instalada ('openai'/'deepseek' no disponibles)."
    )

try:
    import google.generativeai as genai
    from google.api_core.exceptions import (
        InternalServerError as GoogleInternalServerError,
    )
    from google.api_core.exceptions import ResourceExhausted

    SUPPORTED_PROVIDERS.append("google")
except ImportError:
    genai = None
    logger.warning(
        "Librería 'google-generativeai' no instalada ('google' no disponible)."
    )

try:
    from anthropic import Anthropic
    from anthropic import APIError as AnthropicAPIError
    from anthropic import RateLimitError as AnthropicRateLimitError

    SUPPORTED_PROVIDERS.append("anthropic")
except ImportError:
    Anthropic = None
    logger.warning("Librería 'anthropic' no instalada ('anthropic' no disponible).")

try:
    import tiktoken
except ImportError:
    tiktoken = None
    logger.warning("Librería 'tiktoken' no instalada (conteo de tokens deshabilitado).")

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None
    logger.warning("Librería 'tqdm' no instalada (no habrá barra de progreso).")

# --- LLM Constants (VERIFY LIMITS!) ---
DEEPSEEK_MODEL_NAME = "deepseek-chat"
# CONSULTA LA DOCUMENTACIÓN OFICIAL DE DEEPSEEK PARA EL LÍMITE EXACTO!
DEEPSEEK_TOKEN_LIMIT = 32000  # EJEMPLO - VERIFICAR! (Podría ser 128k para V2)

FALLBACK_PROVIDER = "google"
FALLBACK_MODEL_NAME = "gemini-1.5-pro-001"  # Recomendado por costo/contexto
FALLBACK_TOKEN_LIMIT = 1000000

MODEL_TOKEN_LIMITS = {
    "gemini-1.5-pro-latest": 1000000,
    "gemini-1.5-flash-latest": 1000000,
    "gemini-pro": 32000,
    "deepseek-chat": DEEPSEEK_TOKEN_LIMIT,
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 200000,
    "claude-3-haiku-20240307": 200000,
    "gpt-4o": 128000,
    "gpt-4-turbo": 128000,
    "gpt-3.5-turbo": 16385,
}


# --- Command Class ---
class Command(BaseCommand):
    help = "Genera keywords para N partidas usando un LLM específico, con opción de fallback y barra de progreso."

    def add_arguments(self, parser):
        parser.add_argument(
            "--provider",
            type=str,
            required=True,
            choices=SUPPORTED_PROVIDERS,
            help="Proveedor LLM primario.",
        )
        parser.add_argument(
            "--model", type=str, required=True, help="Modelo exacto a utilizar."
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Máximo de partidas a procesar (para pruebas).",
        )
        parser.add_argument(
            "--batch-size", type=int, default=10, help="Partidas por lote DB."
        )
        parser.add_argument(
            "--max-siblings-context",
            type=int,
            default=25,
            help="Max hermanos en prompt (-1 ilimitado).",
        )  # Aumentado ligeramente
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simular sin guardar ni llamar a API real.",
        )
        parser.add_argument(
            "--max-retries", type=int, default=3, help="Reintentos API."
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=2.0,
            help="Delay base reintentos (aumenta exp).",
        )  # Aumentado ligeramente
        parser.add_argument(
            "--skip-token-check",
            action="store_true",
            help="Saltar conteo/fallback por tamaño.",
        )

    # --- Helper Functions ---

    def count_tokens(self, text, skip_check=False):
        if skip_check or not tiktoken:
            return 0
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Fallo conteo tiktoken ({e}). Aproximando len/4.")
            return len(text) // 4

    def get_model_token_limit(self, model_name):
        return MODEL_TOKEN_LIMITS.get(model_name, 4096)  # Default bajo

    def initialize_client(self, provider, model_name):
        client = None
        api_key = None
        try:
            if provider == "deepseek":
                if not OpenAI:
                    raise CommandError("OpenAI lib no instalada p/ DeepSeek.")
                api_key = os.environ.get("DEEPSEEK_API_KEY")
                if not api_key:
                    raise ValueError("DEEPSEEK_API_KEY no en .env")
                client = OpenAI(base_url="https://api.deepseek.com/v1", api_key=api_key)
            elif provider == "google":
                if not genai:
                    raise CommandError("google-generativeai lib no instalada.")
                api_key = os.environ.get("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY no en .env")
                genai.configure(api_key=api_key)
                client = genai.GenerativeModel(model_name)
            elif provider == "anthropic":
                if not Anthropic:
                    raise CommandError("Anthropic lib no instalada.")
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY no en .env")
                client = Anthropic(api_key=api_key)
            elif provider == "openai":
                if not OpenAI:
                    raise CommandError("OpenAI lib no instalada.")
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY no en .env")
                client = OpenAI(api_key=api_key)
            else:
                raise ValueError(f"Proveedor '{provider}' no soportado.")
            logger.info(f"Cliente {provider}/{model_name} inicializado.")
            return client
        except (ValueError, CommandError, Exception) as e:
            logger.error(f"Error inicializando cliente {provider}/{model_name}: {e}")
            return None

    def get_context_for_partida(self, partida, max_siblings_context):
        full_desc = partida.descripcion or ""
        parts = [p.strip() for p in full_desc.split("|")]
        if not parts:
            return {}  # Manejar descripción vacía
        specific_desc = parts[-1]
        parent_desc = parts[-2] if len(parts) > 1 else None
        is_others = specific_desc.lower().startswith(("los demás", "las demás"))
        siblings, sibling_specific_descs, excluded_terms = [], [], []
        common_ancestor_desc_part = parent_desc

        if (
            common_ancestor_desc_part and len(parts) > 1
        ):  # Necesita un padre para buscar hermanos
            required_prefix = "|".join(parts[:-1]) + "|"
            try:
                potential_siblings = (
                    PartidaArancelaria.objects.filter(
                        descripcion__startswith=required_prefix
                    )
                    .exclude(id=partida.id)
                    .order_by("item_no")
                    .values_list("id", "descripcion")
                )  # Optimizar consulta

                # Filtrar por nivel jerárquico exacto (misma cantidad de '|')
                current_level_count = full_desc.count("|")
                valid_siblings_data = [
                    (sid, sdesc)
                    for sid, sdesc in potential_siblings
                    if sdesc.count("|") == current_level_count
                ]

                for _, s_desc in valid_siblings_data:
                    s_parts = [p.strip() for p in s_desc.split("|")]
                    if s_parts:
                        sibling_specific_descs.append(s_parts[-1])

                limited_sibling_specific_descs = sibling_specific_descs
                if (
                    max_siblings_context != -1
                    and len(sibling_specific_descs) > max_siblings_context
                ):
                    limited_sibling_specific_descs = sibling_specific_descs[
                        :max_siblings_context
                    ]
                    # logger.debug(f"Contexto hermanos limitado a {max_siblings_context} p/ ID {partida.id}")

                if is_others:
                    exception_term = None
                    if "excepto" in specific_desc.lower():
                        try:
                            exception_term = (
                                specific_desc.lower()
                                .split("excepto", 1)[1]
                                .strip()
                                .rstrip(".")
                            )
                        except IndexError:
                            pass
                    excluded_terms = [
                        desc
                        for desc in sibling_specific_descs
                        if not desc.lower().startswith(("los demás", "las demás"))
                    ]
                    if exception_term:
                        excluded_terms.append(exception_term)
                    excluded_terms = sorted(
                        list(
                            set(filter(None, [term.lower() for term in excluded_terms]))
                        )
                    )
            except Exception as e:
                logger.error(f"Error buscando hermanos para ID {partida.id}: {e}")
                # Continuar sin hermanos si falla la búsqueda

        context = {
            "current": {
                "codigo": partida.item_no,
                "description": full_desc,
                "specific_desc": specific_desc,
                "parent_desc": parent_desc,
                "is_others": is_others,
                "has_exception": (
                    "excepto" in specific_desc.lower() if is_others else False
                ),
                "exception_term": (
                    specific_desc.lower().split("excepto", 1)[1].strip().rstrip(".")
                    if is_others and "excepto" in specific_desc.lower()
                    else None
                ),
            },
            "sibling_specific_descs": (
                limited_sibling_specific_descs
                if "limited_sibling_specific_descs" in locals()
                else []
            ),
            "excluded_terms": excluded_terms,
        }
        return context

    def build_prompt(self, context):
        current = context.get("current", {})
        sibling_specific_descs = context.get("sibling_specific_descs", [])
        excluded_terms = context.get("excluded_terms", [])
        if not current:
            return ""  # No generar prompt si no hay datos

        prompt_lines = [
            "Eres un experto en clasificación arancelaria y comercio internacional.",
            "Tu tarea es generar un array JSON de keywords de búsqueda relevantes y DISTINTIVAS para la siguiente partida arancelaria, considerando su contexto jerárquico.",
            "### Partida Actual:",
            f"- Código: {current.get('codigo', 'N/A')}",
            f"- Descripción Completa: {current.get('description', 'N/A')}",
            f"- Descripción Específica: {current.get('specific_desc', 'N/A')}",
        ]
        if current.get("parent_desc"):
            prompt_lines.append(f"- Descripción Padre: {current['parent_desc']}")
        if sibling_specific_descs:
            prompt_lines.extend(
                [
                    f"### Contexto (Primeros {len(sibling_specific_descs)} Hermanos - Desc. Específicas):",
                    json.dumps(sibling_specific_descs, ensure_ascii=False, indent=2),
                ]
            )
        prompt_lines.append("### Instrucciones para Generar Keywords:")
        if current.get("is_others"):
            prompt_lines.append(
                f"1. **IMPORTANTE:** Esta es una partida residual ('Los demás')."
            )
            prompt_lines.append(
                f"2. Enfócate en sinónimos/variaciones relacionados con '{current.get('parent_desc', 'la categoría padre')}' que **NO** estén cubiertos por otros hermanos."
            )
            if excluded_terms:
                prompt_lines.append(
                    f"3. **EXCLUYE ESTRICTAMENTE** cualquier término relacionado con: {json.dumps(excluded_terms, ensure_ascii=False)}"
                )
        else:
            prompt_lines.append(
                f"1. **IMPORTANTE:** Esta partida se refiere específicamente a '{current.get('specific_desc', 'este item')}'."
            )
            prompt_lines.append(
                f"2. Enfócate **SOLO** en sinónimos/variaciones de '{current.get('specific_desc', 'este item')}'."
            )
            if sibling_specific_descs:
                prompt_lines.append(
                    f"3. **EVITA** keywords que describan mejor a los hermanos: {json.dumps(sibling_specific_descs, ensure_ascii=False)}"
                )
        prompt_lines.extend(
            [
                "4. Incluye términos técnicos, coloquiales y variaciones regionales si aplica.",
                "5. Piensa en términos que un usuario final usaría para buscar este producto para importar.",
                "### Formato de Salida:",
                "Responde **SOLO** con un array JSON válido y puro (lista de strings), sin texto adicional ni markdown.",
                'Ejemplo: ["keyword 1", "termino tecnico", "busqueda usuario"]',
            ]
        )
        return "\n".join(prompt_lines)

    def generate_keywords_call(
        self, prompt, provider, client, model_name, max_retries, delay
    ):
        logger.debug(f"Llamando a {provider}/{model_name}")
        RETRYABLE_ERRORS = (
            RateLimitError,
            GoogleInternalServerError,
            AnthropicRateLimitError,
            OpenAIAPIError,
            AnthropicAPIError,
            ResourceExhausted,
        )

        for attempt in range(max_retries + 1):
            try:
                response_text = ""
                completion_result = None
                if provider in ["deepseek", "openai"]:
                    if not OpenAI:
                        raise RuntimeError(f"OpenAI lib no disponible p/ {provider}")
                    completion_result = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.6,
                        max_tokens=700,
                        response_format={"type": "json_object"},
                    )  # Aumentado max_tokens
                    response_text = completion_result.choices[0].message.content.strip()
                elif provider == "google":
                    if not genai:
                        raise RuntimeError("Google GenAI lib no disponible")
                    completion_result = client.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=700,
                            temperature=0.6,
                            response_mime_type="application/json",
                        ),
                    )
                    if not completion_result.candidates:
                        logger.error(
                            f"Respuesta Gemini bloqueada/vacía: {completion_result.prompt_feedback}"
                        )
                        return []
                    response_text = completion_result.text.strip()
                elif provider == "anthropic":
                    if not Anthropic:
                        raise RuntimeError("Anthropic lib no disponible")
                    system_prompt = "Eres experto en aranceles. Responde solo con un array JSON válido."
                    completion_result = client.messages.create(
                        model=model_name,
                        system=system_prompt,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=700,
                        temperature=0.6,
                    )
                    response_text = completion_result.content[0].text.strip()

                logger.debug(f"Respuesta cruda de {provider}: {response_text}")
                try:
                    start_index = response_text.find("[")
                    end_index = response_text.rfind("]")
                    if (
                        start_index != -1
                        and end_index != -1
                        and end_index > start_index
                    ):
                        json_str = response_text[start_index : end_index + 1]
                        keywords_data = json.loads(json_str)
                        if isinstance(keywords_data, list):
                            keywords = list(
                                set(
                                    filter(
                                        None,
                                        [
                                            str(k).lower().strip()
                                            for k in keywords_data
                                            if isinstance(k, (str, int, float))
                                        ],
                                    )
                                )
                            )
                            final_keywords = keywords[
                                :100
                            ]  # Aumentado límite de keywords
                            # logger.debug(f"Keywords procesadas: {final_keywords}")
                            return final_keywords
                        else:
                            logger.warning(
                                f"JSON de {provider} no es lista: {response_text}"
                            )
                            return []
                    else:
                        logger.warning(
                            f"Array JSON '[]' no encontrado en resp de {provider}: {response_text}"
                        )
                        return []
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Error parseando JSON de {provider}: {e}\nResp: {response_text}"
                    )
                    return []
                except Exception as e:
                    logger.error(
                        f"Error procesando resp de {provider}: {e}\nResp: {response_text}"
                    )
                    return []

            except RETRYABLE_ERRORS as e:
                if attempt < max_retries:
                    wait = delay * (2**attempt)
                    logger.warning(
                        f"Error API ({provider}, {type(e).__name__}). Reintentando en {wait:.1f}s..."
                    )
                    sleep(wait)
                else:
                    logger.error(
                        f"Error API en {provider} ({type(e).__name__}) tras {max_retries} reintentos: {e}"
                    )
                    return []
            except Exception as e:
                logger.exception(
                    f"Error inesperado no recuperable llamando a {provider}: {e}"
                )
                return []
        return []

    # --- Main Handle Method ---
    def handle(self, *args, **options):
        load_dotenv()

        primary_provider = options["provider"]
        primary_model = options["model"]
        limit = options["limit"]
        batch_size = options["batch_size"]
        max_siblings = options["max_siblings_context"]
        dry_run = options["dry_run"]
        max_retries = options["max_retries"]
        delay = options["delay"]
        skip_token_check = options["skip_token_check"]

        logger.info(f"--- Iniciando Generación de Keywords ---")
        logger.info(f"Proveedor/Modelo Primario: {primary_provider}/{primary_model}")
        logger.info(f"Límite Partidas: {limit}, Batch DB: {batch_size}")
        logger.info(
            f"Dry Run: {'SI' if dry_run else 'NO'}, Reintentos API: {max_retries}"
        )
        if skip_token_check:
            logger.warning("Conteo de tokens y fallback DESHABILITADOS.")

        # --- Initialize Clients ---
        primary_client = self.initialize_client(primary_provider, primary_model)
        fallback_client = None
        if not primary_client:
            raise CommandError(
                f"Fallo al inicializar cliente primario {primary_provider}/{primary_model}."
            )
        if primary_provider == "deepseek" and not skip_token_check:
            logger.info(
                f"Inicializando fallback {FALLBACK_PROVIDER}/{FALLBACK_MODEL_NAME}..."
            )
            fallback_client = self.initialize_client(
                FALLBACK_PROVIDER, FALLBACK_MODEL_NAME
            )
            if not fallback_client:
                logger.warning(f"Fallo al inicializar fallback {FALLBACK_PROVIDER}.")

        # --- Get Partidas ---
        partidas_qs = PartidaArancelaria.objects.filter(search_keywords=[]).order_by(
            "id"
        )[:limit]
        total_partidas_to_process = len(partidas_qs)
        logger.info(
            f"Se procesarán {total_partidas_to_process} partidas con keywords vacíos."
        )
        if total_partidas_to_process == 0:
            logger.info("Nada que procesar.")
            return

        # --- Processing Loop with tqdm ---
        processed_count = 0
        progress_bar = None
        if tqdm:
            progress_bar = tqdm(
                total=total_partidas_to_process,
                desc="Generando Keywords",
                unit="partida",
                ncols=100,
            )

        paginator = Paginator(partidas_qs, batch_size)
        try:
            for page_num in paginator.page_range:
                page = paginator.page(page_num)
                partidas_batch = list(page.object_list)  # Materializar lote

                for partida in partidas_batch:
                    provider_to_use = primary_provider
                    client_to_use = primary_client
                    model_to_use = primary_model
                    use_fallback = False

                    try:  # Manejar errores específicos de procesamiento de una partida
                        context = self.get_context_for_partida(partida, max_siblings)
                        if not context.get("current"):
                            logger.error(
                                f"ID {partida.id}: No se pudo generar contexto (descripción vacía?). SALTANDO."
                            )
                            if progress_bar:
                                progress_bar.update(1)
                                continue

                        prompt = self.build_prompt(context)
                        if not prompt:
                            logger.error(
                                f"ID {partida.id}: No se pudo generar prompt. SALTANDO."
                            )
                            if progress_bar:
                                progress_bar.update(1)
                                continue

                        estimated_tokens = self.count_tokens(prompt, skip_token_check)
                        if not skip_token_check:
                            logger.debug(
                                f"ID {partida.id}: Tokens estimados={estimated_tokens}"
                            )

                        primary_token_limit = self.get_model_token_limit(primary_model)

                        # --- Fallback Logic ---
                        if (
                            primary_provider == "deepseek"
                            and not skip_token_check
                            and estimated_tokens > DEEPSEEK_TOKEN_LIMIT
                        ):
                            if (
                                fallback_client
                                and estimated_tokens <= FALLBACK_TOKEN_LIMIT
                            ):
                                provider_to_use, client_to_use, model_to_use = (
                                    FALLBACK_PROVIDER,
                                    fallback_client,
                                    FALLBACK_MODEL_NAME,
                                )
                                use_fallback = True
                                logger.warning(
                                    f"ID {partida.id}: Usando fallback {model_to_use} ({estimated_tokens} > {DEEPSEEK_TOKEN_LIMIT})"
                                )
                            else:
                                logger.error(
                                    f"ID {partida.id}: Contexto {estimated_tokens} excede DeepSeek y fallback/no disponible. SALTANDO."
                                )
                                if progress_bar:
                                    progress_bar.update(1)
                                continue
                        elif (
                            not skip_token_check
                            and estimated_tokens > primary_token_limit
                        ):
                            logger.error(
                                f"ID {partida.id}: Contexto {estimated_tokens} excede límite {primary_token_limit} de {model_to_use}. SALTANDO."
                            )
                            if progress_bar:
                                progress_bar.update(1)
                            continue

                        # --- Execution ---
                        keywords = []
                        if dry_run:
                            # logger.info(f"[DRY RUN] ID {partida.id}: Usaría {provider_to_use}/{model_to_use}")
                            keywords = ["simulado_1", "simulado_2"]
                            logger.info(
                                f"\n===> ID {partida.id} [DRY RUN]: Keywords simuladas: {json.dumps(keywords, ensure_ascii=False)}"
                            )
                            processed_count += 1
                        else:
                            keywords = self.generate_keywords_call(
                                prompt,
                                provider_to_use,
                                client_to_use,
                                model_to_use,
                                max_retries,
                                delay,
                            )
                            if keywords:
                                logger.info(
                                    f"ID {partida.id}: {len(keywords)} keywords generadas ({provider_to_use}{' F' if use_fallback else ''})."
                                )
                                logger.info(
                                    f"\n===> Keywords para ID {partida.id}: {json.dumps(keywords, ensure_ascii=False)}"
                                )
                                try:
                                    with transaction.atomic():
                                        # Re-fetch for update within transaction
                                        partida_to_update = PartidaArancelaria.objects.select_for_update().get(
                                            pk=partida.pk
                                        )
                                        partida_to_update.search_keywords = keywords
                                        partida_to_update.save()
                                        processed_count += 1
                                except Exception as db_err:
                                    logger.exception(
                                        f"Error CRÍTICO guardando ID {partida.id} en DB: {db_err}"
                                    )
                                    # Consider stopping the whole process depending on severity
                            else:
                                logger.warning(
                                    f"ID {partida.id}: No se generaron keywords ({provider_to_use}{' F' if use_fallback else ''})."
                                )

                        if not dry_run:
                            sleep(0.1)  # Pausa muy corta entre llamadas API

                    except Exception as proc_err:
                        logger.exception(
                            f"Error procesando Partida ID {partida.id}: {proc_err}"
                        )
                        # Decide si continuar o detener

                    finally:  # Asegura que la barra avance incluso si hay error en una partida
                        if progress_bar:
                            progress_bar.update(1)

        finally:  # Asegura que la barra de progreso se cierre
            if progress_bar:
                progress_bar.close()

        # --- Final Summary ---
        logger.info(f"\n--- Proceso Finalizado ---")
        mode = "SIMULACIÓN (Dry Run)" if dry_run else "EJECUCIÓN REAL"
        logger.info(f"Modo: {mode}")
        logger.info(
            f"Se procesaron {processed_count} de {total_partidas_to_process} partidas objetivo."
        )
        if not dry_run:
            logger.info(f"Keywords guardadas para {processed_count} partidas.")


# --- Fin del Script ---
