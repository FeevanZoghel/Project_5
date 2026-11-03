# Electric Bus Planning – Project 5 | Group 5

**Project:** Electric Bus Planning  
**Deliverable:** Python code, datasets, test cases and Streamlit application

## AI Usage

This README.md file was generated with the assisstance of ChatGPT (OpenAI).
The content has been reviewed by the project team.

## 1. Project

This project focuses on checking and improving an electric bus schedule. The Python scripts clean the original planning data, generate an improved bus plan and evaluate feasibility and key performance indicators (KPIs). The **Transdev Planning Checker**, developed in Streamlit, provides a user interface for uploading data, checking a schedule, optimizing it and visualizing the results.

The online application is available at **https://project5-improvedtool.streamlit.app/**. The same link is stored in `Documentation/Streamlit url.txt`.

## 2. Contents of the delivery

| Folder / file | Contents |
| --- | --- |
| `.vscode/` | Optional Visual Studio Code settings. |
| `Code/data cleaning/` | Scripts for cleaning the original data and checking planning feasibility and KPIs. |
| `Code/Improved bus plan/` | Python script for generating a new bus schedule. |
| `Code/Streamlit/` | Streamlit application, supporting Python modules and interface assets. |
| `Documentation/` | Data-cleaning logbook, AI-use declaration and link to the online tool. |
| `Input data/` | Original and cleaned bus plans, distance matrix and timetable. |
| `Output data/` | Generated bus plans and feasibility/KPI results. |
| `Test cases/` | Feasible, infeasible and incorrect test scenarios, boundary tests and test plan. |
| `User instructions/` | Written user manual and instructional video explaining how to use the Transdev Planning Checker. |
| `Justification report Group 5.docx` | Main justification report, located directly in `Inleveren/`. Explains the scheduling algorithm, assumptions, comparisons, feasibility checks and results. |
| `README.md` | This guide. |

### Python files

| File | Purpose |
| --- | --- |
| `Code/data cleaning/Data_cleaning.py` | Checks and corrects the original bus-planning dataset and exports the cleaned version. |
| `Code/data cleaning/Bus_planning_controleren.py` | Provides feasibility checks, KPI calculations and Excel export functions for the standalone planning script. |
| `Code/Improved bus plan/Code_for_improved_bus_plan.py` | Generates an improved schedule and evaluates it using the checking functions. |
| `Code/Streamlit/Streamlit_app.py` | Main Streamlit interface for data uploads, optimization, checks and visualizations. |
| `Code/Streamlit/solver.py` | Generates an improved bus plan from the uploaded input data. |
| `Code/Streamlit/dataframe_check.py` | Checks uploaded data for missing, invalid or incorrectly formatted values. |
| `Code/Streamlit/feasibility_checks.py` | Checks operating constraints such as battery charge, charging time, trip continuity and overlaps. |
| `Code/Streamlit/calculations.py` | Calculates distances, energy use, bus counts and waiting/charging KPIs. |
| `Code/Streamlit/visualisations.py` | Generates interactive Gantt charts of bus activities. |

### Streamlit supporting folders

| Folder / file | Purpose |
| --- | --- |
| `images/` | Logos and icons shown in the application. |
| `styles/` | CSS files for colors, layout and component styling. |
| `templates/` | HTML templates for selected interface components. |
| `requirements.txt` | Python package dependencies for running the application. |

**Important:** In the application code, `styles/` contains **CSS** and `templates/` contains **HTML**. Keep these folders alongside `Streamlit_app.py`.

## 3. Requirements

- Python 3
- The packages listed in `Code/Streamlit/requirements.txt`, including Streamlit, pandas, openpyxl, matplotlib, scipy, numpy and mpld3

Install the dependencies from a terminal opened in the `Inleveren` folder:

```
python -m pip install -r "Code/Streamlit/requirements.txt"
```

## 4. Running the project

**Online application:** Open https://project5-improvedtool.streamlit.app/ (also available in `Documentation/Streamlit url.txt`). On the **Data Check** page, upload the bus plan, timetable and distance matrix in Excel format. Review validation messages, choose an energy estimation method and State of Health (SoH), and select **Optimize**. The improved planning can be downloaded; **Visualisations** shows KPIs and an interactive Gantt chart.

