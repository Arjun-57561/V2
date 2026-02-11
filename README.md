# Uncertainty Agent Council

A multi-agent system for handling uncertainty in LLM responses through specialized agents.

## Architecture

The system consists of 7 specialized agents:
1. Query Processor - Analyzes and structures incoming queries
2. Fact Boundary - Distinguishes facts from inferences
3. Assumption Detection - Identifies underlying assumptions
4. Unknown Detection - Recognizes knowledge gaps
5. Temporal Uncertainty - Handles time-sensitive information
6. Confidence Calibration - Assesses response confidence
7. Decision Guidance - Provides actionable recommendations

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

## Usage

```bash
python main.py
```
