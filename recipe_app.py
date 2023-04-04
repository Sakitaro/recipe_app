import openai

openai.api_key = "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"

def request_recipe(ingredients_list):
    ingredients_text = ', '.join(ingredients_list)
    prompt = f"I have the following ingredients: {ingredients_text}. Can you suggest 3 different recipes? Answer with a numbered list."
    
    
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    recipes_text = response.choices[0].text.strip()
    recipes = recipes_text.split("\n\n")[:3] 

    return recipes
