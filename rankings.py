import Card

rank_number_to_string = {1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10", 11: "J",
                         12: "Q", 13: "K"}

hand_rank_number_to_string = {1: "High Card", 2: "One Pair", 3: "Two Pair", 4: "Three of a Kind", 5: "Straight",
                              6: "Flush", 7: "Full House", 8: "Four of a Kind", 9: "Straight Flush", 10: "Royal Flush"}

# Note: Ace card_number is 14 if it is used as a high card
def rank_hand(full_hand):
    # if has_royal_flush(full_hand):
    #     return 10, None
    # straight_flush_bool, straight_flush_high_card = has_straight_flush(full_hand)
    # if straight_flush_bool:
    #     return 9, straight_flush_high_card
    four_of_a_kind_bool, four_of_a_kind_high_card = has_four_of_a_kind(full_hand)
    if four_of_a_kind_bool:
        return 8, four_of_a_kind_high_card
    full_house_bool, full_house_cards = has_full_house(full_hand)
    if full_house_bool:
        return 7, full_house_cards
    flush_bool, flush_high_card = has_flush(full_hand)
    if flush_bool:
        return 6, flush_high_card
    straight_bool, straight_high_card = has_straight(full_hand)
    if straight_bool:
        return 5, straight_high_card
    three_of_a_kind_bool, three_of_a_kind_card = has_three_of_a_kind(full_hand)
    if three_of_a_kind_bool:
        return 4, three_of_a_kind_card
    two_pair_bool, two_pair_cards = has_two_pair(full_hand)
    if two_pair_bool:
        return 3, two_pair_cards
    one_pair_bool, one_pair_card = has_one_pair(full_hand)
    if one_pair_bool:
        return 2, one_pair_card
    return has_high_card(full_hand)


# TODO: royal flush
def has_royal_flush(full_hand):
    return


# TODO: staight flush
def has_straight_flush(full_hand):
    return


# return whether there's a four of a kind and what the card_number is
# AAAA -> True, 14
def has_four_of_a_kind(full_hand):
    full_hand_numbers = [card.number for card in full_hand]
    for card_number in full_hand_numbers:
        if full_hand_numbers.count(card_number) == 4:
            if card_number == 1:
                card_number = 14
            return True, card_number
    return False, 0


# returns whether there's a full house and what the 3 of a kind is and the pair is in that order
# AAAKK -> True, (A,K)
def has_full_house(full_hand):
    three_of_a_kind = has_three_of_a_kind(full_hand)
    two_pair = has_two_pair(full_hand)
    if three_of_a_kind[0] and two_pair[0] and (three_of_a_kind[1] != max(two_pair[1])):
        return True, (three_of_a_kind[1], max(two_pair[1]))
    if three_of_a_kind[0] and two_pair[0] and (three_of_a_kind[1] != min(two_pair[1])):
        return True, (three_of_a_kind[1], min(two_pair[1]))
    return False, (0, 0)


# returns whether there's a flush and what the high card of the flush is
# 2H 5H 6H 10H 7H -> True, 10
def has_flush(full_hand):
    full_hand_suits = [card.suit for card in full_hand]
    full_hand_numbers = [card.number for card in full_hand]
    has_flush_bool = False
    flush_suit = None
    for suit in full_hand_suits:
        if full_hand_suits.count(suit) > 4:
            has_flush_bool = True
            flush_suit = suit
    if has_flush_bool:
        full_hand_numbers.sort(reverse=True)
        for card in full_hand:
            if card.suit == flush_suit and card.number == 1:
                return True, 14
        for number in full_hand_numbers:
            for card in full_hand:
                if card.suit == flush_suit and card.number == number:
                    return True, number
    return False, 0


# return whether there's a straight and what the highest card of the straight is.
# A2345 -> True, 5
# 10JQKA -> True, A
def has_straight(full_hand):
    has_straight_bool = False
    # a straight requires 5 cards minimum
    if len(full_hand) < 5:
        return False, 0
    current_high_card_number = 0
    for card in full_hand:
        high_card = check_straight_offsets(card, full_hand)
        if high_card > current_high_card_number:
            has_straight_bool = True
            current_high_card_number = high_card
    return has_straight_bool, current_high_card_number


def check_straight_offsets(card, full_hand):
    capture = 0
    for i in range(1, 5):
        # special case for Ace high
        if card.number + i == 14:
            if not value_in_full_hand(1, full_hand):
                return 0
            return 14

        if not value_in_full_hand(card.number + i, full_hand):
            return 0
        capture = i
    return card.number + capture


def value_in_full_hand(card_number, full_hand):  # probably make static I guess
    for card in full_hand:
        if card.number == card_number:
            return True
    return False


# returns whether there's a three of a kind and the best three of a kind card
# 3335557 -> True, 5
def has_three_of_a_kind(full_hand):
    full_hand_numbers = [card.number for card in full_hand]
    current_best = 0
    for card_number in full_hand_numbers:
        if card_number > current_best or card_number == 1:
            if full_hand_numbers.count(card_number) == 3:
                current_best = card_number
                if current_best == 1:
                    return True, 14

    return current_best > 0, current_best


# returns whether there's a two pair and the best two pair
# 5522883 -> True, [5,8]
def has_two_pair(full_hand):
    full_hand_numbers = [card.number for card in full_hand]
    pairs = []
    for card_number in full_hand_numbers:
        if full_hand_numbers.count(card_number) >= 2:
            if card_number == 1:
                card_number = 14
            if card_number not in pairs:
                pairs.append(card_number)
    if len(pairs) > 2:
        pairs.remove(min(pairs))
    return len(pairs) == 2, pairs


# returns whether there's a one pair and what the card number is
# 44786 -> True, 4
def has_one_pair(full_hand):
    full_hand_numbers = [card.number for card in full_hand]
    for card_number in full_hand_numbers:
        if full_hand_numbers.count(card_number) == 2:
            if card_number == 1:
                return True, 14
            return True, card_number
    return False, 0


# returns true (because there's always a high card if nothing else) and the card number
# 28974 -> True, 9
def has_high_card(full_hand):
    full_hand_numbers = [card.number for card in full_hand]
    if 1 in full_hand_numbers:  # Ace
        return True, 14
    return True, max(full_hand_numbers)


ranking = rank_hand(
    [Card.Card("Hearts", "K"), Card.Card("Hearts", "2"), Card.Card("Clubs", "3"), Card.Card("Hearts", "5"),
     Card.Card("Hearts", "A"), Card.Card("Hearts", "3"), Card.Card("Diamonds", "3")])
print(hand_rank_number_to_string[ranking[0]], ranking[1])
