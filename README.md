# Hello, there!

#### Welcome to travel_smolagent_demo. This is a demonstration of agentic programming using smolagent. 

## Setup Instructions

**Please follow these steps to set up your environment:**

1. Ensure that you have the appropriate prerequisites for your environment.  
   - This project was built in **WSL Ubuntu 24.04 LTS** using **Jupyter Notebooks in VS Code**.  
   - Your setup may be different, so please adjust accordingly.

2. Install **Git LFS** (Large File Storage) if you haven't already:
    ```bash
    git lfs install
    ```

3. Clone this repository from GitHub or Hugging Face:
    ```bash
    git clone https://huggingface.co/spaces/seanpoyner/travel_agent
    ```
    or:
    ```bash
    git clone https://github.com/seanpoyner/travel_smolagent_demo.git
    ```

4. Navigate into the project directory:
    ```bash
    cd first_agent
    ```

5. Create and activate a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

6. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

7. Set up environment variables:  
   - Copy the example environment file and update it with your API keys.
     ```bash
     cp example.env .env
     ```
   - Open `.env` and add your Hugging Face API key (`HF_API_TOKEN`) and RapidAPI key (`RAPIDAPI_KEY`).

8. If using Jupyter Notebooks, run the setup script:
    ```bash
    bash setup_jupyter.sh
    ```

---

## Usage

### Running the Application

To start the agent-based application:

```bash
python app.py
```

This will launch a **Gradio UI**, where you can interact with the agent.

### Available Tools

The agent has access to several tools for retrieving travel-related information:

- **Flight Search:** Retrieve flight options based on departure and arrival locations.
- **Hotel Search:** Find hotels in a given city for specified dates.
- **Attractions Search:** Get popular attractions in a destination.
- **Current Date Tool:** Provides the current date for contextual responses.
- **Final Answer Tool:** Aggregates responses into a final output.

---

## Project Structure

```
first_agent/
│── agent.json            # Configuration file for smolagent 
│── app.py                # Main application script 
│── example.env           # Example environment variables file 
│── first_agent.ipynb     # Jupyter Notebook version of the project 
│── Gradio_UI.py          # Gradio-based UI implementation 
│── prompts.yaml          # Prompt templates for agent responses 
│── README.md             # Project documentation 
│── requirements.txt      # Required Python dependencies 
│── setup_jupyter.sh      # Script to set up Jupyter Notebook 
└── tools/                # Custom tool implementations 
      ├── final_answer.py  
      ├── today.py  
      ├── visit_webpage.py  
      └── web_search.py  
```

---

## Contributing

Contributions are welcome! To contribute:

1. Fork this repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -m "Added new feature"`).
4. Push to your fork (`git push origin feature-name`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License.
