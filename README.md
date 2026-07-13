# AI Interview Coach Pro - Production Core Framework Documentation

AI Interview Coach Pro is a self-contained web platform designed to evaluate candidate engineering responses against target track parameters. It calculates technical competence metrics in real time through structured sequence match routines, completely avoiding external network dependency.

## Production Core Prerequisites

- **Python Runtime Environment:** Version 3.8, 3.9, 3.10, or 3.11.
- **Data Persistence Store Layer:** SQLite local instance.
- **Client Rendering Canvas:** Modern HTML5 browser engine supporting ES6 scripts.

## Installation & Deployment Guide

```bash
# 1. Clone or extract project files locally
cd AI_Interview_Coach

# 2. Build and isolate the application's runtime variables
python -m venv venv
source venv/bin/activate  # On Windows terminal workflows: venv\Scripts\activate

# 3. Download verified dependency targets
pip install -r requirements.txt

# 4. Initialize relational tracking schema instances
python -c "import database; database.init_db()"

# 5. Boot local production development runtime server
python app.py