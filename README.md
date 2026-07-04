# Valorant-Rank-Progression-Tracker

terminal-based database program that records the history of competitive matches and computes rank advancement statistics.

## Features
Relational database storage: Match data is safely and permanently stored using SQLite.
The database is automatically queried by SQL Aggregations to determine net Rank Rating (RR) changes and overall win rates.
Rich Terminal User Interface: displays visually appealing match history tables and summary statistic panels, color-coded for victories and losses, by utilizing the `rich` library.

 How to Run
have the required dependencies installed:
   ```bash
   pip install rich
