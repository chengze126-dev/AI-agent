# Data Analysis Agent

Chat with your data. Load any CSV or Excel file and ask analytical questions in natural language.

**Framework**: LangChain (Pandas Agent)  
**LLM**: GPT-4o  

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
# Demo mode — creates sample sales data automatically
python agent.py

# Your own data
python agent.py --file your_data.csv

# Single question
python agent.py --file sales.csv --question "What is the monthly revenue trend?"
```

## Example Questions

- "What is the total revenue by product?"
- "Which region performs best?"
- "Show the correlation between quantity and revenue"
- "What are the top 5 selling products?"
