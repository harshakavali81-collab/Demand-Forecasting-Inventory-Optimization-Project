# Repository standard

## Layout

This repository keeps its working source paths. A shared portfolio structure does not require moving a React application, Python package, BI workbook or Verilog project into identical runtime directories.

| Area | Convention |
| --- | --- |
| Landing page | `README.md`: purpose, visuals, demo, features, stack, architecture, setup, tradeoffs and roadmap |
| Detailed reference | `PROJECT_GUIDE.md`: retained project-specific explanation and historical release notes |
| Documentation | `docs/`: design, inventory, reproduction and evidence |
| Work intake | `.github/ISSUE_TEMPLATE/`: bug and feature forms |
| Review | `.github/PULL_REQUEST_TEMPLATE.md`: linked issue, behavior and validation |
| Automation | `.github/workflows/portfolio-docs.yml`: README section and local-link checks |
| Source and tests | Existing project-specific paths listed below; no empty source/test placeholders |

## Workflow

1. Open an issue describing the user problem and measurable acceptance criteria.
2. Add it to a GitHub Project with Todo, In progress, Review and Done states when a board is configured.
3. Use a focused branch and meaningful commits, such as `docs: correct local setup paths` or `fix(api): reject malformed input`.
4. Run the project's documented checks and `python scripts/check_portfolio_docs.py`.
5. Open a pull request with actual validation results and `Closes #<issue-number>`.
6. Merge after review; record release evidence and update the issue/board.

Board creation, profile pins, repository social previews and milestone settings require account-level configuration. This file does not claim those settings have been applied.

## Validation scope

The documentation check validates the landing-page headings and local link targets only. It does not execute models, certify test coverage, inspect Git history for secrets, verify external websites, or prove production readiness. Existing application workflows remain the source of runtime CI evidence.

Keep credentials in local environment variables. A gitignore rule does not remove secrets already tracked or committed. Use only permitted sample data in public demos.

## Inventory at standardization

The following are the pre-existing public project files. New standardization files are described above. Historical guides may mention external bundles that are not part of this list.

- [`Dockerfile`](<../Dockerfile>)
- [`LICENSE`](<../LICENSE>)
- [`README.md`](<../README.md>)
- [`api`](<../api>)
- [`api/__init__.py`](<../api/__init__.py>)
- [`api/main.py`](<../api/main.py>)
- [`dashboard`](<../dashboard>)
- [`dashboard/app.py`](<../dashboard/app.py>)
- [`data`](<../data>)
- [`data/README.md`](<../data/README.md>)
- [`data/example_outputs`](<../data/example_outputs>)
- [`data/example_outputs/backtest_predictions.csv`](<../data/example_outputs/backtest_predictions.csv>)
- [`data/example_outputs/category_summary.csv`](<../data/example_outputs/category_summary.csv>)
- [`data/example_outputs/decisions.csv`](<../data/example_outputs/decisions.csv>)
- [`data/example_outputs/demand.csv`](<../data/example_outputs/demand.csv>)
- [`data/example_outputs/forecast.csv`](<../data/example_outputs/forecast.csv>)
- [`data/example_outputs/metrics.csv`](<../data/example_outputs/metrics.csv>)
- [`data/example_outputs/sku_summary.csv`](<../data/example_outputs/sku_summary.csv>)
- [`data/raw`](<../data/raw>)
- [`data/raw/demo_products.csv`](<../data/raw/demo_products.csv>)
- [`data/raw/demo_sales.csv`](<../data/raw/demo_sales.csv>)
- [`docker-compose.yml`](<../docker-compose.yml>)
- [`docs`](<../docs>)
- [`docs/data-dictionary.md`](<../docs/data-dictionary.md>)
- [`docs/interview-guide.md`](<../docs/interview-guide.md>)
- [`docs/methodology.md`](<../docs/methodology.md>)
- [`docs/powerbi-blueprint.md`](<../docs/powerbi-blueprint.md>)
- [`docs/project-explanation.md`](<../docs/project-explanation.md>)
- [`docs/workflow.md`](<../docs/workflow.md>)
- [`notebooks`](<../notebooks>)
- [`notebooks/01_data_and_forecasting.ipynb`](<../notebooks/01_data_and_forecasting.ipynb>)
- [`notebooks/02_inventory_optimization.ipynb`](<../notebooks/02_inventory_optimization.ipynb>)
- [`publication`](<../publication>)
- [`publication/linkedin-draft.md`](<../publication/linkedin-draft.md>)
- [`publication/portfolio-project-writeup.md`](<../publication/portfolio-project-writeup.md>)
- [`publication/resume-bullets.md`](<../publication/resume-bullets.md>)
- [`pyproject.toml`](<../pyproject.toml>)
- [`reports`](<../reports>)
- [`reports/Complete_Project_Explanation.pdf`](<../reports/Complete_Project_Explanation.pdf>)
- [`reports/Interview_Questions_Answers.pdf`](<../reports/Interview_Questions_Answers.pdf>)
- [`reports/Methodology_Guide.pdf`](<../reports/Methodology_Guide.pdf>)
- [`reports/Project_Presentation.pptx`](<../reports/Project_Presentation.pptx>)
- [`reports/Project_Report.pdf`](<../reports/Project_Report.pdf>)
- [`reports/Project_Workflow.pdf`](<../reports/Project_Workflow.pdf>)
- [`reports/Setup_Guide.pdf`](<../reports/Setup_Guide.pdf>)
- [`reports/data_dictionary.xlsx`](<../reports/data_dictionary.xlsx>)
- [`reports/forecasting_workflow.svg`](<../reports/forecasting_workflow.svg>)
- [`reports/inventory_workflow.svg`](<../reports/inventory_workflow.svg>)
- [`reports/system_architecture.svg`](<../reports/system_architecture.svg>)
- [`requirements.txt`](<../requirements.txt>)
- [`scripts`](<../scripts>)
- [`scripts/build_publication_assets.py`](<../scripts/build_publication_assets.py>)
- [`scripts/package_project.py`](<../scripts/package_project.py>)
- [`sql`](<../sql>)
- [`sql/business_queries.sql`](<../sql/business_queries.sql>)
- [`sql/schema.sql`](<../sql/schema.sql>)
- [`src`](<../src>)
- [`src/demand_inventory`](<../src/demand_inventory>)
- [`src/demand_inventory/__init__.py`](<../src/demand_inventory/__init__.py>)
- [`src/demand_inventory/cli.py`](<../src/demand_inventory/cli.py>)
- [`src/demand_inventory/data.py`](<../src/demand_inventory/data.py>)
- [`src/demand_inventory/eda.py`](<../src/demand_inventory/eda.py>)
- [`src/demand_inventory/evaluation.py`](<../src/demand_inventory/evaluation.py>)
- [`src/demand_inventory/features.py`](<../src/demand_inventory/features.py>)
- [`src/demand_inventory/forecasting.py`](<../src/demand_inventory/forecasting.py>)
- [`src/demand_inventory/inventory.py`](<../src/demand_inventory/inventory.py>)
- [`src/demand_inventory/pipeline.py`](<../src/demand_inventory/pipeline.py>)
- [`src/demand_inventory/service.py`](<../src/demand_inventory/service.py>)
- [`tests`](<../tests>)
- [`tests/conftest.py`](<../tests/conftest.py>)
- [`tests/test_features_forecasting.py`](<../tests/test_features_forecasting.py>)
- [`tests/test_inventory_service.py`](<../tests/test_inventory_service.py>)
- [`tests/test_packaging.py`](<../tests/test_packaging.py>)
- [`tests/test_pipeline.py`](<../tests/test_pipeline.py>)
