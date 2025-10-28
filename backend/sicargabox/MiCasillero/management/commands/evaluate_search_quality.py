"""
Management command to evaluate Elasticsearch search keyword quality.

This command loads test queries from test_data/test_queries.json, executes
searches, calculates quality metrics, and generates an HTML report.

Usage:
    python manage.py evaluate_search_quality --output=report.html
    python manage.py evaluate_search_quality --json-output=results.json
    python manage.py evaluate_search_quality --verbose

Metrics calculated:
    - Precision@K: Percentage of relevant results in top K results
    - Mean Reciprocal Rank (MRR): Average position of first relevant result
    - Zero-result rate: Percentage of queries returning no results
    - Category-specific breakdowns
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from django.core.management.base import BaseCommand
from django.conf import settings
from elasticsearch_dsl.query import Q as ES_Q

from MiCasillero.documents import PartidaArancelariaDocument
from MiCasillero.models import PartidaArancelaria


class Command(BaseCommand):
    help = "Evaluate Elasticsearch search keyword quality using test dataset"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="search_quality_report.html",
            help="Output HTML report filename",
        )
        parser.add_argument(
            "--json-output",
            type=str,
            default=None,
            help="Optional JSON output filename for raw results",
        )
        parser.add_argument(
            "--test-file",
            type=str,
            default="test_data/test_queries.json",
            help="Path to test queries JSON file",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print detailed output during evaluation",
        )
        parser.add_argument(
            "--k",
            type=int,
            default=5,
            help="Number of top results to consider for Precision@K (default: 5)",
        )

    def handle(self, *args, **options):
        self.verbose = options["verbose"]
        self.k = options["k"]

        # Load test queries
        test_file_path = os.path.join(settings.BASE_DIR, options["test_file"])
        self.stdout.write(f"Loading test queries from: {test_file_path}")

        try:
            with open(test_file_path, "r", encoding="utf-8") as f:
                test_data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(
                self.style.ERROR(f"Test file not found: {test_file_path}")
            )
            return
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f"Invalid JSON in test file: {e}"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {test_data['metadata']['total_queries']} test queries "
                f"across {test_data['metadata']['total_categories']} categories"
            )
        )

        # Run evaluation
        results = self.evaluate_searches(test_data)

        # Calculate metrics
        metrics = self.calculate_metrics(results, test_data)

        # Print summary
        self.print_summary(metrics)

        # Generate HTML report
        html_output = options["output"]
        self.generate_html_report(results, metrics, test_data, html_output)
        self.stdout.write(self.style.SUCCESS(f"\nHTML report saved to: {html_output}"))

        # Optionally save JSON
        if options["json_output"]:
            self.save_json_results(results, metrics, options["json_output"])
            self.stdout.write(
                self.style.SUCCESS(f"JSON results saved to: {options['json_output']}")
            )

        # Return status code based on quality
        overall_precision = metrics["overall"]["precision_at_k"]
        if overall_precision >= 0.9:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Search quality EXCELLENT (Precision@{self.k} = {overall_precision:.1%})"
                )
            )
            return 0
        elif overall_precision >= 0.8:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠ Search quality GOOD (Precision@{self.k} = {overall_precision:.1%})"
                )
            )
            return 0
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"\n✗ Search quality NEEDS IMPROVEMENT (Precision@{self.k} = {overall_precision:.1%})"
                )
            )
            return 1

    def evaluate_searches(self, test_data: Dict) -> List[Dict]:
        """Execute all test queries and collect results."""
        results = []
        total_queries = sum(
            len(cat["queries"]) for cat in test_data["categories"].values()
        )
        current = 0

        for category_id, category_data in test_data["categories"].items():
            for query in category_data["queries"]:
                current += 1
                if self.verbose:
                    self.stdout.write(f"[{current}/{total_queries}] Testing: {query}")

                # Execute search using same logic as views.py
                search_results = self.execute_search(query)

                # Evaluate results
                result = {
                    "query": query,
                    "category": category_id,
                    "category_name": category_data["description"],
                    "expected_patterns": category_data.get(
                        "expected_partida_patterns", []
                    ),
                    "results": search_results,
                    "num_results": len(search_results),
                    "is_zero_result": len(search_results) == 0,
                }

                # Calculate relevance for this query
                result["relevant_in_top_k"] = self.count_relevant_in_top_k(
                    search_results, result["expected_patterns"], self.k
                )
                result["first_relevant_position"] = self.find_first_relevant_position(
                    search_results, result["expected_patterns"]
                )

                results.append(result)

        return results

    def execute_search(self, query: str) -> List[Dict]:
        """Execute Elasticsearch search (mirrors views.buscar_partidas)."""
        if len(query) < 3:
            return []

        try:
            search = PartidaArancelariaDocument.search()

            # Multi-match query with same weights as production
            es_query = ES_Q(
                "multi_match",
                query=query,
                fields=[
                    "item_no^3",
                    "descripcion^2",
                    "full_text_search",
                    "search_keywords",
                ],
                fuzziness="AUTO",
            )

            # Only return ALLOWED category
            search = search.query(es_query)
            search = search.filter("term", courier_category="ALLOWED")
            search = search[:20]  # Limit to top 20 results

            response = search.execute()

            # Convert to list of dicts
            results = []
            for hit in response:
                try:
                    partida = PartidaArancelaria.objects.get(item_no=hit.item_no)
                    results.append(
                        {
                            "item_no": hit.item_no,
                            "descripcion": hit.descripcion,
                            "score": hit.meta.score,
                            "search_keywords": getattr(hit, "search_keywords", []),
                            "courier_category": partida.courier_category,
                        }
                    )
                except PartidaArancelaria.DoesNotExist:
                    continue

            return results
        except Exception as e:
            if self.verbose:
                self.stderr.write(f"Search error for '{query}': {e}")
            return []

    def count_relevant_in_top_k(
        self, results: List[Dict], expected_patterns: List[str], k: int
    ) -> int:
        """Count how many results in top K match expected partida patterns."""
        if not results or not expected_patterns:
            return 0

        top_k_results = results[:k]
        relevant_count = 0

        for result in top_k_results:
            item_no = result["item_no"]
            # Check if item_no starts with any expected pattern
            if any(item_no.startswith(pattern) for pattern in expected_patterns):
                relevant_count += 1

        return relevant_count

    def find_first_relevant_position(
        self, results: List[Dict], expected_patterns: List[str]
    ) -> int:
        """Find position (1-indexed) of first relevant result, or 0 if none found."""
        if not results or not expected_patterns:
            return 0

        for position, result in enumerate(results, start=1):
            item_no = result["item_no"]
            if any(item_no.startswith(pattern) for pattern in expected_patterns):
                return position

        return 0  # No relevant result found

    def calculate_metrics(self, results: List[Dict], test_data: Dict) -> Dict:
        """Calculate aggregate metrics from results."""
        total_queries = len(results)

        # Overall metrics
        zero_result_count = sum(1 for r in results if r["is_zero_result"])
        total_relevant_in_k = sum(r["relevant_in_top_k"] for r in results)
        total_possible_relevant = total_queries * self.k

        # MRR calculation
        reciprocal_ranks = []
        for r in results:
            if r["first_relevant_position"] > 0:
                reciprocal_ranks.append(1.0 / r["first_relevant_position"])
            else:
                reciprocal_ranks.append(0.0)

        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0

        # Category-specific metrics
        category_metrics = {}
        for category_id in test_data["categories"].keys():
            category_results = [r for r in results if r["category"] == category_id]

            if category_results:
                cat_zero_results = sum(
                    1 for r in category_results if r["is_zero_result"]
                )
                cat_relevant = sum(r["relevant_in_top_k"] for r in category_results)
                cat_possible = len(category_results) * self.k

                cat_reciprocal_ranks = [
                    (
                        1.0 / r["first_relevant_position"]
                        if r["first_relevant_position"] > 0
                        else 0.0
                    )
                    for r in category_results
                ]

                category_metrics[category_id] = {
                    "total_queries": len(category_results),
                    "zero_results": cat_zero_results,
                    "zero_result_rate": cat_zero_results / len(category_results),
                    "precision_at_k": (
                        cat_relevant / cat_possible if cat_possible > 0 else 0.0
                    ),
                    "mrr": sum(cat_reciprocal_ranks) / len(cat_reciprocal_ranks),
                    "category_name": category_results[0]["category_name"],
                }

        return {
            "overall": {
                "total_queries": total_queries,
                "zero_results": zero_result_count,
                "zero_result_rate": zero_result_count / total_queries,
                "precision_at_k": (
                    total_relevant_in_k / total_possible_relevant
                    if total_possible_relevant > 0
                    else 0.0
                ),
                "mrr": mrr,
                "k": self.k,
            },
            "categories": category_metrics,
            "timestamp": datetime.now().isoformat(),
            "test_file": test_data["metadata"],
        }

    def print_summary(self, metrics: Dict):
        """Print summary of evaluation results to console."""
        overall = metrics["overall"]

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SEARCH QUALITY EVALUATION SUMMARY"))
        self.stdout.write("=" * 60)

        self.stdout.write(f"\nTotal Queries: {overall['total_queries']}")
        self.stdout.write(f"K (top results considered): {overall['k']}")

        # Zero-result rate
        zero_rate = overall["zero_result_rate"]
        zero_style = (
            self.style.SUCCESS
            if zero_rate < 0.05
            else (self.style.WARNING if zero_rate < 0.1 else self.style.ERROR)
        )
        self.stdout.write(
            f"\nZero-Result Rate: {zero_style(f'{zero_rate:.1%}')} ({overall['zero_results']} queries)"
        )

        # Precision@K
        precision = overall["precision_at_k"]
        prec_style = (
            self.style.SUCCESS
            if precision >= 0.9
            else (self.style.WARNING if precision >= 0.8 else self.style.ERROR)
        )
        self.stdout.write(f"Precision@{overall['k']}: {prec_style(f'{precision:.1%}')}")

        # MRR
        mrr = overall["mrr"]
        mrr_style = (
            self.style.SUCCESS
            if mrr >= 0.8
            else (self.style.WARNING if mrr >= 0.6 else self.style.ERROR)
        )
        self.stdout.write(f"Mean Reciprocal Rank (MRR): {mrr_style(f'{mrr:.3f}')}")

        # Category breakdown (show top 5 best and worst)
        self.stdout.write("\n" + "-" * 60)
        self.stdout.write("TOP 5 BEST PERFORMING CATEGORIES:")
        self.stdout.write("-" * 60)

        sorted_cats = sorted(
            metrics["categories"].items(),
            key=lambda x: x[1]["precision_at_k"],
            reverse=True,
        )

        for cat_id, cat_metrics in sorted_cats[:5]:
            self.stdout.write(
                f"{cat_metrics['category_name']}: "
                f"Precision@{overall['k']}={cat_metrics['precision_at_k']:.1%}, "
                f"MRR={cat_metrics['mrr']:.3f}"
            )

        self.stdout.write("\n" + "-" * 60)
        self.stdout.write("TOP 5 WORST PERFORMING CATEGORIES:")
        self.stdout.write("-" * 60)

        for cat_id, cat_metrics in sorted_cats[-5:]:
            self.stdout.write(
                f"{cat_metrics['category_name']}: "
                f"Precision@{overall['k']}={cat_metrics['precision_at_k']:.1%}, "
                f"MRR={cat_metrics['mrr']:.3f}"
            )

        self.stdout.write("=" * 60 + "\n")

    def generate_html_report(
        self, results: List[Dict], metrics: Dict, test_data: Dict, output_path: str
    ):
        """Generate comprehensive HTML report."""
        overall = metrics["overall"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Determine overall quality level
        precision = overall["precision_at_k"]
        if precision >= 0.9:
            quality_level = "EXCELLENT"
            quality_color = "#22c55e"
        elif precision >= 0.8:
            quality_level = "GOOD"
            quality_color = "#eab308"
        else:
            quality_level = "NEEDS IMPROVEMENT"
            quality_color = "#ef4444"

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Quality Evaluation Report - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #f3f4f6; padding: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        header {{ background: #1f2937; color: white; padding: 2rem; border-radius: 8px 8px 0 0; }}
        header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        header p {{ opacity: 0.8; }}
        .summary {{ padding: 2rem; border-bottom: 1px solid #e5e7eb; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }}
        .metric-card {{ border: 1px solid #e5e7eb; padding: 1.5rem; border-radius: 8px; }}
        .metric-card h3 {{ font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem; text-transform: uppercase; }}
        .metric-card .value {{ font-size: 2.5rem; font-weight: bold; margin-bottom: 0.25rem; }}
        .metric-card .subtitle {{ color: #6b7280; font-size: 0.875rem; }}
        .quality-badge {{ display: inline-block; background: {quality_color}; color: white; padding: 0.5rem 1rem; border-radius: 6px; font-weight: bold; }}
        .section {{ padding: 2rem; border-bottom: 1px solid #e5e7eb; }}
        .section h2 {{ font-size: 1.5rem; margin-bottom: 1.5rem; color: #1f2937; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; color: #374151; }}
        .progress-bar {{ height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: #3b82f6; transition: width 0.3s ease; }}
        .good {{ color: #22c55e; }}
        .warning {{ color: #eab308; }}
        .error {{ color: #ef4444; }}
        .query-result {{ margin-bottom: 1rem; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 6px; }}
        .query-result .query-text {{ font-weight: 600; margin-bottom: 0.5rem; }}
        .query-result .result-item {{ padding: 0.5rem; margin: 0.25rem 0; background: #f9fafb; border-radius: 4px; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Search Quality Evaluation Report</h1>
            <p>Generated: {timestamp}</p>
            <p>Test Dataset: {test_data['metadata']['total_queries']} queries across {test_data['metadata']['total_categories']} categories</p>
        </header>

        <div class="summary">
            <h2 style="margin-bottom: 1.5rem;">Overall Quality: <span class="quality-badge">{quality_level}</span></h2>

            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total Queries</h3>
                    <div class="value">{overall['total_queries']}</div>
                    <div class="subtitle">Test queries executed</div>
                </div>

                <div class="metric-card">
                    <h3>Precision@{overall['k']}</h3>
                    <div class="value" style="color: {quality_color}">{overall['precision_at_k']:.1%}</div>
                    <div class="subtitle">Relevant results in top {overall['k']}</div>
                </div>

                <div class="metric-card">
                    <h3>Mean Reciprocal Rank</h3>
                    <div class="value {'good' if overall['mrr'] >= 0.8 else ('warning' if overall['mrr'] >= 0.6 else 'error')}">{overall['mrr']:.3f}</div>
                    <div class="subtitle">Position of first relevant result</div>
                </div>

                <div class="metric-card">
                    <h3>Zero-Result Rate</h3>
                    <div class="value {'good' if overall['zero_result_rate'] < 0.05 else ('warning' if overall['zero_result_rate'] < 0.1 else 'error')}">{overall['zero_result_rate']:.1%}</div>
                    <div class="subtitle">{overall['zero_results']} queries with no results</div>
                </div>
            </div>
        </div>
"""

        # Category breakdown
        html += (
            """
        <div class="section">
            <h2>Category Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Queries</th>
                        <th>Precision@"""
            + str(overall["k"])
            + """</th>
                        <th>MRR</th>
                        <th>Zero Results</th>
                    </tr>
                </thead>
                <tbody>
"""
        )

        sorted_cats = sorted(
            metrics["categories"].items(),
            key=lambda x: x[1]["precision_at_k"],
            reverse=True,
        )

        for cat_id, cat_metrics in sorted_cats:
            precision_class = (
                "good"
                if cat_metrics["precision_at_k"] >= 0.9
                else ("warning" if cat_metrics["precision_at_k"] >= 0.8 else "error")
            )

            html += f"""
                    <tr>
                        <td>{cat_metrics['category_name']}</td>
                        <td>{cat_metrics['total_queries']}</td>
                        <td class="{precision_class}">{cat_metrics['precision_at_k']:.1%}</td>
                        <td>{cat_metrics['mrr']:.3f}</td>
                        <td>{cat_metrics['zero_results']}</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>
"""

        # Problem queries section (zero results or low relevance)
        problem_results = [
            r for r in results if r["is_zero_result"] or r["relevant_in_top_k"] == 0
        ]

        if problem_results:
            html += f"""
        <div class="section">
            <h2>Problem Queries ({len(problem_results)} queries)</h2>
            <p style="margin-bottom: 1.5rem; color: #6b7280;">Queries with zero results or no relevant results in top {overall['k']}</p>
"""

            for result in problem_results[:20]:  # Show first 20 problem queries
                html += f"""
            <div class="query-result">
                <div class="query-text">"{result['query']}" <span style="color: #6b7280;">({result['category_name']})</span></div>
"""

                if result["is_zero_result"]:
                    html += """<p class="error">⚠ Zero results returned</p>"""
                else:
                    html += f"""
                <p style="margin-bottom: 0.5rem;">Top {min(5, len(result['results']))} results:</p>
"""
                    for idx, res in enumerate(result["results"][:5], 1):
                        html += f"""
                <div class="result-item">{idx}. {res['item_no']} - {res['descripcion'][:100]}...</div>
"""

                html += """
            </div>
"""

            html += """
        </div>
"""

        # Recommendations section
        html += f"""
        <div class="section">
            <h2>Recommendations</h2>
"""

        if precision >= 0.9:
            html += """
            <p>✅ <strong>Current keywords are performing excellently.</strong> No immediate regeneration needed.</p>
            <ul style="margin-top: 1rem; margin-left: 2rem; line-height: 1.8;">
                <li>Proceed with Phase 1 (Celery + Redis infrastructure)</li>
                <li>Implement continuous learning pipeline to maintain quality</li>
                <li>Consider vector embeddings for semantic search enhancement</li>
            </ul>
"""
        elif precision >= 0.8:
            html += """
            <p>⚠ <strong>Current keywords are performing well, but could be improved.</strong></p>
            <ul style="margin-top: 1rem; margin-left: 2rem; line-height: 1.8;">
                <li>Consider regenerating keywords for worst-performing categories</li>
                <li>Run AI model comparison to test if newer models (DeepSeek-V3, GPT-4o, Claude 3.5) improve quality</li>
                <li>Estimated cost for targeted regeneration: $5-10</li>
            </ul>
"""
        else:
            html += f"""
            <p>❌ <strong>Current keywords need significant improvement.</strong> Regeneration strongly recommended.</p>
            <ul style="margin-top: 1rem; margin-left: 2rem; line-height: 1.8;">
                <li>Run AI model comparison immediately to identify best model</li>
                <li>Execute full keyword regeneration for all {test_data['metadata']['total_queries']} partidas</li>
                <li>Estimated cost for full regeneration: $20-135 (depending on model chosen)</li>
                <li>Expected improvement: Precision@{overall['k']} could increase to 85-95%</li>
            </ul>
"""

        html += """
        </div>

        <footer style="padding: 2rem; background: #f9fafb; text-align: center; color: #6b7280; border-radius: 0 0 8px 8px;">
            <p>Generated by SicargaBox Search Quality Evaluation Tool</p>
            <p style="margin-top: 0.5rem;">🤖 Claude Code</p>
        </footer>
    </div>
</body>
</html>
"""

        # Write HTML file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    def save_json_results(self, results: List[Dict], metrics: Dict, output_path: str):
        """Save raw results and metrics to JSON file."""
        output = {
            "metadata": {
                "timestamp": metrics["timestamp"],
                "test_file": metrics["test_file"],
            },
            "metrics": metrics,
            "results": results,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
