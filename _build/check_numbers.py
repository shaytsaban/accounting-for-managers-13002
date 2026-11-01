# Recomputes every figure in the lesson's statements, tables and solved questions. Run: python3 check_numbers.py
ok = True


def eq(name, a, b):
    global ok
    good = abs(a - b) < 1e-9
    ok &= good
    print(('OK  ' if good else 'BAD ') + name, a, b)


# balance sheet of the demonstration company
ca = 40000 + 60000 + 50000
eq('current assets', ca, 150000)
eq('total assets', ca + 170000, 320000)
cl = 38000 + 10000 + 20000
eq('current liabilities', cl, 68000)
eq('total liabilities', cl + 80000, 148000)
eq('equity', 100000 + 72000, 172000)
eq('balance', 148000 + 172000, 320000)
# income statement of Yuval
gp = 500000 - 300000
eq('gross', gp, 200000)
op = gp - 45000 - 65000
eq('operating', op, 90000)
bt = op - 12000
eq('before tax', bt, 78000)
eq('net', bt - 18000, 60000)
eq('all expenses in the demos', 500000 - 60000, 440000)
# retained earnings demo
eq('retained earnings demo', 20000 + 60000 - 8000, 72000)
eq('changes in equity demo', 150000 + 60000 - 8000, 202000)
eq('premium demo', 3 - 1, 2)
eq('notes demo', 120000 + 50000, 170000)
eq('depreciation demo', 100000 / 10, 10000)
# the demonstration table: change in assets = change in liabilities + change in equity
for name, a, l, e in [('shares', 100000, 0, 100000), ('loan', 200000, 200000, 0), ('service', 30000 + 50000, 0, 80000), ('electricity', 0, 5000, -5000), ('supplier', -12000, -12000, 0), ('dividend', -5000, 5000, -10000)]:
    eq('row ' + name, a, l + e)
# practice questions
eq('q16 assets', 60000 - 20000, 40000)
eq('q16 liabilities', 60000 - 20000, 40000)
eq('q17 revenue', 120000 / 12, 10000)
eq('q17 deferred', 120000 - 10000, 110000)
g19 = 400000 - 250000
o19 = g19 - 60000
b19 = o19 - 15000
n19 = b19 - 20000
eq('q19 net', n19, 55000)
eq('q19 retained', 30000 + n19 - 25000, 60000)
eq('q20 interest', 300000 * .08 * 4 / 12, 8000)
eq('interest demo', 100000 * .06 * 6 / 12, 3000)
eq('q18 demo', 30000 - 10000, 20000)
print('ALL OK' if ok else 'FAILED')
