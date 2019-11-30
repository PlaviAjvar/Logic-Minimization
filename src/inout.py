import forms

# convert DNF in string form to DNF in list form(suitable for the algorithm above)
def parse_disj_from_expr(dnf_expr, is_disj):
    op = forms.operator("and")
    if is_disj:
        op = forms.operator("or")
    disj_expr = []
    for char in dnf_expr:
        if char == op:
            disj_expr.append([])
        elif char.is_operand:
            disj_expr[-1].append(char.value)
    return disj_expr

# tests if expression is disjunctive or conjuctive
# form of the kind AvBvCvDv... is considered disjunctive, as it doesn't really matter
def is_disjunctive(expr):
    open_parentheses = 0
    for char in expr:
        if char == forms.parenthesis("("):
            open_parentheses += 1
        elif char == forms.parenthesis(")"):
            open_parentheses -= 1
        elif char == forms.operator("or"):
            # if there is an operator or between two parentheses
            if open_parentheses > 0:
                return True
    return False


# generates disjoint form from proper expression form and tests if it is dnf or cnf
def generate_disj_from_expr(expr):
    is_disj = is_disjunctive(expr)
    return parse_disj_from_expr(expr, is_disj), is_disj


# a proper string is a string which involves only valid operator symbols for "and" and "or"
# also in it the operands are represented with numbers
# negation is represented by a "'" after a number
def generate_expr_from_proper_str(str):
    # remove all whitespace
    str = str.replace(" ", "")
    # remove all conjuctions, leave them to be defined implicitly
    # if there aren't any it's assumed they are implicit
    str = str.replace("\u2229", "")

    # tests if there is a conjuction between the 2 characters
    # implicit conjutions are present in the following cases
    # ")(", ")A", "A(", "AB"
    def is_lim(left, right):
        left_lim = False
        right_lim = False
        # it should be a right parentheses or a variable
        if left.value == ")" or left.is_operand:
            left_lim = True
        if right.value == "(" or right.is_operand:
            right_lim = True
        return (left_lim and right_lim)

    expr = []
    last_char = None
    for char in str:
        # append next character
        if char == "\u2228":
            expr.append(forms.operator("or"))
        elif char == "(" or char == ")":
            expr.append(forms.parenthesis(char))
        elif char == "'":  # negate the last variable
            expr[-1] = forms.operand(-expr[-1].value)
        else:
            if expr[-1].is_operand:
                # append another digit to current variable
                expr[-1] = 10*expr[-1] + int(char)
            else:
                expr.append(forms.operand(int(char)))
        # see if there is a conjuction before this character
        if last_char != None and is_lim(last_char, expr[-1]):
            expr.apend(forms.operator("and"))
            # reverse the alst two characters(and should be before this character)
            expr[-1], expr[-2] = expr[-2], expr[-1]
        last_char = expr[-1]

    return expr

# generate expression from string from standard i/o
# the disjunctions are represented with lowercase v
def generate_expr_from_vstr(vstr):
    # remove all whitespace
    vstr = vstr.replace(" ", "");
    # convert to proper string
    out_str = ""
    for char in vstr:
        if not (char == "(" or char == ")" or char == "v" or char == "'"):
            out_str += str(ord(char))
        else:
            out_str += char

    str = out_str.replace("v", "\u2228")
    # reduce to previous problem
    return generate_expr_from_proper_str(str)

# generate output string from expression
def generate_str_from_expr(expr):
    expr_str = ""
    for expr_member in expr:
        # if it's an operand add it negated or not depending on sign
        if expr_member.is_operand:
            expr_str += chr(abs(expr_member.value))
            if expr_member.value < 0:
                expr_str += "'"
        else:  # otherwise it doesn't matter, just add value which is string anyway
            expr_str += expr_member.value
    return expr_str

# count number of operators in expression(mostly nand or nor)
def op_count(expr):
    # count all opertor occurances
    return sum([char.is_operator for char in expr])

# returns expr generated from v-string on stdin
def input_from_stdin():
    print("Input type of operation(nand, nor): ")
    op = input().lower()
    is_nand = (op == "nand")
    print("\nInput your logical expression in either conjuctive or disjunctive form:\n\ny = ")
    vstr = input()
    # generate expression from inputed string
    expr = generate_expr_from_vstr(vstr)
    return expr, is_nand

# helper function for inputing from file
def input_from_file(file_name):
    # open file for reading and read into string
    input_file = open(file_name,  "r")
    line = input_file.readline().lower()
    is_nand = (line == "nand")
    str = ""
    for line in input_file:
        str += line
    expr = generate_expr_from_proper_str(str)
    return expr, is_nand

# helper function for outputing solution to stdin
def output_to_stdin(min_form, is_nand):
    min_form_str = generate_str_from_expr(min_form)
    print("The minimal form is:\n\ny =", min_form_str)
    print("The minimal number of", ["NORs", "NANDs"][is_nand], "in the optimal solution is", op_count(min_form))

# helper function for outputing solution to file
def output_to_file(file_name, min_form):
    # open file for writing
    output_file = open(file_name, "w")
    min_form_str = generate_str_from_expr(min_form)
    output_file.write(min_form_str)