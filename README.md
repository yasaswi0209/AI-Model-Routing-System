# SmartRoute — AI Model Routing Starter

SmartRoute chooses a small or large LLM using explainable rules, shows the reason and elapsed time, and stores requests in a local SQLite database. An optional estimated cost is calculated from explicitly configured per-million token prices. It is a learning project: its heuristic is not trained and no accuracy or savings are claimed.

## What you need
- Python 3.10 or newer and internet access for installing dependencies.
- Optional: Gemini API key from https://aistudio.google.com/apikey for real responses. Demo mode works without a key, but its output is simulated.

## Run on Windows (VS Code terminal)
1. Extract this ZIP and open the `SmartRoute` folder in VS Code.
2. Open Terminal > New Terminal, then run:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

3. The browser opens the dashboard. Leave **Demo mode** on to try without an API key.
4. For real answers, edit `.env`, set `GEMINI_API_KEY`, save, restart Streamlit and switch Demo mode off. Never commit or share the `.env` file. Check that the two model IDs in `.env` are available to your account. Model access and free quotas can change: https://ai.google.dev/gemini-api/docs/models

On macOS/Linux use `source .venv/bin/activate` and `cp .env.example .env`.

## Cost
Demo mode does not call the provider. Live requests may be subject to quota, provider billing, or changes in model availability. Cost is shown only after you enter both input and output USD-per-million-token prices for each model in `.env`; an unset price is not treated as zero. Estimate uses provider-reported prompt and candidate tokens; it may omit thinking tokens, other token categories, fees and taxes. Check the actual provider bill. Verify current prices: https://ai.google.dev/gemini-api/docs/pricing

## Optional FastAPI service

In a separate terminal with the virtual environment activated:

```bash
uvicorn api:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs. `POST /ask` accepts `question`, `mode` (`auto`, `small`, `large`) and `demo` (defaults to true). `GET /history` displays recent entries. This API has no authentication; keep it local. Do not deploy it publicly without access controls, rate limiting, privacy protections and a secure secret store.

## Files
- `router.py`: baseline rules and explainable routing decisions.
- `core.py`: Gemini API calls, timing and optional cost calculation.
- `storage.py`: local SQLite history.
- `app.py`: Streamlit dashboard.
- `api.py`: optional FastAPI interface.
- `evaluation/questions.csv`: 10 starter questions for manual evaluation; expand to 20–30.
- `tests/`: checks for basic routing and cost calculations.

## Test and evaluate
Run `python -m unittest discover -s tests -v`. For each evaluation question, compare Automatic mode to Always large mode. Manually judge correctness using an agreed rubric and record timings and provider usage. No real evaluation or savings are included in this starter.

## Privacy and limitations
Requests and responses are saved in `data/smartroute.db`; don't put secrets in prompts. Live mode sends prompts to the configured provider. SQLite is for a local demo, not a shared public service. The routing keywords can misclassify questions. There is no RAG, automatic quality grading, or trained classifier. Gemini responses can be incorrect. If live calls fail, check provider availability, key, quota and allowed models. No production deployment is included.
