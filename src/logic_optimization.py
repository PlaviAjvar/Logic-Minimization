import forms
import inout

# The task is to minimize the number of NANDs/NORs in the expression obtained
# by transforming the initial one, utilizing De-Morgan's laws and properties of NAND/NOR.

inf = 10 ** 18  # artificial infinity, larger than any feasible length of expression


# utility function which optimizes nand/nor usage for both cases(conjuctive and disjunctive)
# just need to define different base cases
# adv_flag tells us if we can use DeMorgan negation to our advantage
# either we are using nand on dnf, or nor on cnf, and in both cases in the second layer
def minimize_util(low_idx, high_idx, min_op, backtrack, adv_flag):
    # to prevent further copying of min_op and backtrack lists
    def minimize_util_help(low_idx, high_idx):
        # base case
        if low_idx == high_idx:
            return min_op[low_idx][high_idx]
        # if we've already calculated the value
        if min_op[low_idx][high_idx] != inf:
            return min_op[low_idx][high_idx]

        for split_point in range(low_idx, high_idx):
            left_cost = 2 * minimize_util_help(low_idx, split_point) + 1
            # if one of the operands is a first layer problem, and we can exploit negation
            # then half the nands/nors dissapear, and we use it only once since there is no need to set A' = A op A
            # special case when left operand is a single variable and we cant exploit this feature
            if left_cost != 1 and low_idx == split_point and adv_flag:
                left_cost = left_cost // 4

            right_cost = 2 * minimize_util_help(split_point + 1, high_idx) + 1
            if right_cost != 1 and split_point + 1 == high_idx and adv_flag:
                right_cost = right_cost // 4

            # calculate minimal cost for split at split point
            split_cost = left_cost + right_cost + 1
            # if found better solution, update
            if split_cost < min_op[low_idx][high_idx]:
                min_op[low_idx][high_idx] = split_cost
                backtrack[low_idx][high_idx] = split_point

        return min_op[low_idx][high_idx]

    return minimize_util_help(low_idx, high_idx)

