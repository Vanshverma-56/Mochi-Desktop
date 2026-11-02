\# Mochi



\*\*A customisable Windows desktop companion and productivity workspace.\*\*



Mochi is a Windows desktop productivity application built with Python and PySide6. It combines a floating desktop companion with a modular workspace for managing everyday activities.



\## Features



\### Floating Desktop Companion

\- Separate floating companion window.

\- Designed to coexist with the main workspace.

\- Foundation for future customisation and appearance options.



\### Task Management

\- Create, edit and delete tasks.

\- Assign High, Medium and Low priorities.

\- Add descriptions, categories and due dates.

\- Search by title, description and category.

\- Filter tasks into Upcoming, Pending, Completed and No Due Date.

\- Group tasks by due date and sort by priority.

\- Mark tasks complete and undo recent completion actions.



\## Workspace



| Section | Current status |

|---|---|

| Dashboard | Initial implementation |

| Calendar | Planned |

| Tasks | Implemented |

| Notes | Planned |

| Daily Logbook | Planned |

| Focus | Planned |

| Settings \& Appearance | Planned |



\## Technology Stack

\- Python 3.11+

\- PySide6

\- SQLite

\- pytest

\- psutil



\## Project Structure



```text

Widget/

├── app.py

├── pyproject.toml

├── requirements.txt

├── README.md

├── CHANGELOG.md

├── assets/

├── docs/

├── src/

│   └── mochi/

│       ├── appearance/

│       ├── companion/

│       ├── core/

│       ├── database/

│       ├── integrations/

│       ├── services/

│       ├── widgets/

│       └── workspace/

│           └── pages/

└── tests/

```



\## Getting Started



\### Requirements

\- Windows

\- Python 3.11 or newer

\- Git



\### Installation



Clone the repository:



```powershell

git clone https://github.com/Vanshverma-56/Mochi-Desktop.git

cd Mochi-Desktop

```



Create and activate a virtual environment:



```powershell

py -3.11 -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



Install dependencies:



```powershell

python -m pip install --upgrade pip

pip install -e .

pip install pytest

```



\### Run Mochi



```powershell

python app.py

```



\### Run Tests



```powershell

python -m pytest -v

```



\## Data Storage



Mochi uses a local SQLite database. Application data is stored in the operating system's application data directory rather than in the source repository.



\## Development Roadmap



\- \[x] Initial application structure

\- \[x] SQLite database foundation

\- \[x] Task management service

\- \[x] Task management interface

\- \[x] Floating companion window

\- \[x] Initial dashboard

\- \[ ] Collapsible workspace sidebar

\- \[ ] Dashboard redesign and functional modules

\- \[ ] Calendar and event management

\- \[ ] Notes and scratchpad

\- \[ ] Daily Logbook

\- \[ ] Focus timer and session tracking

\- \[ ] Settings and appearance customisation

\- \[ ] Independent desktop widgets

\- \[ ] Persistent companion customisation

\- \[ ] Further automated tests and Windows integration



\## Project Status



Mochi is under active development. The current implementation establishes the desktop application foundation, floating companion, database architecture and task management functionality. Other workspace modules and independent widgets will be introduced progressively.



\## License



No open-source license has been added yet.
