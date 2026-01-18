



synclist = {}
def populateSynclist(wo, signal):
    index = 0
    for w in wo:
        if w[0] == "sync":
            synclist[(signal, w[1])] = index
        else:
            index += w[1]

def advLetter(letter, i):
    return chr(ord(letter) + i)

letter = "A"
for wo in work:
    populateSynclist(wo, letter)
    letter = advLetter(letter , 1)
lastletter = letter

header = '{"blueprint": {"item": "blueprint", "label": "test", "tiles": [], "icons": [{"index": 1, "signal": {"name": "decider-combinator"}}], "schedules": [],"entities": ['

def makeEntity(index):
    return '{"entity_number": ' + str(index) + ', "name": "decider-combinator", "position": {"x": ' + str(index) + ', "y": 0}, "control_behavior": {"decider_conditions": {"outputs": [{"signal": {"type": "virtual", "name": "signal-each"}, "copy_count_from_input": false}], "conditions": ['
entityfooter = ']}}},'
footer = "]}}"

def makebody(first, red, green, comparator, constant, prev):
    return '{"first_signal": {"type": "virtual", "name": "' + first + '"}, "first_signal_networks": {"red": ' + red + ', "green": ' + green + '}, "constant": ' + constant + ', "comparator": "' + comparator + '", "compare_type": "' + prev + '"},'

def makesentinel():
    return '{"first_signal": {"type": "virtual", "name": "signal-X"}, "first_signal_networks": {"red": false, "green": false}, "constant": 5, "comparator": ">", "compare_type": "or"}'

def makeSyncStatement(sync, signal, conj):
    return  makebody("signal-" + signal, "true", "false", ">=", str(synclist[(signal,sync)]), conj)

def makestage(start, count, recipe, completion, work, sync):
    out=""
    conj = "or"
    if sync != False:
        letter = "A"
        while letter != lastletter:
            if synclist[(letter,sync)] != 0:
                out += makeSyncStatement(sync, letter, conj)
                conj = "and"
            letter = advLetter(letter, 1)
    if (count > 1):
        #bulk phase
        out += makebody("signal-each", "false", "true", "=", str(recipe), conj)
        out += makebody("signal-" + completion, "true", "false", ">", str(start), "and")
        out += makebody("signal-" + completion, "true", "false", "<", str(start + count), "and")
        conj = "or"

    #final output
    out += makebody("signal-each", "false", "true", "=", str(recipe), conj)
    out += makebody("signal-" + completion, "true", "false", "=", str(start + count), "and")
    out += makebody("signal-" + work, "true", "false", "=", str(0), "and")
    return out

body = ""
for i,wo in enumerate(work):
    index = -1
    body += makeEntity(i)
    sync = False
    for stage in wo:
        if stage[0] == "sync":
            sync = stage[1]
        else:
            body += makestage(index, stage[1], recipeTable[stage[0]], advLetter("A",i), advLetter("K",i), sync)
            index += stage[1]
            sync = False
    body = body[:-1]
    body += entityfooter

body += '{"entity_number": 100, "name": "constant-combinator", "position": {"x": -1, "y": -1}, "control_behavior": { "sections":{ "sections": [{ "index":1, "filters":['
for r, v in recipeTable.items():
    t = "item"
    if "empty" in r:
        t = "recipe"
    body += '{"index": ' + str(v) + ', "type": "' + t + '", "name": "' + r + '", "quality": "normal", "comparator": "=", "count": ' + str(v) + '},'
body = body[:-1]
body += ']}]}}}'

print(header + body + footer)
