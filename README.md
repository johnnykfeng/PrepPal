
![Alt text](logo.jpeg "logo")

# ChatGPT-based Writing and Reading Proficiency Evaluator

This project uses the ChatGPT API to evaluate students' writing and reading proficiency tailored for exams such as IELTS. Deployed using Streamlit, this tool offers an interactive interface for educators and students alike.

[Pitch Deck](https://docs.google.com/presentation/d/1K5R1EqNaB_1PF3__VHCqVmuKlmQAU5qk7C30wgXWBjQ/edit?usp=sharing)
<!-- ![Screenshot of the application](path_to_screenshot.png) *Replace with an actual screenshot link* -->

## Features

- **Writing Assessment**: Evaluates written passages and provides feedback on grammar, vocabulary, coherence, and other key writing aspects.
- **Reading Assessment**: Offers comprehension questions based on passages and uses ChatGPT to judge the correctness of student responses.
- **Interactive UI**: User-friendly Streamlit interface that allows easy submission of texts and displays results in a comprehensible manner.
- **Tailored Feedback**: Provides feedback that is specifically designed for the requirements of exams like IELTS and TOEFL.

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/johnnykfeng/PrepPal.git
   cd repository_name
   ```

2. **Install Required Libraries**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up ChatGPT API Credentials**:
   Ensure you have the ChatGPT API keys. Place them in a `.env` file as:
   ```env
   OPENAI_API_KEY = <your api key>
   ```

4. **Run the Streamlit App**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Navigate to the provided URL after running the Streamlit app.
2. Choose the test you are studying for: IELTS or CELPIP
3. For Writing Assessment:
   - Click 'Get writing task' to cycle through a pre-saved writing tasks
   - Input your passage in the provided text box.
   - Click 'Evaluate my writing' and wait for the feedback.
   - Optionally check spelling, grammar, and suggest improvements<br>
4. For Reading Assessment:
   - Click 'Get reading task'
   - Read the given passage.
   - Click 'Generate Multiple Choice Questions'
      - wait for GPT to create questions
   - Click 'Generate Fill in the Blank Exercises' for feedback on your answers.
      - cheat sheet is available in expander tab 🤫
      - optional check 'Synonyms Allowed'

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please ensure to update tests as appropriate.

## Contributors
- Lisa Luo
- Bo Wen
- Yiju Liu
