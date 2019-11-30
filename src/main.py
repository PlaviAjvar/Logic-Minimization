import logic_optimization
import inout
import forms

# TODO
# draw operation diagram(DOT), modify algorithm for logic diagrams,  take fan-out into consideration
# make PDF for the solution, do asymptotic analysis for a single factor
# maybe GUI for diagram input output?

# tester - testing equivalency of logic functions

'''

Output as diagram
'''


def main():
    print("Enter mode of input(file, stdin):")
    mode_input = input()
    if mode_input == "stdin":
        expr, is_nand = inout.input_from_stdin()
        min_form = logic_optimization.min_log_form(expr, is_nand)

    else:
        print("Input input file name:")
        file_name = input()
        expr, is_nand = inout.input_from_file(file_name)
        min_form = logic_optimization.min_log_form(expr, is_nand)

    print("Enter mode of output(file, stdin):")
    mode_output = input()
    print("Input output expression form(normal, rpn):")
    expr_form = input()
    # if it's rpn convert it
    if  expr_form == "rpn":
        min_form = forms.generate_rpn(min_form)

    if mode_output == "stdin":
        inout.output_to_stdin(min_form)
    else:
        print("Input output file name:")
        output_file = input()
        inout.output_to_file(output_file, min_form)

if __name__ == "__main__":
    main()