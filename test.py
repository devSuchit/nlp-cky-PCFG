import os
import sys
from pcky import parse, find_best


def main():
	if len(sys.argv) != 3:
		print("   Usage: python3 test.py <grammar_file> <sentence>")
		print("   Example: python3 test.py grammar.cfg \"I prefer the morning flight through Denver\"")
		sys.exit()

	filename = sys.argv[1]
	if not os.path.isfile(filename):
		print("ERROR. File '"+str(filename)+"' not found")
		sys.exit()

	sentence = sys.argv[2]
	if sentence[0] == "\"" and sentence[-1] == "\"": sentence = sentence[1:-1]
	sentence = sentence.lower()
	
	forest = parse(filename, sentence, debug=False)
	for tree in forest:
		tree.print()
		print()

	best = find_best(forest)
	if best: 
		print("Best parse tree found:")
		best.print(print_probs=True)
	else: print("This is not a valid sentence according to the grammar")

if __name__ == '__main__':
	main()


