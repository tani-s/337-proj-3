# "Vegetarian": someone that does not eat meat but does consume 
# animal products that do not require the death of that animal.
# i.e., milk, eggs, cheese, and butter allowed, but not meat.
#   replace all animal broths + stocks with veggie broth
#   replace all ground meat with beyond meat / ground meat alternative
#   replace all burgers/ patties with veggie burgers/patties
#           and sausages, meatballs, bacon, hot dogs
#   replace all steaks with vital wheat gluten "steak"
#   replace all kinds of fish with tempeh
#   replace shellfish (crab, scallops, clam, oyster, shrimp) with tofu
#   replace chicken with seitan
#   replace pork with portobello
#   replace all deli meats (sliced turkey, ham, etc) with seitan deli slices
#   replace fish sauce and oyster sauce with hoisin
#   TIL eel sauce is vegan

veg_sub = {
    'chicken': "seitan",
    "pork" : "portobello",
    'fish sauce': 'hoisin',
    'oyster sauce': 'hoisin',
    'pepperoni': 'seitan deli slices',
    'salami': 'seitan deli slices'
} 

animals = [
    'beef', 'veal', 'chicken', 'poultry', 'turkey', 'pork', 'ham', 'lamb', 'fish', 'seafood', 'fish' 
]

# can't forget plurals... 
products_2 = [
    'xxx bouillon', 'xxx broth', 'xxx stock', 'xxx juice',  'xxx sauce', 'xxx seasoning',
    'xxx patty', 'xxx burger', 'xxx sausage', 'xxx bacon', 'xxx meatball', 'xxx hot dog', 
    
]

products_1 = [
    'ground xxx', 'minced xxx', 'xxx filet',
]

steak_cuts = [
    'filet mignon', 'flank steak', 'top sirloin', 't-bone', 'rib eye', 'ribeye', 'skirt steak', 'strip steak', 
    'flat iron steak', 'brisket', 'ribs', 'chuck', 'shoulder'
]

fish = [
    'catfish', 'salmon', 'tuna', 'tilapia', 'swordfish', 'sardine', 'haddock', 'anchovy', 'mackerel', 'seabass', 
    'yellowtail', 'halibut', 'trout', 'cod'
]

seafood = [
    'clam', 'mussel', 'oyster', 'shrimp', 'prawn', 'crab', 'lobster', 'scallop', 'squid', 'eel', 'calamari', 
    'shellfish', 'crayfish'
]

for p in products_2:
    for a in animals:
        rep = p.replace("xxx", a)
        if rep not in veg_sub:
            veg_sub[rep] = p.replace("xxx", 'veggie')

for p in products_1:
    for a in animals:
        rep = p.replace("xxx", a)
        if rep not in veg_sub:
            veg_sub[rep] = p.replace("xxx", "plant-based alternative")

for s in steak_cuts:
    veg_sub[s] = "vital wheat gluten \"" + s + "\""

for f in fish:
    veg_sub[f] = "tempeh"

for sf in seafood:
    veg_sub[sf] = "tofu"

for a in animals: 
    f = 'sliced ' + a
    veg_sub[f] = 'seitan deli slices'

for a in animals:
    veg_sub[a] = 'veggie'

# print(veg_sub)