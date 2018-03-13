#!/usr/bin/env python3
import argparse
from decimal import Decimal


def parse_people(file_path):
    """Return a list of people names provided in a text file."""
    result = []
    with open(file_path) as file:
        for line in file.read().split('\n'):
            if line:
                result.append(''.join(ch for ch in line if ch.isalnum()))
    return result


def parse_expenses(file_path, people_list):
    """Return a dictionary in `Person: Amount` format obtained from a
    parsed expenses text file, where `Amount` is a sum of all expenses
    a person has.
    """
    def get_person(string):
        for person in people_list:
            if person in string:
                return person

    def get_amount(string):
        return Decimal(string[string.find('$')+1:string.find(' for')])

    result = {person: Decimal(0) for person in people_list}
    with open(file_path) as file:
        for line in file.read().split('\n'):
            if line:
                result[get_person(line)] += get_amount(line)
    return result


def compute_debts(expenses, people_list):
    """Return a list of debts that are needed to be paid in order to
    break even amoung given people.
    """
    def initialize_result_list():
        result = []
        for person in people_list:
            for person2 in people_list:
                if person2 != person:
                    result.append({
                        'from': person,
                        'to': person2,
                        'amount': Decimal(0)
                    })
        return result

    def add_new_transaction(result, from_, to, amount):
        """Add new future transaction to the results.

        E.g. {'from': 'Alice', 'to': 'Bob', 'amount': Decimal('52.87')}
        """
        for item in result:
            if item['from'] == from_ and item['to'] == to:
                item['amount'] += amount

    def merge_dual_transactions(result):
        """Update results by seeking two-way transitions between two
        people and merging them to simplify the end result.

        Example:

        Given two transactions:
            1. Alice pays $52.88 to Bob.
            2. Bob pays $10.00 to Alice.

        We can merge them down to:
            Alice pays $42.88 to Bob.
        """
        for trans1 in result:
            if trans1['amount']:
                for trans2 in result:
                    if trans2['amount']:
                        if (trans1['from'] == trans2['to'] and
                                trans1['to'] == trans2['from']):
                            if trans1['amount'] > trans2['amount']:
                                trans1['amount'] = trans1['amount'] - trans2['amount']
                                result.remove(trans2)
                            else:
                                trans2['amount'] = trans2['amount'] - trans1['amount']
                                result.remove(trans1)

    result = initialize_result_list()
    for person, amount in expenses.items():
        if amount > 0:
            to_be_paid = amount / len(people_list)
            for person2, amount2 in expenses.items():
                if person != person2:
                    add_new_transaction(result, person2, person, to_be_paid)
    merge_dual_transactions(result)
    return result


def print_results(transactions):
    """Output transactions in a human-readable format in a terminal
    window.
    """
    for trans in transactions:
        if trans['amount']:
            rounded_amount = round(abs(trans['amount']), 2)
            print(f"{trans['from']} pays ${rounded_amount} to {trans['to']}")


def get_input_args():
    """Return people names and expenses text files as arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('people', type=str)
    parser.add_argument('expenses', type=str)
    return parser.parse_args()


if __name__ == '__main__':
    args = get_input_args()
    people_list = parse_people(args.people)
    expenses = parse_expenses(args.expenses, people_list)
    debts = compute_debts(expenses, people_list)
    print_results(debts)
