# iCal Project - copilot-version

This project processes iCal (ICS) files by converting them to JSON format and back to ICS format with additional modifications. It uses Python and manages dependencies through [Rye](https://rye-up.com/).

---

## Features

- Converts ICS files to JSON format.
- Extracts and processes specific events (e.g., "Dur Muhurtamulu" and "Varjyam").
- Converts JSON back to ICS format with custom event details.

---

## Prerequisites

- Python 3.8 or higher
- [Rye](https://rye-up.com/) for dependency and environment management

---

## Installation

1. **Install Rye**  
   If Rye is not already installed, run the following command:

   ```bash
   curl -sSf https://rye-up.com/get | bash