**Locally:** Keep the entire folder structure intact. From the `Inleveren` folder, start the Streamlit application with:

```
python -m streamlit run "Code/Streamlit/Streamlit_app.py"
```

To run the separate data-cleaning and planning scripts, use:

```
python "Code/data cleaning/Data_cleaning.py"
python "Code/Improved bus plan/Code_for_improved_bus_plan.py"
```

Run data cleaning only when the cleaned input needs to be regenerated. The improved-planning script uses functions from `Bus_planning_controleren.py`; do not remove or rename that file without updating the import. The scripts expect Excel inputs in `Input data/` and are configured to export results to `Output data/`.

## 5. Input and output

| File | Contents |
| --- | --- |
| `Input data/Original_bus_plan.xlsx` | Original bus schedule. |
| `Input data/Bus_Plan_Cleaned.xlsx` | Cleaned bus schedule used for subsequent calculations. |
| `Input data/DistanceMatrix.xlsx` | Distances and minimum/maximum travel times. |
| `Input data/Timetable.xlsx` | Required service trips and departure times. |
| `Output data/Generated_Improved_Bus_Planning.xlsx` | Bus schedule exported by the standalone improvement script. |
| `Output data/Improved_bus_plan.xlsx` | Separately stored improved bus schedule. |
| `Output data/Improved_plan_Feasibility_and_KPI_results.xlsx` | Exported feasibility results and KPI values. |

**Note:** `Generated_Improved_Bus_Planning.xlsx` and `Improved_bus_plan.xlsx` are separate files; they should not automatically be treated as identical versions of the same plan.

## 6. Validation and test cases

The `Test cases/` folder contains `Casus 1 - Feasible/`, `Casus 2 - Infeasible/` and `Casus 3 - Incorrect/`, along with supporting Excel datasets. The folder also includes `Bus_Plan_foutief.xlsx`, `Bus_Planning_Boundary_Tests.xlsx` and `Test plan.xlsx` for checking incorrect inputs, boundary conditions and documented test outcomes.

The application distinguishes between **input validation** (data formats and values) and **planning feasibility** (operational constraints). Test scenarios are supplied for reproducibility; detailed expected results are recorded in the test plan.

## 7. User instructions

The `User instructions/` folder contains two complementary guides for users of the **Transdev Planning Checker**:

| File | Purpose |
| --- | --- |
| `User instructions/User Manual Group 5.docx` | Written, illustrated user manual covering how to access the online tool, upload the required Excel files, understand data validation and feasibility results, choose optimization settings, download an improved plan, compare KPIs and Gantt charts, and avoid common mistakes. |
| `User instructions/User_manual_video.mp4` | Instructional video demonstrating how to use the tool. |

**Recommended starting point:** Watch `User_manual_video.mp4` first. Use `User Manual Group 5.docx` for step-by-step explanations, screenshots and troubleshooting. The manual is intended for people using the application; the present README primarily explains the delivered files and how to run or maintain the project.

## 8. Documentation and maintenance

The **`Justification report Group 5.docx`** is stored directly in the root of `Inleveren/`, not in a subfolder. It documents the greedy scheduling approach and its pseudocode, battery and charging assumptions, and the comparison of the original and improved bus plans using KPIs and feasibility checks. Refer to this report for the rationale behind the method and the interpretation of the results.

`Documentation/Data-cleaning logbook Dennis.xlsx` records the data-cleaning process. `Documentation/Declaration of AI Usage Project 5 Groep5.xlsx` documents AI use. `Documentation/Streamlit url.txt` contains the deployed application address.

For maintenance, update `solver.py` when changing the Streamlit optimization logic, `dataframe_check.py` for input rules, `feasibility_checks.py` or `calculations.py` for checks and KPIs, and `visualisations.py` for Gantt charts. Visual styling is maintained in `styles/` (CSS), `templates/` (HTML) and `images/`. Update `requirements.txt` when dependencies change.

**Keep the folder names and relative paths unchanged**, or update the corresponding references in the Python code. The project files, test datasets and documentation together form the handover package.
