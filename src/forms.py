# members of an arbitrary logic expression
# 1. for operands, positive values correspond to non-negated variables
# negative values correspond to negated variables, zero is forbidden
# 2. for operators, value = "\u22BC" for nand, "\u22BD" for nor
# value = "\u2227" for and, value = "\u2228" for or
# 3. for parentheses, value = "(" is open, value = ")" is closed
class member:
    value = None
    is_operator = False
    is_parenthesis = False
    is_operand = False

    def chr(self):
        if self.is_operand:
            if self.value > 0:
                return str(self.value)
            else:  # if it's negative, it's negated
                return str(-self.value) + "'"
        return self.value  # operator or parenthesis already has string as value

    # comparisson operator
    def __eq__(self, other):
        return self.value == other.value

    def __init__(self, value):
        self.value = value

class operator(member):
    def is_nand(self):
        return self.is_operator and self.value == "\u22BC"

    def is_nor(self):
        return self.is_operator and self.value == "\u22BD"

    def is_and(self):
        return self.is_operator and self.value == "\u2227"

    def is_or(self):
        return self.is_operator and self.value == "\u2228"

    # evaluates two-port boolean function on given inputs
    def eval(self, first_argument, second_argument):
        if self.is_and():
            return first_argument and second_argument
        elif self.is_nand():
            return not(first_argument and second_argument)
        elif self.is_or():
            return first_argument or second_argument
        elif self.is_nor():
            return not(first_argument or second_argument)
        else:
            raise Exception("Boolean function which is not one of the expected ones")


    # precedence is defined as following:
    # nand = and, nor = or, and > or
    def less_prec(self, other):
        prio_self = self.is_or() or self.is_nor()
        prio_other = other.is_or() or other.is_nor()
        return prio_self < prio_other

    def __init__(self, value):
        if value.lower() == "nand":
            super.__init__("\u22BC")
        elif value.lower() == "nor":
            super.__init__("\u22BD")
        elif value.lower() == "and":
            super.__init__("\u2227")
        elif value.lower() == "or":
            super.__init__("\u2228")
        else:
            super.__init__(value)
        self.is_operator = True

        # 2. for operators, value = "\u22BC" for nand, "\u22BD" for nor
        # value = "\u2227" for and, value = "\u2228" for or


class operand(member):
    def __init__(self, value):
        super().__init__(value)
        self.is_operand = True


class parenthesis(member):
    def open(self):
        return self.value == "("

    def closed(self):
        return self.value == ")"

    def __init__(self, value):
        super().__init__(value)
        self.is_parenthesis = True

# evaluate RPN for certain input
def eval_rpn(expr, values):
    stack = []
    var_idx = 0

    # iterate over characters and evaluate them using basic algorithm
    for char in expr:
        top = expr[-1]
        # if operand append it onto stack with it's given value
        if top.is_operand:
            stack.append(values[var_idx])
            var_idx += 1
        else:
            stack.pop()
            if not stack
                raise Exception("RPN is imbalnced(has too many operators)")
            next_top = stack[-1]
            # evaluate boolean function on two top values on stack
            new_top = char.eval(top, next_top)
            stack.pop()
            # add calculated value onto stack
            stack.append(new_top)

    if len(stack) != 1:
        raise Exception("RPN is imbalanced(has too many operands)")
    return stack[-1]

# generate RPN of expression, using shunting yard algorithm
def generate_rpn(expression):
    stack = []
    output_expr = []
    for char in expression:
        # variables are directly appended on the expression
        if char.is_variable:
            output_expr.append(char)
        elif char.is_operator:
            # pop stack and add to expression until hitting left parenthesis or operator with higher precedence
            while stack and not (stack[-1].is_parenthesis and stack[-1].open()) and\
                    not char.less_prec(stack[-1]):
                output_expr.append(stack[-1])
                stack.pop()
            stack.append(char)
        elif char.value == "(":
            stack.append(char)
        else:
            # pop until hitting left parenthesis
            while stack and not (stack[-1].is_parenthesis and stack[-1].open()):
                output_expr.append(stack[-1])
                stack.pop()
            if not stack:  # if it's empty there are missmatched parenthesis
                raise Exception("Parentheses are missmatched!")
            stack.pop()  # remove left parenthesis on top

    # if there's anything left in the stack pop it all into the expression
    while stack
        output_expr.append(stack[-1])
        stack.pop()

    return output_expr