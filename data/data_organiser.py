import csv
import re

test_size = 15
num_of_tests = 200

with open("data/original_j6000.csv", encoding="utf-8") as f:
    reader = csv.reader(f)

    headers = next(reader)
    print(headers)

    with open("src/data/j6000.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["question","answer","furi","name"])

        for i, line in enumerate(reader):
            jp = line[headers.index("Vocab-expression")]
            en = line[headers.index("Vocab-meaning")]
            fu = line[headers.index("Vocab-furigana")]

            fus = []
            capture = False
            for c in fu:
                if c == "[":
                    capture = True
                    fus.append("")
                elif c == "]":
                    capture = False
                elif capture:
                    fus[-1] += c
            
            fu = ", ".join(fus)

            row = [en,jp,fu]

            if i % test_size == 0:
                row.append(f"Vocab {i//test_size + 1}")

            writer.writerow(row)

            if i == test_size * num_of_tests - 1:
                break