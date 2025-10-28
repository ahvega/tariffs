#!/usr/bin/env python
"""
Phase 2D - Courier Items to Partidas Matcher
Matches top 200 courier items to their corresponding tariff classifications.

Usage:
    python match_courier_items_to_partidas.py [--dry-run] [--verbose]
"""

import json
import os
import sys
from pathlib import Path

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SicargaBox.settings")
django.setup()

from django.db.models import Q

from MiCasillero.models import PartidaArancelaria

# Import the courier items list
sys.path.append(str(Path(__file__).parent.parent.parent))
from research_top_200_courier_items import top_200_courier_items


class CourierItemMatcher:
    """Matches courier items to tariff partidas using intelligent search."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.matches = []
        self.manual_review_needed = []
        self.stats = {
            "total_items": 0,
            "auto_matched": 0,
            "manual_review": 0,
            "no_match": 0,
        }

    def log(self, message):
        """Print if verbose mode."""
        if self.verbose:
            print(message)

    def search_partidas(self, query_text, limit=10):
        """
        Search for partidas using multiple strategies.
        Returns list of (partida, confidence_score) tuples.
        """
        results = []

        # Strategy 1: Exact keyword match (highest confidence)
        exact_matches = PartidaArancelaria.objects.filter(
            search_keywords__contains=[query_text.lower()]
        )[:limit]

        for p in exact_matches:
            results.append((p, "HIGH", "Exact keyword match"))

        if results:
            return results

        # Strategy 2: Partial keyword match
        for word in query_text.lower().split():
            if len(word) < 3:  # Skip very short words
                continue

            partial_matches = PartidaArancelaria.objects.filter(
                search_keywords__icontains=word
            )[:limit]

            for p in partial_matches:
                if p not in [r[0] for r in results]:
                    results.append((p, "MEDIUM", f'Partial match: "{word}"'))

        if results:
            return results[:limit]

        # Strategy 3: Description search (lowest confidence)
        desc_words = query_text.lower().split()
        q_filter = Q()
        for word in desc_words:
            if len(word) > 3:
                q_filter |= Q(descripcion__icontains=word)

        if q_filter:
            desc_matches = PartidaArancelaria.objects.filter(q_filter)[:limit]
            for p in desc_matches:
                if p not in [r[0] for r in results]:
                    results.append((p, "LOW", "Description match"))

        return results[:limit]

    def match_item(self, item):
        """
        Match a single courier item to a partida.
        Returns match info or None if manual review needed.
        """
        item_name = item["item"]
        description = item["description"]

        self.log(f"\nMatching: {item_name}")
        self.log(f"Description: {description}")

        # Search using item name + description
        search_query = f"{item_name} {description}"
        results = self.search_partidas(search_query)

        if not results:
            self.log("  ❌ No matches found - MANUAL REVIEW NEEDED")
            return None

        # Get best match
        best_match, confidence, reason = results[0]

        self.log(f"  ✓ Found {len(results)} matches")
        self.log(f"  Best: {best_match.item_no} ({confidence} confidence) - {reason}")
        self.log(f"  Desc: {best_match.descripcion[:60]}")

        match_info = {
            "item": item_name,
            "description": description,
            "partida_no": best_match.item_no,
            "partida_desc": best_match.descripcion,
            "confidence": confidence,
            "match_reason": reason,
            "current_provider": self._get_provider(best_match),
            "keyword_count": (
                len(best_match.search_keywords) if best_match.search_keywords else 0
            ),
            "alternative_matches": [
                {"item_no": p.item_no, "desc": p.descripcion[:60], "confidence": conf}
                for p, conf, _ in results[1:4]  # Top 3 alternatives
            ],
        }

        # Flag for manual review if confidence is LOW or multiple good matches
        if confidence == "LOW" or len([r for r in results if r[1] == "HIGH"]) > 1:
            self.log(
                "  ⚠️ FLAGGED FOR MANUAL REVIEW (low confidence or multiple matches)"
            )
            return match_info, True  # Return with manual review flag

        return match_info, False

    def _get_provider(self, partida):
        """Guess which provider generated keywords based on quality."""
        if not partida.search_keywords:
            return "NONE"

        # Check if it's likely Claude (from Phase 2C - Los demás)
        desc_lower = partida.descripcion.lower()
        if desc_lower.startswith("los demás") or desc_lower.startswith("las demás"):
            return "Claude (Phase 2C)"

        # Otherwise assume DeepSeek baseline
        return "DeepSeek (Baseline)"

    def match_all_items(self):
        """Match all 200 courier items to partidas."""
        print("=" * 70)
        print("Phase 2D: Matching Top 200 Courier Items to Partidas")
        print("=" * 70)
        print()

        self.stats["total_items"] = len(top_200_courier_items)

        for item in top_200_courier_items:
            result = self.match_item(item)

            if result is None:
                # No match found
                self.manual_review_needed.append(
                    {
                        "item": item["item"],
                        "description": item["description"],
                        "reason": "No matches found",
                        "suggested_partida": None,
                    }
                )
                self.stats["no_match"] += 1
            elif result[1]:  # Manual review flag
                match_info = result[0]
                self.manual_review_needed.append(
                    {
                        "item": match_info["item"],
                        "description": match_info["description"],
                        "reason": f"Low confidence ({match_info['confidence']}) or multiple matches",
                        "suggested_partida": match_info["partida_no"],
                        "suggested_desc": match_info["partida_desc"],
                        "alternatives": match_info["alternative_matches"],
                    }
                )
                self.stats["manual_review"] += 1
            else:
                # Good match
                self.matches.append(result[0])
                self.stats["auto_matched"] += 1

    def generate_report(self):
        """Generate matching report."""
        print("\n" + "=" * 70)
        print("MATCHING REPORT")
        print("=" * 70)
        print(f"\nTotal courier items: {self.stats['total_items']}")
        print(f"[OK] Auto-matched: {self.stats['auto_matched']}")
        print(f"[REVIEW] Manual review needed: {self.stats['manual_review']}")
        print(f"[NONE] No matches: {self.stats['no_match']}")
        print()

        # Analyze matched partidas
        unique_partidas = set(m["partida_no"] for m in self.matches)
        deepseek_count = len(
            [m for m in self.matches if "DeepSeek" in m["current_provider"]]
        )
        claude_count = len(
            [m for m in self.matches if "Claude" in m["current_provider"]]
        )

        print(f"Unique partidas matched: {len(unique_partidas)}")
        print(f"  - Currently using DeepSeek: {deepseek_count}")
        print(f"  - Already using Claude: {claude_count}")
        print()

        # Save results to files
        self._save_results()

        # Print manual review list
        if self.manual_review_needed:
            print("\n" + "=" * 70)
            print("ITEMS NEEDING MANUAL REVIEW")
            print("=" * 70)
            print()

            for idx, item in enumerate(self.manual_review_needed, 1):
                print(f"{idx}. {item['item']}")
                print(f"   Description: {item['description']}")
                print(f"   Reason: {item['reason']}")

                if item.get("suggested_partida"):
                    print(
                        f"   Suggested: {item['suggested_partida']} - {item['suggested_desc'][:60]}"
                    )

                    if item.get("alternatives"):
                        print(f"   Alternatives:")
                        for alt in item["alternatives"]:
                            print(f"     - {alt['item_no']}: {alt['desc']}")

                print()

        return unique_partidas

    def _save_results(self):
        """Save matching results to JSON files."""
        output_dir = Path(__file__).parent.parent.parent / "phase_2d_results"
        output_dir.mkdir(exist_ok=True)

        # Save auto-matched items
        with open(output_dir / "auto_matched.json", "w", encoding="utf-8") as f:
            json.dump(self.matches, f, indent=2, ensure_ascii=False)

        # Save manual review items
        with open(output_dir / "manual_review.json", "w", encoding="utf-8") as f:
            json.dump(self.manual_review_needed, f, indent=2, ensure_ascii=False)

        # Save partida list for regeneration (sorted unique list)
        unique_partidas = list(set(m["partida_no"] for m in self.matches))
        with open(output_dir / "partidas_to_regenerate.txt", "w") as f:
            f.write("\n".join(sorted(unique_partidas)))

        # Save summary
        summary = {
            "stats": self.stats,
            "unique_partidas": len(unique_partidas),
            "partidas_to_regenerate": unique_partidas,
            "deepseek_count": len(
                [m for m in self.matches if "DeepSeek" in m["current_provider"]]
            ),
            "claude_count": len(
                [m for m in self.matches if "Claude" in m["current_provider"]]
            ),
        }

        with open(output_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Results saved to: {output_dir}/")
        print(f"  - auto_matched.json ({len(self.matches)} items)")
        print(f"  - manual_review.json ({len(self.manual_review_needed)} items)")
        print(f"  - partidas_to_regenerate.txt ({len(unique_partidas)} partidas)")
        print(f"  - summary.json")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Match courier items to partidas")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

    args = parser.parse_args()

    matcher = CourierItemMatcher(verbose=args.verbose)
    matcher.match_all_items()
    unique_partidas = matcher.generate_report()

    if args.dry_run:
        print("\n[DRY RUN MODE] - No files saved")
        return

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print()
    print("1. Review manual_review.json and add manual matches")
    print("2. Run keyword regeneration:")
    print()
    print("   cd backend/sicargabox")
    print("   python manage.py generate_search_keywords \\")
    print("     --api-provider=anthropic \\")
    print("     --from-file=../../phase_2d_results/partidas_to_regenerate.txt \\")
    print("     --batch-size=10")
    print()
    print(f"Estimated cost: ${len(unique_partidas) * 0.01:.2f}")
    print()


if __name__ == "__main__":
    main()
