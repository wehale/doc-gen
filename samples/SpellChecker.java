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
	private Map<String, List<Integer>> misspelled = new HashMap<String, List<Integer>>();
	private Set<String> dictionary;

	public SpellChecker(Set<String> dic) {
		dictionary = dic;
	}

	public void checkWords(String inFile) throws FileNotFoundException {

		Scanner in = new Scanner(new FileReader(inFile));
		int lineNum = 0;

		while (in.hasNextLine()) {
			String line = in.nextLine();
			lineNum++;
			String[] tokens = line.split("\\s+");

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

		Set<String> words = misspelled.keySet();
		for (String word : words) {
			List<Integer> lines = misspelled.get(word);
			Set<String> alters = findAlternatives(word);
			System.out.println(word + " on " + lines +":   " + alters);
		}
	}

	private Set<String> findAlternatives(String word) {
		List<String> list1 = addChar(word);
		List<String> list2 = removeChar(word);
		List<String> list3 = xchangeChar(word);

		Set<String> alterSet = new HashSet<String>();
		alterSet.addAll(list1);
		alterSet.addAll(list2);
		alterSet.addAll(list3);

		Iterator<String> iter = alterSet.iterator();
		while (iter.hasNext()) {
			String alter = iter.next();
			if (!dictionary.contains(alter))
				iter.remove();
		}
		return alterSet;
	}

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
			loadDictionary(dic, dictionary);
			SpellChecker checker = new SpellChecker(dic);
			checker.checkWords(inFile);
		} catch (FileNotFoundException e) {
			System.err.println("File not found: " + e);
			e.printStackTrace();
		}

	}
}