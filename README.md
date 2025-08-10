Python ETL Pipeline logging
===
A production-ready logging starter for Python ETL jobs. It cleanly splits console output (**non-errors → stdout**, **errors → stderr**), writes **all levels** to a rotating **JSON Lines** file with UTC timestamps, and runs logging off the main thread using **QueueHandler/QueueListener**. Configuration is declarative via `dictConfig` and uses only the Python standard library.


## Papar Information
- Title:  `ETL Pipeline logging`
- [From Print to Production: Best Practices for Python Logging](https://medium.com/@aliakbarhosseinzadeh/from-print-to-production-best-practices-for-python-logging-c4e8de2fa665)

## Install & Dependence
- python

## Requirements
- Python > 3.9

## Usage
From the repository root:
```bash
python -m src.main
```

## Directory Hierarchy
```
|—— .gitignore
|—— logs
|    |—— etl-pipeline.log.jsonl
|—— requirements.txt
|—— src
|    |—— config
|        |—— logger_config.py
|        |—— logging.json
|        |—— logging_utils.py
|        |—— __init__.py
|    |—— main.py
```


## References
- [logging-Python](https://docs.python.org/3/library/logging.html)
  
