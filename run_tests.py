#!/usr/bin/env python3
import io
import sys
import subprocess
import unittest

from decimal import Decimal
from compute_debts import parse_people, parse_expenses, compute_debts, \
    print_results


class ComputeDebtsTest(unittest.TestCase):
    def setUp(self):
        self.people_list = ['Alice', 'Bob', 'Claire', 'David']
        self.transactions = [
            {'from': 'Alice', 'to': 'Bob', 'amount': Decimal('52.875')},
            {'from': 'Alice', 'to': 'Claire', 'amount': Decimal('58.5875')},
            {'from': 'Alice', 'to': 'David', 'amount': Decimal('66.925')},
            {'from': 'Bob', 'to': 'Claire', 'amount': Decimal('5.7125')},
            {'from': 'Bob', 'to': 'David', 'amount': Decimal('14.050')},
            {'from': 'Claire', 'to': 'David', 'amount': Decimal('8.3375')}
        ]

    def test_get_input_args(self):
        def get_return_code(shell_command):
            """Run a shell command and return its execution code."""
            return subprocess.run(shell_command, shell=True).returncode

        # Incorrect/incomplete args
        self.assertEqual(
            get_return_code('python3 compute_debts.py'), 2
        )
        self.assertEqual(
            get_return_code('python3 compute_debts.py TestPeople.txt'), 2
        )
        self.assertEqual(
            get_return_code('python3 compute_debts.py TestExpenses.txt'), 2
        )
        self.assertEqual(
            get_return_code('python3 compute_debts.py random'), 2
        )
        # Correct args
        self.assertEqual(
            get_return_code('python3 compute_debts.py TestPeople.txt TestExpenses.txt'), 0
        )

    def test_parse_people(self):
        self.assertEqual(parse_people('TestPeople.txt'), self.people_list)
        # Parsing a non-existent file should give an error
        with self.assertRaises(FileNotFoundError):
            parse_people('empty.txt')

    def test_parse_expenses(self):
        expenses = parse_expenses('TestExpenses.txt', self.people_list)
        self.assertIsInstance(expenses, dict)
        transactions = {
            'Alice': Decimal('0'),
            'Bob': Decimal('211.50'),
            'Claire': Decimal('234.35'),
            'David': Decimal('267.70')
        }
        for person, amount in transactions.items():
            self.assertEqual(expenses[person], amount)
        # Parsing a non-existent file should give an error
        with self.assertRaises(FileNotFoundError):
            parse_expenses('empty.txt', self.people_list)
            parse_expenses('empty.txt', [])

    def test_compute_debts(self):
        expenses = parse_expenses('TestExpenses.txt', self.people_list)
        debts = compute_debts(expenses, self.people_list)
        for trans in self.transactions:
            self.assertIn(trans, debts)

    def test_print_results(self):
        # Capture `print` statement's output in a variable
        output = io.StringIO()
        sys.stdout = output
        print_results(self.transactions)
        sys.stdout = sys.__stdout__
        self.assertIn("Alice pays $52.88 to Bob", output.getvalue())
        self.assertIn("Alice pays $58.59 to Claire", output.getvalue())
        self.assertIn("Alice pays $66.92 to David", output.getvalue())
        self.assertIn("Bob pays $5.71 to Claire", output.getvalue())
        self.assertIn("Bob pays $14.05 to David", output.getvalue())
        self.assertIn("Claire pays $8.34 to David", output.getvalue())


if __name__ == '__main__':
    print("Running tests...\n")
    unittest.main()
