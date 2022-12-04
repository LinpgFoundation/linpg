import linpg

testDict: dict = {}
testKeys: list = []

assert linpg.TypeSafeGetter.get_by_keys(testDict, testKeys) == {}

testKeys.append("k")

assert linpg.TypeSafeGetter.get_by_keys(testDict, testKeys, str(testKeys)) == str(testKeys)

testDict[testKeys[0]] = "test_value1"

assert linpg.TypeSafeGetter.get_by_keys(testDict, testKeys) == testDict[testKeys[0]]

testDict[testKeys[0]] = {}

testKeys.append("k2")

testDict[testKeys[0]][testKeys[1]] = "test_value2"

assert linpg.TypeSafeGetter.get_by_keys(testDict, testKeys) == testDict[testKeys[0]][testKeys[1]]

assert linpg.TypeSafeGetter.get_by_keys(testDict, testKeys[:1]) == testDict[testKeys[0]]

linpg.TypeSafeSetter.set_by_keys(testDict, testKeys, "changed_value")

assert linpg.TypeSafeGetter.get_by_keys(testDict, testKeys) == "changed_value"

testKeys2 = ["a,", "b", "c"]

linpg.TypeSafeSetter.set_by_keys(testDict, testKeys2, "changed_value2", False)

assert linpg.TypeSafeGetter.get_by_keys(testDict, testKeys2) == "changed_value2"
