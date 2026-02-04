import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QTextEdit, QLineEdit, QPushButton, QProgressBar
)
from PySide6.QtCore import QThread, Signal
from langchain_core.prompts import PromptTemplate
from npmai import Ollama
from langchain_core.output_parsers import StrOutputParser
import traceback

# =======================
# WORKER THREAD
# =======================
class CodeWorker(QThread):
    log = Signal(str)
    finished = Signal(str)

    def __init__(self, task_text):
        super().__init__()
        self.task_text = task_text

    def run(self):
        try:
            self.log.emit("Generating code using NPM AutoCode AI...")

            # Prompt template
            prompt = PromptTemplate(
                input_variables=["inpu"],
                template=(
                    "Hey you are helpful code assistant that writes code just write code nothing else "
                    "and maintain proper indentation. No extra explanations. "
                    "remember that whatever imports you are using install dependencies in code using subprocess beacuase user had not installed your code requirements"
                    "Do not respond with any insturction or any other statement if you are giving any statement in english or that is not of code so give in # comment ok beacuase your code will be executed through exec() function of python so give such format code that can be executed in exec() function YOUR WHOLE RESPONSE WILL BE SENT TO exec() so do not write anything except code."
                    "You will be asked to generate code about a task. "
                    "This is the task:{inpu}"
                ))

            user_query = self.task_text
            llm = Ollama(
                model="codellama:7b-instruct",
                temperature=0.8
                )
            parser = StrOutputParser()

            
            response1 = llm.invoke(prompt.format(inpu=user_query))

            response= parser.parse(response1)

            # Clean code from ```python blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith("```python"):
                cleaned_response = cleaned_response[len("```python"):]
            elif cleaned_response.startswith("```"):
                cleaned_response= cleaned_response[len("```"):]
            else:
                pass
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-len("```")]

            self.log.emit("Code generated:\n" + cleaned_response)

            # Execute code safely
            self.log.emit("Executing code...")
            local_vars = {}
            exec(cleaned_response.strip(), {}, local_vars)
            self.log.emit("Code executed successfully")
            self.finished.emit("Task completed")
        except Exception as e:
            self.finished.emit("Error: " + str(e))
            self.log.emit(traceback.format_exc())

# =======================
# UI
# =======================
class AutoCodeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NPM AutoCode AI")
        self.resize(600, 600)
        layout = QVBoxLayout()

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Describe your automation task here...")

        self.done_btn = QPushButton("Generate & Execute")
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        layout.addWidget(QLabel("Task Description:"))
        layout.addWidget(self.task_input)
        layout.addWidget(self.done_btn)
        layout.addWidget(QLabel("Logs:"))
        layout.addWidget(self.log_box)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        self.done_btn.clicked.connect(self.start_task)

    def start_task(self):
        task_text = self.task_input.text().strip()
        if not task_text:
            self.log_box.append("Please enter a task description")
            return

        self.log_box.append("Starting task...")
        self.progress_bar.setValue(10)

        self.worker = CodeWorker(task_text)
        self.worker.log.connect(self.log_box.append)
        self.worker.finished.connect(self.task_finished)
        self.worker.start()

    def task_finished(self, msg):
        self.log_box.append(msg)
        self.progress_bar.setValue(100)

# =======================
# MAIN
# =======================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoCodeApp()
    window.show()
    sys.exit(app.exec())

