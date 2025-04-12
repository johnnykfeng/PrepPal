from pydantic import BaseModel


spell_check_instructions = 'Given the following piece of writing, \
find all the spelling mistakes in the text. \
Output the mistakes as JSON with the following format:'

spell_check_format = '{{"mistakes": ["<spelling mistake 1>", "<spelling mistake 2>", ...]\
"correction":["<correct spelling 1>", "<correct spelling 2>, ...]}}'

spell_check_system_prompt = f"{spell_check_instructions}\n{spell_check_format}"

same_meaning_system_prompt = """You are a helpful assistant that helps students practice for their english proficieny exams. \
Given the following two words enclosed in double square brackets [[]], \
determine if they are synonyms or have the similar meaning. \
Format the output as 'True' or 'False', nothing else. 'True' if they have the similar meaning, \
'False' otherwise."""

def same_meaning_user_prompt(word1, word2):
    return f"Two words to compare: [[{word1}]], [[{word2}]]"
              
        
class WritingScore(BaseModel):
    task_achievement_score: int
    coherence_and_cohesion_score: int
    lexical_resource_score: int
    grammatical_range_and_accuracy_score: int
    overall_score: int
    
    

