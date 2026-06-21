file = open("bucket-list.txt", "w")
file.write("1.Visit the Eifel tower\n")
file.write("2.Learn to play the guitar\n")
file.write("3.Code my own game\n")
file.close()
print("Bucket list saved to bucket-list.txt!")


file = open("bucket-list.txt", "r")
content = file.read()
print("\n=== My Bucket list ===")
print(content)
file.close()


file = open("bucket-list.txt", "r")
lines = file.readlines()
print(f"You have {len(lines)} items on your bucket list.")
file.close()


file = open("bucket-list.txt", "a")
file.write("4.Travel to Japan\n")
file.write("5.Run a 5k marathon\n")
file.close()
print("\n2 more items added")

file = open("bucket-list.txt", "r")
print("\n=== Updated Bucket list===")
print(file.read())
file.close()

