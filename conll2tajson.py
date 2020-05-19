import codecs
import json
import os
import sys

# This file converts a folder full of labeled text file in CONLL Format (one token and one label per line)
# into a folder of tajson files.

# Usage:
# $ conll2tajson.py input_folder output_folder


def lines2json(lines, fname):
    """ This takes a set of lines (read from some text file)
    and converts them into a JSON TextAnnotation. This assumes
    that there is one sentence per line, whitespace tokenized. """

    doc = {}
    doc["corpusId"] = ""
    doc["id"] = fname

    sents = {}
    sentends = []
    tokens = []
    toks = []

    tokenOffsets = []
    startCharOffset = 0

    constituents_ner = []
    prevLabel = 'O'
    startNerOffset = 0
    start = True

    constituents_token = []

    for line in lines:
        if len(line) > 1:
            word = line.split(' ')
            toks.append(word[0])

            # Token Offset
            endCharOffset = startCharOffset + len(word[0])
            tokenOffsets.append({
                'form' : word[0],
                'startCharOffset' : startCharOffset,
                'endCharOffset' : endCharOffset
            })
            startCharOffset = endCharOffset + 1

            # View NER CONLL
            if start:
              start = False
              if word[1] == 'O':
                prevLabel = word[1]
              else:
                prevLabel = word[1][2:]
              startNerOffset += 1
              continue

            if word[1] == 'O':
              if prevLabel != 'O':
                endNerOffset = len(tokens) + len(toks)
                constituents_ner.append({
                  'label' : prevLabel[2:],
                  'score' : 1.0,
                  'start' : startNerOffset,
                  'end' : endNerOffset - 1
                })
                startNerOffset = endNerOffset
              else:
                startNerOffset += 1
              prevLabel = word[1]

            elif prevLabel != word[1]:
              if prevLabel != 'O' and word[1][:2] == 'B-':
                endNerOffset = len(tokens) + len(toks) 
                constituents_ner.append({
                  'label' : word[1][2:],
                  'score' : 1.0,
                  'start' : startNerOffset,
                  'end' : endNerOffset - 1
                })
                startNerOffset = endNerOffset - 1
              prevLabel = word[1]

        else:
            tokens.extend(toks)
            sentends.append(len(tokens))
            toks = []

    tokens.extend(toks)
    sentends.append(len(tokens))

    print(tokens[92810:92812])

    doc["text"] = " ".join(tokens)
    doc["tokens"] = tokens

    sents["sentenceEndPositions"] = sentends
    sents["score"] = 1.0
    sents["generator"] = "conll2tajson.py"
    doc["sentences"] = sents
    doc["tokenOffsets"] = tokenOffsets

    doc["views"] = [{
      "viewName": "NER_CONLL",
      "viewData": [
        {
          "viewType": "edu.illinois.cs.cogcomp.core.datastructures.textannotation.SpanLabelView",
          "viewName": "NER_CONLL",
          "generator": "conll2tajson.py",
          "score": 1.0,
          "constituents" : constituents_ner
        }]
      }]

    return doc


def convert(infolder, outfolder):
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)

    for fname in os.listdir(infolder):
        with open(infolder + "/" + fname) as f:
            lines = f.readlines()
        with codecs.open(outfolder + "/" + fname, "w", encoding="utf-8") as out:
            doc = lines2json(lines, fname)
            json.dump(doc, out, sort_keys=True, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: txt2tajson.py input_folder output_folder")
        exit(1)

    infolder = sys.argv[1]
    outfolder = sys.argv[2]
    convert(infolder, outfolder)
