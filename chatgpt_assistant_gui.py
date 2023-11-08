import tkinter as tk
from tkinter import simpledialog
from tkhtmlview import HTMLLabel 
import openai
import threading
import markdown2 


# Initialize OpenAI client
client = openai.Client(api_key='Your_API_Key')

assistant = client.beta.assistants.create(
    name="Customer Support Assistant",
    instructions="You are an AI assistant that provides customer support for a tech company. Answer user questions, provide troubleshooting steps, and offer detailed product information.",
    tools=[],  
    model="gpt-4-1106-preview"
)
thread = client.beta.threads.create()


# interact with the assistant
def ask_assistant(question):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    global chat_history_html 

    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        if run_status.completed_at is not None:
            break

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    for msg in messages.data:
        if msg.role == 'assistant':
            for content in msg.content:
                if content.type == 'text':
                    # Update the chat window
                    html_content = markdown2.markdown(content.text.value)
                    global chat_history
                    chat_history_html += "<p><b>Assistant:</b> {}</p>".format(html_content)

                    # Update the chat window with HTML content
                    chat_history.set_html(chat_history_html)
                    chat_history.yview(tk.END)

# get the user's question and start interaction with the assistant
def send():
    user_query = user_input.get()
    global chat_history_html
    user_question_html = markdown2.markdown(user_query)
    chat_history_html += "<p><b>You:</b> {}</p>".format(user_question_html)
    chat_history.set_html(chat_history_html)

    user_input.delete(0, tk.END)
    threading.Thread(target=ask_assistant, args=(user_query,)).start()

# main window
root = tk.Tk()
root.title("Customer Support Assistant")

# chat history text area
chat_history_html = "<p>Welcome to the Customer Support Assistant!</p>"
chat_history = HTMLLabel(root, width=80, height=20)
chat_history.set_html(chat_history_html)
chat_history.pack(padx=10, pady=10)

# field for user input
user_input = tk.Entry(root, width=80)
user_input.pack(padx=10, pady=10)

# send button
send_button = tk.Button(root, text="Send", command=send)
send_button.pack(padx=10, pady=10)

root.mainloop()