# 🌴 CDC Flight Tracker

A private automated flight price monitor that tracks **American Airlines** and **JetBlue** routes from Miami (**MIA**) and Fort Lauderdale (**FLL**) to the Dominican Republic.

Built with the [fli](https://github.com/punitarani/fli) library, this project bypasses the need for web scraping by interacting directly with Google Flights' internal API.

## 🚀 How it Works

1.  **Search Logic**: The Python script (`main.py`) performs six searches per destination:
    * Round-Trip from MIA and FLL.
    * One-Way Outbound from MIA and FLL.
    * One-Way Return to MIA and FLL.
2.  **Automation**: A GitHub Action runs the script every 6 hours (triggered by a cron job).
3.  **Deployment**: The script generates a static `index.html` dashboard. GitHub Actions commits this file back to the repository, and **Vercel** automatically redeploys the live site.
4.  **Notifications**: If configured, the script can send real-time price alerts to your phone via **Pushover**.

## 📊 The Dashboard

The dashboard is split into two clear sections to account for airline hub differences (AA at MIA vs. JetBlue at FLL). It compares bundled Round-Trip prices against "Mix & Match" One-Way prices to find the absolute cheapest way to travel.



## 🛠 Setup & Installation

### 1. Repository Secrets
To run the automation, you must add the following secrets to your GitHub Repo (**Settings > Secrets and variables > Actions**):

* `PUSHOVER_TOKEN`: Your Pushover API Application Token.
* `PUSHOVER_USER`: Your Pushover User Key.

### 2. GitHub Actions Permissions
Ensure the workflow has permission to update your dashboard:
1.  Go to **Settings > Actions > General**.
2.  Under **Workflow permissions**, select **Read and write permissions**.

### 3. Vercel Deployment
1.  Connect your GitHub account to [Vercel](https://vercel.com).
2.  Import this repository.
3.  Vercel will detect the `index.html` and host your dashboard at a custom `.vercel.app` URL.

## 📂 Project Structure

* `main.py`: The core engine. Handles flight searching, price comparison, and HTML generation.
* `.github/workflows/monitor.yml`: The automation schedule and deployment logic.
* `requirements.txt`: Python dependencies (`flights`, `requests`, `pydantic`).
* `index.html`: The auto-generated dashboard (do not edit manually).

## ⚙️ Customization

To change your travel dates or destinations, edit the `Configuration` section at the top of `main.py`:

```python
# --- Configuration ---
DESTINATIONS = [Airport.SDQ, Airport.PUJ, Airport.LRM]
OUT_DATE = "2026-07-17"
IN_DATE = "2026-07-21"
AIRLINES = [Airline.AA, Airline.B6]
```

## 🤖 Triggering Manually
You can force a price refresh at any time by going to the **Actions** tab in this repository, selecting the **Flight Monitor & Deploy** workflow, and clicking **Run workflow**.

---
*Disclaimer: This tool is for personal use and relies on the internal API structures of Google Flights. Use responsibly.*
