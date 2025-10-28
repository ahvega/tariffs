from django.core.management.base import BaseCommand
import pandas as pd
import os


class Command(BaseCommand):
    help = "Rebuilds tariff descriptions with hierarchical information"

    def add_arguments(self, parser):
        parser.add_argument("input_file", type=str, help="Input CSV file path")
        parser.add_argument(
            "--output-file",
            type=str,
            default="aranceles_jerarquia.csv",
            help="Output CSV file path",
        )

    def normalize_parent_code(self, code):
        """
        Normalize parent code to the correct format.
        For example:
        - 970122.0 -> 9701.22
        - 970129.0 -> 9701.29
        - 970191.0 -> 9701.91
        """
        if pd.isna(code):
            return None

        # Convert to string and remove decimal part
        code_str = str(int(code))

        # For level 4 items (6 digits), get the first 4 digits and add decimal point
        if len(code_str) == 6:
            return f"{code_str[:4]}.{code_str[4:]}"

        # For level 3 items (4 digits), get the first 2 digits and add decimal point
        if len(code_str) == 4:
            return f"{code_str[:2]}.{code_str[2:]}"

        # For level 2 items (2 digits), return as is
        if len(code_str) == 2:
            return code_str

        return code_str

    def build_hierarchical_description(self, row, df):
        """
        Build complete description for level 4 items by including parent descriptions.
        """
        self.stdout.write(f"Processing item: {row['código']} (level {row['level']})")

        if row["level"] != 4:
            return row["descripción"]

        # Get parent (level 3) and grandparent (level 2) descriptions
        parent_code = self.normalize_parent_code(row["parent_code"])
        self.stdout.write(f"Parent code for {row['código']}: {parent_code}")

        if not parent_code:
            self.stdout.write(f"Warning: No parent code found for {row['código']}")
            return row["descripción"]

        # Find parent item (level 3)
        parent_mask = df["código"] == parent_code
        if not parent_mask.any():
            self.stdout.write(
                f"Warning: Parent item not found for code {parent_code} (child: {row['código']})"
            )
            return row["descripción"]
        parent_item = df[parent_mask].iloc[0]
        self.stdout.write(
            f"Found parent item: {parent_item['código']} - {parent_item['descripción'][:50]}..."
        )

        # Get grandparent code (level 2)
        grandparent_code = self.normalize_parent_code(parent_item["parent_code"])
        self.stdout.write(f"Grandparent code for {parent_code}: {grandparent_code}")

        if not grandparent_code:
            self.stdout.write(f"Warning: No grandparent code found for {parent_code}")
            return f"{parent_item['descripción']} - {row['descripción']}"

        # Find grandparent item (level 2)
        grandparent_mask = df["código"] == grandparent_code
        if not grandparent_mask.any():
            self.stdout.write(
                f"Warning: Grandparent item not found for code {grandparent_code} (parent: {parent_code})"
            )
            return f"{parent_item['descripción']} - {row['descripción']}"
        grandparent_item = df[grandparent_mask].iloc[0]
        self.stdout.write(
            f"Found grandparent item: {grandparent_item['código']} - {grandparent_item['descripción'][:50]}..."
        )

        # Build complete hierarchical description
        complete_desc = f"{grandparent_item['descripción']} - {parent_item['descripción']} - {row['descripción']}"
        self.stdout.write(
            f"Successfully built description for {row['código']}: {complete_desc[:100]}..."
        )
        return complete_desc

    def handle(self, *args, **options):
        self.stdout.write("Starting rebuild_descriptions command...")

        input_file = options["input_file"]
        output_file = options["output_file"]

        self.stdout.write(f"Input file: {input_file}")
        self.stdout.write(f"Output file: {output_file}")

        if not os.path.exists(input_file):
            self.stdout.write(
                self.style.ERROR(f"Input file {input_file} does not exist")
            )
            return

        try:
            # Read the CSV file
            self.stdout.write(f"Reading {input_file}...")
            df = pd.read_csv(input_file)

            # Print some basic information about the data
            self.stdout.write(f"Total rows: {len(df)}")
            self.stdout.write(f"Levels found: {df['level'].unique()}")
            self.stdout.write(f"Sample of parent codes: {df['parent_code'].head()}")
            self.stdout.write(f"Columns found: {df.columns.tolist()}")

            # Sort by código to ensure proper hierarchical order
            df = df.sort_values("código")

            # Build hierarchical descriptions for level 4 items
            self.stdout.write("Building hierarchical descriptions...")
            df["descripción_completa"] = df.apply(
                lambda row: self.build_hierarchical_description(row, df), axis=1
            )

            # For level 4 items, replace the original description with the complete one
            level4_mask = df["level"] == 4
            level4_count = level4_mask.sum()
            self.stdout.write(f"Found {level4_count} level 4 items")

            if level4_count > 0:
                df.loc[level4_mask, "descripción"] = df.loc[
                    level4_mask, "descripción_completa"
                ]
                self.stdout.write("Updated descriptions for level 4 items")
            else:
                self.stdout.write("Warning: No level 4 items found!")

            # Drop the temporary column
            df = df.drop("descripción_completa", axis=1)

            # Save to output file
            self.stdout.write(f"Saving results to {output_file}...")
            df.to_csv(output_file, index=False)

            self.stdout.write(
                self.style.SUCCESS(f"Successfully processed {len(df)} items")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing file: {str(e)}"))
            import traceback

            self.stdout.write(self.style.ERROR(traceback.format_exc()))
