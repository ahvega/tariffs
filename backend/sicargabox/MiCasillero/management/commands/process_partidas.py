import json
import logging

import openai
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

from MiCasillero.models import PartidaArancelaria

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Process Partidas Arancelarias CSV and classify items for courier shipping"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")
        parser.add_argument("--api-key", type=str, help="OpenAI API key")
        parser.add_argument(
            "--batch-size", type=int, default=100, help="Batch size for processing"
        )

    def classify_description(self, client, descripcion):
        prompt = """
        Analyze this product description and classify it for courier shipping suitability.
        Product: "{descripcion}"
        
        Consider:
        1. Size and weight typical for this product
        2. Dangerous goods regulations
        3. Prohibited items (weapons, drugs, etc.)
        4. Perishable nature
        5. Special handling needs
        
        Respond in JSON format:
        {{
            "suitable_for_courier": boolean,
            "category": "ALLOWED/RESTRICTED/PROHIBITED",
            "restrictions": [],
            "package_type": "string",
            "requires_special_handling": boolean,
            "special_instructions": "string",
            "max_weight_allowed": number or null
        }}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a customs and logistics expert.",
                    },
                    {"role": "user", "content": prompt.format(descripcion=descripcion)},
                ],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error classifying description: {descripcion}")
            logger.error(str(e))
            return None

    def handle(self, *args, **options):
        client = openai.OpenAI(api_key=options["api_key"])
        df = pd.read_csv(options["csv_file"])
        batch_size = options["batch_size"]

        self.stdout.write("Starting partidas processing...")

        for i in range(0, len(df), batch_size):
            batch = df[i : i + batch_size]
            for _, row in batch.iterrows():
                try:
                    classification = self.classify_description(
                        client, row["descripcion"]
                    )
                    if not classification:
                        continue

                    if classification["suitable_for_courier"]:
                        partida = PartidaArancelaria(
                            item_no=row["codigo"],
                            descripcion=row["descripcion"],
                            partida_arancelaria=row["codigo"],
                            impuesto_dai=float(row["dai"]) if row["dai"] != "-" else 0,
                            impuesto_isc=float(row["isc"]) if row["isc"] != "-" else 0,
                            impuesto_ispc=(
                                float(row["ispc"]) if row["ispc"] != "-" else 0
                            ),
                            impuesto_isv=float(row["isv"]) if row["isv"] != "-" else 0,
                            courier_category=classification["category"],
                            restrictions=classification["restrictions"],
                            package_type=classification["package_type"],
                            requires_special_handling=classification[
                                "requires_special_handling"
                            ],
                            special_instructions=classification["special_instructions"],
                            max_weight_allowed=classification["max_weight_allowed"],
                        )
                        partida.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Successfully processed partida: {row["codigo"]}'
                            )
                        )
                except Exception as e:
                    logger.error(f"Error processing row: {row['codigo']}")
                    logger.error(str(e))
                    continue

            self.stdout.write(f"Processed batch {i//batch_size + 1}")

        self.stdout.write(self.style.SUCCESS("Successfully processed all partidas"))
