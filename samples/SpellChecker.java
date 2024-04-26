// from the program by Farshad Rum
// simplified a little by eoneil for class solutions.
package cs310;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Scanner;
import java.util.Set;
import java.util.TreeSet;

public class SpellChecker {
	/*
	 * misspelled is a map from the misspelled words to list of lines where
	 * they happened. .
	 */
	private Map<String, List<Integer>> misspelled = new HashMap<String, List<Integer>>();
	// the dictionary in use to check words
	private Set<String> dictionary;

	// In this implementation, the dictionary is loaded outside SpellChecker 
	// and its Set<String> is passed in here. Alternatively, the constructor
	// could take the dictionary filename as an argument instead.
	public SpellChecker(Set<String> dic) {
		dictionary = dic;
	}

	// This is the main processing loop. It should be in an object method rather
	// than in main for greater reusability (we could have multiple
	// SpellCheckers built around different dictionaries in an app).
	// Note that this method throws on file not found, because it
	// doesn't know how to handle it. That's fine--let main take care of it.
	public void checkWords(String inFile) throws FileNotFoundException {

		Scanner in = new Scanner(new FileReader(inFile));
		int lineNum = 0;

		while (in.hasNextLine()) {
			String line = in.nextLine();
			lineNum++;
			// Alternatively here, assume spaces between words: line.split(" ");
			// Best way: split on white space as follows--
			String[] tokens = line.split("\\s+");
			// or use a Scanner for the line with next(), which by default uses
			// whitespace delimitation, or use a Scanner with a delimiter
			// set to a regular expression such as in the above comment.

			for (String word : tokens) {
				if (!dictionary.contains(word)) {
					List<Integer> lines = null;
					if ((lines = misspelled.get(word)) == null) {
						lines = new LinkedList<Integer>();
						misspelled.put(word, lines);
					}
					lines.add(lineNum);
				}
			}
		}
		in.close();

		/*
		 * After the analysis is done print the findings with each misspelled word
		 * followed by lines where it happened and list of possible corrections
		 */
		Set<String> words = misspelled.keySet();
		for (String word : words) {
			List<Integer> lines = misspelled.get(word);
			Set<String> alters = findAlternatives(word);
			System.out.println(word + " on " + lines +":   " + alters);
		}
	}

	/*
	 * Finds possible alternatives to a misspelled word.
	 */
	private Set<String> findAlternatives(String word) {
		List<String> list1 = addChar(word);
		List<String> list2 = removeChar(word);
		List<String> list3 = xchangeChar(word);

		Set<String> alterSet = new HashSet<String>();
		alterSet.addAll(list1);
		alterSet.addAll(list2);
		alterSet.addAll(list3);
		// In this implementation, the alternatives are first collected, then checked
		// against the dictionary. Alternatively (and arguably better), check them
		// during the process of collecting them.
		Iterator<String> iter = alterSet.iterator();
		while (iter.hasNext()) {
			String alter = iter.next();
			if (!dictionary.contains(alter))
				iter.remove();
		}
		return alterSet;
	}

	/*
	 * Returns a list of possible words composed by adding a character to anywhere
	 * in the given word
	 */

	private static List<String> addChar(String aWord) {
		StringBuilder wordBuff = new StringBuilder(aWord);
		List<String> result = new ArrayList<String>();
		for (int i = 0; i <= aWord.length(); i++) {
			for (char ch = 'a'; ch <= 'z'; ch++) {
				String alter = wordBuff.insert(i, ch).toString();
				// we could check if it's in the dictionary at this point
				// in this solution, that is done later
				result.add(alter);
				wordBuff.delete(i, i + 1);
			}
		}
		return result;
	}

	/*
	 * Returns a list of possible alternatives by removing one character from
	 * anywhere in the word
	 */

	private static List<String> removeChar(String aWord) {
		StringBuilder wordBuff = new StringBuilder(aWord);
		List<String> result = new ArrayList<String>();
		for (int i = 0; i < aWord.length(); i++) {
			char ch = wordBuff.charAt(i);
			String alter = wordBuff.deleteCharAt(i).toString();
			result.add(alter);
			wordBuff.insert(i, ch);
		}
		return result;

	}

	/*
	 * Returns a list of words by exchanging adjacent characters in the misspelled
	 * word.
	 */
	private static List<String> xchangeChar(String aWord) {

		List<String> result = new ArrayList<String>();
		for (int i = 0; i < aWord.length() - 1; i++) {
			StringBuilder wordBuff = new StringBuilder(aWord);
			char ch = wordBuff.charAt(i + 1);
			wordBuff.deleteCharAt(i + 1);
			String alter = wordBuff.insert(i, ch).toString();
			result.add(alter);
		}
		return result;
	}

	// helper to main: load word files into main dictionary
	// Alternatively, add this responsibility to SpellChecker itself
	public static void loadDictionary(Set<String> dic, String dictFile) throws FileNotFoundException {
		Scanner fileIn = new Scanner(new FileReader(dictFile));
		while (fileIn.hasNext()) {
			dic.add(fileIn.next());
		}
		fileIn.close();
	}

	public static void main(String[] args) {

		if (args.length != 2)
			System.out.println("Please provide your input document followed the dictionary file.");
		String inFile = args[0];
		String dictionary = args[1];
		Set<String> dic = new TreeSet<String>();
		try {
			// one way: load dictionary into a Set<String> before creating SpellChecker
			// Alternatively, have SpellChecker do the dictionary load itself
			loadDictionary(dic, dictionary);
			// create a SpellChecker with the dictionary
			SpellChecker checker = new SpellChecker(dic);
			// check words in inFile and report on them
			checker.checkWords(inFile);
		} catch (FileNotFoundException e) {
			System.err.println("File not found: " + e);
			e.printStackTrace(); // for debugging (remove for production version)
		}

	}

}