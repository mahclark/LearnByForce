import csv
from collections import OrderedDict
from dataclasses import dataclass

def check_fu(fu):

    next_exp = {
        " ": "[",
        "[": "]",
        "]": " "
    }

    first_fu = True
    expected = " "
    for c in fu:
        if c in next_exp:
            if c == expected or first_fu and expected == " ":
                first_fu = False
                expected = next_exp[c]
            else:
                return False
    
    return expected == " "

def merge_fu(fu_a, fu_b):
    i_a = 0
    i_b = 0

    merge_splitter = "／"

    merged = ""

    while i_a < len(fu_a) and i_b < len(fu_b):
        c_a, c_b = fu_a[i_a], fu_b[i_b]
        assert c_a == c_b
        c = c_a

        merged += c

        if c == "[":
            a = ""
            while fu_a[i_a + 1] != "]":
                i_a += 1
                a += fu_a[i_a]

            b = ""
            while fu_b[i_b + 1] != "]":
                i_b += 1
                b += fu_b[i_b]
            
            fu_dict = OrderedDict.fromkeys(a.split(merge_splitter))
            fu_dict.update(OrderedDict.fromkeys(b.split(merge_splitter)))
            merged += merge_splitter.join(fu_dict)
        
        i_a += 1
        i_b += 1
    
    return merged

def format_fu(fu):
    fus = []

    rubied = False
    for c in fu:
        if c == " ":
            fus.append("<ruby>")
            rubied = True
        elif c == "[":
            fus.append("<rt>")
            if not rubied:
                fus = ["<ruby>"] + fus
        elif c == "]":
            fus.append("</rt></ruby>")
        else:
            fus.append(c)
    
    return "".join(fus)

class OrderedSet(OrderedDict):

    def __init__(self, itr):
        super().__init__()
        self.update(itr)

    def update(self, *iters):
        for itr in iters:
            for elem in itr:
                self.add(elem)
    
    def add(self, elem):
        self[elem] = None
    
    def join(self):
        return ", ".join(self.keys())

    
@dataclass
class TestItem:
    
    def __init__(self, en, jp, fu):
        self.ens = OrderedSet(en.split(", "))
        self.jps = OrderedDict([(jp, fu)])
    
    def set_fus_at(self, i, fu):
        fus = self.fus()
        fus[i] = fu
        self.fu = ", ".join(fus)
    
    def add_en(self, en):
        self.ens.update(en.split(", "))

    def add_jp_fu(self, jp, fu):
        if jp in self.jps:
            self.jps[jp] = merge_fu(self.jps[jp], fu)
        else:
            self.jps[jp] = fu
    
    def row(self):
        return (self.ens.join(), ", ".join(self.jps.keys()), ", ".join(self.jps.values()))


if __name__ == "__main__":

    test_size = 15

    idx_by_jp = {}
    idx_by_en = {}

    jp_grouped = []
    all_grouped = []

    # read original data
    with open("data/original_j6000.csv", encoding="utf-8") as f:
        reader = csv.reader(f)

        headers = next(reader)

        for i, line in enumerate(reader):
            core_id = int(line[headers.index("Core-index")])
            jp = line[headers.index("Vocab-expression")]
            en = line[headers.index("Vocab-meaning")]
            fu = line[headers.index("Vocab-furigana")]
            part = line[headers.index("Vocab-pos")]

            # add "to" in front of each verb
            if part == "Verb":
                en = ", ".join(["to " + e for e in en.split(", ")])
            
            # group the items by japanese
            if fu in idx_by_jp:
                test_item = jp_grouped[idx_by_jp[fu]]
                test_item.add_en(en)
            else:
                idx_by_jp[fu] = len(jp_grouped)
                jp_grouped.append(TestItem(en, jp, fu))
            
            if not check_fu(fu):
                print(f"badly formatted furigana (index {core_id})): {en}")

            # exclude the obscure vocab of above 4000
            if core_id == 4023:
                break

    # group the items by english
    for test_item in jp_grouped:
        en, jp, fu = test_item.row()

        if en in idx_by_en:
            test_item = all_grouped[idx_by_en[en]]
            test_item.add_jp_fu(jp, fu)
        else:
            idx_by_en[en] = len(all_grouped)
            all_grouped.append(TestItem(en, jp, fu))

    rows = [
        test_item.row()
        for test_item in all_grouped
    ]

    # write to the csv
    with open("src/data/j6000.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["question","answer","furi","name"])

        for i, (en, jp, fu) in enumerate(rows):

            row = [en, jp, ", ".join(map(format_fu, fu.split(", ")))]

            if i % test_size < 1:
                row.append(f"Vocab {i//test_size + 1}")

            writer.writerow(row)
