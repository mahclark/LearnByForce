import csv
from collections import OrderedDict
from dataclasses import dataclass


class NoChange:
    pass

@dataclass
class Correction:
    en : str = NoChange
    jp : str = NoChange
    fu : str = NoChange

    def correct(self, en, jp, fu):
        return (
            en if self.en == NoChange else self.en,
            jp if self.jp == NoChange else self.jp,
            fu if self.fu == NoChange else self.fu
        )

corrections = {
    ("未[ま]だ", "yet, more") : Correction("not yet, still"),
    ("洋服[ようふく]", "clothes") : Correction("clothes (western style)"),
    ("ふらふら", "weak") : Correction("dizzy, unsteady, for no particular reason"),
    ("開[ひら]く", "to open") : Correction("to be opened"),
    ("開[あ]く", "to open") : Correction("to be opened"),
    ("閉[と]じる", "to close") : Correction("to shut, to close"),
    ("新[あら]た", "new, fresh") : Correction("newly, freshly", jp="新たに", fu="新[あら]たに"),
    ("私[わたし]", "I") : Correction("I, me"),
    ("俺[おれ]", "I, me") : Correction("I, me (masculine, informal)"),
    ("作業[さぎょう]", "work, operation") : Correction("tasks, work"),
    ("始[はじ]まる", "to begin") : Correction("to be started"),
    ("出掛[でか]ける", "to go out, to be about to go out") : Correction("to go out (and do something)"),
    ("続[つづ]ける", "to continue, to keep up") : Correction("to continue (doing something)"),
    ("用[もち]いる", "to use, to make use of") : Correction("to use"),
    ("場所[ばしょ]", "place, space") : Correction("place"),
    ("思[おも]う", "to think") : Correction("to think (opinion, feeling)"),
    ("考[かんが]える", "to think, to consider") : Correction("to think, to ponder"),
    ("位置[いち]", "position, place") : Correction("position, standing"),
    ("おっしゃる", "to say") : Correction("to utter, to express"),
    ("言[い]い 表[あら]わす", "to express, to say") : Correction("to utter, to express"),
    ("近[ちか]い", "near, soon") : Correction("near, nearby"),
    ("近[ちか]く", "near, close to") : Correction("near, nearby"),
    ("近[ちか]く", "vicinity, nearby") : Correction("near, nearby"),
    ("そば", "side, vicinity") : Correction("buckwheat noodles, next to"),
    ("そば", "buckwheat noodles, soba") : Correction("buckwheat noodles, next to"),
    ("辺[へん]", "vicinity, part") : Correction("vicinity, side, edge"),
    ("一帯[いったい]", "area, vicinity") : Correction("whole area, stretch of land"),
    ("もう", "already, yet, another, again") : Correction("already, more"),
    ("込[こ]める", "to put in, to concentrate on") : Correction("to put in (effort), to load/charge"),
    ("いかが", "how, what") : Correction("how, how about"),
    ("正面[しょうめん]", "front, face") : Correction("front, face, facade"),
    ("終[お]わる", "to finish, to end") : Correction("to end, to finish (intransitive)"),
    ("暮[く]らす", "to live, to earn one's livelihood") : Correction("to live, to earn a living"),
    ("帰[かえ]る", "to return, to go back") : Correction("to return (home)"),
    ("後[あと]", "after") : Correction("after, afterwards"),
    ("より", "more, further") : Correction("than, since"),
    ("一層[いっそう]", "more, even more") : Correction("even more"),
    ("広[ひろ]い", "wide, big") : Correction("spacious"),
    #() : Correction(""), 202
    
    ("一番[いちばん]", "most") : Correction("no. 1, most"),
}

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
            en = line[headers.index("Vocab-meaning")]
            jp = line[headers.index("Vocab-expression")]
            fu = line[headers.index("Vocab-furigana")]
            part = line[headers.index("Vocab-pos")]

            # add "to" in front of each verb
            if part == "Verb":
                en = ", ".join(["to " + e for e in en.split(", ")])
            
            # apply corrections
            if (fu, en) in corrections:
                en, jp, fu = corrections.pop((fu, en)).correct(en, jp, fu)
            
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
    
    if len(corrections) > 0:
        print(f"Warning: unable to find correction matches for:\n{corrections}")

    # group the items by english
    for test_item in jp_grouped:
        en, jp, fu = test_item.row()

        if en in idx_by_en:
            test_item = all_grouped[idx_by_en[en]]
            test_item.add_jp_fu(jp, fu)
        else:
            idx_by_en[en] = len(all_grouped)
            all_grouped.append(TestItem(en, jp, fu))
    
    # detect duplicates for correction
    ej = {}
    for test_item in all_grouped:
        for en in test_item.ens.keys():
            ej.setdefault(en, []).append(test_item)
    
    duplicates = {
        k : v
        for k, v in ej.items()
        if len(v) > 1
    }
    
    with open("data/duplicates.txt", "w", encoding="utf-8") as dup_txt:
        txt = f"{len(duplicates)}\n"
        for en, test_items in duplicates.items():
            txt += f"{en}:\n"
            for test_item in test_items:
                e, _, f = test_item.row()
                txt += f'\t"{f}", "{e}"\n'
        
        dup_txt.write(txt)


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
