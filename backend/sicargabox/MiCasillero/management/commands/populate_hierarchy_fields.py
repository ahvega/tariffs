from django.core.management.base import BaseCommand
from MiCasillero.models import PartidaArancelaria
import re


class Command(BaseCommand):
    help = 'Populates hierarchy fields for all PartidaArancelaria records based on item_no patterns'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate without making changes (show examples only)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed progress for each record',
        )

    def extract_hierarchy(self, item_no):
        """
        Extracts hierarchy metadata from item_no.

        Handles patterns found in database:
        - 99.3%: XXXX.XX.XX.XX (e.g., "0101.21.00.00", "8471.30.00.00")
        - 0.5%:  XXXX.XX.XX.XX.XX (e.g., "8471.30.00.00.10")
        - 0.2%:  Irregular patterns

        Returns:
            dict: {
                'chapter_code': str,
                'heading_code': str,
                'parent_item_no': str,
                'grandparent_item_no': str,
                'hierarchy_level': int,
                'is_leaf_node': bool
            }
        """
        # Remove any whitespace
        item_no = item_no.strip()

        # Split by dots
        parts = item_no.split('.')

        # Extract chapter (first 4 digits)
        if len(parts) > 0 and parts[0]:
            chapter_code = parts[0].zfill(4)  # Pad with zeros if needed
        else:
            chapter_code = item_no[:4] if len(item_no) >= 4 else item_no.zfill(4)

        # Extract heading (chapter + first subheading)
        # Example: "0101.21" from "0101.21.00.00"
        if len(parts) >= 2:
            heading_code = f"{parts[0]}.{parts[1]}"
        else:
            heading_code = chapter_code

        # Determine parent based on pattern
        # Strategy: Replace last non-zero segment with "00"
        parent_item_no = None
        grandparent_item_no = None

        if len(parts) >= 3:
            # Find indices of non-zero parts
            non_zero_indices = []
            for i, part in enumerate(parts):
                if part and part != '00' and part != '0':
                    non_zero_indices.append(i)

            if non_zero_indices:
                last_significant_idx = non_zero_indices[-1]

                # Parent: replace last significant part with '00'
                if last_significant_idx > 0:  # Not the chapter itself
                    parent_parts = parts.copy()
                    parent_parts[last_significant_idx] = '00'
                    parent_item_no = '.'.join(parent_parts)

                # Grandparent: parent's parent
                if len(non_zero_indices) >= 2:
                    second_last_idx = non_zero_indices[-2]
                    if second_last_idx > 0:
                        gparent_parts = parts.copy()
                        # Zero out both last and second-to-last significant parts
                        gparent_parts[non_zero_indices[-1]] = '00'
                        gparent_parts[second_last_idx] = '00'
                        grandparent_item_no = '.'.join(gparent_parts)

        # Calculate hierarchy level
        # Count number of non-zero parts (more specific = deeper)
        hierarchy_level = 1  # Base level (chapter)
        for part in parts:
            if part and part != '00' and part != '0':
                hierarchy_level += 1

        # Cap at level 4 (most tariff systems don't go deeper)
        hierarchy_level = min(hierarchy_level, 4)

        return {
            'chapter_code': chapter_code,
            'heading_code': heading_code,
            'parent_item_no': parent_item_no,
            'grandparent_item_no': grandparent_item_no,
            'hierarchy_level': hierarchy_level,
            'is_leaf_node': True  # All current records are leaves
        }

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']

        partidas = PartidaArancelaria.objects.all().order_by('item_no')
        total = partidas.count()

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('HIERARCHY FIELD POPULATION'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'\nTotal partidas to process: {total:,}\n')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved\n'))

        updated = 0
        errors = 0
        skipped = 0

        # Show examples of different patterns
        self.stdout.write('\n--- PATTERN EXAMPLES ---\n')
        examples_shown = 0
        seen_patterns = set()

        for partida in partidas:
            if examples_shown >= 10:
                break

            # Get pattern signature (number of parts)
            pattern = '.'.join(['X' * len(p) for p in partida.item_no.split('.')])

            if pattern not in seen_patterns:
                seen_patterns.add(pattern)
                hierarchy = self.extract_hierarchy(partida.item_no)

                self.stdout.write(f'\nPattern: {pattern}')
                self.stdout.write(f'  Example: {partida.item_no}')
                self.stdout.write(f'  Chapter: {hierarchy["chapter_code"]}')
                self.stdout.write(f'  Heading: {hierarchy["heading_code"]}')
                self.stdout.write(f'  Parent: {hierarchy["parent_item_no"]}')
                self.stdout.write(f'  Grandparent: {hierarchy["grandparent_item_no"]}')
                self.stdout.write(f'  Level: {hierarchy["hierarchy_level"]}')

                examples_shown += 1

        if dry_run:
            self.stdout.write(f'\n{self.style.SUCCESS("DRY RUN COMPLETE - No changes made")}\n')
            return

        # Proceed with actual update
        self.stdout.write('\n--- PROCESSING ALL RECORDS ---\n')

        for i, partida in enumerate(partidas, 1):
            try:
                hierarchy = self.extract_hierarchy(partida.item_no)

                # Only update if values have changed
                needs_update = (
                    partida.chapter_code != hierarchy['chapter_code'] or
                    partida.heading_code != hierarchy['heading_code'] or
                    partida.parent_item_no != hierarchy['parent_item_no'] or
                    partida.grandparent_item_no != hierarchy['grandparent_item_no'] or
                    partida.hierarchy_level != hierarchy['hierarchy_level'] or
                    partida.is_leaf_node != hierarchy['is_leaf_node']
                )

                if needs_update:
                    for field, value in hierarchy.items():
                        setattr(partida, field, value)
                    partida.save()
                    updated += 1
                else:
                    skipped += 1

                # Progress indicator every 500 records
                if i % 500 == 0:
                    progress_pct = (i / total) * 100
                    self.stdout.write(
                        f'Progress: {i:,}/{total:,} ({progress_pct:.1f}%) - '
                        f'Updated: {updated:,}, Skipped: {skipped:,}, Errors: {errors}'
                    )

                # Show verbose output for first 5 and last 5
                if verbose and (i <= 5 or i >= total - 4):
                    self.stdout.write(
                        f'\n  [{i}] {partida.item_no} -> '
                        f'Chapter: {hierarchy["chapter_code"]}, '
                        f'Heading: {hierarchy["heading_code"]}, '
                        f'Level: {hierarchy["hierarchy_level"]}'
                    )

            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'\nError processing {partida.item_no}: {str(e)}'
                    )
                )

        # Final summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('COMPLETED!'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'\nTotal processed: {total:,}')
        self.stdout.write(self.style.SUCCESS(f'Updated:         {updated:,}'))
        self.stdout.write(f'Skipped:         {skipped:,} (already up to date)')

        if errors > 0:
            self.stdout.write(self.style.ERROR(f'Errors:          {errors}'))
        else:
            self.stdout.write(self.style.SUCCESS('Errors:          0'))

        self.stdout.write('\n')
