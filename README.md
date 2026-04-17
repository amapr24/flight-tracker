# 🌴 Caribbean Flight Tracker

A private automated flight intelligence dashboard that tracks **American Airlines** and **JetBlue** routes from South Florida (**MIA** & **FLL**) to the Dominican Republic.

Built with the [fli](https://github.com/punitarani/fli) library, this project bypasses the need for manual searching by interacting directly with Google Flights' internal API.


## 🚀 How it Works

1.  **Dual-Origin Search**: The Python script (`main.py`) performs a full suite of searches for **both** Miami (MIA) and Fort Lauderdale (FLL) independently.
2.  **Comparison Engine**: It fetches official Round-Trip bundles and compares them against "Mix & Match" One-Way fares to ensure you see the absolute lowest price.
3.  **Automation**: Triggered by **cron-job.org**, a GitHub Action runs the script every 6 hours.
4.  **Instant Deployment**: The script generates a travel-styled `index.html`. GitHub Actions commits this file back to the repo, and **Vercel** automatically redeploys the live dashboard.
5.  **Alerts**: Real-time price notifications are sent to your phone via **Pushover**.


## 📊 The Dashboard

The dashboard is organized into two distinct tables (MIA vs. FLL) to clearly separate airline hub operations:
* **American Airlines** primarily appears in the MIA table.
* **JetBlue** primarily appears in the FLL table.


## 🛠 Setup & Installation

### 1. Repository Secrets
Add these to your GitHub Repo (**Settings > Secrets and variables > Actions**):
* `PUSHOVER_TOKEN`: Your Pushover API Application Token.
* `PUSHOVER_USER`: Your Pushover User Key.

### 2. GitHub Actions Permissions
1.  Go to **Settings > Actions > General**.
2.  Under **Workflow permissions**, select **Read and write permissions**. (Required to update `index.html`).

### 3. Vercel Deployment
1.  Connect your GitHub account to [Vercel](https://vercel.com).
2.  Import this repository.
3.  Vercel will host your dashboard at a custom `.vercel.app` URL.


## ⚙️ Configuration & Reference

To update your dates or destinations, edit the `Configuration` section at the top of `main.py`.

### 🗓️ Dates
Dates must be in `YYYY-MM-DD` format.
```python
OUT_DATE = "2026-07-17"
IN_DATE = "2026-07-21"
```

### 📍 Airport Enums
| Code | Enum |
| :--- | :--- |
| **MIA** | `Airport.MIA` |
| **FLL** | `Airport.FLL` |
| **SDQ** | `Airport.SDQ` |
| **PUJ** | `Airport.PUJ` |
| **LRM** | `Airport.LRM` |

### ✈️ Airline Enums
| Carrier | Enum Code |
| :--- | :--- |
| **American Airlines** | `Airline.AA` |
| **JetBlue** | `Airline.B6` |
| **Spirit Airlines** | `Airline.NK` |
| **Delta Air Lines** | `Airline.DL` |
| **Southwest** | `Airline.WN` |

## 📂 Project Structure
* `main.py`: Core logic for fetching data and building the HTML dashboard.
* `.github/workflows/monitor.yml`: The automation engine that pushes updates.
* `requirements.txt`: Required libraries (`flights`, `requests`, `pydantic`).
* `index.html`: The auto-generated dashboard (do not edit manually).


## 🤖 Triggering Manually
You can force a price refresh at any time by going to the **Actions** tab in this repository, selecting the **Flight Monitor & Deploy** workflow, and clicking **Run workflow**.

---
*Disclaimer: This tool is for personal use and relies on the internal API structures of Google Flights. Use responsibly.*
