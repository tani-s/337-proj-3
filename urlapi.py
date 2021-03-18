import json
from bs4 import BeautifulSoup
import requests
from unicodedata import numeric
import nltk
import re
from pattern.en import pluralize
import string
import veggies
import pprint
import ingPy
from helper import get_after_prefix, apply, get_POS_after_prefix, contains
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))


url = 'https://www.allrecipes.com/recipe/273864/greek-chicken-skewers/'

url2 = 'https://www.allrecipes.com/recipe/228122/herbed-scalloped-potatoes-and-onions/'

url3 = 'https://www.allrecipes.com/recipe/166583/spicy-chipotle-turkey-burgers/?internalSource=hub%20recipe&referringContentType=Search'


# incomplete, but a start
# liters, gallons, oz, fl oz, bottle, abbreviations of the above, pint, mL, quarts, 
# clove, dash, pinch, cube, can, kg, strip, piece, slice, packet, package, head, bunch
nouns = ["NN","NNP","NNS"]
adj = ["JJ","JJR","JJS","DT"]

tools = {"cut": "knife",
        "chop": "knife",
        "slice": "knife",
        "mince": "knife",
        "whisk": "whisk",  # "whisk with a fork" is a possibility...
        "grate": "grater",
        "stir": "spoon",
        "grill": "grill"}

tool_phrases = ["using a", "use a", "with a", "in a", "in the"]
tool_phrases = apply(nltk.word_tokenize, tool_phrases)

tool_phrases2 = ["using", "use", "in"]
tool_phrases2 = apply(nltk.word_tokenize, tool_phrases2)

methods = ["bake", "fry", "sear", "saute", "boil", "braise", "poach", "mix"]

tools_2 = ["oven", "baking sheet", "baking dish", "pan", "saucepan", "skillet", "pot",
        "spatula", "fork", "foil", "knife", "whisk", "grater", "spoon"]

time_measure = ["second", "minute", "hour", "seconds", "minutes", "hours"]

health_sub = {"butter": "coconut oil",
        "sugar": "zero calorie sweetener",
        "lard": "coconut oil",
    "flour": "whole wheat flour",
"noodles": "whole grain pasta",
"spaghetti": "whole grain pasta",
"linguini": "whole grain pasta",
"penne": "whole grain pasta",
"bread": "whole wheat bread"
}


Lithuanian_sub = {"vegetable oil": "flaxseed oil", "coconut oil": "flaxseed oil", "olive oil": "flaxseed oil",
     "hot dog": "skilandis", "bratwurst": "skilandis", "salami": "skilandis",
     "beer": "farmhouse brewed beer", "wine": "fruit wine","coffee": "kava",
     "goose": "chicken", "mutton": "lamb", "veal": "lamb", "rabbit": "lamb",
     "walleye": "zander", "cod": "perch", "tuna": "pike",
     "basil": "bay leaf", "rosemary": "caraway", "thyme": "coriander" ,"parsley": "horseradish",
     "paprika": "coriander", "saffron": "oregano", "cumin": "horseradish", 
     "wheat bread": "rye bread", "bagel": "rye bread", "biscuit": "rye bread", "brioche": "rye",
     "ciabatta":"rye", "naan": "rye bread","pita": "rye bread", "chile": "garlic",
     "wasabi": "horseradish","fennel": "bay leaf","chives": "coriander","sage":"bay leaf",
     "lemon": "apple", "orange": "apricot", "pineapple": "plum", "banana": "pear",
     "lettuce": "cabbage",
     "swiss cheese": "dziugas", "blue cheese": "liliputas", "american cheese": "dziugas", "cheddar cheese": "dziugas",
     "parmesan": "dziugas","mozzarella": "dziugas", "brie": "liliputas"}

dairy_free_sub = {"milk": "soy milk", "butter": "coconut oil", "cream": "coconut cream", 
    "parmesan": "nutritional yeast", "yogurt": "applesauce", "mayonnaise": "vegenaise", "cheese": "vegan cheese"}



