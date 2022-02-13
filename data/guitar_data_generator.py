import csv

with open('src\\data\\music.csv', 'w', newline='') as f:
    writer = csv.writer(f)

    writer.writerow(['question','answer','furi','name'])

    notes = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
    bk = ':'#•
    fb = f'[ | |{bk}| |{bk}| |{bk}| |{bk}| | |'

    for st in ['E','A','D','G','B']:
        writer.writerow([fb, st, '', f'{st} String'])

        for fret in range(1, 12):
            q = fb[:(fret-1)*2+1] + 'X' + fb[(fret-1)*2+2:]
            a = notes[(notes.index(st) + fret) % len(notes)]
            writer.writerow([q, a])