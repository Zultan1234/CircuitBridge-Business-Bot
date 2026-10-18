---
title: CircuitBridge NOVA Business Assistant
emoji: ⚡
colorFrom: indigo
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
---

# CircuitBridge Electronics — NOVA Agent

## Demonstration Video

[Watch NOVA Chatbot Demonstration](https://youtu.be/kOK09VoFhIk)

**EECE 503P/798S — Introduction to Agents.** Complete fictional online-electronics-store chatbot project.

> **Everything in this shop is fictional**. Demo product listings, pricing, team members and quotations are coursework-only. No orders, emails, or real fulfillment occur.

## Features

- Persona **NOVA** and separately labeled operational **INSTRUCTIONS** (`bot_core.py`, also discussed in notebook).
- Three-way deterministic router: `general_question`, `lead_collection`, and `feedback`.
- `record_customer_interest(email, name, message)` and `record_feedback(question)` persist JSONL files and print trace messages.
- Real Gemini API calls with **manual function-calling dispatch** and response handoff. Supporting tools: `search_catalog` and `create_quote`.
- Reliable, deterministic catalog pricing: quantity × published fictional unit price (excludes shipping/tax/customs).
- Short-term chat history sent to Gemini, and local Gradio state for incomplete lead details.
- Optional second-model **reflection** pass; UI trace displays original draft and revised reply.
- Working Gradio `app.py`, Colab notebook, and Hugging Face Spaces YAML configuration.
- Reads the simulated PDF and text summary to ground answers.

## Fix for Gemini tool handoff (v2)

The initial version passed `id=` directly to `types.Part.from_function_response`.
Some SDK versions reject that argument with `TypeError` **after** a successful
`search_catalog` tool call. Version 2 handles both SDK signatures and prints
sanitized error details in the Live Agent Trace. Use a **fresh Colab runtime**
with the revised ZIP/notebook so old Python definitions aren't still loaded.

## Conversation memory reliability (v3)

The Gradio app now stores the latest user and assistant messages **inside
Gradio session state** (`_conversation_history`) rather than depending solely
on the visible chat transcript to send history back during subsequent
callbacks. The trace shows how many prior messages reached the agent.
The **Clear chat** control resets both the UI and session memory. In Colab,
restart the runtime before launching this updated app so cached Python imports
and UI callbacks don't keep the earlier implementation.

**Two-turn test:** Ask: "I'm building an ESP32 smart home project with
motion and temperature sensors." Then ask: "What project did I describe?"
The second trace should report `Conversation context: 2 prior message(s)
supplied` and NOVA should refer to the ESP32 project.

## Setup in Colab (the easiest way)

1. Download and extract the project ZIP, or upload the entire project to your Google Drive.
2. Open `business_agent.ipynb` in Google Colab. Follow the first cells to upload/extract the project ZIP when necessary.
3. Obtain a **Gemini API key** from [Google AI Studio](https://aistudio.google.com/app/apikey).
4. Set `GEMINI_API_KEY` in Colab Secrets (left sidebar, key icon) or enter it into the **hidden password prompt** from the notebook. Do not paste the key into a saved code cell.
5. Run the notebook in order, including `%pip install -r requirements.txt`.
6. Run the final cell to launch Gradio with `share=True`; Colab prints a temporary public `gradio.live` link. It only works while the notebook runtime is running.

If the model isn't available for your account, choose an available model at [Gemini Models](https://ai.google.dev/gemini-api/docs/models), and set `GEMINI_MODEL` before launching.

## Local run

```bash
python -m pip install -r requirements.txt
cp .env.example .env
# edit .env and provide GEMINI_API_KEY (never commit .env)
python app.py
```

Visit the local URL printed by Gradio.

## Hugging Face Spaces deployment (bonus)

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space); select **Gradio** and the Space visibility you want.
2. Upload the **contents** of this project (not the outer ZIP folder) to the Space, including `app.py`, `bot_core.py`, `requirements.txt`, `me/`, and `README.md`.
3. In Space **Settings → Variables and secrets**, add a **Secret** named `GEMINI_API_KEY` with your key; optionally set a variable `GEMINI_MODEL` to an available Gemini model.
4. Wait for the Space to build, then open the **App** tab. Copy the Space URL into your Moodle / GitHub README as proof of deployment.

Important: **no Hugging Face Space was created by this ZIP**. Upload and secret setup require your own Hugging Face account. Local JSONL logs inside the free Space filesystem are temporary and not appropriate for customer-production data.

## Notebook and coursework deliverables

```
CircuitBridge_Business_Bot/
├── me/
│   ├── about_business.pdf
│   ├── business_summary.txt
│   └── product_catalog.json
├── business_agent.ipynb       # main notebook/Colab launcher + class demos
├── bot_core.py                # inspectable business, routing, tools, Gemini logic
├── app.py                     # Gradio interface + HF Spaces app entrypoint
├── requirements.txt
├── tests/test_bot.py          # offline tests
├── .env.example               # safe API key template
├── .gitignore
└── README.md                  # you are here
```

The 4 tool names, input schemas and output contracts are documented in `bot_core.py` (`TOOL_SCHEMAS`). The same definitions are imported and displayed in the notebook.

## Test plan / video script (~4 minutes)

1. **General:** "What products do you sell?" → answer grounded in catalog.
2. **Recommendation:** "Recommend a Wi-Fi adapter under $50" → `search_catalog` invoked, shows real demo price.
3. **Quote:** "Quote 2 x CB-SOLDER-75" → `create_quote`, 2 × $89.00 = **$178.00**, excluding taxes/shipping.
4. **Lead:** "My name is Sam Demo, my email is sam.demo@example.com. Please contact me about an oscilloscope." → router `lead_collection`, lead tool log.
5. **Feedback:** "Feedback: I wish you had more sensor packs." → feedback tool log.
6. **Unknown:** "Do you guarantee delivery to the Moon?" → don't make shipping promises; log unanswered question via `record_feedback`.
7. With **reflection enabled**, display **draft** and **revised reply** in the trace panel.
8. Open the running Colab Gradio link or deployed Space link.

You may use fake demo names/emails; do not collect real customer information for coursework.

## Privacy and limitations

- `.env` and `data/` are git-ignored and should **never** be committed.
- Gemini API free tiers may use requests to improve Google's products. Do not enter confidential material. Rates and availability may change.
- No third-party commerce or payment integrations. Pricing is fictional; stocks, shipping, taxes, returns and warranties are unconfirmed.
- The router is intentionally a simple reproducible heuristic, and may misclassify unusual messages.
- Public Space persistence is ephemeral; the `data/` folder may reset on rebuild/restart. Production would require an authenticated database and privacy notice.

## Instructor submission

Submit your **GitHub repository link** plus a demo video link according to the assignment PDF. The Moodle page accepts 4 files, so if you need a physical upload, submit the project ZIP and optionally the MP4 demo. **Never upload your `.env` or key.**

## Sources for API and deployment guidance

- [Google GenAI SDK function calling](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)
- [Google Gemini model list](https://ai.google.dev/gemini-api/docs/models)
- [Google Gemini developer API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Hugging Face Gradio Spaces](https://huggingface.co/docs/hub/spaces-sdks-gradio)
