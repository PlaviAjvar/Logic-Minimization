import forms

# truth table

# generates boolean function output for given combination of input values
def generate_output(expr, mask, num_var):
    # first convert to rpn for easier calculation
    rpn_expr = forms.generate_rpn(expr)
    values = [mask & (1 << i) for i in range(num_var)]
    return forms.eval_rpn(rpn_expr, values)

# returns True if two boolean functions are equal on every possible input
# also returns second value which is 0 if True
# if False it is the mask which represents the values for the variables for which the function outputs differ
def equal(first_expr, second_expr):
    operands_first = sum([mem.is_operand for mem in first_expr])
    operands_second = sum([mem.is_operand for mem in second_expr])
    if operands_first != operands_second:
        raise Exception("Expressions have different number of parameters!")

    num_var = operands_first
    # iterate over all possible combinations of variable values
    for mask in range(1 << num_var):
        output_first = generate_output(first_expr, mask, num_var)
        output_second = generate_output(second_expr, mask, num_var)
        if output_first != output_second:
            return False, mask

    return True, 0

# format nicely and display truth table of expression
def truth_table(expr):
    num_var = sum([mem.is_operand for mem in expr])
    rpn_expr = forms.generate_rpn(expr)

    for mask in range(1 << num_var):
        # print binary mask representing input variables
        print(bin(mask)[2:])
        value = forms.eval_rpn(rpn_expr)
        print(" | ", value)
