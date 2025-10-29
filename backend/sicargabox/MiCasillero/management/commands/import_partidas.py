# MiCasillero/management/commands/import_partidas.py

import json
import logging
import math
import os
from decimal import Decimal

import numpy as np
import openai
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from dotenv import load_dotenv

from MiCasillero.models import PartidaArancelaria

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import and classify Partidas Arancelarias from CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")
        parser.add_argument(
            "--batch-size", type=int, default=50, help="Batch size for processing"
        )
        parser.add_argument(
            "--start-index", type=int, default=0, help="Start from specific index"
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="Run without saving to database"
        )
        parser.add_argument(
            "--api-provider",
            type=str,
            choices=["openai", "deepseek"],
            default="deepseek",
            help="API provider to use (openai or deepseek)",
        )

    def clean_decimal(self, value):
        """Convert value to Decimal, handling NaN and empty values."""
        if pd.isna(value) or value == "" or value == "-":
            return Decimal("0")
        try:
            return Decimal(str(value))
        except:
            return Decimal("0")

    def classify_description(self, client, descripcion, codigo, model_name):
        # Clean the description to prevent JSON issues
        descripcion = descripcion.replace("\n", " ").replace("\r", "")
        descripcion = descripcion.replace('"', '\\"')  # Escape quotes
        descripcion = descripcion.replace("\\", "\\\\")  # Escape backslashes
        descripcion = " ".join(descripcion.split())  # Normalize whitespace

        prompt = f"""
        Como experto en aduanas y logística, analiza este producto (código: {codigo}) para determinar su idoneidad para envío por courier.
        Descripción del producto: "{descripcion}"
        
        Considera las siguientes restricciones de envío por courier:
        1. Tamaño/Peso: Debe ser manejable para manipulación por courier
        2. Valor: Artículos de alto valor pueden necesitar manejo especial
        3. Regulaciones: Mercancías peligrosas, artículos prohibidos
        4. Necesidades especiales: Control de temperatura, fragilidad
        
        Responde en formato JSON:
        {{
            "suitable_for_courier": boolean,
            "category": "PERMITIDO/RESTRINGIDO/PROHIBIDO",
            "restrictions": ["lista de restricciones específicas"],
            "package_type": "CAJA_REGULAR/CAJA_REFORZADA/SOBRE/EMBALAJE_ESPECIAL",
            "requires_special_handling": boolean,
            "special_instructions": "instrucciones de manejo",
            "max_weight_allowed": número o null,
            "reasoning": "explicación breve de la clasificación"
        }}
        """

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en aduanas y logística especializado en envíos por courier.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            # Get the response content and clean it
            content = response.choices[0].message.content
            # Remove any potential BOM or hidden characters
            content = content.strip().lstrip("\ufeff")
            # Ensure the content is properly terminated
            if not content.endswith("}"):
                content = content + "}"

            try:
                result = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error for {codigo}: {str(e)}")
                logger.error(f"Raw content: {content}")
                # Try to fix common JSON issues
                content = content.replace("\n", " ").replace("\r", "")
                content = content.replace("\\", "\\\\")  # Escape backslashes
                content = content.replace('"', '\\"')  # Escape quotes
                try:
                    result = json.loads(content)
                except:
                    # If still fails, return default result
                    return self._get_default_classification()

            # Validate and clean the result
            result = self._validate_classification_result(result)
            return result

        except Exception as e:
            logger.error(f"Error clasificando {codigo}: {descripcion}")
            logger.error(str(e))
            return self._get_default_classification()

    def _get_default_classification(self):
        """Return a default classification result for error cases"""
        return {
            "suitable_for_courier": False,
            "category": "PROHIBIDO",
            "restrictions": ["Error en clasificación"],
            "package_type": "NO_APLICA",
            "requires_special_handling": True,
            "special_instructions": "Requiere revisión manual",
            "max_weight_allowed": None,
            "reasoning": "Error en el proceso de clasificación",
        }

    def _validate_classification_result(self, result):
        """Validate and clean the classification result"""
        # Ensure all required fields exist
        required_fields = {
            "suitable_for_courier": False,
            "category": "PROHIBIDO",
            "restrictions": ["Sin clasificación"],
            "package_type": "NO_APLICA",
            "requires_special_handling": True,
            "special_instructions": "Requiere revisión manual",
            "max_weight_allowed": None,
            "reasoning": "Sin explicación",
        }

        # Add missing fields with defaults
        for field, default in required_fields.items():
            if field not in result:
                result[field] = default

        # Clean string fields
        string_fields = [
            "category",
            "package_type",
            "special_instructions",
            "reasoning",
        ]
        for field in string_fields:
            if field in result:
                # Clean the string value
                value = str(result[field])
                value = value.replace("\n", " ").replace("\r", "")
                value = value.replace('"', '\\"')
                value = value.replace("\\", "\\\\")
                value = " ".join(value.split())  # Normalize whitespace
                result[field] = value.strip()

        # Ensure boolean values
        result["requires_special_handling"] = bool(
            result.get("requires_special_handling", True)
        )
        result["suitable_for_courier"] = bool(result.get("suitable_for_courier", False))

        # Ensure restrictions is a list
        if not isinstance(result.get("restrictions"), list):
            result["restrictions"] = ["Sin clasificación"]

        # Clean restrictions list
        result["restrictions"] = [
            str(r)
            .replace("\n", " ")
            .replace("\r", "")
            .replace('"', '\\"')
            .replace("\\", "\\\\")
            .strip()
            for r in result["restrictions"]
            if r
        ]

        return result

    def process_row(self, row, client, model_name):
        try:
            # Use the correct column names from the new CSV format
            codigo = str(row["Codigo"]).strip()
            descripcion = str(
                row["partida"]
            ).strip()  # Using the extended description from 'partida'
            dai = self.clean_decimal(row["dai"])  # Already in percentage (0-1)
            isc = self.clean_decimal(row["isc"])  # Already in percentage (0-1)
            ispc = self.clean_decimal(row["ispc"])  # Already in percentage (0-1)
            isv = self.clean_decimal(row["isv"])  # Already in percentage (0-1)
            parent_code = str(row["padre"]).strip() if "padre" in row else None
            level = (
                str(row["nivel"]).strip() if "nivel" in row else "4"
            )  # Default to level 4 if not specified

            # Get classification from API
            classification_result = self.classify_description(
                client, descripcion, codigo, model_name
            )

            # Ensure we have a valid classification result
            if not classification_result:
                classification_result = {
                    "category": "PROHIBIDO",
                    "restrictions": ["Error en clasificación"],
                    "package_type": "NO_APLICA",
                    "requires_special_handling": True,
                    "special_instructions": "Requiere revisión manual",
                    "max_weight_allowed": None,
                }

            # Map category to courier_category choices
            category_mapping = {
                "PERMITIDO": "ALLOWED",
                "RESTRINGIDO": "RESTRICTED",
                "PROHIBIDO": "PROHIBITED",
            }
            courier_category = category_mapping.get(
                classification_result.get("category", "PROHIBIDO"), "PROHIBITED"
            )

            # Ensure all required fields have values
            return {
                "item_no": codigo or "NO_CODE",  # Ensure non-null
                "descripcion": descripcion or "Sin descripción",  # Ensure non-null
                "partida_arancelaria": codigo or "NO_CODE",  # Ensure non-null
                "impuesto_dai": dai,
                "impuesto_isc": isc,
                "impuesto_ispc": ispc,
                "impuesto_isv": isv,
                "courier_category": courier_category,  # Mapped from classification
                "restrictions": classification_result.get(
                    "restrictions", ["Sin clasificación"]
                ),
                "package_type": classification_result.get("package_type", "NO_APLICA"),
                "requires_special_handling": bool(
                    classification_result.get("requires_special_handling", True)
                ),
                "special_instructions": classification_result.get(
                    "special_instructions", "Requiere revisión manual"
                ),
                "max_weight_allowed": classification_result.get("max_weight_allowed"),
                "search_keywords": f"{descripcion} {codigo}".strip()
                or "Sin palabras clave",  # Ensure non-null
            }
        except Exception as e:
            row_id = row["Codigo"] if "Codigo" in row else "unknown"
            logger.error(f"Error processing row {row_id}: {str(e)}")
            logger.error(f"Row contents: {row}")
            raise

    def handle(self, *args, **options):
        # Get API key from environment based on provider
        if options["api_provider"] == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise CommandError(
                    "DEEPSEEK_API_KEY not found in environment variables. Please add it to your .env file."
                )

            # Get DeepSeek configuration from environment
            base_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
            model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

            # Configure DeepSeek client
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise CommandError(
                    "OPENAI_API_KEY not found in environment variables. Please add it to your .env file."
                )

            # Configure OpenAI client
            client = openai.OpenAI(api_key=api_key)
            model_name = "gpt-4-0125-preview"

        # Handle CSV file path
        csv_path = options["csv_file"]
        if not os.path.isabs(csv_path):
            # If path is relative, make it absolute from the project root
            project_root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
            )
            csv_path = os.path.join(project_root, csv_path)

        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        self.stdout.write(
            f'Using {options["api_provider"]} API with model {model_name}'
        )
        if options["api_provider"] == "deepseek":
            self.stdout.write(f"DeepSeek API URL: {base_url}")
        self.stdout.write(f"Reading CSV file from: {csv_path}")

        # Read CSV with specific encoding and separator
        df = pd.read_csv(csv_path, encoding="utf-8", sep=",")
        total_rows = len(df)

        # Print column names for debugging
        self.stdout.write(f"Columns found in CSV: {df.columns.tolist()}")

        # Get existing records to avoid reprocessing
        existing_records = set(
            PartidaArancelaria.objects.values_list("item_no", flat=True)
        )
        self.stdout.write(f"Found {len(existing_records)} existing records")

        # Filter out already processed records
        df = df[~df["Codigo"].astype(str).isin(existing_records)]
        remaining_rows = len(df)

        if remaining_rows == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "All records have already been processed. Nothing new to import."
                )
            )
            return

        self.stdout.write(
            f'Processing {remaining_rows} new items starting from index {options["start_index"]}'
        )

        processed = 0
        saved = 0
        batch = []

        try:
            for index, row in df.iloc[options["start_index"] :].iterrows():
                processed += 1

                # Skip if already processed
                if str(row["Codigo"]).strip() in existing_records:
                    continue

                # Process the row
                item_data = self.process_row(row, client, model_name)
                if not item_data:
                    continue

                if not options["dry_run"]:
                    try:
                        partida = PartidaArancelaria(**item_data)
                        batch.append(partida)
                        saved += 1

                        # Save in batches
                        if len(batch) >= options["batch_size"]:
                            PartidaArancelaria.objects.bulk_create(batch)
                            self.stdout.write(
                                f"Saved batch of {len(batch)} items. Progress: {saved}/{processed} processed"
                            )
                            batch = []

                    except Exception as e:
                        error_msg = (
                            f"Error saving item {item_data['item_no']}: {str(e)}"
                        )
                        logger.error(error_msg)
                        self.stdout.write(self.style.ERROR(error_msg))
                        self.stdout.write(
                            self.style.ERROR(
                                "Aborting import due to validation error. Please fix the issues and try again."
                            )
                        )
                        raise CommandError(error_msg)
                else:
                    self.stdout.write(
                        f"Would save item: {item_data['item_no']} - {item_data.get('courier_category', 'UNKNOWN')}"
                    )
                    saved += 1

                # Progress update
                if processed % 10 == 0:
                    self.stdout.write(f"Processed {processed} items...")

            # Save any remaining items
            if batch and not options["dry_run"]:
                PartidaArancelaria.objects.bulk_create(batch)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Finished processing {processed} items. Successfully saved {saved} items."
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Import process aborted: {str(e)}"))
            raise CommandError(f"Import process aborted: {str(e)}")