# given a URL, will return the name of the recipe
def get_recipe_name(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    recipe_name = soup.find("h1", class_="headline heading-content").text
    return recipe_name


# When given a url, returns a list of tools based on the tools dict defined at top
# We should probably add something to scan for ... Nouns? things like "oven", "pan", "plate", etc.
# Also for phrases like "With a spoon, xyz" or "use a spatula to xyz"
def get_tools(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    s = soup.find('script', type='application/ld+json')
    j = json.loads(s.string)
    instructions = j[1]['recipeInstructions']

    tool=set()  # so we don't get duplicates
    
    """
    tool1=set()
    for step in instructions:
        for word in step['text'].lower().split():
            if word in tools:
                tool1.add(tools[word])
    """
    
    for step in instructions:
        sent = step['text'].lower()
        words = nltk.word_tokenize(sent)
        for word in words:
            if word in tools:
                tool.add(tools[word])
        pos = nltk.pos_tag(words)
        #post_phrases = get_after_prefix(words, tool_phrases)
        post_phrases = get_POS_after_prefix(pos, tool_phrases2, adj, ignore=True)
        for pp in post_phrases:
            tool.add(pp)

    ing = ingPy.get_ingredients(url)
    for i in ing:
        ing_words = i.split()
        for w in ing_words:
            if w in tool:
                tool.remove(w)
            
    return tool

"""
get_tools(url)
get_tools(url2)
get_tools(url3)
"""

# returns a dict of steps, key = step number, value = action, ingredients, tools, time
def get_steps(url, isEnglish):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    s = soup.find('script', type='application/ld+json')
    j = json.loads(s.string)
    instructions = j[1]['recipeInstructions']
    ingredients = ingPy.get_ingredients(url)

    if isEnglish: 
        steps = []
        for step in instructions:
            steps.append(step['text'].lower().strip())
        return steps


    # splitting into individual steps (by sentence, and splitting up ;s)
    steps = []
    for step in instructions:
        ss = nltk.sent_tokenize(step['text'].lower().strip())
        for s in ss:
            if ";" in s:
                split = s.split("; ")
                steps.append(split[0])
                steps.append(split[1])
            else: steps.append(s)

    instruc = {}
    step_num = 0
    for step in steps:
        ingred = []
        tools = []
        action = []
        time = []
        toks = nltk.word_tokenize(step)
        pos = nltk.pos_tag(toks)

        # getting ingredients from looking through ingredients list from get_ingredients
        # parsing through those ingredients bc usually they'll just say 'chicken' instead of 'skinless chicken breast' for example
        for i in ingredients:
            if i in step:
                ingred.append(i)
            tok = nltk.word_tokenize(i)
            tok = nltk.pos_tag(tok)
            for word in tok:
                if word[0] in step and (word[1] == "NN" or word[1] == "NNS"):
                    ingred.append(word[0])
    
        ingred = checker(ingred)
        # getting tools, but from the list of commonly used tools at the top
        # could be altered to use get_tools
        for t in tools_2:
            if t in step:
                tools.append(t)
        
        # assuming first word is always an action verb, then also looking for other verbs
        action.append(pos[0][0])
        for word in pos:
            if word[1] == 'VB':
                action.append(word[0])
        
        # getting time...most steps dont have a time to it'll return an empty list for that
        for m in time_measure:
            if m in toks:
                #time = m
                index = toks.index(m)
                time.append(toks[index-1] + " " + toks[index])
                #time = index

        step_num += 1
        instruc[step_num] =  list(set(action)), list(set(ingred)), tools, time
    return instruc

#pprint.pprint(get_steps(url2))
#pprint.pprint(get_steps(url))

def checker(ingred):
    out = []
    for i in range(0, len(ingred)):
        temp = True
        for j in range(0, len(ingred)):
            if ingred[i] in ingred[j] and i != j:
                temp = False
        if temp:
            out.append(ingred[i])
    return out





def get_method(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    s = soup.find('script', type='application/ld+json')
    j = json.loads(s.string)
    instructions = j[1]['recipeInstructions']

    main_method = ""
    index = 12
    temp = -1
    for step in instructions:
        split = nltk.word_tokenize(step['text'].lower().strip())
        split = nltk.pos_tag(split)
        for i in split:
            if "VB" in i[1] and temp == -1:
                index = len(methods)
                main_method = i[0]
            if i[0] in methods:
                if (methods.index(i[0]) < temp and temp != -1) or temp == -1:
                    temp = methods.index(i[0])
                    main_method = i[0]

    return main_method

def healthify(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    s = soup.find('script', type='application/ld+json')
    j = json.loads(s.string)
    instructions = j[1]['recipeInstructions']

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    s = soup.find('script', type='application/ld+json')
    j = json.loads(s.string)
    ingredients = j[1]['recipeIngredient']

    ing_dict = {}
    for ing in ingredients:
        lst = ingPy.parse_ingredients(ing)
        ing_dict[health_sub_help(lst[2])] = [lst[0], lst[1], lst[3], lst[4], lst[5]]

    steps = []
    for step in instructions:
        steps.append(health_sub_help(step['text'].lower().strip()))
    return ing_dict, steps


def health_sub_help(step):
    next = step
    for i in health_sub:
        next = next.replace(i, health_sub[i])
    return next

def double(recipe): 
    ing = recipe['ingredients']
    for key in ing:
        if ing[key][0] is not None:
            if 0.5 < ing[key][0] <= 1 and ing[key][1] is not None:
                ing[key][1]= pluralize(ing[key][1])
                # make plural
            ing[key][0] *= 2
            #print(ing[key])

    doubled = {
        'name': recipe['name'],
        'ingredients': ing,
        'tools': recipe['tools'],
        'method': recipe['method'],
        'steps': recipe['steps'],
    }
    return doubled



def halve(recipe): 
    ing = recipe['ingredients']
    p = nltk.PorterStemmer()
    
    for key in ing.copy():
        if ing[key][0] is not None:
            if 1 < ing[key][0] <= 2:  # plurals need changing
                if ing[key][1] is not None:
                    ing_lst = ing[key][1].split()
                    i = 0
                    for word,pos in nltk.pos_tag(ing_lst):
                        #print(word, pos)
                        if pos == 'NNS':
                            ing_lst[i] = p.stem(word)
                        i += 1
                    ing[key][1] = ' '.join(ing_lst)
                    ing[key][0] /= 2
                
                else: # the plural that needs changing is in the desc, not the measure
                    ing_lst = key.split()
                    i = 0
                    for word,pos in nltk.pos_tag(ing_lst):
                        if pos == 'NNS':
                            ing_lst[i] = p.stem(word)
                        i += 1
                    
                    new_key = ' '.join(ing_lst)
                    new_val = ing[key]
                    del ing[key]
                    ing[new_key] = new_val
                    ing[new_key][0] /= 2
                    
                # could be chicken BREASTS or CLOVES garlic
                # de-pluralize
            else: 
                ing[key][0] /= 2
            #print(ing[key])

    halved = {
        'name': recipe['name'],
        'ingredients': ing,
        'tools': recipe['tools'],
        'method': recipe['method'],
        'steps': recipe['steps'],
    }
    return halved

def transform(url, food_sub):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    s = soup.find('script', type='application/ld+json')
    j = json.loads(s.string)
    instructions = j[1]['recipeInstructions']

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    s = soup.find('script', type='application/ld+json')
    j = json.loads(s.string)
    ingredients = j[1]['recipeIngredient']

    ing_dict = {}
    for ing in ingredients:
        lst = ingPy.parse_ingredients(ing)
        ing_dict[transform_help(lst[2], food_sub)] = [lst[0], lst[1], lst[3], lst[4], lst[5]]

    steps = []
    for step in instructions:
        steps.append(transform_help(step['text'].lower().strip(), food_sub))
    return ing_dict, steps

def transform_help(step, food_sub):
    next = step
    for i in food_sub:
        next = next.replace(i, food_sub[i])
    return next

"""
print(transform(url, Lithuanian_sub))
print(transform(url2, Lithuanian_sub))
print(transform(url3, Lithuanian_sub))
"""

# credit for this function to https://stackoverflow.com/questions/4664850/how-to-find-all-occurrences-of-a-substring
def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def url_to_recipe(url):
    recipe = {
        'name': get_recipe_name(url),
        'ingredients': ingPy.get_ingredients(url),
        'tools': get_tools(url),
        'method': get_method(url),
        'steps': get_steps(url, True),
    }
    return recipe

#print(ingredients.get_ingredients(url))
#print(ingredients.get_ingredients(url2))
#print(get_tools(url2))
#print(get_steps(url2))
#print(get_method(url2))
#print(healthify(url2))
#print(double(url_to_recipe(url2))['ingredients'])

# print(url_to_recipe(url2))

#print(transform(url, veggies.veg_sub))

#print(transform(url2, veggies.veg_sub))

#print(transform(url2, dairy_free_sub))
def url_to_transform(url, transform):
    ing, steps = transform(url)
    
    recipe = {
        'name': get_recipe_name(url),
        'ingredients': ing,
        'tools': get_tools(url),
        'method': get_method(url),
        'steps': steps,
    }
    return recipe

def url_to_transform_gen(url, third):
    ing, steps = transform(url, third)
    
    recipe = {
        'name': get_recipe_name(url),
        'ingredients': ing,
        'tools': get_tools(url),
        'method': get_method(url),
        'steps': steps,
    }
    return recipe

def veg_transform(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    s = soup.find('script', type='application/ld+json')
    j = json.loads(s.string)
    instructions = j[1]['recipeInstructions']

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    s = soup.find('script', type='application/ld+json')
    j = json.loads(s.string)
    ingredients = j[1]['recipeIngredient']

    ing_dict = {}
    for ing in ingredients:
        lst = ingPy.parse_ingredients(ing)
        ing_dict[veg_transform_help(lst[2])] = [lst[0], lst[1], lst[3], lst[4], lst[5]]

    steps = []
    for step in instructions:
        steps.append(veg_transform_help(step['text'].lower().strip()))
    return ing_dict, steps

def veg_transform_help(step):
    n = step
    for k in sorted(veggies.veg_sub, key= len, reverse=True):  # longest (more detailed) transforms first
        rep = r"\b" + k  # only make tranformations on words at the word boundary
        n = re.sub(rep, veggies.veg_sub[k], n)
    return n

#print(veg_transform(url))
#print(veg_transform(url2))

def printStep(steps):
    for i in range(1, len(steps) + 1):
        print ("step number " + str(i))
        temp = ", "
        temp = temp.join(steps[i][0])
        print("     actions: " + temp)
        if len(steps[i][1]) > 0:
            temp = ", "
            temp = temp.join(steps[i][1])
            print("     ingredients: " + temp)
        else:
            print("     no ingredients")
        if len(steps[i][2]) > 0:
            temp = ", "
            temp = temp.join(steps[i][2])
            print("     tools: " + temp)
        else:
            print("     no tools")
        if len(steps[i][3]) > 0:
            temp = ", "
            temp = temp.join(steps[i][3])
            print("     time: " + temp)
        else:
            print("     no time")

def printCount(steps):
    for i in range(1, len(steps) + 1):
        print("     " + str(i) + ": " + steps[i - 1])

def main():
    url = input("Ayyyyo whasss Gucci! It's cha boi, Sir Pickles Von Quackmeister III here to help you with your recipe! Enter a URL to parse!\n")
    while "allrecipes" not in url:
        url = input("This URL doesn't work (must be AllRecipes). Try again:")
    
    run = True
    while run:
        # get a transform
        function = input('''What would you like to do? \n 
        [a] Parse as-is
        [b] Transform to vegetarian 
        [c] Parse with recipe doubled
        [d] Parse with recipe halved
        [e] Transform to Lithuanian
        [f] Transform to healthy
        ''')
        recipe = None
        if function == 'a' or function == 'A' or contains(function, "as-is") or contains(function, "as is"):
            recipe = url_to_recipe(url)
        elif function == 'b' or function == 'B' or contains(function, "vegetarian"):
            recipe = url_to_transform(url, veg_transform)
        elif function == 'c' or function == 'C' or contains(function, "double"):
            recipe = double(url_to_recipe(url))
        elif function == 'd' or function == 'D' or contains(function, "half") or contains(function, "halve"):
            recipe = halve(url_to_recipe(url))
        elif function == 'e' or function == 'E' or contains(function, "lithuanian"):
            recipe = url_to_transform_gen(url, Lithuanian_sub)
        elif function == 'f' or function == 'F' or contains(function, "health"):
            recipe = url_to_transform_gen(url, health_sub)
        elif function == 'q' or function == 'Q' or function == 'quit' or function == "Quit":
            print("Okay! Bye!")
            run = False
            break
        else: 
            print("Sorry, I didn\'t understand that. You can enter 'Q' at any time to quit.")
            run = True
        
        # print information (basic goal 1, to expand on this we could use regex to scan for keywords)
        step = 0
        prevStep = -1
        if recipe:
            print("Ok, let's do that with your recipe, \'%s\'. " % recipe['name'])
        while recipe:
            function = input('''What would you like to see? \n 
            [a] Ingredients
            [b] Steps 
            [c] Tools
            [d] Methods
            [e] All of the above
            [f] I have a question.
            ''')
            if function == 'a' or function == 'A' or contains(function, "ingredient"):
                ingPy.ing_print(recipe['ingredients'])
            elif function == 'b' or function == 'B' or contains(function, "step"):
                oneByOne = None
                while not oneByOne:
                    oneByOne = input('Would you like [1] one step at a time or [2] all steps now?\n')
                    if oneByOne == "2" or  contains(oneByOne, "all"):
                        print_steps(recipe)
                    elif oneByOne == "1" or contains(oneByOne, "one"):
                        print("You can tell me to go forward, backward, start over, or go to a particular step at any time.")
                        print("Your recipe has " + str(len(recipe['steps'])) + ' steps.')
                        print_step(recipe, step)
                        prevStep = step
                        step += 1
                    else:
                        print('Hmm, I didn\'t catch that.')
                        oneByOne = None
            elif function == 'c' or function == 'C' or contains(function, "tool"):
                print_tools(recipe)
            elif function == 'd' or function == 'D' or contains(function, "method"):
                print_methods(recipe)
            elif function == 'e' or function == 'E' or contains(function, "all"):
                print_all(recipe)
            elif function == 'f' or function == 'F' or contains(function, "question"):
                handle_question(recipe, prevStep)

            elif function == 'q' or function == 'Q' or function == 'quit' or function == "Quit":
                print("Okay! Bye!")
                recipe = False
                run = False
                break

            # navigate forward and back a step at a time (goal 2, complete)
            elif 'forward' in function or 'next' in function:
                doStep = True
                if 'step' not in function:
                    check = input("To be clear, you'd like to see the next step? [1] Yes [2] No \n")
                    if check == '2': doStep = False
                if doStep:
                    if step < len(recipe['steps']) - 1:
                        #step += 1
                        print_step(recipe, step)
                        prevStep = step
                        step += 1
                    else:
                        print("There is no next step! Here is the last step: ")
                        prevStep = step
                        step = len(recipe['steps']) - 1
                        print_step(recipe, step)

            elif 'backward' in function or 'back' in function or 'previous' in function:
                doStep = True
                if 'step' not in function:
                    check = input("To be clear, you'd like to see the previous step? [1] Yes [2] No \n")
                    if check == '2': doStep = False
                if doStep:
                    if step > 0:
                        prevStep = step
                        step -= 1
                        print_step(recipe, step)
                    else:
                        print("There is no previous step! Here is the first step: ")
                        print_step(recipe, 0)
                        prevStep = step
                        step = 0

            elif re.search(r"\bstep\b", function): # the word "step" with word boundaries at either side
                found = False
                for word in function.lower().split():
                    nth = re.match(r"([0-9]+)", word)
                    if nth:
                        found = True
                        num = nth.group(0)
                        if int(num) > 0 and int(num) < len(recipe['steps']) + 1:
                            print("Here is step " + nth.group(0) + ':')
                            step = int(num) - 1
                            print_step(recipe, step)
                        else:
                            print("Sorry, that step number is out of bounds.")
                            print("Your recipe has " + str(len(recipe['steps'])) + ' steps.')
                if not found:
                    print('Sorry, which step would you like to see? Please use numerals rather than spelled out words.')

            else:
                print("Sorry, I didn\'t understand that. You can enter 'Q' at any time to quit.")



def handle_question(recipe, step):
    # here we handle specific how-to questions (goal 4, to expand we will need other question forms)
    # for now, i'm only taking questions of the form "How do I <xyz>?"
    # we will also need to handle "vague questions" like "how do i do that" (goal 3)
    #   this will require the bot to know what it has previously said
    # for an extra goal, we could add something like "how much x do i need" and answer with ingredients
    #                   or "how long do i bake this for" and answer with the time from the relevant step
    question = None
    while not question:
        question = input("Okay! What's your question? \n")
        q = question.lower()
        if q[:16] == 'how do i do that':
            if step == -1:
                print("I'm not sure what you mean.")
            else:
                print("I found this on the web.")
                key = slice_step(recipe['steps'][step])
                print(get_link_from_q(key))
        elif q[:9] == 'how do i ':
            print('''I found this on the web for "%s":
            ''' % question)
            print(get_link_from_q(q[9:]))
        elif q[:8] == 'what is ':
            print('''I found this on the web for "%s":
            ''' % question)
            print(get_link_from_q_what(q[8:]))
        elif q[:9] == 'what are ':
            print('''I found this on the web for "%s":
            ''' % question)
            print(get_link_from_q_what(q[9:]))
        elif q[:9] == 'how much ' or q[:9] == 'how many ':
            print(get_ingredient_quantity(q[9:], recipe))
        else:
            print('''I'm sorry, I don't know how to help you with that question yet.
            Try asking questions of the form "How do I..."
            ''')

def get_ingredient_quantity(string, recipe):
    print(recipe['ingredients'])
    for i in recipe['ingredients']:
        if i in string:
            if recipe['ingredients'][i][1] == None:
                print("You need " + str(recipe['ingredients'][i][0]) + " of " + i)
            else:
                print("You need " + str(recipe['ingredients'][i][0]) + " " + recipe['ingredients'][i][1] + " of " + i)
            return
    print("I couldn't find that ingredient in your current recipe. Are you sure that you need it for this?")
    return




def slice_step(step):
    done = False
    keys = ""
    splits = step.split()
    for i in splits:
        if i == "for" or i == "to" or i == "and" or "into":
            done = True
        elif i == ".":
            break
        elif i == ",":
            keys = ""
            done = False
        if not(done):
            keys = keys + " " + i
    return keys

def get_link_from_q(q):
    q = q.translate(str.maketrans('', '', string.punctuation))
    query = []
    for word in q.split(' '):
        if word not in stop_words:
            query.append(word)
    link ='https://www.google.com/search?q=how+to'
    for word in query:
        link += '+' + word
    return link

def get_link_from_q_what(q):
    q = q.translate(str.maketrans('', '', string.punctuation))
    query = []
    for word in q.split(' '):
        if word not in stop_words:
            query.append(word)
    link ='https://www.google.com/search?q='
    for word in query:
        link += word + '+'
    return link[:-1]

def print_all(recipe):
    print('Recipe name: ' + recipe['name'])
    ingPy.ing_print(recipe['ingredients'])
    print_tools(recipe)
    print_methods(recipe)
    print_steps(recipe)

def print_tools(recipe):
    print('Tools: %s' %recipe['tools'])

def print_methods(recipe):
    print('Primary method: %s' %recipe['method'])

def print_steps(recipe):
    print('Steps: ')
    printCount(recipe['steps'])

def print_step(recipe, i):
    print('Step ' + str(i + 1) + ': ')
    print(recipe['steps'][i])

main()

#print(double(url_to_recipe(url2)))
#print(halve(url_to_recipe(url2)))


