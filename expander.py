from sympy.logic import simplify_logic
from sympy import symbols


'''  Used to generate slow version of PUF by repeated substitution '''

a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11 = symbols('a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11')

b0 = (a0 & a1 & a2) | (~a1 & a3)
b1 = (a4 & ~a5 & a6) | (~a4 & ~a7) | (a5 & a7)
b2 = (a8 & ~a9) | (a9 & ~a10 & ~a11)
b3 = (~a0 & ~a4 & a8) | (a0 & ~a10)

c0 = (b0 & b1 & b2) | (~b1 & b3)
c1 = (b1 & ~b0 & b3) | (~b1 & ~b3) | (b0 & b2)
c2 = (b1 & ~b3) | (b2 & ~b0 & ~b1)
c3 = (~b0 & ~b2 & b3) | (b1 & ~b3)

d0 = (c0 & c1 & c2) | (~c1 & c3)
d1 = (c1 & ~c0 & c3) | (~c1 & ~c3) | (c0 & c2)
d2 = (c1 & ~c3) | (c2 & ~c0 & ~c1)
d3 = (~c0 & ~c2 & c3) | (c1 & ~c3)

e0 = (d0 & d1 & d2) | (~d1 & d3)
e1 = (d1 & ~d0 & d3) | (~d1 & ~d3) | (d0 & d2)
e2 = (d1 & ~d3) | (d2 & ~d0 & ~d1)
e3 = (~d0 & ~d2 & d3) | (d1 & ~d3)

f0 = (e0 & e1 & e2) | (~e1 & e3)
f1 = (e1 & ~e0 & e3) | (~e1 & ~e3) | (e0 & e2)
f2 = (e1 & ~e3) | (e2 & ~e0 & ~e1)
f3 = (~e0 & ~e2 & e3) | (e1 & ~e3)

print("f0 =", simplify_logic(f0, form='cnf'))
print("f1 = ", simplify_logic(f1, form='cnf'))
print("f2 = ", simplify_logic(f2, form='cnf'))
print("f3 = ", simplify_logic(f3, form='cnf'))
