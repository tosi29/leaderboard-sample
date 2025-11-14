"""Reporter - Generates HTML reports from benchmark results"""

import json
from pathlib import Path
from typing import Optional

from jinja2 import Template

DEFAULT_TEMPLATE_PATH = Path(__file__).with_name("templates") / "leaderboard.html"


def load_template(template_file: Optional[str] = None) -> Template:
    """Load the HTML template from disk."""
    template_path = Path(template_file) if template_file else DEFAULT_TEMPLATE_PATH

    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found at {template_path}")

    template_text = template_path.read_text(encoding="utf-8")
    return Template(template_text)


def generate_report(
    results_file: str = "results/benchmark_results.json",
    output_file: str = "docs/index.html",
    template_file: Optional[str] = None,
) -> None:
    """
    Generate an HTML report from benchmark results

    Args:
        results_file: Path to the JSON results file
        output_file: Path where the HTML report should be saved
        template_file: Optional override for the Jinja template path
    """
    # Load results
    results_path = Path(results_file)
    if not results_path.exists():
        print(f"Error: Results file not found at {results_file}")
        return

    with results_path.open("r", encoding="utf-8") as f:
        results = json.load(f)

    # Prepare data for template
    agents_data = []

    for agent_name, agent_info in results.get("agents", {}).items():
        summary = agent_info.get("summary", {})
        total = summary.get("total", 0)
        correct = summary.get("correct", 0)
        incorrect = summary.get("incorrect", 0)

        accuracy = (correct / total * 100) if total > 0 else 0

        # Collect task details
        tasks = []
        total_execution_time = 0
        for task_id, task_info in agent_info.get("tasks", {}).items():
            execution_time = task_info.get("execution_time", 0)
            total_execution_time += execution_time
            tasks.append(
                {
                    "name": task_info.get("task_name", task_id),
                    "correct": task_info.get("correct", False),
                    "execution_time": execution_time,
                }
            )

        # Calculate average execution time
        average_time = (total_execution_time / total) if total > 0 else 0

        agents_data.append(
            {
                "name": agent_name,
                "accuracy": accuracy,
                "average_time": average_time,
                "correct": correct,
                "incorrect": incorrect,
                "total": total,
                "tasks": tasks,
            }
        )

    # Sort by accuracy (descending) and assign ranks
    agents_data.sort(key=lambda x: x["accuracy"], reverse=True)
    for i, agent in enumerate(agents_data, 1):
        agent["rank"] = i

    # Render template
    try:
        template = load_template(template_file)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return

    html_content = template.render(
        timestamp=results.get("timestamp", "Unknown"),
        agents=agents_data,
    )

    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML report generated at {output_file}")


def main():
    """Main entry point for the reporter"""
    import sys

    results_file = sys.argv[1] if len(sys.argv) > 1 else "results/benchmark_results.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "docs/index.html"
    template_file = sys.argv[3] if len(sys.argv) > 3 else None

    generate_report(results_file, output_file, template_file)


if __name__ == "__main__":
    main()
