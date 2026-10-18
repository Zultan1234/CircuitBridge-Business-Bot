"""Launch NOVA, a Gemini-powered Gradio business assistant for a fictional store."""
import gradio as gr
import inspect
from bot_core import handle_turn, MODEL

CSS = """
#hero {text-align: center; margin-bottom: 10px;}
#hero h1 {margin-bottom: 2px;}
#chat {min-height: 430px;}
#disclaimer {font-size: 0.88rem; opacity: .8;}
"""


def chat_ui(message, history, state, reflection_enabled):
    """Preserve Gemini context in Gradio session state, not just the UI transcript.

    Certain Gradio versions/sessions can send an empty chatbot value on a
    subsequent event even while previous bubbles are still visible. Storing
    the true conversation separately in gr.State prevents such a history gap.
    """
    shown_history = list(history or [])
    session_state = dict(state or {})
    prior_turns = list(session_state.get("_conversation_history") or shown_history)
    response, updated_state, trace = handle_turn(
        message, history=prior_turns, state=session_state,
        reflection=reflection_enabled)
    new_turns = [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response},
    ]
    updated_state["_conversation_history"] = (prior_turns + new_turns)[-24:]
    # If the UI transcript arrives empty despite an existing server-side
    # conversation, rebuild it so the user can still see previous turns.
    if not shown_history and prior_turns:
        shown_history = list(prior_turns)
    shown_history.extend(new_turns)
    return "", shown_history, updated_state, trace


def clear_all():
    return [], {}, "", "Cleared. No messages processed."


def build_demo():
    theme = gr.themes.Soft(primary_hue="indigo", secondary_hue="cyan", neutral_hue="slate")
    opts = {"title": "CircuitBridge Electronics | NOVA"}
    if int(gr.__version__.split(".")[0]) < 6:
        opts.update(theme=theme, css=CSS)
    with gr.Blocks(**opts) as demo:
        with gr.Column(elem_id="hero"):
            gr.Markdown("# ⚡ CircuitBridge Electronics")
            gr.Markdown("### NOVA • Your virtual technical sales engineer")
            gr.Markdown("Ask about hardware, request a simulated quote, or contact our fictional sales team.")
        gr.Markdown("**Assignment demo only:** products, employees, prices and store are fictional. No real orders or follow-up messages are sent.", elem_id="disclaimer")
        with gr.Row():
            with gr.Column(scale=3):
                cb_args = {"label": "Talk to NOVA", "elem_id": "chat", "height": 455}
                if "type" in inspect.signature(gr.Chatbot).parameters:
                    cb_args["type"] = "messages"
                chatbot = gr.Chatbot(**cb_args)
                message = gr.Textbox(label="Your message", placeholder="e.g. Quote 2 x CB-SOLDER-75; or recommend a Wi-Fi adapter", lines=2)
                with gr.Row():
                    send = gr.Button("Send", variant="primary")
                    clear = gr.Button("Clear chat")
            with gr.Column(scale=2):
                gr.Markdown("### Agent controls")
                reflection = gr.Checkbox(label="Bonus reflection pass (draft → check → final)", value=True)
                trace = gr.Textbox(label="Live agent trace (routing, tool calls, original/revised replies)", lines=21, interactive=False)
                gr.Markdown("**Try these examples** (paste into the chat):\n"
                            "- What do you sell?\n"
                            "- Recommend a USB-C charger for under $40.\n"
                            "- Quote 2 x CB-SOLDER-75.\n"
                            "- My name is Sam Demo, my email is sam.demo@example.com. Please contact me about lab equipment.\n"
                            "- Feedback: I would like more beginner kits.\n"
                            "- Can you guarantee drone delivery to the Moon?\n")
                gr.Markdown(f"**Model:** `{MODEL}`. API access requires `GEMINI_API_KEY`. Leads/feedback are written to a local private demo log; on Spaces these files may be erased on restart.")
        state = gr.State({})
        for source in (send.click, message.submit):
            source(fn=chat_ui, inputs=[message, chatbot, state, reflection],
                   outputs=[message, chatbot, state, trace])
        clear.click(fn=clear_all, inputs=None, outputs=[chatbot, state, message, trace])
    return demo


def launch_demo(share=False, debug=False, server_name=None):
    """Start compatible Gradio 5 / 6 UI with the theme and CSS."""
    demo = build_demo()
    options = {"share": share, "debug": debug, "server_name": server_name}
    if "theme" in inspect.signature(gr.Blocks.launch).parameters:
        options.update(theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="cyan", neutral_hue="slate"), css=CSS)
    return demo.launch(**options)


if __name__ == "__main__":
    import os
    # Use share=True in Colab, not in Hugging Face Spaces.
    launch_demo(share=os.getenv("COLAB_SHARE", "0") == "1", server_name="0.0.0.0")
