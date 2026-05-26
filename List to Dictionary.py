def test(lst):
    result = {}
    for item in lst:
        result[item[0]] = item[1:]
    return result


students = [[1, 'Jean Castro', 'V'],[2, 'Lula Powwel', 'V'],[3, 'Brian Howwel', 'VI'],[4, 'lynne Foster', 'VI'],[5, 'Ryan', 'VII']]


print("\nOriginal list of lists:")
print(students)
print("\Converted lists to a dictionary:")
print(test(students))