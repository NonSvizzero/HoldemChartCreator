cards = 'AKQJT98765432'

hands = []
for i, card_a in enumerate(cards):
    hands.append([])
    for j, card_b in enumerate(cards):
        if i > j:
            hand = card_b + card_a +'o'
        elif i == j:
            hand = card_a + card_b
        else:
            hand = card_a + card_b + 's'
        hands[-1].append(hand)

if __name__ == '__main__':
    print(hands)