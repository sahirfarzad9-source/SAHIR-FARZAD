pasta = ("Pasta Arrabiata", "Italian", 20, "medium")
biryani = ("Chicken biryani", "Pakistani", 45, "hard")
print("Recipe 1", pasta)
print("Name",pasta[0])
print("Cuisine:", pasta[1])
print("Difficulty",[-1])

all_recipes = (pasta, biryani)
print("\nFirst recipe name:", all_recipes[0][0])
print("Second recipe time:",all_recipes[1][2], "mins")
print("Pasta details (sliced):", pasta[1:3])

print("\nPasta Recipe Details:")
for detail in pasta:
    print(" -", detail)

pasta_ingredients = {"tomato","garlic","olive oil","chilli","pasta"}
biryani_ingredients = {"rice","chicken","garlic","onion","tomato","spices"}
print("\nPasta ingredients:", pasta_ingredients)
print("Biryani ingredients:", biryani_ingredients)
print("Total pasta ingredients:", len(pasta_ingredients))

pasta_ingredients.add("parmesan")
pasta_ingredients.discard("chilli")
print("\nUpdated pasta ingredients:", pasta_ingredients)

all_ingredients = pasta_ingredients.union(biryani_ingredients)
common = pasta_ingredients.intersection(biryani_ingredients)
only_pasta = pasta_ingredients.difference(biryani_ingredients)
uniqe_to_each = pasta_ingredients.symmetric_difference(biryani_ingredients)

print("\nAll ingredients (union):",all_ingredients)
print("Common ingredients (intersetction)",common)
print("Only in pasta (difference)",only_pasta)
print("Not shared(symmetric difference)",uniqe_to_each)