# generates optimal expression of arbitrary normal form from calculated backtracking table
def nf_expression(backtrack, expr, is_nand, is_dnf):
    # define operation character(nand/nor)
    op = forms.operator("nand")
    if not is_nand:
        op = forms.operator("nor")

    # utility function for generating negation of first layer problem
    # let's assume we have conjuctive form without loss of generality
    # we can use the negation to our advantage
    # we have the following cases:
    # 1. conjuction is one letter - we have to form it's negation A' = A nand A
    # 2. conjuction is three letters(negation), and therefore (A nand A)' = A
    # 3. conjuction is of the form A nand A(any case where both halves of A are nonempty)
    # last case is same as second, except we need to add parentheses in the end
    def factor_negate(factor):
        if len(factor) == 1:
            return [forms.parenthesis("(")] + factor + [op] + factor + [forms.parenthesis(")")]
        elif len(factor) == 3:
            return [factor[1]]
        return factor[0:len(factor) // 2]

    # returns (A op A) as string
    def negation_form(expr):
        if len(expr) == 1:
            return [forms.parenthesis("(")] + expr + [op] + expr + [forms.parenthesis(")")]
        return [forms.parenthesis("(")]*2 + expr + [forms.parenthesis(")")] + [op] + [forms.parenthesis("(")] + expr + [forms.parenthesis(")")]*2

    # returns (A op B) as string
    def op_form(left_expr, right_expr):
        if len(left_expr) != 1:
            left_expr = [forms.parenthesis("(")] + left_expr + [forms.parenthesis(")")]
        if len(right_expr) != 1:
            right_expr = [forms.parenthesis("(")] + right_expr + [forms.parenthesis(")")]
        return [forms.parenthesis("(")] + left_expr + [op] + right_expr + [forms.parenthesis(")")]

        # utility function for recursivelly generating expression
    def expression_util(low_idx, high_idx):
        if low_idx == high_idx: # reduces to first layer problem
            return expr[low_idx]
        # AvB = (AvB)'' = (A'B')' = (A nand A) nand (B nand B)
        # AvB = (AvB)'' = (A nor B)' = (A nor B) nor (A nor B)
        # AB = (AB)'' = (A nand B)' = (A nand B) nand (A nand B)
        # AB = (AB)'' = (A' v B')' = A' nor B' = (A nor A) nor (B nor B)
        # in cases 1 and 4 we can exploit the negation on the left and right side
        left_expr = expression_util(low_idx, backtrack[low_idx][high_idx])
        right_expr = expression_util(backtrack[low_idx][high_idx] + 1, high_idx)
        # cases 1 and 4
        if is_nand == is_dnf:
            first_half = negation_form(left_expr) # (A op A)
            second_half = negation_form(right_expr)
        # cases 2 and 3
        else:
            first_half = op_form(left_expr, right_expr)  # (A op B)
            second_half = first_half

        if is_nand == is_dnf and low_idx == backtrack[low_idx][high_idx]:
            first_half = factor_negate(left_expr)

        if is_nand == is_dnf and high_idx == backtrack[low_idx][high_idx] + 1:
            second_half = factor_negate(right_expr)

        full_expr = first_half + [op] + second_half
        return full_expr

    return expression_util(0, len(expr) - 1)


# finds minimal equivalent expression of conjuction/disjunction using only NANDs/NORs
# argument is list of numbers corresponding to the indices of the input variables
def first_layer(factor, is_nand, is_dnf):
    num_var = len(factor)
    # minimal number of NANDs/NORs to represent segment in conjuctive/disjunctive factor
    min_op = [[inf] * num_var for i in range(num_var)]
    backtrack = [[-1] * num_var for i in range(num_var)]  # store optimal splitting point of each segment
    # base cases
    for i in range(num_var):
        if factor[i] > 0:
            # zero NANDs/NORs are needed to write expression with a single non-negated variable
            min_op[i][i] = 0
        else:
            # one NAND/NOR needed when there is a single negation
            min_op[i][i] = 1
        backtrack[i][i] = i

    # the first layer problem can be considered the oposite of the second layer one
    minimize_util(0, num_var-1, min_op, backtrack, is_nand != is_dnf)
    return backtrack, min_op

# generates expression for optimal solution of first layer
def first_layer_expression(factor, is_nand, is_dnf):
    op = forms.operator("nand")
    if not is_nand:
        op = forms.operator("nor")
    expr = [[forms.operand(x)] if x > 0 else [forms.operand(-x)] + [op] + [forms.operand(-x)] for x in factor]

    backtrack, min_op = first_layer(factor, is_nand, is_dnf)
    return nf_expression(backtrack, expr, is_nand, not is_dnf)


# finds equivalent of disjunctive/conjuctive form with least number of NANDs/NORs
def second_layer(cost, is_nand, is_dnf):
    num_var = len(cost)
    # minimal number of NANDs/NORs to represent segment in disjunctive/conjuctive form
    min_op = [[inf] * num_var for i in range(num_var)]
    backtrack = [[-1] * num_var for i in range(num_var)]  # store optimal splitting point of each segment
    # base cases
    for i in range(num_var):
        min_op[i][i] = cost[i]  # minimal cost of conjuction/disjunction in disjunctive/conjuctive form
        backtrack[i][i] = i

    minimize_util(0, num_var - 1, min_op, backtrack, (is_nand == is_dnf))
    return backtrack, min_op

# generates expression for optimal solution of second layer
def second_layer_expression(expr, cost, is_nand, is_dnf):
    backtrack, min_op = second_layer(cost, is_nand, is_dnf)
    return nf_expression(backtrack, expr, is_nand, is_dnf)


# the first argument is the list of lists(list of conjuctions/disjunctions) in disjoint form
# the inner lists contain the indexes of the logical input variables
# it is already assumed there are disjunctions between the conjuctive forms
# the second argument represents the number of variables in the initial logic function
def min_log_form_util(nf, is_nand, is_dnf):
    # depending on if form is dnf calculate minimum conjuction or disjunction cost individually
    expr = [first_layer_expression(factor, is_nand, is_dnf) for factor in nf]
    cost = [len(nand_ex) for nand_ex in expr]
    # calculate optimal form given the expressions and costs for first layer problem
    form = []
    if len(nf) > 1:
        form = second_layer_expression(expr, cost, is_nand, is_dnf)
    elif len(nf) == 1:
        form = expr[0]
    return form

# returns minimal logic form of an expression given in expression form
def min_log_form(expr, is_nand):
    disj_expr, is_dnf = inout.generate_disj_from_expr(expr)
    return min_log_form_util(disj_expr, is_nand, is_dnf)